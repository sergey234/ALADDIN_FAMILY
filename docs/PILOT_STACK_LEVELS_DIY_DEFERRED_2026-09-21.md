# Levels DIY ($249→$1) — разбор и решение для ALADDIN

**Статус:** ALADDIN OPS — отложено · **отдельный продукт scrape** — см. решение FetchLite  
**Канон отдельного продукта:** [`docs/PRODUCT_FETCHLITE_LEVELS_STYLE_SOLUTION_2026-09-21.md`](PRODUCT_FETCHLITE_LEVELS_STYLE_SOLUTION_2026-09-21.md)  
**TODO id:** `ps-levels-diy-scraper` (разбор) · продукт FetchLite — отдельный GO  
**Дата:** 2026-09-21

---

## 0. Уточнение владельца

Levels-стиль scrape = **другой продукт**, не фича iOS и не «Firecrawl для Hermes».  
Ниже — старый контекст «для ALADDIN OPS»; полное **как сделать** — в FetchLite-доке.

## 1. Суть статьи (просто)

Питер Левелс (соло, Nomads / Remote OK / Photo AI):

- Платил ~**$249/мес** за сервис «открой сайт → обойди блоки → верни данные».  
- Собрал **свой узкий** скрипт под **свои** продукты → ~**$1/мес** · ~90% запросов ок.  
- Дальше тем же методом: модерация ИИ вместо людей, NSFW на бесплатной модели, свои скрипты картинок, open-source для карт/видео/мониторинга.  
- Оценка экономии до ~$25k/мес (подписки **+** люди).  
- Принцип: **инфраструктуру оставить снаружи** (домены, VPS, storage, LLM API), **забрать только свою бизнес-логику**. Не клонировать Calendly/Zapier целиком — одну форму / три сценария.

---

## 2. Можно ли «по образу» у ALADDIN?

**Да, как философия. Нет — как один большой «наш Browserless для рынка».**

| Levels-подход | У ALADDIN |
|---------------|-----------|
| Узкий скрипт под свой продукт | ✅ совпадает с Mech Pilot / минимальный diff |
| Не строить SaaS для всех | ✅ bot≠iOS, не раздувать scope |
| Инфра снаружи, логика своя | ✅ уже Contabo/FirstVDS + свои API |
| Резать дорогие SaaS | ⚠️ сначала **инвентарь подписок** — что реально платим |

У нас уже есть «свои» куски вместо SaaS: antifake moderation queue, family chat moderation API, orch на Mac, Repowise, VPN stack. Нет смысла строить публичный scraper-SaaS.

---

## 3. Что у нас уже «по Levels» (не делать заново)

| Область | Уже есть | Не клонировать |
|---------|----------|----------------|
| Модерация / жалобы | antifake reports + family chat moderation | чужой Trust&Safety SaaS «на всё» |
| Агенты / ночь | Coding Orchestrator | второй Nightcafe-оркестратор |
| Карта кода | Repowise | Trailhq Graft constantly (только ROI) |
| Секреты / mesh | ADMIN_MESH план | Aperture-vault всего |
| Локальный LLM draft | пилот Bonsai | платный «всегда online» draft API |

---

## 4. Где идея Levels реально может дать $ (кандидаты)

Делать **только после** Pilot Stack и только с инвентарём чеков:

| Кандидат | Levels-логика | Риск для ALADDIN |
|----------|---------------|------------------|
| **A. Узкий fetch HTML/API** для своих OPS (health, цены конкурентов VPN, App Store metadata) | Свой cron + httpx/playwright на Brain/Mac | Юр./ToS сайтов; не скрапить без нужды |
| **B. NSFW / image triage** для UGC (если платим Vision API) | Локальная/дешёвая модель + свой порог | False positive на детский контент — ** Critial**; нужен human path |
| **C. Картинки** (resize/watermark) вместо Cloudinary-класса | `sips` / libvips / свой worker | Уже частично локально в iOS pipeline |
| **D. Мониторинг uptime** вместо дорогого ping-SaaS | cron + curl + Telegram alert (у нас уже health-паттерны) | Низкий |
| **E. Формы / запись** | одна страница, не Typeform | Низкий приоритет |

**Не кандидат:** «полный антибот-браузерный scraper как сервис» — дорого в поддержке, серая зона, не core ALADDIN (family safety / VPN / bot shop).

---

## 5. Рекомендуемое решение (когда дойдём до конца плана)

### Вариант выбранный: **«Levels Lite для ALADDIN OPS»** (не marketplace)

1. **Инвентарь 30 мин:** список платных API/SaaS (OpenAI vision, scraping, uptime, image CDN, Zapier-like).  
2. Выбрать **1** строку с max $/мес и узким use-case.  
3. Сделать **один** скрипт/worker на уже существующем узле (🇩🇪 Brain или Mac orch), без нового продукта.  
4. GATES: % успеха · $/мес · время поддержки ≤1ч/нед · ask-before-ops.  
5. Если ROI слабый — выключить (как Graft/Bonsai вердикт).

### Не делать

- Публичный «ALADDIN Scraper Cloud»  
- Замена модерации parental/antifake на «бесплатную модель без человека»  
- Параллельно с Bonsai install / Tailscale (размыть фокус)

---

## 6. Чеклист внедрения (позже)

- [ ] Pilot Stack: Bonsai ROI вердикт **или** сознательный skip железа  
- [ ] Admin Phase 0 хотя бы прочитан/GO решён  
- [ ] Инвентарь подписок  
- [ ] GO владельца: `GO Levels Lite — <конкретный SaaS>`  
- [ ] Минимальный worker + journal ROI 2 недели  

---

## 7. Связь с текущим стартом

Сейчас выполняем **без GO:** baseline Bonsai + runtime research + admin plan read.  
Levels остаётся в TODO `ps-levels-diy-scraper` как **отложенный** трек.
