# AiMonkey — сводный план (Stars + VPN + РКН)

**Дата:** 2026-06-30  
**Статус:** согласовано в сессии диагностики (Contabo + MAIN + OneXray)  
**SSOT TODO в Cursor:** список задач в чате (`stars-ux`, `vpn-vision`, …)  
**Связанные документы:**  
`VPN_RESILIENT_ARCHITECTURE_PLAN_2026.md` · `VPN_PUBLIC_SURFACE_REGISTRY.md` · `VPN_FULL_SESSION_HANDOFF_ML_2026-06-27.md`

---

## 0. Чеклист «ничего не забыли»

| # | Что выяснили | В плане | TODO |
|---|--------------|---------|------|
| 1 | Stars: только 100 / 500 / 1000+ + ручной ввод с авто-ценой | §2 | `stars-ux` |
| 2 | Stars: авто-выдача ON на проде, мин. 50 | §2.3 | `stars-auto-ff` |
| 3 | Кнопки CopyText обрезались → callback + URL в тексте (deploy `20260630`) | §3.0 | `vpn-copy-buttons` ✅ |
| 4 | `flow=""` (нет Vision) на direct | §4.1 | `vpn-vision` |
| 5 | Мост нужен на 4G (без него не работало) | §4.2 | — (решение: оставить) |
| 6 | 2× xhttp на мосте → 2–5 Мбит/с, зависания | §4.2 | `vpn-bridge-tcp`, `vpn-wg-internal` |
| 7 | Wi‑Fi → «Домашний Wi‑Fi»; 4G → «Мобильный интернет» (не мост primary) | §4.3 | `stars-user-guide` |
| 8 | CDN слабый, SSL mismatch на `cdn.aladdin-ai.ru` | §4.4 | `vpn-cdn-cf` |
| 9 | Зависшие xhttp-сессии (HTTP/2 CANCEL), Telegram жив, веб мёртв | §4.5 | `vpn-ops` |
| 10 | Зеркало `.com` для `/sub/` (не для скорости) | §5 | `vpn-domain-com` |
| 11 | Риск блокировки РКН `.ru` | §5.2 | `vpn-rkn-mitigation` |
| 12 | Сравнение с VPNUS (`eu-fffast.com`, IP Москва) | §6 | — |
| 13 | Метод 6 шляп | §7 | — |
| 14 | Один Connect + авто-fallback (vpn-78) | §4.6 | `vpn-ux-auto` |
| 15 | G4 drill ×4 оператора | §8 | `vpn-phone-drill` |
| 16 | Сервер Contabo ~20 Мбит/с egress | §6 | — |
| 17 | Подписка: 4 профиля (Wi‑Fi, 4G direct, мост, CDN) | §4 | — |
| 18 | Идея: MAIN→Contabo через WG internal | §4.2 | `vpn-wg-internal` |
| 19 | Три режима в подписке вместо 4 путаницы | §4.6 | часть `vpn-ux-auto` |
| 20 | Кастом Stars &lt; 50 → только ручная выдача | §2.3 | в `stars-ux` |

**Вывод:** все согласованные пункты из диалога отражены в плане и TODO.

---

## 1. Итог одной фразой

**Мост на 4G оставляем**, но **упрощаем транспорт** (Vision, меньше xhttp, опционально WG между MAIN↔Contabo). На **Wi‑Fi всегда direct**. **CDN и `.com`** — для **надёжности обновления подписки**, не для «магической» скорости. **Stars** — упростить витрину и добавить ручной ввод с авто-ценой.

---

## 2. Stars (бот)

### 2.1 Текущее состояние (`bot/products.yaml`)

| ID | Stars | Действие |
|----|-------|----------|
| stars_100 | 100 | оставить |
| stars_300 | 300 | **скрыть** (`hide_from_menu: true`) |
| stars_500 | 500 | оставить |
| stars_1000 | 1000 | оставить, подпись **«1000+»** |
| stars_2000 | 2000 | **скрыть** |
| stars_5000 | 5000 | **скрыть** |

