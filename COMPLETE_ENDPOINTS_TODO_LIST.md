# 🎯 ПОЛНЫЙ TODO ЛИСТ ДЛЯ ВСЕХ 331 ENDPOINT'ОВ

**Дата:** 2026-02-11  
**Специалист:** iOS разработчик с 15-летним опытом  
**Цель:** Проверить, исправить и протестировать ВСЕ 331 endpoint для продакшна  
**Приоритет:** 🔥 КРИТИЧНО - от этого зависят миллионы семей!

---

## 📊 ОБЩАЯ СТАТИСТИКА

### **По документации:**
- **Всего специфицировано:** 221 endpoint (базовая спецификация)
- **На сервере должно быть:** 331 endpoint (150% от спецификации)
  - Старые: 183 endpoint'а
  - Новые роутеры: 52 endpoint'а
  - Синхронизация: 96 endpoint'ов
- **В iOS должно быть:** 210 методов

### **Текущее состояние:**
- **Подключено роутеров:** 35+
- **Видно в OpenAPI:** 115 endpoint'ов
- **Проблема:** Многие endpoint'ы не видны или не работают

---

## 🔥 КРИТИЧЕСКИЕ ENDPOINT'Ы (ИСПРАВИТЬ СЕЙЧАС)

### **1. POST /api/family/create** ❌ **КРИТИЧНО!**

**Проблема:** Функция `create_family()` существует в `security/family/family_registration.py`, но FastAPI endpoint не добавлен в роутер.

**Статус:** ❌ НЕ РАБОТАЕТ (404)

**TODO:**
- [ ] Найти файл `app/routers/family.py` или создать его
- [ ] Импортировать `create_family` из `security.family.family_registration`
- [ ] Создать Pydantic модели: `CreateFamilyRequest` и `CreateFamilyResponse`
- [ ] Добавить endpoint: `@router.post("/create")`
- [ ] Проверить подключение роутера в `main.py`
- [ ] Протестировать: `curl -X POST "http://149.154.65.180:8002/api/family/create" -H "Content-Type: application/json" -d '{"role": "parent", "age_group": "Adult (18-64)", "personal_letter": "V", "device_type": "iOS"}'`
- [ ] Проверить ответ (должен быть 200/201 с JSON)

**Файлы для изменения:**
- `app/routers/family.py` (создать или обновить)
- `main.py` (проверить подключение роутера)

---

### **2. POST /api/auth/login-by-recovery-code** ❌ **КРИТИЧНО!**

**Проблема:** Endpoint полностью отсутствует. Нужен для авторизации БЕЗ персональных данных.

**Статус:** ❌ НЕ СУЩЕСТВУЕТ (404)

**TODO:**
- [ ] Найти файл `app/routers/auth_router.py`
- [ ] Создать Pydantic модель: `RecoveryCodeLoginRequest` (family_id, recovery_code)
- [ ] Создать функцию `login_by_recovery_code()` с проверкой recovery code
- [ ] Добавить endpoint: `@router.post("/auth/login-by-recovery-code")`
- [ ] Реализовать проверку recovery code в БД
- [ ] Создать JWT токены (access_token, refresh_token)
- [ ] Вернуть `LoginResponse` с токенами
- [ ] Протестировать: `curl -X POST "http://149.154.65.180:8002/api/auth/login-by-recovery-code" -H "Content-Type: application/json" -d '{"family_id": "FAM_TEST", "recovery_code": "TEST"}'`
- [ ] Проверить ответ (должен быть 200 с access_token и refresh_token)

**Файлы для изменения:**
- `app/routers/auth_router.py` (добавить endpoint)
- Возможно, создать функцию проверки recovery code в БД

---

## 📋 ЭТАП 1: ДИАГНОСТИКА ВСЕХ ENDPOINT'ОВ

### **Задача 1.1: Создать полный список всех 331 endpoint'а**

