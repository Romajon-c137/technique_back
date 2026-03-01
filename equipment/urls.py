from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrandViewSet, TechTagViewSet, EquipmentViewSet, HintViewSet

router = DefaultRouter(trailing_slash=False)
router.register('brands', BrandViewSet, basename='brand')
router.register('tags', TechTagViewSet, basename='tag')
router.register('items', EquipmentViewSet, basename='equipment')
router.register('hints', HintViewSet, basename='hint')

urlpatterns = [
    path('', include(router.urls)),
]
