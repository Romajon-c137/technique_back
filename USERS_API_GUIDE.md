# API Пользователей - Инструкция

## 📋 Получение списка пользователей

### Endpoint
```
GET /api/v1/auth/users/
```

**ВАЖНО:** Этот endpoint **исключает** пользователей с ролью `admin`. Возвращает только `engineer` и `manager`.

---

## Авторизация
Требуется JWT токен в заголовке `Authorization`

---

## Примеры использования

### 1. Получить всех пользователей (без админов)

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://192.168.1.95:8000/api/v1/auth/users/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();
console.log(data.results); // Список пользователей
```

### 2. Поиск по имени или телефону

```javascript
// Поиск по имени "bilol"
const response = await fetch(
  'http://192.168.1.95:8000/api/v1/auth/users/?search=bilol',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);

// Поиск по номеру телефона
const response = await fetch(
  'http://192.168.1.95:8000/api/v1/auth/users/?search=996550',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

### 3. Фильтр по роли

```javascript
// Только инженеры
const response = await fetch(
  'http://192.168.1.95:8000/api/v1/auth/users/?role=engineer',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);

// Только менеджеры
const response = await fetch(
  'http://192.168.1.95:8000/api/v1/auth/users/?role=manager',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

### 4. Комбинация поиска и фильтра

```javascript
// Инженеры с именем содержащим "ivan"
const response = await fetch(
  'http://192.168.1.95:8000/api/v1/auth/users/?role=engineer&search=ivan',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

---

## Структура ответа

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid-здесь",
      "phone": "+996550998609",
      "full_name": "bilol",
      "avatar": "http://192.168.1.95:8000/media/avatars/photo.jpg",
      "role": "engineer",
      "birth_date": "2026-02-01",
      "last_login_at": "2026-02-09T13:47:50.725630Z"
    },
    {
      "id": "uuid-здесь-2",
      "phone": "+996700111111",
      "full_name": "Иван Инженеров",
      "avatar": null,
      "role": "manager",
      "birth_date": null,
      "last_login_at": "2026-02-10T00:15:30.123456Z"
    }
  ]
}
```

---

## React Hook для списка пользователей

```jsx
import { useState, useEffect } from 'react';

function useUsers(search = '', role = '') {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (role) params.append('role', role);
      
      const token = localStorage.getItem('access_token');
      const url = `http://192.168.1.95:8000/api/v1/auth/users/?${params}`;
      
      try {
        const response = await fetch(url, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setUsers(data.results);
      } catch (error) {
        console.error('Ошибка загрузки пользователей:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [search, role]);

  return { users, loading };
}

// Использование:
function UserSelector() {
  const [search, setSearch] = useState('');
  const [role, setRole] = useState('');
  const { users, loading } = useUsers(search, role);

  return (
    <div>
      <input
        type="text"
        placeholder="Поиск по имени или телефону..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      
      <select value={role} onChange={(e) => setRole(e.target.value)}>
        <option value="">Все роли</option>
        <option value="engineer">Инженеры</option>
        <option value="manager">Менеджеры</option>
      </select>

      {loading ? (
        <p>Загрузка...</p>
      ) : (
        <ul>
          {users.map(user => (
            <li key={user.id}>
              {user.full_name} ({user.phone}) - {user.role}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

## Получение конкретного пользователя

```javascript
const userId = 'uuid-здесь';
const response = await fetch(
  `http://192.168.1.95:8000/api/v1/auth/users/${userId}/`,
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);

const user = await response.json();
```

---

## Доступные параметры

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `search` | string | Поиск по ФИО или телефону | `?search=ivan` |
| `role` | string | Фильтр по роли (engineer, manager) | `?role=engineer` |

---

## TypeScript интерфейсы

```typescript
interface User {
  id: string;
  phone: string;
  full_name: string;
  avatar: string | null;
  role: 'engineer' | 'manager';
  birth_date: string | null;
  last_login_at: string;
}

async function getUsers(
  search?: string,
  role?: 'engineer' | 'manager'
): Promise<User[]> {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (role) params.append('role', role);
  
  const token = localStorage.getItem('access_token');
  const response = await fetch(
    `http://192.168.1.95:8000/api/v1/auth/users/?${params}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  const data = await response.json();
  return data.results;
}
```

---

## Важные замечания

1. **Админы исключены** - API автоматически исключает всех пользователей с `role='admin'`
2. **Read-only** - Endpoint только для чтения, изменять пользователей нельзя
3. **Поиск без регистра** - Поиск не чувствителен к регистру
4. **Частичное совпадение** - Поиск работает по частичному совпадению в любой части строки

---

**Базовый URL:** `http://192.168.1.95:8000/api/v1/auth/users/`

**Swagger:** `http://192.168.1.95:8000/api/docs/` → раздел "Users"
