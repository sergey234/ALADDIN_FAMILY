# ALADDIN Wellness + Companion — дорожная карта до 100%

> **Для кого:** PO, iOS, backend, другая ML-система (handoff).  
> **Рабочая папка:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
> **Обновлено:** 2026-06-03 (PO: Hermes/OpenRouter → **батч 7**, вместе с Rive; работаем батч 4 без ключей)  
> **Ядро платформы:** 131/131 + PO 133/134 ([WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md))  
> **Canary rollout:** **не делаем** (по решению PO — сразу 100% при включённых флагах).

---

## Часть 1. Простыми словами — как устроены герои

### 1.1 Что такое «герой» в коде?

Это **не отдельная нейросеть на каждого персонажа**. Это **один общий чат-ИИ** (Hermes/OpenRouter), которому перед каждым ответом подставляют **инструкцию**:

1. **Кто ты** — Единорог / Аладдин / Джин + стиль (дружелюбный, наставник, игривый…).  
   Файл: `security/services/ai_platform/companion_persona.py`

2. **В какой «дорожке» самопомощи** сейчас разговор — разобрать мысли / маленькие шаги / принять себя / понять себя.  
   Файлы: `wellness_orchestrator.py`, `wellness_prompt_builder.py`

3. **Что нельзя говорить** — без диагноза, без «терапии», при кризисе — 112 и взрослый.  
   Файлы: `companion_ethics.py`, `wellness_escalation.py`, guard после ответа.

**Аналогия:** один актёр (LLM), разный **сценарий и костюм** (промпт), а не три разных актёра с нуля.

---

### 1.2 Почему НЕ fine-tune (дообучение модели)?

| Fine-tune (дообучение) | Наш способ (Knowledge Pack + промпты) |
|------------------------|----------------------------------------|
| Дорого, долго, сложно обновлять | Меняем текст в YAML/JSON — быстро |
| Сложно контролировать кризис и детей | Правила в коде **до** и **после** LLM |
| 3 героя × 4 дорожки = 12 моделей? | **1 LLM** + 3 голоса (flavor) + 4 сценария (pack) |

**«Обучение» героев у нас значит:**

| Термин | Простыми словами | Где в проекте |
|--------|------------------|---------------|
| **Knowledge Pack** | Готовый «учебник» для одной дорожки: что можно говорить, что запрещено, шаги упражнений | `security/services/ai_platform/wellness_knowledge/*/v1/pack.yaml` |
| **Промпты** | Текст-инструкция, который видит LLM перед ответом (герой + дорожка + возраст) | `companion_persona.py`, `wellness_prompt_builder.py`, prefix в `ai_companion_router.py` |
| **Метрики** | Смотрим, помогло ли: оценка после упражнения, усталость от дорожки, смена дорожки | `wellness_outcomes.py`, `wellness_pillar_fatigue.py`, recap |
| **Голос** | Как герой звучит: STT → ответ → TTS, эмоция на экране | iOS `CompanionConversationScreen`, caps voice realtime |

---

### 1.3 Что такое Knowledge Pack и `status: draft`?

**Knowledge Pack** — файл `pack.yaml` для одной дорожки (cognitive / behavioral / humanistic / jung).

Внутри:

- `allowed_topics` — о чём можно говорить в этой сессии  
- `forbidden_concepts` — чего нельзя (диагноз, другие школы…)  
- `hero_flavor` — как **тот же смысл** говорит Единорог vs Аладдин vs Джин  
- шаги упражнений (часть текста в JSON/i18n)

**`status: draft`** = черновик: текст есть, но **внешний или клинический ревьюер ещё не подписал**, что это безопасно для детей/подростков/родителей.

**`status: approved`** = можно считать продакшен-каноном; smoke-тесты на запрещённые слова обязаны проходить.

Сейчас все 4 pack — **draft** → продукт **технически работает**, но **содержание не финализировано**.

---

### 1.4 Как сообщение доходит от кнопки до ответа героя

```
Пользователь пишет/говорит в чат
    → iOS шлёт character_id + wellness_pillar (выбранная дорожка)
    → Сервер собирает: [личность героя] + [блок wellness из pack] + [сообщение]
    → Hermes отвечает
    → Сервер проверяет: не «утекла» ли другая дорожка/диагноз
    → iOS показывает текст + эмоцию героя
```

iOS почти всегда передаёт `wellness_pillar` из `WellnessSessionStore.activePillar` — см. `CompanionAPIService.swift`.

