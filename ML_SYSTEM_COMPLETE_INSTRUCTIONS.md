# 🤖 ПОЛНАЯ ИНСТРУКЦИЯ ДЛЯ ML СИСТЕМЫ: Исправление архитектуры роутеров

**Дата:** 10 февраля 2026 г.  
**Цель:** Загрузить и подключить роутеры для Notifications и AI Assistant  
**Приоритет:** 🔥 КРИТИЧЕСКИЙ

---

## 📊 ТЕКУЩИЙ СТАТУС

### **На какой задаче остановились:**
- ✅ **Задача 1 (`ai_server_endpoints`):** ВЫПОЛНЕНО - endpoints добавлены в api_gateway.py
- ✅ **Задача 19 (`notifications_server_implementation`):** ВЫПОЛНЕНО - endpoints добавлены в api_gateway.py
- ❌ **НО:** endpoints добавлены в неправильный файл (api_gateway.py не используется)
- ❌ **НО:** роутеры не подключены в main.py

### **Проблема:**
- Endpoints добавлены в `api_gateway.py` (не используется)
- Нужно добавить в роутеры и подключить в `main.py`

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ

### **ЗАДАЧА B1-B3: Исправление архитектуры роутеров**

#### **B1. Загрузить notifications_router_extended.py** (30 минут)
#### **B2. Загрузить ai_assistant_router.py** (15 минут)
#### **B3. Подключить роутеры в main.py** (15 минут)
#### **B4. Перезапустить сервер** (30 минут)
#### **B5. Протестировать endpoints** (30 минут)

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### **ШАГ 1: ПОДГОТОВКА ФАЙЛОВ**

#### **1.1. Проверить наличие файлов локально**

```bash
# Перейти в директорию проекта
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Проверить наличие файлов
ls -lh notifications_router_extended.py ai_assistant_router.py

# Должны быть:
# - notifications_router_extended.py (25K, ~500 строк)
# - ai_assistant_router.py (24K, ~400 строк)
```

**Если файлов нет:**
- Они уже созданы в этой сессии
- Проверьте текущую директорию

---

### **ШАГ 2: СОЗДАНИЕ РЕЗЕРВНЫХ КОПИЙ НА СЕРВЕРЕ**

#### **2.1. Подключиться к серверу и создать бэкапы**

```bash
# Использовать expect для автоматизации
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"📦 Создание резервных копий...\"

# Бэкап notifications_router.py
spawn ssh \$server \"cp /opt/aladdin-backend/security/api/routers/notifications_router.py /opt/aladdin-backend/security/api/routers/notifications_router.py.backup_\$(date +%Y%m%d_%H%M%S)\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

# Бэкап main.py
spawn ssh \$server \"cp /opt/aladdin-backend/main.py /opt/aladdin-backend/main.py.backup_\$(date +%Y%m%d_%H%M%S)\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Резервные копии созданы\"
"
```

**Ожидаемый результат:**
- ✅ Создан бэкап `notifications_router.py.backup_YYYYMMDD_HHMMSS`
- ✅ Создан бэкап `main.py.backup_YYYYMMDD_HHMMSS`

---

### **ШАГ 3: ЗАГРУЗКА ФАЙЛОВ НА СЕРВЕР**

#### **3.1. Загрузить notifications_router_extended.py**

```bash
# Использовать expect для SCP
expect -c "
set timeout 120
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"📤 Загрузка notifications_router_extended.py...\"

spawn scp notifications_router_extended.py \$server:/opt/aladdin-backend/security/api/routers/notifications_router.py
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    \"yes/no\" { send \"yes\\r\"; exp_continue }
    eof
}

puts \"✅ notifications_router_extended.py загружен\"
"
```

**Ожидаемый результат:**
- ✅ Файл загружен на сервер
- ✅ Заменил существующий `notifications_router.py`

#### **3.2. Загрузить ai_assistant_router.py**

```bash
# Использовать expect для SCP
expect -c "
set timeout 120
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"📤 Загрузка ai_assistant_router.py...\"

spawn scp ai_assistant_router.py \$server:/opt/aladdin-backend/security/api/routers/ai_assistant_router.py
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    \"yes/no\" { send \"yes\\r\"; exp_continue }
    eof
}

puts \"✅ ai_assistant_router.py загружен\"
"
```

