# 🚀 ИНСТРУКЦИЯ: Деплой AI Categories Agent на сервер

**Дата:** 11 декабря 2025  
**Статус:** ✅ Готово к деплою

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### ✅ Проверено локально:
- [x] ✅ Flake8: 0 ошибок
- [x] ✅ Все тесты созданы (35+ тестов)
- [x] ✅ Файл регистрации создан
- [x] ✅ 8 функций описаны
- [x] ✅ 8 API endpoints описаны

---

## 🚀 БЫСТРЫЙ ДЕПЛОЙ

### Автоматический деплой (рекомендуется):

```bash
# 1. Настройте переменные окружения
export ALADDIN_SERVER=149.154.65.180
export ALADDIN_SERVER_USER=root

# 2. Запустите скрипт деплоя
./deploy_ai_categories_to_server.sh
```

Скрипт автоматически:
- ✅ Проверит файлы локально
- ✅ Создаст директории на сервере
- ✅ Скопирует все файлы
- ✅ Зарегистрирует в SFM
- ✅ Интегрирует router в main.py
- ✅ Подсчитает общее количество функций
- ✅ Перезапустит сервис (опционально)

---

## 📝 РУЧНОЙ ДЕПЛОЙ (по шагам)

### Шаг 1: Копирование файлов на сервер

```bash
# Агент
scp security/ai_agents/ai_categories_agent.py \
    root@149.154.65.180:/opt/aladdin-backend/security/ai_agents/

# API Router
scp security/api/routers/ai_categories_router.py \
    root@149.154.65.180:/opt/aladdin-backend/security/api/routers/

# Registry entry
scp security/ai_agents/function_registry_entry_ai_categories.json \
    root@149.154.65.180:/tmp/

# Скрипты
scp register_ai_categories_in_sfm.py root@149.154.65.180:/tmp/
scp add_ai_categories_to_main.py root@149.154.65.180:/tmp/
```

### Шаг 2: Регистрация в SFM

```bash
ssh root@149.154.65.180

cd /tmp
python3 register_ai_categories_in_sfm.py
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
python3 add_ai_categories_to_main.py
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
# Импорт (в начале файла, после других импортов routers)
from security.api.routers.ai_categories_router import router as ai_categories_router

# Регистрация (после создания app)
try:
    app.include_router(ai_categories_router)
    print("✅ AI Categories Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать AI Categories Router: {e}")
```

### Шаг 4: Перезапуск сервиса

```bash
# Через systemctl
systemctl restart aladdin-backend
systemctl status aladdin-backend

# Или через supervisorctl
supervisorctl restart aladdin-backend
```

### Шаг 5: Проверка работы

```bash
# Health check
curl http://localhost:8000/api/ai-categories/health

# Должен вернуть:
# {
#   "status": "healthy",
#   "agent": "ai_categories_agent",
#   "version": "1.0.0",
#   "sites_count": 9,
#   "timestamp": "..."
# }

# Получить список сайтов
curl http://localhost:8000/api/ai-categories/sites
```

---

## ✅ ПРОВЕРКА ПОСЛЕ ДЕПЛОЯ

### 1. Проверка файлов на сервере

```bash
ssh root@149.154.65.180

# Проверка агента
ls -lh /opt/aladdin-backend/security/ai_agents/ai_categories_agent.py

# Проверка router
ls -lh /opt/aladdin-backend/security/api/routers/ai_categories_router.py

# Проверка registry
grep -A 5 "ai_categories_agent" /opt/aladdin-backend/data/sfm/function_registry.json
```

### 2. Проверка импорта в main.py

```bash
grep "ai_categories_router" /opt/aladdin-backend/api/main.py
# или
grep "ai_categories_router" /opt/aladdin-backend/main.py
```

### 3. Проверка логов

```bash
# Логи systemd
journalctl -u aladdin-backend -n 50 | grep -i "ai_categories"

# Должно быть видно:
# ✅ AI Categories Router зарегистрирован
```

### 4. Проверка API endpoints

```bash
# Health check
curl http://localhost:8000/api/ai-categories/health

# Список сайтов
curl http://localhost:8000/api/ai-categories/sites

# Статус (требует user_id)
curl "http://localhost:8000/api/ai-categories/status?user_id=test123"
```

---

## 📊 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После успешного деплоя:

1. **Файлы на сервере:**
   - ✅ `/opt/aladdin-backend/security/ai_agents/ai_categories_agent.py`
   - ✅ `/opt/aladdin-backend/security/api/routers/ai_categories_router.py`

2. **SFM Registry:**
   - ✅ Агент `ai_categories_agent` зарегистрирован
   - ✅ 8 функций в registry
   - ✅ Общее количество функций увеличилось на 8

3. **main.py:**
   - ✅ Импорт добавлен
   - ✅ Router зарегистрирован
   - ✅ Синтаксис корректен

4. **API:**
   - ✅ Health check работает
   - ✅ Все 8 endpoints доступны

---

## 🔧 УСТРАНЕНИЕ ПРОБЛЕМ

### ⚠️ КРИТИЧЕСКИ ВАЖНО: Типичные проблемы при деплое агентов

Этот раздел содержит **реальные проблемы**, которые возникали при деплое AI Categories Agent и их решения. **Обязательно прочитайте перед деплоем нового агента!**

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
    from .fake_news_detection_agent import FakeNewsDetectionAgent  # noqa: F401
except ImportError:
    pass  # Зависимости не установлены

