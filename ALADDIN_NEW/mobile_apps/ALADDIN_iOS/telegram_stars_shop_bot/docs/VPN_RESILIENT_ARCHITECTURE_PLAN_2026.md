# ALADDIN VPN — план устойчивой архитектуры (2026)

**Дата:** 2026-06-28 (**v7.1** — §11.6 tiered CDN DNS)  
**Контекст:** prod-инциденты MegaFon 4G, HitWave (iOS), MAIN как RU-мост, **режим v6**, **UX subscription §12**  
**Связано:** `VPN_FULL_SESSION_HANDOFF_ML_2026-06-27.md`, `VPN30_SINGLE_NODE_MAX.md`, `VPN_TASKS_STATUS.md`  
**Cursor TODO SSOT:** `.cursor/VPN_RESILIENT_TASK_REGISTRY.md` (`vpn-r00` … `vpn-r54`)

---

## 1. Решение продукта (зафиксировано)

**Целевой стек:** **Вариант 3** — RU bridge + Contabo egress + Cloudflare CDN fallback.

| Уровень | Назначение |
|---------|------------|
| **L1 Wi‑Fi / low-latency** | Прямой XHTTP+Reality на Contabo (профиль `#wifi-direct`) |
| **L2 Mobile 4G (primary)** | RU bridge (MAIN `:443` или отдельный RU VPS) → Contabo egress (`#mobile-bridge`) |
| **L3 Mobile whitelist / авария** | VLESS через Cloudflare CDN (профиль `#mobile-cdn`) |
| **L4 iPhone RU Store, только Wi‑Fi** | OpenVPN TCP-only `.ovpn` (не обещать на 4G) |

**OpenVPN / WireGuard / прямой Reality+Vision на foreign IP — не primary для 4G и не primary для Wi‑Fi (OpenVPN ~3.6 Кб/с — prod fail).**

**Инвесторский brief:** `VPN_INVESTOR_BRIEF_2026.md`

**Для пользователя (простой язык):** одна ссылка → одно приложение → два понятных профиля: **«Домашний Wi‑Fi»** и **«Мобильный интернет»**. Без слов Contabo, мост, XHTTP, Reality.

---

## 1.0 Два сервера — роли (зафиксировано)

| Сервер | IP | Хостер | Роль |
|--------|-----|--------|------|
| **MAIN** | `149.154.65.180` | FVDS (РФ) | iOS backend `:8002`; nginx `aladdin-ai.ru`; **кандидат RU-мост** (Xray на **отдельном порту**, `:8002` не трогаем) |
| **Contabo EU** | `185.225.233.150` | Contabo DE | VPN egress: Xray `:8443`, WG, OpenVPN, shop-vpn-api |

**RU-мост:** задача **vpn-82**. На MAIN VPN уже на **другом порту** — `:8002` iOS backend **не нагружаем** (как сейчас). Отдельный RU VPS — запасной вариант изоляции (vpn-65).

---

## 1.2 RU-мост: MAIN `149.154.65.180` — подойдёт?

| Критерий | MAIN (FVDS РФ) | Отдельный RU VPS |
|----------|----------------|------------------|
| IP уже в РФ | ✅ | ✅ (pre-check vpn-64) |
| VPN на отдельном порту, `:8002` свободен | ✅ **уже так** | ✅ |
| Xray bridge :443 / :8443 | ✅ | ✅ |
| Изоляция от iOS backend | ⚠️ один IP с `aladdin-ai.ru` | ✅ |
| Блокировка моста → риск для app | ⚠️ | ✅ меньше |
| Доп. €/мес | **€0** | €3–8 |

**Решение v5:** MAIN **допустим как RU-мост** — Xray inbound на **отдельном порту** (не `:8002`); nginx/SNI или поддомен `bridge.aladdin-ai.ru`. **vpn-82:** задокументировать схему + legal (vpn-54). Отдельный VPS — **vpn-65** reserve, не блокер v1.

---

## 1.2b HitWave (iOS) — клиент подписки `/sub/`

**Happ удалён из App Store (2026).** Основной iOS-клиент для `/sub/` — **HitWave** (App Store).

**Модель доставки (зафиксировано, §12):** одна **subscription URL** `https://aladdin-ai.ru/sub/<token>` — стандарт Xray/Marzban/3x-ui. Пользователь **не ходит в бот постоянно**: import **один раз** → **Auto Update** в HitWave → дальше только Connect.

| Клиент | Import | Deep link |
|--------|--------|-----------|
| **HitWave** (RU App Store) | Paste URL / QR | ❌ публичного `hitwave://` нет |
| **v2RayTun** (foreign Apple ID) | Paste или `v2raytun://import/` | ✅ |
| **Happ** (legacy) | `happ://add/` | ✅ только если уже установлен |
| **v2rayNG** (Android) | Subscription URL + Auto Update 24h | стандарт |

| Шаг | Действие |
|-----|----------|
| 1 | Оплата → **ссылка приходит в чат автоматически** (vpn-91) |
| 2 | HitWave → Подписка / Import URL → **один раз** |
| 3 | HitWave → включить **Auto Update** подписки (vpn-92) |
| 4 | Wi‑Fi: **«Домашний Wi‑Fi»** · 4G: **«Мобильный интернет»** (vpn-81) |
| 5 | Connect. Повторно в бот — только новый телефон / сброс |

**Протокол на сервере:** VLESS + Reality + XHTTP (vpn-42 ✅). HitWave совместим с тем же форматом, что v2rayNG.

**Happ:** только legacy — «если уже установлен, не удалять»; новым пользователям **не рекомендуем**.

**Задачи:** **vpn-86** ✅ · **vpn-90**–**vpn-95** (UX onboarding, §12).

---

## 1.3 Скорость — ожидания (честно)

| Уровень | Типичная скорость пользователю | Узкое место |
|---------|-------------------------------|-------------|
| Contabo «голый» (curl) | **~16 МБ/с (~128 Мбит/с)** | канал VPS |
| Wi‑Fi + `#wifi-direct` (после плана) | **20–80 Мбит/с** | DPI/throttle на пути |
| 4G + `#mobile-bridge` | **5–30 Мбит/с** | оператор + 2 hop |
| 4G + `#mobile-cdn` | **3–20 Мбит/с** | CF + latency |
| OpenVPN Wi‑Fi (сейчас) | **~3.6 Кб/с** | не использовать как primary |
| **Минимум успеха (DoD)** | **≥1 Мбит/с стабильно ≥5 мин** на 4G | drill vpn-55 |

**Для максимальной скорости на Contabo не нужен второй IP** — нужны **XHTTP**, **мост на 4G**, без `flow=vision` на mobile, MTU 1280 на OVPN. Второй IPv4 (vpn-74) — про **порт 443 и резерв**, не про «разогнать до 100 Мбит/с».

