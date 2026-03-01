from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from datetime import date
from django_filters.rest_framework import DjangoFilterBackend

from .models import MaintenancePlan, MaintenanceInstance, MaintenancePhoto
from .serializers import (
    MaintenancePlanListSerializer,
    MaintenancePlanDetailSerializer,
    MaintenanceInstanceListSerializer,
    MaintenanceInstanceDetailSerializer,
    MaintenanceInstanceUpdateSerializer,
    MaintenancePhotoSerializer
)
from .permissions import IsMaintenanceResponsibleOrAssigned, CanPerformMaintenance


class MaintenancePlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для планов ТО (только чтение)
    
    list: Список всех планов ТО
    retrieve: Детали конкретного плана ТО
    """
    queryset = MaintenancePlan.objects.select_related(
        'equipment__brand', 'equipment__responsible', 'created_by'
    ).prefetch_related('tasks').all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['equipment', 'type', 'is_active']
    search_fields = ['title', 'equipment__model']
    ordering_fields = ['created_at', 'start_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MaintenancePlanDetailSerializer
        return MaintenancePlanListSerializer


class MaintenanceInstanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для инстансов ТО
    
    list: Список всех инстансов ТО
    retrieve: Детали конкретного инстанса ТО
    partial_update: Обновить task_states
    start: Начать выполнение ТО
    complete: Завершить ТО
    cancel: Отменить ТО
    my_todos: Получить мои ТО для выполнения
    """
    queryset = MaintenanceInstance.objects.select_related(
        'plan', 'equipment__brand', 'equipment__responsible',
        'assigned_to', 'completed_by'
    ).prefetch_related('photos').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'status', 'scheduled_date', 'assigned_to', 'completed_by', 'equipment__responsible']
    search_fields = ['equipment__model', 'plan__title']
    ordering_fields = ['scheduled_date', 'created_at', 'completed_at']
    ordering = ['scheduled_date']
    
    def get_queryset(self):
        """Auto-mark instances as overdue before returning results."""
        today = date.today()
        # Bulk-update all stale instances that are past their scheduled date
        MaintenanceInstance.objects.filter(
            scheduled_date__lt=today,
            status__in=['planned', 'due', 'in_progress']
        ).update(status='overdue')

        return MaintenanceInstance.objects.select_related(
            'plan', 'equipment__brand', 'equipment__responsible',
            'assigned_to', 'completed_by'
        ).prefetch_related('photos').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MaintenanceInstanceDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return MaintenanceInstanceUpdateSerializer
        return MaintenanceInstanceListSerializer

    def partial_update(self, request, *args, **kwargs):
        """PATCH: обновляем task_states и возвращаем полный детальный ответ с фото"""
        instance = self.get_object()
        serializer = MaintenanceInstanceUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Return full detail so frontend doesn't lose photos
        detail = MaintenanceInstanceDetailSerializer(instance)
        return Response(detail.data)
    
    def get_permissions(self):
        """Все аутентифицированные пользователи могут видеть и выполнять любое ТО"""
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Фильтрация инстансов — видят все аутентифицированные пользователи"""
        queryset = super().get_queryset()
        
        # Фильтрация по диапазону дат
        date_after = self.request.query_params.get('scheduled_date_after')
        date_before = self.request.query_params.get('scheduled_date_before')
        if date_after:
            queryset = queryset.filter(scheduled_date__gte=date_after)
        if date_before:
            queryset = queryset.filter(scheduled_date__lte=date_before)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_todos(self, request):
        """
        Получить список моих ТО для выполнения
        
        Возвращает только:
        - status = 'due' или 'overdue'
        - Сегодня или просроченные
        
        Query params:
        - equipment (int): фильтр по ID техники
        """
        today = date.today()
        
        queryset = self.get_queryset().filter(
            Q(status='due') | Q(status='overdue'),
            scheduled_date__lte=today
        ).order_by('scheduled_date')
        
        # Фильтрация по технике если передан параметр
        equipment_id = request.query_params.get('equipment')
        if equipment_id:
            queryset = queryset.filter(equipment_id=equipment_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Начать выполнение ТО
        
        - Меняет status: planned/due → in_progress
        - Устанавливает started_at
        """
        instance = self.get_object()
        
        # Проверка статуса
        if instance.status not in ['planned', 'due', 'overdue']:
            return Response(
                {'error': f'Нельзя начать ТО со статусом "{instance.get_status_display()}"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Обновление
        instance.status = 'in_progress'
        instance.started_at = timezone.now()
        instance.save()
        
        serializer = MaintenanceInstanceDetailSerializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Завершить ТО
        
        Проверяет:
        - Все обязательные задачи выполнены
        - Загружено минимум 1 фото
        
        Затем:
        - Меняет status: in_progress → done
        - Устанавливает completed_at и completed_by
        """
        instance = self.get_object()
        
        # Проверка статуса
        if instance.status != 'in_progress':
            return Response(
                {'error': f'Нельзя завершить ТО со статусом "{instance.get_status_display()}"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка обязательных задач
        required_tasks_incomplete = []
        for task in instance.task_states:
            if task.get('is_required', True) and task.get('status') != 'done':
                required_tasks_incomplete.append(task.get('title', 'Неизвестная задача'))
        
        if required_tasks_incomplete:
            return Response(
                {
                    'error': 'Не все обязательные задачи выполнены',
                    'incomplete_tasks': required_tasks_incomplete
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка фото
        if instance.photos.count() == 0:
            return Response(
                {'error': 'Необходимо загрузить минимум 1 фото'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Завершение
        instance.status = 'done'
        instance.completed_at = timezone.now()
        instance.completed_by = request.user
        instance.save()
        
        serializer = MaintenanceInstanceDetailSerializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Отменить ТО (только для суперюзеров)
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Только администраторы могут отменять ТО'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance = self.get_object()
        
        if instance.status == 'done':
            return Response(
                {'error': 'Нельзя отменить уже выполненное ТО'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.status = 'cancelled'
        instance.save()
        
        serializer = MaintenanceInstanceDetailSerializer(instance)
        return Response(serializer.data)


class MaintenancePhotoViewSet(viewsets.ModelViewSet):
    """
    ViewSet для фото ТО
    
    create: Загрузить фото
    destroy: Удалить фото
    """
    queryset = MaintenancePhoto.objects.select_related('instance', 'uploaded_by').all()
    serializer_class = MaintenancePhotoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтрация фото по instance"""
        queryset = super().get_queryset()
        instance_id = self.request.query_params.get('instance', None)
        if instance_id:
            queryset = queryset.filter(instance_id=instance_id)
        return queryset
    
    def perform_create(self, serializer):
        """Автоматически установить uploaded_by"""
        serializer.save(uploaded_by=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Удалить фото (только если ТО не завершено)"""
        photo = self.get_object()
        
        if photo.instance.status == 'done':
            return Response(
                {'error': 'Нельзя удалить фото из завершённого ТО'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)
