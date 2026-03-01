from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginAPIView,
    ChangePasswordAPIView,
    CurrentUserAPIView,
    UpdateProfileAPIView,
    UserViewSet
)

# Создаем router для ViewSet
router = DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('login', LoginAPIView.as_view(), name='login'),
    path('change-password', ChangePasswordAPIView.as_view(), name='change-password'),
    path('me', CurrentUserAPIView.as_view(), name='current-user'),
    path('profile', UpdateProfileAPIView.as_view(), name='update-profile'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]
