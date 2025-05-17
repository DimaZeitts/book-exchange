from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flasgger import Swagger

# Инициализация расширений Flask
# db: объект SQLAlchemy для работы с базой данных
# migrate: объект для управления миграциями Alembic
# CORS: поддержка кросс-доменных запросов
# Swagger: автогенерация документации по API

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """
    Фабрика приложения Flask.
    Создаёт и настраивает Flask-приложение, подключает расширения, регистрирует blueprints и документацию Swagger.
    :return: Flask app
    """
    app = Flask(__name__)
    # Настройки подключения к PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Регистрация blueprint с основными маршрутами
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Подключение Swagger для автодокументации
    Swagger(app)

    return app

# Импорт моделей для Alembic и других расширений
from . import models