---

## Часть 2. Шесть шляп — продукт сейчас и лучший путь

### 🤍 Белая шляпа — факты

- 131 задача wellness в коде — **закрыты**.  
- Backend на VPS, prod verify **14/14**.  
- iOS: 25/25 `Wellness*.swift` в таргете; UX-спринты 1–3 (вкладки, Hub, «столп» убран).  
- 4 Knowledge Pack — **draft**.  
- Postgres: dual-write есть, **read cutover** (`WELLNESS_PG_READ=1`) — ещё нет.  
- Parent LLM: код есть, на проде часто `llm_used: false` без ключей Hermes.  
- **Canary** — **не делаем** (решение PO).

### ❤️ Красная — чувства пользователя

**Плюсы:** тёплые герои, семейный контекст, не «сухой психолог», ребёнок защищён.  
**Минусы:** если LLM тормозит или отвечает шаблонно — ощущение «робот», не Grok.

### 🖤 Чёрная — риски

- Jung/глубокие темы без clinical sign-off.  
- Drift: герой смешивает дорожки в одном ответе (есть guard, но нужен мониторинг).  
- Родитель видит не то age_band (частично исправлено resolver).  
- HealthKit/App Store — отдельный PO-трек.

### 💛 Жёлтая — плюсы

- Один backend, этика L3, family-first.  
- 4 дорожки = структурированная самопомощь без слова «КПТ» в UI.  
- Уже близко к «Grok» по голосу и чату, плюс уникальная семейная ценность.

### 💚 Зелёная — творчество / лучший вариант

**Лучший вариант (рекомендация PO+тех):**

1. **Не** fine-tune.  
2. **Да** — довести pack до `approved` + матрица герой×дорожка.  
3. **Да** — ops: PG read + Hermes + мониторинг + TestFlight.  
4. **Да** — ощущение «живого» (recap, голос, streaming позже).  
5. **Нет** — canary по % (пропускаем).

### 💙 Синяя — процесс и порядок работ

**Спринт A (ops + правда на проде)** → **Спринт B (герои + контент)** → полировка iOS/widget → App Store.

---

## Часть 3. Продукт уже хороший?

| Вопрос | Ответ |
|--------|--------|
| Можно показывать бете? | **Да** — функционал широкий, prod smoke OK. |
| Это финальный «идеал»? | **Нет** — pack draft, PG read, LLM parent, widget, внешний clinical. |
| Оценка сейчас | **~85% инженерия**, **~60% «душа героев»** (контент+LLM стабильность) |

**Вывод:** продукт **уже сильный MVP+**, лучший путь — **углубить канон (pack) + ops + UX на устройстве**, а не переписывать архитектуру.

---

## Часть 3б. «Лучший вариант» — простыми словами

**Не ломаем дом** (архитектуру: один чат, один LLM, 4 дорожки в промпте).

**Доделываем четыре вещи:**

| Шаг | Простыми словами | id в todo |
|-----|------------------|-----------|
| **Pack** | Утвердить «сценарии уроков» для 4 дорожек (сейчас черновик) | `r100-4-*`, `r100-7-10` в конце |
| **Hermes** | Чтобы ИИ на сервере реально отвечал (ключи + флаг родительского playbook) | `r100-0-03`, `r100-0-04` |
| **PG** | Перенести чтение wellness-данных в Postgres (запись уже dual-write) | `r100-1-04` |
| **UX на телефоне** | TestFlight, навигация, подписи героев, без «столп» | `r100-0-01`, `r100-0-05`, `r100-3-hero-*` |

**Rive** (единый: [RIVE_MASTER_PLAN.md](./RIVE_MASTER_PLAN.md) — **02b→07** 3× `.riv`, **07b** Wellness Hub), **clinical**, **sleep**, **docs** — **в самом конце** (батч 7).

---

## Часть 3в. Уже сделано — не делать второй раз

| Тема | Статус | id в todo |
|------|--------|-----------|
| Ядро 131/131 wellness + companion API | ✅ Закрыто 2026-06-01 | — |
| UX спринты 1–3 (4 вкладки, Hub perf, «столп», баннеры) | ✅ В коде | — |
| Deploy sprint3: age_band + reflective JSON | ✅ На VPS | — |
| `verify_wellness_reflective_prod` | ✅ | `r100-0-06` **done** |
| Postgres **миграция + dual-write** | ✅ ~160 rows | Не повторять migrate; только **read cutover** `r100-1-04` |
| `FEATURE_WELLNESS_PARENT_LLM=1` на VPS | ⚠️ Мог быть включён, но **llm_used всё ещё false** без ключей | Проверить `r100-0-03` + `r100-0-04` |
| Prod verify 14/14 | ✅ Исторически | `r100-0-02` = **повторять после каждого deploy**, не «с нуля» |
| Canary 5→25→100 | ❌ **Не делаем** | Нет id |
| Подписи героев + убрать «Стиль по умолчанию» | ✅ В репо 2026-06-03 | `r100-3-hero-*` → **done** после deploy BE taglines |

