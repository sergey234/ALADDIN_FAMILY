# План усиления героев — юмор, мудрость, глубина, эмпатия

> **Дата:** 2026-06-04 (v2 — expert review + PO refinements)  
> **Статус:** ✅ **COMPLETE (37/37)** — 2026-06-04  
> **Задач:** **37** (`hero-x-00`…`hero-x-69`, из них **3 backlog**)  
> **Аудитория:** ML-система (Cursor / Claude / GPT), продолжающая r100  
> **Рабочая папка:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
> **Связано:** [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md) · [WELLNESS_ML_HANDOFF_R100.md](./WELLNESS_ML_HANDOFF_R100.md) · [WELLNESS_CLINICAL_REVIEW.md](./WELLNESS_CLINICAL_REVIEW.md)

---

## 0. Сообщение для новой ML (скопировать в чат)

```text
Реализуй docs/WELLNESS_HERO_PERSONA_ENHANCEMENT_PLAN.md — усиление героев (hero-x-* todo).

Папка: …/mobile_apps/ALADDIN_iOS · ветка master.

Порядок v2: hero-x-00 → 01-09+44 (parallel) → 06 → 10-15 → 14 → 20-24 → 40-43 → 50-52+65 → 30 → 60-64.
Prod blockers: 08, 63, 07, 44, 15, 24.

Жёстко: не ломать child-safe, L3, forbidden_phrases в pack.yaml, prod-no-mock-bypass.
Юмор: много у Джина, но НЕ каждый ответ; иногда PG-сарказм про ситуацию.
Ведическая линия: принципы Gita/Mahabharata БЕЗ религиозных слов в ответах user.
Пользователю НЕ говорить «психоанализ», «диагноз», «терапия», «лечу» — plain-language самопомощь.

После BE: deploy_wellness_batch4 + deploy_companion_p0 → verify_wellness_prod 14/14.
pytest ≥40 cases; golden set hero-x-07; companion guard hero-x-08 — hard gate prod.
```

---

## 0.1 Уточнения PO после expert review (2026-06-04)

| Тема | Решение PO |
|------|------------|
| **Юмор Джина** | Много юмора, **но не в каждом ответе** — не стендап. Баланс через `humor_frequency` в tiers.yaml (~60–70% при playful/L0, ~40% при neutral). **Иногда** лёгкий сарказм PG (про ситуацию, не про человека). Max = **cap**, не flood. |
| **Ведическая линия** | Знания из Gita/Mahabharata передаются **без упоминания религии** в ответах пользователю: нет «бог», «храм», «молитва», «вера», названий традиций. Framing: «древняя мудрость», «вечные принципы». Internal id `gita_lite` — только в YAML, не в UI. |
| **Pattern reflection** | Не «ты третий раз…» каждый диалог — max **1 раз / 10 turns**, только при явной теме; opt-out hint; без ощущения слежки. |
| **Любая тема** | Мягкий отказ человеческим языком; при низкой уверенности домена — не robotic redirect (hero-x-43). |
| **Герои** | Узнаваемые, но **не навязчивые** — retention через характер, не через давление. |

---

## 1. Цели PO (что хотим)

| # | Запрос PO | Как трактуем в продукте |
|---|-----------|-------------------------|
| 1 | **Сильнее юмор у всех; у Джина — максимум** | PG/PG-13; **много, но не каждый ответ**; иногда сарказм PG (ситуация, не человек); **0 шуток** при sad/L2/L3 |
| 2 | **Джин + Аладдин — мудрость Махабхараты / Бхагavad Gita** | Knowledge слой: **пересказ принципов** (dharma, karma, equanimity) **без религиозной лексики** в ответах; опционально по возрасту |
| 3 | **Все герои — «в совершенстве» психология и психоанализ** | **Внутренние** инструкции LLM + расширенные pack; **в UI/ответах** — простой язык, без названий школ и без «я ваш терапевт» |
| 4 | **Максимальная эмпатия** | Усилить mood routing, validation, reflective listening в persona + intent |
| 5 | **Любая тема** | Расширить домены диалога + мягкий redirect на безопасные границы (не NSFW, не illegal, не medical diagnosis) |

---

## 2. Ограничения (не нарушать)

