# 🚀 ПОЛНАЯ ИНСТРУКЦИЯ: Настройка Backend на продакшн-сервере

## 📋 РЕЗЮМЕ ПРОБЛЕМЫ

**Ошибка:** `405 Not Allowed` при попытке оплаты

**Причина:**
1. ❌ Backend не запущен на сервере
2. ❌ Nginx не настроен для проксирования `/api/` на backend

**Решение:**
1. ✅ Запустить backend на порту 8000 (localhost)
2. ✅ Настроить Nginx для проксирования `/api/` → `http://localhost:8000`

---

## 🎯 АРХИТЕКТУРА (Почему порт 8000?)

```
Пользователь → https://aladdin-ai.ru/api/payments/create
                ↓
            Nginx (443, HTTPS)
                ↓ proxy_pass
            Backend (8000, HTTP, localhost)
                ↓
            FastAPI обрабатывает запрос
```

**Почему порт 8000?**
- ✅ Стандартный порт для Python backend (FastAPI, Flask, Django)
- ✅ Backend слушает только `localhost:8000` (не доступен из интернета)
- ✅ Nginx проксирует внешние запросы на внутренний backend
- ✅ Безопасность: backend не доступен напрямую из интернета

**Почему localhost, а не 0.0.0.0?**
- ✅ Безопасность: только Nginx может обращаться к backend
- ✅ Защита от прямых атак на API
- ✅ Firewall не нужен для порта 8000

---

## 📝 ШАГ 1: ЗАГРУЗКА BACKEND НА СЕРВЕР

### 1.1. Подключитесь к серверу

```bash
ssh root@149.154.65.180
# Пароль: Sergio675
```

### 1.2. Создайте директорию для backend

```bash
mkdir -p /opt/aladdin-backend
cd /opt/aladdin-backend
```

### 1.3. Загрузите файлы backend с локального Mac

**На локальном Mac выполните:**

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Загружаем payment_service на сервер
rsync -avz --progress payment_service/ root@149.154.65.180:/opt/aladdin-backend/
```

**Или используйте expect-скрипт:**

```bash
./deploy_backend.sh  # (создадим ниже)
```

---

## 📝 ШАГ 2: УСТАНОВКА ЗАВИСИМОСТЕЙ

### 2.1. На сервере установите Python и зависимости

```bash
# На сервере
cd /opt/aladdin-backend

# Установите Python 3.11+ (если нет)
apt update
apt install -y python3 python3-pip python3-venv

# Создайте виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

---

## 📝 ШАГ 3: НАСТРОЙКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ

### 3.1. Создайте файл `.env`

```bash
# На сервере
cd /opt/aladdin-backend
nano .env
```

### 3.2. Добавьте в `.env`:

```env
# База данных
PAYMENT_DATABASE_URL=sqlite+aiosqlite:///./payments.db

# API ключи
PAYMENT_API_KEY_PUBLIC=PUBLIC_CLIENT_KEY
PAYMENT_WEBHOOK_SECRET=WEBHOOK_SECRET_KEY_CHANGE_IN_PRODUCTION
PAYMENT_ADMIN_KEY=ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION

# Оплата на карту через СБП
PAYMENT_CARD_NUMBER=2202 2083 0881 3410
PAYMENT_CARD_HOLDER_NAME=

# Rate limiting
PAYMENT_RATE_LIMIT_RETRIEVE_MAX=5
PAYMENT_RATE_LIMIT_RETRIEVE_WINDOW=60
```

### 3.3. Сохраните файл (Ctrl+O, Enter, Ctrl+X)

---

## 📝 ШАГ 4: ЗАПУСК BACKEND

### 4.1. Запустите backend вручную (для теста)

```bash
# На сервере
cd /opt/aladdin-backend
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000
```

**Параметры:**
- `--host 127.0.0.1` — слушать только localhost (безопасность)
- `--port 8000` — порт для backend
- `main:app` — точка входа FastAPI приложения

### 4.2. Проверьте, что backend работает

**В другом терминале на сервере:**

```bash
curl http://localhost:8000/api/payment-methods
```

**Ожидаемый результат:** JSON с методами оплаты

---

## 📝 ШАГ 5: НАСТРОЙКА SYSTEMD (Автозапуск)

### 5.1. Создайте systemd service

```bash
# На сервере
nano /etc/systemd/system/aladdin-backend.service
```

### 5.2. Добавьте конфигурацию:

```ini
[Unit]
Description=Aladdin Payment Service Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aladdin-backend
Environment="PATH=/opt/aladdin-backend/.venv/bin"
ExecStart=/opt/aladdin-backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.3. Сохраните и активируйте сервис

```bash
# Перезагрузите systemd
systemctl daemon-reload

# Включите автозапуск
systemctl enable aladdin-backend

# Запустите сервис
systemctl start aladdin-backend