---

## Часть 3г. Sleep CDN (`r100-7-08`) — что это?

**Простыми словами:** в wellness есть **«истории для сна»** (спокойное аудио перед сном, в основном для взрослых/60+).

Сейчас API `GET /api/wellness/sleep/stories` отдаёт **список**, но **ссылки на mp3** должны вести на **реальный CDN** (облако с файлами), а не заглушки.

**Что сделать позже (батч 7):**

1. Залить 5–10 mp3 на CDN (S3/сервер).  
2. Прописать URL в JSON на backend.  
3. iOS: скачать/кэшировать, кнопка «слушать» в Hub или senior flow.

**Не блокирует** Спринт A (pack + Hermes + PG + телефон).

---

## Часть 4. Что значит 100% (три уровня)

| Уровень | Простыми словами | Критерии готовности |
|---------|------------------|---------------------|
| **100% инженерия** | Всё включено и не ломается | PG read, widget в Store, CI тесты, prod 14/14, po-healthkit решён, **без canary** |
| **100% герои** | Герои правда помогают по 4 дорожкам | 4 pack `approved`, flavor matrix, drift под контролем, parent LLM `llm_used: true`, UX на device OK |
| **100% продукт** | Рынок и доверие | TestFlight отзывы, внешний clinical, premium воронка, 30 дней без срывов L3 |

---

## Часть 5. План задач для другой ML (батчи + id)

Используй **TodoWrite** в Cursor с id `r100-*`.  
Связанные доки: [WELLNESS_POSTGRES_MIGRATION.md](./WELLNESS_POSTGRES_MIGRATION.md), [WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md](./WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md), [WELLNESS_CANARY_RUNBOOK.md](./WELLNESS_CANARY_RUNBOOK.md) (справочно; **rollout не выполняем**).

---

### Батч 0 — Спринт A: прод работает честно (P0)

| id | Задача | Что делать | Как проверить (DoD) |
|----|--------|------------|---------------------|
| `r100-0-01` | TestFlight UX | Собрать билд после UX 1–3; прогнать 15 пунктов на iPhone | Нет блокеров; список багов пуст или в backlog |
| `r100-0-02` | Prod verify | После каждого backend deploy | `./scripts/verify_wellness_prod.sh https://aladdin-ai.ru` → 14/14 |
| `r100-0-05` | Embedded nav | Ручной тест: Companion → вкладка wellness → exercise → назад → «Поговорить с героем» | Не выкидывает на Main; `actionErrorText` виден при ошибке |
| `r100-0-06` | Reflective prod | Уже есть скрипт | `./scripts/verify_wellness_reflective_prod.sh` — hint без «столп» |

> **Перенесено в батч 7 (конец):** `r100-0-03` Hermes/OpenRouter keys, `r100-0-04` Parent LLM `llm_used` — вместе с Rive. До ключей: чат на SFM/fallback, playbook — 6 фраз из JSON.

---

### Батч 1 — Ops и данные (P0) — **без Canary**

| id | Задача | Что делать | DoD |
|----|--------|------------|-----|
| `r100-1-04` | Postgres read cutover | 7 дней `WELLNESS_PG_DUAL_WRITE=1` → затем `WELLNESS_PG_READ=1` | `GET /api/wellness/store/backend` → `"backend":"postgres"` |
| `r100-1-15` | Мониторинг | Логи/метрики: Hub latency, `guard_reason`, chat 5xx, pillar drift | Дашборд или ежедневный скрипт + алерт |
| `r100-1-16` | Premium воронка | Paywall → StoreKit → `premium/eligibility` | Покупка/restore на staging; blocked без подписки где нужно |
| ~~r100-1-05~~ | ~~Canary~~ | **Отменено PO** | Оставить `WELLNESS_CANARY_PERCENT=100` |

**PG cutover (кратко):**

