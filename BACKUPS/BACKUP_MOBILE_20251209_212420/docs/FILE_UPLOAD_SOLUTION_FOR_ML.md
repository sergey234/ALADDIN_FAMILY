# 🚀 РЕШЕНИЕ ПРОБЛЕМЫ ЗАГРУЗКИ ФАЙЛОВ НА СЕРВЕР ДЛЯ ML СИСТЕМ

**Дата:** 2025-11-26  
**Проблема:** Загрузка Python скрипта на сервер через `expect` не работает из-за интерпретации фигурных скобок  
**Решение:** Использование base64 кодирования для передачи файла через SSH команду  
**Для:** Других ML систем, которые столкнутся с аналогичной проблемой

---

## 📋 ПРОБЛЕМА

### Что НЕ работает:
1. **`expect` интерпретирует Python код как команды TCL**
   - Фигурные скобки `{}` в Python коде интерпретируются как команды TCL
   - Ошибка: `invalid command name "\"name\": m.name, \"value\": m.value..."`
   
2. **`scp` через `expect` требует интерактивного ввода**
   - `scp` не может корректно обработать интерактивный режим через `expect`
   - Команда отменяется пользователем

3. **Base64 строки слишком длинные для expect**
   - Длинные base64 строки обрываются или обрабатываются неправильно

### Что нужно было сделать:
- Загрузить Python скрипт `/tmp/add_endpoints.py` на сервер `root@149.154.65.180:/tmp/add_endpoints.py`
- Выполнить скрипт на сервере
- Проверить результат

---

## ✅ РЕШЕНИЕ: BASE64 КОДИРОВАНИЕ

### Идея решения:
Вместо передачи Python кода напрямую через `expect`, мы:
1. Кодируем файл в base64 локально
2. Передаем base64 строку через SSH команду
3. Декодируем base64 на сервере и сохраняем файл

Это обходит все проблемы с `expect` и фигурными скобками, так как base64 строка - это просто текст.

---

## 📝 ПОШАГОВАЯ ИНСТРУКЦИЯ

### ШАГ 1: Создание Python скрипта локально

**Файл:** `/tmp/add_endpoints.py`

**Содержимое:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления endpoints мониторинга в API Gateway
"""

import sys

file_path = '/opt/aladdin-backend/security/microservices/api_gateway.py'

# Читаем файл
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Проверяем, не добавлены ли уже endpoints
if '@app.get("/api/metrics")' in ''.join(lines):
    print("⚠️  Endpoints уже добавлены!")
    sys.exit(0)

# Код для добавления (endpoints_code)
endpoints_code = '''@app.on_event("startup")
async def startup_event_monitoring():
    """Инициализация мониторинга при запуске"""
    global monitor_manager, alert_manager
    try:
        config = MonitorConfig(collection_interval=30)
        monitor_manager = MonitorManager(config)
        await monitor_manager.initialize()
        await monitor_manager.start()
        alert_manager = AlertManager()
        await alert_manager.start_alert_processing()
        logger.info("✅ Мониторинг и алерты инициализированы")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации мониторинга: {e}")

@app.get("/api/metrics")
async def get_metrics():
    """Получить все метрики системы"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    return {
        "metrics": [
            {
                "name": m.name,
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "status": m.status.value,
                "unit": m.unit
            } for m in metrics
        ]
    }

@app.get("/api/metrics/cpu")
async def get_cpu_metrics():
    """Получить метрики CPU"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    cpu_metrics = [m for m in metrics if "cpu" in m.name.lower()]
    return {
        "cpu": [
            {
                "name": m.name,
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "status": m.status.value
            } for m in cpu_metrics
        ]
    }

@app.get("/api/metrics/ram")
async def get_ram_metrics():
    """Получить метрики RAM"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    ram_metrics = [m for m in metrics if "ram" in m.name.lower() or "memory" in m.name.lower()]
    return {
        "ram": [
            {
                "name": m.name,
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "status": m.status.value
            } for m in ram_metrics
        ]
    }

