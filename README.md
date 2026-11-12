# django_rest_framework

REST API для системы управления обучением (LMS) на Django и Django REST Framework с документацией OpenAPI и интеграцией платежного шлюза Stripe.

## Стек технологий
* Python 3.x, Django 6.x, DRF
* djangorestframework-simplejwt (JWT-авторизация)
* drf-yasg (автогенерация документации Swagger и ReDoc)
* Stripe API / requests (онлайн-оплата курсов и уроков)
* coverage (анализ покрытия тестами)
* Django-filter (фильтрация)
* Django-environ (переменные окружения)
* django-cors-headers (настройка CORS)
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

### 4. Платежи и интеграция со Stripe (`users`)
* **Онлайн-оплата через Stripe:** Реализованы сервисные функции (`users/services.py`) для создания продукта, цены (в копейках/центах) и платежной сессии Stripe Checkout. При создании платежа ссылка на оплату (`link`) и ID сессии (`session_id`) сохраняются в БД и возвращаются пользователю.
* **Проверка статуса платежа:** Реализован эндпоинт для получения актуального статуса оплаты сессии из Stripe API по ID платежа.
* **Фильтрация и наполнение:** Фильтрация списка платежей по курсу, уроку и способу оплаты, сортировка по дате, а также кастомная команда `python manage.py fill_payments`.

### 5. Документация API (`drf-yasg`)
* Подключена интерактивная документация **Swagger UI** и **ReDoc** с поддержкой авторизации по `Bearer`-токену.

---

## Локальное развертывание

```bash
# 1. Клонирование и переход в проект
git clone https://github.com && cd django_rest_framework

# 2. Настройка виртуального окружения
python -m venv venv
venv\Scripts\activate     # Для Windows (source venv/bin/activate для Linux/macOS)
pip install django djangorestframework djangorestframework-simplejwt pillow django-environ django-filter coverage drf-yasg django-cors-headers requests

# 3. Создание файла переменных окружения (.env в корне проекта)
# Укажите ваши значения SECRET_KEY и тестовый секретный ключ Stripe (sk_test_...)
echo -e "DEBUG=True\nSECRET_KEY=django_secret_key\nSTRIPE_API_KEY=sk_test_your_stripe_key" > .env

# 4. Миграции, загрузка фикстур групп и наполнение БД платежами
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata users/fixtures/groups.json
python manage.py fill_payments

# 5. Запуск локального сервера
python manage.py runserver
```

---

## Документация API

После запуска сервера документация доступна по следующим адресам:
* **Swagger UI:** `http://127.0.0` (для авторизации нажмите **Authorize** и введите `Bearer <access_token>`)
* **ReDoc:** `http://127.0.0`

---

## Запуск автотестов и анализ покрытия (Coverage)

В проекте написаны интеграционные тесты (`APITestCase`), проверяющие CRUD уроков, работу валидатора сторонних ссылок, логику подписок, а также создание платежей и проверку статуса сессии Stripe с использованием моков (`unittest.mock.patch`).

```bash
# Выполнение всех тестов
python manage.py test

# Запуск сбора статистики покрытия кода тестами
coverage run --source='.' manage.py test

# Вывод отчета по покрытию в терминал
coverage report

# Генерация визуального HTML-отчета (создаст папку htmlcov/)
coverage html
```

---

## Эндпоинты API

### Авторизация, Профили и Платежи (`/users/`)
* `POST /users/register/` — Регистрация (Доступна без токена)
* `POST /users/token/` — Получение JWT-токена (Вход по `email` и `password`)
* `POST /users/token/refresh/` — Обновление JWT-токена
* `GET /users/profile/<id>/` — Детали профиля (`payments_history` виден только владельцу)
* `PATCH /users/update/<id>/` — Редактирование профиля (Только для владельца)
* `GET /users/payments/` — Список платежей (`?payment_method=cash`, `?ordering=-payment_date`)
* `POST /users/payments/create/` — Создание платежа и генерация ссылки на оплату через Stripe
* `GET /users/payments/<id>/status/` — Проверка актуального статуса оплаты сессии в Stripe

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

## Настройка Celery и периодических задач

1. Добавьте настройки Redis в файл `.env`:
   ```env
   CELERY_BROKER_URL=redis://127.0.0.1:6379/0
   CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
   ```
2. Запустите воркер Celery (для Windows используйте флаг `--pool=solo`):
   ```bash
   celery -A config worker -l INFO --pool=solo
   ```
3. В отдельном окне терминала запустите планировщик периодических задач Celery Beat:
   ```bash
   celery -A config beat -l INFO -S django
   ```
## Настройка Celery и периодических задач

1. Добавьте настройки Redis в файл `.env`:
   ```env
   CELERY_BROKER_URL=redis://127.0.0.1:6379/0
   CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
   ```
2. Запустите воркер Celery (для Windows используйте флаг `--pool=solo`):
   ```bash
   celery -A config worker -l INFO --pool=solo
   ```
3. В отдельном окне терминала запустите планировщик периодических задач Celery Beat:
   ```bash
   celery -A config beat -l INFO -S django
   ```
