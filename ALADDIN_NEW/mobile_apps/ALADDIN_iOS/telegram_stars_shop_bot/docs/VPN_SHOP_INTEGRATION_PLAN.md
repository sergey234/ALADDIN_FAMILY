# ALADDIN × Telegram Shop Bot — VPN (WG + Xray/Reality + OpenVPN), **без триала**

**Назначение документа:** единый план для ML/разработки и эксплуатации: что переиспользуем из старого кода, куда класть на сервере, как связать **только** с ботом `@AiMonkeyStars_bot` / `telegram_stars_shop_bot`, пути в репозитории и на проде.

**Связанные документы:**

- Деплой бота, Partner API, systemd: `docs/ML_SYSTEM_HANDOFF_FINAL.md` (§0.5–0.6, §2 канон доставки).
- **Контракт API и auth:** `docs/VPN_SHOP_API.md` (SSOT по эндпоинтам, HMAC, idempotency, состояния, `jobs`).
- **Публичные имена и точки входа (реестр):** `docs/VPN_PUBLIC_SURFACE_REGISTRY.md` — вести в актуальном виде.
- **Список локаций в боте (JSON):** `docs/VPN_LOCATIONS_JSON.md`.
- **Чертёж внешнего хаба инструкций:** `docs/VPN_INSTRUCTIONS_HUB_OUTLINE.md` (полный текст: `aladdin_shop_vpn_api/legal_docs/vpn-instructions.md`, URL `/v1/legal/vpn-instructions`).
- **Канал статуса (процесс):** `docs/VPN34_STATUS_CHANNEL_RUNBOOK.md`.
- **Handoff для ML (после выката, env, Prometheus, список todo):** `docs/VPN_ML_SYSTEM_HANDOFF.md`.

---

## 0) North Star и фазы

### Продуктовая формулировка

- Доступ к VPN **только после оплаты** соответствующего SKU в магазине (**триала нет** — ни в продукте, ни в API, ни в текстах бота).
- **Многоуровневый доступ:** по умолчанию **WireGuard**; если не работает — **VLESS + Reality** (subscription); запасной путь — **OpenVPN**.
- **Не обещаем** «единый динамический VPN+прокси с авто-переключением на устройстве без действий пользователя»: «умное переключение» = **порядок кнопок в боте** + короткие инструкции по ОС; для продвинутых — одна subscription с fallback outbounds (фаза 2+).

### Фазы

| Фаза | Содержание | Явно не входит |
|------|------------|----------------|
| **1 (MVP прод)** | WG на ноде, `aladdin-shop-vpn-api` на loopback, HMAC+nonce+`Idempotency-Key`, отдельный `vpn.db`, очередь `jobs` + воркер, оплата → provision/extend, revoke по `paid_until`, воронка в боте (WG + «не работает?» заглушки под фазу 2), legal/AUP минимум, метрики, liveness/readiness, сценарии «оплатили — peer нет» |
| **2** | Xray Reality, `GET /sub/<opaque_token>`, nginx без логирования секретов |
| **3** | OpenVPN TCP 443, лимиты CPU/сессий |

### Definition of Done (фаза 1)

- Оплаченный SKU создаёт/продлевает entitlement и peer; истечение `paid_until` отключает доступ.
- Нет утечки ключей и полных конфигов в логах; прод без «mock подключён».
- Handoff и runbook позволяют другой ML повторить деплой.

---

## 1. Решение по размещению на сервере (наилучший вариант)

**Не размещать** новый VPN-стек внутри `/opt/aladdin-backend` и не расширять там `app/security/vpn` как «боевой» сервис: смешиваются домены (семья, отчёты, `:8002`), пути в коде уже расходятся (`security/vpn` vs `app/security/vpn`), выше риск инцидентов и путаницы при аудите.

**Рекомендуемая схема (однозначно «для нашего shop-бота»):**

