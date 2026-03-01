from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .models import Brand, TechTag, Equipment
from .serializers import BrandSerializer, TechTagSerializer, EquipmentSerializer
from .filters import EquipmentFilter


@extend_schema_view(
    list=extend_schema(
        summary='Список брендов',
        description='Получить список всех брендов техники',
        tags=['Technique']
    ),
    retrieve=extend_schema(
        summary='Детали бренда',
        description='Получить информацию о конкретном бренде',
        tags=['Technique']
    )
)
class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра брендов (только чтение)"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(
        summary='Список тегов',
        description='Получить список всех тегов техники',
        tags=['Technique']
    ),
    retrieve=extend_schema(
        summary='Детали тега',
        description='Получить информацию о конкретном теге',
        tags=['Technique']
    )
)
class TechTagViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра тегов (только чтение)"""
    queryset = TechTag.objects.all()
    serializer_class = TechTagSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(
        summary='Список техники',
        description='Получить список всей техники с полной информацией о бренде, теге, ответственном и изображениях. Поддерживает фильтрацию по модели, бренду, тегу и ответственному.',
        tags=['Technique'],
        parameters=[
            OpenApiParameter(name='model', description='Поиск по модели (частичное совпадение)', type=str),
            OpenApiParameter(name='brand', description='Фильтр по ID бренда', type=int),
            OpenApiParameter(name='tag', description='Фильтр по ID тега', type=int),
            OpenApiParameter(name='responsible', description='Фильтр по ID ответственного', type=str),
            OpenApiParameter(name='brand_name', description='Поиск по названию бренда', type=str),
            OpenApiParameter(name='tag_name', description='Поиск по названию тега', type=str),
            OpenApiParameter(name='responsible_name', description='Поиск по имени ответственного', type=str),
        ]
    ),
    retrieve=extend_schema(
        summary='Детали техники',
        description='Получить подробную информацию о конкретной единице техники',
        tags=['Technique']
    )
)
class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра техники (только чтение) с поддержкой фильтрации"""
    queryset = Equipment.objects.select_related('brand', 'tag', 'responsible').prefetch_related('images', 'hints__elements')
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EquipmentFilter


from .models import Hint
from .serializers import HintSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Список подсказок',
        description='Получить список всех подсказок для техники. Можно фильтровать по technique_id.',
        tags=['Technique']
    ),
    retrieve=extend_schema(
        summary='Детали подсказки',
        description='Получить подробную информацию о конкретной подсказке с элементами',
        tags=['Technique']
    )
)
class HintViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра подсказок (только чтение)"""
    queryset = Hint.objects.prefetch_related('elements')
    serializer_class = HintSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтрация подсказок по технике"""
        queryset = super().get_queryset()
        technique_id = self.request.query_params.get('technique')
        if technique_id:
            queryset = queryset.filter(technique_id=technique_id)
        return queryset
