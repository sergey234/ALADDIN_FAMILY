# 🏗️ АРХИТЕКТУРА BACKEND: Где и как должен работать backend

## 📋 ТЕКУЩАЯ СИТУАЦИЯ

### ❌ Что не работает:
1. **Backend не запущен** — нет процессов Python на портах 8000, 8001 и т.д.
2. **Nginx не настроен** — нет `location /api/` для проксирования запросов
3. **Директория пустая** — `/opt/aladdin-backend/` существует, но пуста

### ✅ Что работает:
- Лендинг доступен на `https://aladdin-ai.ru/`
- Nginx работает и отдает статические файлы
- SSL сертификаты настроены

---

## 🎯 ПРАВИЛЬНАЯ АРХИТЕКТУРА

### Вариант 1: Backend на том же сервере (рекомендуется для начала)

```
┌─────────────────────────────────────┐
│  Сервер: 149.154.65.180             │
│  Домен: aladdin-ai.ru               │
├─────────────────────────────────────┤
│                                      │
│  ┌──────────────┐                   │
│  │   Nginx       │  :443 (HTTPS)     │
│  │   (Frontend)  │                   │
│  └──────┬────────┘                   │
│         │                            │
│         ├─── / → /var/www/...        │
│         │    (статические файлы)     │
│         │                            │
│         └─── /api/ → proxy_pass      │
│              └─── http://localhost:8000  │
│                  (Backend API)       │
│                                      │
│  ┌──────────────┐                   │
│  │   Backend     │  :8000 (HTTP)     │
│  │   (FastAPI)   │  (только localhost) │
│  └──────────────┘                   │
│                                      │
└─────────────────────────────────────┘
```

**Почему порт 8000?**
- Это стандартный порт для разработки (FastAPI, Flask, Django)
- Backend слушает только `localhost:8000` (не доступен извне)
- Nginx проксирует внешние запросы на внутренний backend
- Безопасность: backend не доступен напрямую из интернета

### Вариант 2: Backend на отдельном сервере (для масштабирования)

```
┌──────────────────┐         ┌──────────────────┐
│  Frontend Server │         │  Backend Server  │
│  aladdin-ai.ru   │ ──────→ │  api.aladdin-ai.ru│
│  (Nginx)         │         │  (FastAPI)       │
└──────────────────┘         └──────────────────┘
```

---

## 🔧 КАК ДОЛЖНО РАБОТАТЬ

### 1. Backend запущен локально на сервере

```bash
# Backend слушает на localhost:8000
# Только внутренние запросы (от Nginx)
http://localhost:8000/api/payments/create
```

**Почему localhost, а не 0.0.0.0?**
- Безопасность: backend не доступен из интернета напрямую
- Только Nginx может обращаться к backend
- Защита от прямых атак на API

### 2. Nginx проксирует запросы

```nginx
location /api/ {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Что это делает:**
- Запрос `https://aladdin-ai.ru/api/payments/create` 
- → Nginx получает запрос
- → Nginx проксирует на `http://localhost:8000/api/payments/create`
- → Backend обрабатывает запрос
- → Backend возвращает ответ
- → Nginx возвращает ответ клиенту

### 3. Пользователь видит только HTTPS

```
Пользователь → https://aladdin-ai.ru/api/payments/create
                ↓
            Nginx (443)
                ↓
            Backend (8000, localhost)
```

---

## 📊 ПОРТЫ И ИХ НАЗНАЧЕНИЕ

| Порт | Протокол | Доступ | Назначение |
|------|----------|--------|------------|
| **80** | HTTP | Публичный | Редирект на HTTPS |
| **443** | HTTPS | Публичный | Nginx (Frontend + API Proxy) |
| **8000** | HTTP | Только localhost | Backend API (FastAPI) |
| **22** | SSH | Публичный | Удаленное управление |

**Почему 8000?**
- Стандартный порт для разработки Python приложений
- Не конфликтует с другими сервисами
- Легко запомнить
- Можно использовать любой другой порт (8001, 8080, 5000)

---

## 🚀 ЧТО НУЖНО СДЕЛАТЬ

### Шаг 1: Запустить Backend на порту 8000

```bash
# На сервере
cd /opt/aladdin-backend
# Или где находится payment_service
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
```

**Параметры:**
- `--host 127.0.0.1` — слушать только localhost (безопасность)
- `--port 8000` — порт для backend
- `main:app` — точка входа FastAPI приложения

### Шаг 2: Настроить Nginx для проксирования

Добавить в `/etc/nginx/sites-available/aladdin-ai.ru`:

```nginx
server {
    server_name aladdin-ai.ru www.aladdin-ai.ru;
    
    root /var/www/aladdin-ai.ru;
    index index.html;
    
    # Статические файлы
    location / {
        try_files $uri $uri/ /index.html;
    }
    
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
    }
    
    # SSL конфигурация (уже есть)
    listen 443 ssl;
    # ...
}
```

### Шаг 3: Перезагрузить Nginx

```bash
nginx -t  # Проверка конфигурации
systemctl reload nginx  # Перезагрузка
```

---

## 🔍 АЛЬТЕРНАТИВНЫЕ ВАРИАНТЫ ПОРТОВ

### Почему не другие порты?

| Порт | Использование | Подходит? |
|------|---------------|-----------|
| **80** | HTTP (Nginx) | ❌ Занят Nginx |
| **443** | HTTPS (Nginx) | ❌ Занят Nginx |
| **8000** | Backend API | ✅ Идеально |
| **8001** | Backend API | ✅ Можно использовать |
| **8080** | Альтернативный HTTP | ✅ Можно использовать |
| **5000** | Flask по умолчанию | ✅ Можно использовать |
| **3000** | Node.js по умолчанию | ⚠️ Если не Node.js |

**Рекомендация:** Используйте **8000** — это стандарт для Python backend.

---

## 🛡️ БЕЗОПАСНОСТЬ

### ✅ Правильная конфигурация:

```python
# Backend слушает только localhost
uvicorn main:app --host 127.0.0.1 --port 8000
```

**Почему?**
- Backend не доступен из интернета напрямую
- Только Nginx может обращаться к backend
- Защита от прямых атак на API
- Firewall не нужен для порта 8000

### ❌ НЕПРАВИЛЬНАЯ конфигурация:

```python
# Backend доступен из интернета
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Почему плохо?**
- Backend доступен напрямую из интернета
- Можно обойти Nginx
- Нет SSL/TLS (только HTTP)
- Уязвимость безопасности

---

## 📝 ИТОГОВАЯ СХЕМА

```
Пользователь
    ↓
HTTPS:443 → Nginx (aladdin-ai.ru)
    ↓
    ├── / → /var/www/aladdin-ai.ru/ (статические файлы)
    │
    └── /api/ → proxy_pass → HTTP:8000 → Backend (localhost:8000)
                                    ↓
                            FastAPI обрабатывает запрос
                                    ↓
                            Возвращает JSON ответ
                                    ↓
                            Nginx → Пользователь
```

---

## 🎯 ВЫВОДЫ

1. **Backend должен быть на порту 8000** (или другом, но 8000 — стандарт)
2. **Backend слушает только localhost** (127.0.0.1) для безопасности
3. **Nginx проксирует /api/ на backend** через proxy_pass
4. **Пользователь видит только HTTPS** (443), backend работает на HTTP (8000)
5. **Порт 8000 не доступен из интернета** — только через Nginx

---

**Дата:** 19 ноября 2025  
**Версия:** 1.0

