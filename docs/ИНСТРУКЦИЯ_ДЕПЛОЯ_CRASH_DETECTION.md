# 🚗 ИНСТРУКЦИЯ: Деплой Crash Detection Agent на сервер

**Дата:** 12 декабря 2025  
**Статус:** ✅ Готово к деплою

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### ✅ Проверено локально:
- [x] ✅ Flake8: 0 ошибок
- [x] ✅ Все тесты созданы (35+ тестов)
- [x] ✅ Файл регистрации создан
- [x] ✅ 8 функций описаны
- [x] ✅ 8 API endpoints описаны
- [x] ✅ Оптимизация и калибровка завершены

---

## 🚀 БЫСТРЫЙ ДЕПЛОЙ

### Автоматический деплой (рекомендуется):

```bash
# 1. Настройте переменные окружения (опционально)
export ALADDIN_SERVER=149.154.65.180
export ALADDIN_SERVER_USER=root
export ALADDIN_SERVER_PASS=Sergio675

# 2. Запустите скрипт деплоя
./deploy_crash_detection_to_server.sh
```

Скрипт автоматически:
- ✅ Проверит файлы локально
- ✅ Проверит синтаксис Python
- ✅ Создаст директории на сервере
- ✅ Скопирует все файлы
- ✅ Зарегистрирует в SFM
- ✅ Интегрирует router в main.py
- ✅ Проверит импорты на сервере
- ✅ Подсчитает общее количество функций

---

## 📝 РУЧНОЙ ДЕПЛОЙ (по шагам)

### Шаг 1: Копирование файлов на сервер

```bash
# Агент
scp security/ai_agents/crash_detection_agent.py \
    root@149.154.65.180:/opt/aladdin-backend/security/ai_agents/

# API Router
scp security/api/routers/crash_detection_router.py \
    root@149.154.65.180:/opt/aladdin-backend/security/api/routers/

# Registry entry
scp security/ai_agents/function_registry_entry_crash_detection.json \
    root@149.154.65.180:/tmp/

# Скрипты
scp register_crash_detection_in_sfm.py root@149.154.65.180:/tmp/
scp add_crash_detection_to_main.py root@149.154.65.180:/tmp/
```

### Шаг 2: Регистрация в SFM

```bash
ssh root@149.154.65.180

cd /tmp
python3 register_crash_detection_in_sfm.py
```

Скрипт автоматически:
- ✅ Загрузит существующий registry
- ✅ Добавит новую запись
- ✅ Создаст backup
- ✅ Подсчитает общее количество функций

### Шаг 3: Интеграция в main.py

```bash
ssh root@149.154.65.180

cd /tmp
python3 add_crash_detection_to_main.py
```

Скрипт автоматически:
- ✅ Найдет main.py
- ✅ Добавит импорт router
- ✅ Добавит регистрацию router
- ✅ Создаст backup
- ✅ Проверит синтаксис

**Или вручную:**

Добавьте в `main.py` на сервере:

```python
# Импорт
from security.api.routers.crash_detection_router import router as crash_detection_router

# Регистрация (в блоке try/except)
try:
    app.include_router(crash_detection_router)
    print("✅ Crash Detection Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать Crash Detection Router: {e}")
```

### Шаг 4: Проверка импорта

```bash
ssh root@149.154.65.180

cd /opt/aladdin-backend

# Проверка агента
python3 -c "from security.ai_agents.crash_detection_agent import CrashDetectionAgent; print('✅ Агент импортирован')"

# Проверка router
python3 -c "from security.api.routers.crash_detection_router import router; print('✅ Router импортирован')"
```

### Шаг 5: Перезапуск сервиса (опционально)

```bash
ssh root@149.154.65.180

# Проверка статуса
systemctl status aladdin-backend

# Перезапуск (если нужно)
systemctl restart aladdin-backend

# Проверка логов
journalctl -u aladdin-backend -f
```

---

## ✅ ПРОВЕРКА РАБОТОСПОСОБНОСТИ

### 1. Health Check

```bash
curl http://localhost:8000/api/crash-detection/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "agent": "crash_detection_agent",
  "version": "1.0.0",
  "emergency_service": "112",
  "auto_call_enabled": true,
  "g_force_threshold": 3.0,
  "prefer_gps": true
}
```

### 2. Запуск мониторинга

```bash
curl -X POST http://localhost:8000/api/crash-detection/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123"}'
```

### 3. Отправка данных сенсоров

```bash
curl -X POST http://localhost:8000/api/crash-detection/data \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "accelerometer": {
      "x": 0.1,
      "y": 0.2,
      "z": 9.8,
      "timestamp": 1234567890.123
    },
    "speed": 60.0,
    "location": {
      "latitude": 55.7558,
      "longitude": 37.6173
    }
  }'
```