**TODO:**
- [ ] Прочитать документацию `ALADDIN_COMPLETE_SYSTEM_ARCHITECTURE_AND_API_REFERENCE.md`
- [ ] Извлечь все 221 endpoint из спецификации
- [ ] Добавить 96 endpoint'ов синхронизации (уже реализованы)
- [ ] Добавить 14 endpoint'ов из новых роутеров (Notifications, AI Assistant, Components, System)
- [ ] Создать таблицу Excel/CSV со всеми endpoint'ами:
  - Номер
  - Метод (GET/POST/PUT/DELETE)
  - Путь
  - Категория
  - Роутер
  - Статус (✅ работает / ❌ не работает / ⚠️ требует проверки)
  - Проблема (если есть)
  - Решение (если есть)

**Результат:** Файл `ALL_331_ENDPOINTS_LIST.csv` с полным списком

---

### **Задача 1.2: Проверить каждый endpoint на сервере**

**Для каждого endpoint'а проверить:**

**Чеклист диагностики:**
- [ ] **1. Функция существует?**
  - Команда: `grep -r "def function_name" /opt/aladdin-backend/`
  - Результат: ✅ Да / ❌ Нет
  
- [ ] **2. FastAPI endpoint добавлен?**
  - Команда: `grep -r "@router\.(get|post|put|delete).*endpoint_path" /opt/aladdin-backend/`
  - Результат: ✅ Да / ❌ Нет
  
- [ ] **3. Роутер подключен в main.py?**
  - Команда: `grep -r "include_router.*router_name" /opt/aladdin-backend/main.py`
  - Результат: ✅ Да / ❌ Нет
  
- [ ] **4. Виден в OpenAPI?**
  - Команда: `curl -s http://149.154.65.180:8002/openapi.json | jq '.paths | keys' | grep "endpoint_path"`
  - Результат: ✅ Да / ❌ Нет
  
- [ ] **5. Работает через HTTP?**
  - Команда: `curl -X METHOD "http://149.154.65.180:8002/endpoint_path" -H "Authorization: Bearer TOKEN"`
  - Результат: ✅ 200/201 / ❌ 404 / ⚠️ 401/403 / ❌ 500

**Результат:** Таблица `ENDPOINTS_DIAGNOSIS_REPORT.csv` с результатами диагностики

---

### **Задача 1.3: Создать таблицу статуса каждого endpoint'а**

**Формат таблицы:**

| № | Метод | Путь | Категория | Роутер | Функция есть? | Endpoint есть? | Роутер подключен? | Виден в OpenAPI? | HTTP работает? | Статус | Проблема | Решение |
|---|-------|------|-----------|--------|---------------|----------------|-------------------|------------------|-----------------|--------|----------|---------|
| 1 | POST | /api/family/create | Family | family.py | ✅ | ❌ | ✅ | ❌ | ❌ 404 | ❌ | Нет FastAPI endpoint | Добавить в роутер |
| 2 | POST | /api/auth/login-by-recovery-code | Auth | auth_router.py | ❌ | ❌ | ✅ | ❌ | ❌ 404 | ❌ | Endpoint отсутствует | Создать полностью |

**Результат:** Файл `ENDPOINTS_STATUS_TABLE.md` с полной таблицей

---

## 📋 ЭТАП 2: ИСПРАВЛЕНИЕ КРИТИЧЕСКИХ ENDPOINT'ОВ

### **Задача 2.1: Исправить POST /api/family/create**

**Шаги:**
1. [ ] Подключиться к серверу: `ssh root@149.154.65.180`
2. [ ] Перейти в директорию: `cd /opt/aladdin-backend`
3. [ ] Проверить существование файла: `ls -la app/routers/family.py`
4. [ ] Если файл не существует, создать его:
   ```python
   from fastapi import APIRouter, Depends, HTTPException
   from sqlalchemy.orm import Session
   from app.database.database import get_db
   from security.family.family_registration import create_family
   from pydantic import BaseModel
   
   router = APIRouter(prefix="/api/family", tags=["family"])
   
   class CreateFamilyRequest(BaseModel):
       role: str
       age_group: str
       personal_letter: str
       device_type: str
   
   class CreateFamilyResponse(BaseModel):
       success: bool
       family_id: str
       recovery_code: str
       members: list
       your_member_id: str
   
   @router.post("/create", response_model=CreateFamilyResponse)
   async def create_family_endpoint(
       request: CreateFamilyRequest,
       db: Session = Depends(get_db)
   ):
       try:
           result = create_family(
               role=request.role,
               age_group=request.age_group,
               personal_letter=request.personal_letter,
               device_type=request.device_type
           )
           return CreateFamilyResponse(**result)
       except Exception as e:
           raise HTTPException(status_code=500, detail=str(e))
   ```
