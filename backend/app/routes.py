from flask import Blueprint, request, jsonify
from .models import Book
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
    return books_schema.jsonify(books)

@main.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return book_schema.jsonify(book)

@main.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    book = book_schema.load(data)
    new_book = Book(**book)
    db.session.add(new_book)
    db.session.commit()
    return book_schema.jsonify(new_book), 201

@main.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(book, key, value)
    db.session.commit()
    return book_schema.jsonify(book)

@main.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return '', 204