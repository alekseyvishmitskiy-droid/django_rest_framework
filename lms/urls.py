from django.urls import path
from rest_framework.routers import DefaultRouter
from lms.apps import LmsConfig
from lms.views import (CourseViewSet, LessonCreateAPIView, LessonListAPIView,
                       LessonRetrieveAPIView, LessonUpdateAPIView, LessonDestroyAPIView, SubscriptionAPIView)

app_name = LmsConfig.name

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')

urlpatterns = [
    path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
    path('lessons/', LessonListAPIView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-get'),
    path('lessons/update/<int:pk>/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('lessons/delete/<int:pk>/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
    path('subscription/', SubscriptionAPIView.as_view(), name='subscription'),
] + router.urls
