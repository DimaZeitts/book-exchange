import re


def is_valid_email(email):
    """
    Проверяет, соответствует ли email простому регулярному выражению.
    """
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def test_valid_email():
    """
    Проверяет корректность работы функции is_valid_email
    для валидных и невалидных email.
    """
    assert is_valid_email("user@example.com")
    assert is_valid_email(
        "test.user@domain.ru"
    )
    assert not is_valid_email("userexample.com")
    assert not is_valid_email("user@.com")
    assert not is_valid_email("")


def test_required_field():
    """
    Проверяет, что функция is_required
    корректно определяет обязательность поля.
    """
    def is_required(value):
        """Возвращает True, если значение не None и не пустая строка."""
        return value is not None and value != ''

    assert is_required(
        "something"
    )
    assert not is_required("")
    assert not is_required(None)