1. `docs/WELLNESS_POSTGRES_MIGRATION.md`  
2. `migrate_wellness_sqlite_to_pg.py` уже гоняли — проверить row count  
3. Dual-write 7 дней → `WELLNESS_PG_READ=1`  
4. `verify_wellness_prod.sh`  
5. Rollback: `WELLNESS_PG_READ=0`

---

### Батч 2 — iOS completeness (P1)

| id | Задача | DoD |
|----|--------|-----|
| `r100-2-06` | Widget | `MANUAL_WIDGET_SETUP.md` + target `ALADDINWidgets` | Виджет «Как ты?» открывает check-in |
| `r100-2-11` | Unit tests | `WellnessModelsTests.swift` в `ALADDINUnitTests` | CI green |
| `r100-2-12` | E2E UI | Сценарии: 4 вкладки, Hub embed, reflective→mic, companion CTA | XCTest/Maestro зелёный |
| `r100-2-13` | Navigation | `companionReturnScreen` для embedded wellness | Таблица переходов в комментарии к PR |
| `r100-2-14` | Glossary | `WELLNESS_I18N_GLOSSARY.md`: UI «дорожка», код `pillar` | `check_wellness_l10n.py` без user-facing «столп» |

---

### Батч 3 — Подписи героев (вкладка «Герои») — P0, быстрый UX

Экран: `CompanionHomeScreen` → вкладка **Герои** → `CompanionHubScreen`.

| id | Было | Стало | Файлы |
|----|------|-------|-------|
| `r100-3-hero-unicorn` | «Тёплый магический компаньон для детей» | **«Магический друг для детей»** | `ai_companion_router.py` CHARACTERS |
| `r100-3-hero-aladdin` | «Мудрый наставник-человек (не джин)» | **«Мудрый наставник»** | то же |
| `r100-3-hero-genie` | «Магический остроумный спутник» | без изменений текста | то же |
| `r100-3-hero-style` | Было «Стиль по умолчанию: …» | **Только слово:** Единорог→Игривый, Аладдин→Спокойный, Джин→Остроумный | `CompanionHubScreen.swift` + keys `companion_hero_style_*` |

**DoD:** на вкладке «Герои» только имя + одна строка tagline; после deploy BE — tagline с API совпадает.

**Deploy taglines на VPS:**

```bash
./scripts/deploy_companion_p0.sh root 149.154.65.180 ~/.ssh/aladdin_server
# или scp только ai_companion_router.py + restart
```

---

### Батч 4 — Герои «мозг» (P0 ядро продукта)

#### 4.1 Knowledge Pack → production

**«Уточнить тексты упражнений»** — простыми словами: в `pack.yaml` для каждой дорожки дописать/выровнять:
- **`hint`** — что видит пользователь на шаге упражнения в Hub;
- **`instruction`** — что герой должен сказать на этом шаге (один вопрос, без других дорожек);
- **`llm_rules`** — общие правила тона для всей сессии чата по этой дорожке.

Это **не** обучение модели: меняем YAML → деплой → Hermes/SFM читают новый prefix. `status: draft` до clinical (батч 7).

| id | Дорожка | Сделать |
|----|---------|---------|
| `r100-4-cog` | cognitive | Сценарии thought record; child/teen короче; smoke forbidden |
| `r100-4-beh` | behavioral | Связь с habits API; if-then примеры |
| `r100-4-hum` | humanistic | «Побудь рядом» после reflective; STOP/дыхание |
| `r100-4-jung` | jung | 5 reflective modes; без предсказаний |

**DoD батча 4.1:** `pytest Tests/test_wellness_pillar_prompts.py` + запрещённые фразы ru/en.

#### 4.2 Матрица герой × дорожка

| id | Задача |
|----|--------|
| `r100-4-flavor` | Заполнить `hero_flavor` в каждом `pack.yaml` для unicorn, aladdin, genie |

Таблица тонов — см. Часть 6 ниже.

#### 4.3 Поведение «живой компаньон»

| id | Механизм | Действие |
|----|----------|----------|
| `r100-4-recap` | Continuity | Строка recap над чатом iOS + уже есть в prefix |
| `r100-4-memory` | Memory | Parent/teen: chips по consent, не дословный child chat |
| `r100-4-outcome` | Outcome 24h | Связать «хуже» → fatigue → смена дорожки |
| `r100-4-drift` | Drift | Лог `apply_response_guard`; weekly 50 логов |
| `r100-4-voice` | Voice | STT→LLM→TTS latency; emotion sync |

---

