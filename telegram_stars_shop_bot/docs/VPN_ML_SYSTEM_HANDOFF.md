# VPN Shop + vpn-api — handoff для ML-системы

**Назначение:** один файл, чтобы после прочтения было ясно: **как устроен контур**, **что уже сделано в репозитории**, **что осталось по задачам**, **что выкатывать на прод** и **какой чеклист после деплоя**. Детали метрик и PromQL — в runbook vpn-15.

**Порядок чтения (канон):**

1. `docs/VPN_SHOP_INTEGRATION_PLAN.md` — общий план, §13 (todo), §14 (UX).
2. `docs/VPN_SHOP_API.md` — контракт API (эндпоинты, HMAC, состояния).
3. `docs/VPN_PUBLIC_SURFACE_REGISTRY.md` — публичные URL/порты (обновлять при изменениях).
4. Этот файл — **операционный handoff** и список оставшейся работы.
5. Наблюдаемость vpn-api: **`../aladdin_shop_vpn_api/deploy/VPN15_OBSERVABILITY_RUNBOOK.md`** (от этой папки `docs/`).
6. Единый выкат: **`../aladdin_shop_vpn_api/deploy/VPN17_DEPLOY_RUNBOOK.md`**.

Пути ниже от каталога **`telegram_stars_shop_bot/docs/`**, если не указано иначе.

---

## 1. План после выката на прод (конфиг + наблюдаемость)

Цель: **один каталог локаций**, **инструкции по URL**, **опционально Sentry**, **Prometheus scrape**, **Grafana**.

| Шаг | Действие | Где |
|-----|----------|-----|
| 1 | Убедиться, что на сервере поднята актуальная версия **`aladdin-shop-vpn-api`** (код из репо `aladdin_shop_vpn_api/`) и бота (`telegram_stars_shop_bot/`). | VPS + CI/CD по вашему каналу |
| 2 | В **`shared/.env`** (или env unit) **vpn-api** задать **`VPN_LOCATIONS_JSON`** **точно так же**, как у бота (один JSON — один список стран/локаций). | Файл на сервере vpn-api |
| 3 | У бота в `.env`: **`VPN_INSTRUCTIONS_URL`** = HTTPS на хаб инструкций (рекомендуется `https://aladdin-ai.ru/v1/legal/vpn-instructions` или ваш канонический URL). | `shared/.env` бота |
| 4 | Если каталог строк локаций должен браться **из API**, а не только из JSON в боте: **`VPN_LOCATIONS_FROM_API=true`** (бот дергает HMAC **`GET /internal/v1/locations/catalog`**). | бот `.env` |
| 5 | По желанию на **vpn-api**: **`SENTRY_DSN`**, **`SENTRY_ENVIRONMENT`**, **`SENTRY_TRACES_SAMPLE_RATE`**. | vpn-api `.env` |
| 6 | В **Prometheus** добавить `scrape_config` на **`http://127.0.0.1:8091/metrics`** (job/instance подписать сами). **`/metrics` не выставлять в интернет** без ACL; при необходимости — `aladdin_shop_vpn_api/deploy/nginx_vpn_metrics_allow_local.conf.example`. | Prometheus на той же машине или через SSH tunnel — по политике |
| 7 | В **Grafana**: импорт JSON **`aladdin_shop_vpn_api/deploy/grafana/aladdin_shop_vpn_api_dashboard.json`**, выбрать datasource Prometheus. | Grafana |
| 8 | **`systemctl restart`** (или ваш оркестратор) **vpn-api** и **бота** после правок `.env`. | VPS |

Подробности, PromQL для **p95**, проверка `curl` — **`VPN15_OBSERVABILITY_RUNBOOK.md`** (разделы 1–8, включая повтор пункта про `VPN_LOCATIONS_JSON` / бот).

---

## 2. Что нужно задеплоить (артефакты)

### Из репозитория (код и статика)

| Компонент | Путь в репо | Комментарий |
|-----------|-------------|-------------|
| VPN API (FastAPI) | `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/aladdin_shop_vpn_api/` | Включая `GET /metrics`, `prometheus_client`, middleware, роуты |
| Shop-бот | `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/telegram_stars_shop_bot/` | VPN funnel, `VPN_LOCATIONS_FROM_API`, инструкции |
| Дашборд Grafana | `aladdin_shop_vpn_api/deploy/grafana/aladdin_shop_vpn_api_dashboard.json` | Импорт в UI, не «деплой» как сервис |
| Сниппеты nginx (опционально) | `aladdin_shop_vpn_api/deploy/nginx_vpn_metrics_allow_local.conf.example`, `nginx_vpn_sub_rate_limit_snippet.conf.example` | Вручную в прод-конфиг nginx |

### На сервере (не в git, руками / секрет-хранилище)

- Обновлённые **`shared/.env`** (или split-env) для **vpn-api** и **бота** — см. §1.
- Конфиг **Prometheus** (`scrape_configs`) — см. §1 шаг 6.
- Импорт панелей **Grafana** — §1 шаг 7.

---

## 3. Сделано / осталось

**Полный реестр vpn-00…vpn-40 (✅/🟡/⏳), цепочка оплаты без PII, прод-фиксы 2026-05-16:** см. **`docs/VPN_TASKS_STATUS.md`**.

Кратко: **~32 из 41** ID закрыты на single-node; **vpn-30** (гео вне РФ), **vpn-02-legal**, контент **vpn-38–40**, **vpn-37-peer** — в очереди.

**Идентификация покупателя VPN:** только **Telegram user ID** в `shop.db` → `provision(telegram_user_id)` → кнопки **📥 Файл для подключения** / **📷 QR для подключения** отдают конфиг по ID нажавшего. Телефон и email не собираем.

---

## 4. Осталось сделать (приоритет)

| ID | Задача |
|----|--------|
| **vpn-30-secondary-egress-node** | VPS/IP **вне РФ** — смена гео выхода |
| **vpn-02-legal** | Юрист, финальный legal |
| **vpn-37-locations-api-peer** | Локация → peer/endpoint |
| **vpn-38-instructions-hub-content** | Скриншоты, TV/VR |
| **vpn-34-status-channel-process** | Регулярные посты в канал |
| **vpn-32-external-monitoring** | Cron smoke с внешней сети |
| **vpn-05-xray-reality** | :443, автоген `/sub` |
| **vpn-19**, **vpn-39**, **vpn-40** | По таблице в `VPN_TASKS_STATUS.md` |

Детальная таблица — **`VPN_TASKS_STATUS.md`**, не дублировать здесь.

---

## 5. Как другой агенту продолжить работу

1. Взять задачу из §4 (или уточнить приоритет у владельца продукта).
2. Для API-изменений — обновить **`VPN_SHOP_API.md`** и при необходимости **`VPN_PUBLIC_SURFACE_REGISTRY.md`**.
3. Для серверных шагов — следовать runbook’ам в `aladdin_shop_vpn_api/deploy/` и `docs/VPN34_*`.
4. После значимого выката — пройти **§1 этого файла** (env + metrics + рестарты).

---

## 6. Версия документа

| Дата | Изменение |
|------|-----------|
| 2026-05-14 | Первый handoff: пост-деплой план, что деплоить, сделано/осталось, ссылки на SSOT. |
| 2026-05-15 | В репо: vpn-25 circuit breaker, выдача WG `.conf`/QR в боте, vpn-26 backoff jobs + systemd limits, **VPN17_DEPLOY_RUNBOOK.md**. |