---

## 1.4 IPv4 на Contabo — vpn-74 (решение зафиксировано)

| Факт | Значение |
|------|----------|
| **IPv4 уже есть** | `185.225.233.150` — один публичный IPv4 на Contabo (**не покупать «первый»**) |
| Xray сейчас | TCP **8443** |
| HTTPS `/sub/` | MAIN **443** → nginx proxy → Contabo `:8091` |

### v1 (рекомендуется) — достаточно для скорости

- Оставить **8443 + XHTTP + RU-мост** (MAIN или отдельный RU VPS).
- **Не нужно** доп. железо/IP на Contabo для «максимальной скорости».
- Тюнинг: XHTTP, без `flow=vision` на mobile, MTU 1280 на OpenVPN (legacy).

### v2 — только если drill FAIL на 8443

- **Доп. IPv4** на Contabo (~€2–4/мес) → XHTTP/Reality на **:443** напрямую на EU.
- Альтернатива без доп. IP: nginx stream SNI mux на MAIN `:443`.

**Итог vpn-74:** v1 по умолчанию; v2 — по результатам drill, не upfront.

---

## 1.5 Операторы РФ (drill ×4)

| Оператор | Поведение | Primary профиль 4G | Запасной |
|----------|-----------|-------------------|----------|
| MegaFon | tcp-freeze после 15–20 KB на foreign IP | `#mobile-bridge` | `#mobile-cdn` |
| MTS | DPI + throttle foreign DC | `#mobile-bridge` | `#mobile-cdn` |
| Beeline | как MTS/MegaFon | `#mobile-bridge` | `#mobile-cdn` |
| **Tele2** | жёстче к VPN-подписям | `#mobile-bridge` | `#mobile-cdn` |

**Wi‑Fi:** `#wifi-direct`. **Drill:** vpn-55 + vpn-79 — все **4 оператора**, метрика **speed ≥1 Мбит/с ≥5 мин**, не «connected».

---

## 1.6 UX в проде — что показывать пользователю

### Показывать ✅
- «Купили → ссылка → приложение → подключились»
- Профили: **«🏠 Домашний Wi‑Fi»**, **«📱 Мобильный интернет»** (vpn-81)
- **Android:** v2rayNG · **iOS:** **HitWave** > Hiddify (foreign Apple ID)
- «На 4G — профиль „Мобильный интернет“»
- 📥 📷 🧪 📖 + канал статуса + AUP «защищённое соединение»

### Не показывать ❌
- Contabo, IP, мост, Cloudflare, XHTTP, Reality, VLESS, pbk, sid
- «100% всегда», «обход блокировок»
- OpenVPN/WG как лучший на 4G; v2RayVPN; Happ как основной (удалён из Store)
- 4 равных протокола без подсказки

### HitWave — алгоритм (vpn-86)

`/sub/` → HitWave Import → профиль «Мобильный интернет» / «Домашний Wi‑Fi» → Connect. Тот же VLESS+Reality, что у v2rayNG.

### Приоритет клиентов (vpn-60, vpn-86)
- **Android:** v2rayNG → Hiddify
- **iOS:** **HitWave** (App Store) → Hiddify → v2RayTun (foreign Apple ID) → OpenVPN **только Wi‑Fi**
- **Legacy:** Happ — только если уже установлен

---

## 1.1 Wi‑Fi reality check (зафиксировано 2026-06-27)

| Канал | Симптом | Сервер | Вердикт |
|-------|---------|--------|---------|
| OpenVPN TCP Wi‑Fi | connect OK, **~3.6 Кб/с** | handshake + data channel OK, tun1 ~KB total | **Не primary** |
| OpenVPN 4G MegaFon | timeout 60s | VERIFY OK → TLS fail | **Не использовать** |
| Contabo raw | **~16 MB/s** download | curl speedtest | Сервер **не** узкое место |
| Xray direct | переменно | — | Лучше OVPN, **недостаточно без bridge** |

**Вывод:** узкое место — **путь клиент → foreign IP (DPI/throttle)**, не код бота и не «слабый Contabo».

---

## 2. Повторная верификация: почему Вариант 3 — оптимальный (не «магия 100%»)

### 2.1 Честная оценка

| Утверждение | Правда |
|-------------|--------|
| «100% никогда не блокируется» | **Ложь** — TSPU обновляет правила; нужен мониторинг и ротация |
| «Лучший из реалистичных DIY+продукт» | **Да** — покрывает все известные механизмы блокировки 2026 |
| «Дешевле коммерческого VPN» | **Да** при своей базе пользователей |
| «Проще одного Contabo» | **Нет** — нужен DevOps и 4G smoke |

### 2.2 Матрица альтернатив (независимая проверка)

