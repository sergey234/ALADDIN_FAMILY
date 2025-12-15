# ✅ ЧЕКЛИСТ ДЕПЛОЯ: Dark Web Monitoring

**Дата:** 9 декабря 2025  
**Статус:** Готово к выполнению

---

## 📋 ПЕРЕД НАЧАЛОМ

### ✅ Проверки на локальной машине:

- [x] flake8 проверка пройдена (0 ошибок)
- [x] Компиляция успешна
- [x] Все файлы созданы
- [x] FastAPI роутер готов
- [x] Инструкции обновлены

---

## 🚀 ЭТАП 1: АВТОМАТИЧЕСКИЙ ДЕПЛОЙ

### Шаг 1.1: Запуск скрипта деплоя

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./deploy_dark_web_monitoring.sh
```

**Что делает скрипт:**
- ✅ Проверяет flake8
- ✅ Проверяет компиляцию
- ✅ Отправляет файлы на сервер:
  - `dark_web_monitoring_agent.py`
  - `threat_monitoring_interface.py`
  - `dark_web_monitoring_router.py`
  - `function_registry_entry_dark_web_monitoring.json`

**Ожидаемый результат:**
```
✅ flake8: OK
✅ Компиляция: OK
✅ Файлы отправлены
```

**Если ошибка SSH:** Проверьте подключение к серверу:
```bash
ssh root@149.154.65.180
```

---

## 🔧 ЭТАП 2: РЕГИСТРАЦИЯ В SFM

### Шаг 2.1: Подключение к серверу

```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
```

### Шаг 2.2: Найти function_registry.json

```bash
find . -name "function_registry.json" -type f
# Обычно: /opt/aladdin-backend/data/sfm/function_registry.json
```

### Шаг 2.3: Создать backup

```bash
cd /opt/aladdin-backend/data/sfm
cp function_registry.json function_registry.json.backup_$(date +%Y%m%d_%H%M%S)
```

### Шаг 2.4: Зарегистрировать агент

```bash
python3 << 'EOF'
import json
from pathlib import Path

# Загрузить существующий registry
registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")
with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

# Загрузить новую entry
entry_path = Path("/tmp/function_registry_entry_dark_web_monitoring.json")
with open(entry_path, 'r', encoding='utf-8') as f:
    new_entry = json.load(f)

# Добавить в registry
if isinstance(registry, list):
    existing = next((a for a in registry if a.get("name") == "dark_web_monitoring_agent"), None)
    if existing:
        print("⚠️  Агент уже зарегистрирован! Обновляю...")
        idx = registry.index(existing)
        registry[idx] = new_entry
    else:
        registry.append(new_entry)
elif isinstance(registry, dict):
    if "agents" in registry:
        existing = next((a for a in registry["agents"] if a.get("name") == "dark_web_monitoring_agent"), None)
        if existing:
            print("⚠️  Агент уже зарегистрирован! Обновляю...")
            idx = registry["agents"].index(existing)
            registry["agents"][idx] = new_entry
        else:
            registry["agents"].append(new_entry)
    else:
        registry[new_entry["name"]] = new_entry

