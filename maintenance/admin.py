from django.contrib import admin
from django import forms
from django.contrib import messages
from .models import MaintenancePlan, MaintenanceTask, MaintenanceInstance, MaintenancePhoto
from .utils.instance_generator import generate_instances_for_all_plans, generate_instance_for_plan


class MaintenanceTaskInline(admin.TabularInline):
    """Inline для задач плана ТО"""
    model = MaintenanceTask
    extra = 1
    fields = ('title', 'is_required', 'order')
    ordering = ('order',)


class MaintenancePlanAdminForm(forms.ModelForm):
    """Custom форма для динамического показа полей расписания"""
    
    class Meta:
        model = MaintenancePlan
        fields = '__all__'
    
    class Media:
        js = ('admin/js/maintenance_plan_form.js',)


@admin.register(MaintenancePlan)
class MaintenancePlanAdmin(admin.ModelAdmin):
    """Админка для планов ТО с динамическими полями"""
    form = MaintenancePlanAdminForm
    list_display = ('title', 'equipment', 'type', 'start_date', 'is_active', 'created_by', 'created_at')
    list_filter = ('type', 'is_active', 'created_at')
    search_fields = ('title', 'equipment__model', 'equipment__brand__name')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    inlines = [MaintenanceTaskInline]
    actions = ['generate_instances_action']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('equipment', 'title', 'is_active', 'generate_first_instance')
        }),
        ('Расписание', {
            'fields': ('type', 'start_date', 'scheduled_date', 'weekday', 'day_of_month'),
            'description': 'Заполните соответствующие поля в зависимости от типа ТО'
        }),
        ('Системная информация', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Автоматически установить created_by и сгенерировать первый инстанс если нужно"""
        if not change:
            obj.created_by = request.user
        
        super().save_model(request, obj, form, change)
        
        # Если стоит галочка "Создать сейчас" - создать первый инстанс
        if obj.generate_first_instance:
            created, skipped = generate_instance_for_plan(obj)
            if created > 0:
                messages.success(request, f'✅ Создан инстанс ТО для плана "{obj.title}"')
            else:
                messages.warning(request, f'⚠️ Инстанс для плана "{obj.title}" уже существует')
            
            # Сбросить флаг после генерации
            obj.generate_first_instance = False
            obj.save(update_fields=['generate_first_instance'])
    
    @admin.action(description='🔄 Сгенерировать инстансы ТО')
    def generate_instances_action(self, request, queryset):
        """Action для массовой генерации инстансов"""
        total_created = 0
        total_skipped = 0
        
        for plan in queryset.filter(is_active=True):
            created, skipped = generate_instance_for_plan(plan)
            total_created += created
            total_skipped += skipped
        
        if total_created > 0:
            messages.success(
                request,
                f'✅ Создано инстансов: {total_created}, пропущено: {total_skipped}'
            )
        else:
            messages.warning(
                request,
                f'⚠️ Новых инстансов не создано. Пропущено: {total_skipped}'
            )


class MaintenancePhotoInline(admin.TabularInline):
    """Inline для фото инстанса"""
    model = MaintenancePhoto
    extra = 0
    fields = ('image', 'uploaded_by', 'uploaded_at')
    readonly_fields = ('uploaded_by', 'uploaded_at')


class ExcludeCompletedFilter(admin.SimpleListFilter):
    """Фильтр для исключения выполненных инстансов"""
    title = 'статус (быстрый фильтр)'
    parameter_name = 'status_filter'
    
    def lookups(self, request, model_admin):
        return (
            ('not_done', 'Все кроме выполненных'),
            ('all', 'Все'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'not_done':
            return queryset.exclude(status='done')
        return queryset


@admin.register(MaintenanceInstance)
class MaintenanceInstanceAdmin(admin.ModelAdmin):
    """Админка для инстансов ТО"""
    list_display = ('equipment', 'plan', 'scheduled_date', 'assigned_to', 'status', 'completed_by', 'completed_at')
    list_filter = (ExcludeCompletedFilter, 'status', 'scheduled_date', 'assigned_to', 'created_at')
    search_fields = ('equipment__model', 'equipment__brand__name', 'plan__title')
    readonly_fields = ('equipment', 'created_at', 'updated_at', 'started_at', 'completed_at', 'completed_by')
    inlines = [MaintenancePhotoInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('plan', 'equipment', 'scheduled_date', 'assigned_to', 'status')
        }),
        ('Задачи', {
            'fields': ('task_states',),
            'description': 'Состояние задач в JSON формате'
        }),
        ('Выполнение', {
            'fields': ('started_at', 'completed_at', 'completed_by')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        """Разрешить удаление, но защитить выполненные инстансы"""
        if obj and obj.status == 'done':
            # Запретить удаление выполненных ТО
            return False
        return super().has_delete_permission(request, obj)
    
    def delete_model(self, request, obj):
        """Дополнительная проверка при удалении"""
        if obj.status == 'done':
            messages.error(request, f'❌ Нельзя удалить выполненный инстанс ТО!')
            return
        super().delete_model(request, obj)
        messages.success(request, f'✅ Инстанс ТО удалён')


@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    """Админка для задач ТО"""
    list_display = ('title', 'plan', 'is_required', 'order')
    list_filter = ('is_required',)
    search_fields = ('title', 'plan__title')
    ordering = ('plan', 'order')


@admin.register(MaintenancePhoto)
class MaintenancePhotoAdmin(admin.ModelAdmin):
    """Админка для фото ТО"""
    list_display = ('instance', 'image', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('instance__equipment__model',)
    readonly_fields = ('uploaded_by', 'uploaded_at')