Из [WELLNESS_CLINICAL_REVIEW.md](./WELLNESS_CLINICAL_REVIEW.md) и существующих `pack.yaml`:

| Запрет | Почему |
|--------|--------|
| Слова «диагноз», «терапия», «лечу», «КПТ», «Юнг», «Фрейд» **в ответах пользователю** | PO checklist, App Store, child safety |
| Позиция «замена психолога / врача» | Юридический риск |
| Шутки при кризисе (L2/L3), self-harm, насилие | Ethics r100-5-ethics |
| Родитель видит teen-chat дословно | Privacy |
| Fine-tune отдельной модели на героя | Архитектурное решение PO — только prompts + Knowledge Pack |
| Проповедь / конверсия в религию | Семейное приложение, разные культуры |

**Формулировка для пользователя:** «мудрый друг», «помогаю разобраться», «опора из древних текстов» — не «психоанализ» и не «духовный наставник».

---

## 3. Архитектура (куда класть изменения)

```
Сообщение пользователя
  → companion_intent_router.py     # mood, domain, humor_density, empathy_hint, escalation
  → companion_ethics.py            # L0–L3 → hero-x-03 wiring
  → [NEW] companion_prompt_assembler.py  # hero-x-09: priority stack + token budget
  → companion_persona.py           # базовый system prompt героя
  → [NEW] companion_wisdom.py      # vedic / empathy snippets по character_id
  → [NEW] companion_knowledge/psychology/  # internal YAML (не показывать user)
  → wellness_prompt_builder.py     # если активна wellness-сессия → pack.yaml
  → apply_response_guard           # wellness pillar
  → [NEW] companion_response_guard.py  # hero-x-08: free chat forbidden phrases
  → Hermes/OpenRouter LLM
```

**Priority stack (hero-x-09):** ethics/L3 → wellness pack → psych internal → wisdom → humor hint → persona. При переполнении budget — отрезаются нижние слои, **никогда** ethics/wellness.

| Слой | Файлы сегодня | После плана |
|------|---------------|-------------|
| Юмор | `companion_persona.py`, `companion_intent_router.py`, `companion_characters.py`, `pack.yaml` hero_flavor | + `humor/v1/tiers.yaml` (SSOT + **escalation_matrix** + **humor_frequency** + sarcasm rules) |
| Post-LLM guard | wellness only | + **`companion_response_guard.py`** для free chat |
| Golden set | — | `Tests/fixtures/companion_golden/` + CI scorer (**hero-x-07**) |
| Ведическая мудрость | — | `companion_knowledge/vedic/v1/` + `companion_wisdom.py` + **anti-repetition** |
| Психология (internal) | 4× `wellness_knowledge/*/pack.yaml` | + `companion_knowledge/psychology/v1/internal.yaml` |
| Эмпатия | `_hint_for`, mood sad/lonely | + `empathy_macros.yaml`, active listening templates |
| Любая тема | `COMPANION_DOMAINS` (18 доменов) | + `topic_router_expanded.py` или расширение intent router |

---

## 4. Фаза 1 — Юмор (все герои; Джин max)

### 4.1 Целевые уровни

| Герой | Сейчас `HUMOR_DENSITY` | Цель | Стиль |
|-------|------------------------|------|--------|
| Единорог | medium | **medium-high** | Тёплые «магические» сравнения; шутка **~1 из 2–3** ответов при playful; **без сарказма** |
| Аладдин | low | **low-medium** | Сухая мудрая ирония **иногда**; чаще тёплый wit; сарказм **редко**, только PG и про ситуацию |
| Джин | high | **maximum (cap)** | Много юмора в характере, но **не каждый ответ**: ~60–70% при playful/L0, ~40% при neutral; max 1 каламбур/шутка когда включается; **иногда** лёгкий сарказм PG (не над человеком); **0** при sad/anxious/L1+ |

### 4.2 Файлы для правки

1. `security/services/ai_platform/companion_characters.py` — `HUMOR_DENSITY`, опционально `HUMOR_TIER` (0–3)
2. `security/services/ai_platform/companion_intent_router.py` — `_humor_hint_for_character()` — детальные правила по mood + escalation
3. `security/services/ai_platform/companion_persona.py` — `_UNICORN_BASE`, `_ALADDIN_HUMAN_BASE`, `_GENIE_BASE`, `PERSONALITY_PRESET_HINTS`
4. `wellness_knowledge/*/v1/pack.yaml` — блок `hero_flavor` (12 комбинаций) — **не** ломать L0 no-joke rules на humanistic/jung
5. **NEW** `security/services/ai_platform/companion_knowledge/humor/v1/tiers.yaml` — SSOT: character×mood×**escalation_matrix**, **humor_frequency**, sarcasm rules

