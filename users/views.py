from rest_framework import generics
from users.models import User
from users.serializers import UserSerializer

class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
