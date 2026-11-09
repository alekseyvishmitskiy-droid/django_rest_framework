# django_rest_framework

REST API для системы управления обучением (LMS) на Django и Django REST Framework.

## Стек технологий
* Python 3.x, Django 5.x, DRF
* Django-filter (фильтрация)
* Django-environ (переменные окружения)
* SQLite

## Реализованный функционал
* **Пользователи (`users`):** Авторизация по `email`. Кастомные поля профиля. Generic-эндпоинт обновления данных.
* **Платежи (`users`):** Модель `Payment` (курс/урок, сумма, способ оплаты). Фильтрация, сортировка по дате. Вложенная история платежей в профиле. Кастомная команда генерации данных.
* **Обучение (`lms`):** CRUD для курсов (ViewSets) и уроков (Generics). Связь `ForeignKey`. Вложенный вывод уроков и динамический подсчет их количества (`lessons_count`) в сериализаторе курса.

---

## Локальное развертывание

```bash
# 1. Клонирование и переход в проект
git clone https://github.com && cd django_rest_framework

# 2. Настройка окружения
python -m venv venv
venv\Scripts\activate     # Для Windows (source venv/bin/activate для Linux/macOS)
pip install django djangorestframework pillow django-environ django-filter

# 3. Переменные окружения (создать .env в корне)
echo "DEBUG=True\nSECRET_KEY=django_secret_key" > .env

# 4. Миграции и наполнение БД тестовыми платежами
python manage.py makemigrations && python manage.py migrate
python manage.py fill_payments

# 5. Запуск
python manage.py runserver
```

---

## Эндпоинты (Postman)

### Курсы & Уроки (`/lms/`)
* `GET /lms/courses/` — Список курсов с вложенными уроками и их количеством
* `POST /lms/courses/` — Создание курса
* `GET|PUT|PATCH|DELETE /lms/courses/<id>/` — CRUD-операции с курсом
* `GET /lms/lessons/` — Список уроков
* `POST /lms/lessons/create/` — Создание урока
* `GET /lms/lessons/<id>/` — Детали урока
* `PUT|PATCH /lms/lessons/update/<id>/` — Редактирование урока
* `DELETE /lms/lessons/delete/<id>/` — Удаление урока

### Профиль & Платежи (`/users/`)
* `PATCH /users/update/<id>/` — Редактирование данных пользователя
* `GET /users/profile/<id>/` — Профиль пользователя со вложенным массивом истории `payments_history`
* `GET /users/payments/` — Полный список платежей

### Фильтрация платежей
* `?payment_method=cash` / `?payment_method=transfer` — Фильтр по способу оплаты
* `?paid_course=<id>` / `?paid_lesson=<id>` — Фильтр по купленной сущности
* `?ordering=-payment_date` — Сортировка от новых платежей к старым
