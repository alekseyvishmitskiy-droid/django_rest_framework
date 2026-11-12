from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from lms.models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return

    subscriptions = Subscription.objects.filter(course=course).select_related('user')
    recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

    if recipient_list:
        send_mail(
            subject=f'Обновление курса «{course.title}»',
            message=f'Материалы курса «{course.title}» были обновлены. Зайдите на платформу, чтобы ознакомиться с изменениями.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
