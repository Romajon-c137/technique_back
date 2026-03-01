"""
Команда для ретроспективной генерации уведомлений для уже существующих инстансов.
Нужна для первоначальной загрузки или если сервер был выключен.

В штатном режиме уведомления создаются автоматически через сигналы (notifications/signals.py)
при каждом сохранении MaintenanceInstance.

Использование:
    python manage.py generate_notifications
"""
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from maintenance.models import MaintenanceInstance


class Command(BaseCommand):
    help = 'Ретроспективно создать уведомления для существующих инстансов (re-save → сигналы)'

    def handle(self, *args, **options):
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # ── 1. ТО на сегодня и завтра ──────────────────────────────────────────
        due_qs = MaintenanceInstance.objects.filter(
            scheduled_date__in=[today, tomorrow],
            status__in=['planned', 'due', 'in_progress'],
        ).select_related('equipment__responsible', 'plan', 'equipment__brand')

        self.stdout.write(f'Инстансов на сегодня/завтра: {due_qs.count()}')
        for inst in due_qs:
            inst.save()  # запускает сигнал → создаёт уведомление если нет дубликата
            self.stdout.write(f'  ✓ {inst}')

        # ── 2. Просроченные ────────────────────────────────────────────────────
        overdue_qs = MaintenanceInstance.objects.filter(
            status='overdue',
        ).select_related('equipment__responsible', 'plan', 'equipment__brand')

        self.stdout.write(f'Просроченных: {overdue_qs.count()}')
        for inst in overdue_qs:
            inst.save()
            self.stdout.write(f'  ✓ {inst}')

        from notifications.models import Notification
        total = Notification.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\nГотово. Всего уведомлений в системе: {total}'))
