# ALADDIN Wellness Platform — Master Plan v2.5 (Final)

> **Статус:** финальная версия для реализации + **handoff для другой ML** (§19) + **Knowledge Pack / герои** (§4.3)  
> **Репозиторий:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
> **Позиционирование:** «Семейный цифровой друг с эмоциональной поддержкой»  
> **Принцип:** не замена психолога — **мост к живым людям** (`companion_ethics.py`)  
> **Продуктовая модель:** **4 столпа самопомощи** в одном Wellness Hub (не 4 приложения)

| Документ | Назначение |
|----------|------------|
| **[WELLNESS_ML_HANDOFF.md](./WELLNESS_ML_HANDOFF.md)** | **Инструкция для другой ML** — старт, TodoWrite §10, gate |
| **[WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md)** | **131/131 готово** — деплой VPS, plan vs fact, verify prod |
| **[WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md)** | Чеклист **131 задача** (`p0-01` … `p3-20`, `p18-*`) |
| **[WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md)** | HealthKit capability (p2-36) — шаги PO в Apple Developer |
| **[WELLNESS_I18N_CHECKLIST.md](./WELLNESS_I18N_CHECKLIST.md)** | Ключи `wellness_*` ru/en |
| **[WELLNESS_I18N_GLOSSARY.md](./WELLNESS_I18N_GLOSSARY.md)** | Термины, запреты в UI |
| **[ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md](../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md)** | **Прод-сервер:** SSH, `:8002`, деплой `security/` — читать перед выкладкой wellness API |

> **Сервер (обязательно перед deploy):**  
> 1. `curl -s -S -m 8 http://149.154.65.180:8002/api/health` → `{"status":"ok"}`  
> 2. SSH: `root@149.154.65.180` (ключ, не пароль в репо)  
> 3. Backend root: `/opt/aladdin-backend` — см. гайд §10–§12  
> 4. Правило Cursor: `.cursor/rules/aladdin-server-connection.mdc`

**Передать другой системе:** прикрепить `@WELLNESS_ML_HANDOFF.md` + вставить текст из handoff §0.

---

## 1. Краткое резюме

ALADDIN уже имеет Companion (чат, voice, avatar, ethics, teen playbook, social bridge).  
Добавляем **Wellness Loop Engine** — автоматизированную цепочку как у Jivi, но **family-first** и через **4 понятные дорожки** для пользователя.

```
Trigger → Check-in → Screening → [4 столпа] → Chat → Journal → Timeline → Alert → Family bridge
```

**Не делаем:** PPG-камера, freemium без регистрации, отдельное приложение «Psychology», claims «лечит депрессию/травмы».

---

## 2. Четыре столпа — для пользователя и для разработки

### 2.1 Четыре кнопки в Wellness Hub (UI)

| # | Кнопка в приложении | Научная база | Одной фразой для пользователя |
|---|---------------------|--------------|-------------------------------|
| 1 | **«Разобрать мысли»** | КПT (Beck, Ellis) + 2-я волна | «Когда крутятся тревожные мысли — разложим по полочкам» |
| 2 | **«Маленькие шаги»** | Бихевiorизм (Pavlov, Skinner) + 1-я волна | «Не мотивация, а привычка: один маленький шаг сегодня» |
| 3 | **«Принять себя»** | Гуманизм (Rogers) + ACT/DBT lite (3-я волна) | «Без оценок — просто побыть рядом и дышать» |
| 4 | **«Понять себя»** | **Юнг lite** + психодинамика lite (Freud — внутри, не отдельная кнопка) | «Сны, символы, образы — что это может значить для меня» |

**В UI никогда не пишем:** Pavlov, Freud, Jung, КПT, психоанализ, терапия.  
**В UI всегда пишем:** самопомощь, поддержка, исследование себя.

### 2.2 Столп 1 — «Разобрать мысли» (КПT)

**Научная база:** когнитивно-поведенческая терапия (Beck), рационально-эмotive (Ellis).

**Что внутри приложения:**
- Thought Record (мысль → факты за/против → переформулировка)
- Различение: факт / интерпретация / эмоция / мысль
- PHQ-lite, PHQ-9, GAD-7 (скрининг, не диагноз)
- Микро-вопросы при rumination («что самое страшное, если это правда?»)

**Когда автоматически предлагать:** mood = anxious, слова «тревож», «крутится в голове», «не могу перестать думать».

**Age gating:**
- child: ❌ thought record; ✅ «что ты думаешь?» простым языком
- teen+: ✅ full lite
- parent/senior: ✅ full

**Backend:** `wellness_cognitive_prompt.py`, `wellness_cbt_exercises.py`, `wellness_assessments.py`

---

### 2.3 Столп 2 — «Маленькие шаги» (Pavlov / поведение)

**Научная база:** классическое и оперантное обусловливание (Pavlov, Skinner), behavioral activation.

**Что внутри приложения:**
- If-then планы («Если 19:00 → 2 мин дневник настроения»)
- Habit stacking (привязка к существующей привычке)
- Behavioral activation (1 приятное действие в день)
- Exposure-lite (микро-шаг к страху, только teen+ с disclaimer)
- Streaks и напоминания (scheduler)
- Micro-step из reflective session → сюда

**Когда автоматически предлагать:** mood = tired, «выгорел», «лень», «откладываю», avoidance.

**Age gating:**
- child: ✅ «одна маленькая победа сегодня»
- teen+: ✅ if-then, activation
- parent/senior: ✅ + burnout MBI-lite

**Backend:** `wellness_behavioral_exercises.py`, `wellness_habit_plans.py`

**Copy-правило:** никогда «дрессировка», «условный рефлекс» — только «привычка», «шаг», «ритуал».

---

### 2.4 Столп 3 — «Принять себя» (Rogers + ACT/DBT)

**Научная база:** клиент-центрированная терапия (Rogers), ACT (Hayes), DBT skills (Linehan) — lite.

**Что внутри приложения:**
- Режим «просто побудь рядом» (presence) — без анализа
- Grounding 5-4-3-2-1
- Box breathing (4-4-4-4)
- DBT STOP
- Values card lite («что для меня важно на этой неделе») — Phase 3
- Self-compassion фразы (не религия, не эзотерика)

**Когда автоматически предлагать:** mood = sad, lonely, comfort_needed; фраза «просто побудь рядом».

**Age gating:**
- child: ✅ presence + breathing (основной столп для child)
- teen+: ✅ all lite
- parent/senior: ✅ + values card (P3)

**Backend:** `wellness_humanistic_prompt.py`, упражнения в `wellness_cbt_exercises.py` (grounding, STOP)

---

### 2.5 Столп 4 — «Понять себя» (Jung lite + psychodynamic lite)

**Научная база:** аналитическая психология (Jung) — lite; психодинамика (Freud) — только внутри «глубокого исследования», не отдельная кнопка.

**Что внутри приложения (Jung lite):**
- **Дневник снов** (teen+ / parent / senior): записал сон → AI помогает исследовать **символы как метафоры**, без «это точно значит X»
- **Карточки архетипов** как метафоры (Искатель, Защитник, Тень lite) — не диагноз, не типология личности
- **Интуиция vs тревога** — упражнение различения
- **Active imagination lite** — guided visualization 2–3 мин с safety guard
- **Образ внутри** — «если бы чувство было образом, какой бы он был?»
- **Reflective deep mode** (§8) — psychodynamic: паттерны, части (IFS упрощённо), «как я научился так жить»

**Чего НЕ делаем в Jung-столпе:**
- ❌ Предсказания, магия, «судьба»
- ❌ Глубокая травма, EMDR, transference
- ❌ Жёсткая типология («ты архетип X»)
- ❌ Замена религии/духовного учителя
- ❌ child: только сказочные метафоры, без анализа снов

**Когда автоматически предлагать:** curious, nostalgic; «почему я так», «сон», «символ», «знак»; user chip «Понять себя».

**Age gating:**
- child: ✅ метафоры/сказка («какой герой сегодня внутри»)
- teen: ✅ dream journal lite, archetype cards, без trauma deep
- parent/senior: ✅ full lite + reflective deep

**Backend:** `wellness_jung_prompt.py`, `wellness_jung_exercises.py`, `wellness_reflective_prompt.py`, `wellness_reflective_guards.py`

---

### 2.6 Правило «один столп = одна сессия»

Orchestrator выбирает **один** `wellness_pillar` на turn/session:
`cognitive` | `behavioral` | `humanistic` | `jung`

Переключение — только явным chip или фразой пользователя.  
Crisis (ethics L3) → **блок всех столпов** → 112 + взрослый.

---

## 3. Автоматическая маршрутизация (Emotion Agent → столп)

```
mood + keywords + user chip
        ↓
┌───────────────────────────────────────────────────────────┐
│ anxious + rumination     → «Разобрать мысли» (cognitive)  │
│ tired + avoidance        → «Маленькие шаги» (behavioral)  │
│ sad + lonely             → «Принять себя» (humanistic)    │
│ curious + dream/symbol   → «Понять себя» (jung)           │
│ «разбери глубоко»        → jung + reflective sub-mode     │
│ «просто побудь рядом»    → humanistic / presence only     │
│ crisis (ethics L3)         → STOP all → crisis protocol     │
└───────────────────────────────────────────────────────────┘
```

**Файл:** `wellness_four_pillars.py` (router + pillar enum + auto-select)

---

## 4. Архитектура Wellness Loop Engine

```
Wellness Hub (4 chips)
    ↓
Check-in (emoji + sleep/stress)
    ↓
Screening (PHQ-lite / GAD / burnout) — age-gated
    ↓
wellness_four_pillars.py → ONE pillar session
    ↓
Companion chat + pillar-specific prompt + exercises
    ↓
wellness_insights_extractor → journal
    ↓
Timeline + parent aggregate (opt-in)
    ↓
Alerts + family bridge
```

### 4.1 Backend — полный список модулей

```
security/services/ai_platform/
├── wellness_four_pillars.py          # роутинг 4 столпов
├── wellness_orchestrator.py          # полная цепочка агентов
├── wellness_journal.py
├── wellness_assessments.py
├── wellness_cbt_exercises.py         # столп 1 + grounding STOP (3)
├── wellness_behavioral_exercises.py  # столп 2
├── wellness_habit_plans.py           # if-then, streaks
├── wellness_humanistic_prompt.py     # столп 3 (тон; контент из pack)
├── wellness_jung_prompt.py           # столп 4 (тон; контент из pack)
├── wellness_jung_exercises.py        # сны, символы, active imagination lite
├── wellness_reflective_prompt.py     # deep mode внутри столпа 4
├── wellness_reflective_modes.py      # 5 sub-modes
├── wellness_reflective_guards.py
├── wellness_prompt_builder.py        # build_wellness_prefix() → [WELLNESS v1] block
├── wellness_knowledge/             # канон по столпам (не по героям)
│   ├── cognitive/v1/pack.yaml
│   ├── behavioral/v1/pack.yaml
│   ├── humanistic/v1/pack.yaml
│   └── jung/v1/pack.yaml
├── wellness_insights_extractor.py
├── wellness_emotion_agent.py
├── wellness_plan_agent.py
├── wellness_triggers.py
├── wellness_alerts.py
├── wellness_scheduler.py
└── wellness_analytics.py

security/api/routers/
├── wellness_router.py
└── (patch) ai_companion_router.py — wellness_prefix + pillar router (§4.3)
```

### 4.3 Knowledge Pack — как герои «владеют» 4 столпами (без fine-tune)

> **Синтез (6 шляп):** герои не обучают отдельную модель психологии. Они **озвучивают** проверенный **Knowledge Pack одного столпа** простым языком своего характера, пока **код** держит этику, возраст и шаг упражнения; LLM заполняет щели между шагами, **не придумывая школу с нуля**.

**Принцип UX:** один backend, один чат — **семейный друг**, не «приложение психолога». Герой передаёт **тепло и образы**; наука спрятана в сценарии. В UI и LLM **запрещены:** Pavlov, Freud, Jung, КПT, терапия, диагноз (см. [WELLNESS_I18N_GLOSSARY.md](./WELLNESS_I18N_GLOSSARY.md)).

#### 4.3.1 Четыре слоя (порядок вызова)

