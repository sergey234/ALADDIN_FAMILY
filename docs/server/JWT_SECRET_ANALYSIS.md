# 🔐 JWT-004: Анализ JWT_SECRET на сервере

**Дата:** 2026-03-16  
**Статус:** ❌ **ОБНАРУЖЕНО НЕСООТВЕТСТВИЕ СЕКРЕТОВ!**

---

## 📊 Результаты проверки

### 1. JWT_SECRET в переменных окружения
- **Статус:** ⚠️ НЕ УСТАНОВЛЕН
- **Значение:** Используется дефолт из кода

### 2. JWT_SECRET в файлах кода

#### app/auth/auth.py (используется для декодирования)
```python
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
```
- **Значение:** `"your-secret-key-change-in-production"` (36 символов)
- **Источник:** Дефолт, если не установлен env

#### backend/app/services/jwt_service.py (используется для создания токенов)
```python
SECRET_KEY = "aladdin-super-secret-key-change-in-production"
ALGORITHM = "HS256"
```
- **Значение:** `"aladdin-super-secret-key-change-in-production"` (47 символов)
- **Источник:** Хардкод в коде

---

## ❌ КРИТИЧЕСКАЯ ПРОБЛЕМА ОБНАРУЖЕНА!

### Несоответствие секретов:
- **Токены создаются** с `SECRET_KEY = "aladdin-super-secret-key-change-in-production"`
- **Токены декодируются** с `JWT_SECRET = "your-secret-key-change-in-production"`

### Последствия:
1. ✅ Токены создаются успешно (через jwt_service.py)
2. ❌ Токены НЕ декодируются (через auth.py) - **ОШИБКА 401!**
3. ❌ Это объясняет проблему: "Клиент: токен валиден, Сервер: 401"

---

## 🔧 РЕШЕНИЕ

### Вариант 1: Унифицировать секреты (РЕКОМЕНДУЕТСЯ)
Использовать один и тот же секрет везде:

```python
# app/auth/auth.py
JWT_SECRET = os.getenv("JWT_SECRET", "aladdin-super-secret-key-change-in-production")

# backend/app/services/jwt_service.py
SECRET_KEY = os.getenv("JWT_SECRET", "aladdin-super-secret-key-change-in-production")
```

### Вариант 2: Использовать переменную окружения
Установить `JWT_SECRET` в переменных окружения на сервере:
```bash
export JWT_SECRET="aladdin-super-secret-key-change-in-production"
```

---

## ✅ Рекомендации

1. **СРОЧНО:** Унифицировать секреты между файлами
2. **ВАЖНО:** Использовать переменные окружения вместо хардкода
3. **БЕЗОПАСНОСТЬ:** Использовать сильный случайный секрет в продакшене

---

## 📝 Следующие шаги

1. Исправить несоответствие секретов (jwt-011)
2. Проверить работу после исправления
3. Убедиться, что все токены декодируются правильно
