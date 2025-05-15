import pytest
from app import create_app, db

def user_payload(username, email):
    return {"username": username, "email": email}

def book_payload(owner_id, title="Book", author="Author"):
    return {"title": title, "author": author, "description": "desc", "owner_id": owner_id}

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

def create_book(client, owner_id):
    resp = client.post('/books', json=book_payload(owner_id))
    return resp.get_json()['id']

def test_create_book_with_invalid_owner(client):
    resp = client.post('/books', json=book_payload(999))
    assert resp.status_code == 400 or resp.status_code == 404

def test_create_user_with_empty_email(client):
    resp = client.post('/users', json=user_payload("user", ""))
    assert resp.status_code == 400 or resp.status_code == 422

def test_get_nonexistent_book(client):
    resp = client.get('/books/999')
    assert resp.status_code == 404

def test_update_nonexistent_user(client):
    resp = client.put('/users/999', json={"username": "x", "email": "x@x.com"})
    assert resp.status_code == 404

def test_delete_nonexistent_review(client):
    resp = client.delete('/reviews/999')
    assert resp.status_code == 404

def test_create_review_with_empty_text(client):
    user_id = create_user(client)
    book_id = create_book(client, user_id)
    resp = client.post('/reviews', json={"user_id": user_id, "book_id": book_id, "text": "", "rating": 5})
    assert resp.status_code == 400 or resp.status_code == 422
