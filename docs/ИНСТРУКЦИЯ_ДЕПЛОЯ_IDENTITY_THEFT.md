# 🚀 ИНСТРУКЦИЯ: Деплой Identity Theft Protection на сервер

**Дата:** 10 декабря 2025  
**Статус:** ✅ Готово к деплою

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### ✅ Проверено локально:
- [x] ✅ Flake8: 0 ошибок
- [x] ✅ Все тесты пройдены
- [x] ✅ Файл регистрации создан
- [x] ✅ 11 функций описаны

---

## 🚀 БЫСТРЫЙ ДЕПЛОЙ

### Автоматический деплой (рекомендуется):

```bash
# 1. Настройте переменные окружения
export ALADDIN_SERVER=your-server.com
export ALADDIN_SERVER_USER=root

# 2. Запустите скрипт деплоя
./deploy_identity_theft_to_server.sh
```

Скрипт автоматически:
- ✅ Проверит файлы локально
- ✅ Создаст директории на сервере
- ✅ Скопирует все файлы
- ✅ Зарегистрирует в SFM
- ✅ Подсчитает общее количество функций

---

## 📝 РУЧНОЙ ДЕПЛОЙ (по шагам)

### Шаг 1: Копирование файлов на сервер

```bash
# Агент
scp security/ai_agents/russian_identity_theft_protection_agent.py \
    user@server:/opt/aladdin-backend/security/ai_agents/

# API Router
scp security/api/routers/identity_theft_protection_router.py \
    user@server:/opt/aladdin-backend/security/api/routers/

# Registry entry
scp security/ai_agents/function_registry_entry_identity_theft_protection.json \
    user@server:/tmp/

# Скрипт регистрации
scp register_identity_theft_in_sfm.py user@server:/tmp/
```

### Шаг 2: Регистрация в SFM

```bash
ssh user@server

cd /tmp
python3 register_identity_theft_in_sfm.py
```

Скрипт автоматически:
- ✅ Загрузит существующий registry
- ✅ Добавит новую запись
- ✅ Создаст backup
- ✅ Подсчитает общее количество функций

### Шаг 3: Интеграция в main.py

Добавьте в `main.py` на сервере:

```python
from security.api.routers.identity_theft_protection_router import router as identity_theft_router

app.include_router(
    identity_theft_router,
    prefix="/api/identity-theft",
    tags=["Identity Theft Protection"]
)
```

### Шаг 4: Перезапуск сервиса

```bash
# Через systemctl
systemctl restart aladdin-backend
systemctl status aladdin-backend

# Или через supervisorctl
supervisorctl restart aladdin-backend
```

---

## 📊 ПРОВЕРКА ДЕПЛОЯ

### 1. Проверка файлов на сервере:

```bash
ssh user@server

# Проверка агента
ls -lh /opt/aladdin-backend/security/ai_agents/russian_identity_theft_protection_agent.py

# Проверка router
ls -lh /opt/aladdin-backend/security/api/routers/identity_theft_protection_router.py

# Проверка registry
cat /opt/aladdin-backend/data/sfm/function_registry.json | python3 -m json.tool | grep -A 5 "russian_identity_theft_protection_agent"
```

### 2. Проверка регистрации в SFM:

```bash
ssh user@server

python3 << 'EOF'
import json
from pathlib import Path

registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")
with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

# Поиск агента
if isinstance(registry, list):
    agent = next((a for a in registry if a.get("name") == "russian_identity_theft_protection_agent"), None)
elif isinstance(registry, dict):
    if "agents" in registry:
        agent = next((a for a in registry["agents"] if a.get("name") == "russian_identity_theft_protection_agent"), None)
    else:
        agent = registry.get("russian_identity_theft_protection_agent")

if agent:
    print("✅ Агент зарегистрирован!")
    print(f"   Функций: {len(agent.get('functions', []))}")
    print(f"   API endpoints: {len(agent.get('api_endpoints', []))}")
else:
    print("❌ Агент НЕ найден в registry!")
EOF
```

### 3. Проверка API endpoints:

```bash
# Health check
curl http://your-server/api/identity-theft/health

# С авторизацией (требуется токен)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://your-server/api/identity-theft/status?user_id=test_user
```

---

## 📊 ПОДСЧЕТ ФУНКЦИЙ В SFM

После регистрации скрипт автоматически покажет:

```
📊 СТАТИСТИКА SFM (ВСЕ АГЕНТЫ):
================================================================================
Всего агентов: 2
Всего функций: 23
Детализация по агентам:
  • dark_web_monitoring_agent: 12 функций
  • russian_identity_theft_protection_agent: 11 функций
================================================================================
```

Или проверьте вручную:

```bash
ssh user@server

python3 << 'EOF'
import json
from pathlib import Path

registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")
with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

if isinstance(registry, list):
    agents = registry
elif isinstance(registry, dict):
    agents = registry.get("agents", list(registry.values()) if "agents" not in registry else [])
else:
    agents = []

total_functions = sum(len(a.get("functions", [])) for a in agents if isinstance(a, dict))

print(f"Всего функций в SFM: {total_functions}")
for agent in agents:
    if isinstance(agent, dict):
        print(f"  • {agent.get('name')}: {len(agent.get('functions', []))} функций")
EOF
```

---

## ✅ ЧЕКЛИСТ ДЕПЛОЯ

- [ ] Файлы скопированы на сервер
- [ ] Агент зарегистрирован в SFM
- [ ] Router интегрирован в main.py
- [ ] Сервис перезапущен
- [ ] API endpoints работают
- [ ] Проверена регистрация в SFM
- [ ] Подсчитано общее количество функций

---

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После успешного деплоя:

- ✅ **Файлы на сервере:** 2 файла (агент + router)
- ✅ **Зарегистрировано в SFM:** 1 агент с 11 функциями
- ✅ **Всего функций в SFM:** 23 функции
  - Dark Web Monitoring: 12 функций
  - Identity Theft Protection: 11 функций
- ✅ **API endpoints:** 11 endpoints доступны

---

## ❌ РЕШЕНИЕ ПРОБЛЕМ

### Проблема: "Registry не найден"

**Решение:** Создайте registry вручную:
```bash
ssh user@server
mkdir -p /opt/aladdin-backend/data/sfm
echo '{"agents": []}' > /opt/aladdin-backend/data/sfm/function_registry.json
```

### Проблема: "Permission denied"

**Решение:** Проверьте права доступа:
```bash
ssh user@server
chmod 755 /opt/aladdin-backend/data/sfm
chmod 644 /opt/aladdin-backend/data/sfm/function_registry.json
```

### Проблема: "Module not found"

**Решение:** Проверьте зависимости:
```bash
ssh user@server
cd /opt/aladdin-backend
python3 -c "from security.ai_agents.russian_identity_theft_protection_agent import RussianIdentityTheftProtectionAgent; print('✅ OK')"
```

---

**Дата создания:** 10 декабря 2025  
**Статус:** ✅ Готово к использованию
