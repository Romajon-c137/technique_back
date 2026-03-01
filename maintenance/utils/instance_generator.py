"""
Генератор инстансов технического обслуживания
"""
from datetime import date, timedelta
from calendar import monthrange
import logging

logger = logging.getLogger(__name__)


def generate_instances_for_plan(plan, days_ahead=30):
    """
    Генерирует инстансы ТО для плана на указанное количество дней вперед
    
    Args:
        plan: MaintenancePlan instance
        days_ahead: количество дней для генерации (по умолчанию 30)
    
    Returns:
        tuple: (created_count, skipped_count)
    """
    from maintenance.models import MaintenanceInstance
    
    if not plan.is_active:
        logger.info(f"План {plan} неактивен, пропуск генерации")
        return (0, 0)
    
    today = date.today()
    end_date = today + timedelta(days=days_ahead)
    
    created = 0
    skipped = 0
    
    if plan.type == 'daily':
        created, skipped = _generate_daily_instances(plan, today, end_date)
    elif plan.type == 'weekly':
        created, skipped = _generate_weekly_instances(plan, today, end_date)
    elif plan.type == 'monthly':
        created, skipped = _generate_monthly_instances(plan, today, end_date)
    elif plan.type == 'one_time':
        created, skipped = _generate_onetime_instance(plan, today, end_date)
    
    logger.info(f"План {plan}: создано {created}, пропущено {skipped} инстансов")
    return (created, skipped)


def _generate_daily_instances(plan, start_date, end_date):
    """Генерация ежедневных инстансов"""
    created_count = 0
    skipped_count = 0
    
    current_date = max(start_date, plan.start_date)
    
    while current_date <= end_date:
        if _create_instance_if_not_exists(plan, current_date):
            created_count += 1
        else:
            skipped_count += 1
        current_date += timedelta(days=1)
    
    return (created_count, skipped_count)


def _generate_weekly_instances(plan, start_date, end_date):
    """Генерация еженедельных инстансов"""
    if plan.weekday is None:
        logger.error(f"План {plan} типа weekly не имеет weekday")
        return (0, 0)
    
    created_count = 0
    skipped_count = 0
    
    # Находим первую дату с нужным днем недели
    current_date = max(start_date, plan.start_date)
    
    # Переходим к ближайшему нужному дню недели
    days_ahead = (plan.weekday - current_date.weekday()) % 7
    current_date += timedelta(days=days_ahead)
    
    while current_date <= end_date:
        if current_date >= plan.start_date:
            if _create_instance_if_not_exists(plan, current_date):
                created_count += 1
            else:
                skipped_count += 1
        current_date += timedelta(weeks=1)
    
    return (created_count, skipped_count)


def _generate_monthly_instances(plan, start_date, end_date):
    """Генерация ежемесячных инстансов"""
    if plan.day_of_month is None:
        logger.error(f"План {plan} типа monthly не имеет day_of_month")
        return (0, 0)
    
    created_count = 0
    skipped_count = 0
    
    current_date = max(start_date, plan.start_date)
    
    # Начинаем с текущего месяца
    year = current_date.year
    month = current_date.month
    
    while True:
        # Получаем последний день текущего месяца
        last_day = monthrange(year, month)[1]
        
        # Выбираем день: либо указанный, либо последний день месяца
        day = min(plan.day_of_month, last_day)
        
        try:
            scheduled_date = date(year, month, day)
        except ValueError:
            logger.error(f"Невозможно создать дату {year}-{month}-{day}")
            break
        
        if scheduled_date > end_date:
            break
        
        if scheduled_date >= plan.start_date and scheduled_date >= start_date:
            if _create_instance_if_not_exists(plan, scheduled_date):
                created_count += 1
            else:
                skipped_count += 1
        
        # Переходим к следующему месяцу
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    return (created_count, skipped_count)


