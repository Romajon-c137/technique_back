from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Notification
from .serializers import NotificationSerializer, NotificationDetailSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NotificationDetailSerializer
        return NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(
            Q(recipient__isnull=True) | Q(recipient=user)
        ).prefetch_related('read_by', 'elements').order_by('-created_at')

    @action(detail=False, methods=['get'], url_path='unread_count')
    def unread_count(self, request):
        queryset = self.get_queryset()
        count = sum(
            1 for n in queryset
            if not n.read_by.filter(pk=request.user.pk).exists()
        )
        return Response({'unread_count': count})

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read_by.add(request.user)
        serializer = NotificationDetailSerializer(notification, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='mark_all_read')
    def mark_all_read(self, request):
        notifications = self.get_queryset()
        for n in notifications:
            n.read_by.add(request.user)
        return Response({'status': 'ok', 'marked': notifications.count()})
