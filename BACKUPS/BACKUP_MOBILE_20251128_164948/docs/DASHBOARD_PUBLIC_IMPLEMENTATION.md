# 📊 ПУБЛИЧНЫЙ DASHBOARD - РЕАЛИЗАЦИЯ

**URL:** `https://aladdin-ai.ru/dashboard`  
**Стиль:** Карточный  
**Время:** 1-2 дня  
**Статус:** Ожидает выполнения

---

## 🎯 ЦЕЛЬ

Создать публичный dashboard для демонстрации статистики системы защиты.

---

## 📋 ЧТО НУЖНО СДЕЛАТЬ

### 1. Дизайн (Карточный стиль)

**Компоненты:**
- Карточка "Всего защищено устройств"
- Карточка "Блокировано угроз"
- Карточка "Активных пользователей"
- Карточка "Время работы системы"
- График "Угрозы по времени"
- График "Топ угроз"

**Цвета:**
- Основной: Синий (#007AFF)
- Успех: Зеленый (#34C759)
- Опасность: Красный (#FF3B30)
- Предупреждение: Оранжевый (#FF9500)

---

### 2. Backend API

**Источник данных (что уже есть):**
- `monitor_manager.get_system_status()` → CPU/RAM/disk, активные алерты.
- `/api/metrics` (с Redis кешем) → история метрик.
- `/var/log/aladdin/` → количество заблокированных угроз, uptime.

**Что нужно добавить:**
1. **Сервис сбора статистики** (cron или background task), который раз в N минут агрегирует:
   - `protected_devices` (количество устройств в БД семьи).
   - `blocked_threats_total` (сумма из логов ThreatManager).
   - `active_users` (семьи с активной подпиской).
   - `uptime_days` (текущее `datetime - install_date`).
   - `threats_timeline` (list[{timestamp,value}]).
   - `top_threats` (list[{name,count}]).
2. **Endpoints**:
```python
@app.get("/api/dashboard/public/stats")
async def get_public_stats():
    return stats_cache.get("public", default_payload)

@app.get("/api/dashboard/public/threats-timeline")
async def get_public_timeline():
    return {"timeline": collect_timeline(24)}

@app.get("/api/dashboard/public/top-threats")
async def get_public_top_threats():
    return {"items": top_threats(limit=5)}
```
- Все ответы кешировать (Redis) с TTL 30‑60 секунд.

---

### 3. Frontend (HTML/CSS/JavaScript)

**Структура:**
```
/var/www/aladdin-ai.ru/dashboard/
├── index.html
├── css/
│   └── dashboard.css
├── js/
│   └── dashboard.js
└── assets/
    └── images/
```

**Основные функции:**
- Загрузка данных через API
- Обновление каждые 30 секунд
- Адаптивный дизайн (mobile-friendly)
- Анимации карточек

---

### 4. Интеграция с Nginx

**Добавить в конфигурацию Nginx:**
```nginx
location /dashboard {
    alias /var/www/aladdin-ai.ru/dashboard;
    try_files $uri $uri/ /dashboard/index.html;
    index index.html;
}
```

---

## 📊 КРИТЕРИИ УСПЕХА

1. ✅ Dashboard доступен по URL
2. ✅ Данные загружаются из API
3. ✅ Дизайн карточный и красивый
4. ✅ Адаптивный (работает на мобильных)
5. ✅ Обновление в реальном времени

---

## 📝 ФАЙЛЫ

**Создать:**
- `/var/www/aladdin-ai.ru/dashboard/index.html`
- `/var/www/aladdin-ai.ru/dashboard/css/dashboard.css`
- `/var/www/aladdin-ai.ru/dashboard/js/dashboard.js`

---

**Готово к выполнению!** 🚀

---

## ✅ План работ (чек-лист)
1. **API Gateway**
   - [ ] Добавить модуль `dashboard_stats.py` (агрегатор, кеш).
   - [ ] Создать endpoints `/api/dashboard/public/*`.
   - [ ] Прописать маршруты в `api_gateway.py`, включить Redis TTL.
2. **Cron/Background**
   - [ ] Scheduler (например, `asyncio.create_task`) для обновления статистики каждые 60 сек.
3. **Frontend**
   - [ ] Сверстать `index.html` + стили/скрипты.
   - [ ] Реализовать запросы к API, загрузочный спиннер, автorefresh.
   - [ ] Добавить fallback (если API недоступно).
4. **Nginx/Deploy**
   - [ ] Создать каталог `/var/www/aladdin-ai.ru/dashboard`.
   - [ ] Добавить location в `nginx.conf`, выкатить статику.
5. **Тесты**
   - [ ] Проверить CORS (если dashboard на том же домене – достаточно `same-origin`).
   - [ ] Проверить обновление данных, mobile view, Lighthouse ≥90.

