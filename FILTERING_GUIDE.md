# Фильтрация техники - Инструкция для Frontend

## Доступные фильтры

API `/api/v1/technique/items/` поддерживает следующие фильтры:

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `model` | string | Поиск по модели (частичное совпадение, без учета регистра) | `model=GBH` |
| `brand` | number | Фильтр по ID бренда | `brand=1` |
| `brand_name` | string | Поиск по названию бренда | `brand_name=Bosch` |
| `tag` | number | Фильтр по ID тега | `tag=2` |
| `tag_name` | string | Поиск по названию тега | `tag_name=Drill` |
| `responsible` | UUID | Фильтр по ID ответственного | `responsible=uuid-здесь` |
| `responsible_name` | string | Поиск по имени ответственного | `responsible_name=Админ` |

---

## Примеры использования

### 1. Фильтр по модели

```javascript
// Поиск всей техники с моделью содержащей "GBH"
const response = await fetch(
  'http://192.168.1.95:8000/api/v1/technique/items/?model=GBH',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

### 2. Фильтр по ID бренда

```javascript
// Получить всю технику бренда Bosch (ID=1)
const response = await fetch(
  'http://192.168.1.95:8000/api/v1/technique/items/?brand=1',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

### 3. Фильтр по названию бренда (поиск)

```javascript
// Поиск техники брендов содержащих "bos"
const response = await fetch(
  'http://192.168.1.95:8000/api/v1/technique/items/?brand_name=bos',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

### 4. Фильтр по ID тега

```javascript
// Получить технику с тегом "Drill" (ID=1)
const response = await fetch(
  'http://192.168.1.95:8000/api/v1/technique/items/?tag=1',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

### 5. Фильтр по ответственному

```javascript
// Техника ответственного с конкретным ID
const userId = '9d7e572e-8281-459f-ad17-d1affaa891c1';
const response = await fetch(
  `http://192.168.1.95:8000/api/v1/technique/items/?responsible=${userId}`,
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

### 6. Комбинированные фильтры

```javascript
// Дрели (tag=1) бренда Bosch (brand=1) с моделью содержащей "2-28"
const response = await fetch(
  'http://192.168.1.95:8000/api/v1/technique/items/?brand=1&tag=1&model=2-28',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

---

## React Hook для фильтрации

```jsx
import { useState, useEffect } from 'react';

function useEquipmentFilters() {
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    model: '',
    brand: '',
    tag: '',
    responsible: '',
    brand_name: '',
    tag_name: '',
    responsible_name: ''
  });

  useEffect(() => {
    const fetchEquipment = async () => {
      setLoading(true);
      
      // Создаем query параметры только для заполненных фильтров
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const token = localStorage.getItem('access_token');
      const url = `http://192.168.1.95:8000/api/v1/technique/items/?${params}`;
      
      try {
        const response = await fetch(url, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setEquipment(data.results);
      } catch (error) {
        console.error('Ошибка загрузки техники:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEquipment();
  }, [filters]);

  return { equipment, loading, filters, setFilters };
}

// Использование:
function EquipmentList() {
  const { equipment, loading, filters, setFilters } = useEquipmentFilters();

  return (
    <div>
      <input
        type="text"
        placeholder="Поиск по модели..."
        value={filters.model}
        onChange={(e) => setFilters({ ...filters, model: e.target.value })}
      />
      
      <select
        value={filters.brand}
        onChange={(e) => setFilters({ ...filters, brand: e.target.value })}
      >
        <option value="">Все бренды</option>
        <option value="1">Bosch</option>
        <option value="2">Makita</option>
      </select>

      {loading ? (
        <p>Загрузка...</p>
      ) : (
        equipment.map(item => (
          <div key={item.id}>
            {item.brand.name} {item.model}
          </div>
        ))
      )}
    </div>
  );
}
```

---

## Построение URL с фильтрами

### Простой способ (URLSearchParams)

```javascript
function buildFilterUrl(baseUrl, filters) {
  const params = new URLSearchParams();
  
  // Добавляем только непустые фильтры
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) {
      params.append(key, value);
    }
  });
  
  return `${baseUrl}?${params.toString()}`;
}

// Использование
const url = buildFilterUrl(
  'http://192.168.1.95:8000/api/v1/technique/items/',
  {
    model: 'GBH',
    brand: 1,
    tag: null,  // Пропустится
    brand_name: ''  // Пропустится
  }
);
// Результат: http://192.168.1.95:8000/api/v1/technique/items/?model=GBH&brand=1
```

---

## TypeScript интерфейсы

```typescript
interface EquipmentFilters {
  model?: string;
  brand?: number;
  brand_name?: string;
  tag?: number;
  tag_name?: string;
  responsible?: string;
  responsible_name?: string;
}

// Функция для получения отфильтрованной техники
async function getFilteredEquipment(
  filters: EquipmentFilters,
  token: string
): Promise<Equipment[]> {
  const params = new URLSearchParams();
  
  (Object.keys(filters) as Array<keyof typeof filters>).forEach(key => {
    const value = filters[key];
    if (value !== undefined && value !== '') {
      params.append(key, String(value));
    }
  });
  
  const response = await fetch(
    `http://192.168.1.95:8000/api/v1/technique/items/?${params}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  const data = await response.json();
  return data.results;
}
```

---

## Советы по использованию

### 1. Поиск vs Точный фильтр

- **Поиск** (`model`, `brand_name`, `tag_name`, `responsible_name`):
  - Частичное совпадение
  - Не чувствителен к регистру
  - Хорош для поисковой строки

- **Точный фильтр** (`brand`, `tag`, `responsible`):
  - Точное совпадение по ID
  - Быстрее работает
  - Хорош для dropdown/select

### 2. Производительность

Используйте ID фильтры когда возможно:
```javascript
// ❌ Медленнее
?brand_name=Bosch

// ✅ Быстрее
?brand=1
```

### 3. Очистка фильтров

```javascript
// Сбросить все фильтры
setFilters({
  model: '',
  brand: '',
  tag: '',
  responsible: '',
  brand_name: '',
  tag_name: '',
  responsible_name: ''
});
```

### 4. Debounce для поиска

```javascript
import { useDebounce } from 'use-debounce';

function EquipmentSearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch] = useDebounce(searchTerm, 500);

  useEffect(() => {
    // Поиск выполняется только после 500мс простоя
    fetchEquipment({ model: debouncedSearch });
  }, [debouncedSearch]);

  return (
    <input
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Поиск..."
    />
  );
}
```

---

## Тестирование в Swagger

1. Откройте: `http://192.168.1.95:8000/api/docs/`
2. Авторизуйтесь с токеном
3. Найдите endpoint `GET /api/v1/technique/items/`
4. Нажмите "Try it out"
5. Заполните нужные фильтры
6. Нажмите "Execute"

---

**Базовый URL:** `http://192.168.1.95:8000/api/v1/technique/items/`

**Документация:** `http://192.168.1.95:8000/api/docs/`
