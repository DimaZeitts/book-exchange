import pytest
from app import create_app, db


def user_payload(username, email):
    return {
        "username": username,
        "email": email
    }


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


def create_user(client, username="testuser", email="testuser@example.com"):
    response = client.post('/users', json=user_payload(username, email))
    assert response.status_code == 201
    return response.get_json()["id"]


def test_create_book(client):
    user_id = create_user(client)
    response = client.post('/books', json={
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description",
        "owner_id": user_id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == "Test Book"


def test_get_books(client):
    user_id = create_user(client)
    client.post('/books', json={
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description",
        "owner_id": user_id
    })
    response = client.get('/books')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_update_book(client):
    user_id = create_user(client)
    client.post('/books', json={
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description",
        "owner_id": user_id
    })
    response = client.put('/books/1', json={
        "title": "Updated Title"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == "Updated Title"


def test_delete_book(client):
    user_id = create_user(client)
    client.post('/books', json={
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description",
        "owner_id": user_id
    })
    response = client.delete('/books/1')
    assert response.status_code == 204
    response = client.get('/books/1')
    assert response.status_code == 404