**Ожидаемый результат:**
- ✅ Файл загружен на сервер
- ✅ Создан новый файл `ai_assistant_router.py`

#### **3.3. Проверить загрузку**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🔍 Проверка загруженных файлов...\"

spawn ssh \$server \"ls -lh /opt/aladdin-backend/security/api/routers/notifications_router.py /opt/aladdin-backend/security/api/routers/ai_assistant_router.py\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

spawn ssh \$server \"wc -l /opt/aladdin-backend/security/api/routers/notifications_router.py /opt/aladdin-backend/security/api/routers/ai_assistant_router.py\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Файлы проверены\"
"
```

**Ожидаемый результат:**
- ✅ `notifications_router.py`: ~500 строк
- ✅ `ai_assistant_router.py`: ~400 строк

---

### **ШАГ 4: ПОДКЛЮЧЕНИЕ РОУТЕРОВ В MAIN.PY**

#### **4.1. Прочитать текущий main.py**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"📖 Чтение main.py...\"

spawn ssh \$server \"cat /opt/aladdin-backend/main.py | head -50\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}
"
```

#### **4.2. Добавить импорты роутеров**

**Найти место для импортов (после других импортов роутеров):**

```python
# Найти строки типа:
from security.api.routers.location_bubble_router import router as location_router
from security.api.routers.identity_theft_protection_router import router as identity_router
from security.api.routers.driving_reports_router import router as driving_router

# Добавить ПОСЛЕ них:
from security.api.routers.notifications_router import router as notifications_router
from security.api.routers.ai_assistant_router import router as ai_assistant_router
```

**Команда для добавления импортов:**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"✏️  Добавление импортов в main.py...\"

# Скачать main.py локально
spawn scp \$server:/opt/aladdin-backend/main.py ./main.py.temp
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ main.py скачан для редактирования\"
"
```

**Затем отредактировать локально и загрузить обратно:**

```bash
# Найти строку с последним импортом роутера
# Добавить после неё:
# from security.api.routers.notifications_router import router as notifications_router
# from security.api.routers.ai_assistant_router import router as ai_assistant_router

# Загрузить обратно
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

spawn scp ./main.py.temp \$server:/opt/aladdin-backend/main.py
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}
"
```

#### **4.3. Добавить подключения роутеров**

**Найти место для подключений (после других `app.include_router()`):**

```python
# Найти строки типа:
app.include_router(location_router)
app.include_router(identity_router)
app.include_router(driving_router)
app.include_router(ai_categories_router)

# Добавить ПОСЛЕ них:
app.include_router(notifications_router)
app.include_router(ai_assistant_router)
```

**Команда для добавления подключений (через sed):**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"✏️  Добавление подключений роутеров в main.py...\"

# Добавить импорты (после последнего импорта роутера)
spawn ssh \$server \"sed -i '/from security.api.routers.driving_reports_router/a from security.api.routers.notifications_router import router as notifications_router\\nfrom security.api.routers.ai_assistant_router import router as ai_assistant_router' /opt/aladdin-backend/main.py\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

# Добавить подключения (после последнего include_router)
spawn ssh \$server \"sed -i '/app.include_router(ai_categories_router)/a app.include_router(notifications_router)\\napp.include_router(ai_assistant_router)' /opt/aladdin-backend/main.py\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Роутеры добавлены в main.py\"
"
```

#### **4.4. Проверить изменения**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🔍 Проверка изменений в main.py...\"

spawn ssh \$server \"grep -A2 'notifications_router\|ai_assistant_router' /opt/aladdin-backend/main.py | head -10\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Изменения проверены\"
"
```

**Ожидаемый результат:**
- ✅ Импорты добавлены
- ✅ Подключения добавлены

---

### **ШАГ 5: ПРОВЕРКА СИНТАКСИСА**

#### **5.1. Проверить синтаксис Python файлов**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🔍 Проверка синтаксиса Python файлов...\"

spawn ssh \$server \"cd /opt/aladdin-backend && python3 -m py_compile main.py && echo '✅ main.py: OK'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

spawn ssh \$server \"cd /opt/aladdin-backend && python3 -m py_compile security/api/routers/notifications_router.py && echo '✅ notifications_router.py: OK'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

spawn ssh \$server \"cd /opt/aladdin-backend && python3 -m py_compile security/api/routers/ai_assistant_router.py && echo '✅ ai_assistant_router.py: OK'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Синтаксис проверен\"
"
```

