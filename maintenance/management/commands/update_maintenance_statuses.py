"""
Management command для обновления статусов инстансов ТО
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from maintenance.models import MaintenanceInstance


class Command(BaseCommand):
    help = 'Обновляет статусы инстансов ТО (due/overdue)'

    def handle(self, *args, **options):
        today = date.today()
        
        self.stdout.write('Обновление статусов инстансов ТО...')
        
        # Обновляем просроченные
        overdue_count = MaintenanceInstance.objects.filter(
            scheduled_date__lt=today,
            status__in=['planned', 'due', 'in_progress']
        ).update(status='overdue')
        
        # Обновляем те, что нужно выполнить сегодня
        due_count = MaintenanceInstance.objects.filter(
            scheduled_date=today,
            status='planned'
        ).update(status='due')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Обновлено статусов: {overdue_count} overdue, {due_count} due'
            )
        )
