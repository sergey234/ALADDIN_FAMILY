# 🔐 ПРИВАТНЫЙ DASHBOARD - РЕАЛИЗАЦИЯ

**URL:** `https://aladdin-ai.ru/admin/dashboard`  
**Стиль:** Профессиональный  
**Время:** 2-3 дня  
**Статус:** Ожидает выполнения

---

## 🎯 ЦЕЛЬ

Создать приватный dashboard для администраторов с детальной статистикой и управлением.

---

## 📋 ЧТО НУЖНО СДЕЛАТЬ

### 1. Авторизация

**Требования:**
- Форма входа + двухфакторный PIN (по e-mail/Telegram).
- JWT (access + refresh) с хранением в Redis и сроком 12 ч.
- Ограничение попыток (rate limit / captcha после 5 ошибок).
- Логирование всех входов в `/var/log/aladdin/admin_auth.log`.

**Endpoints (FastAPI):**
```python
POST /api/admin/login        # email+password(+otp) → tokens
POST /api/admin/refresh      # refresh → new access
POST /api/admin/logout       # revoke tokens
GET  /api/admin/me           # Проверка сессии
```

---

### 2. Дизайн (Профессиональный стиль)

**Компоненты:**
- Sidebar навигация
- Заголовок с информацией о пользователе
- Основная область с виджетами:
  - Системные метрики (CPU, RAM, Disk)
  - Статистика пользователей
  - Статистика угроз
  - Логи в реальном времени
  - Управление сервисами
  - Настройки системы

**Цвета:**
- Темная тема (профессиональная)
- Акценты: Синий, Зеленый, Красный

---

### 3. Backend API

**Источники данных:**
- `monitor_manager.get_metrics()` → системные метрики.
- БД пользователей / подписок (`security/database/models.py`) → статистика клиентов.
- Threat manager / alert manager → угрозы, алерты.
- Systemd / `journalctl` → логи сервисов.

**Endpoints:**
```python
# Метрики
GET /api/admin/metrics/system
GET /api/admin/metrics/users
GET /api/admin/metrics/threats

# Логи
GET /api/admin/logs
GET /api/admin/logs/{service}

# Управление
POST /api/admin/services/{service}/restart
POST /api/admin/services/{service}/stop
POST /api/admin/services/{service}/start

# Настройки
GET /api/admin/settings
POST /api/admin/settings
```

---

### 4. Frontend

**Технологии:**
- React или Vue.js (рекомендуется)
- Или чистый HTML/CSS/JS

**Структура:**
```
/var/www/aladdin-ai.ru/admin/
├── index.html
├── login.html
├── css/
│   └── admin.css
├── js/
│   ├── admin.js
│   ├── charts.js
│   └── api.js
└── assets/
```

---

### 5. Функциональность

**Управление:**
- Перезапуск сервисов
- Просмотр логов
- Настройка системы
- Управление пользователями

**Мониторинг:**
- Графики метрик
- Алерты
- Статистика

---

## 📊 КРИТЕРИИ УСПЕХА

1. ✅ Авторизация работает
2. ✅ Все метрики отображаются
3. ✅ Управление сервисами работает
4. ✅ Логи доступны
5. ✅ Дизайн профессиональный

---

**Готово к выполнению!** 🚀

---

## ✅ План работ (чек-лист)
1. **Auth & Security**
   - [ ] Создать таблицу администраторов + миграции.
   - [ ] Реализовать JWT/refresh, хранение в Redis, rate limit входов.
   - [ ] Добавить middleware, который закрывает `/api/admin/*`.
2. **API/Сервис статистики**
   - [ ] Сервис `admin_stats.py` (агрегация CPU/RAM/Users/Threats).
   - [ ] Endpoints из списка выше + пэйджинг для логов.
   - [ ] Команды управления сервисами (обёртка над `systemctl` / `supervisorctl`).
3. **Frontend**
   - [ ] Страницы: `login.html`, `dashboard.html`.
   - [ ] Sidebar с разделами (Системные метрики / Пользователи / Угрозы / Логи / Настройки).
   - [ ] Графики (Chart.js), таблицы (DataTables или собственные).
4. **Деплой**
   - [ ] Каталог `/var/www/aladdin-ai.ru/admin`.
   - [ ] Nginx location `/admin/` + `/admin/api` (проксировать в API Gateway).
   - [ ] Включить HTTPS + Basic Auth (как дополнительный слой).
5. **Тесты**
   - [ ] Проверка авторизации (валид/невалид, rate limiting).
   - [ ] Проверка управления сервисами (безопасность — whitelist команд).
   - [ ] Проверка логов, push-уведомлений (при падении сервиса).