| Слой | Модули | Роль |
|------|--------|------|
| **1. Детерминизм (до LLM)** | `companion_ethics.py`, `wellness_escalation.py`, `age_policy`, Hub UI, `wellness_assessments.py`, `wellness_pillar_guard.py` | Кризис L3 → 112; PHQ score → referral **кодом**; child 2 кнопки; один `primary_pillar` |
| **2. Упражнения (структура)** | `wellness_*_exercises.py`, `WellnessExerciseScreen.swift` | State machine + steps JSON; **~80% текста** из JSON/i18n; LLM только «перефразируй hint шага N для {age_band}» |
| **3. Knowledge + prompt** | `wellness_knowledge/*/pack.yaml`, `wellness_prompt_builder.py`, patch `ai_companion_router` | Один pack на столп; **3 героя = 3 flavor-строки**, не 12 промптов |
| **4. Метрики (без дообучения)** | `wellness_outcomes.py`, `wellness_pillar_fatigue.py`, p2-38 A/B, `vps_smoke_wellness.py`, p3-10 canary | Корректировка routing/prompts по outcome 24h, не fine-tune |

#### 4.3.2 Knowledge Pack (канон по столпу)

```
wellness_knowledge/
  cognitive/v1/     — CBT-lite: thought record, факты vs догадки, запреты
  behavioral/v1/    — привычки, if-then, micro-step (без «рефлекс», «дрессировка»)
  humanistic/v1/    — presence, дыхание, DBT STOP
  jung/v1/          — сны, метафоры; запрет предсказаний (gate p0-08, p0-11)
```

**Загрузка:** `load_pillar_pack(pillar, locale, version) -> str`  
**Сборка префикса:** `build_wellness_prefix(pillar, age_band, character_id, exercise_ctx) -> str`

**Hero flavor (unicorn / genie / aladdin):** 2–3 предложения тона поверх **одного** pack; clinical review — **4 пакета**, не 12.

| Герой | Flavor |
|-------|--------|
| unicorn | коротко, как другу; без пугающих деталей |
| genie | одна лёгкая образная фраза; **без шуток при L2/L3** |
| aladdin | один шаг, один вопрос, наставник |

#### 4.3.3 Контракт `[WELLNESS v1]` (в prefixed message)

```text
[WELLNESS v1]
primary_pillar=cognitive
escalation=L0
age_band=teen
exercise=thought_record
exercise_step=2/5
allowed_topics=untangle_thoughts,facts_vs_guesses
forbidden=diagnosis,other_pillars,therapy_claims
pack_version=cognitive_v1.0
hero_flavor=mentor_short
instruction=Озвучь только шаг 2; один вопрос; простой русский.
```

**Сборка в `ai_companion_router` (~1378–1393):**

```text
prefixed =
  companion_system_prefix(character, age)   # persona (как сейчас)
  + wellness_prefix(pillar, exercise, esc)  # НОВОЕ — Knowledge Pack
  + family_hint + ethics + teen_playbook
  + user_message
```

#### 4.3.4 Практика «наилучшим образом» (чеклист)

| # | Практика | Реализация |
|---|----------|------------|
| 1 | Детерминизм → LLM | Кризис / PHQ≥10 / referral — без импровизации героя |
| 2 | Один столп = один prompt | `wellness_pillar_guard` + один `load_pillar_pack` |
| 3 | Упражнение = структура | 80% JSON/i18n; LLM — 1–2 предложения перефраза |
| 4 | Clinical gate | p0-08 подписывает **4 пакета**; Jung/premium после p0-11, p3-12 |
| 5 | Простой язык | glossary + `_child` / `_teen`; герой не вводит термины школ |
| 6 | Не дублировать AI | только patch `ai_companion_router`, не «Psychology API» |
| 7 | «100% знаний» | `pack_version` + smoke запрещённых фраз (p1-29) |
| 8 | Герои | одна наука, три голоса — flavor, не отдельная КПT на героя |

#### 4.3.5 Дорожная карта Knowledge Pack по фазам

| Фаза | Фокус | TODO |
|------|-------|------|
| 0 | ADR: формат pack + контракт prefix; hero intros; clinical review шаблонов | p0-14 … p0-16 |
| 1 | `wellness_prompt_builder`; cognitive + humanistic v1; router patch; smoke | p1-26 … p1-29 |
| 2 | behavioral + jung packs; exercise 80/20 policy | p2-49 … p2-51 |
| 3 | orchestrator выбирает `pack_version`; Rive по pillar (см. p3-09) | p3-20 |

#### 4.3.6 Запреты (не делать)

- ❌ Отдельный «Psychology API» и 4 fine-tuned модели  
- ❌ 12 system prompts (3 героя × 4 столпа) без общего pack  
- ❌ Объяснять пользователю Павлова, Юнга, КПT  
- ❌ Jung / PHQ-9 до p0-08 / p0-11  
- ❌ Score PHQ и escalation через LLM  
- ❌ Шутки джина при кризисе L3 (риск доверия)

**Шаблон pack:** `wellness_knowledge/cognitive/v1/pack.yaml` — `principles`, `step_hints`, `forbidden_phrases`, `hero_flavor` (создаётся в p0-15).

### 4.2 Database (companion_store.py extensions)

