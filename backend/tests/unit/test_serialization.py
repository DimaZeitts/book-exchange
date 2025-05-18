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
    """
    Проверяет корректность сериализации и десериализации Book.
    """
    book = Book("BookTitle", "AuthorName", "Desc", 1)
    data = serialize_book(book)
    assert data == {
        "title": "BookTitle",
        "author": "AuthorName",
        "description": "Desc",
        "owner_id": 1
    }
    book2 = deserialize_book(data)
    assert book2.title == "BookTitle"
    assert book2.author == "AuthorName"
    assert book2.owner_id == 1
