from flask import Blueprint, request, jsonify
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
    Получить список книг.
    ---
    tags:
      - Books
    parameters:
      - name: author
        in: query
        type: string
        required: false
        description: Фильтр по автору
      - name: title
        in: query
        type: string
        required: false
        description: Фильтр по названию
      - name: is_available
        in: query
        type: boolean
        required: false
        description: Фильтр по доступности
    responses:
      200:
        description: Список книг
    """
    author = request.args.get('author')
    title = request.args.get('title')
    is_available = request.args.get('is_available')

    query = Book.query

    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if is_available is not None:
        is_available_bool = is_available.lower() in [
            'true', '1', 'yes'
        ]
        query = query.filter(Book.is_available == is_available_bool)

    books = query.all()
    result = []
    for b in books:
        book_data = book_schema.dump(b)
        book_data['owner_username'] = b.owner.username if b.owner else None
        result.append(book_data)
    return jsonify(result)


@main.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Получить книгу по id.
    ---
    tags:
      - Books
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
        description: ID книги
    responses:
      200:
        description: Данные книги
      404:
        description: Книга не найдена
    """
    book = Book.query.get_or_404(book_id)
    return jsonify(book_schema.dump(book))


@main.route('/books', methods=['POST'])
def create_book():
    """
    Добавить новую книгу.
    ---
    tags:
      - Books
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            author:
              type: string
            description:
              type: string
            owner_id:
              type: integer
    responses:
      201:
        description: Книга создана
      400:
        description: Ошибка валидации
    """
    data = request.get_json()
    for field in ['title', 'author', 'owner_id']:
        if not data.get(field):
            return jsonify({'error': f'Missing or empty field: {field}'}), 400
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
    ---
    tags:
      - Books
    consumes:
      - application/json
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
        description: ID книги
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            author:
              type: string
            description:
              type: string
            owner_id:
              type: integer
            is_available:
              type: boolean
    responses:
      200:
        description: Книга обновлена
      404:
        description: Книга не найдена
    """
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
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
    ---
    tags:
      - Books
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
        description: ID книги
    responses:
      204:
        description: Книга удалена
      404:
        description: Книга не найдена
    """
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return '', 204