### 4. Получение статуса

```bash
curl "http://localhost:8000/api/crash-detection/status?user_id=test_user_123"
```

---

## 🔧 КОНФИГУРАЦИЯ

### Переменные окружения (опционально):

```bash
# На сервере в /opt/aladdin-backend/.env или через systemd
CRASH_G_FORCE_THRESHOLD=3.0
CRASH_SPEED_CHANGE_THRESHOLD=30.0
CRASH_EMERGENCY_NUMBER=112
CRASH_AUTO_CALL_ENABLED=true
CRASH_FALSE_POSITIVE_FILTER=true
CRASH_USE_GEOFENCE=true
CRASH_GEOFENCE_RADIUS=500
CRASH_PREFER_GPS=true
```

---

## 📊 СТАТИСТИКА SFM

После деплоя проверьте статистику:

```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
python3 -c "
import json
with open('data/sfm/function_registry.json', 'r') as f:
    registry = json.load(f)
agents = {k: v for k, v in registry.items() 
          if k not in ['functions', 'handlers', 'last_updated'] 
          and isinstance(v, dict) and 'functions' in v}
total_funcs = sum(len(agent.get('functions', [])) for agent in agents.values())
total_endpoints = sum(len(agent.get('api_endpoints', [])) for agent in agents.values())
print(f'Агентов: {len(agents)}')
print(f'Функций в агентах: {total_funcs}')
print(f'API endpoints: {total_endpoints}')
"
```

---

## ⚠️ КРИТИЧЕСКИ ВАЖНО: Типичные проблемы при деплое агентов

Этот раздел содержит **реальные проблемы**, которые возникали при деплое Crash Detection Agent и других агентов, и их решения. **Обязательно прочитайте перед деплоем нового агента!**

---

### 🔴 ПРОБЛЕМА 1: `ModuleNotFoundError` при импорте агента

**Симптомы:**
```python
ModuleNotFoundError: No module named 'cv2'
# или
ModuleNotFoundError: No module named 'torch'
```

**Причина:**
Файл `/opt/aladdin-backend/security/ai_agents/__init__.py` на сервере пытается импортировать **все агенты** при импорте пакета. Если какой-то агент требует зависимости (`cv2`, `torch` и т.д.), которых нет на сервере, **весь пакет не импортируется**, даже если ваш новый агент не использует эти зависимости.

**Решение:**

1. **Проверьте `__init__.py` на сервере:**
```bash
ssh root@149.154.65.180
cat /opt/aladdin-backend/security/ai_agents/__init__.py
```

2. **Убедитесь, что ВСЕ импорты обернуты в `try/except`:**
```python
# ✅ ПРАВИЛЬНО:
try:
    from .fake_documents_agent import FakeDocumentsAgent  # noqa: F401
except ImportError:
    pass  # cv2 не установлен, пропускаем

try:
    from .crash_detection_agent import CrashDetectionAgent  # noqa: F401
except ImportError:
    pass  # Зависимости не установлены

# ❌ НЕПРАВИЛЬНО:
from .fake_documents_agent import FakeDocumentsAgent  # Может упасть если cv2 нет!
from .crash_detection_agent import CrashDetectionAgent  # Может упасть если зависимости нет!
```

3. **Если нужно исправить, создайте скрипт:**
```python
#!/usr/bin/env python3
# fix_init_py.py
from pathlib import Path

init_file = Path('/opt/aladdin-backend/security/ai_agents/__init__.py')
# ... обернуть все импорты в try/except
```

4. **Запустите на сервере:**
```bash
scp fix_init_py.py root@149.154.65.180:/tmp/
ssh root@149.154.65.180 "python3 /tmp/fix_init_py.py"
```

---

### 🔴 ПРОБЛЕМА 2: `AttributeError: 'Agent' object has no attribute 'config'`

**Симптомы:**
```python
AttributeError: 'CrashDetectionAgent' object has no attribute 'config'
```

**Причина:**
В `__init__` агента используется `self.config.get(...)`, но `SecurityBase` может не инициализировать `self.config` если `config=None`.

**Решение:**

Используйте локальную переменную вместо `self.config`:
```python
# ✅ ПРАВИЛЬНО:
def __init__(self, config: Optional[Dict[str, Any]] = None):
    super().__init__(config)
    config_dict = config if config is not None else {}
    self.g_force_threshold = config_dict.get("g_force_threshold", 3.0)
    self.emergency_service_number = config_dict.get("emergency_service_number", "112")

# ❌ НЕПРАВИЛЬНО:
def __init__(self, config: Optional[Dict[str, Any]] = None):
    super().__init__(config)
    self.g_force_threshold = self.config.get("g_force_threshold", 3.0)  # Может упасть!
```

