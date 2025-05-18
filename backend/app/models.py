from . import db
from datetime import datetime


class User(db.Model):
    """
    Модель пользователя системы обмена книгами.
    Атрибуты:
        id (int): Уникальный идентификатор пользователя (PRIMARY KEY).
        username (str): Имя пользователя (уникальное, не может быть пустым).
        email (str): Email пользователя (уникальный, не может быть пустым).
        books (relationship): Книги, опубликованные пользователем.
            - backref='owner': позволяет получить владельца книги через
              book.owner
            - lazy=True: связанные объекты загружаются при обращении
            - cascade="all, delete-orphan": при удалении пользователя
              удаляются все его книги
        exchanges (relationship): Обмены, инициированные пользователем.
            - backref='user': позволяет получить пользователя через
              exchange.user
            - lazy=True
            - cascade="all, delete-orphan"
        reviews (relationship): Отзывы, оставленные пользователем.
            - backref='user': позволяет получить пользователя через
              review.user
            - lazy=True
            - cascade="all, delete-orphan"
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    books = db.relationship(
        'Book',
        backref='owner',
        lazy=True,
        cascade="all, delete-orphan"
    )
    exchanges = db.relationship(
        'Exchange',
        backref='user',
        lazy=True,
        cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        'Review',
        backref='user',
        lazy=True,
        cascade="all, delete-orphan"
    )


class Book(db.Model):
    """
    Модель книги, доступной для обмена.
    Атрибуты:
        id (int): Уникальный идентификатор книги (PRIMARY KEY).
        title (str): Название книги (обязательное).
        author (str): Автор книги (обязательное).
        description (str): Описание книги (опционально).
        owner_id (int): ID владельца книги (FOREIGN KEY на User).
        is_available (bool): Доступна ли книга для обмена (по умолчанию True).
        exchanges (relationship): Обмены, связанные с книгой.
            - backref='book': позволяет получить книгу через exchange.book
            - lazy=True
            - cascade="all, delete-orphan"
        reviews (relationship): Отзывы на книгу.
            - backref='book': позволяет получить книгу через review.book
            - lazy=True
            - cascade="all, delete-orphan"
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    author = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    exchanges = db.relationship(
        'Exchange',
        backref='book',
        lazy=True,
        cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        'Review',
        backref='book',
        lazy=True,
        cascade="all, delete-orphan"
    )


class Exchange(db.Model):
    """
    Модель обмена книгой между пользователями.
    Атрибуты:
        id (int): Уникальный идентификатор обмена (PRIMARY KEY).
        user_id (int): ID пользователя, инициировавшего обмен.
        book_id (int): ID книги, участвующей в обмене (FOREIGN KEY на Book).
        place (str): Место обмена (выбирается из списка, опционально).
        timestamp (datetime): Дата и время создания заявки на обмен.
        status (str): Статус обмена: pending/accepted/rejected
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    place = db.Column(db.String(128), nullable=True)
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    status = db.Column(
        db.String(20),
        default='pending'
    )


class Review(db.Model):
    """
    Модель отзыва на книгу.
    Атрибуты:
        id (int): Уникальный идентификатор отзыва (PRIMARY KEY).
        user_id (int): ID пользователя, оставившего отзыв.
        book_id (int): ID книги, на которую оставлен отзыв.
        text (str): Текст отзыва (обязательное поле).
        rating (int): Оценка книги (обязательное поле).
        timestamp (datetime): Дата и время создания отзыва.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