Кастомного ввода **пока нет** — только фиксированные пакеты.

### 2.2 Реализация (`stars-ux`)

1. Кнопки: **100** · **500** · **1000+** · **✏️ Своё количество**
2. FSM: пользователь вводит число (целое, ≥ 50)
3. Цена: `qty × (price_usd stars_100 / 100) × USD_RUB` + реф. скидка + опт от `stars_wholesale_threshold`
4. Превью цены **до** оплаты (идея из зелёной шляпы)
5. Заказ: `product_id=stars_custom`, `stars_qty=N` в metadata
6. Файлы: `shop.py`, `shop_kb.py`, `catalog.py`, `pricing.py`, новый handler FSM

### 2.3 Авто-выдача (`stars-auto-ff`)

| Параметр | Значение (prod) |
|----------|-----------------|
| `AUTO_FULFILL_ENABLED` | true |
| `AUTO_FULFILL_STARS_ENABLED` | true |
| `AUTO_FULFILL_MAX_ORDER_RUB` | 50 000 |
| Минимум qty | **50** (`auto_fulfill_policy.py`) |

**Тест DoD:** оплата тестового заказа 100 Stars + кастом 150 Stars → iStar → Stars на @username без оператора.

---

## 3. VPN — UX (сделано / в работе)

### 3.0 Сделано ✅

- **CopyText** на две половинки «Ссылка | Скопировать» → **callback-кнопки** + полный URL в `<code>`
- Deploy: `20260630-135654`
- Файлы: `vpn_user_links.py`, `vpn_screen_nav.py`, `vpn.py`, `vpn_post_purchase_delivery.py`

### 3.1 Инструкция пользователю (`stars-user-guide`)

| Сеть | Профиль в OneXray |
|------|-------------------|
| Wi‑Fi дома | **Домашний Wi‑Fi** |
| 4G (первый выбор) | **Мобильный интернет** |
| 4G если direct не коннектится | **Мобильный мост** |
| 4G авария | **Мобильный CDN** (после `vpn-cdn-cf`) |

После смены профиля: **Disconnect → Update подписки → Connect**.

---

## 4. VPN — техническая архитектура

### 4.1 Vision (`xtls-rprx-vision`) — `vpn-vision`

**Что значит «flow пусто»:** клиент ходит VLESS+xhttp **без** режима Vision. DPI 2025–2026 чаще режет такой трафик.

| | Сейчас | Цель (direct) |
|--|--------|---------------|
| flow | пусто | `xtls-rprx-vision` |
| транспорт | xhttp | **A/B:** xhttp+Vision или TCP+Vision |
| где | все 4 профиля | сначала **:8443 direct** (Wi‑Fi + 4G direct) |

**Важно:** в `VPN_RESILIENT_ARCHITECTURE_PLAN_2026.md` ранее было «без vision on mobile». Новое решение: **A/B на staging**, не выкатывать всем сразу (`vpn-vision`).

**Нужно ли:** **да**, для устойчивости и скорости direct-путей. Не заменяет мост на 4G.

### 4.2 Мост — сравнительный анализ

```
Без моста (4G direct):     Телефон ──xhttp──► Contabo (DE)     → часто таймаут
С мостом (сейчас):         Телефон ──xhttp──► MAIN ──xhttp──► Contabo → 2–5 Мбит/с, зависания
Цель (мост v2):            Телефон ──TCP+Vision──► MAIN ──WG/TCP──► Contabo → быстрее, меньше CANCEL
Wi‑Fi (direct):            Телефон ──TCP+Vision──► Contabo → 10–25+ Мбит/с
```

| Критерий | Без моста 4G | Мост xhttp×2 (сейчас) | Мост TCP+Vision / WG (`vpn-bridge-tcp`, `vpn-wg-internal`) |
|----------|--------------|----------------------|-------------------------------------------------------------|
| Подключение на MegaFon | ❌ часто нет | ✅ есть | ✅ ожидаем |
| Скорость | — | 2–5 Мбит/с | 5–15+ Мбит/с (цель) |
| Зависшие сессии | — | часто | реже |
| Зачем ML сказал «мост нужен» | — | обход DPI на первом hop | то же, но лучший транспорт |

