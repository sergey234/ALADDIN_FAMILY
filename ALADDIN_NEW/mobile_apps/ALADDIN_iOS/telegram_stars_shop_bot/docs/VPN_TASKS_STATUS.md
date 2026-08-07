# VPN — реестр задач (vpn-00 … vpn-40) и статус

**Обновлено:** 2026-06-28 (инцидент REALITY dest ✅; UFW OVPN ✅; HitWave кнопки ✅; E2E xray PASS)  
**Устойчивость 4G+Wi‑Fi:** `VPN_RESILIENT_ARCHITECTURE_PLAN_2026.md` (**v7.1**) · **Инвесторы:** `VPN_INVESTOR_BRIEF_2026.md`  
**Cursor TODO SSOT:** `.cursor/VPN_RESILIENT_TASK_REGISTRY.md` (`vpn-r00`…`vpn-r59`, **55** + **5 incident** + **vpn-dns**)

## Исключено по решению продукта (не в этом спринте)

| ID | Причина |
|----|---------|
| **vpn-30** | Вторая нода / IP вне РФ — отдельный заказ хостера |
| **vpn-02-legal** | → перенесено в **vpn-77** (legal полный) |
| **vpn-39** | Mini App |

---

## Сводка

| | |
|--|--|
| **Готово (single-node)** | **~95%** техники + UX |
| **Осталось** | **6** Cursor ⏳ + **G4 phone drill** + legal sign + CDN ф1/ф3 |

---

## Инцидент 2026-06-28 — доработки после аудита

| ID | Задача | Статус |
|----|--------|--------|
| vpn-96 | REALITY `dest` microsoft → **cloudflare** (Contabo :8443, bridge :8444, hop SNI); Xray 26.3 RSA handshake fail | ✅ E2E PASS |
| vpn-97 | UFW forward return **tun0/tun1** (`deploy/scripts/ovpn-fix-forwarding.sh`) | ✅ Contabo |
| vpn-98 | Бот: кнопки **HitWave (мост)** / **HitWave (Wi‑Fi)** — `vless://` отдельно от `/sub/` | ✅ 20260628-161604 |
| vpn-99 | xhttp `mode: stream-one` inbounds + bridge hop outbound | ✅ |
| vpn-100 | env `/sub/` SNI sync (`VPN_XRAY_REALITY_SNI`, `VPN_BRIDGE_REALITY_SNI` → cloudflare) | ✅ |

### Причины плохой работы VPN (полный список)

1. **P0 REALITY dest microsoft.com** — Xray 26.3 не завершает handshake с RSA-сертификатом Microsoft; data channel мёртв при «открытом» TCP :8443.
2. **P0 Ложный smoke PASS** — cron проверял только TCP, не VLESS+REALITY+XHTTP end-to-end.
3. **P1 UFW OpenVPN** — return traffic на tun1 блокировался; асимметрия BYTES_OUT >> BYTES_IN.
4. **P1 OpenVPN TCP 443** — TCP-over-TCP meltdown, `TCP_OVERFLOW`, таймауты RU→EU.
5. **P1 iOS MTU** — клиент ставит 1500, сервер push 1280 игнорируется.
6. **P1 HitWave UX** — вставка `/sub/` URL вместо `vless://` → «invalid link».
7. **P2 Старые профили** — пользователи с `sni=microsoft.com` в кэше HitWave.
8. **P2 CDN tiered DNS** — фазы 1/3 (grey/orange CF) не активированы.
9. **P3 Ожидания** — 100 Mbps на OpenVPN нереалистично; целевой путь = Xray мост 4G.

### Что ещё доделать

| Приоритет | Задача | Статус |
|-----------|--------|--------|
| **P0** | **Phone drill G4** ×4 оператора (speedtest мост) | ⏳ |
| **P1** | OpenVPN retest после UFW; при fail → UDP 1194 профиль | ⏳ |
| **P1** | Расширить `vpn_bridge_hop_smoke.py` — REALITY E2E, не только TCP | ⏳ |
| **P2** | CDN DNS ф1 grey / ф3 orange после drill | ⏳ |
| **P2** | Legal sign-off vpn-54/77 | ⏳ |
| **P3** | vpn-76 reserve EU IP, vpn-78 auto transport | post-GA |

