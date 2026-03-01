# Akfa Technique Backend API

Django REST API для системы управления пользователями и авторизации.

## Требования

- Python 3.13+
- pip
- virtualenv (рекомендуется)

## Установка и запуск

### 1. Клонирование проекта (если нужно)

```bash
cd /Users/user/Desktop/Dev/Akfa-technique/Back
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
```

### 3. Активация виртуального окружения

```bash
source venv/bin/activate
```

### 4. Установка зависимостей

```bash
pip install -r requirements.txt
```

Если файл requirements.txt отсутствует или нужно обновить:

```bash
pip install django djangorestframework djangorestframework-simplejwt drf-spectacular Pillow django-phonenumber-field[phonenumberslite]
pip freeze > requirements.txt
```

### 5. Применение миграций базы данных

```bash
python manage.py migrate
```

### 6. Создание тестовых пользователей (опционально)

```bash
python create_users.py
```

Это создаст:
- Админ: `+996700123456` / `admin123`
- Инженер: `+996700111111` / `engineer2026`
- Менеджер: `+996700222222` / `manager123`

**ИЛИ** создать только суперпользователя вручную:

```bash
python manage.py createsuperuser
```

### 7. Запуск сервера разработки

#### Локальный запуск (только на этом компьютере):

```bash
python manage.py runserver
```

Сервер будет доступен на: `http://127.0.0.1:8000/`

#### Запуск с доступом из локальной сети:

```bash
python manage.py runserver 0.0.0.0:8000
```

Сервер будет доступен на:
- Локально: `http://127.0.0.1:8000/`
- По сети: `http://192.168.1.87:8000/` (ваш локальный IP)

---

## Основные URL

### Админ-панель
```
http://127.0.0.1:8000/admin/
```
Войдите с данными суперпользователя для управления пользователями.

### Swagger документация (API docs)
```
http://127.0.0.1:8000/api/docs/
```
Интерактивная документация всех API endpoints.

### API Schema (OpenAPI)
```
http://127.0.0.1:8000/api/schema/
```

---

## API Endpoints

### 1. Авторизация (Login)

**POST** `/api/v1/auth/login`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+996700111111",
    "password": "engineer2026"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "user": {
    "id": "uuid",
    "phone": "+996700111111",
    "full_name": "Иван Инженеров",
    "role": "engineer"
  }
}
```

### 2. Смена пароля

**POST** `/api/v1/auth/change-password`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "new_password": "newPassword123",
    "new_password_confirm": "newPassword123"
  }'
```

**Response:**
```json
{
  "message": "Пароль успешно изменен"
}
```

---

## Структура проекта

```
Back/
├── config/                 # Настройки Django проекта
│   ├── settings.py        # Главные настройки
│   ├── urls.py            # URL маршруты
│   ├── wsgi.py
│   └── asgi.py
├── users/                 # Приложение управления пользователями
│   ├── models.py          # Модель User
│   ├── views.py           # API views (Login, ChangePassword)
│   ├── serializers.py     # Сериализаторы
│   ├── admin.py           # Админ-панель
│   ├── urls.py            # URL маршруты
│   └── migrations/
├── venv/                  # Виртуальное окружение
├── db.sqlite3             # База данных SQLite
├── manage.py              # Утилита управления Django
├── requirements.txt       # Зависимости проекта
├── create_users.py        # Скрипт создания тестовых пользователей
└── README.md              # Эта инструкция
```

---

## Модель пользователя

### Поля:
- `id` — UUID (первичный ключ)
- `phone` — Номер телефона (уникальный, используется для логина)
- `password` — Хэш пароля
- `full_name` — Полное имя
- `role` — Роль: `admin`, `engineer`, `manager`
- `is_active` — Активен/заблокирован
- `avatar` — Аватар (изображение)
- `birth_date` — Дата рождения
- `last_login_at` — Время последнего входа
- `created_at` — Дата создания
- `updated_at` — Дата обновления

---

## Технологии

- **Django 6.0.1** — Web framework
- **Django REST Framework** — REST API
- **djangorestframework-simplejwt** — JWT authentication
- **drf-spectacular** — Swagger/OpenAPI документация
- **Pillow** — Обработка изображений
- **django-phonenumber-field** — Валидация номеров телефонов

---

## Настройки JWT

- Access token: **2 часа**
- Refresh token: **7 дней**
- Алгоритм: **HS256**

---

## Разработка

### Создание новых миграций

```bash
python manage.py makemigrations
```

### Применение миграций

```bash
python manage.py migrate
```

### Создание суперпользователя

```bash
python manage.py createsuperuser
```

### Запуск Django shell

```bash
python manage.py shell
```

---

## Тестирование API

### Через Swagger UI
Откройте `http://127.0.0.1:8000/api/docs/` в браузере и используйте интерактивную документацию.

### Через curl

1. Получите токен:
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+996700111111", "password": "engineer2026"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

2. Используйте токен для запросов:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"new_password": "newpass123", "new_password_confirm": "newpass123"}'
```

---

## Production

⚠️ **ВНИМАНИЕ**: Это development сервер! Для продакшена используйте:

- **Gunicorn** или **uWSGI** как WSGI сервер
- **Nginx** как reverse proxy
- **PostgreSQL** или **MySQL** вместо SQLite
- Смените `SECRET_KEY` в `settings.py`
- Установите `DEBUG = False`
- Настройте `ALLOWED_HOSTS`
- Используйте HTTPS

---

## Поддержка

Для вопросов и поддержки обращайтесь к документации:
- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- JWT: https://django-rest-framework-simplejwt.readthedocs.io/

---

## Лицензия

Proprietary - Akfa Technique