**Решение:** мост **не убираем** на 4G. Меняем **только транспорт** между MAIN↔Contabo.

### 4.3 Текущие 4 профиля в подписке

| Профиль | Host | Проблема |
|---------|------|----------|
| Домашний Wi‑Fi | vpn.aladdin-ai.ru:8443 | нет Vision |
| Мобильный интернет | vpn.aladdin-ai.ru:8443 | нет Vision |
| Мобильный мост | 149.154.65.180:8444 | 2× xhttp |
| Мобильный CDN | cdn.aladdin-ai.ru:8445 | SSL mismatch, слабый |

### 4.4 CDN — `vpn-cdn-cf`

| | VPNUS (вероятно) | Мы сейчас |
|--|------------------|-----------|
| CDN | Cloudflare (настоящий) | `cdn.aladdin-ai.ru` → MAIN, cert mismatch |
| SNI | cloudflare.com | cdn.aladdin-ai.ru ❌ |

**DoD:** smoke без SSL error; SNI = `www.cloudflare.com` или валидный CF cert; orange cloud опционально.

### 4.5 Зависшие сессии и `vpn-ops` — **делать, это правильный шаг**

| Симптом | Причина | Мера |
|---------|---------|------|
| HTTP/2 CANCEL в логах xray | зомби xhttp-сессии | `connIdle`, `downlinkOnly` policy |
| UI «Connected», fast.com мёртв | мост + xhttp | restart моста + **корневая** смена на TCP+Vision |
| Telegram работает, веб нет | UDP/TCP разный путь DPI | алерт «веб мёртв 15 мин» |

**`vpn-ops` — не замена Vision, а страховка:**

1. `connIdle` / timeouts в xray (MAIN + Contabo)
2. Ночной `systemctl restart xray-bridge` (cron + healthcheck)
3. Алерт: egress OK + DNS OK + HTTP к fast.com fail 15 мин → Telegram ops
4. Runbook: пользователю «Disconnect → Update → другой профиль»

**Вердикт:** **да, делать.** Снижает боль до выката протокольных фиксов.

### 4.6 UX продукта — `vpn-ux-auto` (vpn-78)

Цель: **одна кнопка Connect**, сервер/клиент выбирает профиль:

1. Wi‑Fi → direct  
2. 4G → direct, fallback мост, fallback CDN  
3. В подписке оставить 3 имени вместо 4 (скрыть дубли через remark/priority)

---

## 5. РКН и домены

### 5.1 `subs.aladdin-ai.com` → тот же API `/sub/` — правильно ли?

**Да, как зеркало для обновления подписки — с оговорками.**

| Вопрос | Ответ |
|--------|-------|
| Ускорит VPN? | **Нет** |
| Поможет если заблокируют **имя** `aladdin-ai.ru`? | **Да** — OneXray Update по `.com` |
| Поможет если заблокируют **IP** `149.154.65.180`? | **Нет**, если `.com` на тот же IP |
| Как у VPNUS? | `eu-fffast.com`, но IP подписки **Москва** — `.com` ≠ «европейский сервер» |

**Правильная схема (`vpn-domain-com`):**

```
PRIMARY (не менять сразу):  https://aladdin-ai.ru/sub/<token>
MIRROR (в боте второй ряд): https://subs.aladdin-ai.com/sub/<token>
```

**Техника:**

1. DNS `subs.aladdin-ai.com` → **Cloudflare proxy (orange)** → origin Contabo `:8091` **или** MAIN nginx  
2. Тот же `location /sub/` proxy_pass, тот же TLS на origin  
3. В боте: основная ссылка `.ru`, кнопка **«Зеркало подписки (.com)»**  
4. Мониторинг: HTTP 200 обоих URL каждые 5 мин  
5. **Не** рекламировать `.com` как «быстрее» — только «если не обновляется»

