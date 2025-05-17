import pytest
from app.models import User, Book, Exchange, Review

def test_user_creation():
    """
    Проверяет корректность создания экземпляра User и присвоения полей.
    """
    user = User(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_book_creation():
    """
    Проверяет корректность создания экземпляра Book и присвоения полей.
    """
    book = Book(title="BookTitle", author="AuthorName", description="Desc", owner_id=1)
    assert book.title == "BookTitle"
    assert book.author == "AuthorName"
    assert book.owner_id == 1

def test_exchange_creation():
    """
    Проверяет корректность создания экземпляра Exchange и присвоения полей.
    """
    exchange = Exchange(user_id=1, book_id=2, place="Аудитория B816")
    assert exchange.user_id == 1
    assert exchange.book_id == 2
    assert exchange.place == "Аудитория B816"

def test_review_creation():
    """
    Проверяет корректность создания экземпляра Review и присвоения полей.
    """
    review = Review(user_id=1, book_id=2, text="Отлично!", rating=5)
    assert review.text == "Отлично!"
    assert review.rating == 5
