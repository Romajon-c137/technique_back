from django.core.management.base import BaseCommand
from django.utils import timezone
from maintenance.models import MaintenanceInstance


class Command(BaseCommand):
    help = 'Automatically mark maintenance instances as overdue if past scheduled date'

    def handle(self, *args, **options):
        today = timezone.now().date()
        updated = MaintenanceInstance.objects.filter(
            scheduled_date__lt=today,
            status__in=['planned', 'due', 'in_progress']
        ).update(status='overdue')

        self.stdout.write(
            self.style.SUCCESS(f'Marked {updated} instance(s) as overdue.')
        )
