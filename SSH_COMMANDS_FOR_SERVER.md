# 🔧 КОМАНДЫ ДЛЯ ПРОВЕРКИ И ИСПРАВЛЕНИЯ НА СЕРВЕРЕ

**Дата:** 2026-02-13  
**Цель:** Проверить и исправить все проблемы для продакшн

---

## 📋 БЫСТРЫЙ СТАРТ:

### **1. Подключиться к серверу:**
```bash
ssh root@149.154.65.180
```

### **2. Перейти в директорию проекта:**
```bash
cd /opt/aladdin-backend
```

---

## 🔍 ПРОВЕРКА METRICS ROUTER:

### **Шаг 1: Проверить файл роутера**
```bash
ls -la security/api/routers/metrics_router.py
```

**Ожидаемый результат:** Файл существует

---

### **Шаг 2: Проверить префикс роутера**
```bash
grep -A 2 "APIRouter" security/api/routers/metrics_router.py
```

**Ожидаемый результат:**
```python
router = APIRouter(prefix="/metrics", tags=["metrics"])
```

**Если префикс `/api/metrics` - нужно исправить на `/metrics`**

---

### **Шаг 3: Проверить подключение в main.py**
```bash
grep -n "metrics_router" main.py
```

**Ожидаемый результат:** Должны быть строки с импортом и подключением

---

### **Шаг 4: Проверить независимость подключения**
```bash
grep -A 10 "metrics_router_available" main.py
```

**Ожидаемый результат:**
```python
if metrics_router_available:
    try:
        app.include_router(metrics_router)
        print("✅ Роутер Metrics подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Metrics: {e}")
```

**Если роутер внутри блока `if system_router_available:` - нужно исправить!**

---

### **Шаг 5: Проверить статус сервиса**
```bash
systemctl status aladdin-production-api
```

**Ожидаемый результат:** `active (running)`

---

### **Шаг 6: Проверить логи**
```bash
journalctl -u aladdin-production-api -n 50 --no-pager | grep -i metrics
```

**Ожидаемый результат:** Должны быть записи о подключении роутера

---

### **Шаг 7: Протестировать endpoint**
```bash
curl -X POST https://aladdin-ai.ru/api/metrics/upload \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"test","appVersion":"1.0.0","platform":"ios","metrics":[]}'
```

**Ожидаемый результат:** HTTP 200 OK с JSON ответом

---

## 🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМ:

### **Проблема 1: Роутер подключен условно**

**Исправление:**

1. **Открыть main.py:**
```bash
nano main.py
```

2. **Найти блок с metrics_router (обычно внутри system_router):**
```python
# НЕПРАВИЛЬНО:
if system_router_available:
    app.include_router(system_router)
    if metrics_router_available:
        app.include_router(metrics_router)
```

3. **Исправить на независимое подключение:**
```python
# ПРАВИЛЬНО:
if system_router_available:
    app.include_router(system_router)

# Независимо от system_router
if metrics_router_available:
    try:
        app.include_router(metrics_router)
        print("✅ Роутер Metrics подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Metrics: {e}")
```

4. **Сохранить и выйти:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### **Проблема 2: Неправильный префикс роутера**

**Исправление:**

1. **Открыть metrics_router.py:**
```bash
nano security/api/routers/metrics_router.py
```

2. **Найти строку с APIRouter:**
```python
# НЕПРАВИЛЬНО:
router = APIRouter(prefix="/api/metrics", tags=["metrics"])

# ПРАВИЛЬНО:
router = APIRouter(prefix="/metrics", tags=["metrics"])
```

3. **Сохранить и выйти:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### **Проблема 3: Роутер не подключен**

**Исправление:**

1. **Проверить импорт в main.py:**
```bash
grep "from security.api.routers.metrics_router import" main.py
```

2. **Если импорта нет, добавить после других импортов роутеров:**
```python
try:
    from security.api.routers.metrics_router import router as metrics_router
    metrics_router_available = True
except ImportError as e:
    print(f"⚠️ metrics_router недоступен: {e}")
    metrics_router_available = False
    metrics_router = None
```

3. **Добавить подключение роутера (после других роутеров):**
```python
if metrics_router_available:
    try:
        app.include_router(metrics_router)
        print("✅ Роутер Metrics подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Metrics: {e}")
```

---

## 🔄 ПЕРЕЗАПУСК СЕРВИСА:

После всех исправлений:

```bash
# Перезапустить сервис
sudo systemctl restart aladdin-production-api

# Подождать 5 секунд
sleep 5

# Проверить статус
systemctl status aladdin-production-api

# Проверить логи
journalctl -u aladdin-production-api -n 20 --no-pager
```

**Ожидаемый результат:**
- Сервис активен
- В логах есть: `✅ Роутер Metrics подключен`
- Нет ошибок

---

## ✅ ФИНАЛЬНАЯ ПРОВЕРКА:

```bash
# Тест endpoint
curl -X POST https://aladdin-ai.ru/api/metrics/upload \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"final_test","appVersion":"1.0.0","platform":"ios","metrics":[{"type":"user_action","timestamp":1234567890.0,"action":"test"}]}'
```

**Ожидаемый результат:**
```json
{
  "success": true,
  "uploadedCount": 1,
  "message": "Успешно загружено 1 метрик",
  "timestamp": "2026-02-13T..."
}
```

---

## 📋 ЧЕКЛИСТ:

- [ ] Файл `metrics_router.py` существует
- [ ] Префикс роутера правильный (`/metrics`)
- [ ] Роутер подключен в `main.py`
- [ ] Роутер подключен независимо (не зависит от system_router)
- [ ] Сервис перезапущен
- [ ] В логах есть сообщение о подключении роутера
- [ ] Endpoint возвращает HTTP 200

---

**Последнее обновление:** 2026-02-13
