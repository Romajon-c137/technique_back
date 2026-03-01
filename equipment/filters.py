from django_filters import rest_framework as filters
from .models import Equipment


class EquipmentFilter(filters.FilterSet):
    """Фильтры для техники"""
    
    # Поиск по модели (частичное совпадение, без учета регистра)
    model = filters.CharFilter(lookup_expr='icontains')
    
    # Фильтрация по точному ID бренда
    brand = filters.NumberFilter(field_name='brand__id')
    
    # Фильтрация по точному ID тега
    tag = filters.NumberFilter(field_name='tag__id')
    
    # Фильтрация по точному ID ответственного
    responsible = filters.UUIDFilter(field_name='responsible__id')
    
    # Бонус: поиск по имени бренда (частичное совпадение)
    brand_name = filters.CharFilter(field_name='brand__name', lookup_expr='icontains')
    
    # Бонус: поиск по имени тега (частичное совпадение)
    tag_name = filters.CharFilter(field_name='tag__name', lookup_expr='icontains')
    
    # Бонус: поиск по имени ответственного (частичное совпадение)
    responsible_name = filters.CharFilter(field_name='responsible__full_name', lookup_expr='icontains')
    
    class Meta:
        model = Equipment
        fields = ['model', 'brand', 'tag', 'responsible', 'brand_name', 'tag_name', 'responsible_name']