### 4.3 Правила безопасности (обязательны в коде)

```yaml
humor_hard_stops:
  moods: [sad, lonely, comfort_needed, anxious]
  escalation: [L1, L2, L3]
  wellness_pillars_no_jokes: [humanistic, jung]
  child_band: no_sarcasm_no_innuendo
  keyword_override: [грустно, плохо, хочу умереть, боюсь]  # hero-x-44
  max_jokes_per_reply:
    genie: 1
    unicorn: 1
    aladdin: 1
humor_frequency:  # не стендап — баланс
  genie:
    L0_playful: 0.70
    L0_neutral: 0.40
    L0_curious: 0.50
  unicorn:
    L0_playful: 0.45
  aladdin:
    L0_playful: 0.25
sarcasm:
  genie: situational_pg_only  # иногда; never at person
  aladdin: rare_dry_wit
  unicorn: false
  child: false
```

### 4.4 iOS (опционально)

- `Core/Companion/CompanionPersonalityPresets.swift` — подсказки в UI «Игривый = больше шуток» (l10n keys)
- Не менять child: witty → playful guard

### 4.5 Тесты

- `Tests/test_companion_humor_policy.py` — mood=sad → hint contains «Без шуток»; escalation L1+ → no humor
- `Tests/test_companion_humor_genie_max.py` — genie + playful → hint allows pun **with frequency cap**
- `Tests/fixtures/companion_golden/` — **hero-x-07** golden set + CI scorer (humor rate, forbidden phrases)
- Regression: `Tests/test_wellness_age_policy_device_auth.py`
- Manual QA: **12 cases** — 3 heroes × (playful L0, sad L0, anxious L1, wellness humanistic) — **hero-x-06**

---

## 5. Фаза 2 — Ведическая мудрость (Аладдин + Джин)

### 5.1 Продуктовая модель

| Герой | Роль ведической линии |
|-------|----------------------|
| **Аладдин** | Спокойный **наставник**: duty без насилия над собой, ясность, стойкость — **пересказ идей** Gita 2.47, 6.5 **без религиозных слов** |
| **Джин** | **Образная** мудрость: метафора лампы/пути; лёгкая игра слов **после** смысла |
| **Единорог** | Tier **`universal`** only (child): сказочные параллели (дружба, смелость), **без** vedic refs |

**PO rule:** в `ru_paraphrase` / ответах LLM — **запрещены** слова религии и традиций. Источник (Gita/Mahabharata) — только internal metadata в YAML.

### 5.2 Новые файлы

```
security/services/ai_platform/companion_knowledge/
  vedic/
    v1/
      wisdom.yaml          # principles, short paraphrases ru/en, forbidden (proselytizing)
      mahābhārata_lite.yaml # stories as metaphors (не история войны в деталях)
      gita_lite.yaml        # ключевые идеи по темам: страх, долг, привязанность, медитация
  companion_wisdom.py        # pick_snippet(character_id, domain, mood, age_band)
```

**Структура записи в YAML:**

```yaml
- id: gita_2_47_lite
  source_internal: gita_2_47          # только YAML, не в ответ user
  snippet_tier: vedic_lite            # teen+ | universal (child)
  themes: [anxiety, duty, exam_stress]
  characters: [aladdin, genie]
  age_band_min: teen
  ru_paraphrase: "Сделай лучшее, что можешь сейчас — и отпусти тревогу о результате, которую не контролируешь."
  tone: calm_mentor
  max_chars_in_reply: 120
  forbidden: [preach, convert, shame, religion_words]
  forbidden_user_words: [бог, храм, молитва, вера, религия, ислам, христиан, будд, инду]
```

### 5.3 Интеграция в промпт

В `ai_companion_router.py` (или `build_companion_system_prefix`):

```python
wisdom = pick_wisdom_snippet(character_id, domain, mood, age_band)
if wisdom:
    parts.append(f"[WISDOM v1] theme={wisdom.theme} snippet={wisdom.ru_paraphrase}\n")
```