5. [ ] Проверить синтаксис: `python3 -m py_compile app/routers/family.py`
6. [ ] Проверить подключение в `main.py`: `grep "family" main.py`
7. [ ] Если не подключен, добавить: `app.include_router(family.router)`
8. [ ] Перезапустить сервер: `systemctl restart aladdin-backend.service`
9. [ ] Проверить статус: `systemctl status aladdin-backend.service`
10. [ ] Протестировать endpoint (см. Задача 2.1 в PRODUCTION_ENDPOINTS_FIX_PLAN.md)

**Результат:** ✅ Endpoint работает (200/201)

---

### **Задача 2.2: Создать POST /api/auth/login-by-recovery-code**

**Шаги:**
1. [ ] Подключиться к серверу: `ssh root@149.154.65.180`
2. [ ] Перейти в директорию: `cd /opt/aladdin-backend`
3. [ ] Открыть файл: `nano app/routers/auth_router.py`
4. [ ] Добавить модели:
   ```python
   class RecoveryCodeLoginRequest(BaseModel):
       family_id: str
       recovery_code: str
   ```
5. [ ] Добавить функцию проверки recovery code (если нет):
   ```python
   def verify_recovery_code(db: Session, family_id: str, recovery_code: str) -> bool:
       # TODO: Реализовать проверку recovery code в БД
       # Проверить, что family_id существует
       # Проверить, что recovery_code совпадает
       return True  # Временно
   ```
6. [ ] Добавить endpoint:
   ```python
   @router.post("/auth/login-by-recovery-code", response_model=LoginResponse)
   async def login_by_recovery_code(
       request: RecoveryCodeLoginRequest,
       db: Session = Depends(get_db)
   ):
       # Проверить recovery code
       if not verify_recovery_code(db, request.family_id, request.recovery_code):
           raise HTTPException(status_code=401, detail="Invalid recovery code")
       
       # Создать токены
       token_data = {
           "family_id": request.family_id,
           "id": request.family_id
       }
       access_token = create_access_token(token_data, expires_delta=timedelta(hours=24))
       refresh_token = create_refresh_token(token_data)
       
       return LoginResponse(
           access_token=access_token,
           refresh_token=refresh_token,
           expires_in=86400,
           token_type="Bearer"
       )
   ```
7. [ ] Проверить синтаксис: `python3 -m py_compile app/routers/auth_router.py`
8. [ ] Перезапустить сервер: `systemctl restart aladdin-backend.service`
9. [ ] Протестировать endpoint (см. PRODUCTION_ENDPOINTS_FIX_PLAN.md)

**Результат:** ✅ Endpoint работает (200 с токенами)

---

## 📋 ЭТАП 3: ПРОВЕРКА ВСЕХ РОУТЕРОВ

### **Задача 3.1: Найти все роутеры на сервере**

**TODO:**
- [ ] Подключиться к серверу
- [ ] Найти все router файлы: `find /opt/aladdin-backend -name "*router*.py" -type f`
- [ ] Создать список всех роутеров с количеством endpoint'ов
- [ ] Проверить каждый роутер на наличие декораторов `@router.get/post/put/delete`

**Команды:**
```bash
# Найти все роутеры
find /opt/aladdin-backend -name "*router*.py" -type f

# Подсчитать endpoint'ы в каждом роутере
for file in $(find /opt/aladdin-backend -name "*router*.py"); do
    echo "=== $file ==="
    grep -c "@router\.\(get\|post\|put\|delete\)" "$file"
done
```

**Результат:** Файл `ALL_ROUTERS_LIST.md` со списком всех роутеров

---

### **Задача 3.2: Проверить подключение роутеров в main.py**

**TODO:**
- [ ] Открыть `main.py` на сервере
- [ ] Найти все `app.include_router()` вызовы
- [ ] Создать таблицу:
  - Имя роутера
  - Файл роутера
  - Подключен? (✅/❌)
  - Строка в main.py
  - Prefix
  - Количество endpoint'ов

