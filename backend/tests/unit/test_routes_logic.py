import pytest

def can_exchange(user_id, book_owner_id):
    # Пользователь не может обменять свою же книгу
    return user_id != book_owner_id

def test_can_exchange():
    assert can_exchange(1, 2) is True
    assert can_exchange(2, 1) is True
    assert can_exchange(1, 1) is False
