# 🚀 ПОШАГОВАЯ НАСТРОЙКА NGINX И SYSTEMD

## 📋 ПЛАН ДЕЙСТВИЙ

1. ✅ Проверить текущее состояние
2. ✅ Настроить Nginx для ALADDIN API
3. ✅ Создать systemd сервис для API Gateway
4. ✅ Проверить работу через HTTPS

---

## 1️⃣ ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ

### Что уже есть:

✅ **Firewall:** Настроен (порты 22, 80, 443 открыты)  
✅ **SSL:** Сертификат установлен для `aladdin-ai.ru`  
✅ **Nginx:** Работает, есть конфигурация для `aladdin-ai.ru`  
✅ **API:** Работает на порту 8000 (через старый сервис)  
✅ **Systemd:** Есть сервис `aladdin-backend.service`

### Что нужно проверить:

- Работает ли API через HTTPS?
- Правильно ли настроен Nginx?
- Нужно ли обновить systemd сервис?

---

## 2️⃣ НАСТРОЙКА NGINX ДЛЯ ALADDIN API

### Текущая конфигурация:

Nginx уже настроен на проксирование `/api/` на `localhost:8000`

**Файл:** `/etc/nginx/sites-available/aladdin-ai.ru`

**Текущая настройка:**
```nginx
location /api/ {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Это правильно!** ✅

### Что можно улучшить:

1. Добавить timeout для долгих запросов
2. Добавить rate limiting
3. Добавить логирование

---

## 3️⃣ СОЗДАНИЕ SYSTEMD СЕРВИСА ДЛЯ API GATEWAY

### Вариант A: Обновить существующий сервис

Если старый API работает, можно обновить его на новый API Gateway.

### Вариант B: Создать новый сервис

Создать отдельный сервис для нового API Gateway.

---

## 4️⃣ ПРОВЕРКА РАБОТЫ ЧЕРЕЗ HTTPS

После настройки проверить:
- `https://aladdin-ai.ru/api/health`
- `https://aladdin-ai.ru/api/subscription/tariffs`
- Мобильное приложение может подключиться

---

## 📝 ЧЕКЛИСТ

- [ ] Проверить текущий API
- [ ] Проверить Nginx конфигурацию
- [ ] Обновить/создать systemd сервис
- [ ] Перезапустить сервисы
- [ ] Проверить HTTPS API
- [ ] Проверить работу из мобильного приложения

