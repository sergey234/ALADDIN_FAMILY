# 📝 ИНСТРУКЦИЯ: Регистрация Dark Web Monitoring Agent в SFM

**Дата:** 9 декабря 2025  
**Агент:** DarkWebMonitoringAgent

---

## 🎯 ЦЕЛЬ

Зарегистрировать `DarkWebMonitoringAgent` в Safe Function Manager (SFM) для автоматического управления и мониторинга.

---

## ✅ ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА

Перед регистрацией в SFM **ОБЯЗАТЕЛЬНО** выполнить:

1. ✅ Проверка flake8:
   ```bash
   python3 -m flake8 security/ai_agents/dark_web_monitoring_agent.py \
       --max-line-length=120 --ignore=E501,W503,E203,W293,W391
   python3 -m flake8 security/ai_agents/threat_monitoring_interface.py \
       --max-line-length=120 --ignore=E501,W503,E203,W293,W391
   ```

2. ✅ Проверка компиляции:
   ```bash
   python3 -m py_compile security/ai_agents/dark_web_monitoring_agent.py
   python3 -m py_compile security/ai_agents/threat_monitoring_interface.py
   ```

3. ✅ Проверка импортов:
   ```bash
   python3 -c "from security.ai_agents.dark_web_monitoring_agent import DarkWebMonitoringAgent"
   ```

**Только после успешного прохождения всех проверок можно регистрировать в SFM!**

---

## 📋 ШАГИ РЕГИСТРАЦИИ

### Шаг 1: Подготовка файла регистрации

Файл готов: `security/ai_agents/function_registry_entry_dark_web_monitoring.json`

### Шаг 2: Отправка файлов на сервер

```bash
# 1. Отправить агент на сервер
scp security/ai_agents/dark_web_monitoring_agent.py \
    root@149.154.65.180:/opt/aladdin-backend/security/ai_agents/

# 2. Отправить интерфейс (если его еще нет)
scp security/ai_agents/threat_monitoring_interface.py \
    root@149.154.65.180:/opt/aladdin-backend/security/ai_agents/

# 3. Отправить entry для регистрации
scp security/ai_agents/function_registry_entry_dark_web_monitoring.json \
    root@149.154.65.180:/tmp/
```

### Шаг 3: Подключение к серверу

```bash
ssh root@149.154.65.180
```

### Шаг 4: Регистрация в function_registry.json

```bash
cd /opt/aladdin-backend/data/sfm

# Создать backup
cp function_registry.json function_registry.json.backup_$(date +%Y%m%d_%H%M%S)

# Добавить entry в function_registry.json
# Способ 1: Через Python скрипт (рекомендуется)
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

# Добавить в registry (если это список) или в словарь
if isinstance(registry, list):
    registry.append(new_entry)
elif isinstance(registry, dict):
    if "agents" in registry:
        registry["agents"].append(new_entry)
    else:
        registry[new_entry["name"]] = new_entry

# Сохранить
with open(registry_path, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print("✅ Агент зарегистрирован в SFM!")
EOF

# Или способ 2: Вручную через nano/vim
# nano function_registry.json
# Добавить entry вручную
```

### Шаг 5: Проверка регистрации

```bash
# Проверить что entry добавлен
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
    agent = registry.get("dark_web_monitoring_agent")

if agent:
    print(f"✅ Агент найден: {agent['name']}")
    print(f"   Статус: {agent.get('status')}")
    print(f"   Путь: {agent.get('path')}")
else:
    print("❌ Агент не найден в registry!")
EOF
```

### Шаг 6: Перезапуск SFM (если нужно)

```bash
# Проверить статус SFM
systemctl status aladdin-sfm

# Если нужно перезапустить
systemctl restart aladdin-sfm

# Или через supervisor (если используется)
supervisorctl restart aladdin-sfm
```

---

## 🔧 КОНФИГУРАЦИЯ

### Обязательные настройки:

1. **API ключи** (в конфиге агента или переменных окружения):
   ```bash
   export HIBP_API_KEY="your-api-key-here"
   export BREACHDIRECTORY_API_KEY="your-api-key-here"  # опционально
   ```

2. **Путь к файлу** должен быть корректным:
   - Локально: `/opt/aladdin-backend/security/ai_agents/dark_web_monitoring_agent.py`
   - Проверить: `ls -la /opt/aladdin-backend/security/ai_agents/dark_web_monitoring_agent.py`

3. **Зависимости** должны быть установлены:
   - `threat_intelligence_agent` должен быть зарегистрирован
   - `threat_monitoring_interface` должен быть доступен

---

## 🧪 ПРОВЕРКА РАБОТЫ

После регистрации проверить:

```python
# Через Python на сервере
from security.ai_agents.dark_web_monitoring_agent import DarkWebMonitoringAgent

# Инициализация
config = {
    "hibp_api_key": "your-key",
    "cache_ttl": 86400
}
agent = DarkWebMonitoringAgent(config)

# Проверка методов
result = agent.check_email_breach("test@example.com")
print(f"Результат: {result}")
```

---

## 📊 СТРУКТУРА ENTRY

См. файл: `security/ai_agents/function_registry_entry_dark_web_monitoring.json`

**Основные поля:**
- `name`: уникальное имя агента
- `type`: тип (`ai_agent`)
- `path`: абсолютный путь к файлу
- `class`: имя класса
- `functions`: список всех методов агента
- `dependencies`: зависимости от других агентов
- `api_endpoints`: endpoints для API
- `monitoring`: настройки автоматического мониторинга

---

## ⚠️ ВАЖНО

1. ✅ **Всегда делайте backup** перед изменением `function_registry.json`
2. ✅ **Проверяйте JSON валидность** перед сохранением
3. ✅ **Убедитесь что путь к файлу правильный** на сервере
4. ✅ **Проверьте зависимости** - они должны быть зарегистрированы раньше
5. ✅ **Тестируйте после регистрации** - проверьте что агент работает

---

**Готово к регистрации на сервере!** 🚀
