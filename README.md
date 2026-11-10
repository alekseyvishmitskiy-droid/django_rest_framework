# django_rest_framework

REST API для системы управления обучением (LMS) на Django и Django REST Framework.

## Стек технологий
* Python 3.x, Django 5.x, DRF
* djangorestframework-simplejwt (JWT-авторизация)
* Django-filter (фильтрация)
* Django-environ (переменные окружения)
* SQLite

## Реализованный функционал
* **Пользователи & JWT:** Авторизация по `email` с использованием JWT-токенов (`access`, `refresh`). Реализован открытый эндпоинт регистрации.
* **Права доступа (Permissions):** 
  * Каждый эндпоинт (кроме авторизации и регистрации) закрыт авторизацией.
  * **Модераторы:** Объединены в группу `Moderators`. Могут просматривать и редактировать любые курсы и уроки, но не имеют прав на их создание и удаление.
  * **Обычные пользователи (Владельцы):** Имеют полный CRUD-доступ только к собственным курсам и урокам. При создании объекта через `perform_create()` автор автоматически назначается владельцем (`owner`).
  * **Профили пользователей (Доп. задание *):** Авторизованный пользователь может просматривать любой профиль, но редактировать — только свой. При просмотре чужого профиля приватная информация (история платежей) скрывается автоматически.
* **Платежи (`users`):** Модель `Payment` (курс/урок, сумма, способ оплаты). Фильтрация, сортировка по дате. Вложенная история платежей в профиле. Кастомная команда генерации данных.
* **Обучение (`lms`):** CRUD для курсов (ViewSets) и уроков (Generics). Связи настроены через `related_name='lessons'`. Вложенный вывод уроков и динамический подсчет их количества (`lessons_count`) в сериализаторе курса с оптимизацией запросов `prefetch_related`.

---

## Локальное развертывание

```bash
# 1. Клонирование и переход в проект
git clone https://github.com && cd django_rest_framework

# 2. Настройка окружения
python -m venv venv
venv\Scripts\activate     # Для Windows (source venv/bin/activate для Linux/macOS)
pip install django djangorestframework djangorestframework-simplejwt pillow django-environ django-filter

# 3. Переменные окружения (создать .env в корне)
echo "DEBUG=True\nSECRET_KEY=django_secret_key" > .env

# 4. Миграции, применение фикстур групп и наполнение БД тестовыми платежами
python manage.py makemigrations && python manage.py migrate
python manage.py loaddata users/fixtures/groups.json
python manage.py fill_payments

# 5. Запуск
python manage.py runserver
```

---

## Эндпоинты (Postman)

### Авторизация и Пользователи (`/users/`)
* `POST /users/register/` — Регистрация нового пользователя (Открытый эндпоинт)
* `POST /users/token/` — Получение JWT-токена (Открытый эндпоинт. Принимает `email` и `password`)
* `POST /users/token/refresh/` — Обновление JWT-токена
* `GET /users/profile/<id>/` — Профиль пользователя (Владельцу доступна вся информация и `payments_history`, остальным — публичная урезанная инфа)
* `PATCH /users/update/<id>/` — Редактирование данных пользователя (Только для владельца профиля)
* `GET /users/payments/` — Полный список платежей

### Фильтрация платежей
* `?payment_method=cash` / `?payment_method=transfer` — Фильтр по способу оплаты
* `?paid_course=<id>` / `?paid_lesson=<id>` — Фильтр по купленной сущности
* `?ordering=-payment_date` — Сортировка от новых платежей к старым

### Курсы & Уроки (`/lms/`)
*Все эндпоинты ниже требуют передачи заголовка `Authorization: Bearer <access_token>`*

* `GET /lms/courses/` — Список курсов (Модератор видит все, владелец — только свои)
* `POST /lms/courses/` — Создание курса (Модераторам запрещено)
* `GET|PUT|PATCH /lms/courses/<id>/` — Просмотр деталей и редактирование курса (Доступно модераторам или владельцам)
* `DELETE /lms/courses/<id>/` — Удаление курса (Только для владельца, модераторам запрещено)
* `GET /lms/lessons/` — Список уроков (Модератор видит все, владелец — только свои)
* `POST /lms/lessons/create/` — Создание урока (Модераторам запрещено)
* `GET /lms/lessons/<id>/` — Детали урока (Доступно модераторам или владельцам)
* `PUT|PATCH /lms/lessons/update/<id>/` — Редактирование урока (Доступно модераторам или владельцам)
* `DELETE /lms/lessons/delete/<id>/` — Удаление урока (Только для владельца, модераторам запрещено)