**Ожидаемый результат:**
- ✅ Все файлы компилируются без ошибок
- ✅ Нет синтаксических ошибок

**Если есть ошибки:**
- ❌ Исправить ошибки
- ❌ Повторить проверку

---

### **ШАГ 6: ПЕРЕЗАПУСК СЕРВЕРА**

#### **6.1. Остановить сервисы**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🛑 Остановка сервисов...\"

spawn ssh \$server \"systemctl stop aladdin-backend.service && echo '✅ aladdin-backend.service остановлен'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

spawn ssh \$server \"systemctl stop aladdin-production-api.service && echo '✅ aladdin-production-api.service остановлен'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

# Убить процессы если они еще работают
spawn ssh \$server \"pkill -f 'uvicorn.*main:app' && echo '✅ Процессы uvicorn остановлены' || echo '⚠️  Процессы уже остановлены'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Сервисы остановлены\"
"
```

#### **6.2. Запустить сервисы**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🚀 Запуск сервисов...\"

spawn ssh \$server \"systemctl start aladdin-backend.service && echo '✅ aladdin-backend.service запущен'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

spawn ssh \$server \"systemctl start aladdin-production-api.service && echo '✅ aladdin-production-api.service запущен'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

# Подождать 5 секунд
spawn ssh \$server \"sleep 5 && echo '✅ Ожидание завершено'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Сервисы запущены\"
"
```

#### **6.3. Проверить статус**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🔍 Проверка статуса сервисов...\"

spawn ssh \$server \"systemctl status aladdin-backend.service --no-pager -l | head -10\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

spawn ssh \$server \"ps aux | grep 'uvicorn.*main:app' | grep -v grep\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Статус проверен\"
"
```

**Ожидаемый результат:**
- ✅ Сервисы активны (active/running)
- ✅ Процессы uvicorn запущены
- ✅ Порты 8000 и 8002 слушают

---

### **ШАГ 7: ТЕСТИРОВАНИЕ ENDPOINTS**

#### **7.1. Проверить AI Assistant endpoints**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🧪 Тестирование AI Assistant endpoints...\"

# Тест 1: GET /api/ai/assistant/capabilities
spawn ssh \$server \"curl -s http://localhost:8000/api/ai/assistant/capabilities | head -20\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

# Тест 2: POST /api/ai/assistant/chat
spawn ssh \$server \"curl -s -X POST http://localhost:8000/api/ai/assistant/chat -H 'Content-Type: application/json' -d '{\\\"message\\\":\\\"test\\\",\\\"context\\\":\\\"general\\\"}' | head -20\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ AI Assistant endpoints протестированы\"
"
```

**Ожидаемый результат:**
- ✅ `GET /api/ai/assistant/capabilities` → 200 OK
- ✅ `POST /api/ai/assistant/chat` → 200 OK

#### **7.2. Проверить Notifications endpoints**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🧪 Тестирование Notifications endpoints...\"

# Тест 1: GET /api/notifications/list
spawn ssh \$server \"curl -s http://localhost:8000/api/notifications/list | head -20\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

# Тест 2: GET /api/notifications/stats
spawn ssh \$server \"curl -s http://localhost:8000/api/notifications/stats | head -20\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

# Тест 3: GET /api/notifications/unread_count
spawn ssh \$server \"curl -s http://localhost:8000/api/notifications/unread_count | head -20\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Notifications endpoints протестированы\"
"
```

**Ожидаемый результат:**
- ✅ `GET /api/notifications/list` → 200 OK (не 404!)
- ✅ `GET /api/notifications/stats` → 200 OK
- ✅ `GET /api/notifications/unread_count` → 200 OK

#### **7.3. Проверить все новые endpoints**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🧪 Тестирование всех новых endpoints...\"

# Список всех endpoints для проверки
set endpoints {
    \"/api/ai/assistant/capabilities\"
    \"/api/ai/assistant/history\"
    \"/api/ai/assistant/security_tips\"
    \"/api/notifications/list\"
    \"/api/notifications/stats\"
    \"/api/notifications/unread_count\"
    \"/api/notifications/categories\"
    \"/api/notifications/preferences\"
}

foreach endpoint \$endpoints {
    spawn ssh \$server \"curl -s -o /dev/null -w '%{http_code}' http://localhost:8000\$endpoint\"
    expect {
        \"password:\" { send \"\$password\\r\"; exp_continue }
        eof
    }
}

puts \"✅ Все endpoints протестированы\"
"
```

