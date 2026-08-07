# Реестр публичной поверхности (Shop + VPN)

**Назначение:** один список всего, что видно из интернета или у партнёров: домены, URL, порты, владельцы. Обновлять при каждом изменении DNS/TLS/хостера. Связано с **`VPN_SHOP_INTEGRATION_PLAN.md`** §6.1 и инцидент-плейбуком **`vpn-33`**.

**Задача в Cursor:** `vpn-29-public-surface-registry`.

**Одна нода (максимум):** `aladdin_shop_vpn_api/deploy/VPN30_SINGLE_NODE_MAX.md` — Профиль A/B без второго IP.

---

## Как пользоваться при инциденте «не коннектится / блокировка»

1. Открыть эту таблицу.  
2. Отметить, какой ряд затронут (домен, IP, порт).  
3. В постмортеме указать тип: **IP** / **UDP** / **DPI** / **DNS** / **хостер**.

---

## Профили (после миграции 2026-06-25)

| Роль | Хост | IP |
|------|------|-----|
| **HTTPS / iOS / webhooks** | `aladdin-ai.ru` | `149.154.65.180` (MAIN, nginx proxy) |
| **Shop + VPN runtime** | Contabo EU | `185.225.233.150` |
| **WireGuard / Xray / OpenVPN endpoint** | `vpn.aladdin-ai.ru` | `185.225.233.150` (Contabo) |

| Профиль | Протокол | Порт | Примечание |
|---------|----------|------|------------|
| **A** | WireGuard | UDP **443** | Endpoint = `VPN_WG_ENDPOINT_HOST` → `vpn.aladdin-ai.ru` |
| **B** (транспорт) | VLESS + REALITY (Xray) | TCP **8443** | `VPN_XRAY_PUBLIC_HOST=vpn.aladdin-ai.ru`; подписка HTTPS **443** → MAIN nginx → Contabo `/sub/<opaque>` |
| **B** (транспорт) | OpenVPN | UDP **1194** + TCP **443** | `openvpn-server@server` (UDP), `openvpn-server@server-tcp` (TCP 443, **2026-06-27**) |

При **блокировке всего IP** — смена IP у хостера Contabo, или вторая VPS (`VPN_EGRESS_NODES_JSON` → `secondary`).

---

## Таблица (фактические значения, нода A)

| Имя / сервис | URL или хост | Порт / протокол | TLS / сертификат | Владелец (роль) | Примечание |
|--------------|--------------|------------------|------------------|-----------------|------------|
| Partner API (публичный) | `https://aladdin-ai.ru` (и др.) | 443 → MAIN nginx → **185.225.233.150:8090** | TLS | Partner API (Contabo) | Вебхуки оплат |
| Webhook Ckassa / LAVA / Crypto / xRocket | … | | | | См. `CRYPTO_PAY_SPEC.md` |
| Лендинг реф `/r/{code}` | `https://<partner-host>/r/{code}` | GET 443 | TLS | Partner API | **302** → `t.me/<SHOP_BOT_USERNAME>?start=r-{code}` |
| VPN legal (markdown) | `https://aladdin-ai.ru/v1/legal/vpn-terms` (+ `vpn-aup`, `vpn-data`, **`vpn-instructions`**) | GET 443 | TLS | MAIN nginx → **185.225.233.150:8091** | Префикс `/v1/legal/vpn-*` |
| VPN subscription (Reality) | `https://aladdin-ai.ru/sub/<opaque>` | GET 443 | TLS | MAIN nginx → **185.225.233.150:8091** | Тело: `VPN_SUBSCRIBE_VLESS_TEMPLATE`; Xray **8443** TCP на Contabo |
| VPN subscription **mirror** | `https://subs.aladdin-ai.com/sub/<opaque>` | GET 443 | TLS (CF or LE) | MAIN nginx → **185.225.233.150:8091** | **vpn-domain-com** — только Update подписки |
| VPN WireGuard (Профиль A) | **`vpn.aladdin-ai.ru`** | UDP **443** | n/a | wg0 (Contabo) | `VPN_WG_LISTEN_PORT=443` |
| Xray VLESS+REALITY (Профиль B) | **`vpn.aladdin-ai.ru`** | TCP **8443** | REALITY (Microsoft SNI) | xray.service (Contabo) | Ключи `/opt/xray/` |
| VPN OpenVPN (Профиль B) | **`vpn.aladdin-ai.ru`** | UDP **1194**, TCP **443** | tls-crypt + CRL | `openvpn-server@server`, `openvpn-server@server-tcp` | Per-user `.ovpn` (TCP 443 first) via `POST /internal/v1/ovpn/conf` |
| **Нода B (вторая VPS)** | `VPN_EGRESS_NODES_JSON` → `secondary` | … | | | `active: false` до появления хоста |
| Prometheus scrape (vpn-api) | `http://127.0.0.1:8091/metrics` | loopback | n/a | ops | `VPN15_OBSERVABILITY_RUNBOOK.md` |
| Канал статуса VPN/магазина | `t.me/…` | — | — | | `VPN34_STATUS_CHANNEL_RUNBOOK.md` |
| Бэкап `vpn.db` | `/var/backups/aladdin-shop-vpn/` (пример) | — | — | root | `VPN13_SECRETS_SUDOERS_RUNBOOK.md` |
| Внешний мониторинг | cron + `external_vpn_smoke.sh` | — | — | | `VPN32_EXTERNAL_MONITORING_RUNBOOK.md` |
| Хаб инструкций | `VPN_INSTRUCTIONS_URL` → `…/v1/legal/vpn-instructions` | GET 443 | TLS | | `legal_docs/vpn-instructions.md` |
| Локации в боте | `VPN_LOCATIONS_JSON` / API catalog | — | — | Shop-бот | `vpn:loc:*` |

---

## История изменений

| Дата | Что изменилось |
|------|----------------|
| 2026-05-15 | **vpn-06:** OpenVPN UDP **1194** active; `openvpn-install.sh`, per-user `openvpn-client-issue.sh`, UFW |
| 2026-05-16 | Бот: авто-📥 после оплаты; `vpn:check`; инструкции + шаблоны постов vpn-34 |
| 2026-05-16 | WG client: только `AllowedIPs 0.0.0.0/0` (без IPv6 до форвардинга v6) |
| 2026-05-15 | **vpn-30 single-node:** `VPN30_SINGLE_NODE_MAX.md`, Профиль A/B в реестре, `VPN_EGRESS_NODES_JSON`, генератор `/sub`, MTU в WG |
| 2026-05-14 | **vpn-15:** Prometheus `/metrics`, Grafana, Alertmanager Telegram |
| 2026-05-14 | **vpn-14** admin `/admin_vpn*`; **vpn-13** sudoers/backup |
| 2026-05-14 | **vpn-06** OpenVPN runbook; **vpn-10** бот fallback |
| 2026-05-14 | **vpn-03** nginx `/sub/`, legal; **vpn-05** xray :8443 |
| 2026-06-25 | **Миграция Shop+VPN на Contabo** `185.225.233.150`; MAIN nginx proxy `/v1/`, `/sub/`, `/v1/legal/vpn-*`; endpoint `vpn.aladdin-ai.ru` |
| 2026-06-27 | **OpenVPN TCP 443** (`openvpn-server@server-tcp`); dual `<connection>` в `.ovpn`; UX handoff **`VPN_FULL_SESSION_HANDOFF_ML_2026-06-27.md`** |