| Вариант | Wi‑Fi | 4G RU | Устойчивость к tcp-16-20 | Устойчивость к CIDR whitelist | Сложность | Вердикт |
|---------|-------|-------|--------------------------|-------------------------------|-----------|---------|
| Текущий (Contabo only) | ⚠️ | ❌ | ❌ | ❌ | Низкая | Заменить |
| Только XHTTP на Contabo | ✅ | ⚠️ 50–70% | ⚠️ | ❌ | Средняя | Недостаточно |
| RU bridge + egress (#2) | ✅ | ✅ 80–90% | ✅ | ⚠️ | Высокая | **Core** |
| #2 + CF CDN (#3) | ✅ | ✅ 90–95%* | ✅ | ✅ | Высокая | **⭐ Выбран** |
| Только CF CDN без bridge | ✅ | ⚠️ 60–80% | ⚠️ | ✅ | Средняя | Запасной, не primary |
| OpenVPN TCP 443 | ✅ Wi‑Fi | ❌ 4G | ❌ | ❌ | Низкая | Только L4 |
| WireGuard / AmneziaWG direct | ⚠️ | ❌ | ❌ | ❌ | Средняя | Не primary |
| Resell чужой VPN | ✅ | ⚠️/✅ | ? | ? | Нулевая | Не наш продукт |

\* 90–95% — при условии мониторинга 4G, ротации SNI/fp, актуального Xray ≥25.12.

### 2.3 Почему не «что-то ещё лучше»

1. **Только bridge без CDN** — не спасает при региональном **CIDR whitelist** (MegaFon/Yota, Habr 990236).
2. **Только CDN без bridge** — latency выше; при блокировке CF-пути остаётесь без L2.
3. **Только OpenVPN** — доказано на MegaFon: VERIFY OK → timeout (логи 2026-06-27).
4. **Hysteria/QUIC** — на mobile часто режется сильнее TCP.
5. **Коммерческий VPN** — не контроль, margin уходит, нет интеграции с ботом.

**Вывод:** Вариант 3 — **Pareto-optimal**: максимум покрытия 4G+Wi‑Fi при приемлемой стоимости (~€8–15/мес infra) и сохранении своего продукта.

---

## 3. Реестр задач vpn-41 … vpn-95

| ID | Задача | Фаза | Зависимости |
|----|--------|------|-------------|
| vpn-41 | SSOT: этот документ + обновить VPN_TASKS_STATUS | 0 | — |
| vpn-42 | Contabo: XHTTP+Reality inbound (8443 v1 или :443 с доп. IP) | 1 | — |
| vpn-43 | `/sub/`: `#wifi-direct`, `#mobile-xhttp` (без Vision на mobile) | 1 | vpn-42 |
| vpn-44 | Бот: «4G ≠ OpenVPN», QR, playbook | 1 | — |
| vpn-45 | 4G smoke cron → ops алерт | 1 | — |
| vpn-46 | RU bridge: **MAIN** (отд. порт) или RU VPS после vpn-82 | 2 | vpn-82 |
| vpn-47 | Bridge: Xray VLESS+XHTTP+Reality :443 | 2 | vpn-46 |
| vpn-48 | Bridge → Contabo hop | 2 | vpn-42, vpn-47 |
| vpn-49 | Split routing RU на bridge | 2 | vpn-48 |
| vpn-50 | `/sub/`: `#mobile-bridge`, VPN_EGRESS_NODES_JSON | 2 | vpn-48 |
| vpn-51 | Cloudflare CDN origin | 3 | vpn-42 |
| vpn-52 | `/sub/`: `#mobile-cdn` | 3 | vpn-51 |
| vpn-53 | Ops: ротация SNI/fp runbook | 3 | vpn-45 |
| vpn-54 | Legal review bridge RU | 2–3 | vpn-46 |
| vpn-55 | Drill 4G: **MegaFon+MTS+Beeline+Tele2** | **4 (G4)** | vpn-43,50,52, **vpn-88** |
| vpn-56 | Wi‑Fi baseline OVPN vs Xray A/B | **4 (G4)** | vpn-43, **vpn-88** |
| vpn-57 | Script server vs tunnel speed | 1 | — |
| vpn-58 | OpenVPN MTU 1280, tcp-only | 1 | vpn-44 |
| vpn-59 | WG «только Wi‑Fi» | 1 | vpn-44 |
| vpn-60 | Client matrix v2rayNG/**HitWave**/Hiddify/NOT v2RayVPN | 1 | vpn-44 |
| vpn-61 | vpn-instructions.md rewrite | 1–3 | vpn-43,52 |
| vpn-62 | MAIN bot post-deploy guard | 1 | — |
| vpn-63 | Throttle alert <100 Kbit/s | 1–4 | vpn-45 |
| vpn-64 | Bridge IP pre-check (traceroute) | 2 | vpn-46 |
| vpn-65 | Bridge failover reserve RU | 2 | vpn-47 |
| vpn-66 | Bot hint Wi‑Fi vs 4G профиль | 2 | vpn-50 |
| vpn-67 | CF CDN health ops | 3 | vpn-51 |
| vpn-68 | Investor brief | 0 | ✅ |
| vpn-69 | Grafana per-profile metrics | 4 | vpn-45 |
| vpn-70 | vpn-33 bridge/CDN playbook | 3 | vpn-51 |
| vpn-71 | iOS Hiddify / Apple ID guide | 1 | vpn-60 |
| vpn-72 | Autotests /sub/ + QR | 1 | vpn-43 |
| vpn-73 | OVPN explicit IPv4 remote | 1 | vpn-58 |
| vpn-74 | Contabo IPv4: **v1** 8443+XHTTP+мост; **v2** доп.IP :443 если FAIL (§1.4) | 1 | vpn-42 |
| vpn-75 | GA gate: drill PASS ×**4** ops | 3–4 | vpn-55 |
| vpn-76 | Reserve EU egress + runbook | 4–5 | vpn-70, vpn-74 |
| vpn-77 | Legal полный (**параллельно vpn-46**) | 2–4 | vpn-54 |
| vpn-78 | v2: **один профиль Connect** — сервер выбирает transport; bridge/CDN fallback без ручного переключения | 5 | vpn-50,52,66,90 |
| vpn-79 | Drill **Tele2** (4-й оператор) | 4 | vpn-55 |
| vpn-80 | Плавная ротация SNI (dual serverName) | 3–4 | vpn-53 |
| vpn-81 | Человекочитаемые `#fragment` в `/sub/` | 1–2 | vpn-43 |
| vpn-82 | MAIN bridge: Xray отд. порт, `:8002` не трогаем + legal (§1.2) | 2 | — |
| vpn-83 | Статус-канал при инцидентах 4G | 4 | vpn-45 |
| vpn-84 | Автоматизация §9 (A1–A3 ✅, B1–B9 ⏳) | 1–4 | vpn-72 |
| vpn-85 | UX «простой язык» в боте | 1–2 | vpn-44,81 |
| vpn-86 | **HitWave** iOS: бот, drill, инструкции (Happ → legacy) | 1 | vpn-60,44 | ✅ |
| vpn-87 | **Режим v6:** комбинированный план (§11) — спринты, 3 track, gate G0–G4 | 0 | vpn-41 | ✅ |
| vpn-88 | **Integration Week G4:** календарь + журнал Wi‑Fi/4G ×4 ops | 4 | vpn-43,50,52 |
| vpn-89 | **Pre-GA audit:** сверка DoD §5.1 ↔ чеклист «6 шляп» (§11.4) | 4 | vpn-88,75 |
| vpn-90 | **UX SSOT §12:** subscription URL модель, оценка архитектуры, HitWave без deep link | 0–1 | vpn-41 | ✅ |
| vpn-91 | **Post-payment pack:** ссылка + QR + «3 шага» одним сообщением после оплаты | 1 | vpn-86,44 |
| vpn-92 | **HitWave onboarding:** «import один раз» + Auto Update — бот + `vpn-instructions.md` | 1 | vpn-86,61 |
| vpn-93 | **UX simplify:** OVPN/WG только «🔀 Запасные способы», не на главном экране | 1 | vpn-44,85 |
| vpn-94 | **Deep link matrix:** HitWave paste vs `v2raytun://import/` — doc + бот | 1 | vpn-71,92 |
| vpn-95 | **Landing `/i/{code}`:** QR + import в браузере (post-GA, опц.) | 5–6 | vpn-91 |

**Tier 3 (после GA):** своё iOS-приложение · **vpn-39** Mini App ⏸ · §12.4.

**Решение продукта (зафиксировано):** **resell чужого VPN — не делаем** (см. `VPN_INVESTOR_BRIEF_2026.md` § Свой vs resell). Отдельной задачи не требуется.

---

## 4. Детальный план по фазам

### Фаза 0 — Документация и baseline (1–2 дня)

- [x] **vpn-41** Опубликовать этот план; обновить `VPN_TASKS_STATUS.md`
- [x] **vpn-68** `VPN_INVESTOR_BRIEF_2026.md` для инвесторов
- [x] **vpn-87** Режим выполнения v6 (§11) — этот документ
- [ ] Зафиксировать baseline 4G MegaFon (handoff 2026-06-27) → **G4** vpn-88
- [ ] **vpn-56** Wi‑Fi baseline → **G4 Integration Week** (vpn-88), не блокирует Sprint 1
- [ ] Обновить `VPN_ML_SYSTEM_HANDOFF.md` ссылкой на resilient plan + investor brief
- [ ] Обновить `VPN_PUBLIC_SURFACE_REGISTRY.md` (bridge IP — после vpn-46)

### Фаза 1 — Быстрые улучшения на Contabo (**Sprint 1**, см. §11)

**Цель:** XHTTP + UX batch; **не блокируется** Wi‑Fi/4G drill (перенесён в **G4 Integration Week**, vpn-88). Параллельно **Track C:** vpn-77 (legal).

**Критерий G1 (конец Sprint 1):** см. §11.3 — auto-smoke 10/10, `/sub/` профили, pytest; **не** ручной 4G.

| # | Работа | Файлы / сервер |
|---|--------|----------------|
| 1.1 | XHTTP inbound на Xray (Contabo) | `/opt/xray/config.json`, runbook VPN05 |
| 1.2 | Reality на 443 через nginx `stream` SNI mux ИЛИ отдельный IP | `nginx`, `VPN05`, `VPN30` §доп. IPv4 |
| 1.3 | Env: `VPN_SUBSCRIBE_*` — mobile без `flow=xtls-rprx-vision`, fp=firefox | `env`, `subscription_util.py` |
| 1.4 | Новые profile names в `/sub/` | `subscription_util.py`, tests |
| 1.5 | Бот: OpenVPN только Wi‑Fi; 4G → Xray; QR rename | `vpn_connect_copy.py`, `vpn_user_links.py` |
| 1.6 | OpenVPN: `tcp443-only.ovpn` + IPv4 + MTU 1280 (**vpn-58, vpn-73**) | `openvpn-client-issue.sh` |
| 1.7 | **vpn-57** Диагностика server vs tunnel speed | `deploy/scripts/` |
| 1.8 | **vpn-59** WG copy «только Wi‑Fi» | `vpn_connect_copy.py` |
| 1.9 | **vpn-60** Матрица клиентов + NOT v2RayVPN | бот + legal |
| 1.10 | **vpn-61** Обновить `vpn-instructions.md` | legal_docs |
| 1.11 | **vpn-62** MAIN bot guard post-deploy | ops runbook |
| 1.12 | **vpn-71** iOS Hiddify / Apple ID guide | docs |
| 1.13 | **vpn-72** Autotests /sub/ + QR buttons | tests/ |
| 1.14 | **vpn-74** Decision: **8443 OK v1** vs доп. IPv4 :443 (§1.4) | doc + infra |
| 1.15 | Smoke auto только (**vpn-56** → G4 Integration Week) | — |
| 1.16 | **vpn-81** Человекочитаемые имена профилей | `subscription_util.py` |
| 1.17 | **vpn-85** UX простой язык в боте | `vpn_connect_copy.py` |
| 1.18 | **vpn-91** Post-payment pack: ссылка+QR+3 шага | `vpn_post_purchase_delivery.py` |
| 1.19 | **vpn-92** HitWave: import один раз + Auto Update | бот + `vpn-instructions.md` |
| 1.20 | **vpn-93** OVPN/WG только «Запасные способы» | `vpn.py`, `vpn_connect_copy.py` |
| 1.21 | **vpn-94** Deep link matrix (HitWave vs v2raytun) | docs + бот |

**Критерий готовности Ф1:** **G1 PASS** (§11.3). XHTTP в `/sub/`; бот честный (4G≠OVPN); pytest green.

### Фаза 2 — RU Bridge (**Sprint 2**, ⭐ Core)

**Цель:** обход tcp-16-20 freeze и foreign IP filtering на mobile.

| # | Работа | Детали |
|---|--------|--------|
| 2.1 | RU VPS (**vpn-64** pre-check) **или** MAIN после vpn-82 | Selectel / Yandex / FVDS |
| 2.1b | **vpn-65** Reserve bridge провайдер | второй RU VPS doc only до need |
| 2.2 | Xray bridge :443 | VLESS+XHTTP+Reality; SNI = whitelisted RU HTTPS (vk, ozon, sber — по RealiTLScanner) |
| 2.3 | Outbound bridge → Contabo | VLESS+XHTTP+Reality; отдельные keys/uuid/path |
| 2.4 | Routing | `geosite:category-ru`, `geoip:ru` → direct; остальное → foreign-egress |
| 2.5 | API/подписка | Вторая строка VLESS `#mobile-bridge` с host=bridge IP/domain |
| 2.6 | `VPN_EGRESS_NODES_JSON` | `{id:bridge,...}`, `{id:primary,...}` |
| 2.7 | UFW, systemd, backup | как Contabo runbooks |
| 2.8 | Auto-smoke bridge (не ручной drill) | ops; **ручной 4G ×4 → G4** vpn-88 |
| 2.9 | **vpn-66** Бот: «на 4G выберите #mobile-bridge» | copy |
| 2.10 | **vpn-54** Legal sign-off bridge RU | юрист |

**Критерий готовности Ф2:** **G2 PASS** (§11.3). `#mobile-bridge` в `/sub/`; bridge auto-smoke OK.

### Фаза 3 — Cloudflare CDN fallback (**Sprint 3**)

**Цель:** CIDR whitelist / блок foreign IP на mobile.

| # | Работа | Детали |
|---|--------|--------|
| 3.1 | Поддомен `vpn-cdn.aladdin-ai.ru` (или отдельный) | DNS → CF proxy ON |
| 3.2 | Origin на Contabo | nginx reverse proxy → xray websocket/xhttp path |
| 3.3 | CF SSL mode Full (strict), origin cert | CF dashboard |
| 3.4 | Профиль `#mobile-cdn` в `/sub/` | grpc или xhttp через CF |
| 3.5 | Бот: «если bridge не работает → профиль CDN» | `vpn_connect_copy.py` |
| 3.6 | Smoke whitelist-сценарий | Yota/MegaFon регионы с whitelist |
| 3.7 | **vpn-67** CF health check + fallback order | ops |
| 3.8 | **vpn-70** vpn-33 playbook bridge/CDN | deploy |

**Критерий готовности Ф3:** **G3 PASS** (§11.3). `#mobile-cdn` работает; CF health OK.

### Фаза 4 — Integration Week + Ops (**Sprint 4**, G4)

- [x] **vpn-53** Runbook ротации SNI/fp (**vpn-80** dual serverName — без обрыва пользователей)
- [x] **vpn-45** External smoke → Telegram ops (скрипты + cron; **включить cron** на external host)
- [x] **vpn-63** Throttle alert speed <100 Kbit/s (cron + Prometheus rules)
- [x] **vpn-69** Grafana success rate по `/sub/*` (панели + alert rules)
- [x] **vpn-88** Integration Week G4: календарь + журнал ✅; drill ⏳ телефон
- [ ] **vpn-89** Pre-GA audit: auto ✅; sign-off ⏳ journal
- [ ] **vpn-75** Release gate: drill PASS ×4 ops → marketing GA
- [ ] **vpn-77** Legal полный (**старт параллельно vpn-46**, не в конце)
- [x] **vpn-83** Статус-канал: autopost module + process doc (**env + cron** ⏳)
- [x] **vpn-84** Автоматизация B3–B9 скрипты ✅; **cron на prod** ⏳
- [x] **vpn-64** Bridge IP pre-check (B9)
- [x] **vpn-65** Bridge failover runbook
- [x] **vpn-34-posts** Процесс регулярных постов
- [x] **vpn-71** Hiddify / Apple ID guide
- [x] **vpn-44/85/61** UX 4 профиля + bridge order (дочистка S1)

**Критерий Ф4:** **G4 PASS** (§11.3): Integration Week журнал; drill ×4 ops; audit vpn-89; ops алерты; legal согласован.

### Фаза 5 — v2 после GA (уровень «как у крупных»)

| # | Работа | Задача |
|---|--------|--------|
| 5.1 | Второй EU egress / reserve Contabo IP | **vpn-76** |
| 5.2 | Runbook: «Contabo IP заблокирован → смена IP / failover secondary» | **vpn-76** + vpn-70 |
| 5.3 | `VPN_EGRESS_NODES_JSON` secondary `active: true` | **vpn-76** |
| 5.4 | **Один профиль Connect** — сервер подбирает Wi‑Fi/4G/bridge/CDN; пользователь не переключает вручную | **vpn-78** |
| 5.5 | Бот: «мы подобрали профиль» — не «выберите #mobile-bridge» | **vpn-78** |
| 5.6 | Landing `/i/{code}` для QR/import (опц.) | **vpn-95** |

**Критерий Ф5:** при блокировке primary EU IP пользователь **автоматически** на reserve/CDN; UX как у платных VPN.

---

## 5. Cursor TODO (зеркало для агента)

**SSOT:** `.cursor/VPN_RESILIENT_TASK_REGISTRY.md` — синхронизировать статус при закрытии каждой задачи (`merge: true`).

| Cursor ID | = vpn-xx | Кратко |
|-----------|----------|--------|
| vpn-r00 | vpn-41 | SSOT документ ✅ |
| vpn-r01 | vpn-42 | XHTTP Contabo |
| vpn-r02 | vpn-43 | /sub/ профили xHTTP |
| vpn-r03 | vpn-44 | Бот UX тексты |
| vpn-r04 | vpn-45 | 4G smoke алерт |
| vpn-r05 | vpn-46 | RU bridge VPS / MAIN go/no-go |
| vpn-r06 | vpn-47 | Bridge Xray :443 |
| vpn-r07 | vpn-48 | Bridge→Contabo hop |
| vpn-r08 | vpn-49 | Split routing RU |
| vpn-r09 | vpn-50 | /sub/ #mobile-bridge |
| vpn-r10 | vpn-51 | Cloudflare CDN setup |
| vpn-r11 | vpn-52 | /sub/ #mobile-cdn |
| vpn-r12 | vpn-53 | Ops rotation runbook |
| vpn-r13 | vpn-54 | Legal bridge |
| vpn-r14 | vpn-55 | Drill **×4** ops (G4) |
| vpn-r15 | vpn-56 | Wi‑Fi baseline A/B (G4) |
| vpn-r16 | vpn-57 | Tunnel vs server speed |
| vpn-r17 | vpn-58 | OpenVPN MTU + tcp-only |
| vpn-r18 | vpn-59 | WG Wi‑Fi only |
| vpn-r19 | vpn-60 | Client matrix |
| vpn-r20 | vpn-61 | vpn-instructions.md |
| vpn-r21 | vpn-62 | MAIN bot guard |
| vpn-r22 | vpn-63 | Throttle alert |
| vpn-r23 | vpn-64 | Bridge IP pre-check |
| vpn-r24 | vpn-65 | Bridge failover |
| vpn-r25 | vpn-66 | Bot 4G hint |
| vpn-r26 | vpn-67 | CF CDN health |
| vpn-r27 | vpn-69 | Grafana metrics |
| vpn-r28 | vpn-70 | vpn-33 playbook |
| vpn-r29 | vpn-71 | iOS Hiddify |
| vpn-r30 | vpn-72 | Autotests /sub/ |
| vpn-r31 | vpn-73 | OVPN IPv4 remote |
| vpn-r32 | vpn-74 | Contabo 8443 vs 2-й IP |
| vpn-r33 | vpn-75 | GA gate drill |
| vpn-r34 | vpn-34-posts | Статус-канал посты |
| vpn-r35 | vpn-76 | Reserve EU egress |
| vpn-r36 | vpn-77 | Legal полный |
| vpn-r37 | vpn-78 | Auto profile v2 |
| vpn-r38 | vpn-79 | Drill Tele2 |
| vpn-r39 | vpn-80 | Dual SNI rotation |
| vpn-r40 | vpn-81 | Human profile names |
| vpn-r41 | vpn-82 | MAIN bridge go/no-go |
| vpn-r42 | vpn-83 | Status channel 4G |
| vpn-r43 | vpn-84 | Automation pack |
| vpn-r44 | vpn-85 | Simple language UX |
| vpn-r45 | vpn-86 | HitWave iOS client ✅ |
| vpn-r46 | vpn-87 | Execution model v6 (§11) ✅ |
| vpn-r47 | vpn-88 | Integration Week G4 |
| vpn-r48 | vpn-89 | Pre-GA 6 hats audit |
| vpn-r49 | vpn-90 | UX SSOT §12 subscription URL ✅ |
| vpn-r50 | vpn-91 | Post-payment onboarding pack |
| vpn-r51 | vpn-92 | HitWave import once + Auto Update |
| vpn-r52 | vpn-93 | OVPN/WG backup menu only |
| vpn-r53 | vpn-94 | Deep link matrix doc+bot |
| vpn-r54 | vpn-95 | Landing /i/{code} (post-GA) |

**Итого Cursor TODO:** **55** задач (`vpn-r00` … `vpn-r54`). Resell ❌.

---

## 5.1 Чеклист «идеально продумано» (definition of done продукта)

| # | Критерий | Задачи |
|---|----------|--------|
| 1 | 4G **×4 ops** ≥1 Мбит/с ≥5 мин (не «connected») | vpn-50,55,79,75 |
| 2 | Wi‑Fi primary = XHTTP, не OVPN | vpn-43,56,44 |
| 3 | 3 этажа: direct / bridge / CDN в `/sub/` | vpn-43,50,52 |
| 4 | Бот простой язык, без жаргона | vpn-44,85,81 |
| 5 | 4G smoke + throttle alert | vpn-45,63 |
| 6 | Legal bridge RU | vpn-54 |
| 7 | Legal полный (параллельно ф2) | vpn-77 |
| 8 | Инцидент-плейбуки + dual SNI | vpn-70,53,80,76 |
| 9 | Investor + ML docs | vpn-68,41 |
| 10 | Autotests + CI /sub/ | vpn-72,84 |
| 11 | GA только после drill ×**4** ops | vpn-75 |
| 12 | Reserve EU IP | vpn-76 (v2) |
| 13 | Автовыбор профиля | vpn-78 (v2) |
| 14 | Resell | ❌ vpn-68 |
| 15 | MAIN bridge go/no-go задокументирован | vpn-82 |
| 16 | Статус-канал при инцидентах | vpn-83,34-posts |
| 17 | **HitWave** primary iOS (Happ legacy) | vpn-86 ✅ |
| 18 | Режим v6: спринты + gate G0–G4 | vpn-87, §11 |
| 19 | Integration Week G4 пройден | vpn-88, 56,55,79 |
| 20 | Pre-GA audit «6 шляп» | vpn-89 |
| 21 | Subscription URL — **один раз import**, не постоянно в бот | vpn-90, §12 |
| 22 | Post-payment pack (ссылка+QR+3 шага) | vpn-91 |
| 23 | HitWave Auto Update + «import один раз» | vpn-92 |
| 24 | OVPN/WG спрятаны в «Запасные» | vpn-93 |
| 25 | Deep link matrix задокументирована | vpn-94 |
| 26 | v2 **один Connect** (vpn-78) | vpn-78,95 |

---

## 6. Оценка бюджета и сроков

| Статья | EUR/мес | Примечание |
|--------|---------|------------|
| Contabo (есть) | ~€5 | egress |
| RU bridge VPS | €3–8 | Selectel/Yandex minimal |
| Cloudflare | €0 | Free plan достаточно для старта |
| Доп. IPv4 Contabo (опц.) | ~€2–4 | Reality :443 без mux |
| Reserve EU VPS (vpn-76, опц.) | ~€3–8 | второй egress |
| **Итого infra v1** | **~€8–17** | без труда |
| **Итого infra v2** | **~€11–25** | + reserve EU |

| Фаза | Календарь (v6) |
|------|----------------|
| Sprint 0 (G0) ✅ | doc + HitWave |
| Sprint 1 + G1 | неделя 1 |
| Sprint 2 + G2 | недели 2–3 |
| Sprint 3 + G3 | неделя 4 |
| Sprint 4 + G4 Integration Week | неделя 5 |
| Фаза 5 (v2) | после GA vpn-75 |

---

## 7. Риски и mitigations

| Риск | Mitigation |
|------|------------|
| Bridge IP не «белый» | Тест до покупки; запасной провайдер |
| CF блокируют | Профиль bridge остаётся |
| XHTTP fingerprinted | Ротация + sing-box clients |
| iOS нет клиента | **HitWave** + Hiddify / foreign Apple ID (vpn-86) |
| Legal RU bridge | vpn-54 + vpn-77 до масштаба |
| Contabo IP заблокирован целиком | vpn-76 reserve egress + vpn-70 playbook |
| UX «простой язык» (auto profile) | vpn-78 после GA; v1 vpn-85 |

---

## 9. Автоматизация (vpn-84) — полный реестр

### Уже есть ✅

| # | Автоматизация | Задача |
|---|---------------|--------|
| A1 | `vpn_prod_smoke.sh` на Contabo (timer ~15 min) | vpn-16 |
| A2 | `external_vpn_smoke.sh` (скрипт) | vpn-32 |
| A3 | Prometheus + Alertmanager → Telegram | vpn-15 |

### Добавить ⏳ (vpn-84)

| # | Автоматизация | Задача | Файлы |
|---|---------------|--------|-------|
| B1 | Throttle alert speed **<100 Kbit/s** | vpn-63 | ✅ `vpn_tunnel_speed_cron.sh` + alert rules |
| B2 | **CI:** pytest `/sub/` + QR buttons на каждый PR | vpn-84,72 | ✅ CI |
| B3 | **Cron:** `external_vpn_smoke.sh` → Telegram | vpn-84,45 | ✅ `vpn_external_smoke_cron.sh`; cron ⏳ |
| B4 | **Post-deploy:** MAIN bot inactive check | vpn-62,84 | ✅ |
| B5 | **Cron:** напоминание quarterly drill **×4 ops** | vpn-84 | ✅ `vpn_quarterly_drill_reminder.sh` |
| B6 | **Cron:** tunnel vs server speed | vpn-57,84 | ✅ `vpn_tunnel_speed_cron.sh` |
| B7 | Grafana success rate по профилю | vpn-69 | ✅ dashboard + Prom rules |
| B8 | **Автопост** статус-канал при smoke FAIL | vpn-83,84 | ✅ `vpn_ops_notify.sh` |
| B9 | Script pre-check bridge IP до VPS | vpn-64,84 | ✅ `vpn_bridge_ip_precheck.sh` |

### Не автоматизировать v1 ❌

- Ручной drill 4G с SIM (MF / MTS / Beeline / Tele2)
- Юрист (vpn-54, vpn-77)
- Финальный выбор SNI — ops + RealiTLScanner (vpn-53)

---

## 10. Не делать (зафиксировано)

- ❌ «VPN готов на всё» до drill ×4 ops (vpn-75)
- ❌ OpenVPN / WireGuard primary на 4G
- ❌ v2RayVPN (Ru Store)
- ❌ «Обход блокировок» в маркетинге
- ❌ IP Contabo, мост, Cloudflare, XHTTP, Reality пользователю
- ❌ Resell чужого VPN
- ❌ Hysteria/QUIC primary на mobile
- ❌ 4 равных протокола без подсказки «что на 4G»
- ❌ **Happ** как основной iOS-клиент (удалён из App Store) — см. **HitWave** (vpn-86)

---

## 11. Комбинированный режим выполнения v6 (vpn-87)

**Проблема «или всё сразу, или тест после каждой задачи»:** оба крайности плохи. **v6 = batch build по спринтам + автоматические gate между фазами + ручная Integration Week в конце.**

### 11.1 Три параллельных track

| Track | Что | Задачи | Deploy |
|-------|-----|--------|--------|
| **A — INFRA** | Contabo, bridge, CF, Xray, `/sub/` | vpn-42…52, 74, 64, 65, 67, 70 | по мере готовности на VPS |
| **B — PRODUCT** | бот, тексты, HitWave, инструкции | vpn-44, 59, 60, 61, 66, 81, 85, 86 ✅ | **1 deploy Contabo в конце каждого спринта**, если менялся Track B |
| **C — OPS/LEGAL** | legal, automation, guard, runbooks | vpn-77 (параллельно ф2), 54, 53, 62, 84, 45, 63 | scripts/cron без блокировки A |

**Правило:** внутри спринта **не** останавливаться на ручной 4G-проверке. Между спринтами — **только auto gate** (G1–G3).

### 11.2 Спринты и gate G0–G4

| Gate | Когда | Авто / ручное | Критерий PASS |
|------|-------|---------------|---------------|
| **G0** | Старт (✅) | doc | vpn-41, 68, 86, **87** |
| **G1** | Конец **Sprint 1** (ф1) | **авто** | `vpn_prod_smoke.sh` 10/10; `/sub/` `#wifi-direct` + `#mobile-xhttp`; pytest vpn-72 green |
| **G2** | Конец **Sprint 2** (ф2) | **авто** | `#mobile-bridge` в `/sub/`; bridge→Contabo hop smoke; vpn-82 go/no-go задокументирован |
| **G3** | Конец **Sprint 3** (ф3) | **авто** | `#mobile-cdn` в `/sub/`; CF origin health (vpn-67); playbook vpn-70 черновик |
| **G4** | **Integration Week** (ф4) | **ручное** | vpn-88: Wi‑Fi A/B (vpn-56) + 4G ×4 ops (vpn-55, 79) ≥1 Мбит/с ≥5 min; **vpn-89** audit; затем vpn-75 GA |

| Sprint | Содержание | Gate после |
|--------|------------|------------|
| **0** ✅ | Документы, HitWave deploy | G0 |
| **1** | vpn-42, 43, 44, 57–62, 71–74, 81, 85, **91–94** + старт vpn-77 | **G1** |
| **2** | vpn-82, 46–50, 64–66, 54 | **G2** |
| **3** | vpn-51, 52, 67, 70, 80 | **G3** |
| **4** | vpn-88 Integration Week, 53, 45, 63, 69, 83, 84, 89, **75** | **G4 → GA** |

**vpn-56 перенесён:** не блокирует Sprint 1; выполняется в **G4** вместе с drill (vpn-88).

**vpn-74 v1/v2:** v1 (8443) в Sprint 1; v2 (доп. IPv4 :443) — только если G4 drill FAIL на direct.

### 11.3 Gate checklist (копировать в ops)

**G1 — Sprint 1**
- [ ] XHTTP+Reality на Contabo (vpn-42)
- [ ] `/sub/` профили wifi + mobile-xhttp (vpn-43)
- [ ] `vpn_prod_smoke.sh` → 10/10
- [ ] pytest `/sub/` + QR (vpn-72)
- [ ] Один deploy бота Contabo (Track B batch)
- [ ] MAIN bot inactive check (vpn-62 / B4)

**G2 — Sprint 2**
- [ ] Bridge поднят (MAIN отд. порт или RU VPS per vpn-82)
- [ ] `#mobile-bridge` в `/sub/` (vpn-50)
- [ ] Auto-smoke bridge hop (не SIM)
- [ ] Legal bridge review стартовал (vpn-54)

**G3 — Sprint 3**
- [ ] CF CDN origin (vpn-51)
- [ ] `#mobile-cdn` в `/sub/` (vpn-52)
- [ ] CF health (vpn-67)
- [ ] **CDN DNS tiered** §11.6: ф0 reg.ru → ф1 grey / ф2 relay / ф3 CF по drill

**G4 — Integration Week (vpn-88)**
- [ ] Wi‑Fi: `#wifi-direct` vs OVPN A/B (vpn-56)
- [ ] 4G MegaFon, MTS, Beeline, Tele2 (vpn-55, 79) — speed ≥1 Мбит/с ≥5 min
- [ ] Журнал заполнен (`VPN_QUARTERLY_DRILL_CHECKLIST.md` § Integration Week)
- [ ] **vpn-89** Pre-GA audit §11.4 + §11.6 → все пункты ✅
- [ ] **vpn-75** → marketing GA разрешён

### 11.4 Аудит «6 шляп» → план (vpn-89)

| Шляпа | Вывод | Где в плане | Задачи |
|-------|-------|-------------|--------|
| ⚪ Белая (факты) | Contabo-only не держит 4G; HitWave в App Store; MAIN `:8002` священен | §1, §1.2, §1.2b | vpn-86 ✅, 82 |
| 🔴 Красная (риски UX) | Пользователь боится «сложного VPN» | §1.6 | vpn-44, 85, 81 |
| ⚫ Чёрная (риски) | Bridge IP, CF блок, legal RU, throttle | §7 | vpn-54, 77, 63, 76, 70 |
| 🟡 Жёлтая (выгоды) | 3 этажа = максимум покрытия при ~€8–17 | §2.3 | vpn-43, 50, 52 |
| 🟢 Зелёная (идеи) | Комбо: спринты + gate + Integration Week | **§11** | vpn-87, 88 |
| 🔵 Синяя (процесс) | Не тестировать 4G после каждой задачи; batch + G4 | **§11** | vpn-88, 89, 75 |

**Pre-GA (vpn-89):** пройти таблицу §5.1 (20 пунктов) + §11.4 + **§11.6** (tiered CDN DNS); зафиксировать дату и подпись ops в `VPN_QUARTERLY_DRILL_CHECKLIST.md`.

### 11.5 Что НЕ меняется

- Resell ❌
- Happ не primary (HitWave) ✅
- GA только после G4 + vpn-75
- Юрист и SIM-drill не автоматизируем (§9)
- **Egress всегда EU (Contabo)**; RU — только first hop (мост + опционально CDN relay), не единственный exit
- **Порядок профилей в `/sub/`:** мост → direct → CDN
- reg.ru нужен для **имени** `cdn`, не для «разрешения VPN»; куда направить A/CNAME — решает drill на 4G

### 11.6 Tiered CDN DNS + первый TCP на 4G (дополнение к §11.4, vpn-51/52/89)

**Принцип (лучший системный дизайн — каскад 3 профилей + поэтапный DNS CDN 1→2→3, не «сразу только Cloudflare»):**

| Слой | Пользователь (`/sub/`) | Первый TCP 4G | Egress |
|------|------------------------|---------------|--------|
| L1 | «Мобильный мост» | **MAIN (РФ)** `:8444` | EU Contabo |
| L2 | «Мобильный интернет» | **Contabo (EU)** `:8443` | EU Contabo |
| L3 | «Мобильный CDN» | **зависит от фазы DNS** | EU Contabo |

**Ops DNS `cdn.aladdin-ai.ru` — эволюция по drill (Contabo grey → MAIN relay → CF orange):**

| Фаза | DNS | Первый TCP CDN | Когда включать |
|------|-----|----------------|----------------|
| **0** | A `cdn` в reg.ru (минимум) | имя резолвится | **обязательно** — иначе профиль 3 мёртв |
| **1 grey** | A → Contabo `:8445` | EU, другие SNI | IP OK, режут SNI/fingerprint |
| **2 relay** | A → MAIN `:8445` → relay Contabo | **РФ** | foreign IP block (Contabo IP режут) |
| **3 CF orange** | CF proxy → origin `:443` | **CF edge** `:443` | Contabo IP в blocklist, CF проходит — «CDN‑страховка» |

**Таблица «куда первый TCP» (Integration Week ×4 — зафиксировать по операторам):**

| Что режет оператор | Лучший первый TCP | Профиль / DNS |
|--------------------|-------------------|---------------|
| Foreign IP | **РФ (MAIN)** | «Мобильный мост»; CDN: **ф2** cdn → MAIN relay |
| SNI / fingerprint, IP OK | **EU Contabo**, другие ключи | «Мобильный CDN» **ф1 grey** → Contabo `:8445` |
| Contabo IP в blocklist, CF OK | **Cloudflare edge** `:443` | **ф3** CF orange → origin Contabo; `VPN_CDN_PORT=443` |
| Всё режут | Нет серебряной пули | SNI rotation (vpn-80), reserve IP (vpn-76), status channel (vpn-83) |

**C (фаза 3)** — лучший для сценария «блокируют Contabo IP, CF проходит»; **не** замена моста при foreign IP block.

**Старт после ф0:** A `cdn` → Contabo (grey, **ф1**) **или** → MAIN (**ф2**) если drill уже показал IP block — выбор **ф1 или сразу ф2** по симптомам, не по теории.

**Чеклист:** `deploy/VPN_CDN_DNS_PHASE_CHECKLIST.md`

**План действий ops:**

- [ ] **0** A `cdn` в reg.ru
- [ ] **1** grey Contabo **или** **2** MAIN relay (nginx relay на MAIN ✅)
- [ ] **G4** Integration Week ×4 — матрица IP vs SNI vs CF по операторам (vpn-55, 56, 79, 88)
- [ ] **3** CF orange + `VPN_CDN_PORT=443` при необходимости (vpn-51, 67)
- [ ] **Legal** vpn-54 + vpn-77: RU transit + **CF как subprocessor**

---

## 12. UX подписки и onboarding (vpn-90)

**Вопрос:** «Пользователь постоянно берёт ссылку в боте?» — **Нет.** Модель industry-standard: **одна `/sub/` URL** → import **один раз** → **Auto Update** в клиенте.

### 12.1 Оценка «лучшее решение?»

| Аспект | Оценка | Задачи |
|--------|--------|--------|
| Архитектура РФ 4G (XHTTP+bridge+CDN) | ✅ лучшая практика anti-DPI | vpn-42…52 |
| Subscription URL | ✅ стандарт Xray/Marzban/3x-ui | vpn-43,90 |
| UX обычного пользователя | ⚠️ промежуточный | vpn-91…94, 81 |
| Идеал «как NordVPN» | ❌ без своего app | Tier 3 §12.4 |

**Вывод:** infra — **да**; UX — **улучшаем** Sprint 1 batch + **vpn-78** post-GA.

### 12.2 Уровень 1 — пользователь (Sprint 1, Track B)

| # | Действие | Задача | Эффект |
|---|----------|--------|--------|
| L1.1 | После оплаты: **ссылка + QR + 3 шага** одним сообщением | **vpn-91** | Не искать «📋 Ссылка VPN» |
| L1.2 | Тексты: **«import один раз»** + **Auto Update** HitWave | **vpn-92** | Не возвращаться в бот |
| L1.3 | Профили: **«Домашний Wi‑Fi»** / **«Мобильный интернет»** | **vpn-81** | Не `wifi-direct` в UI |
| L1.4 | OVPN/WG **только** «🔀 Запасные способы» | **vpn-93** | Меньше путаницы |
| L1.5 | Deep link matrix: HitWave paste · v2raytun для foreign ID | **vpn-94** | Честные альтернативы |

### 12.3 Уровень 2 — продукт (фаза 5, post-GA)

| # | Действие | Задача |
|---|----------|--------|
| L2.1 | **Один профиль Connect** — сервер выбирает transport | **vpn-78** |
| L2.2 | Bridge/CDN fallback **на сервере**, не ручной выбор | vpn-78 + vpn-50,52 |

### 12.4 Уровень 3 — опционально после GA

| Вариант | Плюсы | Минусы | Статус |
|---------|-------|--------|--------|
| **Своё iOS app** | NordVPN-level UX, deep link | Дорого, Store | backlog |
| **Mini App** | мастер оплата→import | dev | **vpn-39** ⏸ |
| **Landing `/i/{code}`** | QR в браузере | ещё surface | **vpn-95** |

### 12.5 Проверка с телефона (чеклист)

- [ ] После оплаты ссылка **в чате автоматически** (vpn-91)
- [ ] HitWave → Import **один раз** → Auto Update ON (vpn-92)
- [ ] Профили: «Домашний Wi‑Fi» / «Мобильный интернет»
- [ ] 4G → speedtest **≥1 Мбит/с ≥5 min** (G4, vpn-88)
- [ ] Повторно в бот — только новый телефон / поломка

### 12.6 Sprint 1 Track B (batch UX)

```
vpn-91 → vpn-92 → vpn-93 → vpn-94 параллельно vpn-81, vpn-85
→ один deploy бота Contabo → G1
```

---

## 8. Версия

| Дата | Изменение |
|------|-----------|
| 2026-06-27 | v1–v3: вариант 3, vpn-41…78, DoD |
| 2026-06-28 | v4: Tele2, vpn-79…85, automation §9, Cursor 45 |
| 2026-06-28 | v5: HitWave iOS (vpn-86), MAIN bridge (§1.2), vpn-74 v1/v2, B1–B9 |
| 2026-06-28 | **v6:** комбинированный режим §11, Integration Week, audit 6 шляп, Cursor 49 |
| 2026-06-28 | **v7.1:** §11.6 tiered CDN DNS (grey→relay→CF), VPN_CDN_DNS_PHASE_CHECKLIST |