| Роль | Путь на сервере `149.154.65.180` | Назначение |
|------|----------------------------------|------------|
| Shop-бот (как сейчас) | `/opt/aladdin-telegram-shop-bot` | `aiogram`, handlers, вызовы HTTP к VPN-API |
| Partner API (как сейчас) | `/opt/aladdin-telegram-shop-bot/releases/.../current` + unit `aladdin-partner-api.service` (слушает **8090**) | Webhook оплат; постановка **jobs** на VPN (не долгий `wg` в запросе webhook) |
| **Новый** VPN control plane | **`/opt/aladdin-shop-vpn-api`** | Отдельный venv, FastAPI: **оплаченный** доступ, выдача `.conf` / subscription / `.ovpn`, **без** публичного анонимного доступа к control plane |
| **Новый** провижининг (опционально отдельный user) | **`/opt/aladdin-shop-vpn-api/scripts/`** + `sudoers` **только** на `wg-peer-up.sh` / `wg-peer-down.sh` (см. **`VPN13_SECRETS_SUDOERS_RUNBOOK.md`**); `wg-quick`/xray/OpenVPN — отдельные unit под root, не через Python | Узкие обёртки; Python **не** с root и не с широким sudo |
| Конфиги и секреты WG/Xray на ноде | **`/etc/wireguard/`**, **`/usr/local/etc/xray/`** (или выбранный канон), ключи только root | Стандарт ОС; не хранить приватные ключи в git |
| **БД состояния VPN** | **`/opt/aladdin-shop-vpn-api/var/vpn.db`** (рекомендуется) | Не смешивать с `shop.db`; миграции и бэкапы отдельно |
| Логи VPN-API (не смешивать с backend) | **`/var/log/aladdin-shop-vpn-api/`** | Ротация logrotate |
| Systemd | **`/etc/systemd/system/aladdin-shop-vpn-api.service`**, **`aladdin-shop-vpn-worker.service`** / **`.timer`** | `Restart=on-failure`, лимиты рестартов; префикс `aladdin-shop-` |

**Именование в мониторинге и README:** везде использовать префикс **`aladdin-shop-vpn`**.

**Альтернатива (если VPN на отдельной VPS):** тот же каталог **`/opt/aladdin-shop-vpn-api`** на **другом** хосте; бот и Partner API ходят по **HTTPS + mTLS** (или как минимум TLS + сильный shared secret). На основном сервере — только управление, без UDP VPN-трафика при желании.

---

## 2. Что переиспользуем из старого кода (репозиторий + копия на сервере)

### 2.1 В репозитории (источник правды для выборочного переноса)

| Путь в репо | Что пригодится |
|-------------|----------------|
| `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/app/security/vpn/protocols/wireguard_server.py` | Идея: `wg genkey` / `pubkey`, шаблон `[Interface]`/`[Peer]` — **перенести упрощённо** в новый модуль `aladdin-shop-vpn-api`, без Flask и без `sudo` из произвольного кода |
| `.../protocols/openvpn_server.py` | Структура конфигов/клиентов — как **референс** для генерации `.ovpn` |
| `.../protocols/v2ray_client.py` | Только **модели** протоколов (VLESS и т.д.) — не как запущенный клиент |
| `.../docs/legal/` | Черновики юртекстов — после правки юристом |
| Остальной каталог `app/security/vpn/` | Документация, тесты, идеи — **не** подключать целиком к процессу бота |

### 2.2 На прод-сервере (только справка; деплой нового кода — из git)

| Путь на сервере | Содержимое |
|-----------------|------------|
| `/opt/aladdin-backend/app/security/vpn` | **103** `.py` — зеркало старого дерева; **архив/справка** |
| `/root/backup_20260130_122000/backend_backup/security/vpn` | Бэкап копия |
| `/root/backup_20260130_122000/sfm_backup/security/vpn` | Бэкап копия |

