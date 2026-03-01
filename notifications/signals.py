"""
Сигналы для авто-создания уведомлений.

Правила:
  • При создании инстанса:
      - scheduled_date == сегодня → maintenance_today
      - scheduled_date == завтра  → maintenance_today  (напоминание за 1 день)
      - status == 'overdue'       → maintenance_overdue (edge case)
  • При изменении статуса инстанса:
      - новый статус 'due'     → maintenance_today    (система переключила в "надо выполнить")
      - новый статус 'overdue' → maintenance_overdue
"""
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

# Используем строки для ленивого импорта (избегаем circular imports)


def _get_models():
    from maintenance.models import MaintenanceInstance
    from notifications.models import Notification
    return MaintenanceInstance, Notification


def _create_if_not_exists(notif_type: str, instance, recipient):
    """Создаёт уведомление только если такое ещё не существует для этого инстанса сегодня."""
    _, Notification = _get_models()
    today = date.today()
    exists = Notification.objects.filter(
        type=notif_type,
        related_instance=instance,
        created_at__date=today,
    ).exists()
    if exists:
        return None

    messages = {
        'maintenance_today': (
            f'ТО сегодня: {instance.equipment}',
            f'Техобслуживание «{instance.plan.title}» запланировано на {instance.scheduled_date}. Выполните сегодня!'
        ),
        'maintenance_overdue': (
            f'Просрочено: {instance.equipment}',
            f'Техобслуживание «{instance.plan.title}» было запланировано на {instance.scheduled_date} и не выполнено. Срочно!'
        ),
    }
    title, body = messages[notif_type]

    return Notification.objects.create(
        type=notif_type,
        title=title,
        body=body,
        recipient=recipient,
        related_instance=instance,
    )


@receiver(post_save, sender='maintenance.MaintenanceInstance')
def handle_instance_save(sender, instance, created, **kwargs):
    """
    Срабатывает каждый раз при сохранении MaintenanceInstance.
    Логика:
      1. Если новый статус 'overdue' → maintenance_overdue ответственному
      2. Если статус 'due' или 'in_progress' или дата = сегодня/завтра → maintenance_today
    """
    try:
        responsible = instance.equipment.responsible
    except Exception:
        return  # если нет ответственного — пропускаем

    today = date.today()
    tomorrow = today + timedelta(days=1)
    status = instance.status
    sched = instance.scheduled_date

    # Просроченное ТО
    if status == 'overdue':
        _create_if_not_exists('maintenance_overdue', instance, responsible)
        return

    # ТО на сегодня или завтра (напоминание за день)
    if status in ('due', 'in_progress', 'planned') and sched in (today, tomorrow):
        _create_if_not_exists('maintenance_today', instance, responsible)
