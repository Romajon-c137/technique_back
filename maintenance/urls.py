from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaintenancePlanViewSet, MaintenanceInstanceViewSet, MaintenancePhotoViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'plans', MaintenancePlanViewSet, basename='maintenanceplan')
router.register(r'instances', MaintenanceInstanceViewSet, basename='maintenanceinstance')
router.register(r'photos', MaintenancePhotoViewSet, basename='maintenancephoto')

urlpatterns = [
    path('', include(router.urls)),
]