# Сохранить
with open(registry_path, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print("✅ Агент зарегистрирован в SFM!")
EOF
```

### Шаг 2.5: Проверить регистрацию

```bash
python3 << 'EOF'
import json
from pathlib import Path

registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")
with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

if isinstance(registry, list):
    agent = next((a for a in registry if a.get("name") == "dark_web_monitoring_agent"), None)
elif isinstance(registry, dict):
    if "agents" in registry:
        agent = next((a for a in registry["agents"] if a.get("name") == "dark_web_monitoring_agent"), None)
    else:
        agent = registry.get("dark_web_monitoring_agent")

if agent:
    print(f"✅ Агент найден: {agent['name']}")
    print(f"   Статус: {agent.get('status')}")
    print(f"   Путь: {agent.get('path')}")
else:
    print("❌ Агент не найден!")
EOF
```

**Ожидаемый результат:**
```
✅ Агент найден: dark_web_monitoring_agent
   Статус: active
   Путь: /opt/aladdin-backend/security/ai_agents/dark_web_monitoring_agent.py
```

---

## 🔌 ЭТАП 3: ИНТЕГРАЦИЯ API ENDPOINTS

### Шаг 3.1: Найти main.py

```bash
find /opt/aladdin-backend -name "main.py" -type f | grep -v __pycache__
# Обычно: /opt/aladdin-backend/api/main.py
```

### Шаг 3.2: Создать backup

```bash
cp main.py main.py.backup_$(date +%Y%m%d_%H%M%S)
```

### Шаг 3.3: Добавить роутер

Открыть `main.py` и добавить:

**В начале файла с импортами:**
```python
from security.api.routers.dark_web_monitoring_router import router as dark_web_router
```

**После создания FastAPI app (в блоке регистрации роутеров):**
```python
# Регистрация Dark Web Monitoring Router
try:
    from security.api.routers.dark_web_monitoring_router import router as dark_web_router
    app.include_router(dark_web_router)
    logger.info("✅ Dark Web Monitoring Router зарегистрирован")
except Exception as e:
    logger.warning(f"⚠️ Не удалось зарегистрировать Dark Web Monitoring Router: {e}")
```

**Проверить что файл сохранен:**
```bash
grep -n "dark_web_router" main.py
```

---

## ⚙️ ЭТАП 4: НАСТРОЙКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ

### Шаг 4.1: Добавить API ключи

```bash
# Вариант 1: В .env файле
echo "HIBP_API_KEY=your-api-key-here" >> /opt/aladdin-backend/.env
echo "BREACHDIRECTORY_API_KEY=your-api-key-here" >> /opt/aladdin-backend/.env  # опционально

# Вариант 2: В systemd service
# Отредактировать /etc/systemd/system/aladdin-backend.service
# Добавить в [Service]:
# Environment="HIBP_API_KEY=your-key"
```

### Шаг 4.2: Проверить переменные

```bash
export HIBP_API_KEY="your-key"
python3 -c "import os; print('HIBP_API_KEY:', os.getenv('HIBP_API_KEY'))"
```

---

## 🔄 ЭТАП 5: ПЕРЕЗАПУСК СЕРВИСОВ

### Шаг 5.1: Проверить статус

```bash
systemctl status aladdin-backend
systemctl status aladdin-sfm
```

### Шаг 5.2: Перезапустить

```bash
# Backend
systemctl restart aladdin-backend

# SFM (если нужно)
systemctl restart aladdin-sfm

# Проверить статус после перезапуска
systemctl status aladdin-backend
```

### Шаг 5.3: Проверить логи

```bash
# Логи backend
journalctl -u aladdin-backend -n 50 --no-pager

# Поиск ошибок
journalctl -u aladdin-backend | grep -i error | tail -20

# Поиск успешной регистрации
journalctl -u aladdin-backend | grep -i "dark web"
```

**Ожидаемый результат в логах:**
```
✅ Dark Web Monitoring Router зарегистрирован
✅ DarkWebMonitoringAgent инициализирован
```

---

## 🧪 ЭТАП 6: ТЕСТИРОВАНИЕ

### Тест 1: Health Check

```bash
curl http://localhost:8000/api/darkweb/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "agent_loaded": true,
  "timestamp": "2025-12-09T..."
}
```

### Тест 2: Проверка email (требует токен)

```bash
curl -X POST http://localhost:8000/api/darkweb/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"email": "test@example.com"}'
```

### Тест 3: Через Python на сервере

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/aladdin-backend')

from security.ai_agents.dark_web_monitoring_agent import DarkWebMonitoringAgent

config = {
    "hibp_api_key": "your-key",
    "cache_ttl": 86400
}

agent = DarkWebMonitoringAgent(config)
result = agent.check_email_breach("test@example.com", include_russian=False)

print(f"✅ Агент работает!")
print(f"   Результат: {result['breaches_found']} утечек найдено")
EOF
```

---

## ✅ ФИНАЛЬНЫЙ ЧЕКЛИСТ

- [ ] Файлы отправлены на сервер
- [ ] Агент зарегистрирован в SFM
- [ ] Router добавлен в main.py
- [ ] API ключи настроены
- [ ] Сервисы перезапущены
- [ ] Health check работает
- [ ] Тестовый запрос проходит

---

## 🆘 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

### Проблема: SSH подключение не работает

**Решение:**
```bash
# Проверить подключение
ssh -v root@149.154.65.180

# Использовать ключ
ssh -i ~/.ssh/your_key root@149.154.65.180
```

### Проблема: Агент не загружается

**Решение:**
```bash
# Проверить путь к файлу
ls -la /opt/aladdin-backend/security/ai_agents/dark_web_monitoring_agent.py

# Проверить импорты
python3 -c "import sys; sys.path.insert(0, '/opt/aladdin-backend'); from security.ai_agents.dark_web_monitoring_agent import DarkWebMonitoringAgent"
```

### Проблема: Router не регистрируется

**Решение:**
```bash
# Проверить путь к router
ls -la /opt/aladdin-backend/security/api/routers/dark_web_monitoring_router.py

# Проверить импорты
python3 -c "import sys; sys.path.insert(0, '/opt/aladdin-backend'); from security.api.routers.dark_web_monitoring_router import router"

# Проверить логи
journalctl -u aladdin-backend | grep -i "dark web"
```

---

**🎉 УДАЧНОГО ДЕПЛОЯ!**