---

### 🔴 ПРОБЛЕМА 3: `TypeError: Can't instantiate abstract class`

**Симптомы:**
```python
TypeError: Can't instantiate abstract class CrashDetectionAgent without an implementation 
for abstract methods 'analyze_threats', 'collect_threats', 'send_alert'
```

**Причина:**
Если агент наследуется от `ThreatMonitoringInterface`, он **обязан** реализовать все абстрактные методы.

**Решение:**

Добавьте все требуемые методы в ваш агент:
```python
def collect_threats(self) -> List[Dict[str, Any]]:
    """Сбор угроз"""
    threats = []
    # Ваша реализация - собрать угрозы из истории
    for user_id, history in self.crash_history.items():
        for crash in history:
            if crash.severity in [CrashSeverity.HIGH, CrashSeverity.CRITICAL]:
                threats.append({
                    "event_id": crash.event_id,
                    "agent_name": "crash_detection_agent",
                    "threat_type": "crash",
                    "severity": crash.severity.value,
                    # ...
                })
    return threats

def analyze_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Анализ угроз"""
    analyzed = []
    for threat in threats:
        threat["recommendations"] = [
            "Проверьте состояние водителя",
            "Обратитесь за медицинской помощью при необходимости"
        ]
        analyzed.append(threat)
    return analyzed

def send_alert(self, alert: Dict[str, Any]) -> bool:
    """Отправка уведомления"""
    try:
        if self.event_bus:
            event = ThreatEvent(...)
            self.event_bus.publish(event)
            return True
    except Exception as e:
        self.logger.error(f"Ошибка при отправке уведомления: {e}")
        return False
```

**Проверьте примеры в других агентах:**
- `security/ai_agents/dark_web_monitoring_agent.py` (строки 877-976)
- `security/ai_agents/crash_detection_agent.py` (строки 701-781)

---

### 🔴 ПРОБЛЕМА 4: `FileNotFoundError: logs/threat_intelligence.log`

**Симптомы:**
```python
FileNotFoundError: [Errno 2] No such file or directory: '/opt/aladdin-backend/logs/threat_intelligence.log'
```

**Причина:**
Директория `logs/` не существует на сервере, но какой-то агент пытается создать файл лога.

**Решение:**

Создайте директорию на сервере:
```bash
ssh root@149.154.65.180
mkdir -p /opt/aladdin-backend/logs
chmod 755 /opt/aladdin-backend/logs
```

---

### 🔴 ПРОБЛЕМА 5: `Permission denied (publickey,password)` при SSH/SCP

**Симптомы:**
```
Permission denied (publickey,password).
lost connection
```

**Причина:**
Неправильные учетные данные или пользователь.

**Решение:**

1. **Используйте правильного пользователя:**
```bash
# ✅ ПРАВИЛЬНО:
ssh root@149.154.65.180
scp file.py root@149.154.65.180:/opt/aladdin-backend/

# ❌ НЕПРАВИЛЬНО:
ssh Sergio675@149.154.65.180  # Пользователь должен быть root!
```

2. **Пароль:** `Sergio675` (используется с пользователем `root`)

3. **Для автоматизации используйте `expect` скрипты:**
```bash
#!/usr/bin/expect
set password "Sergio675"
set server "root@149.154.65.180"

spawn scp file.py $server:/opt/aladdin-backend/
expect "password:"
send "$password\r"
expect eof
```

---

### 🔴 ПРОБЛЕМА 6: `Address already in use` при запуске uvicorn

**Симптомы:**
```
ERROR: [Errno 98] error while attempting to bind on address ('0.0.0.0', 8000): address already in use
```

**Причина:**
Старый процесс `uvicorn` все еще работает на порту 8000.

**Решение:**

Убейте старый процесс перед перезапуском:
```bash
ssh root@149.154.65.180
pkill -f 'uvicorn main:app'
systemctl restart aladdin-backend
```

---

### 🔴 ПРОБЛЕМА 7: `SyntaxError: expected 'except' or 'finally' block` в main.py

**Симптомы:**
```python
SyntaxError: expected 'except' or 'finally' block
```

**Причина:**
Скрипт `add_crash_detection_to_main.py` создал незакрытый `try` блок или вставил код в неправильное место.

**Решение:**

1. **Проверьте синтаксис main.py:**
```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
python3 -m py_compile main.py
```

