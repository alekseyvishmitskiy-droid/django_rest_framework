from django.urls import path
from users.apps import UsersConfig
from users.views import UserUpdateAPIView

app_name = UsersConfig.name

urlpatterns = [
    path('update/<int:pk>/', UserUpdateAPIView.as_view(), name='user-update'),
]