def _generate_onetime_instance(plan, start_date, end_date):
    """Генерация одноразового инстанса"""
    if plan.scheduled_date is None:
        logger.error(f"План {plan} типа one_time не имеет scheduled_date")
        return (0, 0)
    
    # Проверяем, что дата в диапазоне
    if plan.scheduled_date < start_date or plan.scheduled_date > end_date:
        return (0, 0)
    
    if _create_instance_if_not_exists(plan, plan.scheduled_date):
        return (1, 0)
    else:
        return (0, 1)


def _create_instance_if_not_exists(plan, scheduled_date):
    """
    Создает инстанс ТО, если он еще не существует (идемпотентность)
    
    Returns:
        bool: True если создан новый инстанс, False если уже существовал
    """
    from maintenance.models import MaintenanceInstance
    
    # Проверяем существование (unique constraint)
    if MaintenanceInstance.objects.filter(
        plan=plan,
        scheduled_date=scheduled_date
    ).exists():
        return False
    
    # Копируем задачи из плана в task_states
    task_states = []
    for task in plan.tasks.all().order_by('order'):
        task_states.append({
            'title': task.title,
            'is_required': task.is_required,
            'order': task.order,
            'status': 'pending',
            'checked_by_id': None,
            'checked_at': None,
            'comment': ''
        })
    
    # Создаем инстанс
    instance = MaintenanceInstance.objects.create(
        plan=plan,
        equipment=plan.equipment,  # Автоматически берём из плана
        scheduled_date=scheduled_date,
        task_states=task_states,
        status='planned'
    )
    
    logger.debug(f"Создан инстанс {instance}")
    return True


def generate_instance_for_plan(plan):
    """
    Генерирует один инстанс ТО для плана на ближайшую дату
    Используется для кнопки "Создать сейчас" в админке
    
    Args:
        plan: MaintenancePlan instance
    
    Returns:
        tuple: (created_count, skipped_count)
    """
    from maintenance.models import MaintenanceInstance
    
    if not plan.is_active:
        logger.info(f"План {plan} неактивен")
        return (0, 0)
    
    today = date.today()
    
    # Выбираем дату для создания инстанса в зависимости от типа плана
    if plan.type == 'daily':
        scheduled_date = max(today, plan.start_date)
    elif plan.type == 'weekly':
        if plan.weekday is None:
            return (0, 0)
        # Ближайший день недели
        current_date = max(today, plan.start_date)
        days_ahead = (plan.weekday - current_date.weekday()) % 7
        scheduled_date = current_date + timedelta(days=days_ahead)
    elif plan.type == 'monthly':
        if plan.day_of_month is None:
            return (0, 0)
        # Ближайшее число месяца
        year = today.year
        month = today.month
        last_day = monthrange(year, month)[1]
        day = min(plan.day_of_month, last_day)
        scheduled_date = date(year, month, day)
        if scheduled_date < today:
            # Следующий месяц
            month += 1
            if month > 12:
                month = 1
                year += 1
            last_day = monthrange(year, month)[1]
            day = min(plan.day_of_month, last_day)
            scheduled_date = date(year, month, day)
    elif plan.type == 'one_time':
        if plan.scheduled_date is None:
            return (0, 0)
        scheduled_date = plan.scheduled_date
    else:
        return (0, 0)
    
    # Создаем инстанс если его нет
    if _create_instance_if_not_exists(plan, scheduled_date):
        return (1, 0)
    else:
        return (0, 1)


def generate_instances_for_all_plans(days_ahead=30):
    """
    Главная функция генерации: проходится по всем активным планам
    и создает для них инстансы на указанное количество дней вперед
    
    Args:
        days_ahead: количество дней для генерации (по умолчанию 30)
    
    Returns:
        dict: статистика генерации
    """
    from maintenance.models import MaintenancePlan
    
    plans = MaintenancePlan.objects.filter(is_active=True).prefetch_related('tasks')
    
    total_created = 0
    total_skipped = 0
    plans_processed = 0
    
    for plan in plans:
        created, skipped = generate_instances_for_plan(plan, days_ahead)
        total_created += created
        total_skipped += skipped
        plans_processed += 1
    
    return {
        'plans_processed': plans_processed,
        'instances_created': total_created,
        'instances_skipped': total_skipped
    }

