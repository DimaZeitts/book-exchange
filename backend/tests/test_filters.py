import pytest
from app import create_app, db

def user_payload(username, email):
    return {"username": username, "email": email}

def book_payload(owner_id, title, author, is_available=True):
    return {"title": title, "author": author, "description": "desc", "owner_id": owner_id, "is_available": is_available}

@pytest.fixture
def client():
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
    user_id = create_user(client)
    client.post('/books', json=book_payload(user_id, "Book1", "AuthorA"))
    client.post('/books', json=book_payload(user_id, "Book2", "AuthorB"))
    resp = client.get('/books?author=AuthorA')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['author'] == "AuthorA"

def test_filter_by_title(client):
    user_id = create_user(client)
    client.post('/books', json=book_payload(user_id, "UniqueTitle", "AuthorA"))
    resp = client.get('/books?title=UniqueTitle')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['title'] == "UniqueTitle"

def test_filter_by_is_available(client):
    user_id = create_user(client)
    client.post('/books', json=book_payload(user_id, "Book1", "AuthorA", is_available=True))
    client.post('/books', json=book_payload(user_id, "Book2", "AuthorA", is_available=False))
    resp = client.get('/books?is_available=true')
    assert resp.status_code == 200
    data = resp.get_json()
    assert all(book['is_available'] for book in data)
    resp2 = client.get('/books?is_available=false')
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert all(not book['is_available'] for book in data2)

def test_filter_empty_result(client):
    user_id = create_user(client)
    client.post('/books', json=book_payload(user_id, "Book1", "AuthorA"))
    resp = client.get('/books?author=Nonexistent')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == []
