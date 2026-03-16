# 🔧 ИСПРАВЛЕНИЕ: Отключение кэширования Nginx для API

**Дата:** 2026-03-14  
**Проблема:** Nginx кэширует ответы API на 60 секунд  
**Решение:** Отключить кэширование для `/api/*` endpoints

---

## 🔍 ПРОБЛЕМА

**Найдено в конфигурации Nginx:**
- `/etc/nginx/nginx.conf`: `proxy_cache_path /var/cache/nginx/api`
- `proxy_cache_valid 200 60s` - кэширование на 60 секунд

**Результат:**
- Мобильное приложение получает закэшированные ответы
- Старые ответы "SFM_PROXIED" хранятся в кэше
- Timestamp старый (`2026-03-15T15:06:18`)

---

## ✅ РЕШЕНИЕ

### **1. Отключить кэширование для `/api/*`:**

Добавить в конфигурацию Nginx (`/etc/nginx/sites-enabled/aladdin-ai.ru`):

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8002;
    
    # ✅ ОТКЛЮЧИТЬ КЭШИРОВАНИЕ
    proxy_cache off;
    proxy_no_cache 1;
    proxy_cache_bypass 1;
    
    # ✅ ЗАГОЛОВКИ ДЛЯ ОТКЛЮЧЕНИЯ КЭША
    proxy_set_header Cache-Control "no-cache, no-store, must-revalidate";
    proxy_set_header Pragma "no-cache";
    proxy_set_header Expires "0";
    
    # Стандартные заголовки прокси
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### **2. Очистить существующий кэш:**

```bash
rm -rf /var/cache/nginx/api/*
```

### **3. Перезагрузить Nginx:**

```bash
nginx -t  # Проверить конфигурацию
systemctl reload nginx  # Перезагрузить
```

---

## 🧪 ПРОВЕРКА

### **После исправления:**

```bash
# Проверить заголовки
curl -v "https://aladdin-ai.ru/api/reports/driving/stats" 2>&1 | grep -i cache
# Должны быть:
# Cache-Control: no-cache, no-store, must-revalidate

# Проверить данные
curl "https://aladdin-ai.ru/api/reports/driving/stats"
# Должен вернуть актуальные данные без "SFM_PROXIED"
```

---

**Статус:** ⚠️ ТРЕБУЕТСЯ ОБНОВЛЕНИЕ КОНФИГУРАЦИИ NGINX