@main.route('/users', methods=['POST'])
def create_user():
    """
    Создать пользователя.
    ---
    tags:
      - Users
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
    responses:
      201:
        description: Пользователь создан
      400:
        description: Ошибка валидации
      409:
        description: Email или username уже существует
    """
    data = request.get_json()
    for field in ['username', 'email']:
        if not data.get(field):
            return jsonify({'error': f'Missing or empty field: {field}'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'error': 'Пользователь с такой почтой уже зарегистрирован'
        }), 409
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'error': 'Пользователь с таким именем уже зарегистрирован'
        }), 409
    try:
        user = User(username=data['username'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Integrity error'}), 400


@main.route('/users', methods=['GET'])
def get_users():
    """
    Получить список всех пользователей или по email.
    ---
    tags:
      - Users
    parameters:
      - name: email
        in: query
        type: string
        required: false
        description: Email для поиска
    responses:
      200:
        description: Список пользователей
    """
    email = request.args.get('email')
    if email:
        users = User.query.filter_by(email=email).all()
    else:
        users = User.query.all()
    return jsonify([
        {'id': u.id, 'username': u.username, 'email': u.email}
        for u in users
    ])


@main.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Получить пользователя по id.
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID пользователя
    responses:
      200:
        description: Данные пользователя
      404:
        description: Пользователь не найден
    """
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })


@main.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Обновить пользователя по id.
    ---
    tags:
      - Users
    consumes:
      - application/json
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID пользователя
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
    responses:
      200:
        description: Пользователь обновлён
      404:
        description: Пользователь не найден
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })


@main.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Удалить пользователя по id.
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID пользователя
    responses:
      204:
        description: Пользователь удалён
      404:
        description: Пользователь не найден
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
    ---
    tags:
      - Exchanges
    parameters:
      - name: user_id
        in: query
        type: integer
        required: false
        description: Фильтр по инициатору обмена
      - name: owner_id
        in: query
        type: integer
        required: false
        description: Фильтр по владельцу книги
    responses:
      200:
        description: Список обменов
    """
    user_id = request.args.get('user_id')
    owner_id = request.args.get('owner_id')
    query = Exchange.query
    if user_id:
        query = query.filter(Exchange.user_id == int(user_id))
    if owner_id:
        user_books = Book.query.filter(Book.owner_id == int(owner_id)).all()
        user_book_ids = [b.id for b in user_books]
        query = query.filter(Exchange.book_id.in_(user_book_ids))
    exchanges = query.all()
    result = []
    for e in exchanges:
        book = Book.query.get(e.book_id)
        result.append({
            'id': e.id,
            'user_id': e.user_id,
            'book_id': e.book_id,
            'book_title': book.title if book else None,
            'offered_book_title': None,
            'place': e.place,
            'timestamp': (
                e.timestamp.isoformat()
                if e.timestamp else None
            ),
            'status': e.status
        })
    return jsonify(result)


@main.route('/exchanges', methods=['POST'])
def create_exchange():
    """
    Создать обмен.
    ---
    tags:
      - Exchanges
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
            book_id:
              type: integer
            place:
              type: string
    responses:
      201:
        description: Обмен создан
      400:
        description: Ошибка валидации
    """
    data = request.get_json()
    for field in ['user_id', 'book_id']:
        if not data.get(field):
            return jsonify({'error': f'Missing or empty field: {field}'}), 400
    user = User.query.get(data['user_id'])
    book = Book.query.get(data['book_id'])
    if not user or not book:
        return jsonify({'error': 'User or Book not found'}), 400
    try:
        exchange = Exchange(
            user_id=data['user_id'],
            book_id=data['book_id'],
            place=data.get('place')
        )
        db.session.add(exchange)
        db.session.commit()
        return jsonify({
            'id': exchange.id,
            'user_id': exchange.user_id,
            'book_id': exchange.book_id,
            'place': exchange.place,
            'timestamp': (
                exchange.timestamp.isoformat()
                if exchange.timestamp else None
            )
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@main.route('/exchanges/<int:exchange_id>', methods=['DELETE'])
def delete_exchange(exchange_id):
    """
    Удалить обмен по id.
    ---
    tags:
      - Exchanges
    parameters:
      - name: exchange_id
        in: path
        type: integer
        required: true
        description: ID обмена
    responses:
      204:
        description: Обмен удалён
      404:
        description: Обмен не найден
    """
    exchange = Exchange.query.get_or_404(exchange_id)
    db.session.delete(exchange)
    db.session.commit()
    return '', 204


@main.route('/exchanges/<int:exchange_id>', methods=['PUT'])
def update_exchange(exchange_id):
    """
    Обновить статус обмена (принять/отклонить).
    ---
    tags:
      - Exchanges
    consumes:
      - application/json
    parameters:
      - name: exchange_id
        in: path
        type: integer
        required: true
        description: ID обмена
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            action:
              type: string
              enum: [accept, reject]
    responses:
      200:
        description: Статус обмена обновлён
      404:
        description: Обмен не найден
    """
    exchange = Exchange.query.get_or_404(exchange_id)
    data = request.get_json()
    action = data.get('action')
    if action == 'accept':
        exchange.status = 'accepted'
    elif action == 'reject':
        exchange.status = 'rejected'
    else:
        return jsonify({'error': 'Invalid action'}), 400
    db.session.commit()
    return jsonify({'id': exchange.id, 'status': exchange.status})


@main.route('/reviews', methods=['GET'])
def get_reviews():
    """
    Получить список всех отзывов.
    ---
    tags:
      - Reviews
    responses:
      200:
        description: Список отзывов
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
    ---
    tags:
      - Reviews
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
            book_id:
              type: integer
            text:
              type: string
            rating:
              type: integer
    responses:
      201:
        description: Отзыв создан
      400:
        description: Ошибка валидации
    """
    data = request.get_json()
    for field in ['user_id', 'book_id', 'text', 'rating']:
        if field not in data or data[field] is None or (
            isinstance(data[field], str) and not data[field].strip()
        ):
            return jsonify({'error': f'Missing or empty field: {field}'}), 400
    user = User.query.get(data['user_id'])
    book = Book.query.get(data['book_id'])
    if not user or not book:
        return jsonify({'error': 'User or Book not found'}), 400
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
            'timestamp': (
                review.timestamp.isoformat()
            )
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@main.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    Удалить отзыв по id.
    ---
    tags:
      - Reviews
    parameters:
      - name: review_id
        in: path
        type: integer
        required: true
        description: ID отзыва
    responses:
      204:
        description: Отзыв удалён
      404:
        description: Отзыв не найден
    """
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return '', 204