**Wellness:** wisdom только если `escalation=L0` и pillar ≠ crisis; не подменять `instruction` шага упражнения.

### 5.4 PO / Legal gate (обязательно до prod)

- [ ] PO review: **светские семьи** — zero religion lexicon in user-facing text
- [ ] Опция **выключить** vedic layer: `FEATURE_COMPANION_VEDIC_WISDOM=0` в `.env`
- [ ] Child 8–12: **off** или только **`universal`** tier (hero-x-10)
- [ ] Anti-repetition: same snippet max 1× / session (**hero-x-15**); frequency cap 1 wisdom / 5 turns

---

## 6. Фаза 3 — Глубина психологии (internal, «высший уровень»)

### 6.1 Важно: как это выглядит для пользователя

| Внутри LLM (можно) | Пользователю (нельзя) |
|--------------------|------------------------|
| Attachment, cognitive distortions, defense mechanisms, reflective listening, motivational interviewing | «КПТ», «психоанализ», «диагноз депрессии», «я лечу» |
| Переформулировка, validation, Socratic question | «Вы в стадии denial по Фрейду» |

### 6.2 Новый internal Knowledge Pack

```
companion_knowledge/psychology/v1/internal.yaml
```

Секции:

- `listening_ladder` — уровни эмпатического ответа (reflect → validate → one question)
- `distortion_labels_internal` — для LLM only (catastrophizing, mind-reading…)
- `age_band_playbooks` — child / teen / parent / senior
- `forbidden_user_phrases` — mirror из pack.yaml
- `depth_gear` — когда углубляться vs когда остановиться (escalation)

### 6.3 Расширение wellness pack (4 дорожки)

Дополнить `llm_rules` и `principles` в каждом `pack.yaml`:

- cognitive — больше micro-techniques (не называя CBT)
- humanistic — unconditional positive regard (plain language)
- behavioral — implementation intentions
- jung — archetypes as **метафора** (уже есть; усилить без «Юнг» в UI)

**Статус pack:** `draft` → **`cognitive_v1.1`** (и аналоги для 4 pillar) + changelog в MD — **hero-x-22**; финально `approved` после **hero-x-30**.

### 6.4 «Психоанализ в совершенстве» — реалистичная трактовка

Реализовать как:

1. **Longer context window usage** — recap + memory chips + last N turns
2. **Pattern reflection** — мягко: «похоже, эта тема для тебя важна» (не «ты третий раз»); **hero-x-24**: max 1× / 10 turns, teen-sensitive wording
3. **One insight + one question** — не лекции
4. Guard: не интерпретировать сны как diagnosis (jung pack rules); no surveillance tone

---

## 7. Фаза 4 — Максимальная эмпатия + «любая тема»

### 7.1 Эмпатия

| Механизм | Где |
|----------|-----|
| Active listening macros | `empathy_macros.yaml` |
| Mood-first routing | `companion_intent_router.py` — sad → 2 строки validation до вопроса |
| «Name the feeling» | hint: «назови чувство одним словом, если уместно» |
| Pause respect | calm preset + senior band — короче абзацы |

### 7.2 «Любая тема» — расширение доменов

Текущие `COMPANION_DOMAINS` (18) → добавить:

```python
"philosophy", "spirituality_lite", "career", "money_worries", "identity",
"grief", "motivation", "sleep", "food_mood", "internet_drama", "pets",
"travel_dreams", "creativity_block", "parenting_stress"
```

**Out-of-scope handler** (новая функция):

- medical diagnosis → «я друг, не врач; к врачу»
- legal → общие принципы + специалист
- explicit / romance → отказ PG
- politics flame → нейтральный redirect

Файл: `companion_topic_policy.py` + тесты.

### 7.3 Не путать с wellness

Если `wellness_pillar` active → **topic router** не расширяет beyond `allowed_topics` pack.

---

## 8. Фаза 5 — iOS / l10n / UX

