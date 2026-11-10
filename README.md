# django_rest_framework

REST API для системы управления обучением (LMS) на Django и Django REST Framework.

## Стек технологий
* Python 3.x, Django 5.x, DRF
* djangorestframework-simplejwt (JWT-авторизация)
* coverage (анализ покрытия тестами)
* Django-filter (фильтрация)
* Django-environ (переменные окружения)
* SQLite

## Реализованный функционал

### 1. Пользователи, JWT-авторизация и Профили
* **Авторизация:** Вход по `email` и паролю с выдачей пары JWT-токенов (`access`, `refresh`).
* **Регистрация:** Открытый эндпоинт создания пользователя с автоматическим безопасным хешированием паролей.
* **Доступ к профилям:** Авторизованный пользователь может просмотреть любой профиль, но редактировать — только свой. При просмотре чужого профиля скрываются приватные финансовые логи (`payments_history`).

### 2. Права доступа (Permissions)
* **Глобальная защита:** Все эндпоинты по умолчанию требуют JWT-авторизацию.
* **Модераторы (группа `Moderators`):** Имеют право просматривать и редактировать любые курсы и уроки, но ограничены в правах на их создание и удаление.
* **Владельцы (Обычные пользователи):** Видят и управляют только своими объектами. При создании записи автор автоматически привязывается к полю `owner` через хук `perform_create()`.

### 3. Обучение, Валидация и Пагинация (`lms`)
* **Связи моделей:** Реализован CRUD для курсов и уроков через ForeignKey со связанным именем `related_name='lessons'`.
* **Валидация контента:** Реализован кастомный класс-валидатор `YoutubeOnlyValidator`. Прикреплять к урокам можно исключительно ссылки на домены `youtube.com` или `youtu.be`.
* **Подписки на обновления:** Добавлена модель `Subscription`. Реализован эндпоинт, который работает циклично: при первом запросе активирует подписку на курс, при повторном — удаляет. При просмотре курсов возвращается динамический флаг `is_subscribed` для текущего пользователя.
* **Пагинация:** Внедрен постраничный вывод списков курсов и уроков (класс `LMSPagination`). Лимит — 5 элементов на страницу с возможностью кастомизации через query-параметр `?page_size=`.

### 4. Платежи (`users`)
* Фильтрация списка платежей по курсу, уроку и способу оплаты. Сортировка по дате.
* Кастомная консольная команда `python manage.py fill_payments` для быстрого наполнения БД.

---

## Локальное развертывание

```bash
# 1. Клонирование и переход в проект
git clone https://github.com && cd django_rest_framework

# 2. Настройка виртуального окружения
python -m venv venv
venv\Scripts\activate     # Для Windows (source venv/bin/activate для Linux/macOS)
pip install django djangorestframework djangorestframework-simplejwt pillow django-environ django-filter coverage

# 3. Создание файла переменных окружения (.env в корне проекта)
echo "DEBUG=True\nSECRET_KEY=django_secret_key" > .env

# 4. Миграции, загрузка фикстур групп и наполнение БД платежами
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata users/fixtures/groups.json
python manage.py fill_payments

# 5. Запуск локального сервера
python manage.py runserver
```

---

## Запуск автотестов и анализ покрытия (Coverage)

В проекте написаны интеграционные тесты (`APITestCase`), проверяющие CRUD уроков, работу валидатора сторонних ссылок, а также логику активации и деактивации подписок.

```bash
# Выполнение тестов
python manage.py test

# Запуск сбора статистики покрытия кода тестами
coverage run --source='.' manage.py test

# Вывод отчета по покрытию в терминал
coverage report

# Генерация визуального HTML-отчета (создаст папку htmlcov/)
coverage html
```

---

## Эндпоинты API (Postman)

### Авторизация и Профили (`/users/`)
* `POST /users/register/` — Регистрация (Доступна без токена)
* `POST /users/token/` — Получение JWT-токена (Вход по `email` и `password`)
* `POST /users/token/refresh/` — Обновление JWT-токена
* `GET /users/profile/<id>/` — Детали профиля (`payments_history` виден только владельцу)
* `PATCH /users/update/<id>/` — Редактирование профиля (Только для владельца)
* `GET /users/payments/` — Список платежей (`?payment_method=cash`, `?ordering=-payment_date`)

### Курсы, Уроки и Подписки (`/lms/`)
*Запросы ниже требуют передачи заголовка `Authorization: Bearer <access_token>`*

* `GET /lms/courses/` — Список курсов с постраничной пагинацией (включает поля `lessons_count` и `is_subscribed`)
* `POST /lms/courses/` — Создание курса (Запрещено модераторам)
* `GET|PUT|PATCH /lms/courses/<id>/` — Детали / Редактирование курса (Доступно модераторам или владельцам)
* `DELETE /lms/courses/<id>/` — Удаление курса (Доступно только владельцу)
* `GET /lms/lessons/` — Список уроков с постраничной пагинацией
* `POST /lms/lessons/create/` — Создание урока с валидацией YouTube-ссылки (Запрещено модераторам)
* `GET|PUT|PATCH /lms/lessons/<id>/` — Детали / Редактирование урока (Доступно модераторам или владельцам)
* `DELETE /lms/lessons/delete/<id>/` — Удаление урока (Доступно только владельцу)
* `POST /lms/subscription/` — Управление подпиской. Принимает в Body `{"course_id": <id>}`. Переключает состояние подписки текущего пользователя на курс.
