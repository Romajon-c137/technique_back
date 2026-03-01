#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

# Удалить существующего пользователя если есть
User.objects.filter(phone='1').delete()

# Создать нового суперпользователя
user = User.objects.create_superuser(
    phone='1',
    password='1',
    full_name='Admin',
    role='admin'
)

print(f'✅ Суперпользователь создан!')
print(f'   Логин (телефон): 1')
print(f'   Пароль: 1')
print(f'   Роль: {user.role}')
