import pytest

def capitalize_first_letter(s):
    return s.capitalize() if s else s

def user_greeting(username):
    return f"Привет, {username}!" if username else "Привет, гость!"

def test_capitalize_first_letter():
    assert capitalize_first_letter("hello") == "Hello"
    assert capitalize_first_letter("") == ""
    assert capitalize_first_letter("привет") == "Привет"

def test_user_greeting():
    assert user_greeting("Дмитрий") == "Привет, Дмитрий!"
    assert user_greeting("") == "Привет, гость!"
    assert user_greeting(None) == "Привет, гость!"