**Важно:** пути вида `/opt/aladdin-backend/security/vpn/logs/...` на машине **отсутствуют** — **устаревшие** ссылки. Новый стек не повторять.

---

## 3. Интеграция с ботом (воронка и оплата)

| Компонент | Путь в репо | Действие |
|-----------|-------------|----------|
| Handlers VPN | `telegram_stars_shop_bot/bot/handlers/vpn.py` | **`nav:vpn`**, **`/vpn`**; колбэки **`vpn:*`**: выбор ОС, WG, кнопки «Не работает WG? → Reality / OpenVPN» (по мере фаз) |
| Клавиатура | `telegram_stars_shop_bot/bot/keyboards/shop_kb.py` → **`hub_menu_kb`** | Строка **«🌐 VPN»** при `UI_SHOW_VPN` |
| Конфиг | `telegram_stars_shop_bot/bot/config.py` + **`bot/main.py`** | `ui_show_vpn`, `vpn_api_base_url`, `vpn_api_hmac_secret` |
| Оплата | `partner_api/...` + webhooks + `bot/handlers/shop.py` (баланс / mix) + `bot/handlers/admin.py` | При **`paid`**: идемпотентно **`POST /internal/v1/provision`** (SKU `kind: vpn`, `vpn_subscription_days` в YAML); внешние webhooks не держат `wg` — только постановка job в VPN-API (**`vpn-11`**) |
| Лендинг реф | `partner_api/routers/vpn_ref_landing.py` | **`GET /r/{code}`** → **302** на `https://t.me/{SHOP_BOT_USERNAME}?start=r-{code}`; нужен **`SHOP_BOT_USERNAME`** (**`vpn-12`**) |
| Документация | `docs/ML_SYSTEM_HANDOFF_FINAL.md` §0.5–0.6 | Продуктовая строка VPN |

**UX:** многоуровневый доступ через кнопки и инструкции; опционально QR для WG (ранний UX-win после стабильной выдачи `.conf`).

---

## 4. Протоколы и модель доступа (без триала)

- **По умолчанию:** WireGuard peer на **оплаченный** период (`paid_until`).
- **Запасной 1:** Xray VLESS + Reality — выдача subscription через **`GET /sub/<opaque_token>`** (без query в URL; логи off/masked).
- **Запасной 2:** OpenVPN `.ovpn` (фаза 3).
- **Воркер:** по расписанию отключает peer при `now > paid_until` (и политика grace — если введёте, зафиксировать в оферте); продление только из **оплаченного** webhook.

---

## 5. Минимизация данных, абуз и legal

- **Идентификатор:** `telegram_user_id` для выдачи в боте и связи с `vpn_account_id`; с legal согласовать формулировку «минимальный набор данных» vs «не собираем ПДн».
- **Один активный entitlement VPN на `telegram_user_id`** (или явное правило «один WG peer на пользователя» + лимиты сессий OVPN).
- **Rate limits** на edge (nginx `limit_req`) и в приложении на выдачу конфигов / `GET /sub/...`; IP — не хранить долго или хранить обезличенно/коротко — по политике с legal.
- **AUP:** запрет спама, вредоноса, botnet — в оферте; снижает риск хостера.
- **Channel gate** (уже в магазине): при необходимости ограничить доступ к разделу VPN подпиской на канал.
- **Не логировать:** полные конфиги, длинные query с секретами, plaintext ключи; не хранить историю сайтов / DPI-метаданные, если не нужны.
- **Поведенческие сигналы:** частые revoke/rotate → флаг для ручной модерации.

---

## 6. Автоматизация при сбоях (слоями)

**Инфра:** `systemd` `Restart=on-failure`, лимиты рестартов; отдельный **timer** для воркера revoke/sync; **liveness** vs **readiness** (процесс vs `wg0`, маршрут, DNS с ноды, при фазе 2 — порт Xray); nginx/firewall — только нужные порты; при падении TLS — **алерт**, не тихий деград.

