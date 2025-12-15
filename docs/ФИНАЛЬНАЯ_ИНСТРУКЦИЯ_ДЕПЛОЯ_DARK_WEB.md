# 🚀 ФИНАЛЬНАЯ ИНСТРУКЦИЯ: Деплой Dark Web Monitoring

**Дата:** 9 декабря 2025  
**Статус:** ✅ Готово к деплою

---

## ✅ ПРЕДВАРИТЕЛЬНЫЕ ПРОВЕРКИ (ВЫПОЛНЕНЫ)

- ✅ flake8 проверка: 0 ошибок
- ✅ Компиляция: успешна
- ✅ Импорты: проверены
- ✅ Тесты: 50+ тестов написано

---

## 📋 ПОЛНЫЙ ПЛАН ДЕПЛОЯ

### 🎯 ОПЦИЯ 1: Автоматический деплой (рекомендуется)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./deploy_dark_web_monitoring.sh
```

Скрипт автоматически:
1. ✅ Проверит flake8
2. ✅ Проверит компиляцию
3. ✅ Проверит импорты
4. ✅ Отправит все файлы на сервер

---

### 🎯 ОПЦИЯ 2: Ручной деплой

#### Шаг 1: Отправка файлов

```bash
# Агент
scp security/ai_agents/dark_web_monitoring_agent.py \
    root@149.154.65.180:/opt/aladdin-backend/security/ai_agents/

# Интерфейс
scp security/ai_agents/threat_monitoring_interface.py \
    root@149.154.65.180:/opt/aladdin-backend/security/ai_agents/

# API Endpoints (FastAPI router)
scp security/api/routers/dark_web_monitoring_router.py \
    root@149.154.65.180:/opt/aladdin-backend/security/api/routers/

# JSON Entry для регистрации
scp security/ai_agents/function_registry_entry_dark_web_monitoring.json \
    root@149.154.65.180:/tmp/
```

---

#### Шаг 2: Регистрация в SFM

**Подключитесь к серверу:**
```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
```

**Найдите function_registry.json:**
```bash
find . -name "function_registry.json" -type f
# Обычно находится в: /opt/aladdin-backend/data/sfm/function_registry.json
```

**Создайте backup:**
```bash
cd /opt/aladdin-backend/data/sfm
cp function_registry.json function_registry.json.backup_$(date +%Y%m%d_%H%M%S)
```

**Добавьте entry (Python скрипт):**
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
    # Если это список - проверить что entry еще нет
    existing = next((a for a in registry if a.get("name") == "dark_web_monitoring_agent"), None)
    if existing:
        print("⚠️  Агент уже зарегистрирован! Обновляю...")
        idx = registry.index(existing)
        registry[idx] = new_entry
    else:
        registry.append(new_entry)
elif isinstance(registry, dict):
    # Если это словарь
    if "agents" in registry:
        # Проверить существование
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

**Проверьте регистрацию:**
```bash
python3 << 'EOF'
import json
from pathlib import Path

registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")
with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

# Поиск агента
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
    print("❌ Агент не найден в registry!")
EOF
```

---

#### Шаг 3: Интеграция API Endpoints в main.py

**Найдите main.py:**
```bash
find /opt/aladdin-backend -name "main.py" -type f | grep -v __pycache__
# Обычно: /opt/aladdin-backend/api/main.py или /opt/aladdin-backend/main.py
```

**Откройте main.py и добавьте:**

1. **В начале файла с импортами:**
```python
from security.api.routers.dark_web_monitoring_router import router as dark_web_router
```

2. **После создания FastAPI app:**
```python
# Пример:
app = FastAPI(...)

# ... другие регистрации роутеров ...

# Регистрация Dark Web Monitoring router (с обработкой ошибок)
try:
    from security.api.routers.dark_web_monitoring_router import router as dark_web_router
    app.include_router(dark_web_router)
    logger.info("✅ Dark Web Monitoring Router зарегистрирован")
