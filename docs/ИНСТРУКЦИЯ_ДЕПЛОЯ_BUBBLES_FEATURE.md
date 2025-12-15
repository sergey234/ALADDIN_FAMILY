# 🚀 ИНСТРУКЦИЯ: Деплой Location Bubble Agent на сервер

**Дата:** 12 декабря 2025  
**Статус:** ✅ Готово к деплою

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### ✅ Проверено локально:
- [x] ✅ Flake8: 0 ошибок
- [x] ✅ Все тесты созданы (16 тестов)
- [x] ✅ Файл регистрации создан
- [x] ✅ 5 функций описаны
- [x] ✅ 6 API endpoints описаны

---

## 🚀 БЫСТРЫЙ ДЕПЛОЙ

### Вариант 1: Автоматический деплой (рекомендуется)

```bash
# 1. Запустите скрипт деплоя
./deploy_location_bubble_to_server.sh
```

Скрипт автоматически:
- ✅ Проверит файлы локально
- ✅ Скопирует все файлы на сервер
- ✅ Покажет инструкции для следующих шагов

### Вариант 2: Ручной деплой (по шагам)

---

## 📝 РУЧНОЙ ДЕПЛОЙ (по шагам)

### Шаг 1: Копирование файлов на сервер

```bash
# Агент
scp security/ai_agents/location_bubble_agent.py \
    root@149.154.65.180:/opt/aladdin-backend/security/ai_agents/

# API Router
scp security/api/routers/location_bubble_router.py \
    root@149.154.65.180:/opt/aladdin-backend/security/api/routers/

# Registry entry
scp security/ai_agents/function_registry_entry_location_bubble.json \
    root@149.154.65.180:/tmp/

# Скрипты
scp register_location_bubble_in_sfm.py root@149.154.65.180:/tmp/
scp add_location_bubble_to_main.py root@149.154.65.180:/tmp/
```

### Шаг 2: Подключение к серверу

```bash
ssh root@149.154.65.180
```

### Шаг 3: Регистрация в SFM

```bash
cd /tmp
python3 register_location_bubble_in_sfm.py
```

Скрипт автоматически:
- ✅ Загрузит существующий registry
- ✅ Добавит новую запись
- ✅ Создаст backup
- ✅ Подсчитает общее количество функций

**Ожидаемый вывод:**
```
=== РЕГИСТРАЦИЯ LOCATION BUBBLE AGENT В SFM ===

✅ Запись загружена: location_bubble_agent
✅ Backup создан: /opt/aladdin-backend/data/sfm/function_registry_backup_YYYYMMDD_HHMMSS.json
✅ Агент зарегистрирован в SFM
   - Всего агентов: X
   - Всего функций: X
   - Всего API endpoints: X
   - Функций Location Bubble Agent: 5
   - API endpoints Location Bubble Agent: 6
```

### Шаг 4: Интеграция в main.py

```bash
cd /tmp
python3 add_location_bubble_to_main.py
```

Скрипт автоматически:
- ✅ Найдет main.py
- ✅ Добавит импорт router
- ✅ Добавит регистрацию router
- ✅ Создаст backup
- ✅ Проверит синтаксис

**Или вручную:**

Добавьте в `/opt/aladdin-backend/api/main.py` или `/opt/aladdin-backend/main.py`:

```python
# Импорт (в начале файла, после других импортов routers)
from security.api.routers.location_bubble_router import router as location_bubble_router

# Регистрация (после создания app)
try:
    app.include_router(location_bubble_router)
    print("✅ Location Bubble Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать Location Bubble Router: {e}")
```

### Шаг 5: Перезапуск сервиса

```bash
# Через systemctl
systemctl restart aladdin-backend
systemctl status aladdin-backend

# Или через supervisorctl
supervisorctl restart aladdin-backend
```

### Шаг 6: Проверка работы

```bash
# Health check
curl http://localhost:8000/api/location/bubble/health

# Должен вернуть:
# {
#   "status": "healthy",
#   "agent": "location_bubble_agent",
#   "version": "1.0.0",
#   "timestamp": "2025-12-12T..."
# }
```

```bash
# Если используется systemd
systemctl restart aladdin-backend

# Или если используется supervisor
supervisorctl restart aladdin-backend

# Или если запущен вручную
# Остановите и запустите заново
```

---

## ✅ ПРОВЕРКА ДЕПЛОЯ

### 1. Проверка файлов на сервере

```bash
ssh root@149.154.65.180

# Проверка агента
ls -la /opt/aladdin-backend/security/ai_agents/location_bubble_agent.py

# Проверка router
ls -la /opt/aladdin-backend/security/api/routers/location_bubble_router.py

# Проверка регистрации в SFM
grep -A 5 "location_bubble_agent" /opt/aladdin-backend/data/sfm/function_registry.json
```

### 2. Проверка импорта в main.py

```bash
grep "location_bubble_router" /opt/aladdin-backend/api/main.py
# или
grep "location_bubble_router" /opt/aladdin-backend/main.py
```

### 3. Проверка логов

```bash
# Логи systemd
journalctl -u aladdin-backend -n 50 | grep -i "location_bubble"

# Должно быть видно:
# ✅ Location Bubble Router зарегистрирован
```

### 4. Проверка API endpoints

