from django.contrib import admin
from .models import Notification, NotificationElement


class NotificationElementInline(admin.StackedInline):
    model = NotificationElement
    extra = 1
    fields = ['element_type', 'order', 'text_content', 'image', 'video_url']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'recipient', 'created_at', 'read_count', 'elements_count']
    list_filter = ['type', 'created_at']
    search_fields = ['title', 'body']
    readonly_fields = ['id', 'created_at', 'read_by']
    inlines = [NotificationElementInline]
    fieldsets = (
        ('Содержимое', {
            'fields': ('type', 'title', 'body'),
        }),
        ('Получатель', {
            'description': 'Оставьте "Получатель" пустым → уведомление получат все пользователи.',
            'fields': ('recipient', 'related_instance'),
        }),
        ('Служебное', {
            'fields': ('id', 'created_at', 'read_by'),
            'classes': ('collapse',),
        }),
    )

    def read_count(self, obj):
        return obj.read_by.count()
    read_count.short_description = 'Прочитали'

    def elements_count(self, obj):
        c = obj.elements.count()
        return f'{c} эл.' if c else '—'
    elements_count.short_description = 'Контент'
