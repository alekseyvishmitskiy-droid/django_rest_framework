from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # Добавили импорт JWT

from users.apps import UsersConfig
from users.views import (
    UserUpdateAPIView,
    PaymentListAPIView,
    UserProfileRetrieveAPIView,
    UserRegisterView
)

app_name = UsersConfig.name

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('update/<int:pk>/', UserUpdateAPIView.as_view(), name='user-update'),
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('profile/<int:pk>/', UserProfileRetrieveAPIView.as_view(), name='user-profile'),
]