**Команды:**
```bash
# Найти все подключения роутеров
grep -n "include_router" /opt/aladdin-backend/main.py

# Найти все импорты роутеров
grep -n "from.*router" /opt/aladdin-backend/main.py
```

**Результат:** Таблица `ROUTERS_CONNECTION_STATUS.md`

---

### **Задача 3.3: Найти дублирование роутеров**

**Проблема:** Некоторые роутеры подключены дважды (см. FINAL_CORRECTED_ENDPOINTS_ANALYSIS.md)

**TODO:**
- [ ] Проверить дублирование Components Router (старый + новый)
- [ ] Проверить дублирование Security роутеров (через security_routers + напрямую)
- [ ] Создать список дублирующихся роутеров
- [ ] Исправить дублирование (отключить старые версии)

**Результат:** Список исправленных дублирований

---

## 📋 ЭТАП 4: АВТОМАТИЗИРОВАННОЕ ТЕСТИРОВАНИЕ

### **Задача 4.1: Создать скрипт тестирования всех endpoint'ов**

**TODO:**
- [ ] Создать скрипт `test_all_331_endpoints.sh`
- [ ] Реализовать авторизацию через recovery code:
  1. Создать тестовую семью
  2. Получить recovery code
  3. Авторизоваться
  4. Получить токен
- [ ] Для каждого endpoint'а:
  - Отправить запрос с токеном
  - Проверить HTTP код
  - Проверить формат ответа (JSON)
  - Сохранить результат
- [ ] Создать отчет в формате JSON/CSV

**Структура скрипта:**
```bash
#!/bin/bash
BASE_URL="http://149.154.65.180:8002"
RESULTS_FILE="endpoints_test_results_$(date +%Y%m%d_%H%M%S).json"

# 1. Создать тестовую семью
FAMILY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/family/create" \
  -H "Content-Type: application/json" \
  -d '{"role": "parent", "age_group": "Adult (18-64)", "personal_letter": "V", "device_type": "iOS"}')

FAMILY_ID=$(echo "$FAMILY_RESPONSE" | jq -r '.family_id')
RECOVERY_CODE=$(echo "$FAMILY_RESPONSE" | jq -r '.recovery_code')

# 2. Получить токен
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login-by-recovery-code" \
  -H "Content-Type: application/json" \
  -d "{\"family_id\": \"$FAMILY_ID\", \"recovery_code\": \"$RECOVERY_CODE\"}" \
  | jq -r '.access_token')

# 3. Тестировать каждый endpoint
# ... (цикл по всем endpoint'ам)
```

**Результат:** Скрипт `test_all_331_endpoints.sh` + отчет `endpoints_test_results_*.json`

---

### **Задача 4.2: Создать чеклист для каждого endpoint'а**

**Для каждого endpoint'а проверить:**

**Чеклист тестирования:**
- [ ] **1. Реализация:**
  - [ ] Endpoint создан в роутере
  - [ ] HTTP метод правильный (GET/POST/PUT/DELETE)
  - [ ] Путь endpoint'а корректен
  - [ ] Параметры пути определены
  - [ ] Query параметры обработаны

- [ ] **2. Валидация:**
  - [ ] Валидация входных параметров
  - [ ] Валидация типов данных
  - [ ] Валидация обязательных полей
  - [ ] Валидация диапазонов значений
  - [ ] Валидация форматов (email, UUID, и т.д.)

- [ ] **3. Авторизация:**
  - [ ] Проверка токена доступа
  - [ ] Проверка прав доступа (только свой userId или родитель)
  - [ ] Обработка неавторизованных запросов (401)
  - [ ] Обработка недостаточных прав (403)

- [ ] **4. Бизнес-логика:**
  - [ ] Получение данных из БД
  - [ ] Обработка данных
  - [ ] Формирование ответа
  - [ ] Атомарность операций (для изменений)

- [ ] **5. Обработка ошибок:**
  - [ ] Обработка 404 (ресурс не найден)
  - [ ] Обработка 403 (недостаточно прав)
  - [ ] Обработка 500 (внутренняя ошибка)
  - [ ] Обработка сетевых ошибок
  - [ ] Обработка ошибок БД

