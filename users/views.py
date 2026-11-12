from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Payment, User
from users.serializers import (
    PaymentSerializer,
    UserProfileSerializer,
    UserSerializer,
    UserRegisterSerializer,
    UserPublicProfileSerializer
)
from users.permissions import IsOwnerOrReadOnly
from users.services import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_session,
    retrieve_stripe_session,
)


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class UserProfileRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        requested_user = self.get_object()
        if self.request.user == requested_user:
            return UserProfileSerializer
        return UserPublicProfileSerializer


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('paid_course', 'paid_lesson', 'payment_method')
    ordering_fields = ('payment_date',)


class PaymentCreateAPIView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        if payment.paid_course:
            product_name = getattr(payment.paid_course, 'title', None) or getattr(payment.paid_course, 'name', 'Оплата курса')
        elif payment.paid_lesson:
            product_name = getattr(payment.paid_lesson, 'title', None) or getattr(payment.paid_lesson, 'name', 'Оплата урока')
        else:
            product_name = "Оплата обучения"

        product_id = create_stripe_product(product_name)
        price_id = create_stripe_price(payment.amount, product_id)
        session_id, payment_link = create_stripe_session(price_id)

        payment.session_id = session_id
        payment.link = payment_link
        payment.save()


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Проверка статуса платежа в Stripe",
        operation_description="Запрашивает актуальный статус сессии в Stripe API и обновляет поле payment_status в базе данных.",
        responses={
            200: openapi.Response(
                description="Актуальный статус платежа",
                examples={
                    "application/json": {
                        "payment_id": 1,
                        "session_id": "cs_test_...",
                        "payment_status": "paid",
                        "status": "complete",
                        "amount_total": 500000
                    }
                }
            ),
            400: "Для платежа не создана сессия Stripe или ошибка запроса к Stripe API",
            401: "Пользователь не авторизован",
            404: "Платеж не найден"
        }
    )
    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, user=request.user)

        if not payment.session_id:
            return Response(
                {"detail": "Для этого платежа не создана сессия Stripe."},
                status=status.HTTP_400_BAD_REQUEST
            )

        session_data = retrieve_stripe_session(payment.session_id)
        stripe_status = session_data.get("payment_status", "unpaid")


        payment.payment_status = stripe_status
        payment.save()

        return Response({
            "payment_id": payment.id,
            "session_id": payment.session_id,
            "payment_status": payment.payment_status,
            "status": session_data.get("status"),
            "amount_total": session_data.get("amount_total"),
        })
