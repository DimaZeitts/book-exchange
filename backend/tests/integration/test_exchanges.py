import pytest
from app import create_app, db

def user_payload(username, email):
    return {"username": username, "email": email}

def book_payload(owner_id, title="Book", author="Author"):
    return {"title": title, "author": author, "description": "desc", "owner_id": owner_id}

def exchange_payload(user_id=1, book_id=1, place="Аудитория B816"):
    """
    Генерирует словарь с данными обмена для тестов.
    :param user_id: int — ID пользователя
    :param book_id: int — ID книги
    :param place: str — место обмена
    :return: dict
    """
    return {"user_id": user_id, "book_id": book_id, "place": place}

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

def test_create_exchange(client):
    """
    Проверяет успешное создание обмена через POST /exchanges.
    Ожидает 201 и корректные данные.
    """
    user_id = create_user(client)
    book_id = create_book(client, user_id)
    resp = client.post('/exchanges', json={"user_id": user_id, "book_id": book_id})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['user_id'] == user_id
    assert data['book_id'] == book_id

def test_create_exchange_invalid_user(client):
    """
    Проверяет, что нельзя создать обмен с несуществующим user_id.
    Ожидает 400.
    """
    user_id = 999
    book_id = 1
    resp = client.post('/exchanges', json={"user_id": user_id, "book_id": book_id})
    assert resp.status_code == 400 or resp.status_code == 404

def test_get_exchanges(client):
    """
    Проверяет получение списка обменов через GET /exchanges.
    Ожидает 200 и наличие созданного обмена.
    """
    user_id = create_user(client)
    book_id = create_book(client, user_id)
    client.post('/exchanges', json={"user_id": user_id, "book_id": book_id})
    resp = client.get('/exchanges')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 1

def test_delete_exchange(client):
    """
    Проверяет удаление обмена через DELETE /exchanges/<id>.
    Ожидает 204 и отсутствие после удаления.
    """
    user_id = create_user(client)
    book_id = create_book(client, user_id)
    resp = client.post('/exchanges', json={"user_id": user_id, "book_id": book_id})
    exch_id = resp.get_json()['id']
    del_resp = client.delete(f'/exchanges/{exch_id}')
    assert del_resp.status_code == 204
    # Повторное удаление должно вернуть 404
    del_resp2 = client.delete(f'/exchanges/{exch_id}')
    assert del_resp2.status_code == 404
