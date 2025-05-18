from marshmallow import Schema, fields

class BookSchema(Schema):
    """
    Схема сериализации/десериализации для модели Book с помощью marshmallow.
    Поля:
        id (Int, dump_only): Уникальный идентификатор книги.
        title (Str, required): Название книги (обязательное).
        author (Str, required): Автор книги (обязательное).
        description (Str): Описание книги (опционально).
        owner_id (Int, required): ID владельца книги (обязательное).
        is_available (Bool): Доступна ли книга для обмена (по умолчанию True).
    """
    id = fields.Int(dump_only=True)  # Только для чтения
    title = fields.Str(required=True)  # Название книги
    author = fields.Str(required=True)  # Автор книги
    description = fields.Str()  # Описание книги
    owner_id = fields.Int(required=True)  # ID владельца
    is_available = fields.Bool()  # Доступность для обмена
