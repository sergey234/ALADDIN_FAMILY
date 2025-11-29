# 🔍 ПРОБЛЕМА: ЗАГРУЗКА ФАЙЛОВ НА СЕРВЕР

**Дата:** 2025-11-26  
**Контекст:** Добавление endpoints мониторинга в API Gateway  
**Проблема:** Не удается загрузить Python скрипт на сервер для автоматического добавления кода

---

## 📋 ЧТО БЫЛО СДЕЛАНО РАНЕЕ (УСПЕШНО)

### ✅ Успешные примеры загрузки файлов:

1. **Загрузка через `scp` (работало):**
   ```bash
   scp /path/to/local/file.py root@149.154.65.180:/tmp/file.py
   ```

2. **Загрузка через `rsync` (работало):**
   ```bash
   rsync -avz /path/to/local/file.py root@149.154.65.180:/tmp/file.py
   ```

3. **Создание файла через `cat` с heredoc (работало):**
   ```bash
   ssh root@149.154.65.180 'cat > /tmp/file.py' < /path/to/local/file.py
   ```

4. **Выполнение Python кода напрямую через SSH (работало для простых команд):**
   ```bash
   ssh root@149.154.65.180 "python3 -c 'print(\"Hello\")'"
   ```

---

## ❌ ЧТО НЕ РАБОТАЕТ СЕЙЧАС

### Проблема 1: `expect` интерпретирует Python код как команды TCL

**Ошибка:**
```
invalid command name "\"name\": m.name, \"value\": m.value..."
```

**Причина:**
- `expect` использует TCL синтаксис
- Фигурные скобки `{}` в Python коде интерпретируются как команды TCL
- Кавычки и специальные символы экранируются неправильно

**Пример проблемного кода:**
```bash
expect <<'EOF'
spawn ssh root@server "python3 -c \"
return {\"name\": m.name, \"value\": m.value}
\""
EOF
```

### Проблема 2: `scp` через `expect` не работает

**Ошибка:**
```
Command was canceled by the user
```

**Причина:**
- `scp` требует интерактивного ввода пароля
- `expect` не может корректно обработать интерактивный режим `scp`
- Таймауты и прерывания

### Проблема 3: Base64 кодирование через `expect`

**Ошибка:**
```
invalid command name "IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwojIC0qLSBjb2Rpbmc6IHV0Zi04IC0qLQoiIiIK0KHQutGA0LjQv9GC..."
```

**Причина:**
- Base64 строка содержит символы, которые `expect` интерпретирует как команды
- Длинные строки обрываются или обрабатываются неправильно

---

## ✅ РЕШЕНИЕ: ПОДРОБНАЯ ИНСТРУКЦИЯ

### Вариант 1: Прямая загрузка через `scp` (БЕЗ expect)

**Шаг 1:** Создать файл локально
```bash
# Файл уже создан: /tmp/add_endpoints.py
# Содержимое: Python скрипт для добавления endpoints
```

**Шаг 2:** Загрузить на сервер БЕЗ expect
```bash
# Использовать sshpass или настроить SSH ключи
sshpass -p 'Sergio675' scp /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py

# ИЛИ использовать SSH ключи (если настроены)
scp /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py
```

**Шаг 3:** Выполнить скрипт на сервере
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && source /opt/aladdin-backend/venvs/main_env/bin/activate && python3 /tmp/add_endpoints.py"
```

---

### Вариант 2: Создание файла на сервере через heredoc (БЕЗ expect)

**Шаг 1:** Прочитать содержимое файла локально
```bash
cat /tmp/add_endpoints.py
```

**Шаг 2:** Создать файл на сервере через heredoc
```bash
ssh root@149.154.65.180 << 'HEREDOC_EOF'
cat > /tmp/add_endpoints.py << 'FILE_EOF'
#!/usr/bin/env python3
# ... (вставить содержимое файла)
FILE_EOF
chmod +x /tmp/add_endpoints.py
HEREDOC_EOF
```

**Проблема:** Нужен пароль для SSH, поэтому нужен `expect` или `sshpass`

---

### Вариант 3: Использовать `sshpass` вместо `expect`

**Установка sshpass (если нет):**
```bash
# macOS
brew install hudochenkov/sshpass/sshpass

