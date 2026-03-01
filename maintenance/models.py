import uuid
from django.db import models
from django.core.exceptions import ValidationError
from equipment.models import Equipment
from users.models import User


class MaintenancePlan(models.Model):
    """План технического обслуживания"""
    
    TYPE_CHOICES = [
        ('daily', 'Ежедневное'),
        ('weekly', 'Еженедельное'),
        ('monthly', 'Ежемесячное'),
        ('one_time', 'Одноразовое'),
    ]
    
    WEEKDAY_CHOICES = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='maintenance_plans',
        verbose_name='Техника'
    )
    title = models.CharField(max_length=255, verbose_name='Название ТО')
    
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Тип периодичности'
    )
    start_date = models.DateField(verbose_name='Дата начала')
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Запланированная дата (для одноразового)'
    )
    weekday = models.IntegerField(
        null=True,
        blank=True,
        choices=WEEKDAY_CHOICES,
        verbose_name='День недели (для еженедельного)'
    )
    day_of_month = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='День месяца (для ежемесячного)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    generate_first_instance = models.BooleanField(
        default=False,
        verbose_name='Создать инстанс сейчас',
        help_text='Создать первый инстанс ТО сразу при сохранении плана'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_maintenance_plans',
        verbose_name='Создал'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'План ТО'
        verbose_name_plural = 'Планы ТО'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['equipment', 'type', 'is_active']),
            models.Index(fields=['is_active', 'type']),
        ]
    
    def __str__(self):
        return f"{self.equipment} - {self.title}"
    
    def clean(self):
        """Валидация полей в зависимости от типа ТО"""
        if self.type == 'weekly' and self.weekday is None:
            raise ValidationError({'weekday': 'Для еженедельного ТО необходимо указать день недели'})
        
        if self.type == 'monthly' and self.day_of_month is None:
            raise ValidationError({'day_of_month': 'Для ежемесячного ТО необходимо указать день месяца'})
        
        if self.type == 'monthly' and (self.day_of_month < 1 or self.day_of_month > 31):
            raise ValidationError({'day_of_month': 'День месяца должен быть от 1 до 31'})
        
        if self.type == 'one_time' and self.scheduled_date is None:
            raise ValidationError({'scheduled_date': 'Для одноразового ТО необходимо указать дату'})


class MaintenanceTask(models.Model):
    """Задача в плане ТО"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        MaintenancePlan,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='План ТО'
    )
    title = models.CharField(max_length=255, verbose_name='Название задачи')
    is_required = models.BooleanField(default=True, verbose_name='Обязательная')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Задача ТО'
        verbose_name_plural = 'Задачи ТО'
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=['plan', 'order']),
        ]
    
    def __str__(self):
        req = "✓" if self.is_required else "○"
        return f"{req} {self.title}"


class MaintenanceInstance(models.Model):
    """Инстанс ТО на конкретную дату"""
    
    STATUS_CHOICES = [
        ('planned', 'Запланировано'),
        ('due', 'Необходимо выполнить'),
        ('in_progress', 'В процессе'),
        ('done', 'Выполнено'),
        ('overdue', 'Просрочено'),
        ('cancelled', 'Отменено'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        MaintenancePlan,
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name='План ТО'
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='maintenance_instances',
        verbose_name='Техника'
    )
    scheduled_date = models.DateField(verbose_name='Запланированная дата')
    
    # Исполнитель (кто должен выполнить ТО)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenances',
        verbose_name='Исполнитель (назначен)'
    )
    
    # Состояние задач в JSON формате (копия на момент создания)
    task_states = models.JSONField(
        default=list,
        verbose_name='Состояние задач',
        help_text='[{"title": "...", "is_required": true, "status": "pending", ...}]'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name='Статус'
    )
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Начато')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершено')
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_maintenances',
        verbose_name='Завершил'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Инстанс ТО'
        verbose_name_plural = 'Инстансы ТО'
        ordering = ['scheduled_date']
        constraints = [
            models.UniqueConstraint(
                fields=['plan', 'scheduled_date'],
                name='unique_maintenance_instance'
            )
        ]
        indexes = [
            models.Index(fields=['scheduled_date', 'status']),
            models.Index(fields=['equipment', 'scheduled_date']),
            models.Index(fields=['plan', 'scheduled_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.equipment} - {self.plan.title} - {self.scheduled_date}"


class MaintenancePhoto(models.Model):
    """Фото-отчет для инстанса ТО"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(
        MaintenanceInstance,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Инстанс ТО'
    )
    image = models.ImageField(
        upload_to='maintenance_photos/',
        verbose_name='Фотография'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_maintenance_photos',
        verbose_name='Загрузил'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    
    class Meta:
        verbose_name = 'Фото ТО'
        verbose_name_plural = 'Фото ТО'
        ordering = ['uploaded_at']
        indexes = [
            models.Index(fields=['instance']),
        ]
    
    def __str__(self):
        return f"Фото для {self.instance}"