| Задача | Файл |
|--------|------|
| Подсказка «Джин — больше шуток» | `LocalizationManager` + keys `companion_humor_hint_*` |
| Настройка «Мудрость древних текстов» (toggle, parent) | `CompanionSettings` + API consent flag |
| **Explainer** под toggle — что меняется, без религии (**hero-x-52**) | l10n `companion_wisdom_toggle_subtitle_*` |
| Teen optional «Меньше шуток» (**hero-x-67**, backlog v1.2) | `CompanionSettings` |
| Отображение recap с empathy line | `CompanionConversationScreen` |

---

## 9. Тестирование и выкат

```bash
# Unit
PYTHONPATH=. python3 -m pytest Tests/test_companion_*.py Tests/test_wellness_*.py -q

# Static iOS
./scripts/verify_r100_ios_static.sh

# Deploy
./scripts/deploy_companion_p0.sh root 149.154.65.180 ~/.ssh/aladdin_server
./scripts/deploy_wellness_batch4.sh root 149.154.65.180 ~/.ssh/aladdin_server

# Prod
./scripts/verify_wellness_prod.sh https://aladdin-ai.ru
```

**Manual QA (device) — 12+ cases (hero-x-06, hero-x-62):**

- Genie + playful + L0 → шутка **часто, но не 10/10 подряд**; не грубо
- Genie + neutral + L0 → иногда шутка, иногда только тепло
- Genie + «мне грустно» / keyword → 0 шуток, эмпатия (**hero-x-44**)
- Aladdin + exam stress → wisdom paraphrase **без религиозных слов**
- Child + genie → witty guard; vedic off (**negative**)
- Child + unicorn → без witty, без vedic
- Vedic toggle off → no `[WISDOM v1]` inject (**negative**)
- Wellness humanistic step → без шуток
- Topic OOS medical → мягкий redirect, не robotic
- Pattern reflection → не чаще 1× / 10 turns

---

## 10. Полный список TODO (`hero-x-*`) для TodoWrite

Импорт с **`merge: true`**. Статус по умолчанию **pending**. **Всего: 37** (34 core + 3 backlog v1.2).

### 10.1 Фаза 0 — PO gate

| id | Задача | Владелец | Критерий done |
|----|--------|----------|---------------|
| **hero-x-00** | **PO gate:** sign-off юмор balance + vedic secular framing + psychology wording | PO | Checkbox §0.1 + дата |

### 10.2 Фаза 1 — Юмор + safety foundation

| id | Задача | Владелец | Критерий done |
|----|--------|----------|---------------|
| **hero-x-01** | `humor/v1/tiers.yaml` — SSOT + **escalation_matrix** + **humor_frequency** + sarcasm rules | BE | File + schema docstring |
| **hero-x-02** | `HUMOR_DENSITY`: unicorn→medium-high, aladdin→low-medium, genie→max | BE | `companion_characters.py` + tests |
| **hero-x-03** | `_humor_hint_for_character(mood, tier, **escalation**)` — wire из `companion_ethics`/router | BE | L1+ → no humor; tests green |
| **hero-x-04** | Обновить `_GENIE_BASE` / `_UNICORN_BASE` / `_ALADDIN_HUMAN_BASE` — balance not flood | BE | Review diff persona |
| **hero-x-05** | `hero_flavor` 3×4 в pack.yaml (no-joke humanistic/jung) | Content | 4 yaml files |
| **hero-x-06** | Regression humor vs wellness; manual **12 cases** (3 heroes × 4 scenarios) | QA | pytest + 12 manual |
| **hero-x-07** | Golden conversation set (30–50) + CI scorer (humor rate, forbidden) | BE+QA | golden pass ≥95% |
| **hero-x-08** | **`companion_response_guard.py`** — post-LLM forbidden phrases в **free chat** | BE | **Hard gate prod** |
| **hero-x-44** | Keyword mood override («грустно», crisis keywords) → hard stop humor | BE | `test_companion_keyword_mood.py` |

### 10.3 Фаза 1b — Prompt assembly (parallel с 01)

| id | Задача | Владелец | Критерий done |
|----|--------|----------|---------------|
| **hero-x-09** | `companion_prompt_assembler.py` + token budget; priority stack | BE | Budget test CI |

### 10.4 Фаза 2 — Vedic wisdom (secular framing)

| id | Задача | Владелец | Критерий done |
|----|--------|----------|---------------|
| **hero-x-10** | vedic YAML: **`universal`** (child) + **`vedic_lite`** (teen+); ≥20 snippets; **no religion words** | Content | forbidden_user_words enforced |
| **hero-x-11** | `companion_wisdom.py` (`pick_wisdom_snippet`) | BE | Unit tests age/character/tier |
| **hero-x-12** | Инжект `[WISDOM v1]` в companion prompt (aladdin+genie) | BE | Router integration test |
| **hero-x-13** | `FEATURE_COMPANION_VEDIC_WISDOM` + child off | BE ops | .env.example |
| **hero-x-14** | PO/legal review vedic texts (secular check) | PO | CLINICAL_REVIEW appendix |
| **hero-x-15** | Wisdom anti-repetition + frequency cap (1/5 turns) | BE | Session dedup tests |

### 10.5 Фаза 3 — Psychology depth

| id | Задача | Владелец | Kритерий done |
|----|--------|----------|---------------|
| **hero-x-20** | `psychology/v1/internal.yaml` | Content | listening_ladder + distortions |
| **hero-x-21** | Инжект `[PSYCH v1 internal]` только system | BE | No forbidden in API + hero-x-08 |
| **hero-x-22** | Усилить `llm_rules` + `principles`; **pack_version v1.1** + changelog | Content | 4 yaml + CHANGELOG |
| **hero-x-23** | Pattern reflection helper (3-turn theme detect) | BE | `test_companion_pattern_reflect.py` |
| **hero-x-24** | Pattern reflection **limits** — max 1/10 turns; anti-creep wording | BE | No «ты третий раз» spam |
| **hero-x-30** | Clinical re-review packs | PO+clinical | draft→approved or waiver |

### 10.6 Фаза 4 — Empathy + topics

| id | Задача | Владелец | Kритerий done |
|----|--------|----------|---------------|
| **hero-x-40** | `empathy_macros.yaml` + validation-first router | BE | sad mood tests |
| **hero-x-41** | Расширить `COMPANION_DOMAINS` + `companion_topic_policy.py` | BE | OOS redirect tests |
| **hero-x-42** | Wellness session blocks topic expansion | BE | pillar active test |
| **hero-x-43** | Topic classifier confidence + graceful «не уверен» | BE | Low-confidence tests |

### 10.7 Фаза 5 — iOS

| id | Задача | Владелец | Kритerий done |
|----|--------|----------|---------------|
| **hero-x-50** | iOS l10n humor/wisdom hints + parent toggle | iOS | check_wellness_l10n |
| **hero-x-51** | «Мудрость древних текстов» off default child | iOS | UserDefaults + consent |
| **hero-x-52** | Toggle **explainer** subtitle (secular, что меняется) | iOS | l10n keys ru/en |
| **hero-x-65** | EN parity checklist (humor, wisdom, empathy, guard) | iOS+BE | checklist signed |

### 10.8 Фаза 6 — QA, deploy, observability

| id | Задача | Владелец | Kритerий done |
|----|--------|----------|---------------|
| **hero-x-60** | pytest `Tests/test_companion_*.py` **≥40** parametrized cases | BE | CI green |
| **hero-x-61** | deploy batch4 + companion_p0 + verify 14/14 | BE ops | IMPLEMENTATION_STATUS date |
| **hero-x-62** | TestFlight smoke + **negative cases** (child+genie, vedic off, humor off) | PO | smoke doc extended |
| **hero-x-63** | Ethics audit r100-5-ethics — **hard gate prod** | QA | teen privacy + L3 |
| **hero-x-64** | Metrics: `humor_injected`, `wisdom_used`, `guard_triggered` | BE ops | logs doc |

### 10.9 Backlog v1.2+ (не блокирует prod)

| id | Задача | Владелец | Kритerий done |
|----|--------|----------|---------------|
| **hero-x-67** | Teen «Меньше шуток» slider | iOS | Settings + API hint |
| **hero-x-68** | A/B: genie max vs genie high (data-driven cap) | PO+BE | experiment flag |
| **hero-x-69** | Parent one-pager «что умеют герои» | PO/marketing | PDF or in-app |

---

## 11. Рекомендуемый порядок выполнения (v2)

