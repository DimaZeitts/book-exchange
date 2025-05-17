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
            - backref='owner': позволяет получить владельца книги через book.owner
            - lazy=True: связанные объекты загружаются при обращении
            - cascade="all, delete-orphan": при удалении пользователя удаляются все его книги
        exchanges (relationship): Обмены, инициированные пользователем.
            - backref='user': позволяет получить пользователя через exchange.user
            - lazy=True
            - cascade="all, delete-orphan"
        reviews (relationship): Отзывы, оставленные пользователем.
            - backref='user': позволяет получить пользователя через review.user
            - lazy=True
            - cascade="all, delete-orphan"
    """
    id = db.Column(db.Integer, primary_key=True)  # PRIMARY KEY
    username = db.Column(db.String(64), unique=True, nullable=False)  # Уникальное имя пользователя
    email = db.Column(db.String(120), unique=True, nullable=False)  # Уникальный email
    books = db.relationship(
        'Book', backref='owner', lazy=True, cascade="all, delete-orphan"
    )
    exchanges = db.relationship(
        'Exchange', backref='user', lazy=True, cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        'Review', backref='user', lazy=True, cascade="all, delete-orphan"
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
    id = db.Column(db.Integer, primary_key=True)  # PRIMARY KEY
    title = db.Column(db.String(128), nullable=False)  # Название книги
    author = db.Column(db.String(128), nullable=False)  # Автор книги
    description = db.Column(db.Text)  # Описание книги
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Владелец
    is_available = db.Column(db.Boolean, default=True)  # Доступна ли для обмена
    exchanges = db.relationship(
        'Exchange', backref='book', lazy=True, cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        'Review', backref='book', lazy=True, cascade="all, delete-orphan"
    )

class Exchange(db.Model):
    """
    Модель обмена книгой между пользователями.
    Атрибуты:
        id (int): Уникальный идентификатор обмена (PRIMARY KEY).
        user_id (int): ID пользователя, инициировавшего обмен (FOREIGN KEY на User).
        book_id (int): ID книги, участвующей в обмене (FOREIGN KEY на Book).
        place (str): Место обмена (выбирается из списка, опционально).
        timestamp (datetime): Дата и время создания заявки на обмен (по умолчанию текущее время).
    """
    id = db.Column(db.Integer, primary_key=True)  # PRIMARY KEY
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Пользователь
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)  # Книга
    place = db.Column(db.String(128), nullable=True)  # Место обмена
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Время создания

class Review(db.Model):
    """
    Модель отзыва на книгу.
    Атрибуты:
        id (int): Уникальный идентификатор отзыва (PRIMARY KEY).
        user_id (int): ID пользователя, оставившего отзыв (FOREIGN KEY на User).
        book_id (int): ID книги, на которую оставлен отзыв (FOREIGN KEY на Book).
        text (str): Текст отзыва (обязательное поле).
        rating (int): Оценка книги (обязательное поле).
        timestamp (datetime): Дата и время создания отзыва (по умолчанию текущее время).
    """
    id = db.Column(db.Integer, primary_key=True)  # PRIMARY KEY
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Пользователь
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)  # Книга
    text = db.Column(db.Text, nullable=False)  # Текст отзыва
    rating = db.Column(db.Integer, nullable=False)  # Оценка
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Время создания
