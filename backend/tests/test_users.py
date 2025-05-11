import pytest
from app import create_app, db

def user_payload(username="testuser", email="testuser@example.com"):
    return {"username": username, "email": email}

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

def test_create_user(client):
    response = client.post('/users', json=user_payload())
    assert response.status_code == 201
    data = response.get_json()
    assert data['username'] == "testuser"
    assert data['email'] == "testuser@example.com"

def test_create_user_empty_username(client):
    response = client.post('/users', json=user_payload(username=""))
    assert response.status_code == 400 or response.status_code == 422

def test_create_user_duplicate_email(client):
    client.post('/users', json=user_payload())
    response = client.post('/users', json=user_payload())
    assert response.status_code == 400 or response.status_code == 409

def test_get_user(client):
    resp = client.post('/users', json=user_payload())
    user_id = resp.get_json()['id']
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == "testuser"

def test_update_user(client):
    resp = client.post('/users', json=user_payload())
    user_id = resp.get_json()['id']
    response = client.put(f'/users/{user_id}', json={"username": "updated", "email": "updated@example.com"})
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == "updated"
    assert data['email'] == "updated@example.com"

def test_delete_user(client):
    resp = client.post('/users', json=user_payload())
    user_id = resp.get_json()['id']
    response = client.delete(f'/users/{user_id}')
    assert response.status_code == 204
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 404