**Прикладной уровень:** таблица **`jobs`** (`provision`, `extend`, `revoke`, `rotate_url`) + воркер с **backoff** и **идемпотентностью** по `payment_event_id` / `order_id`; **ретраи** на временные ошибки; **circuit breaker** или пауза + алерт при серии 5xx к vpn-api; при `paid` и незавершённом провижининге — статусы **`vpn_provisioning` / `vpn_failed` / `vpn_manual_override`** (см. `VPN_SHOP_API.md`).

### 6.1 Устойчивость к блокировкам и «план B» (максимум из разумного)

**Зачем вторая нода (`vpn-30-secondary-egress-node`):** основной IP/подсеть могут внести в блок-лист или «положить» фильтрами. Тогда **все пользователи на одном адресе** теряют доступ сразу. **Вторая egress-нода** — отдельный сервер с **другим IP** (желательно **другой ASN / другой хостер или регион**): пользователь в боте выбирает **«Профиль A / Профиль B»** или получает конфиг с **запасным Endpoint**. Control plane может остаться один на основном хосте, а peer’ы подниматься на двух нодах — архитектуру зафиксировать при реализации `vpn-30`.

**Реестр публичной поверхности (`vpn-29-public-surface-registry`):** один файл **`docs/VPN_PUBLIC_SURFACE_REGISTRY.md`** — все домены, вебхуки, будущий URL подписки, лендинг `/r`, кто владелец DNS/TLS. Без этого при инциденте теряется время на «что вообще светится наружу».

**Классификация инцидентов (белая шляпа):** в постмортеме фиксировать тип: **IP**, **UDP**, **DPI**, **DNS**, **хостер/жалоба** — иначе улучшения вслепую.

**Внешний мониторинг (`vpn-32-external-monitoring`):** проверки **не с того же сервера**, что VPN (Uptime Kuma, HetrixTools, cron с другой сети): HTTPS Partner `:8090`/health через публичный домен, при наличии — TCP/UDP до VPN-портов. Это не заменяет **ручную проверку с телефона** (МТС/домашний Wi‑Fi), но ловит массовые отвалы.

**Канал статуса (`vpn-34-status-channel-process`):** отдельный Telegram-канал или закреп: «всё ок / деградация / что сделать пользователю»; шаблон поста + ответственный. Снижает нагрузку на саппорт.

**Учения раз в квартал:** с реального телефона — цепочка WG → Reality → OVPN; занести в календарь и в runbook.

### 6.2 Плейбук инцидента: блокировка или массовая недоступность (`vpn-33-blocklist-incident-playbook`)

Включить в **`vpn-17-deploy`** / `RUNBOOK` отдельным подразделом (задача **`vpn-33`** — выделить и заполнить):

1. Подтвердить симптом: только VPN, или упал весь хост / только один протокол / только один оператор.  
2. Свериться с **`VPN_PUBLIC_SURFACE_REGISTRY.md`**: что могло попасть под блок (домен, IP, порт).  
3. Внутренние проверки: `systemctl`, `wg`, лог vpn-api, длина очереди `jobs`, метрики **`vpn-15`**.  
4. Меры: смена IP (у хостера), переключение трафика на **ноду B**, смена публичного домена подписки (если применимо), обновление конфигов/инструкций в боте.  
5. Коммуникация: пост в канале статуса, при необходимости рассылка/экран в боте.  
6. Постмортем: тег типа блокировки + даты в реестре.

### 6.3 Админка: статистика VPN (`vpn-31-admin-vpn-stats`)

После появления **`vpn.db`**: в **`/admin`** (рядом с существующим дашбордом через `admin_stats_repo`) — блок **VPN**: активные peer, `vpn_failed` / очередь `jobs`, p95 provision, revoke/rotate за период, ошибки по классу (WG/API/timeout). Без вывода полных конфигов и секретов; `telegram_user_id` — по политике саппорта.

### 6.4 VPN-рефералка (как у Щука: `start=r-{code}`) — **`vpn-36-vpn-referral-days`**

**Цель:** отдельно от ₽-рефки магазина — бонус **в днях подписки** после **первой выданной** (`completed`) покупки VPN у приглашённого; тот же короткий код на сайте (**`vpn-12`**: `/r/{code}` → `t.me/bot?start=r-{code}`).

**Реализовано в репо (каркас):**

| Слой | Что |
|------|-----|
| **shop.db** | `vpn_referral_codes` (user_id ↔ code), `vpn_referral_grants` (идемпотентно: один бонус на `referred_user_id` за жизнь) |
| **Бот** | `/start` с `r-` и `r_` + привязка `referrer_id`; профиль / «Рефералка» / VPN — ссылка и счётчики; после `apply_completed_side_effects` — запись гранта + HTTP к VPN API |
| **Аналитика** | `vpn_ref_link_open` — вход по deep link (для конверсии в `/admin`) |
| **VPN API** | `POST /internal/v1/add-subscription-days` — `max(now, paid_until) + N` дней, upsert аккаунта, job `extend` |
| **Конфиг** | `VPN_REFERRAL_REFERRER_DAYS` (дефолт 14), `VPN_REFERRAL_FRIEND_DAYS` (дефолт 7) — согласовать с продуктом |

**Триггер:** заказ `completed`, `product_kind = vpn` **или** `product_id` с префиксом `vpn`, первая такая выдача у пользователя, в заказе есть `referrer_id`. Без триала — только после выдачи.

**В репо:** SKU **`vpn_30d`** (`kind: vpn`, дни из YAML) + **`vpn-11`** — все пути в **`paid`** (webhooks, админ, оплата с баланса, mix «всё с баланса») вызывают provision; **`vpn-12`** — **`/r/{code}`** на Partner API. **На проде** — выставить **`SHOP_BOT_USERNAME`**, задеплоить роутер и проверить редирект.

---

## 7. WireGuard / Xray / OpenVPN (жёсткие решения)

- **WG:** для MVP зафиксировать **IPv4-only** или dual-stack; **MTU** 1280–1420 в клиентском шаблоне; **DNS** 1–2 резолвера, политика «не логируем DNS-запросы» — согласовать с legal; runbook **ротации server key**; кнопка «Сбросить ключ» = revoke старого peer + новый.
- **Xray:** канон пути конфига; обновление с **checksum** и rollback; в логах **не** полный inbound и не UUID в plaintext на WARN.
- **OpenVPN:** **TCP 443**; **tls-crypt**; **CRL или revoke-скрипт**; срок сертификата связан с `paid_until` (+ grace отдельным полем при необходимости); лимит одновременных сессий / только fallback.

---

## 8. Чеклист «готово на сервере»

- [ ] **`/opt/aladdin-shop-vpn-api`** + venv + `requirements.txt`
- [ ] **`aladdin-shop-vpn-api.service`**; bind **127.0.0.1** или TLS+ACL наружу
- [ ] **WG** (фаза 1); Xray/OVPN — по фазам
- [ ] **`vpn.db`** и бэкап-регламент
- [ ] Секреты в **`ROOT/shared/.env`** для вызова API только ботом/partner_api
- [ ] Документация: VPN магазина **≠** `/opt/aladdin-backend`

---

## 9. История версий плана

| Дата | Изменение |
|------|-----------|
| 2026-05-13 | Первый выпуск |
| 2026-05-14 | **VPN-рефералка §6.4:** shop.db, `r-`/`r_` /start, `add-subscription-days`, админ-метрики; todo **vpn-36** (каркас) |
| 2026-05-16 | Каркас `aladdin_shop_vpn_api/` в репо: схема `vpn.db`, API, воркер, примеры systemd, тесты. Дополнительно: **`vpn-11`** (provision после `paid`, включая баланс), **`vpn-12`** (`GET /r/{code}`), env **`VPN_WG_POST_PROVISION_SCRIPT`** для моста к **`vpn-04`**. |

