# Квартальное учение VPN (quarterly-drill)

**Частота:** раз в 3 месяца, с **реального телефона** (мобильный оператор + домашний Wi‑Fi).

**Последний прогон инфраструктуры (сервер):** 2026-05-17 — `vpn_prod_smoke.sh` **10/10 PASS** (ранее 05-15); P1-WG: timer **active** (~60s), `VPN_WG_POST_EXPIRE_SCRIPT` + `wg-peer-down.sh` **OK**, nginx `limit_req` на `/sub/` **OK**.  
**Прогон с телефона:** 2026-05-16 — админы: тест-grant + **📥/📷** + WG **подключается**; **формальная оплата `vpn_30d`** и **Happ на 4G** (шаги 1, 4) — **PENDING** (см. § Drill Happ).

---

## Чеклист

| # | Шаг | Сеть | 2026-05-15 | Примечание |
|---|------|------|------------|------------|
| 1 | Оплата **`vpn_30d`** (**💳 Купить AiMonkeyVPN**) → `vpn_active` | — | **PENDING** | 2026-05-16: только **тест-grant** админам, не боевой checkout |
| 2 | **📥 Файл для подключения** / **📷 QR для подключения** | Wi‑Fi | **OK** | 2026-05-16 админы; после фикса `wg-peer-up.sh` |
| 3 | WG подключается (UDP 51820) | Wi‑Fi | **OK** | Туннель «вкл», трафик на peer; YT/IG с RU IP — не критерий drill |
| 4 | **🔀 Другой способ** → **📋 Запасная ссылка** → приложение **Happ** (VLESS+REALITY `/sub/`) | 4G/LTE | **PENDING** | После оплаты: вставить ссылку в Happ, подключиться; после expire — профиль удалить, ссылка 404 |
| 5 | **🧱 OpenVPN (файл)** из бота | 4G/LTE | **PENDING** | Сервер :1194 **active**; с телефона не проверено |
| 6 | `https://aladdin-ai.ru/v1/legal/vpn-instructions` | браузер | **OK** | HTTP 200 с интернета + VPS |
| 7 | Grafana: панели VPN API за 24 ч | ops | **PARTIAL** | Grafana **active**; дашборд — вручную |
| 8 | Prometheus + Alertmanager → Telegram | ops | **OK** | `prometheus-alertmanager` **active** |
| — | Внешний smoke (vpn-32) | интернет | **OK** | `external_vpn_smoke.sh` + `/sub/…` → 404 |
| — | UFW VPN-порты (vpn-03) | VPS | **OK** | `ufw_vpn_harden.sh`; ispmanager **оставлен** |
| — | Timer smoke 15 min | VPS | **OK** | `aladdin-vpn-prod-smoke.timer` **10/10** |

**Ответственный:** ops / владелец продукта (заполнить ФИО после телефонного прогона).

---

## Журнал (дата, сеть, протокол, результат)

| Дата (UTC+3) | Сеть | Протокол / шаг | Результат | Кто |
|--------------|------|----------------|-----------|-----|
| 2026-05-15 | VPS (автотест) | smoke API + legal + /sub + ovpn/conf | **OK** 10/10 | `vpn_prod_smoke.sh` |
| 2026-05-15 | VPS | WG + Xray + OpenVPN units | **OK** active | systemctl |
| 2026-05-15 | VPS | Alertmanager | **OK** `prometheus-alertmanager` | fix_alertmanager_telegram.py |
| 2026-05-16 | Wi‑Fi | 📥/📷 + WG connect | **OK** | Админы, тест-grant; фикс пути provision script |
| 2026-05-16 | — | Оплата `vpn_30d` end-to-end | **PENDING** | Карта/СБП или USDT как у Stars |
| __________ | 4G/LTE | 📋 Запасная ссылка / Reality | | |
| __________ | 4G/LTE | 🧱 OpenVPN (файл) | | |

---

## Команды для повтора на VPS

```bash
bash /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_prod_smoke.sh
systemctl is-active aladdin-shop-vpn-api aladdin-telegram-bot xray openvpn-server@server prometheus-alertmanager
```

См. также инструкцию пользователя: `aladdin_shop_vpn_api/legal_docs/vpn-instructions.md` (публично: `/v1/legal/vpn-instructions`).

---

## Drill Happ + оплата (4G) — пошагово

**Цель:** закрыть шаги 1 и 4 таблицы с **реального телефона** (не test-grant).

1. **Оплата** — в боте **💳 Купить AiMonkeyVPN** → тариф **`vpn_30d`** (или другой с `vpn_subscription_days` в `products.yaml`). Дождаться `vpn_active` (**🧪 Проверить VPN** — зелёный статус, дата «до …»).
2. **Wi‑Fi (опционально повтор):** **📥 Файл** / **📷 QR** → WireGuard → интернет через туннель.
3. **Отключить Wi‑Fi**, включить **4G/LTE**.
4. **🌐 VPN** → **🔀 Другой способ** → **📋 Запасная ссылка** → скопировать → открыть **Happ** (App Store / Google Play) → добавить подписку по URL → **Подключить**.
5. Проверить трафик (браузер / speedtest). Записать в журнал ниже: дата, оператор, OK/FAIL.
6. **Анти-абуз (после тестового expire):** сдвинуть `paid_until` в прошлое на тестовом аккаунте или дождаться конца срока → через ≤2 мин worker: `vpn_expired`, старая `/sub/` → **404**, WG peer снят. В Happ — **удалить профиль** (текст в боте в напоминаниях).

**Код анти-абуза (2026-05-17):** P0 `/sub/` только при `vpn_active` + `paid_until`; P1 WG+Xray down; P2 ротация `opaque_token` при expire; P3 `sub_access_log` + ops-alert при &gt;120 обращений/ч на hash.
