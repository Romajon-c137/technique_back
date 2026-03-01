from rest_framework import serializers
from .models import MaintenancePlan, MaintenanceTask, MaintenanceInstance, MaintenancePhoto
from users.serializers import UserSerializer


# ==========================================
# УПРОЩЁННЫЕ СЕРИАЛИЗАТОРЫ ДЛЯ СПИСКОВ
# ==========================================

class LightUserSerializer(serializers.ModelSerializer):
    """Упрощённый сериализатор пользователя - только нужные поля"""
    
    class Meta:
        model = UserSerializer.Meta.model
        fields = ['id', 'full_name', 'avatar', 'role']
        read_only_fields = ['id']


class LightEquipmentSerializer(serializers.Serializer):
    """Упрощённый сериализатор техники - БЕЗ hints, изображений и лишнего"""
    id = serializers.IntegerField()
    brand_name = serializers.CharField(source='brand.name')
    model = serializers.CharField()
    responsible = LightUserSerializer(read_only=True)


class MaintenanceTaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач ТО"""
    
    class Meta:
        model = MaintenanceTask
        fields = ['id', 'title', 'is_required', 'order']
        read_only_fields = ['id']


# ==========================================
# СЕРИАЛИЗАТОРЫ ДЛЯ ПЛАНОВ ТО
# ==========================================

class MaintenancePlanListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка планов ТО - упрощённый"""
    equipment = LightEquipmentSerializer(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenancePlan
        fields = [
            'id', 'equipment', 'title', 'type', 'type_display',
            'start_date', 'is_active', 'tasks_count'
        ]
        read_only_fields = ['id']
    
    def get_tasks_count(self, obj):
        return obj.tasks.count()


class MaintenancePlanDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для плана ТО - с полной информацией"""
    from equipment.serializers import EquipmentSerializer
    
    equipment = EquipmentSerializer(read_only=True)
    tasks = MaintenanceTaskSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = MaintenancePlan
        fields = [
            'id', 'equipment', 'title', 'type', 'type_display',
            'start_date', 'scheduled_date', 'weekday', 'day_of_month',
            'is_active', 'tasks', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MaintenancePhotoSerializer(serializers.ModelSerializer):
    """Сериализатор для фото ТО"""
    uploaded_by = LightUserSerializer(read_only=True)
    
    class Meta:
        model = MaintenancePhoto
        fields = ['id', 'instance', 'image', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']


# ==========================================
# СЕРИАЛИЗАТОРЫ ДЛЯ ИНСТАНСОВ ТО
# ==========================================

class MaintenanceInstanceListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка инстансов ТО - ТОЛЬКО НУЖНЫЕ ДАННЫЕ"""
    plan_title = serializers.CharField(source='plan.title')
    plan_type = serializers.CharField(source='plan.type')
    plan_type_display = serializers.CharField(source='plan.get_type_display')
    
    equipment = LightEquipmentSerializer(read_only=True)
    assigned_to = LightUserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceInstance
        fields = [
            'id', 'plan_title', 'plan_type', 'plan_type_display',
            'equipment', 'scheduled_date', 'assigned_to',
            'status', 'status_display', 'task_states', 'progress',
            'completed_at'
        ]
        read_only_fields = ['id']
    
    def get_progress(self, obj):
        """Вычислить прогресс выполнения задач"""
        if not obj.task_states:
            return {'completed': 0, 'total': 0, 'percentage': 0}
        
        total = len(obj.task_states)
        completed = sum(1 for task in obj.task_states if task.get('status') == 'done')
        percentage = int((completed / total * 100)) if total > 0 else 0
        
        return {
            'completed': completed,
            'total': total,
            'percentage': percentage
        }


class MaintenanceInstanceDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для инстанса ТО - с полной информацией"""
    from equipment.serializers import EquipmentSerializer
    
    plan = MaintenancePlanDetailSerializer(read_only=True)
    equipment = EquipmentSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    completed_by = UserSerializer(read_only=True)
    photos = MaintenancePhotoSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceInstance
        fields = [
            'id', 'plan', 'equipment', 'scheduled_date', 'assigned_to',
            'status', 'status_display', 'task_states', 'progress',
            'started_at', 'completed_at', 'completed_by', 'photos',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'plan', 'equipment', 'status', 'started_at',
            'completed_at', 'completed_by', 'created_at', 'updated_at'
        ]
    
    def get_progress(self, obj):
        """Вычислить прогресс выполнения задач"""
        if not obj.task_states:
            return {'completed': 0, 'total': 0, 'percentage': 0}
        
        total = len(obj.task_states)
        completed = sum(1 for task in obj.task_states if task.get('status') == 'done')
        percentage = int((completed / total * 100)) if total > 0 else 0
        
        return {
            'completed': completed,
            'total': total,
            'percentage': percentage
        }
    
    def validate_task_states(self, value):
        """Валидация task_states"""
        if not isinstance(value, list):
            raise serializers.ValidationError("task_states должен быть списком")
        
        required_fields = ['title', 'is_required', 'order', 'status']
        for i, task in enumerate(value):
            # Проверка наличия обязательных полей
            for field in required_fields:
                if field not in task:
                    raise serializers.ValidationError(
                        f"Задача {i}: отсутствует обязательное поле '{field}'"
                    )
            
            # Проверка статуса
            if task['status'] not in ['pending', 'done', 'skipped']:
                raise serializers.ValidationError(
                    f"Задача {i}: некорректный статус '{task['status']}'"
                )
            
            # Нельзя пропустить обязательную задачу
            if task['is_required'] and task['status'] == 'skipped':
                raise serializers.ValidationError(
                    f"Задача {i}: нельзя пропустить обязательную задачу"
                )
        
        return value


class MaintenanceInstanceUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления task_states"""
    
    class Meta:
        model = MaintenanceInstance
        fields = ['task_states']
    
    def validate_task_states(self, value):
        """Валидация task_states"""
        if not isinstance(value, list):
            raise serializers.ValidationError("task_states должен быть списком")
        
        required_fields = ['title', 'is_required', 'order', 'status']
        for i, task in enumerate(value):
            # Проверка наличия обязательных полей
            for field in required_fields:
                if field not in task:
                    raise serializers.ValidationError(
                        f"Задача {i}: отсутствует обязательное поле '{field}'"
                    )
            
            # Проверка статуса
            if task['status'] not in ['pending', 'done', 'skipped']:
                raise serializers.ValidationError(
                    f"Задача {i}: некорректный статус '{task['status']}'"
                )
            
            # Нельзя пропустить обязательную задачу
            if task['is_required'] and task['status'] == 'skipped':
                raise serializers.ValidationError(
                    f"Задача {i}: нельзя пропустить обязательную задачу"
                )
        
        return value