---

## 10. Уже сделано (UI и конфиг бота)

| Область | Файлы / артефакты | Суть |
|---------|-------------------|------|
| Документация и границы | этот файл, `ML_SYSTEM_HANDOFF_FINAL.md` §0.5–0.6 | Пути **`/opt/aladdin-shop-vpn-api`**, не смешивать с **`/opt/aladdin-backend`** |
| SSOT API (черновик) | `docs/VPN_SHOP_API.md` | Auth, idempotency, jobs, состояния |
| **Каркас `aladdin-shop-vpn-api` в репо** | `aladdin_shop_vpn_api/` | SQLite `vpn.db`, HMAC, `POST /internal/v1/provision|extend|revoke`, воркер, тесты; реальный **`wg set`** на ноде — **`vpn-04`**; опционально **`VPN_WG_POST_PROVISION_SCRIPT`** (вызывается воркером после успешного stub-provision с `argv[1]=telegram_user_id`) — мост к shell/sudoers на сервере |
| **Оплата → VPN (`vpn-11`)** | `bot/services/vpn_payment_hook.py`, `vpn_api_client.post_provision`, webhooks `partner_api`, `shop.py`, `admin.py` | Idempotency **`shop-vpn-prov:{order_id}`** |
| **Лендинг (`vpn-12`)** | `partner_api/routers/vpn_ref_landing.py`, `partner_api/main.py` | **`/r/{code}`** без префикса `/v1` |
| Шаблон env | `env.example` | `UI_SHOW_VPN`, `VPN_API_BASE_URL`, `VPN_API_HMAC_SECRET` |
| Настройки бота | `bot/config.py` | Те же поля |
| Главное меню | `bot/keyboards/shop_kb.py` | «🌐 VPN» при `UI_SHOW_VPN` |
| Модуль VPN в боте | `bot/handlers/vpn.py`, `bot/main.py` | Вводный экран **без триала**; `/vpn` в меню при включённом VPN; **VPN-реф. ссылка** `r-{code}` |
| **VPN-рефералка** | `vpn_referral_repo.py`, `vpn_referral_extensions.py`, `vpn_api_client.py`, `order_flow.py`, `common.py`, `hub.py`, `admin_stats_repo.py` | `shop.db`, гранты, `/start r-`, дашборд `/admin`, вызов **`add-subscription-days`** |
| Тесты | `pytest tests/` | Зелёный прогон |

**На проде (2026-05-14):** `aladdin-shop-vpn-api` в **`/opt/aladdin-shop-vpn-api`** выкатан (systemd **active**); WireGuard/Xray — по runbook’ам **`VPN04`** / **`VPN05`** на хосте (проверка: `8091/ready`, `wg show`). Бот: релиз **`20260514-143345`**, админ-VPN — **`VPN14`**.

---

## 11. Осталось сделать — порядок

1. Legal + AUP + минимизация данных (параллельно инфра).  
2. Инфра VPS, UFW, TLS.  
3. **`vpn-18`** + **`vpn-04`** (WG) + черновик **`vpn-07`** / **`vpn-08`**.  
4. Очередь jobs, воркер, состояния оплаты↔VPN.  
5. Воронка `vpn:*` в боте (WG + кнопки fallback по фазам).  
6. SKU и webhooks → VPN-API.  
7. Лендинг `/r/{code}` при необходимости.  
8. Саппорт, observability, тесты, RUNBOOK.  
9. **`vpn-29`** реестр публичных имён; параллельно планировать **`vpn-30`** (вторая нода) после стабильного MVP.  
10. **`vpn-32`** внешний мониторинг; **`vpn-33`** плейбук блокировки; **`vpn-34`** канал статуса.  
11. **`vpn-31`** блок VPN в `/admin` после `vpn-07`.

