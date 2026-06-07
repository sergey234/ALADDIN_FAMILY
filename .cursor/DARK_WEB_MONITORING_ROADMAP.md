# Dark Web Monitoring — что сделано сейчас и план на будущее

> Обновлено: 2026-06-07. Prod: `149.154.65.180`, `/opt/aladdin-backend`, API `:8002`.

## Сейчас (без бюджета HIBP) — максимум

| Что | Статус | Комментарий |
|-----|--------|-------------|
| Честные счётчики 0/0/0 per user | ✅ prod | Нет фейковых audit-строк в `darkweb_leaks` |
| Scan audit в `darkweb.scan_events` | ✅ prod | JWT `user_id`, не в leaks |
| Fast scan контракт iOS | ✅ prod | `found: false` для email без HIBP |
| **Secure scan пароль (Pwned Passwords)** | ✅ код + prod | **Бесплатно**, SHA-1 на клиенте → сервер |
| Secure scan email hash | ✅ честно | `found: false` — HIBP не ищет по hash |
| Phone / passport / SNILS | ✅ честно | `found: false` — источник не подключён |
| UX: подпись «данные с сервера» + coverage note | ✅ код | Пользователь видит ограничения |
| Smoke | `scripts/smoke_dark_web_prod.sh` | JWT + stats + fast + password |
| `user_id` BIGINT на prod | ✅ миграция | Исправлен 500 при scan (JWT id > 2³¹) |
| HIBP deploy script (на будущее) | `scripts/configure_hibp_api_key_prod.sh` | Ждёт платный ключ |

### Как проверить пароль сейчас (бесплатно)

1. В приложении: **Безопасное сканирование** → ввести пароль (не email).
2. Или на сервере: `./scripts/smoke_dark_web_prod.sh` — блок `secure scan pwned password`.

---

## Альтернативы мониторингу (кроме платного HIBP email)

| Способ | Стоимость | Что даёт | Минусы |
|--------|-----------|----------|--------|
| **HIBP Pwned Passwords** | **$0** | Пароль в утечках? | Только пароль, не email |
| **HIBP breachedaccount (email)** | от ~$4.39/мес Core | Золотой стандарт email | Платно, лимиты RPM |
| **HIBP k-anonymity email** | Core+ подписка | Email без передачи plaintext на сервер | Сложнее, всё равно платно |
| **Клиент → pwnedpasswords.com** | $0 | Пароль без сервера | Нет единой истории в ALADDIN |
| **Ссылка на haveibeenpwned.com** | $0 | Ручная проверка email | Не встроено, нет автоматизации |
| **BreachDirectory API** | платно/ключ | Доп. источник | Код есть, ключ не настроен, юридические риски |
| **Своя база / OSINT** | дорого | Полный контроль | Не для MVP |
| **DeHashed / IntelX** | enterprise $$$ | Широкий dark web | Дорого, compliance |

**Рекомендация для ALADDIN:** сейчас — **пароль бесплатно**; в будущем — **HIBP Core** для email; опционально k-anonymity на клиенте при росте privacy-требований.

---

## Оценка тарифа HIBP Core (когда будет бюджет)

Лимит Core 1: **~10 проверок email в минуту** (600/час, ~14 400/день).

| Сценарий | Сканов/день | Подходит |
|----------|-------------|----------|
| 500 MAU, 1 scan/неделю на пользователя | ~70 | **Core 1** |
| 2 000 MAU, 1 scan/месяц | ~70 | **Core 1** |
| 5 000 MAU, 1 scan/неделю | ~700 | **Core 1–2** |
| 20 000 MAU, 1 scan/неделю | ~2 800 | **Core 3+** |
| Пик: 50 scan/мин в час пик | 50 RPM | **Core 2** (50 RPM) |

Формула: `средние_сканы_в_день = MAU × частота_скана_в_месяц / 30`.  
Пиковый RPM важнее среднего — закладывайте ×3 запас или очередь на сервере.

**Старт:** Core 1 (~$4.39/мес при годовой оплате) — достаточно для раннего prod.

---

## План по фазам (будущее)

### Фаза 0 — сейчас (без затрат) ✅

- [x] Prod truth: per-user stats, scan_events, cleanup legacy
- [x] iOS: нет mock stats, coverage note
- [x] Password: SHA-1 → Pwned Passwords (бесплатно)
- [x] `smoke_dark_web_prod.sh`
- [ ] **E11** iOS smoke на устройстве (ручной)

### Фаза 1 — HIBP email (~$4–40/мес)

1. Оформить [HIBP Core](https://haveibeenpwned.com/Subscription) (Core 1 для старта).
2. Локально: `HIBP_API_KEY='…' ./scripts/configure_hibp_api_key_prod.sh`
3. Smoke: fast scan на тестовый email с утечкой (осторожно с rate limit).
4. Убрать/смягчить `dark_web_coverage_note` в UI.
5. Мониторинг: логировать HTTP 401/429 от HIBP.

### Фаза 2 — качество и privacy

1. **k-anonymity email** на iOS (опционально) — меньше plaintext на сервере.
2. **Очередь сканов** + backoff при 429 HIBP.
3. **Периодический re-scan** (cron): раз в 7 дней для сохранённых email (с согласия).
4. Push родителю при `found: true`.

### Фаза 3 — расширение (по спросу)

1. BreachDirectory как fallback (отдельный ключ + legal review).
2. Phone/SNILS — только при легальном источнике (РФ compliance).
3. Domain monitoring (HIBP Pro) — для корпоративных семей с `@company.ru`.
4. Secure password **на устройстве** (k-anonymity prefix) — сервер не видит даже SHA-1 целиком.

---

## Файлы

| Файл | Назначение |
|------|------------|
| `security/api/dark_web_scan_service.py` | HIBP email + Pwned Passwords |
| `security/api/routers/reports_router.py` | stats, leaks, scan POST |
| `ViewModels/DarkWebMonitoringViewModel.swift` | SHA-1 password, scan UX |
| `scripts/configure_hibp_api_key_prod.sh` | Деплой ключа (фаза 1) |
| `scripts/smoke_dark_web_prod.sh` | Prod smoke |

---

## Решение по умолчанию до бюджета

**Оставить fast scan email в режиме «честные нули»**, активно продвигать **безопасную проверку пароля** (работает бесплатно). Подключить HIBP Core, когда появится ~$5/мес и реальная потребность в email-мониторинге в Premium.