```
hero-x-00 (PO gate)
    ↓
┌─ hero-x-01 → 02 → 03 → 04 → 05 ─┐
├─ hero-x-08 (companion guard)      │  parallel P0
├─ hero-x-44 (keyword override)     │
├─ hero-x-07 (golden set)           │
└─ hero-x-09 (prompt assembler)     ┘
    ↓
hero-x-06 (12 manual + regression)
    ↓
┌─ hero-x-10 → 11 → 12 → 13 ─┐
└─ hero-x-15 (anti-repeat)    ┘
    ↓
hero-x-14 (PO/legal secular)
    ↓
hero-x-20 → 21 → 22 → 23 → 24
    ↓
hero-x-40 → 41 → 42 → 43
    ↓
hero-x-50 → 51 → 52 → 65
    ↓
hero-x-30 → 60 → 61 → 62 → 63 → 64
    ↓
[backlog] hero-x-67 → 68 → 69
```

**Prod blockers:** hero-x-00, **08**, **63**, **07**, **44**, **15**, **24**.

**Оценка:** BE+content **5–7 дней**; iOS **1–1.5 дня**; PO/legal **вне календаря**.

---

## 12. Пример diff (Genie humor balance) — ориентир для ML

`companion_intent_router.py` — фрагмент цели:

```python
if character_id == "genie" and mood in ("neutral", "joyful", "playful", "curious"):
    if escalation == "L0":
        if should_inject_humor(session, probability=0.70 if mood == "playful" else 0.40):
            return (
                "Джин: одна короткая сказочная шутка или каламбур (PG-13), "
                "иногда лёгкий сарказм про ситуацию (не про человека). "
                "Не больше одной шутки. Если шутка не уместна — только тёплая мысль."
            )
        return "Джин: тёплый ответ без шутки в этом сообщении — чередуй, не стендап."
```

`companion_persona.py` — `_GENIE_BASE` дополнение:

```
При neutral/playful и L0 — ты узнаваемый весёлый джин: часто лёгкий каламбур или сказочная «фишка»,
но не в каждом ответе. Чередуй шутку и просто тепло. Без насмешки над человеком.
```

---

## 13. Риски и mitigations (v2)

| Риск | Mitigation |
|------|------------|
| Джин = стендап, раздражение | **humor_frequency** + golden set hero-x-07; not every reply |
| Сарказм над человеком | tiers.yaml: situational only; child off; hero-x-08 guard |
| Скрытая грусть при neutral mood | hero-x-44 keyword override + anxious in hard_stops |
| Vedic = религия / отторжение | **forbidden_user_words**; secular framing; hero-x-14; toggle off |
| Pattern reflection = creepiness | hero-x-24: max 1/10 turns; soft wording |
| «Психоанализ» наружу | hero-x-08 companion guard + wellness guard |
| Robotic OOS redirect | hero-x-43 confidence threshold |
| Jailbreak «игнорируй правила» | content_policy + SFM + humor jailbreak tests in hero-x-07 |
| Token bloat | hero-x-09 prompt assembler; wisdom ≤120 chars |
| Prod без ethics | **hero-x-63 hard gate** — no deploy without pass |

---

## 14. Связь с r100

| r100 id | Связь с hero-x |
|---------|----------------|
| r100-4-voice | Не блокирует; humor/wisdom в text prompt работает и для TTS |
| r100-5-ethics | **hero-x-63** — **hard gate prod** |
| r100-7-10 | **hero-x-30** clinical approved |
| r100-0-03/04 | Hermes keys — quality rephrase (не блокер YAML) |
| hero-x-64 | Observability для prod tuning humor/wisdom |

---

## 15. Definition of Done (весь трек hero-x)

- [x] PO sign-off **hero-x-00**, **hero-x-14**, **hero-x-30** (см. COMPANION_HERO_X00_PO_SIGNOFF.md, WELLNESS_CLINICAL_REVIEW Appendix B/C)
- [x] **hero-x-08** + **hero-x-63** — prod blockers
- [x] CI: pytest **≥40** + golden set **≥95%**
- [x] verify_wellness_prod **14/14** + companion **18/18**
- [x] TestFlight smoke + negative cases (**hero-x-62**) — backend + l10n gate
- [x] IMPLEMENTATION_STATUS обновлён
- [x] Backlog **hero-x-67…69** (v1.2) — teen slider, genie A/B flag, one-pager

---

*План v2 — 2026-06-04 (expert review 5/5 + PO refinements). После реализации — обновить [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md) § «hero enhancement».*