**Следующий шаг:** **`vpn-02-legal`** или **`vpn-03-infra-vps`** → **`vpn-18-server-tree`** + **`vpn-04-wg-server`** + **`vpn-07-db-schema`** / **`vpn-08-api-service`**.

---

## 12. Важно при реализации

| Тема | Почему |
|------|--------|
| Не тащить весь `app/security/vpn` в процесс бота | Лишние зависимости; провижининг — отдельный сервис |
| Секреты не в git | Ключи только на сервере |
| Идемпотентность webhooks | Повтор не удваивает срок и не плодит peer |
| Доступ только после оплаты | Нет триала — меньше абуза; контроль через `paid_until` |
| Логи без секретов | Sentry/nginx |
| Channel gate | По необходимости |
| Прод без mock | Не «подключено», если peer не создан |
| Старые пути `.../security/vpn` | Не повторять |

---

## 13. Cursor Todo — выполнено и ожидает

**Актуальная таблица всех vpn-00…vpn-40:** **`docs/VPN_TASKS_STATUS.md`** (обновляется при каждом значимом выкате).

**Выполнено (репо + прод на `149.154.65.180`, 2026-05-16):**  
`vpn-00` … `vpn-18`, `vpn-20` … `vpn-28`, `vpn-31`, `vpn-36`, `vpn-37` (UI + catalog API), `vpn-38` (хаб URL), **`vpn-02`** (черновики legal), **`vpn-03`** (nginx + UFW VPN-портов), **`vpn-04`** (WG+NAT+hooks+`POST /wg/conf`; фикс пути `VPN_WG_POST_PROVISION_SCRIPT` → `deploy/scripts/wg-peer-up.sh`), **`vpn-05`** (REALITY :8443 + `/sub`), **`vpn-06`** (OpenVPN :1194 на VPS), **`vpn-09`**, **`vpn-10`** (📥 **Файл для подключения** / 📷 **QR для подключения**, fallback, `vpn:os:*`; без авто-push файла после оплаты), **`vpn-11`**, **`vpn-12`**, **`vpn-13`**, **`vpn-14`**, **`vpn-15`**, **`vpn-16`**, **`vpn-17`** (выкат по runbook), **`vpn-23`** (`limit_req` на прод-nginx), **`vpn-25`**, **`vpn-26`**, **`vpn-27`**, **`vpn-33`** (плейбук), **`vpn-34`** (runbook канала), частично **`vpn-29`**, **`vpn-32`** (скрипт smoke).  
Бренд **AiMonkeyVPN**, UX v2 (🟢 **➡️ Оплата и документы**, отдельные строки 📥/📷), `VPN_INSTRUCTIONS_URL` на проде.

**Оплата → пользователь (без телефона/email):** заказ `shop.db.user_id` = Telegram ID → webhook `paid` → `vpn_payment_hook` → `POST /provision` с тем же `telegram_user_id` → 📥/📷 по `cb.from_user.id`. Подробно: **`VPN_TASKS_STATUS.md`** § «Оплата и пользователь».

**Ожидает:**

