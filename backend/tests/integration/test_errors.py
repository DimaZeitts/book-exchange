import pytest
from app import create_app, db


def user_payload(username, email):
    return {"username": username, "email": email}


def book_payload(owner_id, title="Book", author="Author"):
    return {
        "title": title,
        "author": author,
        "description": "desc",
        "owner_id": owner_id
    }


def invalid_book_payload():
    """
    Генерирует некорректный payload для создания книги.
    :return: dict
    """
    return {"title": "", "author": "", "owner_id": None}


@pytest.fixture
def client():
    """
    Фикстура для создания тестового клиента Flask с in-memory БД.
    :yield: Flask test client
    """
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def create_user(client, username="user1", email="user1@example.com"):
    resp = client.post('/users', json=user_payload(username, email))
    return resp.get_json()['id']


def create_book(client, owner_id):
    resp = client.post('/books', json=book_payload(owner_id))
    return resp.get_json()['id']


def test_create_book_with_invalid_owner(client):
    """
    Проверяет, что нельзя создать книгу с несуществующим owner_id.
    Ожидает 400.
    """
    response = client.post(
        '/books',
        json={"title": "Test", "author": "Test", "owner_id": 9999}
    )
    assert response.status_code == 400


def test_create_user_with_empty_email(client):
    """
    Проверяет, что нельзя создать пользователя с пустым email.
    Ожидает 400 или 422.
    """
    response = client.post(
        '/users',
        json={"username": "test", "email": ""}
    )
    assert response.status_code == 400 or response.status_code == 422


def test_get_nonexistent_book(client):
    """
    Проверяет, что запрос к несуществующей книге возвращает 404.
    """
    response = client.get('/books/9999')
    assert response.status_code == 404


def test_update_nonexistent_user(client):
    """
    Проверяет, что обновление несуществующего пользователя возвращает 404.
    """
    response = client.put(
        '/users/9999',
        json={"username": "upd", "email": "upd@e.com"}
    )
    assert response.status_code == 404


def test_delete_nonexistent_review(client):
    """
    Проверяет, что удаление несуществующего отзыва возвращает 404.
    """
    response = client.delete('/reviews/9999')
    assert response.status_code == 404


def test_create_review_with_empty_text(client):
    """
    Проверяет, что нельзя создать отзыв с пустым текстом.
    Ожидает 400.
    """
    response = client.post(
        '/reviews',
        json={"user_id": 1, "book_id": 1, "text": "", "rating": 5}
    )
    assert response.status_code == 400
