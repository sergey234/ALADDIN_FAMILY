# 📋 ПОЛНЫЙ ПЛАН ЗАДАЧ BUILD 122 - SFM И MOCK ДАННЫЕ

**Дата:** 2026-03-16  
**Статус:** В процессе выполнения

---

## 🎯 ЦЕЛЬ
Исправить проблему с mock данными вместо реальных функций SFM, обеспечить работу реального SafeFunctionManager с 1000+ функциями.

---

## ✅ ВЫПОЛНЕНО

### 1. Исправления в `sfm_singleton.py`
- ✅ Добавлен опциональный импорт SafeFunctionManager (пробуем `app.security`, затем `security`)
- ✅ Исправлена инициализация реального SFM в `__init__`
- ✅ Исправлена обработка результата `execute_function` (Tuple[bool, Any, str])
- ✅ Добавлена функция `get_authentication_manager_profile` в core functions
- ✅ Изменена маркировка: `sfm_real` → только от реального SFM, `sfm_fallback` → от core functions

### 2. Исправления в `safe_function_manager.py`
- ✅ Сделан опциональный импорт `async_io_manager` (не падает без aiohttp)
- ✅ Добавлена проверка `ASYNC_IO_AVAILABLE` перед использованием

### 3. Исправления в `NetworkManager.swift`
- ✅ Добавлена обработка mock ответов (проверка `source: "sfm_mock"` перед декодированием)
- ✅ Не декодирует mock в UserProfile

### 4. Исправления в `UserProfileManager.swift`
- ✅ Не загружает профиль на онбординге (проверка `hasCompletedOnboarding`)

---

## ⏳ ОСТАЛОСЬ СДЕЛАТЬ

### ЭТАП 1: ДЕПЛОЙ НА СЕРВЕР

#### 1.1. Деплой `sfm_singleton.py`
**Файл:** `app/security/sfm_singleton.py`  
**Целевой путь:** `/opt/aladdin-backend/app/security/sfm_singleton.py`

**Команды:**
```bash
# Копирование файла
scp app/security/sfm_singleton.py root@149.154.65.180:/opt/aladdin-backend/app/security/sfm_singleton.py

# Проверка синтаксиса
ssh root@149.154.65.180 "cd /opt/aladdin-backend && python3 -m py_compile app/security/sfm_singleton.py"
```

#### 1.2. Деплой `safe_function_manager.py`
**Файл:** `app/security/safe_function_manager.py`  
**Целевой путь:** `/opt/aladdin-backend/app/security/safe_function_manager.py`

**Команды:**
```bash
# Копирование файла
scp app/security/safe_function_manager.py root@149.154.65.180:/opt/aladdin-backend/app/security/safe_function_manager.py

# Проверка синтаксиса
ssh root@149.154.65.180 "cd /opt/aladdin-backend && python3 -m py_compile app/security/safe_function_manager.py"
```

#### 1.3. Перезапуск сервиса
```bash
ssh root@149.154.65.180 "systemctl restart aladdin-backend"
```

---

### ЭТАП 2: ТЕСТИРОВАНИЕ

#### 2.1. Тест инициализации SFM
**Цель:** Проверить что реальный SFM инициализируется

**Команда:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend && python3 -c \"
import sys
sys.path.insert(0, '.')
from app.security.sfm_singleton import get_sfm
sfm = get_sfm()
print('SFM version:', sfm.version)
print('SFM _sfm:', sfm._sfm is not None)
print('Functions count:', len(sfm._sfm.functions) if sfm._sfm else 0)
\""
```

**Ожидаемый результат:**
- `SFM _sfm: True`
- `Functions count: 1000+`

#### 2.2. Тест функции `get_authentication_manager_profile`
**Цель:** Проверить что функция возвращает реальные данные

**Команда:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend && python3 -c \"
import sys
sys.path.insert(0, '.')
from app.security.sfm_singleton import get_sfm
sfm = get_sfm()
result = sfm.execute_function('get_authentication_manager_profile', {'user_id': 'test123'})
print('Result:', result)
print('Source:', result.get('source') if isinstance(result, dict) else 'N/A')
\""
```

**Ожидаемый результат:**
- `Source: sfm_real` или `Source: sfm_fallback`
- НЕ `Source: sfm_mock`

#### 2.3. Тест API endpoint `/api/user/profile`
**Цель:** Проверить что endpoint возвращает реальные данные

**Команда:**
```bash
curl -X GET https://aladdin-ai.ru/api/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  | jq '.source'
```

**Ожидаемый результат:**
- НЕ `"sfm_mock"`
- `"sfm_real"` или `"sfm_fallback"`

---

### ЭТАП 3: ПРОВЕРКА ЛОГОВ

#### 3.1. Проверка логов приложения
**Цель:** Убедиться что нет ошибок декодирования UserProfile

**Что проверить:**
- Нет ошибок `❌ NetworkManager: Decoding error for UserProfile`
- Нет mock ответов в логах
- Профиль не загружается на онбординге

---

## 📊 АНАЛИЗ AIOHTTP

### ✅ ПЛЮСЫ установки aiohttp:
1. **Ускорение I/O операций**
   - Асинхронное чтение/запись файлов
   - Параллельная обработка множественных операций
   - Оптимизация загрузки/сохранения 1000+ функций

2. **Лучшая производительность**
   - Меньше блокировок при работе с файлами
   - Эффективное использование ресурсов
   - Масштабируемость при росте нагрузки

3. **Оптимизация для продакшена**
   - Рекомендуется для высоконагруженных систем
   - Улучшает отзывчивость API

### ❌ МИНУСЫ установки aiohttp:
1. **Дополнительная зависимость**
   - Требует установки пакета
   - Увеличивает размер окружения

2. **Не обязателен**
   - SFM работает без него (синхронный I/O)
   - Fallback механизм уже реализован

### 🎯 ВЫВОД:
**aiohttp опционален, но рекомендуется для продакшена**

**Рекомендация:** Установить после деплоя для оптимизации производительности:
```bash
ssh root@149.154.65.180 "pip3 install aiohttp"
```

---

## 📝 ЧЕКЛИСТ ДЕПЛОЯ

- [ ] Деплой `sfm_singleton.py` на сервер
- [ ] Деплой `safe_function_manager.py` на сервер
- [ ] Проверка синтаксиса Python файлов
- [ ] Перезапуск сервиса `aladdin-backend`
- [ ] Тест инициализации SFM (1000+ функций)
- [ ] Тест функции `get_authentication_manager_profile`
- [ ] Тест API endpoint `/api/user/profile`
- [ ] Проверка логов (нет mock ответов)
- [ ] (Опционально) Установка aiohttp для оптимизации

---

## 🔍 КРИТЕРИИ УСПЕХА

1. ✅ Реальный SFM инициализируется (`self._sfm is not None`)
2. ✅ Доступно 1000+ функций (`len(sfm._sfm.functions) > 1000`)
3. ✅ `get_authentication_manager_profile` возвращает данные (не mock)
4. ✅ API endpoint `/api/user/profile` возвращает реальные данные
5. ✅ Нет ошибок декодирования в логах iOS приложения
6. ✅ Нет mock ответов в продакшене

---

## 📞 СЛЕДУЮЩИЕ ШАГИ

1. **Выполнить деплой** (ЭТАП 1)
2. **Протестировать** (ЭТАП 2)
3. **Проверить логи** (ЭТАП 3)
4. **Установить aiohttp** (опционально, для оптимизации)

---

**Статус:** Готово к деплою ✅
