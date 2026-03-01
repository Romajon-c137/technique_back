import uuid
from django.db import models
from django.conf import settings
from maintenance.models import MaintenanceInstance


class Notification(models.Model):
    """Уведомление для пользователей"""

    TYPE_CHOICES = [
        ('maintenance_today', 'ТО на сегодня'),
        ('maintenance_overdue', 'Просроченное ТО'),
        ('manual', 'Ручное уведомление'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        verbose_name='Тип'
    )
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    body = models.TextField(verbose_name='Текст')

    # null = для всех пользователей; FK = только конкретному
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Получатель (пусто = всем)'
    )

    # Связанный инстанс ТО (если применимо)
    related_instance = models.ForeignKey(
        MaintenanceInstance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Связанное ТО'
    )

    # Кто прочитал (M2M)
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='read_notifications',
        verbose_name='Прочитали'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['type', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"


class NotificationElement(models.Model):
    """Элемент содержимого уведомления (текст / картинка / видео)"""

    ELEMENT_TYPE_CHOICES = [
        ('text',  'Текст'),
        ('image', 'Картинка'),
        ('video', 'Видео'),
    ]

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='elements',
        verbose_name='Уведомление'
    )
    element_type = models.CharField(
        max_length=10,
        choices=ELEMENT_TYPE_CHOICES,
        verbose_name='Тип элемента'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    # Контент (заполняется нужное поле в зависимости от типа)
    text_content = models.TextField(blank=True, null=True, verbose_name='Текст')
    image = models.ImageField(
        upload_to='notification_images/',
        blank=True, null=True,
        verbose_name='Изображение'
    )
    video_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на видео')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Элемент уведомления'
        verbose_name_plural = 'Элементы уведомления'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.get_element_type_display()} #{self.order}"