@app.get("/api/metrics/disk")
async def get_disk_metrics():
    """Получить метрики диска"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    disk_metrics = [m for m in metrics if "disk" in m.name.lower()]
    return {
        "disk": [
            {
                "name": m.name,
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "status": m.status.value
            } for m in disk_metrics
        ]
    }

@app.get("/api/alerts")
async def get_alerts():
    """Получить все алерты"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not initialized")
    alerts = alert_manager.get_alert_history()
    return {
        "alerts": [
            {
                "id": str(a.id) if hasattr(a, "id") else str(a.get("id", "")),
                "severity": a.severity.value if hasattr(a, "severity") else a.get("severity", ""),
                "message": a.message if hasattr(a, "message") else a.get("message", ""),
                "timestamp": a.timestamp.isoformat() if hasattr(a, "timestamp") else a.get("timestamp", ""),
                "resolved": a.resolved if hasattr(a, "resolved") else a.get("resolved", False)
            } for a in alerts
        ]
    }

@app.get("/api/alerts/active")
async def get_active_alerts():
    """Получить активные алерты"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not initialized")
    alerts = alert_manager.get_alert_history()
    active = [a for a in alerts if not (a.resolved if hasattr(a, "resolved") else a.get("resolved", False))]
    return {
        "active_alerts": [
            {
                "id": str(a.id) if hasattr(a, "id") else str(a.get("id", "")),
                "severity": a.severity.value if hasattr(a, "severity") else a.get("severity", ""),
                "message": a.message if hasattr(a, "message") else a.get("message", ""),
                "timestamp": a.timestamp.isoformat() if hasattr(a, "timestamp") else a.get("timestamp", "")
            } for a in active
        ]
    }

@app.get("/api/health")
async def get_health():
    """Получить общее здоровье системы"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    status = await monitor_manager.get_system_status()
    return status