- [ ] **6. Логирование:**
  - [ ] Логирование запросов
  - [ ] Логирование ошибок
  - [ ] Логирование критических операций
  - [ ] Логирование производительности

- [ ] **7. Тестирование:**
  - [ ] Unit тесты
  - [ ] Integration тесты
  - [ ] Тесты производительности
  - [ ] Тесты безопасности
  - [ ] Тесты обработки ошибок

**Результат:** Чеклист для каждого endpoint'а в таблице

---

## 📋 ЭТАП 5: СОЗДАНИЕ ОТЧЕТА

### **Задача 5.1: Создать детальный отчет по каждому endpoint'у**

**Формат отчета:**

```markdown
# ОТЧЕТ ПО ENDPOINT'У: POST /api/family/create

## Основная информация:
- **Метод:** POST
- **Путь:** /api/family/create
- **Категория:** Family
- **Роутер:** app/routers/family.py
- **Приоритет:** 🔥 КРИТИЧНО

## Статус:
- **Функция существует:** ✅ Да (security/family/family_registration.py)
- **FastAPI endpoint добавлен:** ❌ Нет
- **Роутер подключен:** ✅ Да (main.py, строка 348)
- **Виден в OpenAPI:** ❌ Нет
- **HTTP работает:** ❌ Нет (404)

## Проблема:
Функция `create_family()` существует, но FastAPI endpoint не добавлен в роутер.

## Решение:
1. Открыть app/routers/family.py
2. Импортировать create_family
3. Добавить Pydantic модели
4. Добавить @router.post("/create") endpoint
5. Протестировать

## Тестирование:
```bash
curl -X POST "http://149.154.65.180:8002/api/family/create" \
  -H "Content-Type: application/json" \
  -d '{"role": "parent", "age_group": "Adult (18-64)", "personal_letter": "V", "device_type": "iOS"}'
```

## Результат:
- **До исправления:** ❌ 404 Not Found
- **После исправления:** ✅ 200 OK (ожидается)
```

**Результат:** Файл `ENDPOINTS_DETAILED_REPORT.md` с отчетом по каждому endpoint'у

---

## 📊 ПРИОРИТЕТЫ

### **🔥 КРИТИЧНО (сделать СЕЙЧАС):**
1. POST /api/family/create
2. POST /api/auth/login-by-recovery-code

### **🟡 ВАЖНО (сделать сегодня):**
3. Все endpoint'ы для авторизации (12 endpoint'ов)
4. Все endpoint'ы для семьи (10+ endpoint'ов)
5. Все endpoint'ы для уведомлений (19 endpoint'ов)

### **🟢 ОПЦИОНАЛЬНО (можно позже):**
6. Остальные endpoint'ы (290+ endpoint'ов)

---

## 📈 МЕТРИКИ УСПЕХА

### **Критерии завершения:**
- ✅ Все критичные endpoint'ы работают (2/2)
- ✅ Все важные endpoint'ы работают (41/41)
- ✅ Все endpoint'ы протестированы (331/331)
- ✅ Нет 404 ошибок для критичных endpoint'ов
- ✅ Авторизация работает правильно
- ✅ Валидация работает правильно
- ✅ Обработка ошибок работает правильно
- ✅ Логирование работает правильно

### **Текущий прогресс:**
- **Диагностика:** 0% (0/331 endpoint'ов проверено)
- **Исправление:** 0% (0/2 критичных endpoint'ов исправлено)
- **Тестирование:** 0% (0/331 endpoint'ов протестировано)
- **Общий прогресс:** 0%

---

## 🚀 СЛЕДУЮЩИЕ ШАГИ

1. **СЕЙЧАС:** Исправить 2 критичных endpoint'а
2. **СЕГОДНЯ:** Проверить все endpoint'ы авторизации и семьи
3. **НА ЭТОЙ НЕДЕЛЕ:** Проверить все 331 endpoint
4. **ПЕРЕД ПРОДАКШНОМ:** Полное тестирование всех endpoint'ов

---

**Последнее обновление:** 2026-02-11  
**Статус:** 🚀 **ГОТОВ К РЕАЛИЗАЦИИ**
