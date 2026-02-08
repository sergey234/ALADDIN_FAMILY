# 🚨 BACKEND СЕРВЕР - ИСПРАВЛЕНИЕ 502 BAD GATEWAY

**Критическая проблема:** Все API запросы возвращают 502 Bad Gateway
**Влияние:** Приложение работает только локально, без синхронизации с сервером
**Приоритет:** 🔴 КРИТИЧНЫЙ (блокирует продакшн)

---

## 🔍 ДИАГНОСТИКА ПРОБЛЕМЫ

### **Текущий статус:**
```bash
✅ Основной сайт: https://aladdin-ai.ru/ → HTTP 200 OK
❌ API эндпоинты: https://aladdin-ai.ru/api/* → HTTP 502 Bad Gateway
```

**Что это значит:**
- Nginx веб-сервер работает корректно
- Backend приложение (Python/FastAPI) не запущено или не отвечает
- Nginx не может проксировать запросы к backend

---

## 🛠️ ПЛАН ИСПРАВЛЕНИЯ

### **Шаг 1: Доступ к серверу**

```bash
# Подключитесь к серверу по SSH:
ssh user@your-server-ip

# Или если используется облачный провайдер:
# AWS: ssh -i key.pem ubuntu@ec2-instance
# DigitalOcean: ssh root@droplet-ip
```

### **Шаг 2: Проверка статуса сервисов**

```bash
# Проверить статус nginx:
sudo systemctl status nginx
# Должен быть: Active: active (running)

# Проверить статус backend приложения:
sudo systemctl status aladdin-backend
# ИЛИ:
ps aux | grep python
ps aux | grep gunicorn
ps aux | grep uvicorn
```

### **Шаг 3: Диагностика логов**

```bash
# Логи nginx:
sudo tail -50 /var/log/nginx/error.log
sudo tail -50 /var/log/nginx/access.log

# Логи backend приложения (если есть):
sudo tail -50 /var/log/aladdin/backend.log
# ИЛИ:
journalctl -u aladdin-backend -n 50
```

### **Шаг 4: Проверка конфигурации nginx**

```bash
# Проверить конфигурацию сайта:
sudo cat /etc/nginx/sites-available/aladdin

# Пример корректной конфигурации:
server {
    listen 80;
    server_name aladdin-ai.ru;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **Шаг 5: Проверка backend приложения**

```bash
# Проверить, слушает ли приложение порт 8000:
sudo netstat -tlnp | grep :8000
# Должен быть: tcp 0 0 127.0.0.1:8000 LISTEN

# Тестирование локального подключения:
curl -I http://127.0.0.1:8000/api/health
# Должно быть HTTP 200 OK, не 502
```

---

## 🔧 ВОЗМОЖНЫЕ РЕШЕНИЯ

### **Решение 1: Перезапуск backend сервиса**

```bash
# Если сервис существует:
sudo systemctl restart aladdin-backend

# Проверить статус:
sudo systemctl status aladdin-backend

# Если не помогает, проверить логи:
journalctl -u aladdin-backend -f
```

### **Решение 2: Ручной запуск backend**

```bash
# Найти директорию с приложением:
cd /path/to/aladdin/backend

# Активировать виртуальное окружение:
source venv/bin/activate  # или source .venv/bin/activate

# Запустить приложение:
python main.py
# ИЛИ:
gunicorn main:app -b 127.0.0.1:8000
# ИЛИ:
uvicorn main:app --host 127.0.0.1 --port 8000
```

### **Решение 3: Исправление nginx конфигурации**

```bash
# Редактировать конфигурацию:
sudo nano /etc/nginx/sites-available/aladdin

# Исправить proxy_pass (убрать trailing slash для /api/):
location /api/ {
    proxy_pass http://127.0.0.1:8000;  # без /api/
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Перезагрузить nginx:
sudo nginx -t  # проверить конфигурацию
sudo systemctl reload nginx
```

### **Решение 4: Проверка портов и firewall**

```bash
# Проверить открытые порты:
sudo ufw status
# Должен быть разрешен порт 80 и 443

# Проверить, не занят ли порт 8000:
sudo lsof -i :8000
```

---

## 🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ

### **После каждого исправления тестировать:**

```bash
# 1. Локальное тестирование:
curl -I http://127.0.0.1:8000/api/health

# 2. Через nginx:
curl -I https://aladdin-ai.ru/api/health

# 3. Полное тестирование всех API:
for endpoint in "health" "user/profile" "components/status/crash_detection_agent"; do
    echo "Testing: $endpoint"
    curl -I "https://aladdin-ai.ru/api/$endpoint" | grep "HTTP/"
done
```

### **Ожидаемые результаты:**
```bash
✅ curl -I https://aladdin-ai.ru/api/health
HTTP/2 200 OK

✅ curl -I https://aladdin-ai.ru/api/user/profile
HTTP/2 200 OK

✅ curl -I https://aladdin-ai.ru/api/components/status/crash_detection_agent
HTTP/2 200 OK
```

---

## 🚨 АВАРИЙНЫЕ МЕРЫ

### **Если ничего не помогает:**

#### **Временное решение: Отключить backend зависимость**
```swift
// В NetworkProtectionViewModel отключить API запросы:
func loadComponentStatuses() {
    // Временно отключить загрузку статусов
    // self.componentStatuses = [:] // пустой словарь
    print("⚠️ Backend недоступен - работаем в offline режиме")
}
```

#### **Создать mock backend для тестирования:**
```python
# mock_server.py
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/user/profile")
def profile():
    return {"user": "test", "status": "active"}

@app.get("/api/components/status/{component_id}")
def component_status(component_id: str):
    return {"component_id": component_id, "status": "enabled"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

---

## 📊 КРИТЕРИИ ГОТОВНОСТИ

### ✅ **Backend исправлен, если:**
- [ ] `curl https://aladdin-ai.ru/api/health` возвращает HTTP 200
- [ ] Все API эндпоинты работают
- [ ] Приложение может загружать статусы компонентов
- [ ] Синхронизация настроек работает
- [ ] Аналитика отправляется на сервер

### ❌ **Если проблема не решена:**
- [ ] Создать mock backend для тестирования
- [ ] Отключить backend зависимости в коде
- [ ] Протестировать локальную функциональность Crash Detection

---

## 🎯 РЕКОМЕНДАЦИИ

### **Для продакшна:**
1. **Мониторинг:** Настроить мониторинг uptime для API
2. **Логирование:** Включить подробное логирование ошибок
3. **Автозапуск:** Настроить автоматический перезапуск сервиса
4. **Резервное копирование:** Регулярные бэкапы базы данных

### **Для разработки:**
1. **Docker:** Использовать Docker для локальной разработки
2. **CI/CD:** Настроить автоматическое развертывание
3. **Тестирование:** Добавить health checks в pipeline

---

**🚨 BACKEND СЕРВЕР - КРИТИЧЕСКАЯ ПРОБЛЕМА КОТОРАЯ БЛОКИРУЕТ ПРОДАКШН**

**Нужно срочно исправить 502 ошибку на сервере!** 🔴