> **Гарантия скорости:** после vpn-96 серверный E2E **работает**. Полная «быстро и надёжно» — только после **phone drill**; DPI операторов и блокировка IP Contabo остаются внешними рисками (мост/CDN/reserve IP).

---

## Реестр vpn-xx

| ID | Задача | Статус |
|----|--------|--------|
| vpn-00 | SSOT документация | ✅ |
| vpn-01 | Readiness/liveness | ✅ |
| vpn-02 | Legal черновики + эндпоинты | ✅ |
| vpn-02-legal | Юрист | ⏸ исключено |
| vpn-03 | nginx + UFW VPN | ✅ |
| vpn-03-panel | UFW ispmanager | ⏳ вручную |
| vpn-04 | WG + NAT + hooks + /wg/conf | ✅ |
| vpn-05 | REALITY :8443 + /sub | ✅ |
| vpn-05b | Профили /sub/ `#default` + `#mobile-rf` (HitWave 4G) | ✅ 2026-06-19 |
| vpn-05-443 | Reality :443 | ⏳ опционально |
| vpn-06 | OpenVPN :1194 | ✅ |
| vpn-07–09 | DB, API, план | ✅ |
| vpn-10 | Бот funnel + авто-📥 + 🧪 | ✅ |
| vpn-11 | Оплата → provision | ✅ |
| vpn-12 | /r/{code} | ✅ |
| vpn-13–16 | Secrets, admin, obs, tests | ✅ |
| vpn-17–18 | Deploy, server tree | ✅ |
| vpn-19 | protocols/ extract | ⏳ низкий приор. |
| vpn-20–28 | Config, hub, CB, QR… | ✅ |
| vpn-29 | PUBLIC_SURFACE_REGISTRY | ✅ ведётся |
| vpn-30 | Вторая нода | ⏸ исключено |
| vpn-31 | /admin VPN | ✅ |
| vpn-32 | External smoke script | ✅ cron вне VPS ⏳ |
| vpn-33 | Blocklist playbook | ✅ |
| vpn-34 | Runbook + шаблоны постов | ✅ `VPN34_STATUS_POST_TEMPLATES.md` |
| vpn-34-posts | Регулярные посты | ⏳ процесс |
| vpn-36 | Рефералка | ✅ |
| vpn-37 | Локации UI + API + endpoint_host | ✅ single-node |
| vpn-37-peer | Peer на 2-й ноде | ⏸ с vpn-30 |
| vpn-38 | Хаб инструкций | ✅ |
| vpn-38-content | Контент + CTA, скриншоты-заглушки | ✅ |
| vpn-39 | Mini App | ⏸ исключено |
| vpn-40 | CTA на лендинге | ✅ в vpn-instructions.md |
| vpn-41 | SSOT resilient architecture plan | ✅ 2026-06-27 |
| vpn-42 | Contabo XHTTP+Reality (8443 v1) | ✅ 2026-06-28 xhttp /xhttp |
| vpn-43 | /sub/ #wifi-direct #mobile-xhttp | ✅ 2026-06-28 deploy |
| vpn-44 | Бот UX 4G≠OVPN, QR rename | ✅ S4 bridge order |
| vpn-45 | 4G smoke → ops alert | ✅ `vpn_external_smoke_cron.sh`; enable cron ⏳ |
| vpn-46 | RU bridge VPS **или** MAIN go/no-go (vpn-82) | ✅ MAIN :8444 2026-06-28 |
| vpn-47 | Bridge Xray :443 XHTTP+Reality | ✅ `:8444` xhttp-bridge |
| vpn-48 | Bridge→Contabo hop | ✅ hop UUID + outbound |
| vpn-49 | Split routing RU на bridge | ✅ full tunnel → Contabo v1 |
| vpn-50 | /sub/ #mobile-bridge + egress JSON | ✅ «Мобильный мост» |
| vpn-51 | Cloudflare CDN origin | ✅ :8445 origin; **DNS ф1–3 ⏳** по drill |
| vpn-52 | /sub/ #mobile-cdn | ✅ «Мобильный CDN»; **ф0 A cdn ⏳** |
| vpn-53 | Ops SNI/fp rotation runbook | ✅ VPN53 |
| vpn-54 | Legal RU bridge | ⏳ черновик ✅ → юрист (RU transit) |
| vpn-55 | Drill 4G ×**4** ops — **матрица IP/SNI/CF** | ⏳ **G4** Integration Week (vpn-88) |
| vpn-56 | Wi‑Fi baseline OVPN vs Xray A/B | ⏳ **G4** Integration Week (vpn-88) |
| vpn-57 | Script server vs tunnel speed | ✅ `vpn_tunnel_vs_server_speed.sh` |
| vpn-58 | OpenVPN MTU + tcp-only issue | ✅ `openvpn-client-issue.sh` |
| vpn-59 | WG copy «только Wi‑Fi» | ✅ vpn-93 + instructions |
| vpn-60 | Client matrix v2rayNG/**HitWave**/Hiddify/NOT v2RayVPN | ✅ matrix vpn-94 + tests |
| vpn-61 | vpn-instructions.md HitWave + 4 профиля | ✅ S4 |
| vpn-62 | MAIN bot post-deploy guard | ✅ bot stopped 2026-06-28; guard PASS |
| vpn-63 | Throttle alert <100 Kbit/s | ✅ B1 cron + Prom rules |
| vpn-64 | Bridge VPS IP pre-check | ✅ `vpn_bridge_ip_precheck.sh` |
| vpn-65 | Bridge failover reserve RU | ✅ VPN65 runbook |
| vpn-66 | Bot hint профиль 4G vs Wi‑Fi | ✅ мост + CDN в copy |
| vpn-67 | CF CDN health ops | ✅ `vpn_cdn_health.py` |
| vpn-68 | Investor brief 2026 | ✅ |
| vpn-69 | Grafana per-profile metrics | ✅ /sub/* panels + alert rules |
| vpn-70 | vpn-33 bridge/CDN playbook | ✅ `VPN70_BRIDGE_CDN_PLAYBOOK.md` |
| vpn-71 | iOS Hiddify strategy | ✅ VPN71 |
| vpn-72 | Autotests /sub/ + QR | ✅ CI `vpn-api-tests.yml` + pytest |
| vpn-73 | OVPN explicit IPv4 remote | ✅ env `VPN_WG_ENDPOINT_IP` |
| vpn-74 | Contabo IPv4: **8443 v1** vs доп. IPv4 :443 (§1.4 плана) | ✅ `VPN74_CONTABO_PORT_DECISION.md` |
| vpn-75 | GA release gate drill PASS ×**4** | ⏳ фаза 3–4 |
| vpn-76 | Reserve EU egress + runbook смены Contabo IP | ⏳ фаза 5 (v2) |
| vpn-77 | Legal полный + **CF subprocessor** | ⏳ черновик ✅ → юрист |
| vpn-78 | v2: **один Connect** — server-side auto transport + bridge/CDN fallback | ⏳ post-GA |
| vpn-79 | Drill **Tele2** (4-й оператор) | ⏳ фаза 4 |
| vpn-80 | Плавная ротация SNI (dual serverName) | ⏳ фаза 3–4 |
| vpn-81 | Человекочитаемые имена профилей `/sub/` | ✅ 2026-06-28 |
| vpn-82 | MAIN bridge: Xray отд. порт, `:8002` не трогаем (§1.2) | ✅ 2026-06-28 `:8444` |
| vpn-83 | Статус-канал при инцидентах 4G | ✅ B8 module + VPN34 process |
| vpn-84 | Автomatизация §9 B1–B9 | ✅ scripts; prod cron ⏳ |
| vpn-85 | UX «простой язык» в боте | ✅ S4 |
| vpn-86 | **HitWave** iOS: бот ✅, drill ✅, инструкции ✅ (deploy 20260628-024506) | ✅ 2026-06-28 |
| vpn-87 | **Режим v6** §11: комбинированный план, спринты, gate G0–G4 | ✅ 2026-06-28 |
| vpn-88 | **Integration Week G4:** календарь + журнал Wi‑Fi/4G ×4 ops | ✅ календарь+JSON; drill ⏳ phone |
| vpn-89 | **Pre-GA audit:** §5.1 + §11.4 + **§11.6** tiered CDN | ⏳ auto ✅; sign-off ⏳ |
| vpn-90 | **UX SSOT §12:** subscription URL, HitWave без deep link | ✅ 2026-06-28 |
| vpn-91 | **Post-payment pack:** ссылка + QR + «3 шага» после оплаты | ✅ 2026-06-28 |
| vpn-92 | **HitWave onboarding:** import один раз + Auto Update | ✅ 2026-06-28 |
| vpn-93 | **UX:** OVPN/WG только «🔀 Запасные способы» | ✅ 2026-06-28 |
| vpn-94 | **Deep link matrix:** HitWave vs v2raytun:// | ✅ 2026-06-28 |
| vpn-95 | **Landing `/i/{code}`** (post-GA опц.) | ⏳ фаза 5–6 |
| vpn-96 | REALITY dest cloudflare (инцидент Jun 28) | ✅ 2026-06-28 |
| vpn-97 | UFW OVPN tun forward fix | ✅ 2026-06-28 |
| vpn-98 | HitWave кнопки vless мост/Wi‑Fi | ✅ 2026-06-28 |
| vpn-99 | xhttp stream-one server config | ✅ 2026-06-28 |
| vpn-100 | /sub/ SNI env sync cloudflare | ✅ 2026-06-28 |

**Resell чужого VPN:** ❌ не делаем (решение в `VPN_INVESTOR_BRIEF_2026.md`).

**G1 (Sprint 1):** ✅ **PASS 2026-06-28**

**G2 (Sprint 2 — RU bridge):** ✅ **PASS 2026-06-28**

**G3 (Sprint 3 — CDN):** ✅ **PASS 2026-06-28** — origin `:8445`, `/sub/` 4 профиля (мост→direct→CDN), smoke 10/10. **Ops DNS tiered ф0–3 ⏳** — см. §11.6, `VPN_CDN_DNS_PHASE_CHECKLIST.md`.

**G4 (Integration Week):** ⏳ **AUTO PASS** infra; **телефон ×4 + матрица IP/SNI/CF + GA в конце**

**Sprint 4 Ops:** ✅ скрипты B1–B9, runbooks VPN53/65/69, UX/инструкции — см. `deploy/VPN_S4_OPS_RUNBOOK.md`

**Post-GA:** vpn-78 «один Connect» — ⏳.

**DNS CDN tiered (§11.6):**

| Фаза | Действие | Статус |
|------|----------|--------|
| **0** | A `cdn` в reg.ru | ✅ |
| **1** | grey → Contabo `:8445` | ⏳ после drill или старт |
| **2** | relay → MAIN `:8445` | ✅ relay; ⏳ DNS A |
| **3** | CF orange + `VPN_CDN_PORT=443` | ⏳ если Contabo IP block |

**План v7.1:** `VPN_RESILIENT_ARCHITECTURE_PLAN_2026.md` · **Cursor:** 55 задач (`vpn-r00`…`vpn-r54`) + vpn-dns

---

## Выкат 2026-05-16

- Авто-📥, 🧪 Проверить VPN, checkout VPN без @username  
- IPv4-only AllowedIPs в WG  
- `endpoint_host` в каталоге локаций (merge_vpn30_env)  
- Инструкции + шаблоны статус-канала  

**Прод Sprint 1:** xhttp ✅ · `/sub/` human names ✅ · smoke **10/10** · bot `20260628-114543` · onboarding vpn-91…94 ✅
