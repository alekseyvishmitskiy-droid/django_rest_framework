# django_rest_framework

REST API для системы управления обучением (LMS) на базе Django и Django REST Framework. Проект включает документацию OpenAPI, фоновые задачи Celery, интеграцию со Stripe, контейнеризацию в Docker и CI/CD через GitHub Actions.

## Стек технологий
* **Бэкенд:** Python 3.12, Django 6.x, Django REST Framework, djangorestframework-simplejwt, drf-yasg, Django-filter, django-cors-headers
* **База данных и брокер:** PostgreSQL, Redis & Celery / Celery Beat
* **Продакшен и CI/CD:** Docker & Docker Compose, Gunicorn & Nginx, GitHub Actions (Flake8, автотесты, сборка и деплой)
* **Платежи и утилиты:** Stripe API, coverage, python-dotenv

## Реализованный функционал
* **Пользователи и профили:** JWT-авторизация по email/паролю, безопасная регистрация, разграничение доступа к финансовой истории (`payments_history`).
* **Права доступа:** Глобальная защита JWT, разделение ролей для группы `Moderators` и обычных владельцев (`owner` через хук `perform_create()`).
* **Модуль LMS:** CRUD для курсов и уроков, валидатор ссылок `YoutubeOnlyValidator` (только YouTube), динамические подписки на курсы с флагом `is_subscribed` и постраничная пагинация (`LMSPagination` по 5 элементов).
* **Платежи (Stripe):** Создание продуктов и сессий оплаты в Stripe, проверка статуса платежа, фильтрация и кастомная команда заполнения базы `fill_payments`.
* **Фоновые задачи:** Асинхронные рассылки уведомлений об обновлениях курсов и периодическая блокировка неактивных пользователей (более 30 дней) через Celery Beat.
* **Документация:** Интерактивные интерфейсы Swagger UI и ReDoc.

---

## CI/CD и деплой на сервер
Проект настроен для непрерывной интеграции и доставки с помощью GitHub Actions (`.github/workflows/ci_cd.yml`) и развернут на сервере Ubuntu с использованием Docker Compose, Gunicorn и Nginx.

### Этапы пайплайна:
1. **Тестирование и линтинг (`test-and-lint`):** Запуск в тестовом окружении PostgreSQL и Redis, проверка тестами Django и линтером `flake8`.
2. **Сборка и публикация (`build-and-push`):** Сборка и отправка Docker-образа в Docker Hub при пуше в ветку `main`.
3. **Автодеплой (`deploy`):** Подключение по SSH к серверу, обновление репозитория и перезапуск контейнеров.

*Требуемые GitHub Secrets:* `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `SERVER_HOST`, `SERVER_USER`, `SSH_PRIVATE_KEY`.

---

## Запуск проекта через Docker

1. **Клонируйте репозиторий и перейдите в папку проекта:**
   ```bash
   git clone https://github.com
   cd django_rest_framework
   ```
2. **Создайте и настройте файл окружения:**
   ```bash
   cp .env.template .env
   # Заполните SECRET_KEY, POSTGRES_PASSWORD, STRIPE_API_KEY и DOCKER_USERNAME в файле .env
   ```
3. **Соберите и запустите контейнеры:**
   ```bash
   docker compose up -d --build
   ```
4. **Управление и инициализация данных:**
   ```bash
   docker compose ps
   docker compose exec backend python manage.py createsuperuser
   docker compose exec backend python manage.py loaddata users/fixtures/groups.json
   docker compose exec backend python manage.py fill_payments
   docker compose logs -f backend
   docker compose down
   ```

---

## Локальное развертывание (без Docker)

```bash
git clone https://github.com && cd django_rest_framework
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate для Windows
pip install -r requirements.txt
cp .env.template .env  # Укажите POSTGRES_HOST=localhost и CELERY_BROKER_URL=redis://127.0.0.1:6379/0

python manage.py migrate
python manage.py loaddata users/fixtures/groups.json
python manage.py fill_payments

# Запуск сервисов в разных терминалах:
python manage.py runserver
celery -A config worker -l INFO --pool=solo
celery -A config beat -l INFO -S django
```

---

## Документация API и тесты

* **Swagger UI:** `http://127.0.0` *(Authorization: Bearer <access_token>)*
* **ReDoc:** `http://127.0.0`
*(На удаленном сервере замените `127.0.0.1:8000` на IP-адрес сервера)*

**Запуск тестов и покрытие:**
```bash
docker compose exec backend python manage.py test
coverage run --source='.' manage.py test && coverage report && coverage html
```

---

## Основные эндпоинты API

### Авторизация, Профили и Платежи (`/users/`)
* `POST /users/register/` — Регистрация
* `POST /users/token/` & `POST /users/token/refresh/` — Получение и обновление JWT-токенов
* `GET /users/profile/<id>/` & `PATCH /users/update/<id>/` — Просмотр и редактирование профиля
* `GET /users/payments/` & `POST /users/payments/create/` — Список платежей и создание оплаты через Stripe
* `GET /users/payments/<id>/status/` — Проверка статуса платежа в Stripe

### Курсы, Уроки и Подписки (`/lms/`) *(требуется Bearer-токен)*
* `GET|POST /lms/courses/` — Список (с пагинацией и флагами подписок) и создание курсов
* `GET|PUT|PATCH|DELETE /lms/courses/<id>/` — Управление отдельным курсом
* `GET|POST /lms/lessons/` & `GET|PUT|PATCH|DELETE /lms/lessons/<id>/` — Управление уроками (с валидацией YouTube-ссылок)
* `POST /lms/subscription/` — Управление подпиской на курс (`{"course_id": <id>}`)