2. **Восстановите из backup:**
```bash
cp main.py.backup_crash_detection_* main.py
```

3. **Вручную добавьте router правильно:**
```python
# Найти место после других router регистраций
# Убедиться что все try/except блоки закрыты
# Добавить новый router после существующих
```

---

### 🔴 ПРОБЛЕМА 8: Router не регистрируется

**Симптомы:**
- Endpoints не доступны
- Health check возвращает 404

**Решение:**

1. **Проверьте импорт в main.py:**
```bash
ssh root@149.154.65.180
grep "crash_detection_router" /opt/aladdin-backend/main.py
```

2. **Проверьте что файл router существует на сервере:**
```bash
ls -lh /opt/aladdin-backend/security/api/routers/crash_detection_router.py
```

3. **Проверьте логи на ошибки:**
```bash
journalctl -u aladdin-backend -n 50 | grep -i "crash\|error"
```

4. **Проверьте что router правильно зарегистрирован:**
```bash
grep "app.include_router(crash_detection_router)" /opt/aladdin-backend/main.py
```

---

### 🔴 ПРОБЛЕМА 9: Health check не работает

**Симптомы:**
- `curl http://localhost:8000/api/crash-detection/health` возвращает 404 или ошибку

**Решение:**

1. **Проверьте что сервис перезапущен:**
```bash
ssh root@149.154.65.180
systemctl restart aladdin-backend
systemctl status aladdin-backend
```

2. **Проверьте логи:**
```bash
journalctl -u aladdin-backend -n 50
```

Должно быть видно:
```
✅ Crash Detection Router зарегистрирован
```

3. **Проверьте что порт 8000 не занят другим процессом:**
```bash
netstat -tulpn | grep 8000
```

4. **Проверьте что FastAPI запущен:**
```bash
ps aux | grep uvicorn
```

---

### 🔴 ПРОБЛЕМА 10: Ошибка импорта агента на сервере

**Симптомы:**
```python
ModuleNotFoundError: No module named 'security'
# или
ImportError: cannot import name 'CrashDetectionAgent'
```

**Решение:**

1. **Проверьте что файл агента скопирован:**
```bash
ssh root@149.154.65.180
ls -lh /opt/aladdin-backend/security/ai_agents/crash_detection_agent.py
```

2. **Проверьте что SecurityBase доступен на сервере:**
```bash
python3 -c "from security.base import SecurityBase; print('✅ OK')"
```

3. **Проверьте зависимости:**
```bash
cd /opt/aladdin-backend
python3 -c "from security.ai_agents.crash_detection_agent import CrashDetectionAgent; print('✅ OK')"
```

4. **Проверьте `__init__.py` (см. ПРОБЛЕМА 1)**

---

## 🎓 ЧЕКЛИСТ ДЛЯ ДРУГИХ ML МОДЕЛЕЙ

Если вы деплоите **новый агент**, обязательно выполните:

### ✅ Перед деплоем:

1. **Проверка flake8:**
```bash
python3 -m flake8 security/ai_agents/your_agent.py security/api/routers/your_router.py --max-line-length=120 --ignore=E501,W503
```
Должно быть **0 ошибок**.

2. **Проверка синтаксиса:**
```bash
python3 -m py_compile security/ai_agents/your_agent.py
python3 -m py_compile security/api/routers/your_router.py
```

3. **Проверка импорта локально:**
```bash
cd /opt/aladdin-backend  # или локальная копия
source venv/bin/activate  # если используется venv
python3 -c "from security.ai_agents.your_agent import YourAgent; agent = YourAgent(); print('✅ OK')"
```

4. **Проверка `__init__.py` на сервере:**
```bash
ssh root@149.154.65.180 "cat /opt/aladdin-backend/security/ai_agents/__init__.py"
```
Убедитесь что все импорты обернуты в `try/except`.

5. **Проверка директории logs:**
```bash
ssh root@149.154.65.180 "ls -la /opt/aladdin-backend/logs"
```
Если нет - создайте: `mkdir -p /opt/aladdin-backend/logs`

6. **Проверка учетных данных:**
```bash
# Пользователь должен быть root, не Sergio675!
# Пароль: Sergio675
```

### ✅ После деплоя:

1. **Проверка импорта на сервере:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend && python3 -c 'from security.ai_agents.your_agent import YourAgent; agent = YourAgent(); print(\"✅ OK\")'"
```

2. **Проверка main.py:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend && python3 -m py_compile main.py"
```

3. **Проверка сервиса:**
```bash
ssh root@149.154.65.180 "systemctl status aladdin-backend"
```

4. **Проверка health endpoint:**
```bash
curl http://localhost:8000/api/your-agent/health
```