### Батч 5 — Grok-подобный UX (P2)

| id | Задача |
|----|--------|
| `r100-5-stream` | Streaming текста в чате |
| `r100-5-voice` | Стабильный hold-to-talk, reconnect |
| `r100-5-proactive` | После check-in → CTA к герою с выбранной дорожкой |
| `r100-5-ethics` | Не ослаблять L3; не показывать родителю чат teen |

---

### Батч 6 — Релиз (ongoing)

| id | Задача |
|----|--------|
| `r100-6-store` | App Store metadata, скриншоты 4 вкладок |
| `r100-6-healthkit` | po-healthkit: Portal (A) или оставить B |
| `r100-6-ab` | Hub copy A/B аналитика |
| `r100-6-regress` | 110 pytest + iOS tests перед deploy |

---

### Батч 7 — Контент, медиа, Hermes (**в самом конце**, после батчей 0–6)

> PO: Rive, Hermes keys, clinical, sleep — **не начинать**, пока не закрыты батч 4 (pack/flavor/recap) и батч 5 по желанию.

| id | Задача | DoD |
|----|--------|-----|
| `r100-7-07` | Rive **HERO-3-07b** | Те же 3× `Resources/Companion/*.riv` + Hub; art = **[COMPANION_HERO_ART_CANON](./COMPANION_HERO_ART_CANON.md)** 02b→07 — **[RIVE_MASTER_PLAN](./RIVE_MASTER_PLAN.md)** |
| `r100-0-03` | **Hermes / OpenRouter keys** | `.env`: валидный `OPENROUTER_API_KEY` или `HERMES_OPENROUTER_API_KEYS`; `chat_once` без 401 |
| `r100-0-04` | **Parent LLM live** | `FEATURE_WELLNESS_PARENT_LLM=1` + restart; playbook `use_llm=true` → `llm_used: true` |
| `r100-7-08` | Sleep CDN | Реальные mp3 URL + iOS кэш (см. Часть 3г) |
| `r100-7-10` | Clinical sign-off | 4 pack → `status: approved` |
| `r100-7-docs` | Docs cleanup | Внутренние docs «столп»→«дорожка» (не UI) |

**Команды Hermes (батч 7, когда PO даст ключ):**

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180
cd /opt/aladdin-backend
grep -E 'FEATURE_WELLNESS_PARENT_LLM|OPENROUTER' .env
systemctl restart aladdin-backend.service
curl -sS -H "Authorization: Bearer TOKEN" \
  "https://aladdin-ai.ru/api/wellness/parent/playbook?use_llm=true&locale=ru" | python3 -m json.tool
```

---

## Часть 6. Матрица «герой × дорожка» (flavor)

| Дорожка | Единорог | Аладдин | Джин |
|---------|----------|---------|------|
| cognitive | «как пазл, по кусочку» | один чёткий вопрос | одна лёгкая образная фраза |
| behavioral | «один маленький шаг» | план только на сегодня | шутка **только** если не грусть (L0) |
| humanistic | тишина, «я рядом» | наставник без нравоучений | **без** шуток если грустно |
| jung | образы без страха | спокойный смысл | сказочный образ, **не** предсказание |

Править: `wellness_knowledge/<pillar>/v1/pack.yaml` → `hero_flavor`.

---

## Часть 7. Сводная таблица пробелов (Canary исключён)

| # | Пробел | id | Батч | P | Владелец |
|---|--------|-----|------|---|----------|
| — | TestFlight UX | r100-0-01 | 0 | P0 | PO + iOS |
| 9 | Parent LLM + Hermes | r100-0-03, r100-0-04 | **7 (конец)** | P1 | Backend ops + PO key |
| 13 | Embedded nav | r100-0-05 | 0 | P0 | iOS |
| 4 | PG read | r100-1-04 | 1 | P0 | Backend ops |
| ~~5~~ | ~~Canary~~ | — | — | **N/A** | **Не делаем** |
| 15 | Мониторинг | r100-1-15 | 1 | P0 | DevOps |
| 16 | Premium | r100-1-16 | 1 | P1 | Product |
| 6 | Widget | r100-2-06 | 2 | P1 | iOS |
| 11 | Unit CI | r100-2-11 | 2 | P1 | iOS |
| 12 | E2E | r100-2-12 | 2 | P1 | QA |
| 14 | Glossary | r100-2-14 | 2 | P2 | Docs |
| 7 | Rive (3 riv + 07b Hub) | r100-7-07 | **7 (конец)** | P1 | Art: [COMPANION_HERO_ART_CANON](./COMPANION_HERO_ART_CANON.md) |
| 8 | Sleep CDN | r100-7-08 | **7 (конец)** | P1 | BE+iOS |
| 10 | Clinical | r100-7-10 | **7 (конец)** | P0 | PO+внешний |
| — | Hero taglines UI | r100-3-hero-* | **3** | P0 | iOS+BE |
| — | 4 pack approved | r100-4-* | 4 | P0 | Content+BE |
| — | Flavor matrix | r100-4-flavor | 4 | P0 | Content |
| — | Grok-like | r100-5-* | 5 | P2 | iOS+BE |

---

## Часть 7б. Что дальше

| Приоритет | id | Задача |
|-----------|-----|--------|
| **Сейчас** | `r100-2-13` | Embedded wellness → exercise → назад в Companion (не Main) |
| **Сейчас** | `r100-2-06`, `r100-2-11` | Widget + unit tests в CI |
| ~~Сейчас~~ | ~~r100-5-voice~~ | ✅ hold-to-talk + WS reconnect + chat fallback |
| ~~Сейчас~~ | ~~r100-5-stream~~ | ✅ уже `streamMessage` |
| **Потом** | `r100-0-01`, `r100-0-05` | TestFlight + nav smoke (после iOS сборки) |
| ~~Сейчас~~ | ~~r100-4-*~~ | ✅ flavor, recap, drift, pack texts, memory, outcome |
| **Потом** | `r100-0-01`, `r100-0-05` | TestFlight + nav smoke |
| **Потом** | `r100-1-04` | PG read после 7 дней dual-write |
| **Потом** | `r100-5-stream`, `r100-5-voice` | Streaming + устойчивый голос |
| **В конце** | `r100-7-07`, `r100-0-03`, `r100-0-04` | **Rive** ([RIVE_MASTER_PLAN](./RIVE_MASTER_PLAN.md): 07 + 07b) **+ Hermes + Parent LLM** |
| **В конце** | `r100-7-08`, `r100-7-10` | Sleep CDN, clinical → `approved` |
| **Один прогон** | — | См. **[WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md)** — всё накопленное BE+iOS |

---

## Часть 7в. Deploy backlog (не сейчас)

PO: выкат **после** закрытия нужного по плану. Полный чеклист: [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md).

Кратко: `deploy_wellness_batch4.sh` + `deploy_companion_p0.sh` → `verify_wellness_prod.sh` 14/14 → TestFlight с recap/memory/outcome/nav.

---

## Часть 8. Первое сообщение для новой ML (скопировать)

```text
Работай только в:
/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

Прочитай:
1) docs/WELLNESS_ML_HANDOFF_R100.md (главный handoff для продолжения)
2) docs/WELLNESS_ROADMAP_100.md (этот план)
3) docs/WELLNESS_IMPLEMENTATION_STATUS.md (131/131 + 2026-06-02 + Wellness*.swift)
4) docs/WELLNESS_DEPLOY_BACKLOG.md (деплой отложен)
5) docs/WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md

Спринт B (сейчас, без OpenRouter):
- r100-4-flavor матрица 3×4 в pack.yaml
- r100-4-recap над чатом Companion
- r100-4-drift лог на BE
- r100-4-cog/beh/hum/jung тексты (status draft до clinical)

Спринт A (параллельно по готовности):
- r100-0-02 prod verify после deploy
- r100-1-04 PG read (после 7d dual-write)
- r100-0-01 TestFlight + r100-0-05 nav smoke

Позже: r100-5-stream, r100-5-voice

В конце (батч 7): Rive [RIVE_MASTER_PLAN](./RIVE_MASTER_PLAN.md) (02b→07, 07b Hub QA) + r100-0-03/0-04 Hermes + r100-7-08 sleep. Clinical ✅ hero-x-30.

Уже в репо (проверить на device + deploy BE): r100-3-hero-* taglines, без «Стиль по умолчанию»

НЕ ДЕЛАТЬ: canary 5%→25% (PO отменил). WELLNESS_CANARY_PERCENT=100.

Сервер: root@149.154.65.180, /opt/aladdin-backend, ~/.ssh/aladdin_server
Prod: https://aladdin-ai.ru
После deploy: verify_wellness_prod.sh 14/14
```

---

*Связано: WELLNESS_CURSOR_TODO.md (131 ядро), UX спринты 1–3 в чате 2026-06.*