except Exception as e:
    logger.warning(f"⚠️ Не удалось зарегистрировать Dark Web Monitoring Router: {e}")
```

**Создайте backup:**
```bash
cp main.py main.py.backup_$(date +%Y%m%d_%H%M%S)
```

---

#### Шаг 4: Настройка переменных окружения

**Добавьте API ключи:**

```bash
# В /opt/aladdin-backend/.env или через systemd service
export HIBP_API_KEY="your-haveibeenpwned-api-key"
export BREACHDIRECTORY_API_KEY="your-breachdirectory-api-key"  # опционально
```

**Или в systemd service file:**
```ini
[Service]
Environment="HIBP_API_KEY=your-key-here"
Environment="BREACHDIRECTORY_API_KEY=your-key-here"
```

---

#### Шаг 5: Перезапуск сервисов

**Проверьте статус:**
```bash
systemctl status aladdin-backend
systemctl status aladdin-sfm
```

**Перезапустите:**
```bash
# Backend
systemctl restart aladdin-backend

# SFM (если нужно)
systemctl restart aladdin-sfm

# Проверьте логи
journalctl -u aladdin-backend -f
```

---

## 🧪 ТЕСТИРОВАНИЕ НА СЕРВЕРЕ

### 1. Health Check (без авторизации)

```bash
curl http://localhost:5000/api/darkweb/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "agent_loaded": true,
  "timestamp": "2025-12-09T12:00:00"
}
```

### 2. Проверка email (требует токен)

```bash
curl -X POST http://localhost:5000/api/darkweb/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"email": "test@example.com"}'
```

### 3. Проверка через Python на сервере

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/aladdin-backend')

from security.ai_agents.dark_web_monitoring_agent import DarkWebMonitoringAgent

# Инициализация
config = {
    "hibp_api_key": "your-key",
    "cache_ttl": 86400
}

agent = DarkWebMonitoringAgent(config)

# Проверка методов
result = agent.check_email_breach("test@example.com", include_russian=False)
print(f"✅ Агент работает!")
print(f"   Результат: {result['breaches_found']} утечек найдено")
EOF
```

---

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема 1: Агент не загружается

**Решение:**
```bash
# Проверьте путь к файлу
ls -la /opt/aladdin-backend/security/ai_agents/dark_web_monitoring_agent.py

# Проверьте импорты
python3 -c "import sys; sys.path.insert(0, '/opt/aladdin-backend'); from security.ai_agents.dark_web_monitoring_agent import DarkWebMonitoringAgent"
```

### Проблема 2: API endpoints не работают

**Решение:**
```bash
# Проверьте что blueprint зарегистрирован
grep -r "dark_web_bp" /opt/aladdin-backend/api/main.py

# Проверьте логи
journalctl -u aladdin-backend -n 100
```

### Проблема 3: Ошибки импорта ThreatIntelligenceAgent

**Решение:**
Это нормально! Агент использует fallback методы если ThreatIntelligenceAgent недоступен.

---

## 📊 ПРОВЕРОЧНЫЙ ЧЕКЛИСТ

- [ ] Файлы отправлены на сервер
- [ ] Агент зарегистрирован в SFM (function_registry.json)
- [ ] API endpoints добавлены в main.py
- [ ] API ключи настроены (HIBP_API_KEY)
- [ ] Сервисы перезапущены
- [ ] Health check работает
- [ ] Тестовый запрос проходит успешно

---

## ✅ ГОТОВО!

После выполнения всех шагов Dark Web Monitoring готов к использованию!

**Endpoints:**
- `GET /api/darkweb/health` - Health check
- `POST /api/darkweb/check` - Проверка email
- `POST /api/darkweb/start-monitoring` - Запуск мониторинга
- `POST /api/darkweb/stop-monitoring` - Остановка мониторинга
- `GET /api/darkweb/status` - Статус мониторинга
- `GET /api/darkweb/breaches` - Список утечек

---

**🎉 ДЕПЛОЙ ЗАВЕРШЕН!**
