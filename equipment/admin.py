from django.contrib import admin
from .models import Brand, TechTag, Equipment, EquipmentImage, Hint


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Админ-панель для брендов"""
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TechTag)
class TechTagAdmin(admin.ModelAdmin):
    """Админ-панель для тегов"""
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


class EquipmentImageInline(admin.TabularInline):
    """Inline для загрузки изображений в форме техники"""
    model = EquipmentImage
    extra = 1
    fields = ('image', 'is_primary')


class HintInline(admin.StackedInline):
    """Inline для создания подсказок прямо в форме техники"""
    model = Hint
    extra = 0
    fields = ('type', 'title')
    show_change_link = True
    verbose_name = 'Подсказка'
    verbose_name_plural = 'Подсказки'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Админ-панель для техники"""
    list_display = ('__str__', 'brand', 'model', 'tag', 'responsible', 'created_at')
    list_filter = ('brand', 'tag', 'responsible')
    search_fields = ('model', 'brand__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [EquipmentImageInline, HintInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('brand', 'model', 'tag', 'responsible')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


from .models import Hint, HintElement
from django import forms


class HintElementInlineForm(forms.ModelForm):
    """Форма для элементов подсказки с валидацией"""
    
    class Meta:
        model = HintElement
        fields = '__all__'
    
    def clean(self):
        """Валидация: обязательное поле должно быть заполнено в зависимости от типа"""
        cleaned_data = super().clean()
        element_type = cleaned_data.get('element_type')
        text_content = cleaned_data.get('text_content')
        image = cleaned_data.get('image')
        video_url = cleaned_data.get('video_url')
        
        if element_type == 'text' and not text_content:
            raise forms.ValidationError('Для типа "Текст" необходимо заполнить текстовое содержимое')
        
        if element_type == 'image' and not image:
            raise forms.ValidationError('Для типа "Картинка" необходимо загрузить изображение')
        
        if element_type == 'video' and not video_url:
            raise forms.ValidationError('Для типа "Видео" необходимо указать ссылку на видео')
        
        return cleaned_data


class HintElementInline(admin.TabularInline):
    """Inline для добавления элементов подсказки с динамическим отображением полей"""
    model = HintElement
    form = HintElementInlineForm
    extra = 1
    fields = ('element_type', 'order', 'text_content', 'image', 'video_url')
    
    class Media:
        js = ('admin/js/hint_element_dynamic.js',)


@admin.register(Hint)
class HintAdmin(admin.ModelAdmin):
    """Админ-панель для подсказок"""
    list_display = ('title', 'type', 'technique', 'created_at')
    list_filter = ('type', 'technique')
    search_fields = ('title', 'technique__model', 'technique__brand__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [HintElementInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('technique', 'type', 'title')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