```sql
-- Daily check-in
CREATE TABLE wellness_checkins (
    user_id TEXT NOT NULL,
    day TEXT NOT NULL,
    mood_emoji TEXT,
    mood_score INTEGER,
    sleep_hours REAL,
    stress_level INTEGER,
    energy_level INTEGER,
    notes TEXT,
    source TEXT NOT NULL,
    age_band TEXT,
    created_at TEXT NOT NULL,
    PRIMARY KEY (user_id, day)
);

-- Screenings
CREATE TABLE wellness_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    assessment_type TEXT NOT NULL,
    answers_json TEXT NOT NULL,
    score INTEGER NOT NULL,
    severity TEXT NOT NULL,
    suggest_professional INTEGER NOT NULL DEFAULT 0,
    disclaimer_version TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Exercises (all pillars)
CREATE TABLE wellness_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    pillar TEXT NOT NULL,           -- cognitive|behavioral|humanistic|jung
    exercise_type TEXT NOT NULL,
    state_json TEXT NOT NULL,
    step_index INTEGER NOT NULL DEFAULT 0,
    completed INTEGER NOT NULL DEFAULT 0,
    thread_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Dream journal (pillar jung)
CREATE TABLE wellness_dream_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    dream_text TEXT NOT NULL,
    symbols_json TEXT,
    reflection_text TEXT,
    created_at TEXT NOT NULL
);

-- Insights (after sessions)
CREATE TABLE wellness_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    pillar TEXT NOT NULL,
    understood TEXT,
    observe_next TEXT,
    micro_step TEXT,
    patterns_json TEXT,
    created_at TEXT NOT NULL
);

-- Habit plans (pillar behavioral)
CREATE TABLE wellness_habit_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    if_then TEXT NOT NULL,
    streak INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

-- Settings + consent
CREATE TABLE wellness_settings (
    user_id TEXT PRIMARY KEY,
    consent_version TEXT,
    active_pillar TEXT,
    daily_reminder_enabled INTEGER DEFAULT 0,
    daily_reminder_hour INTEGER DEFAULT 19,
    parent_share_aggregate INTEGER DEFAULT 0,
    parent_user_id TEXT,
    locale TEXT DEFAULT 'ru',
    updated_at TEXT NOT NULL
);

-- Crisis audit (NO message text)
CREATE TABLE wellness_alert_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Auto plan
CREATE TABLE wellness_plans (
    user_id TEXT PRIMARY KEY,
    plan_json TEXT NOT NULL,
    primary_pillar TEXT,
    source_assessment_id INTEGER,
    updated_at TEXT NOT NULL
);
```

### 4.3 API

| Method | Path | Описание |
|--------|------|----------|
| GET | `/api/wellness/settings` | настройки + consent |
| POST | `/api/wellness/settings` | reminders, parent share |
| POST | `/api/wellness/consent` | принять disclaimer |
| POST | `/api/wellness/checkin` | emoji + sliders |
| GET | `/api/wellness/checkins?days=30` | timeline |
| POST | `/api/wellness/assessment/start` | PHQ/GAD/burnout |
| POST | `/api/wellness/assessment/submit` | ответы → score |
| GET | `/api/wellness/assessment/latest` | последний результат |
| POST | `/api/wellness/pillar/select` | `{pillar: cognitive\|behavioral\|humanistic\|jung}` |
| GET | `/api/wellness/pillar/suggest` | auto-suggest по mood |
| POST | `/api/wellness/exercise/start` | упражнение по столпу |
| POST | `/api/wellness/exercise/step` | шаг упражнения |
| POST | `/api/wellness/dream` | записать сон (jung) |
| GET | `/api/wellness/dreams?days=30` | дневник снов |
| GET | `/api/wellness/insights?days=30` | инсайты |
| POST | `/api/wellness/habit` | if-then план |
| GET | `/api/wellness/plan` | авто-план |
| GET | `/api/wellness/summary` | личная сводка |
| GET | `/api/wellness/family/summary` | родитель (aggregate) |
| POST | `/api/wellness/export` | GDPR export |
| DELETE | `/api/wellness/data` | удалить данные |

### 4.4 iOS экраны

| Экран | Файл |
|-------|------|
| Wellness Hub (4 chips) | `WellnessHubScreen.swift` |
| Check-in | `WellnessCheckinScreen.swift` |
| Consent | `WellnessConsentScreen.swift` |
| Assessment Hub + Flow | `WellnessAssessmentHubScreen.swift`, `WellnessAssessmentFlowScreen.swift` |
| Timeline + Insights | `WellnessTimelineScreen.swift` |
| Exercise (all pillars) | `WellnessExerciseScreen.swift` |
| Dream journal | `WellnessDreamJournalScreen.swift` |
| Reflective sub-modes | `WellnessReflectiveModeScreen.swift` |
| Family dashboard | `WellnessFamilyDashboardScreen.swift` |
| Settings | `WellnessSettingsScreen.swift` |

**Services:** `WellnessAPIService.swift`, `WellnessOfflineStore.swift`, `WellnessModels.swift`

**Companion:** chip «Настроение» + `suggested_actions` + pillar badge на bubble

---

## 5. Age matrix (4 столпа)

| Функция | child | teen | parent | senior |
|---------|-------|------|--------|--------|
| Check-in emoji | ✅ | ✅ | ✅ | ✅ |
| «Принять себя» (3) | ✅ основной | ✅ | ✅ | ✅ |
| «Маленькие шаги» (2) | ✅ lite | ✅ | ✅ | ✅ |
| «Разобрать мысли» (1) | ⚠️ ultra-lite | ✅ | ✅ | ✅ |
| «Понять себя» / Jung (4) | ⚠️ метафоры | ✅ lite | ✅ | ✅ |
| Dream journal | ❌ | ✅ | ✅ | ✅ |
| PHQ-9 / GAD-7 | ❌ | ✅ | ✅ | ✅ |
| Reflective deep | ❌ | ⚠️ lite | ✅ | ✅ |
| Parent aggregate | N/A | opt-in | sees kids | optional |

---

## 6. Reflective mode (внутри столпа 4 «Понять себя»)

5 sub-modes (chips / фразы):

| Sub-mode | Триггер | Поведение |
|----------|---------|-----------|
| presence | «побудь рядом» | → переключить на столп 3 |
| deep_explore | «разбери глубоко» | reflective prompt + jung |
| structured_view | «взгляд со стороны» | факты / интерпретации |
| blind_spots | «слепые зоны» | паттерны, защиты |
| single_question | «только вопрос» | один вопрос |

Post-session: `wellness_insights_extractor` → «понял / наблюдать / шаг» → timeline.

---

## 7. Риски и митигация

| Риск | Митигация |
|------|-----------|
| «Терапия 4 школ» | UI: самопомощь; один столп за сессию |
| Jung → эзотерика | Символы как метафоры; disclaimer |
| Pavlov → «дрессировка» | Copy: «привычки и шаги» |
| Freud → травма у teen | Только lite; guards; specialist redirect |
| Medical claims | App Store 1.4.1; consent |
| Parent spying | Aggregate only; teen opt-in |
| Crisis | ethics L3 > all prompts → 112 |

---

## 8. Feature flags

```python
FEATURE_WELLNESS_ENABLED = _env_bool("FEATURE_WELLNESS_ENABLED", False)
FEATURE_WELLNESS_ORCHESTRATOR = _env_bool("FEATURE_WELLNESS_ORCHESTRATOR", False)
FEATURE_WELLNESS_REFLECTIVE = _env_bool("FEATURE_WELLNESS_REFLECTIVE", False)
FEATURE_WELLNESS_JUNG = _env_bool("FEATURE_WELLNESS_JUNG", False)  # pillar 4
COMPANION_USE_ORCHESTRATOR = _env_bool("COMPANION_USE_ORCHESTRATOR", False)
```

