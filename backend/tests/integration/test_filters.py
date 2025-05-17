import pytest
from app import create_app, db

def user_payload(username, email):
    return {"username": username, "email": email}

def book_payload(title, author, is_available=True, owner_id=1):
    """
    Генерирует словарь с данными книги для тестов фильтрации.
    :param title: str — название книги
    :param author: str — автор книги
    :param is_available: bool — доступность
    :param owner_id: int — ID владельца
    :return: dict
    """
    return {"title": title, "author": author, "is_available": is_available, "owner_id": owner_id}

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

def test_filter_by_author(client):
    """
    Проверяет фильтрацию книг по автору через GET /books?author=...
    Ожидает 200 и корректный результат.
    """
    user_id = create_user(client)
    client.post('/books', json=book_payload("Book1", "AuthorA", owner_id=user_id))
    client.post('/books', json=book_payload("Book2", "AuthorB", owner_id=user_id))
    response = client.get('/books?author=AuthorA')
    assert response.status_code == 200
    data = response.get_json()
    assert all("AuthorA" in b['author'] for b in data)

def test_filter_by_title(client):
    """
    Проверяет фильтрацию книг по названию через GET /books?title=...
    Ожидает 200 и корректный результат.
    """
    user_id = create_user(client)
    client.post('/books', json=book_payload("Book1", "AuthorA", owner_id=user_id))
    client.post('/books', json=book_payload("Book2", "AuthorB", owner_id=user_id))
    response = client.get('/books?title=Book2')
    assert response.status_code == 200
    data = response.get_json()
    assert all("Book2" in b['title'] for b in data)

def test_filter_by_is_available(client):
    """
    Проверяет фильтрацию книг по доступности через GET /books?is_available=...
    Ожидает 200 и корректный результат.
    """
    user_id = create_user(client)
    client.post('/books', json=book_payload("Book1", "AuthorA", is_available=True, owner_id=user_id))
    client.post('/books', json=book_payload("Book2", "AuthorB", is_available=False, owner_id=user_id))
    response = client.get('/books?is_available=true')
    assert response.status_code == 200
    data = response.get_json()
    assert all(b['is_available'] for b in data)
    resp2 = client.get('/books?is_available=false')
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert all(not b['is_available'] for b in data2)

def test_filter_empty_result(client):
    """
    Проверяет, что фильтрация по несуществующему значению возвращает пустой список.
    """
    user_id = create_user(client)
    client.post('/books', json=book_payload("Book1", "AuthorA", owner_id=user_id))
    response = client.get('/books?author=Nonexistent')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []
