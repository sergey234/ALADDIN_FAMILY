# Business ALADDIN — START HERE (волна E / метрики / рост)

**Для владельца и ML.** Это **отдельный контур** от iOS-кода и Coding Orchestrator.  
Глобальный роутер репо: [`docs/ML_SYSTEM_START_HERE.md`](../ML_SYSTEM_START_HERE.md).  
Короткий запрет «не в iOS commit»: [`.cursor/ASMADY_BUSINESS_OUT_OF_IOS.md`](../../.cursor/ASMADY_BUSINESS_OUT_OF_IOS.md).

| Поле | Значение |
|------|----------|
| **ID трека** | `asm-r-12` / `asm-60` (Asmadey wave E) |
| **Дата** | 2026-09-21 · **пилот гибрид 1+2:** [`HYBRID_1_2_PILOT_PLAN_RU.md`](HYBRID_1_2_PILOT_PLAN_RU.md) (`h12-*`, VPN вне трека) · **семья vs POSI b2c:** [`PLAN_FAMILY_VS_POSI_HYBRID_2026-10-15.md`](PLAN_FAMILY_VS_POSI_HYBRID_2026-10-15.md) (`fvp-*`) · one-pager [`COMPETITIVE_POSI_B2C_ONEPAGER_2026-10-15.md`](COMPETITIVE_POSI_B2C_ONEPAGER_2026-10-15.md) |
| **Тарифы и рост (Life360) — SSOT** | [`PLAN_LIFE360_GROWTH_TARIFFS_2026-11-18.md`](PLAN_LIFE360_GROWTH_TARIFFS_2026-11-18.md) (`l360-*`) — решения, 6 замков доступа, тексты RU/EN, задачи с файлами и строками |
| **Статус** | Канон готов · живые сессии — **по фразе владельца** |
| **Куда класть артефакты** | `docs/business/` (этот каталог) · Notion/Sheets — ок · **не** `Screens/` · **не** `feat(build N)` |

---

## 0. Зачем это отдельно

В Asmadey есть skills про **pricing, growth, SEO, Metrika, landing, market research**.  
Мы **не** вшили их constantly в Cursor рядом с `@aladdin-gates`, чтобы:

1. не смешивать бизнес-эксперименты с App Store / parental / VPN secrets;  
2. агент не «заодно» коммитил SEO в iOS-релиз;  
3. владелец явно открывал **бизнес-сессию**.

Этот файл = **что можно сделать + по каким метрикам оценивать + как работать лучше всего**.

---

## 1. Что агент МОЖЕТ сделать (меню)

Одна сессия = **один фокус** из таблицы.

| Фокус | Что делаем | Типичный выход | Откуда идея (Asmadey) |
|-------|------------|----------------|----------------------|
| **E1 Pricing** | Тарифная сетка Individual / Family / Premium / VPN / Stars; freemium vs paid | 1 страница цен + правила апсейла (факты из StoreKit/бот, без выдуманных цифр) | `pricing-strategy` |
| **E2 Growth** | Воронка: установка → Antifake/Voice → подписка → referral | Карта воронки + 1–2 рычага retention | `growth-expert` |
| **E3 SEO / AEO** | Поисковая/ИИ-выдача по RU: antifake, родительский контроль, семейная защита | 1 ключ + outline **или** цикл «делай loop» по канону | `landing/` hybrid · `seo-audit` · optional `aeo-geo` (GO) |

**Канон SEO/AEO для сайта ALADDIN (не путать):** loop = **`landing/` hybrid** (`SEO_LOOP_RUNBOOK.md` · `seo_*_prompt.md` · GSC CSV → «делай loop» → стоп до «ок теме» / «ок к деплою»).  
**Не** Sanity / Railway / SerpAPI / auto-cron фабрика **для aladdin-ai.ru**. VPN-витрина Stars ≠ blog aladdin-ai.ru.

**Зачем блог / что дают статьи / кадренс / эффект 1–12 мес (SSOT для ML):**  
[`landing/docs/SEO_LOOP_RUNBOOK.md`](../../landing/docs/SEO_LOOP_RUNBOOK.md) **§0** — читать **до** массовой генерации статей.  
Кратко: поиск + доверие + AEO + мост к продукту; **не** мгновенные продажи; 1 тема/неделя + «ок к деплою»; без пачек за ночь.

**Отдельный продукт Editorial OS / SEO-AEO Studio** (не ALADDIN, личное + SaaS):  
[`SEO_AEO_GEO_PRODUCT_MASTER_PLAN_2026-09-29.md`](SEO_AEO_GEO_PRODUCT_MASTER_PLAN_2026-09-29.md) · registry `sap-*` · **не** смешивать с `ado-f*`.  
Дубликат roadmap статей: `seo-aeo-studio/docs/WHAT_ARTICLES_GIVE_AND_ROADMAP.md` (вне iOS-релиза).
| **E4 Metrika / Wordstat** | Что меряем сейчас vs что нужно для гипотезы | Список целей/событий + gap | `yandex-metrika` · `yandex-wordstat` |
| **E5 Landing / оффер** | Один экран посадочной под оффер семьи | Wire + copy (с anti-slop) | `landing-page-design` |
| **E6 Market / ЦА** | Сегменты родителя, боли, конкуренты | ½–1 стр. HeroesGPT-style brief | `HeroesGPT` · `consulting` |
| **E7 Sales enablement** | Скрипты/возражения для бота и поддержки | Battle card (Stars/Premium/VPN) | `sales-enablement` |

**Salesforce in Claude (Anthropic plugin):** **не** продукт ALADDIN. У нас нет Salesforce SoR — CRM = bot **CRM v3** + admin. Идеи brief/prep/follow-up → шаблоны в `docs/business/` и `docs/ops-memory/` (см. `PLAN_ADOPT_UNIFIED_2026-09-29.md` волна A). Личный Claude×SF — только вне репо, если появится SF org.

**Не делать в business-сессии без отдельного GO:** diy-mcp, agent-reach (волна D), Dark Factory, RN/shadcn, правки `Screens/*.swift` «для конверсии», Salesforce MCP в Cursor.

---

## 2. По каким параметрам оценивать (метрики)

Считаем успех **измеримо**. Если цифр нет — сначала E4 (instrumentation), не «красивый план».

### North-star (семья / ALADDIN)

| Метрика | Простыми словами | Хороший знак |
|---------|------------------|--------------|
| **Activated parent** | Родитель сделал ≥1 защитное действие (Antifake check / Voice «ссылка» / parental) | Растёт неделя к неделе |
| **Time-to-first-check** | Минуты от открытия app до первой проверки ссылки/звонка | ↓ к &lt;2 мин (см. JTBD Voice) |
| **Paid conversion** | Trial/IAP → оплата (StoreKit) или Stars/VPN в боте | Стабильный % без «фейковых» скидок |
| **Retention D7 / D30** | Вернулся и снова использовал защиту | D7 важнее «установок» |
| **Referral / family expand** | Пригласил члена семьи / второй девайс | Только честный organic + рефералка |

### По фокусу сессии

| Фокус | KPI сессии (выбрать 1–2) |
|-------|---------------------------|
| E1 Pricing | Понятность тарифа (опрос 5 родителей / support tickets «непонятна цена» ↓) · ARPU / payback (если есть факты) |
| E2 Growth | Шаг воронки с самым большим drop-off · одна гипотеза «если X → conversion +N%» |
| E3 SEO/AEO | 1 целевой запрос · позиция/упоминание **или** готовый publishable draft |
| E4 Metrika | Список событий, которых не хватает для B4-гипотезы · владельцу — что внедрить в app/бот (отдельный GO на код) |
| E5 Landing | CTR hero→CTA · bounce (если есть Metrika) · anti-slop checklist PASS |
| E6 Market | 1 сегмент + 1 оффер + 3 «не делать» |
| E7 Sales | 5 возражений с ответами без воды (`@aladdin-humanizer-ru`) |

### Красные флаги (плохой результат сессии)

- Выдуманные цены / CAC / LTV без источника  
- «Давайте перепишем весь app» без одной метрики  
- Коммит в iOS release или bot+iOS вперемешку  
- Секреты Metrika/API tokens в git или чат  

---

## 3. Как сделать наилучшим образом

```text
1. Владелец: новый чат + фраза из §5
2. ML: читает ЭТОТ файл → выбирает один фокус E1…E7
3. Сначала факты (StoreKit / бот / Metrika / текущие MD) — потом рекомендации
4. Связка с продуктом: если нужна проверка в app → сформулировать hypothesis (B4) и отдать в iOS-чат отдельно
5. Артефакт → docs/business/<дата>_<фокус>.md
6. Коммит business-доков — только по просьбе; никогда вместе с feat(build N)
```

### Порядок «деньги ↔ продукт»

| Сначала | Потом |
|---------|--------|
| B4 hypothesis (что проверяем у родителя) | E2/E1 (как монетизировать / растить) |
| E4 Metrika gaps | Код аналитики (отдельный iOS/bot GO) |
| E5 landing copy | B3 anti-slop на тот же surface |

### Рекомендуемый первый спринт E0 (если владелец сказал «просто начни business»)

1. **E1 Pricing clarity** — одна страница фактов по тарифам (без выдумок).  
2. **E4** — gap метрик под Voice→Antifake JTBD.  
3. **E2** — один рычаг воронки (не пять).

---

## 4. Связь с другими канонами

| Тема | Файл |
|------|------|
| Глобальный вход | [`docs/ML_SYSTEM_START_HERE.md`](../ML_SYSTEM_START_HERE.md) |
| Asmadey skills / волна E id | [`.cursor/ASMADY_SKILLS_ML_HANDOFF.md`](../../.cursor/ASMADY_SKILLS_ML_HANDOFF.md) · `REMAINING_PLAN` `asm-r-12` |
| Как вести B/C/E | [`.cursor/ASMADY_WAVES_BCE_PLAN.md`](../../.cursor/ASMADY_WAVES_BCE_PLAN.md) § волна E |
| JTBD родитель / Voice | `.cursor/ASMADY_PILOT_JOURNAL.md` · `@aladdin-ajtbd` |
| Запрет в iOS commit | [`.cursor/ASMADY_BUSINESS_OUT_OF_IOS.md`](../../.cursor/ASMADY_BUSINESS_OUT_OF_IOS.md) |
| Bot / Stars / VPN деньги | bot handoff + VPN playbook — **отдельные** чаты, не смешивать с этим файлом без нужды |

Thin Cursor skills для бизнеса **пока не обязательны**: достаточно этого канона + явной фразы владельца. При повторяемости — завести `aladdin-pricing` / `aladdin-growth` через `@aladdin-skill-creator` + sandbox.

---

## 5. Фразы владельца (копипаст)

**Универсальная**
```text
Прочитай docs/ML_SYSTEM_START_HERE.md → docs/business/ML_SYSTEM_BUSINESS_START_HERE.md.
Сессия Business, фокус E1 Pricing. Вне iOS commits. Без выдуманных цен.
```

**Growth**
```text
Business E2 Growth: воронка Antifake/Voice → подписка. Одна гипотеза + KPI.
```

**SEO**
```text
Business E3 SEO / AEO: канон landing/docs/SEO_LOOP_RUNBOOK.md + seo_*_prompt.md.
Один RU-ключ · «делай loop» · не Sanity/Railway. Outline или статья → стоп до ок теме / ок к деплою.
```

**Метрики**
```text
Business E4: какие события нужны, чтобы проверить Voice→Antifake &lt;2 мин. Список gap.
```

---

## 6. Definition of Done — одна business-сессия

- [ ] Выбран ровно один фокус E1…E7  
- [ ] Есть 1–2 KPI из §2  
- [ ] Артефакт в `docs/business/` (или явно «только в чат, без файла» по просьбе владельца)  
- [ ] Нет коммита в iOS release / нет секретов  
- [ ] Если нужен код app/bot — отдельный next-step + GO, не «заодно»  

---

*Конец Business START_HERE. Следующий агент: §3 → §5.*
