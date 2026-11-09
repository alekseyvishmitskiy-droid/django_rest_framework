from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Payment
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Заполнение базы данных тестовыми платежами'

    def handle(self, *args, **options):
        User = get_user_model()


        user, _ = User.objects.get_or_create(email='test@example.com', defaults={'is_active': True})
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not course or not lesson:
            self.stdout.write(self.style.ERROR('Сначала создайте хотя бы один курс и один урок в БД!'))
            return


        payments_data = [
            {
                "user": user,
                "paid_course": course,
                "amount": 5000.00,
                "payment_method": Payment.TRANSFER
            },
            {
                "user": user,
                "paid_lesson": lesson,
                "amount": 1500.00,
                "payment_method": Payment.CASH
            }
        ]

        for data in payments_data:
            Payment.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Тестовые платежи успешно добавлены!'))
