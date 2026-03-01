from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Brand(models.Model):
    """Модель для брендов техники"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название бренда'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['name']

    def __str__(self):
        return self.name


class TechTag(models.Model):
    """Модель для тегов техники"""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название тега'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Equipment(models.Model):
    """Модель для техники"""
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='equipment',
        verbose_name='Бренд'
    )
    model = models.CharField(
        max_length=200,
        verbose_name='Модель'
    )
    tag = models.ForeignKey(
        TechTag,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipment',
        verbose_name='Тег'
    )
    responsible = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='equipment',
        verbose_name='Ответственный'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Техника'
        verbose_name_plural = 'Техника'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['brand', 'model', 'tag'],
                name='unique_equipment'
            )
        ]

    def __str__(self):
        return f"{self.brand.name} {self.model}"


class EquipmentImage(models.Model):
    """Модель для изображений техники"""
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Техника'
    )
    image = models.ImageField(
        upload_to='equipment_images/',
        verbose_name='Изображение'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='Основное изображение'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        verbose_name = 'Изображение техники'
        verbose_name_plural = 'Изображения техники'
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        primary_mark = " (основное)" if self.is_primary else ""
        return f"Изображение для {self.equipment}{primary_mark}"


class Hint(models.Model):
    """Модель для подсказок по технике"""
    
    TYPE_CHOICES = [
        ('guide', 'Руководство'),
        ('error', 'Ошибка'),
    ]
    
    technique = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='hints',
        verbose_name='Техника'
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name='Тип подсказки'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Подсказка'
        verbose_name_plural = 'Подсказки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"


class HintElement(models.Model):
    """Модель для элементов подсказки (текст, картинка, видео)"""
    
    ELEMENT_TYPE_CHOICES = [
        ('text', 'Текст'),
        ('image', 'Картинка'),
        ('video', 'Видео'),
    ]
    
    hint = models.ForeignKey(
        Hint,
        on_delete=models.CASCADE,
        related_name='elements',
        verbose_name='Подсказка'
    )
    element_type = models.CharField(
        max_length=10,
        choices=ELEMENT_TYPE_CHOICES,
        verbose_name='Тип элемента'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )
    
    # Поля для разных типов контента
    text_content = models.TextField(
        blank=True,
        null=True,
        verbose_name='Текстовое содержимое'
    )
    image = models.ImageField(
        upload_to='hint_images/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на видео'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Элемент подсказки'
        verbose_name_plural = 'Элементы подсказки'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.get_element_type_display()} #{self.order}"
