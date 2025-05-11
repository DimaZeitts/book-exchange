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

def test_create_review(client):
    user_id = create_user(client)
    book_id = create_book(client, user_id)
    resp = client.post('/reviews', json={"user_id": user_id, "book_id": book_id, "text": "Nice!", "rating": 5})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['user_id'] == user_id
    assert data['book_id'] == book_id
    assert data['rating'] == 5

def test_create_review_invalid_rating(client):
    user_id = create_user(client)
    book_id = create_book(client, user_id)
    resp = client.post('/reviews', json={"user_id": user_id, "book_id": book_id, "text": "Bad", "rating": -1})
    assert resp.status_code == 400 or resp.status_code == 422

def test_get_reviews(client):
    user_id = create_user(client)
    book_id = create_book(client, user_id)
    client.post('/reviews', json={"user_id": user_id, "book_id": book_id, "text": "Nice!", "rating": 5})
    resp = client.get('/reviews')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 1

def test_delete_review(client):
    user_id = create_user(client)
    book_id = create_book(client, user_id)
    resp = client.post('/reviews', json={"user_id": user_id, "book_id": book_id, "text": "Nice!", "rating": 5})
    review_id = resp.get_json()['id']
    del_resp = client.delete(f'/reviews/{review_id}')
    assert del_resp.status_code == 204
    # Повторное удаление должно вернуть 404
    del_resp2 = client.delete(f'/reviews/{review_id}')
    assert del_resp2.status_code == 404
