from flask import Blueprint, request, jsonify
from .models import Book, User, Exchange, Review
from . import db
from .schemas import BookSchema

main = Blueprint('main', __name__)

book_schema = BookSchema()
books_schema = BookSchema(many=True)

@main.route('/')
def index():
    return {"message": "Book Exchange API is running!"}

@main.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify(books_schema.dump(books))

@main.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book_schema.dump(book))

@main.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    book = book_schema.load(data)
    new_book = Book(**book)
    db.session.add(new_book)
    db.session.commit()
    return jsonify(book_schema.dump(new_book)), 201

@main.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(book, key, value)
    db.session.commit()
    return jsonify(book_schema.dump(book))

@main.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return '', 204

@main.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email}), 201

@main.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'email': u.email} for u in users])

@main.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

@main.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

@main.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

@main.route('/exchanges', methods=['GET'])
def get_exchanges():
    exchanges = Exchange.query.all()
    return jsonify([
        {
            'id': e.id,
            'user_id': e.user_id,
            'book_id': e.book_id,
            'timestamp': e.timestamp.isoformat()
        } for e in exchanges
    ])

@main.route('/exchanges', methods=['POST'])
def create_exchange():
    data = request.get_json()
    exchange = Exchange(user_id=data['user_id'], book_id=data['book_id'])
    db.session.add(exchange)
    db.session.commit()
    return jsonify({
        'id': exchange.id,
        'user_id': exchange.user_id,
        'book_id': exchange.book_id,
        'timestamp': exchange.timestamp.isoformat()
    }), 201

@main.route('/exchanges/<int:exchange_id>', methods=['DELETE'])
def delete_exchange(exchange_id):
    exchange = Exchange.query.get_or_404(exchange_id)
    db.session.delete(exchange)
    db.session.commit()
    return '', 204

@main.route('/reviews', methods=['GET'])
def get_reviews():
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
    data = request.get_json()
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

@main.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return '', 204