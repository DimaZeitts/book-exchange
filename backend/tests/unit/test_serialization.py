from app.schemas import BookSchema


class Book:
    """
    Пример класса Book для тестирования сериализации/десериализации.
    """
    def __init__(self, title, author, description, owner_id):
        self.title = title
        self.author = author
        self.description = description
        self.owner_id = owner_id


def serialize_book(book):
    """
    Преобразует объект Book в словарь для сериализации.
    """
    return {
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "owner_id": book.owner_id
    }


def deserialize_book(data):
    """
    Преобразует словарь обратно в объект Book.
    """
    return Book(
        title=data["title"],
        author=data["author"],
        description=data["description"],
        owner_id=data["owner_id"]
    )


def test_book_serialization():
    """Проверяет сериализацию книги в JSON."""
    book_data = {
        "id": 1,
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description",
        "is_available": True,
        "owner_id": 1
    }
    schema = BookSchema()
    result = schema.dump(book_data)
    assert result["id"] == 1
    assert result["title"] == "Test Book"
    assert result["author"] == "Test Author"
    assert result["description"] == "Test Description"
    assert result["is_available"] is True
    assert result["owner_id"] == 1


def test_book_deserialization():
    """Проверяет десериализацию JSON в книгу."""
    json_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description",
        "is_available": True,
        "owner_id": 1
    }
    schema = BookSchema()
    result = schema.load(json_data)
    assert result["title"] == "Test Book"
    assert result["author"] == "Test Author"
    assert result["description"] == "Test Description"
    assert result["is_available"] is True
    assert result["owner_id"] == 1


def test_book_validation():
    """Проверяет валидацию данных книги."""
    schema = BookSchema()
    # Проверка обязательных полей
    json_data = {
        "author": "Test Author",
        "description": "Test Description",
        "is_available": True,
        "owner_id": 1
    }
    errors = schema.validate(json_data)
    assert "title" in errors


def test_book_validation_types():
    """Проверяет валидацию типов данных книги."""
    schema = BookSchema()
    json_data = {
        "title": 123,  # Должно быть строкой
        "author": "Test Author",
        "description": "Test Description",
        "is_available": "not a boolean",  # Должно быть булевым
        "owner_id": "not an integer"  # Должно быть целым числом
    }
    errors = schema.validate(json_data)
    assert "title" in errors
    assert "is_available" in errors
    assert "owner_id" in errors
