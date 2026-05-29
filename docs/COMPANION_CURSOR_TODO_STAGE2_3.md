# Companion — Cursor TODO (Этап 2–3)

**Обновлено:** 2026-05-29 (Sprint 4–5 MVP код ✅ · **build 216** → новый TestFlight)  
**Главный runbook:** [COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md)  
**Handoff:** [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md) · **План:** [COMPANION_PLAN_TO_100_PERCENT.md](./COMPANION_PLAN_TO_100_PERCENT.md)

> Отмечай `[x]` здесь и в панели **Cursor TODO** агента. Не трогать: Rive 07, GATE-DIALOG без PO.

**Рабочая папка:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

---

## Старт (10 мин)

- [x] `git log -1` → `351a9b03` или новее
- [x] `./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru` → **exit 0**
- [ ] Закоммитить `scripts/verify_companion_p0_prod.sh`, если правки только локально

---

## Этап 1 — довести до пользователя (блокер)

- [x] **TestFlight build 215** — в TestFlight + на тестовом iPhone (2026-05-29)
- [x] **Smoke device:** Kids → Друзья → чат → chips → режим — подтверждено PO

---

## Этап 2 — Sprint 4 (6 пунктов)

| # | Задача | Runbook |
|---|--------|---------|
| [x] | **4.1 Redis** — VPS env + restart (2026-05-29) | §4.1 |
| [x] | **4.2 Orchestrator** — VPS `COMPANION_USE_ORCHESTRATOR=1`, verify OK | §4.2 |
| [x] | **4.3 Chips** — device TF215 | §4.3 |
| [x] | **4.4 Social bridge** — verify шаг 18 + fix profile `social_bridge` | §4.4 |
| [x] | **4.5 Teen playbook** — pytest green | §4.5 |
| [x] | **4.6 Trust эмпатия** — `+N к доверию` в UI, stream meta | §4.6 |

---

## Этап 3 — Sprint 5 (приоритет PO → остальное)

### Приоритет 1 (после TF215)

- [x] **5.2 Режимы** — меню fast/think на device (smoke TF215)
- [x] **5.3 Фото/PDF** — галерея `ImagePickerView` (iOS 15.2+) + PDF `fileImporter` → stream
- [x] **5.7 COGS** — карточка в «Моё» родителя
- [x] **5.10 Workspaces** — список + создать + `workspace_id` в stream
- [ ] **TestFlight 216** — Archive после COGS/вложений/social-bridge fix

### Приоритет 2

- [x] **5.1 Поиск** — [COMPANION_SPRINT5_MVP_ENV.md](./COMPANION_SPRINT5_MVP_ENV.md) (`FEATURE_WEB_SEARCH_ENABLED=0`)
- [x] **5.4 Trust streak** — UI при streak ≥ 3
- [x] **5.5 Семья в промпте** — stream → `companion_chat()` (один путь)
- [x] **5.8 60+ Main** — карточка в `01_MainScreen.swift` (код)
- [x] **5.11 Long context** — pytest `build_long_context_hint`

### Уже OK / только дока

- [x] **5.12 Android** — `docs/android/COMPANION_ANDROID_STUB.md`
- [x] **5.13 Adult** — `docs/adult/`
- [x] **5.14 Adult policy** — `pytest Tests/test_adult_companion_policy.py`
- [ ] **5.6 Tools** — опц. `tools_used` в debug / «Моё»
- [ ] **5.9 Media** — stub в доке, `FEATURE_IMAGE_GEN_ENABLED=0`

---

## Этап 2b — Блок G «Мир героев» (device)

- [x] **G.1** — карточка Rewards (TF215 smoke)
- [x] **G.2** — входы → `companionHome` (код + smoke)
- [x] **G.3** — Mic coach + hold-only (код + smoke)

---

## GATE

- [x] **GATE-OPS** — health + verify **18/18** (2026-05-29) — [signoff](./COMPANION_GATE_OPS_SIGNOFF_2026-05-29.md)

---

## Premium озвучка (VOICE-PREM) — [план](./COMPANION_PREMIUM_VOICE_PLAN.md)

> Картинки **одинаковые** на всех тарифах. Меняется **только TTS**: Free → AVSpeech×3, Premium → ElevenLabs.

### Спринт 1–2 (почти $0)

- [x] 2 ключа OpenRouter + rotator + watchdog
- [x] 3 голоса AVSpeech (voice id: Katya / Yuri / Milena RU)
- [x] PNG герои + fallback без Rive
- [x] Честный offline / без шаблона «47 угроз»

### Спринт 3–4 (Premium)

- [x] API `POST /companion/tts` + capability `neuro_tts_premium`
- [x] iOS `CompanionNeuroTTSPlayer` + fallback AVSpeech
- [x] Кэш 30 фраз (server)
- [ ] **VOICE-PREM-04** — 3 voice id 🦄🧞🧑 → [COMPANION_ELEVENLABS_VOICES_RU.md](./COMPANION_ELEVENLABS_VOICES_RU.md) + `configure_companion_neuro_tts_env.sh`
- [ ] **VOICE-PREM-03** — пилот genie + prewarm (**после 04** и ключей)
- [x] Запросить прайс **Yandex SpeechKit** — [сравнение](./COMPANION_TTS_PRICING_COMPARE.md)
- [x] VPS: `FEATURE_NEURO_TTS_ENABLED=1` + deploy + Premium cap (TTS 424 до ключей)

### Спринт 5+ / 2027+

- [ ] Production Rive (HERO-3-07)
- [ ] OpenRouter fallback без Hermes CLI
- [ ] Realtime voice beta Premium+ (2027+)

---

## Финиш (критерий «Этап 2+3 закрыты»)

- [x] Повторный `verify_companion_p0_prod.sh` exit 0 после Redis env
- [x] `pytest Tests/test_companion_sprint4.py Tests/test_companion_sprint5.py` — 15 passed
- [x] Обновить [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) + [WHAT_REMAINS](./COMPANION_WHAT_REMAINS.md)

---

## Справка: что уже ✅

| Шаг | Статус |
|-----|--------|
| Код `351a9b03`, build 215 в git | ✅ |
| VPS deploy Sprint 4–5 (2026-05-29) | ✅ |
| Verify 17 шагов (3 героя, `/domains`, `/cogs`, stream+`chat_mode`) | ✅ |
| TestFlight 215 + smoke device | ✅ 2026-05-29 |
| Sprint 4–5 MVP (код+VPS) | ✅ |
| TestFlight **216** | ⏳ |

**Осталось по 102 задачам:** [COMPANION_WHAT_REMAINS.md](./COMPANION_WHAT_REMAINS.md)

**Порядок сейчас:** Archive **216** → smoke → Rive **07** / GATE только по PO.
