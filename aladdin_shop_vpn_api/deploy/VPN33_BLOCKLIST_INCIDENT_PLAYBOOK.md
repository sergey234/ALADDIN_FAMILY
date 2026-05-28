# VPN33 — плейбук: блокировка IP / массовая недоступность

**Когда:** пользователи массово не подключаются; один оператор / один регион / один протокол.

## 1. Подтвердить симптом (5–10 мин)

| Вопрос | Действие |
|--------|----------|
| Только VPN или весь хост? | `curl` `:8002/health`, `:8090/health`, `:8091/health` на сервере |
| Только WG / только Reality / только OVPN? | Проверка с **двух сетей** (мобильный + домашний Wi‑Fi) |
| Только один оператор? | Спросить 2–3 пользователей из разных сетей |

## 2. Реестр и метрики

1. `docs/VPN_PUBLIC_SURFACE_REGISTRY.md` — какие IP/домены/порты светятся наружу.
2. Grafana **ALADDIN Shop VPN API** — `jobs_failed`, `vpn_failed`, p95, 5xx.
3. Prometheus alerts → Telegram: `AladdinShopVpnApiDown`, `AladdinShopVpnJobsFailed`.
4. `systemctl status aladdin-shop-vpn-api`, `wg show`, очередь `jobs` в `vpn.db`.

## 3. Меры (по приоритету)

1. **Инфра на месте:** рестарт `aladdin-shop-vpn-api`, воркер timer, `wg-quick@wg0`, Xray unit — по runbook VPN04/VPN05.
2. **Только один IP, WG недоступен, IP ещё жив:** переключить пользователей на **Профиль B** (не «другая страна»):
   - REALITY TCP **8443** + подписка `https://…/sub/<opaque>` (кнопки в боте «Не работает WireGuard?»);
   - OpenVPN UDP **1194** (`.ovpn` через API/бот после выката).
   - См. **`deploy/VPN30_SINGLE_NODE_MAX.md`**.
3. **Смена IP** у хостера (основной VPS) + обновить `VPN_WG_ENDPOINT_HOST`, `VPN_EGRESS_NODES_JSON`, Xray/Reality в реестре, бот.
4. **Второй IPv4 на той же VM** (если хостер даёт) — ~50% ценности vpn-30 без второй машины; повесить WG/Reality на новый IP.
5. **Нода B (вторая VPS)** (**vpn-30**): `VPN_EGRESS_NODES_JSON` → `secondary.active=true`, новый `wg_host`.
6. **Домен подписки** `/sub/…` — если блокируют SNI/домен, временный канонический домен + nginx.
7. **Коммуникация:** пост в канал статуса (**VPN34**), при необходимости экран в боте.

## 4. Постмортем (шаблон)

- Дата/время UTC  
- Тип: `IP` | `UDP` | `DPI` | `DNS` | `хостер/жалоба`  
- Затронутые URL/IP из реестра  
- Что сработало (смена IP / нода B / только Reality)  
- Задачи в backlog (vpn-05, vpn-30, vpn-23, …)

См. также **VPN17_DEPLOY_RUNBOOK.md** §8.