5. **Проверка SFM регистрации:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend && python3 -c \"
import json
with open('data/sfm/function_registry.json', 'r') as f:
    registry = json.load(f)
if 'your_agent_name' in registry:
    print('✅ Агент зарегистрирован')
else:
    print('❌ Агент НЕ найден в SFM')
\""
```

6. **Проверка логов:**
```bash
ssh root@149.154.65.180 "journalctl -u aladdin-backend -n 50 | grep -i 'your_agent\|error'"
```

---

## 📝 УЧЕТНЫЕ ДАННЫЕ СЕРВЕРА

**⚠️ ВАЖНО:** Используйте правильные учетные данные!

- **Сервер:** `149.154.65.180`
- **Пользователь:** `root` (не Sergio675!)
- **Пароль:** `Sergio675`
- **Путь к backend:** `/opt/aladdin-backend`
- **Путь к SFM registry:** `/opt/aladdin-backend/data/sfm/function_registry.json`
- **Путь к main.py:** `/opt/aladdin-backend/main.py` или `/opt/aladdin-backend/api/main.py`
- **Порт API:** `8000`
- **Health check:** `http://localhost:8000/api/your-agent/health`

---

## 📊 SFM СТАТИСТИКА

### Текущая статистика (после деплоя Crash Detection Agent):

```
Основные функции: 1074
Агентов: 5
Функций в агентах: 47
API endpoints в агентах: 40
ВСЕГО функций: 1121 ✅ (больше 1100!)
```

### Детализация по агентам:

1. **dark_web_monitoring_agent:** 12 функций, 5 endpoints
2. **russian_identity_theft_protection_agent:** 11 функций, 11 endpoints
3. **ai_categories_agent:** 8 функций, 8 endpoints
4. **crash_detection_agent:** 8 функций, 8 endpoints ✅
5. **Другие агенты...**

### Проверка статистики:

```bash
ssh root@149.154.65.180
cd /tmp
python3 check_sfm_stats_crash.py
```

Или вручную:
```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
python3 << 'PYEOF'
import json
with open('data/sfm/function_registry.json', 'r') as f:
    registry = json.load(f)
agents = {k: v for k, v in registry.items() 
          if k not in ['functions', 'handlers', 'last_updated'] 
          and isinstance(v, dict) and 'functions' in v}
total_funcs = sum(len(agent.get('functions', [])) for agent in agents.values())
total_endpoints = sum(len(agent.get('api_endpoints', [])) for agent in agents.values())
print(f'Агентов: {len(agents)}')
print(f'Функций в агентах: {total_funcs}')
print(f'API endpoints: {total_endpoints}')
PYEOF
```

---

## 📝 ПРИМЕЧАНИЯ

- ⚠️ **ВАЖНО:** Перед деплоем убедитесь что все тесты пройдены локально
- ⚠️ **ВАЖНО:** Создайте backup registry перед регистрацией
- ⚠️ **ВАЖНО:** Проверьте синтаксис main.py после интеграции
- ⚠️ **ВАЖНО:** Используйте пользователя `root`, не `Sergio675`!
- ✅ Скрипты автоматически создают backups
- ✅ Все операции безопасны и обратимы
- ✅ После деплоя проверьте что в SFM больше 1100 функций

---

## 📚 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ

- **Архитектура:** `docs/АРХИТЕКТУРА_CRASH_DETECTION_AGENT.md`
- **GPS ограничения:** `docs/ВАЖНО_CRASH_DETECTION_GPS_ОГРАНИЧЕНИЯ.md`
- **Скорость из акселерометра:** `docs/ОБЪЯСНЕНИЕ_СКОРОСТЬ_ИЗ_АКСЕЛЕРОМЕТРА.md`
- **Отчеты:** 
  - `docs/ОТЧЕТ_CRASH_DETECTION_ДЕНЬ_1_5.md`
  - `docs/ОТЧЕТ_CRASH_DETECTION_ДЕНЬ_6_9.md`
  - `docs/ОТЧЕТ_CRASH_DETECTION_ДЕНЬ_10_12.md`

---

---

## ✅ ПОДТВЕРЖДЕНИЕ ДЕПЛОЯ

**Дата деплоя:** 12 декабря 2025  
**Статус:** ✅ Успешно развернут

**SFM статистика после деплоя:**
- Всего функций: **1121** (больше 1100!) ✅
- Агентов: 5
- Crash Detection Agent: 8 функций, 8 endpoints

**Проверка:**
```bash
ssh root@149.154.65.180
cd /tmp
python3 check_sfm_stats_crash.py
```

---

**Последнее обновление:** 12 декабря 2025
