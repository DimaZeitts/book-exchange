import pytest
from app import create_app, db
import uuid


def user_payload(username="testuser", email="testuser@example.com"):
    """
    Генерирует словарь с данными пользователя для тестов.
    :param username: str — имя пользователя
    :param email: str — email пользователя
    :return: dict
    """
    return {"username": username, "email": email}


@pytest.fixture
def client():
    """
    Фикстура для создания тестового клиента Flask с изолированной in-memory БД.
    Создаёт и удаляет все таблицы до/после теста.
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


def test_create_user(client):
    """
    Проверяет успешное создание пользователя через POST /users.
    Ожидает 201 и корректные данные в ответе.
    """
    username = f"testuser_{uuid.uuid4()}"
    email = f"{username}@example.com"
    response = client.post('/users', json=user_payload(username, email))
    assert response.status_code == 201
    data = response.get_json()
    assert data['username'] == username
    assert data['email'] == email


def test_create_user_empty_username(client):
    """
    Проверяет, что нельзя создать пользователя с пустым username.
    Ожидает 400 или 422.
    """
    response = client.post('/users', json=user_payload(username=""))
    assert response.status_code == 400 or response.status_code == 422


def test_create_user_duplicate_email(client):
    """
    Проверяет, что нельзя создать двух пользователей с одинаковым email.
    Ожидает 400 или 409.
    """
    client.post('/users', json=user_payload())
    response = client.post('/users', json=user_payload())
    assert response.status_code == 400 or response.status_code == 409


def test_get_user(client):
    """
    Проверяет получение пользователя по id через GET /users/<id>.
    Ожидает 200 и корректные данные.
    """
    resp = client.post('/users', json=user_payload())
    user_id = resp.get_json()['id']
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == "testuser"


def test_update_user(client):
    """
    Проверяет обновление пользователя через PUT /users/<id>.
    Ожидает 200 и обновлённые данные.
    """
    resp = client.post('/users', json=user_payload())
    user_id = resp.get_json()['id']
    response = client.put(
        f'/users/{user_id}',
        json={
            "username": "updated",
            "email": "updated@example.com"
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == "updated"
    assert data['email'] == "updated@example.com"


def test_delete_user(client):
    """
    Проверяет удаление пользователя через
    DELETE /users/<id> и отсутствие после удаления.
    Ожидает 204 и 404 при повторном запросе.
    """
    resp = client.post('/users', json=user_payload())
    user_id = resp.get_json()['id']
    response = client.delete(f'/users/{user_id}')
    assert response.status_code == 204
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 404
