import pytest

def capitalize_first_letter(s):
    """
    Возвращает строку с заглавной первой буквой, если строка не пуста.
    """
    return s.capitalize() if s else s

def user_greeting(username):
    """
    Генерирует приветствие для пользователя по имени, либо для гостя.
    """
    return f"Привет, {username}!" if username else "Привет, гость!"

def test_capitalize_first_letter():
    """
    Проверяет работу функции capitalize_first_letter для разных случаев.
    """
    assert capitalize_first_letter("hello") == "Hello"
    assert capitalize_first_letter("") == ""
    assert capitalize_first_letter("привет") == "Привет"

def test_user_greeting():
    """
    Проверяет работу функции user_greeting для разных имён и пустого значения.
    """
    assert user_greeting("Дмитрий") == "Привет, Дмитрий!"
    assert user_greeting("") == "Привет, гость!"
    assert user_greeting(None) == "Привет, гость!"
