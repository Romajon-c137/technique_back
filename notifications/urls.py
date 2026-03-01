from django.urls import path
from .views import NotificationViewSet

# Explicit URL patterns without trailing slash (APPEND_SLASH=False in settings)
# All paths start with '/' so they combine correctly with 'api/v1/notifications' prefix

notification_list    = NotificationViewSet.as_view({'get': 'list'})
notification_detail  = NotificationViewSet.as_view({'get': 'retrieve'})
mark_read_view       = NotificationViewSet.as_view({'post': 'mark_read'})
unread_count_view    = NotificationViewSet.as_view({'get': 'unread_count'})
mark_all_read_view   = NotificationViewSet.as_view({'post': 'mark_all_read'})

urlpatterns = [
    # GET  /api/v1/notifications
    path('',                    notification_list,    name='notification-list'),
    # GET  /api/v1/notifications/unread_count
    path('/unread_count',       unread_count_view,    name='notification-unread-count'),
    # POST /api/v1/notifications/mark_all_read
    path('/mark_all_read',      mark_all_read_view,   name='notification-mark-all-read'),
    # GET  /api/v1/notifications/{pk}
    path('/<str:pk>',           notification_detail,  name='notification-detail'),
    # POST /api/v1/notifications/{pk}/read
    path('/<str:pk>/read',      mark_read_view,       name='notification-mark-read'),
]