**Ожидаемый результат:**
- ✅ Все endpoints возвращают 200 или 422 (валидация), но НЕ 404

---

### **ШАГ 8: ПРОВЕРКА ЛОГОВ**

#### **8.1. Проверить логи на ошибки**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"📋 Проверка логов...\"

spawn ssh \$server \"tail -50 /opt/aladdin-backend/logs/api.log 2>/dev/null | grep -i 'error\\|exception\\|traceback' || echo '✅ Нет ошибок в логах'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

spawn ssh \$server \"journalctl -u aladdin-backend.service --no-pager -n 20 | grep -i 'error\\|failed' || echo '✅ Нет ошибок в systemd логах'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Логи проверены\"
"
```

**Ожидаемый результат:**
- ✅ Нет критических ошибок
- ✅ Сервер запустился успешно

---

## ✅ КРИТЕРИИ УСПЕХА

### **Проверка успешности выполнения:**

1. ✅ **Файлы загружены:**
   - `notifications_router.py`: ~500 строк
   - `ai_assistant_router.py`: ~400 строк

2. ✅ **Роутеры подключены:**
   - Импорты добавлены в main.py
   - `app.include_router()` добавлены в main.py

3. ✅ **Синтаксис корректен:**
   - Все файлы компилируются без ошибок

4. ✅ **Сервер запущен:**
   - Сервисы активны
   - Процессы работают
   - Порты слушают

5. ✅ **Endpoints работают:**
   - `GET /api/ai/assistant/capabilities` → 200 OK
   - `GET /api/notifications/list` → 200 OK (не 404!)
   - Все новые endpoints отвечают

---

## 🚨 ОБРАБОТКА ОШИБОК

### **Ошибка 1: Файл не загружается**

**Симптомы:**
- `scp: connection refused`
- `Permission denied`

**Решение:**
```bash
# Проверить подключение
ssh root@149.154.65.180 "echo 'test'"

# Проверить права доступа
ssh root@149.154.65.180 "ls -la /opt/aladdin-backend/security/api/routers/"
```

### **Ошибка 2: Синтаксическая ошибка**

**Симптомы:**
- `SyntaxError: invalid syntax`
- `IndentationError`

**Решение:**
```bash
# Проверить синтаксис локально
python3 -m py_compile notifications_router_extended.py
python3 -m py_compile ai_assistant_router.py

# Исправить ошибки
# Повторить загрузку
```

### **Ошибка 3: Роутер не подключается**

**Симптомы:**
- `ModuleNotFoundError: No module named 'security.api.routers.ai_assistant_router'`
- `ImportError`

**Решение:**
```bash
# Проверить что файл существует
ssh root@149.154.65.180 "ls -la /opt/aladdin-backend/security/api/routers/ai_assistant_router.py"

# Проверить синтаксис
ssh root@149.154.65.180 "python3 -m py_compile /opt/aladdin-backend/security/api/routers/ai_assistant_router.py"

# Проверить импорты в main.py
ssh root@149.154.65.180 "grep 'ai_assistant_router' /opt/aladdin-backend/main.py"
```

### **Ошибка 4: Endpoint возвращает 404**

**Симптомы:**
- `404 Not Found` для `/api/ai/assistant/capabilities`
- `404 Not Found` для `/api/notifications/list`

**Решение:**
```bash
# Проверить что роутер подключен
ssh root@149.154.65.180 "grep 'include_router.*notifications\|include_router.*ai_assistant' /opt/aladdin-backend/main.py"

# Проверить что сервер перезапущен
ssh root@149.154.65.180 "systemctl status aladdin-backend.service"

# Перезапустить сервер
ssh root@149.154.65.180 "systemctl restart aladdin-backend.service"
```

### **Ошибка 5: Сервер не запускается**

**Симптомы:**
- `Failed to start aladdin-backend.service`
- Процессы не запускаются

**Решение:**
```bash
# Проверить логи
ssh root@149.154.65.180 "journalctl -u aladdin-backend.service --no-pager -n 50"