| ID | Задача | На что обратить внимание |
|----|--------|-------------------------|
| **vpn-02-legal** | Юрист: возраст/гео, финальный текст, согласование с логами | Черновики: `aladdin_shop_vpn_api/.../legal_docs/*.md` |
| **vpn-03-infra-vps** | Сузить UFW (legacy ispmanager/mail) | Только вручную, риск панели |
| **vpn-05-xray-reality** | 443 / полный автоген `/sub` без ручного файла | :8443 уже на проде |
| **vpn-19-code-extract** | Идеи из `protocols/` | Не legacy целиком |
| **vpn-22-ssot-api-md** | Поддерживать **`VPN_SHOP_API.md`** | При каждом изменении API |
| **vpn-29-public-surface-registry** | Вести **`VPN_PUBLIC_SURFACE_REGISTRY.md`** | При новых URL |
| **vpn-30-secondary-egress-node** | **Вторая нода / IP вне РФ** | Гео для Meta/YouTube; см. `VPN30_SINGLE_NODE_MAX.md` |
| **vpn-32-external-monitoring** | Cron smoke с **внешней** сети | Скрипт в репо есть |
| **vpn-34-status-channel-process** | Регулярные посты в канал статуса | Runbook готов |
| **vpn-37-locations-api-peer** | Локация в UI → peer/endpoint | Каталог строк уже есть |
| **vpn-38-instructions-hub-content** | Скриншоты, TV/VR в `vpn-instructions.md` | |
| **vpn-39-webapp-optional** | Mini App | |
| **vpn-40-landing-welcome-strip** | CTA на лендинге | |
| *(backlog)* | Авто-отправка 📥 после оплаты; замер скорости/«Проверить VPN» в боте | Продуктовый UX |

---

## 14. Гибрид UX (как у Щука по смыслу) — план + статус

**Идея:** в чате — короткие действия и «гармошка» списка стран через `edit_message_text`; длинные гайды (TV, VR, белые списки, скриншоты) — на **внешней странице** (Teletype / свой домен / позже Web App).

| Задача | Где | Статус в коде |
|--------|-----|----------------|
| Короткий / полный список стран, кнопки «Показать все» / «Свернуть» | Бот: `vpn:loc:*`, `edit_text` | **Сделано:** `bot/handlers/vpn.py` + **`VPN_LOCATIONS_JSON`** / **`VPN_LOCATIONS_PREVIEW_N`** (см. `docs/VPN_LOCATIONS_JSON.md`) |
| Кнопка «Полная инструкция (сайт)» | URL из `.env` | **Сделано:** `VPN_INSTRUCTIONS_URL` (fallback: `VPN_MARKETING_LANDING_URL`) |
| Кнопка «🌏 Локации (обзор)» на экране настройки VPN | `_vpn_root_kb` | **Сделано** |
| Список стран из **VPN API** `GET /internal/v1/locations/catalog` | vpn-api + бот `VPN_LOCATIONS_FROM_API` | **Сделано** (кэш 60 с в боте; выбор peer по строке — **не** в этом инкременте) |
| Контент хаба инструкций | `GET /v1/legal/vpn-instructions` (`legal_docs/vpn-instructions.md`) | **Сделано** (редактирование контента — по мере продукта) |
| Telegram Web App вместо внешнего URL | Опционально | **vpn-39-webapp-optional** |
| Приветствие на внешней странице (2 строки + CTA) | Лендинг / Teletype | **vpn-40-landing-welcome-strip** |
| Канал статуса (отдельно от магазина) | Процесс + `VPN_NEWS_CHANNEL_URL` | **Runbook:** `docs/VPN34_STATUS_CHANNEL_RUNBOOK.md` (посты — вручную) |

**Колбэки локаций:** `vpn:loc:open` (новое сообщение), `vpn:loc:short` / `vpn:loc:full` (переключение того же сообщения), `vpn:loc:dismiss` (удалить сообщение бота), `vpn:instr:url:none` (alert, если URL не задан).

### Что из чата ещё не автоматизировано в коде (остаётся в todo)

См. **`docs/VPN_TASKS_STATUS.md`** (актуально на 2026-05-16).

- **Авто-отправка 📥** сразу после оплаты (сейчас пользователь жмёт кнопку сам).
- **Замер скорости / «Проверить VPN»** в боте (сейчас — fast.com вручную).
- **Юрист / гео** — **vpn-02-legal**, **vpn-30** (нода вне РФ).
- **Локация → peer/endpoint** — **vpn-37-locations-api-peer**.

**Реестр публичных поверхностей:** при появлении новых URL (инструкции, Web App) обновить **`docs/VPN_PUBLIC_SURFACE_REGISTRY.md`** (**vpn-29**).