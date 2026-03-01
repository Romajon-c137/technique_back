#!/usr/bin/env python
"""Скрипт для создания суперпользователя"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

# Создаем суперпользователя если его еще нет
phone = '+996700123456'
password = 'admin123'

if not User.objects.filter(phone=phone).exists():
    user = User.objects.create_superuser(
        phone=phone,
        password=password,
        full_name='Администратор'
    )
    print(f'✅ Суперпользователь создан:')
    print(f'   Телефон: {phone}')
    print(f'   Пароль: {password}')
else:
    print(f'⚠️  Пользователь с телефоном {phone} уже существует')

# Создаем тестовых пользователей
test_users = [
    {
        'phone': '+996700111111',
        'password': 'engineer123',
        'full_name': 'Иван Инженеров',
        'role': 'engineer'
    },
    {
        'phone': '+996700222222',
        'password': 'manager123',
        'full_name': 'Мария Менеджер',
        'role': 'manager'
    }
]

for user_data in test_users:
    phone = user_data.pop('phone')
    password = user_data.pop('password')
    
    if not User.objects.filter(phone=phone).exists():
        user = User.objects.create_user(phone=phone, password=password, **user_data)
        print(f'✅ Пользователь создан: {user.full_name} ({phone})')
    else:
        print(f'⚠️  Пользователь {phone} уже существует')

print('\n📝 Данные для входа:')
print('=' * 50)
print('Админ:    +996700123456 / admin123')
print('Инженер:  +996700111111 / engineer123')
print('Менеджер: +996700222222 / manager123')