# Проверить синтаксис
ssh root@149.154.65.180 "cd /opt/aladdin-backend && python3 -m py_compile main.py"

# Запустить вручную для отладки
ssh root@149.154.65.180 "cd /opt/aladdin-backend && python3 main.py"
```

---

## 📋 ЧЕКЛИСТ ВЫПОЛНЕНИЯ

### **Перед началом:**
- [ ] Файлы `notifications_router_extended.py` и `ai_assistant_router.py` существуют локально
- [ ] Есть доступ к серверу (SSH работает)
- [ ] Пароль известен: `Sergio675`

### **Шаг 1: Бэкапы**
- [ ] Создан бэкап `notifications_router.py`
- [ ] Создан бэкап `main.py`

### **Шаг 2: Загрузка файлов**
- [ ] `notifications_router_extended.py` загружен
- [ ] `ai_assistant_router.py` загружен
- [ ] Файлы проверены (размеры и строки)

### **Шаг 3: Подключение роутеров**
- [ ] Импорты добавлены в main.py
- [ ] `app.include_router()` добавлены в main.py
- [ ] Изменения проверены

### **Шаг 4: Проверка синтаксиса**
- [ ] `main.py` компилируется без ошибок
- [ ] `notifications_router.py` компилируется без ошибок
- [ ] `ai_assistant_router.py` компилируется без ошибок

### **Шаг 5: Перезапуск**
- [ ] Сервисы остановлены
- [ ] Сервисы запущены
- [ ] Статус проверен (active/running)

### **Шаг 6: Тестирование**
- [ ] AI Assistant endpoints работают (200 OK)
- [ ] Notifications endpoints работают (200 OK, не 404)
- [ ] Логи проверены (нет ошибок)

---

## 🎯 С КАКОГО ПУНКТА НАЧАТЬ

### **Если это первая попытка:**

1. **НАЧАТЬ С:** Шаг 1 (Подготовка файлов)
2. **ПРОДОЛЖИТЬ:** Шаг 2 (Бэкапы)
3. **ЗАТЕМ:** Шаг 3 (Загрузка файлов)
4. **ДАЛЕЕ:** Шаг 4 (Подключение роутеров)
5. **ЗАВЕРШИТЬ:** Шаг 5-6 (Перезапуск и тестирование)

### **Если файлы уже загружены:**

1. **НАЧАТЬ С:** Шаг 4 (Подключение роутеров)
2. **ПРОДОЛЖИТЬ:** Шаг 5 (Перезапуск)
3. **ЗАВЕРШИТЬ:** Шаг 6 (Тестирование)

### **Если роутеры уже подключены:**

1. **НАЧАТЬ С:** Шаг 5 (Перезапуск)
2. **ЗАВЕРШИТЬ:** Шаг 6 (Тестирование)

---

## 📊 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

### **После выполнения всех шагов:**

1. ✅ **notifications_router.py:** 18 endpoints (было 2)
2. ✅ **ai_assistant_router.py:** 8 endpoints (было 0)
3. ✅ **main.py:** +4 строки (2 импорта + 2 подключения)
4. ✅ **Все endpoints работают:** 200 OK (не 404)
5. ✅ **Сервер работает:** активен и отвечает

---

## 🔄 ОТКАТ ИЗМЕНЕНИЙ (если что-то пошло не так)

### **Восстановить из бэкапов:**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🔄 Откат изменений...\"

# Найти последний бэкап
spawn ssh \$server \"ls -t /opt/aladdin-backend/security/api/routers/notifications_router.py.backup_* | head -1\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

# Восстановить notifications_router.py
spawn ssh \$server \"cp \$(ls -t /opt/aladdin-backend/security/api/routers/notifications_router.py.backup_* | head -1) /opt/aladdin-backend/security/api/routers/notifications_router.py\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

# Восстановить main.py
spawn ssh \$server \"cp \$(ls -t /opt/aladdin-backend/main.py.backup_* | head -1) /opt/aladdin-backend/main.py\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

# Удалить ai_assistant_router.py
spawn ssh \$server \"rm -f /opt/aladdin-backend/security/api/routers/ai_assistant_router.py\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Откат выполнен\"
"
```

---

*Дата создания: 10 февраля 2026 г.*  
*Версия: 1.0*  
*Статус: ✅ Готово к выполнению*
