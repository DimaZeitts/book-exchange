import re
import pytest

def is_valid_email(email):
    # Пример простой валидации email
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def test_valid_email():
    assert is_valid_email("user@example.com")
    assert is_valid_email("test.user@domain.ru")
    assert not is_valid_email("userexample.com")
    assert not is_valid_email("user@.com")
    assert not is_valid_email("")

def test_required_field():
    # Пример проверки обязательного поля
    def is_required(value):
        return value is not None and value != ''
    assert is_required("something")
    assert not is_required("")
    assert not is_required(None)