```bash
# Health check
curl http://localhost:8000/api/location/bubble/health

# Тест генерации пузыря (требует авторизации)
curl -X POST http://localhost:8000/api/location/bubble \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "person_id": "test_person",
    "exact_latitude": 55.7558,
    "exact_longitude": 37.6173,
    "radius": 500
  }'
```

---

## 🔧 УСТРАНЕНИЕ ПРОБЛЕМ

### ⚠️ КРИТИЧЕСКИ ВАЖНО: Типичные проблемы при деплое агентов

Этот раздел содержит **реальные проблемы**, которые возникали при деплое других агентов и их решения. **Обязательно прочитайте перед деплоем!**

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
    from .location_bubble_agent import LocationBubbleAgent  # noqa: F401
except ImportError:
    pass  # Зависимости не установлены, пропускаем
```

---

### 🔴 ПРОБЛЕМА 2: `AttributeError: 'Agent' object has no attribute 'config'`

**Симптомы:**
```python
AttributeError: 'LocationBubbleAgent' object has no attribute 'config'
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
    self.default_radius = config_dict.get("default_radius", 500)
```

---

### 🔴 ПРОБЛЕМА 3: `TypeError: Can't instantiate abstract class`

**Симптомы:**
```python
TypeError: Can't instantiate abstract class LocationBubbleAgent without an implementation 
for abstract methods 'analyze_threats', 'collect_threats', 'send_alert'
```

**Причина:**
Если агент наследуется от `ThreatMonitoringInterface`, он **обязан** реализовать все абстрактные методы.

**Решение:**

Добавьте все требуемые методы в ваш агент (уже добавлены в LocationBubbleAgent):
```python
def collect_threats(self) -> List[Dict[str, Any]]:
    """Сбор угроз"""
    return []

def analyze_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Анализ угроз"""
    return threats

def send_alert(self, alert: Dict[str, Any]):
    """Отправка уведомления"""
    pass
```

---

### 🔴 ПРОБЛЕМА 4: `Permission denied (publickey,password)` при SSH/SCP

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

---

### 🔴 ПРОБЛЕМА 5: `Address already in use` при запуске uvicorn

**Симптомы:**
```
ERROR: [Errno 98] error while attempting to bind on address ('0.0.0.0', 8000): address already in use
```

**Решение:**

Убейте старый процесс перед перезапуском:
```bash
ssh root@149.154.65.180
pkill -f 'uvicorn main:app'
systemctl restart aladdin-backend
```

---

### ✅ ПРОБЛЕМА 6: Router не регистрируется

**Решение:**
1. Проверьте импорт в main.py
2. Проверьте что файл router существует на сервере
3. Проверьте логи на ошибки

---

### ✅ ПРОБЛЕМА 7: Health check не работает

**Решение:**
1. Проверьте что сервис перезапущен
2. Проверьте логи: `journalctl -u aladdin-backend -n 50`
3. Проверьте что порт 8000 не занят другим процессом

---

## 🔐 УЧЕТНЫЕ ДАННЫЕ СЕРВЕРА

**⚠️ ВАЖНО:** Эти данные используются для всех деплоев!

- **Сервер:** `149.154.65.180`
- **Пользователь:** `root` (НЕ Sergio675!)
- **Пароль:** `Sergio675`
- **Путь к backend:** `/opt/aladdin-backend`
- **Путь к venv:** `/opt/aladdin-backend/venv`
- **Путь к main.py:** `/opt/aladdin-backend/main.py` или `/opt/aladdin-backend/api/main.py`
- **Путь к SFM registry:** `/opt/aladdin-backend/data/sfm/function_registry.json`
- **Сервис:** `aladdin-backend` (systemctl)
- **Порт API:** `8000`

**Пример подключения:**
```bash
ssh root@149.154.65.180
# Пароль: Sergio675
```

---

## 📊 СТАТИСТИКА ПОСЛЕ ДЕПЛОЯ

После успешного деплоя в SFM должно быть:

- **Всего агентов:** X (было X-1)
- **Всего функций:** X (было X-5)
- **Всего API endpoints:** X (было X-6)
- **Location Bubble Agent:**
  - Функций: 5
  - API endpoints: 6

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

### ✅ После деплоя:

1. **Проверка импорта на сервере:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend && source venv/bin/activate && python3 -c 'from security.ai_agents.location_bubble_agent import LocationBubbleAgent; agent = LocationBubbleAgent(); print(\"✅ OK\")'"
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
ssh root@149.154.65.180 "curl -s http://localhost:8000/api/location/bubble/health | python3 -m json.tool"
```

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

После успешного деплоя:

1. ✅ **Проверьте работу API endpoints**
2. ✅ **Протестируйте генерацию пузырей**
3. ✅ **Проверьте настройки для разных людей**
4. ⏳ **iOS интеграция** (после завершения всех backend агентов)

---

## 📝 ЧЕКЛИСТ ДЕПЛОЯ

- [ ] Файлы скопированы на сервер
- [ ] Агент зарегистрирован в SFM
- [ ] Router интегрирован в main.py
- [ ] Health check работает
- [ ] API endpoints отвечают
- [ ] Логи не содержат ошибок
- [ ] SFM статистика обновлена

---

**Автор:** AI Assistant для ALADDIN Project  
**Дата:** 12 декабря 2025