**Риски зеркала:**

- Два домена в реестре — теоретически двойной риск **если** жалобы массовые  
- На практике зеркало **снижает** операционный риск (бизнес не встаёт при блокировке primary)

### 5.2 Заблокирует ли РКН `aladdin-ai.ru`?

**Риск есть, уровень — средний**, зависит не от TLD, а от:

| Фактор | Риск |
|--------|------|
| Публичная реклама VPN / обход блокировок | высокий |
| Жалобы правообладателей / пользователей | высокий |
| Домен в открытых списках VPN-сервисов | средний |
| Только Telegram-бот + без агрессивного SEO | ниже |
| Разделение: сайт магазина vs `vpn.*` | снижает ущерб |

**Что блокируют чаще:**

1. Путь `/sub/` и домен `vpn.aladdin-ai.ru` (техническая поверхность)  
2. IP egress Contabo при массовом DPI  
3. Реже — весь `aladdin-ai.ru` (магазин Stars + legal)

### 5.3 Как снизить риск РКН (`vpn-rkn-mitigation`)

| # | Мера | Зачем |
|---|------|-------|
| 1 | **Разделение ролей доменов** (реестр `VPN_PUBLIC_SURFACE_REGISTRY.md`) | блок одного не убивает всё |
| 2 | **Зеркало `subs.*.com` за Cloudflare** | другой IP для HTTP подписки |
| 3 | **Не светить VPN в основном лендинге** Stars-магазина | меньше поводов для жалоб |
| 4 | **Legal / AUP** на отдельных URL (`/v1/legal/vpn-*`) | compliance |
| 5 | **Мониторинг реестра РКН** (cron + ручной weekly) | раннее предупреждение |
| 6 | **Запасной origin IP** (vpn-74 второй IPv4 Contabo) | блок IP, не домена |
| 7 | **Тихий бренд** на `.com` (нейтральное имя subs) | не привязка к aladdin в DNS TXT |
| 8 | **Инструкции только в боте**, не на индексируемом сайте | SEO-поверхность |
| 9 | **Rate limit /sub/** + opaque token | anti-scrape |
| 10 | **План B:** выдача vless строкой в боте при падении `/sub/` | ручной канал |

**Не помогает от РКН:** смена только TLD без смены IP/CF; «секретный» порт без DPI-устойчивого протокола.

---

## 6. Сравнение: VPNUS vs AiMonkeyVPN

| Критерий | VPNUS (`eu-fffast.com`) | AiMonkeyVPN | Что улучшить |
|----------|-------------------------|-------------|--------------|
| Подписка | `.com`, своё app | `.ru`, OneXray | зеркало `.com` |
| IP подписки | Москва | MAIN Москва + Contabo DE | ок для моста |
| Импорт | 1 тап `vpnus://` | ручной URL | `vpn-ux-auto` |
| Профили | app выбирает | 4 вручную | один Connect |
| Протокол | TCP+Vision (типично) | xhttp, без Vision | `vpn-vision` P1 |
| 4G | 1 hop или умный мост | 2× xhttp на мосте | `vpn-bridge-tcp` |
| CDN | CF | слабый | `vpn-cdn-cf` |
| Скорость сервера EU | — | ~20 Мбит/с | ок |
| Мост на 4G | да | да | оставить, упростить транспорт |

---

## 7. Метод 6 шляп (сводка)

| Шляпа | Вывод |
|-------|-------|
| 🤍 Белая | Contabo ~20 Мбит/с; авто Stars ON; VPNUS IP Москва; flow пусто; CDN SSL mismatch |
| ❤️ Красная | «Connected, сайты мертвы» = xhttp+мост; 2–5 Мбит/с ожидаемо на мосте |
| 🖤 Чёрная | Vision без A/B ломает клиентов; отказ от моста = 4G fail; `.com` без CF = слабое зеркало |
| 💛 Жёлтая | Wi‑Fi+Vision ≈ VPNUS; умный fallback; кастом Stars; `.com` = живой Update |
| 💚 Зелёная | 3 режима; vpn-78; WG internal hop; превью цены Stars |
| 💙 Синяя | фазы A→B→C ниже |

---

## 8. Фазы выполнения

### Фаза A — быстрые победы (1–3 дня)

| # | Задача | ID |
|---|--------|-----|
| 1 | Stars меню 100/500/1000+ + своё количество | `stars-ux` |
| 2 | Тест авто-выдачи Stars | `stars-auto-ff` |
| 3 | Инструкция Wi‑Fi / 4G в боте | `stars-user-guide` |
| 4 | xray timeouts + restart моста + алерт | `vpn-ops` |
| 5 | Мониторинг реестра РКН + чеклист | `vpn-rkn-mitigation` (часть 1) |

### Фаза B — скорость VPN (1–2 недели)

| # | Задача | ID |
|---|--------|-----|
| 6 | Vision на direct :8443 (A/B) | `vpn-vision` |
| 7 | Мост: TCP+Vision вместо xhttp×2 | `vpn-bridge-tcp` |
| 8 | MAIN↔Contabo WG internal (A/B) | `vpn-wg-internal` |
| 9 | CDN Cloudflare | `vpn-cdn-cf` |

### Фаза C — надёжность (2–4 недели)

| # | Задача | ID |
|---|--------|-----|
| 10 | Зеркало `subs.aladdin-ai.com` + CF | `vpn-domain-com` |
| 11 | Один Connect + авто-fallback | `vpn-ux-auto` |
| 12 | G4 drill ×4 оператора, ≥1 Мбит/с 5 мин | `vpn-phone-drill` |
| 13 | Полный RKN playbook в runbook | `vpn-rkn-mitigation` (часть 2) |

---

## 9. Cursor TODO (полный список)

| ID | Статус | Задача |
|----|--------|--------|
| `stars-ux` | pending | Stars: 100/500/1000+ + своё кол-во + авто-цена |
| `stars-auto-ff` | pending | Проверка авто-выдачи на проде |
| `stars-user-guide` | pending | Инструкция Wi‑Fi/4G в боте после VPN |
| `vpn-copy-buttons` | **done** | CopyText → callback (deploy 20260630) |
| `vpn-vision` | pending | Vision на direct-профилях |
| `vpn-bridge-tcp` | pending | Мост: TCP+Vision вместо xhttp×2 |
| `vpn-wg-internal` | pending | A/B WG hop MAIN→Contabo |
| `vpn-cdn-cf` | pending | CDN + Cloudflare |
| `vpn-domain-com` | pending | Зеркало subs.aladdin-ai.com (secondary) |
| `vpn-ux-auto` | pending | Один Connect + авто-fallback |
| `vpn-ops` | pending | connIdle, restart, алерт «веб мёртв» |
| `vpn-phone-drill` | pending | G4 drill ×4 оператора |
| `vpn-rkn-mitigation` | pending | РКН: домены, мониторинг, playbook |

---

## 10. Ответы на прямые вопросы

### «`subs.aladdin-ai.com` — точно правильное решение?»

**Да, как вторичное зеркало `/sub/` за Cloudflare.** Не primary, не для скорости. Primary остаётся `aladdin-ai.ru` пока не заблокируют.

### «РКН заблокирует aladdin-ai.ru?»

**Возможно, но не неизбежно.** Выше риск у `vpn.*` и `/sub/`, чем у всего домена. Зеркало + CF + разделение ролей + мониторинг — **правильная страховка**.

### «`vpn-ops` (connIdle, restart, алерт) — точно делать?»

**Да.** Это операционная страховка от симптома «Telegram есть, веб мёртв». Корневая причина — xhttp+мост; ops не отменяет `vpn-vision` / `vpn-bridge-tcp`, а дополняет.

---

*Обновлять этот файл при закрытии каждой задачи из §9.*