# Проверьте статус
systemctl status aladdin-backend
```

---

## 📝 ШАГ 6: НАСТРОЙКА NGINX

### 6.1. Создайте backup конфигурации

```bash
# На сервере
cp /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-available/aladdin-ai.ru.backup_$(date +%Y%m%d_%H%M%S)
```

### 6.2. Откройте конфигурацию Nginx

```bash
nano /etc/nginx/sites-available/aladdin-ai.ru
```

### 6.3. Добавьте `location /api/` ПЕРЕД `location /`

```nginx
server {
    server_name aladdin-ai.ru www.aladdin-ai.ru;

    root /var/www/aladdin-ai.ru;
    index index.html;

    access_log /var/log/nginx/aladdin_ai_access.log;
    error_log  /var/log/nginx/aladdin_ai_error.log;

    # ✅ ДОБАВИТЬ: Проксирование API на backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Для POST запросов
        proxy_set_header Content-Type $content_type;
        proxy_set_header Content-Length $content_length;
        
        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Увеличиваем размер тела запроса (для больших JSON)
        client_max_body_size 10M;
    }

    # Статические файлы
    location / {
        try_files $uri $uri/ /index.html;
    }

    # SSL конфигурация (уже есть)
    listen 443 ssl;
    # ...
}
```

### 6.4. Сохраните файл (Ctrl+O, Enter, Ctrl+X)

### 6.5. Проверьте и перезагрузите Nginx

```bash
# Проверка конфигурации
nginx -t

# Если OK, перезагрузите
systemctl reload nginx
```

---

## 📝 ШАГ 7: ПРОВЕРКА

### 7.1. Проверьте, что backend работает

```bash
# На сервере
curl http://localhost:8000/api/payment-methods
```

**Ожидаемый результат:** JSON с методами оплаты

### 7.2. Проверьте через Nginx (извне)

```bash
# С локального Mac
curl https://aladdin-ai.ru/api/payment-methods
```

**Ожидаемый результат:** JSON с методами оплаты

### 7.3. Проверьте создание платежа

```bash
curl -X POST https://aladdin-ai.ru/api/payments/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: PUBLIC_CLIENT_KEY" \
  -d '{
    "tariffId": "family",
    "userAlias": "test123",
    "pin": "1234",
    "paymentMethod": "qr_sbp",
    "periodMonths": 1,
    "amount": 490,
    "personalDataConsent": true,
    "consentTimestamp": "2025-11-19T20:00:00Z",
    "consentIP": "127.0.0.1"
  }'
```

**Ожидаемый результат:** JSON с `paymentId` и `redirectUrl`

---

## 🔧 АВТОМАТИЗАЦИЯ: Скрипты для деплоя

### Скрипт 1: Загрузка backend на сервер

**Файл:** `deploy_backend.sh`

```bash
#!/usr/bin/expect -f
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"
set local_path "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/payment_service/"
set remote_path "/opt/aladdin-backend/"

puts "🚀 Загружаю backend на сервер..."

spawn rsync -avz --progress $local_path $server:$remote_path

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof { puts "\n✅ Backend загружен!" }
    timeout { exit 1 }
}
wait
```

### Скрипт 2: Настройка Nginx

**Файл:** `setup_nginx_api.sh`

См. файл выше в проекте.

---

## 🐛 УСТРАНЕНИЕ ПРОБЛЕМ

### Проблема 1: "Connection refused" на порту 8000

**Решение:**
```bash
# Проверьте, запущен ли backend
systemctl status aladdin-backend

# Если не запущен, запустите
systemctl start aladdin-backend

# Проверьте логи
journalctl -u aladdin-backend -f
```

### Проблема 2: "502 Bad Gateway"

**Решение:**
- Backend не запущен или не слушает на порту 8000
- Проверьте: `curl http://localhost:8000/api/payment-methods`

### Проблема 3: "405 Not Allowed"

**Решение:**
- Nginx не настроен для проксирования `/api/`
- Проверьте конфигурацию: `grep -A 10 'location /api' /etc/nginx/sites-available/aladdin-ai.ru`

### Проблема 4: Backend не запускается

**Решение:**
```bash
# Проверьте логи
journalctl -u aladdin-backend -n 50

# Проверьте зависимости
cd /opt/aladdin-backend
source .venv/bin/activate
pip list

# Запустите вручную для отладки
uvicorn main:app --host 127.0.0.1 --port 8000 --log-level debug
```

---

## ✅ ЧЕКЛИСТ

- [ ] Backend загружен на сервер (`/opt/aladdin-backend/`)
- [ ] Установлены зависимости (`pip install -r requirements.txt`)
- [ ] Создан файл `.env` с переменными окружения
- [ ] Backend запущен (`systemctl start aladdin-backend`)
- [ ] Backend работает локально (`curl http://localhost:8000/api/payment-methods`)
- [ ] Nginx настроен для проксирования `/api/`
- [ ] Nginx перезагружен (`systemctl reload nginx`)
- [ ] API доступен извне (`curl https://aladdin-ai.ru/api/payment-methods`)
- [ ] Создание платежа работает (POST запрос)

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

- **Архитектура:** `docs/BACKEND_ARCHITECTURE_EXPLANATION.md`
- **README Backend:** `payment_service/README.md`
- **Настройка Manual Transfer:** `payment_service/SETUP_MANUAL_TRANSFER.md`

---

**Дата:** 19 ноября 2025  
**Версия:** 1.0