Rollout: parent/senior → teen → child lite; canary 5% → 100%.

---

## 9. Premium (Phase 3)

**Free:** check-in, столп 3 «Принять себя», базовый chat  
**Premium:** все 4 столпа, full PHQ/GAD, timeline, dream journal, CBT/Jung packs, family dashboard

---

## 10. Фазы и сроки

| Фаза | Срок | Результат |
|------|------|-----------|
| **0** | 3–4 дня | ADR, legal, flags, 4-pillar copy |
| **1** | 2–3 нед | Check-in, PHQ-lite, consent, Hub skeleton, pillar routing v1 |
| **2** | 4–5 нед | Все 4 столпа (prompts + exercises), timeline, dreams, reflective, parent |
| **3** | 4–6 нед | Full orchestrator, premium, senior merge, deploy |

**Итого:** ~11–14 недель (1 dev full-time).

---

## 11. Automation matrix

| Событие | Авто-действие |
|---------|---------------|
| Первый заход / 19:00 | Check-in prompt |
| 3 дня low mood | PHQ-lite |
| PHQ ≥ 10 | Plan + pillar suggest + specialist disclaimer |
| anxious + rumination | Столп 1 |
| tired + avoidance | Столп 2 |
| sad + lonely | Столп 3 |
| dream keyword | Столп 4 |
| Deep session end | Insight → journal |
| Crisis L3 | 112, block pillars |
| 3d low + teen opt-in | Parent aggregate alert |
| Weekly cron | Parent digest |

---

## 12. Что НЕ делаем

- Отдельное приложение ALADDIN Psychology
- «Лечит депрессию / прорабатывает травмы»
- PHQ-9 детям 8–12
- Parent видит дословный чат teen
- PPG stress camera
- 4 отдельных приложения / агента-«школы» одновременно в одном ответе
- Jung: предсказания, магия, жёсткие типы личности

---

## 13. Agent registry (Phase 3 target)

```python
WELLNESS_AGENTS = {
    "cognitive": ["cbt_coach_agent"],
    "behavioral": ["habit_coach_agent"],
    "humanistic": ["presence_coach_agent"],
    "jung": ["symbol_coach_agent", "reflective_agent"],
    "screening": ["clinical_screening_agent"],
    "crisis": ["crisis_agent", "self_harm_detection_agent"],
    "family": ["family_bridge_agent"],
}
```

---

## 14. Cursor TODO (синхронизация с этим MD)

| Фаза | Задач | Файл / ID |
|------|-------|-----------|
| 0 | 16 | `p0-01` … `p0-16` |
| 1 | 29 | `p1-01` … `p1-29` |
| 2 | 51 | `p2-01` … `p2-51` |
| 3 | 20 | `p3-01` … `p3-20` |
| i18n | 15 | `p18-01` … `p18-15` |
| **Σ** | **131** | + §4.3 Knowledge Pack |

**Полный список с чекбоксами:** [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md)  
**Как загрузить в панель Cursor:** [WELLNESS_ML_HANDOFF.md](./WELLNESS_ML_HANDOFF.md) §3 Шаг B  

Этот MD = архитектура и «зачем»; **рабочий чеклист** = `WELLNESS_CURSOR_TODO.md`.

### 14.1 PPG / камера стресса (Jivi) — что это и нужно ли нам

**PPG (фотоплетизмография)** — способ «увидеть» пульс **через камеру телефона**:

1. Пользователь прикладывает палец к камере (или смотрит в фронталку).
2. Вспышка подсвечивает кожу.
3. Камера ловит микро-изменения цвета крови при каждом ударе сердца.
4. Алгоритм считает **пульс**, иногда **вариабельность (HRV)** и **оценку стресса**.

**У Jivi** это подаётся как: «стресс и пульс с камеры без гаджетов».

| Плюс | Минус для ALADDIN |
|------|-------------------|
| Выглядит «как медицина» | Медицинские claims, App Store 1.4.1 |
| Не нужны часы | Точность спорная, особенно у детей |
| Wow-эффект в маркетинге | Камера + дети = privacy/COPPA вопросы |
| | **Не связано** с VPN/родконтролем — не ваш moat |

**Решение в плане: ❌ не реализовывать (skip).**  
**Вместо PPG:** Apple Health / часы → `sleep_hours`, пульс в check-in (задача **p2-36**) — данные уже есть у многих, без «лечения камерой».

**Опционально Phase 4+ (research only):** пилот только parent/senior, без детей, без слова «диагностика стресса».

---

## 15. File index (existing)

| Компонент | Путь |
|-----------|------|
| Companion API | `security/api/routers/ai_companion_router.py` |
| Ethics | `security/services/ai_platform/companion_ethics.py` |
| Mood MVP | `companion_mood_classifier.py` |
| Store | `companion_store.py` |
| Flags | `feature_flags.py` |
| Orchestrator stub | `orchestrator.py` |
| Age policy | `age_policy.py` |
| Parent toggle | `ParentalControlViewModel.swift` |
| Companion UI | `Screens/CompanionConversationScreen.swift` |

---

---

## 16. Доведение до 10/10 — Jivi-parity + clinical safety + automation

> **Цель v2.1:** максимальная автоматизация и клиническая безопасность без claim «100% профессиональная терапия».  
> **Позиционирование остаётся:** самопомощь 1-го уровня + семейный мост + направление к специалисту.

### 16.1 Что мы НЕ обещаем (фиксируем навсегда)

| Область | ALADDIN | Очный специалист |
|---------|---------|------------------|
| Глубокая травма, EMDR | ❌ только **направление** | ✅ |
| Диагноз | ❌ только **скрининг** | ✅ |
| Therapeutic alliance | ⚠️ усиленный avatar + trust + continuity | ✅ full |
| 100% картина личности | ❌ structured dashboard | ✅ |

**Обязательный выход:** PHQ ≥ 10, ethics L3, повторяющиеся trauma-keywords → referral + 112.

---

### 16.2 Escalation Ladder (4 уровня) — `wellness_escalation.py`

```
L0 Self-help     → 4 столпа, exercises, check-in
L1 Monitor       → PHQ-lite, outcome 24h, session recap
L2 Specialist    → PHQ≥10 / GAD severe / trauma keywords → referral map + suggest pro
L3 Crisis        → ethics L3 → 112 + block all pillars + alert_log
```

**Авто-правила:**

| Триггер | Уровень | Действие |
|---------|---------|----------|
| Обычный чат | L0 | pillar session |
| 3d low mood | L1 | PHQ-lite |
| PHQ ≥ 10 | L2 | referral + plan + parent opt-in alert |
| trauma/EMDR keywords (teen+) | L2 | stop deep jung → specialist copy |
| suicide/self-harm | L3 | crisis protocol (existing ethics) |

**API:** `GET /api/wellness/escalation/level` → `{level, reason, actions[]}`

**Фаза:** 1 (spec Phase 0, code Phase 1)

---

### 16.3 Jivi-parity automation (добавлено)

#### A. Proactive nudge
- **Триггер:** нет check-in / нет входа 2 дня
- **Действие:** push «Как ты? Всё ок?» → one-tap check-in
- **Модуль:** `wellness_scheduler.py` + `wellness_triggers.py`
- **Фаза:** 2

#### B. Session continuity
- **Триггер:** новая wellness session, есть `wellness_insights`
- **Действие:** system prefix: «В прошлый раз мы остановились на: {observe_next}»
- **Модуль:** `wellness_session_recap.py`
- **Фаза:** 2

#### C. Outcome tracking 24h
- **Триггер:** 24h после deep/cbt session
- **Действие:** push + 1 tap: «легче / так же / хуже» → корректировка `primary_pillar`
- **Таблица:** `wellness_outcomes (session_id, outcome, created_at)`
- **Фаза:** 2

#### D. Smart pillar fatigue
- **Триггер:** 5 сессий подряд один pillar + outcome «так же/хуже»
- **Действие:** suggest другой pillar + message «попробуем иначе»
- **Модуль:** `wellness_four_pillars.py` v3
- **Фаза:** 2

---

### 16.4 Архитектурные усиления (8/10 → 10/10)

| Проблема | Решение | Фаза | Файл |
|----------|---------|------|------|
| Orchestrator stub | **Pillar router v1 в Phase 1** в `ai_companion_router` | 1 | patch router + `wellness_four_pillars.py` |
| Смешение столпов | **Guard:** `assert_single_pillar(session)` pre-LLM | 1 | `wellness_pillar_guard.py` |
| Mood regex MVP | **LLM fallback обязателен** для routing | 2 | `wellness_emotion_agent.py` |
| SQLite prod | **Postgres** + encryption wellness tables | 3 | migration runbook |
| Child 4 кнопки | **UI: 2 кнопки** (Принять себя + Маленькие шаги) | 1 | `WellnessHubScreen` age filter |
| Jung без review | **Clinical + legal checklist** | 0 | `docs/WELLNESS_CLINICAL_REVIEW.md` |
| Premium рано | Premium **после** ethics audit + 48h crisis monitor | 3 | gating in subscription |
| Parent default ON | **Default OFF** teen parent_share | 1 | `wellness_settings` |

**Запреты (hard rules в orchestrator):**
- ❌ один ответ с КПT + Jung + habit
- ❌ copy «AI психолог / психотерапевт»
- ❌ parent видит дословный чат teen

---

### 16.5 Referral map РФ — `wellness_referral.py`

При L2 escalation показывать (locale ru):

- **112** — экстренная помощь
- **8-800-2000-122** — телефон доверия (дети/подростки)
- **051** — экстренная психологическая помощь МЧС
- Текст: «ALADDIN не заменяет очного специалиста»

**API:** `GET /api/wellness/referral?locale=ru&level=L2`

**Фаза:** 0 (copy) + 1 (API)

---

### 16.6 Therapeutic alliance (усиление ⚠️ → ✅)

| Механизм | Как |
|----------|-----|
| Avatar + Rive emotion | pillar → hero emotion map |
| Trust score | existing `companion_trust` в wellness UI |
| Имя героя | «Единорог помнит…» в session recap |
| Continuity | session recap + outcome loop |
| Voice neuro TTS | comfort tone в столпе 3 |

**Фаза:** 2 (logic) + 3 (Rive/TTS polish)

---

### 16.7 P1 enhancements (post-MVP hardening)

| # | Feature | Как лучше | Фаза |
|---|---------|-----------|------|
| 1 | Session recap | `wellness_session_recap.py` reads last insight | 2 |
| 2 | Outcome 24h | scheduler + 1-tap UI | 2 |
| 3 | Pillar fatigue | counter in `wellness_plans.plan_json` | 2 |
| 4 | Apple Health sleep | `HealthKit` read sleep → prefill check-in | 2 iOS |
| 5 | Referral map | static JSON + API | 0–1 |
| 6 | Clinician PDF export | teen-only; aggregate; no raw chat | 2 |
| 7 | A/B pillar copy | feature flag variants + analytics | 2 |

---

### 16.8 P2 enhancements

| # | Feature | Фаза |
|---|---------|------|
| 1 | Parent prompt «как поговорить с ребёнком» | 3 |
| 2 | Seasonal playbooks (школа/экзамены/каникулы) | 3 |
| 3 | Voice-first pillar (senior hands-free) | 3 |

---

### 16.9 Новые backend-модули (v2.1)

```
wellness_escalation.py       # L0–L3 ladder
wellness_referral.py         # RF helplines
wellness_session_recap.py    # continuity
wellness_outcomes.py         # 24h tracking
wellness_pillar_guard.py     # single-pillar enforcement
wellness_pillar_fatigue.py   # smart switch
docs/WELLNESS_CLINICAL_REVIEW.md
docs/WELLNESS_ESCALATION_LADDER.md
```

**DB additions:**

```sql
CREATE TABLE wellness_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    outcome TEXT NOT NULL,  -- better|same|worse
    pillar TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE wellness_escalation_state (
    user_id TEXT PRIMARY KEY,
    level TEXT NOT NULL DEFAULT 'L0',
    reason TEXT,
    updated_at TEXT NOT NULL
);
```

---

### 16.10 iOS additions (v2.1)

| Screen / Service | Назначение |
|------------------|------------|
| `WellnessOutcomeSheet.swift` | 1-tap «легче/так же/хуже» |
| `WellnessReferralSheet.swift` | L2 helplines |
| `WellnessHubScreen` age filter | child: 2 cards only |
| `HealthKitSleepReader.swift` | auto sleep_hours |
| `WellnessClinicianExportService.swift` | PDF teen export |

---

### 16.11 Полный automation flow (target 10/10)

```
Day 0: Check-in → pillar → session → insight saved
Day 0+24h: Outcome push → adjust pillar
Day 2 idle: Proactive nudge
Day 3 low: PHQ-lite → escalation L1
PHQ≥10: L2 referral + specialist suggest
Session start: Recap last insight
5x same pillar + no improvement: fatigue → new pillar
Crisis: L3 block → 112
Weekly: parent digest (opt-in)
Premium: only after 48h crisis monitor clean
```

---

### 16.12 Scorecard target (10/10)

| Критерий | Было | С v2.1 |
|----------|------|--------|
| Клиническая безопасность | 8/10 | **10/10** (ladder + referral + trauma guard) |
| UX / 4 столпа | 9/10 | **10/10** (child 2-btn + outcome UX) |
| Автоматизация | 7→9/10 | **10/10** (nudge + recap + outcome + fatigue) |
| iOS / backend | 8/10 | **10/10** (pillar router P1 + postgres P3) |
| vs Jivi | 9/10 | **10/10** (parity + family loop) |

---

### 16.13 Cursor TODO v2.1

Полный список — см. Cursor TODO (**v2.2: ~105 задач**).

---

## 17. Дополнения для лидерства в нише (без живых коучей, без PPG)

> **Не догоняем:** Jivi (медицина, PPG), Wysa (RCT, human coach).  
> **Цель:** №1 в **family security + wellness** с измеримым прогрессом.

### 17.1 Что НЕ добавляем

| Skip | Почему |
|------|--------|
| PPG / камера стресса | Не core ALADDIN; мед. риски |
| «AI психотерапевт» в UI | Только «Глубокое исследование» + disclaimer |
| Живые коучи | Другая модель; не в scope |

### 17.2 Что добавляем (простым языком)

| # | Функция | Простыми словами | Фаза | TODO |
|---|---------|------------------|------|------|
| A | **Together Mode** | Родитель и ребёнок 3 мин дышат вместе — общий таймер, не чтение переписки | 2 | p2-44 |
| B | **Trust Center** | Экран «как мы работаем»: что храним, crisis, L0–L3, без ложных RCT | 1 | p1-24 |
| C | **Weekly Meaning** | 1×/нед «10 мин понять себя» + streak инсайтов | 2 | p2-45 |
| D | **Themes для родителя** | «Школа, друзья, тревога» — темы, не текст чата | 2 | p2-46 |
| E | **AI для родителя** | Скрипты «как поговорить с ребёнком» — AI, не человек | 3 | p3-16 |
| F | **Security + Mood** | Грустно + угроза online → один alert родителю | 2 | p2-47 |
| G | **Streaks / badges** | «7 дней check-in» — мягкая мотивация teen | 2 | p2-48 |
| H | **Sleep stories** | 5–10 аудио засыпания (Calm-lite, не PPG) | 3 | p3-17 |
| I | **Widget check-in** | Виджет: 1 tap emoji с lock screen | 3 | p3-18 |
| J | **Teen privacy** | Teen сам: родителю кризис / сводка / ничего | 1 | p1-25 |
| K | **Weekly PDF** | Авто-отчёт прогресса без дословного чата | 3 | p3-19 |
| L | **Referral расширенный** | 112 + телефон доверия + 051 + регионы | 0 | p0-13 |

### 17.3 Уже в v2.1 (не забыть)

- outcome 24h, insights, escalation L0–L3  
- session recap, proactive nudge, pillar fatigue  
- 4 столпа, reflective «Глубокое исследование»  
- clinician PDF teen (p2-37), Apple Health sleep (p2-36)

### 17.4 Формула «лучше в нише»

```
Security + 4 столпа + Глубокое исследование
+ Прогресс (outcome, insights, weekly meaning)
+ Семья (Together, themes, teen privacy, AI parent scripts)
+ Wellness ↔ Online safety fusion
— PPG, — живые коучи
```

---

---

## 18. Локализация (i18n) — полный охват

> **Сейчас в TODO:** одна задача **p1-14** (базовые `wellness_*` ru/en).  
> **Ниже — полная матрица**, чтобы ничего не забыть при реализации.

### 18.1 Языки и приоритет

| Приоритет | Языки | Когда |
|-----------|-------|-------|
| P0 (launch) | **ru + en** | Фазы 0–2 |
| P2 | +kk, uk, … | по `LocalizationManager` / тарифам |
| P3 | 100+ (как Jivi) | только если отдельный wellness export |

**Правило:** в UI **нет** хардкода — только ключи `wellness_*` / `companion_*`.

### 18.2 Где лежат строки

| Слой | Файл / формат | Ответственность |
|------|---------------|----------------|
| iOS UI | `Core/Localization/LocalizationManager.swift` | все экраны, кнопки, ошибки |
| Backend user-facing | JSON `wellness_i18n/{locale}/` | вопросы PHQ/GAD, referral, exercise steps |
| Push | `wellness_push_{locale}.json` | nudge, outcome 24h, weekly meaning |
| Legal | `docs/wellness/legal_{locale}.md` → keys | consent, disclaimer |
| PDF export | шаблон ru/en | clinician export |

**API:** заголовок `Accept-Language` или `?locale=ru` — уже в referral; расширить на assessments, exercises, prompts **user-visible parts only**.

### 18.3 Матрица: что переводим по фазам

