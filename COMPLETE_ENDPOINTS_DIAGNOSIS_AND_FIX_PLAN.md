# 🔍 ПОЛНАЯ ДИАГНОСТИКА И ПЛАН ИСПРАВЛЕНИЯ ENDPOINT'ОВ

**Дата:** 2026-02-11  
**Цель:** Разобраться почему некоторые endpoint'ы работают, а некоторые нет  
**Статус:** 🔥 КРИТИЧНО для продакшна

---

## 🎯 ТЕКУЩАЯ СИТУАЦИЯ

### **Что работает:**
- ✅ GET /api/health - работает
- ✅ POST /api/auth/login - работает (но нужны реальные учетные данные)
- ✅ GET /api/family/stats - работает (требует авторизацию)
- ✅ 115 endpoint'ов видны в OpenAPI

### **Что НЕ работает:**
- ❌ POST /api/family/create - 404 Not Found
- ❌ POST /api/auth/login-by-recovery-code - 404 Not Found

---

## 🔍 ЛОГИКА ПОДКЛЮЧЕНИЯ ENDPOINT'ОВ

### **Как работает FastAPI:**

1. **Роутер создается:**
   ```python
   router = APIRouter(prefix="/api/family", tags=["family"])
   ```

2. **Endpoint добавляется в роутер:**
   ```python
   @router.post("/create")
   async def create_family(...):
       ...
   ```

3. **Роутер подключается в main.py:**
   ```python
   app.include_router(family.router, tags=["family"])
   ```

4. **Результат:** Endpoint доступен по пути `/api/family/create`

---

## 🔍 ПРОБЛЕМА: ПОЧЕМУ НЕКОТОРЫЕ НЕ РАБОТАЮТ?

### **Причина 1: Endpoint не добавлен в роутер**

**Пример:**
- Функция `create_family()` существует в `security/family/family_registration.py`
- Но FastAPI endpoint `@router.post("/create")` НЕ добавлен в `app/routers/family.py`

**Решение:** Добавить endpoint в роутер

---

### **Причина 2: Роутер не подключен в main.py**

**Пример:**
- Роутер создан, endpoint'ы добавлены
- Но `app.include_router()` не вызван в main.py

**Решение:** Добавить подключение роутера в main.py

---

### **Причина 3: Неправильный путь**

**Пример:**
- Endpoint определен как `/create`
- Но роутер имеет prefix `/api/family`
- Итоговый путь: `/api/family/create` ✅
- Но запрос идет на `/family/create` ❌

**Решение:** Исправить путь в запросе

---

### **Причина 4: Требуется авторизация**

**Пример:**
- Endpoint работает
- Но без токена возвращает 404 вместо 401/403

**Решение:** Проверить авторизацию

---

## 📋 ПЛАН ДИАГНОСТИКИ КАЖДОГО ENDPOINT'А

### **ШАГ 1: Проверить существование функции**

```bash
# Проверить, есть ли функция в коде
grep -r "def create_family" /opt/aladdin-backend
```

### **ШАГ 2: Проверить FastAPI endpoint**

```bash
# Проверить, есть ли @router.post в роутере
grep -r "@router.post.*create" app/routers/family.py
```

### **ШАГ 3: Проверить подключение роутера**

```bash
# Проверить, подключен ли роутер в main.py
grep -r "include_router.*family" main.py
```

### **ШАГ 4: Проверить через OpenAPI**

```bash
# Проверить, виден ли endpoint в OpenAPI
curl http://localhost:8002/openapi.json | grep "family/create"
```

### **ШАГ 5: Протестировать endpoint**

```bash
# Протестировать endpoint напрямую
curl -X POST http://localhost:8002/api/family/create \
  -H "Content-Type: application/json" \
  -d '{"role": "parent"}'
```

---

## 🎯 ПЛАН ИСПРАВЛЕНИЯ

### **1. Endpoint `/api/family/create`**

**Проблема:** Функция есть, но FastAPI endpoint не добавлен

**Решение:**
1. Добавить endpoint в `app/routers/family.py`
2. Импортировать функцию `create_family` из `security/family/family_registration.py`
3. Создать модель запроса `CreateFamilyRequest`
4. Создать модель ответа `CreateFamilyResponse`
5. Добавить endpoint:
   ```python
   @router.post("/create", response_model=CreateFamilyResponse)
   async def create_family_endpoint(request: CreateFamilyRequest):
       result = create_family(
           role=request.role,
           age_group=request.age_group,
           personal_letter=request.personal_letter,
           device_type=request.device_type
       )
       return CreateFamilyResponse(**result)
   ```

---

### **2. Endpoint `/api/auth/login-by-recovery-code`**

**Проблема:** Endpoint полностью отсутствует

**Решение:**
1. Добавить endpoint в `app/routers/auth_router.py`
2. Создать модель запроса `RecoveryCodeLoginRequest`
3. Добавить функцию проверки recovery code
4. Добавить endpoint:
   ```python
   @router.post("/auth/login-by-recovery-code", response_model=LoginResponse)
   async def login_by_recovery_code(request: RecoveryCodeLoginRequest):
       # Проверить recovery code
       # Создать токены
       # Вернуть токены
   ```

---

## 📊 ТАБЛИЦА ДИАГНОСТИКИ ВСЕХ ENDPOINT'ОВ

| Endpoint | Функция существует? | FastAPI endpoint? | Роутер подключен? | OpenAPI виден? | Работает? | Проблема |
|----------|-------------------|-------------------|-------------------|----------------|-----------|----------|
| GET /api/health | ✅ | ✅ | ✅ | ✅ | ✅ | - |
| POST /api/auth/login | ✅ | ✅ | ✅ | ✅ | ✅ | - |
| POST /api/family/create | ✅ | ❌ | ⚠️ | ❌ | ❌ | Нет FastAPI endpoint |
| POST /api/auth/login-by-recovery-code | ❌ | ❌ | ❌ | ❌ | ❌ | Полностью отсутствует |
| GET /api/family/stats | ✅ | ✅ | ✅ | ✅ | ✅ | - |

---

## 🎯 ПЛАН ДЕЙСТВИЙ

### **ЭТАП 1: Диагностика (1-2 часа)**
1. Проверить все endpoint'ы из документации
2. Создать таблицу статуса каждого endpoint'а
3. Найти все неработающие endpoint'ы

### **ЭТАП 2: Исправление (2-4 часа)**
1. Добавить недостающие FastAPI endpoint'ы
2. Подключить роутеры в main.py
3. Исправить пути и авторизацию

### **ЭТАП 3: Тестирование (2-3 часа)**
1. Протестировать каждый endpoint отдельно
2. Проверить авторизацию
3. Проверить валидацию
4. Проверить обработку ошибок

### **ЭТАП 4: Документация (1 час)**
1. Обновить документацию
2. Создать отчет о статусе всех endpoint'ов

---

**Последнее обновление:** 2026-02-11  
**Статус:** 🔍 **ДИАГНОСТИКА В ПРОЦЕССЕ**
