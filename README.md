# django_rest_framework

Серверное приложение для системы управления обучением (LMS). Проект представляет собой REST API, реализованное на Django и Django REST Framework (DRF), с полноценным CRUD-функционалом для управления курсами, уроками и профилями пользователей.

## Стек технологий
* Python 3.x
* Django 5.x
* Django REST Framework (DRF)
* Django-environ (управление переменными окружения)
* SQLite (db.sqlite3)

## Реализованный функционал

### 1. Управление пользователями (`users`)
* Авторизация переопределена на **Email** вместо стандартного `username`.
* Модель пользователя расширена полями: `email`, `phone`, `city`, `avatar`.
* Реализован Generic-эндпоинт (`UpdateAPIView`) для редактирования профиля любого пользователя.

### 2. Управление обучением (`lms`)
* **Курсы**: CRUD реализован с использованием `ModelViewSet`. При просмотре курса выводится список всех связанных с ним уроков.
* **Уроки**: CRUD реализован с использованием раздельных Generic-классов (`CreateAPIView`, `ListAPIView`, `RetrieveAPIView`, `UpdateAPIView`, `DestroyAPIView`).
* Между курсами и уроками настроена связь «один ко многим» (`ForeignKey`).

---

## Инструкция по локальному развертыванию

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com
   cd django_rest_framework
   ```

2. **Cоздайте и активируйте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Linux/macOS
   venv\Scripts\activate     # Для Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install django djangorestframework pillow django-environ
   ```

4. **Настройте переменные окружения:**
   Создайте файл `.env` в корневой директории и добавьте конфигурацию:
   ```text
   DEBUG=True
   SECRET_KEY=ваш_секретный_ключ_django
   ```

5. **Выполните миграции базы данных:**
   ```bash
   python manage.py migrate
   ```

6. **Запустите локальный сервер:**
   ```bash
   python manage.py runserver
   ```

---

## Примеры эндпоинтов (Тестирование в Postman)

### Курсы (ViewSets)
* `GET /lms/courses/` — Получить список всех курсов
* `POST /lms/courses/` — Создать новый курс (Передать JSON: `title`, `description`)
* `GET /lms/courses/<id>/` — Получить детальную информацию о курсе
* `PUT/PATCH /lms/courses/<id>/` — Редактировать курс
* `DELETE /lms/courses/<id>/` — Удалить курс

### Уроки (Generics)
* `GET /lms/lessons/` — Получить список всех уроков
* `POST /lms/lessons/create/` — Создать новый урок (Передать JSON: `title`, `description`, `video_url`, `course`)
* `GET /lms/lessons/<id>/` — Получить детальную информацию об уроке
* `PUT/PATCH /lms/lessons/update/<id>/` — Редактировать урок
* `DELETE /lms/lessons/delete/<id>/` — Удалить урок

### Профиль пользователя
* `PATCH /users/update/<id>/` — Частичное редактирование профиля пользователя
