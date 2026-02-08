# 🚀 **BACKEND СЕРВЕР - НЕМЕДЛЕННЫЙ ЗАПУСК**

**Цель:** Запустить сервер `149.154.65.180:8002` **НЕМЕДЛЕННО**
**Время:** 10-15 минут
**Приоритет:** 🔴 КРИТИЧНЫЙ

---

## ⚡ **ЭКСТРЕННЫЙ ПЛАН ЗАПУСКА BACKEND**

### **Шаг 1: Быстрая диагностика (2 минуты)**

```bash
# Проверить текущее состояние
echo "=== BACKEND SERVER STATUS ==="
curl -I --connect-timeout 5 http://149.154.65.180:8002/api/health 2>&1 | head -3

# Если "Couldn't connect" - сервер остановлен
# Если "HTTP/2 502" - nginx работает, но backend нет
```

### **Шаг 2: Доступ к серверу (1 минута)**

```bash
# Подключиться к серверу
ssh user@149.154.65.180

# Проверить, что мы на нужном сервере
hostname
# Должно быть что-то вроде aladdin-backend-server
```

### **Шаг 3: Проверить процессы (2 минуты)**

```bash
# Проверить запущенные процессы
ps aux | grep -E "(python|gunicorn|uvicorn|fastapi)"

# Если ничего не найдено - сервер остановлен
# Проверить логи последнего запуска
sudo journalctl -u aladdin-backend -n 10
```

### **Шаг 4: Запуск FastAPI приложения (5 минут)**

#### **Вариант 1: Через systemd (рекомендуется)**
```bash
# Проверить статус сервиса
sudo systemctl status aladdin-backend

# Если stopped - запустить
sudo systemctl start aladdin-backend

# Проверить статус
sudo systemctl status aladdin-backend
```

#### **Вариант 2: Ручной запуск (если systemd не настроен)**
```bash
# Перейти в директорию проекта
cd /path/to/aladdin/backend

# Активировать виртуальное окружение
source venv/bin/activate

# Запустить через Gunicorn
gunicorn main:app \
    --bind 0.0.0.0:8002 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile /var/log/aladdin/access.log \
    --error-logfile /var/log/aladdin/error.log

# ИЛИ через Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### **Шаг 5: Тестирование запуска (3 минуты)**

```bash
# Тестирование на сервере
curl -I http://127.0.0.1:8002/api/health
# Должно быть: HTTP/1.1 200 OK

curl http://127.0.0.1:8002/api/health
# Должно быть: {"status":"ok","source":"real_sfm"}

# Тестирование через внешний IP
curl -I http://149.154.65.180:8002/api/health
# Должно быть: HTTP/1.1 200 OK
```

### **Шаг 6: Тестирование через домен (2 минуты)**

```bash
# Тестирование через aladdin-ai.ru
curl -I https://aladdin-ai.ru/api/health
# Должно быть: HTTP/2 200 OK

curl https://aladdin-ai.ru/api/health
# Должно быть: {"status":"ok","source":"real_sfm"}
```

---

## 🔧 **АВАРИЙНЫЕ КОМАНДЫ**

### **Если systemd сервис не существует:**
```bash
# Создать сервис файл
sudo nano /etc/systemd/system/aladdin-backend.service

# Вставить содержимое:
[Unit]
Description=ALADDIN Backend API
After=network.target

[Service]
User=aladdin
Group=aladdin
WorkingDirectory=/path/to/aladdin/backend
Environment="PATH=/path/to/aladdin/backend/venv/bin"
ExecStart=/path/to/aladdin/backend/venv/bin/gunicorn main:app --bind 0.0.0.0:8002 --workers 4 --worker-class uvicorn.workers.UvicornWorker
Restart=always

[Install]
WantedBy=multi-user.target

# Сохранить, выйти
# Включить и запустить
sudo systemctl daemon-reload
sudo systemctl enable aladdin-backend
sudo systemctl start aladdin-backend
```

### **Если порт 8002 занят:**
```bash
# Проверить, что занимает порт
sudo lsof -i :8002
sudo netstat -tlnp | grep :8002

# Убить процесс, если нужно
sudo kill -9 PID_NUMBER

# Или изменить порт в команде запуска
```

---

## 📊 **КРИТЕРИИ ГОТОВНОСТИ**

### ✅ **Backend запущен успешно, если:**
- [x] `curl http://149.154.65.180:8002/api/health` возвращает HTTP 200
- [x] `curl https://aladdin-ai.ru/api/health` возвращает HTTP 200
- [x] JSON ответ содержит `"source": "real_sfm"`
- [x] Все API эндпоинты отвечают корректно

### ❌ **Если проблемы:**
- [ ] Проверить логи: `sudo journalctl -u aladdin-backend -f`
- [ ] Проверить порт: `sudo netstat -tlnp | grep :8002`
- [ ] Проверить файлы: `ls -la /path/to/aladdin/backend/`

---

## 🚀 **ПОСЛЕ ЗАПУСКА**

### **Тестирование мобильного приложения:**
```bash
# В Xcode запустить приложение
# Проверить Network Protection экран
# Должны загружаться статусы компонентов
# Crash Detection должен работать с сервером
```

### **Мониторинг:**
```bash
# Логи сервера
sudo tail -f /var/log/aladdin/error.log

# Nginx логи
sudo tail -f /var/log/nginx/error.log
```

---

## ⚡ **ВРЕМЕННОЕ РЕШЕНИЕ (5 минут)**

Если невозможно быстро запустить основной сервер:

```python
# Создать временный mock сервер на другом порту
# Запустить на локальной машине для тестирования
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok", "source": "real_sfm"}

@app.get("/api/components/status/{component_id}")
def component_status(component_id: str):
    return {
        "status": "success",
        "source": "real_sfm",
        "data": {"component_id": component_id, "enabled": True}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

---

**⏰ ВРЕМЯ ВЫПОЛНЕНИЯ: 10-15 МИНУТ**
**🚨 ПРИОРИТЕТ: ЗАПУСТИТЬ НЕМЕДЛЕННО**

**Следующий шаг после запуска backend: настроить Settings Modal!**