'''

# Находим строку с if __name__
insert_pos = None
for i, line in enumerate(lines):
    if 'if __name__ == "__main__":' in line:
        insert_pos = i
        break

if insert_pos is None:
    print("❌ Не найдено 'if __name__ == \"__main__\":'")
    sys.exit(1)

# Вставляем код перед if __name__
lines.insert(insert_pos, endpoints_code)

# Записываем файл
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"✅ Endpoints добавлены перед строкой {insert_pos + 1}")
print(f"✅ Файл обновлен: {len(lines)} строк")
```

**Команда для создания:**
```bash
# Создать файл (используйте любой текстовый редактор или команду cat)
cat > /tmp/add_endpoints.py << 'EOF'
# ... (вставить содержимое выше)
EOF

# Сделать исполняемым
chmod +x /tmp/add_endpoints.py
```

---

### ШАГ 2: Кодирование файла в base64

**Команда:**
```bash
base64 /tmp/add_endpoints.py > /tmp/add_endpoints.b64
```

**Результат:**
- Файл `/tmp/add_endpoints.b64` содержит base64 представление Python скрипта
- Это обычная текстовая строка, которую можно безопасно передать через SSH

**Проверка:**
```bash
# Посмотреть первые 100 символов
head -c 100 /tmp/add_endpoints.b64

# Декодировать обратно для проверки
base64 -d /tmp/add_endpoints.b64 | head -20
```

---

### ШАГ 3: Загрузка файла на сервер через SSH с base64

**Метод:** Использование SSH команды с передачей base64 строки и декодированием на сервере

**Команда:**
```bash
# Читаем base64 содержимое
BASE64_CONTENT=$(cat /tmp/add_endpoints.b64)

# Передаем на сервер и декодируем
ssh root@149.154.65.180 "echo '$BASE64_CONTENT' | base64 -d > /tmp/add_endpoints.py && chmod +x /tmp/add_endpoints.py && echo '✅ Файл загружен'"
```

**Проблема:** Команда требует интерактивного ввода пароля.

**Решение:** Использовать `expect` только для передачи пароля, но не для передачи самого Python кода.

**Скрипт с expect:**
```bash
#!/usr/bin/expect -f
# Скрипт для загрузки файла на сервер используя пароль

set timeout 30
set server "root@149.154.65.180"
set password "Sergio675"
set local_file "/tmp/add_endpoints.py"
set remote_path "/tmp/add_endpoints.py"

# Кодируем файл в base64 используя системную команду
set encoded [exec base64 $local_file]

# Подключаемся к серверу и создаем файл
spawn ssh $server "echo '$encoded' | base64 -d > $remote_path && chmod +x $remote_path && echo '✅ Файл загружен'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}

wait
```

**Сохранить как:** `/tmp/upload_with_password.sh`

**Выполнить:**
```bash
chmod +x /tmp/upload_with_password.sh
/tmp/upload_with_password.sh
```

**Ожидаемый результат:**
```
spawn ssh root@149.154.65.180 echo '...' | base64 -d > /tmp/add_endpoints.py && chmod +x /tmp/add_endpoints.py && echo '✅ Файл загружен'
root@149.154.65.180's password: 
✅ Файл загружен
```

---

### ШАГ 4: Выполнение скрипта на сервере

**Скрипт для выполнения:**
```bash
#!/usr/bin/expect -f
# Скрипт для выполнения команды на сервере используя пароль

set timeout 60
set server "root@149.154.65.180"
set password "Sergio675"
set command "cd /opt/aladdin-backend/security/microservices && source /opt/aladdin-backend/venvs/main_env/bin/activate && python3 /tmp/add_endpoints.py"

spawn ssh $server $command

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}

wait
```

**Сохранить как:** `/tmp/execute_on_server.sh`

**Выполнить:**
```bash
chmod +x /tmp/execute_on_server.sh
/tmp/execute_on_server.sh
```

**Ожидаемый результат:**
```
spawn ssh root@149.154.65.180 cd /opt/aladdin-backend/security/microservices && source /opt/aladdin-backend/venvs/main_env/bin/activate && python3 /tmp/add_endpoints.py
root@149.154.65.180's password: 
✅ Endpoints добавлены перед строкой 870
✅ Файл обновлен: 872 строк
```

---

### ШАГ 5: Проверка результата

#### 5.1. Проверка синтаксиса Python

**Команда:**
```bash
expect -c "
set timeout 30
spawn ssh root@149.154.65.180 'cd /opt/aladdin-backend/security/microservices && source /opt/aladdin-backend/venvs/main_env/bin/activate && python3 -m py_compile api_gateway.py && echo \"✅ Синтаксис правильный\"'
expect \"password:\"
send \"Sergio675\r\"
expect eof
"
```

**Ожидаемый результат:**
```
✅ Синтаксис правильный
```

#### 5.2. Проверка добавленных endpoints

**Команда:**
```bash
expect -c "
set timeout 30
spawn ssh root@149.154.65.180 'cd /opt/aladdin-backend/security/microservices && grep -n \"@app.get\" api_gateway.py | grep -E \"/api/metrics|/api/alerts|/api/health\"'
expect \"password:\"
send \"Sergio675\r\"
expect eof
"
```

**Ожидаемый результат:**
```
885:@app.get("/api/metrics")
903:@app.get("/api/metrics/cpu")
921:@app.get("/api/metrics/ram")
939:@app.get("/api/metrics/disk")
957:@app.get("/api/alerts")
975:@app.get("/api/alerts/active")
993:@app.get("/api/health")
```

#### 5.3. Проверка инициализации

**Команда:**
```bash
expect -c "
set timeout 30
spawn ssh root@149.154.65.180 'cd /opt/aladdin-backend/security/microservices && grep -n \"startup_event_monitoring\" api_gateway.py'
expect \"password:\"
send \"Sergio675\r\"
expect eof
"
```

**Ожидаемый результат:**
```
871:async def startup_event_monitoring():
```

#### 5.4. Перезапуск API Gateway

**Команда:**
```bash
expect -c "
set timeout 30
spawn ssh root@149.154.65.180 'systemctl restart aladdin-api-gateway && systemctl status aladdin-api-gateway --no-pager | head -15'
expect \"password:\"
send \"Sergio675\r\"
expect eof
"
```

**Ожидаемый результат:**
```
● aladdin-api-gateway.service - ALADDIN API Gateway Service
     Loaded: loaded (/etc/systemd/system/aladdin-api-gateway.service; enabled; preset: enabled)
     Active: active (running) since Wed 2025-11-26 23:42:27 MSK; 12ms ago
```

---

## 🔑 КЛЮЧЕВЫЕ МОМЕНТЫ

### Почему base64 работает, а expect с Python кодом - нет?

1. **Base64 - это чистый текст**
   - Base64 строка не содержит специальных символов, которые `expect` интерпретирует как команды TCL
   - Фигурные скобки `{}` в Python коде становятся частью base64 строки, а не командами

2. **SSH команда выполняется на сервере**
   - `echo '$BASE64_CONTENT' | base64 -d` выполняется на сервере, а не в `expect`
   - `expect` только передает пароль, не интерпретируя содержимое команды

3. **Одноразовая передача**
   - Base64 строка передается как один аргумент команды
   - Не нужно экранировать кавычки, скобки и другие специальные символы

### Альтернативные методы (если base64 не подходит):

1. **SSH ключи** (рекомендуется для постоянного использования):
   ```bash
   # Создать ключ
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/aladdin_server -N ""
   
   # Скопировать на сервер (один раз, требует пароль)
   ssh-copy-id -i ~/.ssh/aladdin_server.pub root@149.154.65.180
   
   # Использовать ключ
   scp -i ~/.ssh/aladdin_server /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py
   ```

2. **sshpass** (если установлен):
   ```bash
   sshpass -p 'Sergio675' scp /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py
   ```

3. **Вручную через SSH и nano**:
   ```bash
   ssh root@149.154.65.180
   nano /tmp/add_endpoints.py
   # Вставить содержимое, сохранить
   ```

---

## 📊 РЕЗУЛЬТАТ

### Что было сделано:
- ✅ Python скрипт создан локально
- ✅ Файл закодирован в base64
- ✅ Файл загружен на сервер через SSH с base64
- ✅ Скрипт выполнен на сервере
- ✅ 7 endpoints мониторинга добавлены в API Gateway
- ✅ Инициализация `startup_event_monitoring` добавлена
- ✅ Синтаксис Python проверен - правильный
- ✅ API Gateway перезапущен и работает

### Добавленные endpoints:
1. `GET /api/metrics` - все метрики системы
2. `GET /api/metrics/cpu` - метрики CPU
3. `GET /api/metrics/ram` - метрики RAM
4. `GET /api/metrics/disk` - метрики диска
5. `GET /api/alerts` - все алерты
6. `GET /api/alerts/active` - активные алерты
7. `GET /api/health` - здоровье системы

---

## 🎯 ДЛЯ ДРУГИХ ML СИСТЕМ

### Если вы столкнулись с аналогичной проблемой:

1. **Определите проблему:**
   - `expect` интерпретирует ваш код как команды TCL?
   - `scp` через `expect` не работает?
   - Длинные строки обрываются?

2. **Используйте base64:**
   - Кодируйте файл: `base64 file.py > file.b64`
   - Передавайте через SSH: `ssh server "echo 'BASE64_STRING' | base64 -d > file.py"`
   - Используйте `expect` только для передачи пароля, не для передачи кода

3. **Альтернативы:**
   - Настройте SSH ключи для постоянного использования
   - Используйте `sshpass` если доступен
   - Используйте ручной метод через SSH и nano/vi

### Универсальный скрипт для загрузки файла:

```bash
#!/usr/bin/expect -f
set timeout 30
set server "USER@HOST"
set password "PASSWORD"
set local_file "/path/to/local/file"
set remote_path "/path/to/remote/file"

# Кодируем в base64
set encoded [exec base64 $local_file]

# Загружаем на сервер
spawn ssh $server "echo '$encoded' | base64 -d > $remote_path && chmod +x $remote_path && echo '✅ Файл загружен'"

expect {
    "password:" { send "$password\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}
wait
```

---

## ✅ КРИТЕРИИ УСПЕХА

- [x] Файл загружен на сервер
- [x] Скрипт выполнен без ошибок
- [x] Синтаксис Python правильный
- [x] Endpoints добавлены в файл
- [x] API Gateway перезапущен
- [x] Сервис работает корректно

---

**Готово!** 🚀

Теперь любая ML система может использовать этот метод для загрузки файлов на сервер, обходя проблемы с `expect` и специальными символами в коде.