# Linux
sudo apt-get install sshpass
```

**Загрузка файла:**
```bash
sshpass -p 'Sergio675' scp /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py
```

**Выполнение:**
```bash
sshpass -p 'Sergio675' ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && source /opt/aladdin-backend/venvs/main_env/bin/activate && python3 /tmp/add_endpoints.py"
```

---

### Вариант 4: Настроить SSH ключи (РЕКОМЕНДУЕТСЯ)

**Шаг 1:** Создать SSH ключ (если нет)
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/aladdin_server
```

**Шаг 2:** Скопировать ключ на сервер
```bash
ssh-copy-id -i ~/.ssh/aladdin_server.pub root@149.154.65.180
```

**Шаг 3:** Использовать ключ для подключения
```bash
scp -i ~/.ssh/aladdin_server /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py
```

---

### Вариант 5: Выполнить код напрямую через Python на сервере (БЕЗ файла)

**Проблема:** Код содержит фигурные скобки, которые `expect` интерпретирует неправильно.

**Решение:** Использовать Python для чтения кода из строки или использовать `base64` декодирование.

**Шаг 1:** Закодировать файл в base64 локально
```bash
base64 /tmp/add_endpoints.py > /tmp/add_endpoints.b64
```

**Шаг 2:** Передать base64 строку на сервер и декодировать
```bash
# Читаем base64 строку
BASE64_CONTENT=$(cat /tmp/add_endpoints.b64)

# Передаем на сервер и декодируем
ssh root@149.154.65.180 "echo '$BASE64_CONTENT' | base64 -d > /tmp/add_endpoints.py"
```

**Проблема:** Если используется `expect`, base64 строка может быть слишком длинной.

---

## 🎯 РЕКОМЕНДУЕМОЕ РЕШЕНИЕ ДЛЯ ДАННОЙ ЗАДАЧИ

### Пошаговая инструкция:

**1. Создать файл локально:**
```bash
# Файл уже создан: /tmp/add_endpoints.py
# Путь: /Users/sergejhlystov/ALADDIN_NEW/tmp/add_endpoints.py
```

**2. Загрузить на сервер используя `sshpass` или SSH ключи:**
```bash
# Вариант A: С sshpass
sshpass -p 'Sergio675' scp /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py

# Вариант B: С SSH ключами (если настроены)
scp /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py
```

**3. Выполнить скрипт на сервере:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && source /opt/aladdin-backend/venvs/main_env/bin/activate && python3 /tmp/add_endpoints.py"
```

**4. Проверить результат:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && python3 -m py_compile api_gateway.py && grep -n '@app.get.*/api/metrics' api_gateway.py"
```

---

## 📝 ЧТО ДОЛЖЕН СОДЕРЖАТЬ ФАЙЛ `/tmp/add_endpoints.py`

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

---

## 🔑 КЛЮЧЕВЫЕ МОМЕНТЫ

1. **Проблема:** `expect` интерпретирует Python код с фигурными скобками как команды TCL
2. **Решение:** Использовать `sshpass` или SSH ключи для загрузки файлов БЕЗ `expect`
3. **Альтернатива:** Добавить код вручную через SSH и `nano`/`vi`
4. **Рекомендация:** Настроить SSH ключи для автоматизации без паролей

---

## 📍 ТЕКУЩЕЕ СОСТОЯНИЕ

- ✅ Импорты добавлены
- ✅ Глобальные переменные добавлены
- ✅ Синтаксис правильный
- ❌ Endpoints еще не добавлены (нужно выполнить скрипт)

---

**Готово к выполнению!** 🚀

