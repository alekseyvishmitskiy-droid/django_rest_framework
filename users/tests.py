from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course
from users.models import Payment, User
from datetime import timedelta
from django.utils import timezone
from users.tasks import deactivate_inactive_users

class PaymentTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(email='test_user@example.com')
        self.user.set_password('12345')
        self.user.save()

        self.course = Course.objects.create(
            title='Python разработчик',
            description='Базовый курс'
        )


        self.client.force_authenticate(user=self.user)

    @patch('users.views.create_stripe_session')
    @patch('users.views.create_stripe_price')
    @patch('users.views.create_stripe_product')
    def test_create_payment(self, mock_product, mock_price, mock_session):
        mock_product.return_value = 'prod_test_123'
        mock_price.return_value = 'price_test_123'
        mock_session.return_value = ('cs_test_123', 'https://stripe.com')

        data = {
            'paid_course': self.course.id,
            'amount': '5000.00',
            'payment_method': 'transfer'
        }

        response = self.client.post(
            '/users/payments/create/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )


        response_data = response.json()
        self.assertEqual(response_data['amount'], '5000.00')
        self.assertEqual(response_data['session_id'], 'cs_test_123')
        self.assertEqual(response_data['link'], 'https://stripe.com')
        self.assertEqual(response_data['user'], self.user.id)


        self.assertTrue(
            Payment.objects.all().exists()
        )

    def test_list_payment(self):
        Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount='3000.00',
            payment_method='cash'
        )

        response = self.client.get(
            '/users/payments/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.json()),
            1
        )

    @patch('users.views.retrieve_stripe_session')
    def test_payment_status(self, mock_retrieve):
        payment = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount='5000.00',
            session_id='cs_test_status_123'
        )

        mock_retrieve.return_value = {
            'id': 'cs_test_status_123',
            'payment_status': 'paid',
            'status': 'complete',
            'amount_total': 500000
        }

        response = self.client.get(
            f'/users/payments/{payment.id}/status/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json(),
            {
                'payment_id': payment.id,
                'session_id': 'cs_test_status_123',
                'payment_status': 'paid',
                'status': 'complete',
                'amount_total': 500000
            }
        )

        def test_deactivate_inactive_users(self):
            old_user = User.objects.create(
                email='inactive@example.com',
                is_active=True,
                last_login=timezone.now() - timedelta(days=31)
            )
            active_user = User.objects.create(
                email='active@example.com',
                is_active=True,
                last_login=timezone.now() - timedelta(days=5)
            )

            deactivate_inactive_users()

            old_user.refresh_from_db()
            active_user.refresh_from_db()

            self.assertFalse(old_user.is_active)
            self.assertTrue(active_user.is_active)
