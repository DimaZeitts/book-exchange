def can_exchange(user_id, book_owner_id):
    """
    Проверяет, может ли пользователь обменять книгу 
    (нельзя обменять свою же книгу).
    :param user_id: int — ID пользователя
    :param book_owner_id: int — ID владельца книги
    :return: bool — True, если обмен возможен
    """
    # Пользователь не может обменять свою же книгу
    return user_id != book_owner_id


def test_can_exchange():
    """
    Проверяет работу функции can_exchange для разных случаев (свой/чужой).
    """
    assert can_exchange(1, 2) is True
    assert can_exchange(2, 1) is True
    assert can_exchange(1, 1) is False
