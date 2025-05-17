from flask import Blueprint, request, jsonify, abort
from .models import Book, User, Exchange, Review
from . import db
from .schemas import BookSchema
from sqlalchemy.exc import IntegrityError

main = Blueprint('main', __name__)

book_schema = BookSchema()
books_schema = BookSchema(many=True)

@main.route('/')
def index():
    """
    Корневой endpoint API.
    Возвращает статус работы сервиса.
    :return: JSON с сообщением о статусе API.
    """
    return {"message": "Book Exchange API is running!"}

@main.route('/books', methods=['GET'])
def get_books():
    """
    Получить список книг с возможной фильтрацией по автору, названию и доступности.
    :query author: (str, optional) — фильтрация по автору (подстрока, регистронезависимо)
    :query title: (str, optional) — фильтрация по названию (подстрока, регистронезависимо)
    :query is_available: (bool, optional) — фильтрация по доступности
    :return: JSON-список книг с owner_username
    """
    author = request.args.get('author')  # Получаем фильтр по автору
    title = request.args.get('title')    # Получаем фильтр по названию
    is_available = request.args.get('is_available')  # Фильтр по доступности

    query = Book.query  # Базовый запрос

    # Фильтрация по автору
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    # Фильтрация по названию
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    # Фильтрация по доступности (строка -> bool)
    if is_available is not None:
        is_available_bool = is_available.lower() in ['true', '1', 'yes']
        query = query.filter(Book.is_available == is_available_bool)

    books = query.all()  # Получаем книги
    result = []
    for b in books:
        book_data = book_schema.dump(b)
        # Добавляем имя владельца
        book_data['owner_username'] = b.owner.username if b.owner else None
        result.append(book_data)
    return jsonify(result)

@main.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Получить книгу по id.
    :param book_id: int — ID книги
    :return: JSON с данными книги или 404 если не найдена
    """
    book = Book.query.get_or_404(book_id)
    return jsonify(book_schema.dump(book))

@main.route('/books', methods=['POST'])
def create_book():
    """
    Добавить новую книгу.
    Ожидает JSON с title, author, description (опционально), owner_id.
    :return: JSON с созданной книгой или ошибкой
    """
    data = request.get_json()
    # Валидация обязательных полей
    for field in ['title', 'author', 'owner_id']:
        if not data.get(field):
            return jsonify({'error': f'Missing or empty field: {field}'}), 400
    # Проверка существования owner_id
    owner = User.query.get(data['owner_id'])
    if not owner:
        return jsonify({'error': 'Owner not found'}), 400
    try:
        book = book_schema.load(data)
        new_book = Book(**book)
        db.session.add(new_book)
        db.session.commit()
        return jsonify(book_schema.dump(new_book)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@main.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Обновить книгу по id.
    :param book_id: int — ID книги
    :return: JSON с обновлённой книгой или ошибкой
    """
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    # Проверка owner_id, если обновляется
    if 'owner_id' in data:
        owner = User.query.get(data['owner_id'])
        if not owner:
            return jsonify({'error': 'Owner not found'}), 400
    for key, value in data.items():
        setattr(book, key, value)
    db.session.commit()
    return jsonify(book_schema.dump(book))

@main.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Удалить книгу по id.
    :param book_id: int — ID книги
    :return: пустой ответ с кодом 204 или ошибкой
    """
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return '', 204

@main.route('/users', methods=['POST'])
def create_user():
    """
    Создать пользователя.
    Ожидает JSON с username и email.
    Проверяет уникальность username и email.
    :return: JSON с созданным пользователем или ошибкой
    """
    data = request.get_json()
    # Валидация обязательных полей
    for field in ['username', 'email']:
        if not data.get(field):
            return jsonify({'error': f'Missing or empty field: {field}'}), 400
    # Проверка уникальности email и username
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    try:
        user = User(username=data['username'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'id': user.id, 'username': user.username, 'email': user.email}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Integrity error'}), 400

@main.route('/users', methods=['GET'])
def get_users():
    """
    Получить список всех пользователей.
    :return: JSON-список пользователей
    """
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'email': u.email} for u in users])

@main.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Получить пользователя по id.
    :param user_id: int — ID пользователя
    :return: JSON с данными пользователя или 404 если не найден
    """
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

@main.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Обновить пользователя по id.
    :param user_id: int — ID пользователя
    :return: JSON с обновлённым пользователем или ошибкой
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

@main.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Удалить пользователя по id.
    :param user_id: int — ID пользователя
    :return: пустой ответ с кодом 204 или ошибкой
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return '', 204

