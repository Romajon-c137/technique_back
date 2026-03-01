from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Banner
from .serializers import BannerSerializer


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    """Баннеры для главной страницы (только активные)"""
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Banner.objects.filter(is_active=True).order_by('order', '-created_at')
