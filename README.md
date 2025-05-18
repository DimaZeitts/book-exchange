# Book Exchange (Обмен книгами в ЦУ)

## Описание проекта

Веб-приложение для обмена книгами между пользователями. Пользователи могут регистрироваться, добавлять книги, оставлять отзывы, обмениваться книгами и просматривать историю обменов. Проект реализован с использованием современных технологий и полностью покрыт unit- и интеграционными тестами.

---

## Стек технологий

- **Backend:** Python, Flask, SQLAlchemy, Alembic, Marshmallow, PostgreSQL, Docker
- **Frontend:** React, Axios, Material-UI (или ваш UI-фреймворк)
- **Тесты:** Pytest (unit и integration)
- **Документация:** Swagger (Flasgger)
- **CI/CD:** GitLab CI
- **DevOps:** Docker, docker-compose

---

## Внедренные фичи

- Регистрация и аутентификация пользователей
- CRUD для книг
- Система обмена книгами между пользователями
- Оставление и просмотр отзывов
- История обменов для каждого пользователя
- Фильтрация и поиск книг
- Swagger-документация для API
- Unit- и интеграционные тесты
- Автоматическая проверка кода на PEP8/flake8
- Хранение данных в Docker volume (данные не теряются при перезапуске контейнеров)

---

## Структура проекта

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── ...
│   ├── migrations/
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   └── ...
│   ├── package.json
│   └── ...
├── docker-compose.yml
├── .gitlab-ci.yml
├── .flake8
├── README.md
```

---

## Как запустить проект

**1. Клонируйте репозиторий:**
```bash
git clone <URL>
cd <project-folder>
```

**2. Запустите проект через Docker:**
```bash
docker-compose up -d --build
docker-compose exec backend flask db upgrade
```

**3. Запустите фронтенд (если не в Docker):**
```bash
cd frontend
npm install (если запускаете у себя на устройстве впервые)
npm start
```

---

## Проверка тестов

**Unit-тесты (запускать из контейнера backend):**
```bash
docker-compose exec backend bash
pytest tests/unit
```

**Интеграционные тесты (запускать из контейнера backend):**
```bash
docker-compose exec backend bash
pytest tests/integration
```

---

## Проверка кода на flake8

```bash
docker-compose exec backend bash
flake8 app tests
```
(или используйте вашу команду, если путь отличается)

---

## Порты

- **Backend (Flask API):** http://localhost:5050
- **Frontend (React):** http://localhost:3000
- **PostgreSQL:** localhost:5432 (только для подключения к БД)

---

## Swagger (документация API)

Swagger доступен по адресу:  
**http://localhost:5050/apidocs**

---

## Примечания

- Все данные БД сохраняются в Docker volume `book_exchange_postgres_data`
- Для полного сброса данных используйте:  
  ```bash
  docker-compose down -v
  ```

---

## Контакты студента для проверяющего

- **TIMe:** Дмитрий Зейтц
- **Telegram:** [@k0oMmersant](https://t.me/k0oMmersant)

---