# ❌ НЕПРАВИЛЬНО:
from .fake_documents_agent import FakeDocumentsAgent  # Может упасть если cv2 нет!
from .fake_news_detection_agent import FakeNewsDetectionAgent  # Может упасть если torch нет!
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
AttributeError: 'AICategoriesAgent' object has no attribute 'config'
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
    self.notify_parents = config_dict.get("notify_parents", True)

# ❌ НЕПРАВИЛЬНО:
def __init__(self, config: Optional[Dict[str, Any]] = None):
    super().__init__(config)
    self.notify_parents = self.config.get("notify_parents", True)  # Может упасть!
```

---

### 🔴 ПРОБЛЕМА 3: `TypeError: Can't instantiate abstract class`

**Симптомы:**
```python
TypeError: Can't instantiate abstract class AICategoriesAgent without an implementation 
for abstract methods 'analyze_threats', 'collect_threats', 'send_alert'
```

**Причина:**
Если агент наследуется от `ThreatMonitoringInterface`, он **обязан** реализовать все абстрактные методы.

**Решение:**

Добавьте все требуемые методы в ваш агент:
```python
def collect_threats(self) -> List[Dict[str, Any]]:
    """Сбор угроз"""
    # Ваша реализация
    return []

def analyze_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Анализ угроз"""
    # Ваша реализация
    return threats

def send_alert(self, alert: Dict[str, Any]) -> bool:
    """Отправка уведомления"""
    # Ваша реализация
    return True
```

**Проверьте примеры в других агентах:**
- `security/ai_agents/dark_web_monitoring_agent.py` (строки 877-976)
- `security/ai_agents/russian_identity_theft_protection_agent.py` (строки 1189-1218)

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
Скрипт `add_agent_to_main.py` создал незакрытый `try` блок или вставил код в неправильное место.

**Решение:**

1. **Проверьте синтаксис main.py:**
```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
python3 -m py_compile main.py
```

2. **Восстановите из backup:**
```bash
cp main.py.backup_ai_categories main.py
```

3. **Вручную добавьте router правильно:**
```python
# Найти место после других router регистраций
# Убедиться что все try/except блоки закрыты
# Добавить новый router после существующих
```

---

### ✅ ПРОБЛЕМА 8: Router не регистрируется

**Решение:**
1. Проверьте импорт в main.py
2. Проверьте что файл router существует на сервере
3. Проверьте логи на ошибки

---

### ✅ ПРОБЛЕМА 9: Health check не работает

**Решение:**
1. Проверьте что сервис перезапущен
2. Проверьте логи: `journalctl -u aladdin-backend -n 50`
3. Проверьте что порт 8000 не занят другим процессом

---

### ✅ ПРОБЛЕМА 10: Ошибка импорта агента

**Решение:**
1. Проверьте что файл агента скопирован
2. Проверьте что SecurityBase доступен на сервере
3. Проверьте зависимости

---

## 📝 ПРИМЕЧАНИЯ

- ⚠️ **ВАЖНО:** Перед деплоем убедитесь что все тесты пройдены локально
- ⚠️ **ВАЖНО:** Создайте backup registry перед регистрацией
- ⚠️ **ВАЖНО:** Проверьте синтаксис main.py после интеграции
- ✅ Скрипты автоматически создают backups
- ✅ Все операции безопасны и обратимы

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
source venv/bin/activate
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

### ✅ После деплоя:

1. **Проверка импорта на сервере:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend && source venv/bin/activate && python3 -c 'from security.ai_agents.your_agent import YourAgent; agent = YourAgent(); print(\"✅ OK\")'"
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
ssh root@149.154.65.180 "curl -s http://localhost:8000/api/your-agent/health | python3 -m json.tool"
```

5. **Проверка SFM статистики:**
```bash
ssh root@149.154.65.180 "python3 << 'PYEOF'
import json
from pathlib import Path
registry = json.load(open('/opt/aladdin-backend/data/sfm/function_registry.json'))
# Проверьте что ваш агент зарегистрирован
PYEOF
"
```

---

## 🔐 УЧЕТНЫЕ ДАННЫЕ СЕРВЕРА

**⚠️ ВАЖНО:** Эти данные используются для всех деплоев!

- **Сервер:** `149.154.65.180`
- **Пользователь:** `root` (НЕ Sergio675!)
- **Пароль:** `Sergio675`
- **Путь к backend:** `/opt/aladdin-backend`
- **Путь к venv:** `/opt/aladdin-backend/venv`
- **Путь к main.py:** `/opt/aladdin-backend/main.py`
- **Путь к SFM registry:** `/opt/aladdin-backend/data/sfm/function_registry.json`
- **Сервис:** `aladdin-backend` (systemctl)
- **Порт API:** `8000`

**Пример подключения:**
```bash
ssh root@149.154.65.180
# Пароль: Sergio675
```

---

## 📊 SFM СТАТИСТИКА

После деплоя AI Categories Agent:
- **Всего функций в SFM:** 1105
- **Основные функции:** 1074
- **Функции в агентах:** 31
  - `ai_categories_agent`: 8 функций
  - `dark_web_monitoring_agent`: 12 функций
  - `russian_identity_theft_protection_agent`: 11 функций

**Проверка статистики:**
```bash
ssh root@149.154.65.180 "python3 << 'PYEOF'
import json
registry = json.load(open('/opt/aladdin-backend/data/sfm/function_registry.json'))
main_funcs = len(registry.get('functions', []))
agents = {k: len(v.get('functions', [])) for k, v in registry.items() 
          if k not in ['functions', 'handlers', 'last_updated'] and isinstance(v, dict)}
print(f'Основные: {main_funcs}, Агенты: {sum(agents.values())}, Всего: {main_funcs + sum(agents.values())}')
PYEOF
"
```

---

**Удачи с деплоем! 🚀**
