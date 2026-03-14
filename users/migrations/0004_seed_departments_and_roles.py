from django.db import migrations


def create_initial_departments_and_roles(apps, schema_editor):
    Department = apps.get_model('users', 'Department')
    Role = apps.get_model('users', 'Role')

    departments = [
        'Производство',
        'Логистика',
        'ИТ',
        'Администрация',
        'Снабжение',
    ]

    roles = [
        'Инженер',
        'Менеджер',
        'Администратор',
    ]

    for name in departments:
        Department.objects.get_or_create(name=name)

    for name in roles:
        Role.objects.get_or_create(name=name)


def reverse_initial_departments_and_roles(apps, schema_editor):
    Department = apps.get_model('users', 'Department')
    Role = apps.get_model('users', 'Role')

    Department.objects.filter(name__in=[
        'Производство',
        'Логистика',
        'ИТ',
        'Администрация',
        'Снабжение',
    ]).delete()

    Role.objects.filter(name__in=[
        'Инженер',
        'Менеджер',
        'Администратор',
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_role_user_position'),
    ]

    operations = [
        migrations.RunPython(create_initial_departments_and_roles, reverse_initial_departments_and_roles),
    ]