@main.route('/exchanges', methods=['GET'])
def get_exchanges():
    """
    Получить список обменов.
    Можно фильтровать по user_id (инициатор) и owner_id (владелец книги).
    :query user_id: int — фильтрация по инициатору обмена
    :query owner_id: int — фильтрация по владельцу книги
    :return: JSON-список обменов
    """
    user_id = request.args.get('user_id')
    owner_id = request.args.get('owner_id')
    query = Exchange.query
    if user_id:
        query = query.filter(Exchange.user_id == int(user_id))
    if owner_id:
        # Получить все книги пользователя и их id
        user_books = Book.query.filter(Book.owner_id == int(owner_id)).all()
        user_book_ids = [b.id for b in user_books]
        query = query.filter(Exchange.book_id.in_(user_book_ids))
    exchanges = query.all()
    return jsonify([
        {
            'id': e.id,
            'user_id': e.user_id,
            'book_id': e.book_id,
            'place': e.place,
            'timestamp': e.timestamp.isoformat() if e.timestamp else None
        } for e in exchanges
    ])

@main.route('/exchanges', methods=['POST'])
def create_exchange():
    """
    Создать обмен.
    Ожидает JSON с user_id, book_id, place.
    Проверяет существование пользователя и книги.
    :return: JSON с созданным обменом или ошибкой
    """
    data = request.get_json()
    # Валидация обязательных полей
    for field in ['user_id', 'book_id']:
        if not data.get(field):
            return jsonify({'error': f'Missing or empty field: {field}'}), 400
    # Проверка существования user_id и book_id
    user = User.query.get(data['user_id'])
    book = Book.query.get(data['book_id'])
    if not user or not book:
        return jsonify({'error': 'User or Book not found'}), 400
    try:
        exchange = Exchange(user_id=data['user_id'], book_id=data['book_id'], place=data.get('place'))
        db.session.add(exchange)
        db.session.commit()
        return jsonify({
            'id': exchange.id,
            'user_id': exchange.user_id,
            'book_id': exchange.book_id,
            'place': exchange.place,
            'timestamp': exchange.timestamp.isoformat() if exchange.timestamp else None
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@main.route('/exchanges/<int:exchange_id>', methods=['DELETE'])
def delete_exchange(exchange_id):
    """
    Удалить обмен по id.
    :param exchange_id: int — ID обмена
    :return: пустой ответ с кодом 204 или ошибкой
    """
    exchange = Exchange.query.get_or_404(exchange_id)
    db.session.delete(exchange)
    db.session.commit()
    return '', 204

@main.route('/reviews', methods=['GET'])
def get_reviews():
    """
    Получить список всех отзывов.
    :return: JSON-список отзывов
    """
    reviews = Review.query.all()
    return jsonify([
        {
            'id': r.id,
            'user_id': r.user_id,
            'book_id': r.book_id,
            'text': r.text,
            'rating': r.rating,
            'timestamp': r.timestamp.isoformat()
        } for r in reviews
    ])

@main.route('/reviews', methods=['POST'])
def create_review():
    """
    Создать отзыв.
    Ожидает JSON с user_id, book_id, text, rating.
    Проверяет существование пользователя и книги, а также валидность рейтинга.
    :return: JSON с созданным отзывом или ошибкой
    """
    data = request.get_json()
    # Валидация обязательных полей
    for field in ['user_id', 'book_id', 'text', 'rating']:
        if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            return jsonify({'error': f'Missing or empty field: {field}'}), 400
    # Проверка существования user_id и book_id
    user = User.query.get(data['user_id'])
    book = Book.query.get(data['book_id'])
    if not user or not book:
        return jsonify({'error': 'User or Book not found'}), 400
    # Проверка рейтинга
    if not isinstance(data['rating'], int) or data['rating'] < 0:
        return jsonify({'error': 'Rating must be a non-negative integer'}), 400
    try:
        review = Review(
            user_id=data['user_id'],
            book_id=data['book_id'],
            text=data['text'],
            rating=data['rating']
        )
        db.session.add(review)
        db.session.commit()
        return jsonify({
            'id': review.id,
            'user_id': review.user_id,
            'book_id': review.book_id,
            'text': review.text,
            'rating': review.rating,
            'timestamp': review.timestamp.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@main.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    Удалить отзыв по id.
    :param review_id: int — ID отзыва
    :return: пустой ответ с кодом 204 или ошибкой
    """
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return '', 204