| Блок | Примеры ключей | Фаза | TODO |
|------|----------------|------|------|
| 4 столпа Hub | `wellness_pillar_cognitive_title`, `_subtitle` | 1 | p1-14, p18-01 |
| Consent / Trust Center | `wellness_consent_*`, `wellness_trust_*` | 0–1 | p0-04, p1-24, p18-02 |
| Check-in | emoji labels, sleep/stress | 1 | p18-03 |
| Assessments PHQ/GAD/burnout | вопросы + варианты ответов | 1–2 | p18-04 |
| Exercises CBT/Jung | шаги thought record, grounding | 2 | p18-05 |
| Reflective sub-modes | 5 chips + hints | 2 | p18-06 |
| Outcome / Referral sheets | легче/так же/хуже, 112, телефоны | 2 | p18-07 |
| Together Mode | инструкции родителю и ребёнку | 2 | p18-08 |
| Family dashboard | themes labels, aggregate copy | 2 | p18-09 |
| Parent playbook (AI) | скрипты UI, не LLM dump | 3 | p18-10 |
| Push notifications | все wellness push | 2 | p18-11 |
| Widget | короткие строки | 3 | p18-12 |
| Crisis / escalation | L2/L3 тексты, ethics sync | 1 | p18-13 |
| suggested_actions в chat | кнопки «Разобрать мысль» и т.д. | 1 | p1-15, p18-14 |
| Backend errors | `wellness_error_*` | 1 | p18-15 |

### 18.4 Что НЕ переводим через UI (остаётся на сервере)

- System prompts для LLM (ru primary; en mirror для `response_language`)
- Crisis templates — **да** переводим (user sees)
- Clinical disclaimers — **обязательно** ru + en legal review

### 18.5 QA локализации

- [ ] Нет пустых ключей в ru/en (скрипт `scripts/check_wellness_l10n.py`)
- [ ] Длинные немецкие/английские строки не ломают Hub cards (SwiftUI preview)
- [ ] PHQ вопросы совпадают с официальными валидированными переводами
- [ ] Teen/child: простой язык, не копия взрослого текста

### 18.6 Полный чеклист ключей

**Файл:** [WELLNESS_I18N_CHECKLIST.md](./WELLNESS_I18N_CHECKLIST.md) — ~120 ключей `wellness_*`, backend JSON, push, QA.

### 18.7 Cursor TODO §18

Задачи **p18-01 … p18-15** — в [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md).

---

## 19. Передача другой ML-системе (Cursor / Claude / GPT)

> **Цель:** новая ML понимает продукт на 100%, подтверждает подход, прикрепляет **131 TODO** к панели Cursor и не ломает этику/семью. Архитектура знаний героев — **§4.3**.

### 19.1 Что отправить

1. **Сообщение-стартер** — полный текст в [WELLNESS_ML_HANDOFF.md](./WELLNESS_ML_HANDOFF.md) **§0** (копипаст в новый чат).
2. **Файлы через @ mention:**
   - `@docs/WELLNESS_ML_HANDOFF.md`
   - `@docs/WELLNESS_IMPLEMENTATION_STATUS.md`
   - `@docs/WELLNESS_PLATFORM_MASTER_PLAN.md`
   - `@docs/WELLNESS_CURSOR_TODO.md`
3. **Опционально:** `@docs/WELLNESS_I18N_CHECKLIST.md`, `@.cursor/rules/wellness-platform-expert.mdc`
4. **Workspace root:** открыть папку `ALADDIN_iOS` (не весь `ALADDIN_NEW` 28GB).

### 19.2 Что должна сделать новая ML (порядок)

| Шаг | Действие | Результат |
|-----|----------|-----------|
| **A** | Прочитать handoff + master plan | Таблица: 4 столпа, запреты, gate, риски, первые 5 ID |
| **B** | `TodoWrite` — импорт из `WELLNESS_CURSOR_TODO.md` | 131 пункт в **панели TODO** Cursor |
| **C** | Проверить rule `wellness-platform-expert.mdc` | Контекст при wellness-файлах |
| **D** | **Фаза 3** (или §18) после OK PO | Ф0–Ф2 уже закрыты — см. IMPLEMENTATION_STATUS |

Подробно: handoff **§3–§11** · TodoWrite **§10**.

### 19.3 Как прикрепить 131 TODO к панели Cursor (важно)

Cursor **не импортирует** markdown-чеклист автоматически. Два рабочих способа:

**Способ 1 — через агента (рекомендуется):** после Шага A напишите:

```text
Импортируй все задачи из docs/WELLNESS_CURSOR_TODO.md в Cursor TODO.
id = p0-01, p1-12, … (как в файле)
content = русский текст задачи
status = pending; p18-01 = completed
Батчи: Фаза 0, 1, 2, 3+i18n (TodoWrite).
```

**Способ 2 — без панели:** вести прогресс только в `WELLNESS_CURSOR_TODO.md` (`[ ]` → `[x]`).

### 19.4 Подтверждение «делаем правильно»

Новая ML **обязана** явно согласиться с:

- [ ] 4 кнопки Hub и **один столп на сессию**
- [ ] Child: 2 кнопки; без PHQ-9 и снов
- [ ] Teen privacy: родитель без дословного чата
- [ ] L0–L3 escalation + `companion_ethics` на L3
- [ ] ru+en i18n для user-visible
- [ ] Skip: PPG, live coaches, «психотерапевт» в UI

Без галочек — **не стартовать Фазу 3**.

**Прогресс (2026-06-01):** 131/131 · Ф0–Ф3 + §18 = 100% · VPS deploy + smoke + prod verify OK.

### 19.5 Индекс всех wellness-документов

| Документ | Статус |
|----------|--------|
| WELLNESS_PLATFORM_MASTER_PLAN.md | ✅ v2.5 §4.3 |
| WELLNESS_IMPLEMENTATION_STATUS.md | ✅ 131/131, deploy + verify |
| WELLNESS_ML_HANDOFF.md | ✅ v2.0 |
| WELLNESS_CURSOR_TODO.md | ✅ 131 ID (Ф2 закрыта) |
| WELLNESS_APPLE_HEALTHKIT_SETUP.md | ✅ PO manual |
| WELLNESS_I18N_CHECKLIST.md | ✅ |
| WELLNESS_I18N_GLOSSARY.md | ✅ p18-01 |
| ADR-WELLNESS-PLATFORM.md | ☐ p0-01 |
| wellness_knowledge/cognitive/v1/pack.yaml | ☑ draft p0-15 |
| WELLNESS_ESCALATION_LADDER.md | ☐ p0-11 |
| WELLNESS_CLINICAL_REVIEW.md | ☐ p0-08 |

---

*Document version: 2.5-final | 2026-06-01 | §4.3 Knowledge Pack | §19 ML handoff | 131 TODO | Target 10/10*
