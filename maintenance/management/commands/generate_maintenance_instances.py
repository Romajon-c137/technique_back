"""
Management command для генерации инстансов ТО
"""
from django.core.management.base import BaseCommand
from maintenance.models import MaintenancePlan
from maintenance.utils.instance_generator import generate_instances_for_plan


class Command(BaseCommand):
    help = 'Генерирует инстансы ТО на указанное количество дней вперед'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Количество дней вперед для генерации (по умолчанию 30)'
        )
        parser.add_argument(
            '--plan-id',
            type=str,
            help='ID конкретного плана для генерации (опционально)'
        )

    def handle(self, *args, **options):
        days_ahead = options['days']
        plan_id = options.get('plan_id')
        
        self.stdout.write(f'Генерация инстансов ТО на {days_ahead} дней вперед...')
        
        # Получаем планы для обработки
        if plan_id:
            plans = MaintenancePlan.objects.filter(id=plan_id, is_active=True)
            if not plans.exists():
                self.stdout.write(self.style.ERROR(f'План с ID {plan_id} не найден или неактивен'))
                return
        else:
            plans = MaintenancePlan.objects.filter(is_active=True)
        
        total_created = 0
        total_skipped = 0
        plans_processed = 0
        
        for plan in plans:
            created, skipped = generate_instances_for_plan(plan, days_ahead)
            total_created += created
            total_skipped += skipped
            plans_processed += 1
            
            if created > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'План "{plan.title}": создано {created}, пропущено {skipped}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nИтого: обработано планов {plans_processed}, '
                f'создано инстансов {total_created}, пропущено {total_skipped}'
            )
        )
