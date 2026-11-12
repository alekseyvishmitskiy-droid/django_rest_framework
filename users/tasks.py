from datetime import timedelta
from celery import shared_task
from django.utils import timezone

from users.models import User


@shared_task
def deactivate_inactive_users():
    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=one_month_ago
    )
    count = inactive_users.update(is_active=False)
    return f'Заблокировано неактивных пользователей: {count}'
