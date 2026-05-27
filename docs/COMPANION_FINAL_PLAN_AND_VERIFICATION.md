# Companion Platform — финальный план + проверки + Cursor TODO

**Дата:** 2026-05-26  
**Прогресс:** **63 / 102** (62%) · HERO-3: **22 / 26** — [трекер](./COMPANION_PROGRESS_TRACKER.md)  
**Трекер (открыть в Cursor):** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)  
**Матрица HERO-3:** [COMPANION_HERO3_READINESS_MATRIX.md](./COMPANION_HERO3_READINESS_MATRIX.md)  
**Источник правды:** [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md) · [COMPANION_ML_HANDOFF_FULL.md](./COMPANION_ML_HANDOFF_FULL.md) · [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md)

**Правило закрытия задачи:** ✅ только если **BE + iOS + Test + Prod** (где применимо).

---

## Ответ: полный спектр эмоций + юмор — всё в плане?

| Ваш пробел | Задачи в плане | Проверка (gate) |
|------------|----------------|-----------------|
| **Весь спектр эмоций** (не только sad) | **P1-30** + **P1-23** + **P1-08** — таблица § CX.4 (12 эмоций) | **GATE-EMO-SPEC** |
| **Юмор в ответах** | **P1-26** промпт + `playful` emotion + preset playful | 3 тест-шутки → ответ с юмором PG |
| **Подстройка под настроение** | **P1-30** + **P2-11** | EMO-3 |
| **Не security-intent** | **P1-27** + **P1-30** | EMO-4 |
| **Живое лицо Rive** | **P1-08** + **P1-23** | EMO-5 |

**Итог:** герои **разные под каждое настроение**; **юмор** — ветка `playful` + текст. Код — после **GATE-EMO**.

---

## Порядок блоков (критический путь)

```
OPS → CX (P1-26…30, P1-25) → GATE-CX
  → P1-07…11 → GATE-P1
  → GATE-EMO (P1-08, P1-30, P1-23, P2-11) + P1-13 голос
  → P1+ production → GATE-PROD
  → P2 (аудитории 60+, teen) → GATE-P2
  → P3 / Adult
```

---

## БЛОК 0 — P0 (MVP) · 19/19 спринт «готово»

| ID | Задача | Статус |
|----|--------|--------|
| P0-01…P0-19 | JWT, policy, DB MVP, voice stub, iOS Hub/чат, smoke, deploy… | ✅ репо |

### GATE-P0 — приёмка блока

- [x] `PYTHONPATH=. python3 Tests/test_companion_p0_smoke.py` → **10 OK** (2026-05-27)
- [ ] На устройстве: Kids → Игры → **«Мир героев»** → `Главное/Герои/Моё` (минимум) + **HERO-3-08b PASS** ([чеклист](./COMPANION_08B_DEVICE_CHECKLIST.md))
- [ ] Prod: `./scripts/verify_companion_p0_prod.sh` (базовый)
- [ ] Слои 🟡 зафиксированы: SQLite, voice stub, orchestrator — закрываются в P1+ / P2

---

## БЛОК 1 — OPS · 3/4

| ID | Задача | Статус | Test / Verify |
|----|--------|--------|---------------|
| OPS-01 | Деплой SSH P1-04…06 на прод | ✅ | `deploy_companion_p0.sh` exit 0 |
| OPS-02 | Расширить verify | ✅ | = P1-15 |
| OPS-04 | Алерт LLM cost | ✅ | `companion_llm_cost_alert.sh` + cron VPS |
| OPS-05 | DoD после каждого деплоя | ✅ | чеклист §12 handoff |

### GATE-OPS

- [ ] `curl` health + OpenAPI companion paths на `aladdin-ai.ru`
- [ ] Verify: characters, capabilities, **stream**, threads, memory, profile, feedback, cosmetics
- [ ] Ручной: stream + resume на устройстве

---

## БЛОК 2 — CX (жизнь, возрасты, эмоции от настроения) · 6/6 ✅

| ID | Задача | Статус | Test / Verify |
|----|--------|--------|---------------|
| P1-26 | Persona **life-first** (не security-first) | ✅ | `test_companion_persona_not_security_only` |
| P1-27 | `companion_intent_router` domains+mood | ✅ | meta `domain`, `mood` |
| P1-28 | Персоны child/teen/parent/senior | ✅ | 4 pytest |
| P1-29 | Режим «эксперт безопасности» toggle | ✅ | iOS + BE |
| P1-30 | Полный спектр эмоций + mood | ✅ BE+iOS enum | GATE-EMO-SPEC ⏳ device |
| P1-25 | Этика L1–L3 одиночество + кризис | ✅ | unit 5/5 |

### GATE-CX

- [ ] Сообщение «мне одиноко и скучно» → ответ **без** VPN, с эмпатией
- [ ] «мне грустно» → `meta.emotion` ∈ {sad, comfort}
- [ ] «расскажи анекдот» → playful / happy
- [ ] «помоги с VPN» → security контекст
- [ ] Кризис-фраза → L3 (не продолжать ролевую игру)

---

## БЛОК 3 — P1 спринт (фичи) · 10/11

| ID | Задача | Статус | Test / Verify |
|----|--------|--------|---------------|
| P1-01…P1-06 | threads, consent, memory, personality, feedback, stream | ✅ | smoke + device |
| P1-07 | Косметика iOS | ✅ | GET cosmetics + UI |
| P1-08 | **Rive** инфра + procedural | ✅ инфра | финал .riv → **HERO-3-07** |
| P1-09 | Legal | ✅ | legal review |
| P1-10 | Аналитика N1–N6 | ✅ | iOS + `POST /api/ai/companion/analytics` |
| P1-11 | Banner 20% лимита | ✅ | UI при usage&gt;80% |

### GATE-P1

- [ ] Family: consent, memory, personality
- [ ] Cosmetics: наряд отображается
- [ ] Legal тексты в сборке

---

## БЛОК 3b — HERO-3 (3 героя Figma→Rive) · 22/26

> План: [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) · Матрица: [COMPANION_HERO3_READINESS_MATRIX.md](./COMPANION_HERO3_READINESS_MATRIX.md)  
> Порядок: `17` → `02` → `07`+`22` → `08` → `18→19→26` → `23→24` → `10` → `25` → `11`

| ID | Задача | Статус |
|----|--------|--------|
| HERO-3-01 | ADR §1–11 + §2.1–2.3 | ✅ |
| HERO-3-03…06, 12…16, 18–19 | BE genie, Hub, witty, timeline, lip-sync | ✅ |
| HERO-3-20, 21 | ADR 13 state + матрица готовности | ✅ док |
| HERO-3-23…26 | thinking policy, sad UI, emotion sync, debounce unit | ✅ |
| HERO-3-17 | Motion + Mimic Spec Figma ([sign-off](./COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md)) | ⏳ |
| HERO-3-02, 07, 08, 09, 10, 11, 22 | Figma, .riv, Rive, Bible, deploy, QA, riv CI | ⏳ |

### GATE-HERO-3-IOS-α (до production `.riv`)

- [x] `CompanionStreamEmotionDebouncer` 400 ms + **HERO-3-26** unit PASS
- [ ] Фазы listening / thinking / speaking различимы на device (procedural §2.2)
- [x] 🧞 только `genie`; `aladdin` → 🧑‍🎓 (**06** ✅)
- [x] Text-only stream: `speaking` ≥1.2 s → content emotion (**18** ✅)
- [x] TTS end → `contentEmotionAfterSpeaking`, не hardcoded `.happy` (**18** ✅)
- [x] **HERO-3-23:** во время `thinking` нет скачка в `playful` с SSE (meta on done)
- [x] **HERO-3-24:** `sad`/`comfort` без ✨/playful overlay

### GATE-EMO-EMPATHY (device, 5 мин × 3 профиля)

| Профиль | Тестер | Сценарии (не только D10 технич.) |
|---------|--------|----------------------------------|
| **child** | 1 | шутка PG; грусть → comfort; без genie в Hub |
| **teen** | 1 | genie+witty уместен; одиночество без VPN spam |
| **senior** | 1 | aladdin calm/nostalgic; без шуток при грусти |

- [ ] Протокол: tester, дата, build, запись hero-зоны
- [ ] Отличие от **GATE-EMO:** эмпатия и тон, не только смена state

---

## БЛОК 4 — GATE-EMO (грустный герой + живое лицо + mood) · частично

> **HERO-3-18/19** ✅ в iOS; **GATE-EMO** закрывается с **HERO-3-07** (.riv) + device D10.

| ID | Что закрывает | Статус | Test / Verify |
|----|---------------|--------|---------------|
| P1-30 | enum `sad`, mood → emotion | ✅ BE | unit |
| P1-08 | Rive файлы, state machine | 🟡 инфра | нет production .riv |
| P1-23 | stream/voice/chat → heroEmotion | 🟡 | **18/19** ✅; Rive ⏳ |
| P2-11 | классификатор mood | ✅ MVP | prod logs |

### GATE-EMO (обязательно все ✅)

- [ ] **EMO-1:** 13 state (HERO-3-20): 9 контент + 4 фазы — `idle`, `happy`, `sad`, `playful`, `comfort`, `celebrate`, `curious`, `nostalgic`, `excited`, `alert`, `listening`, `speaking`, `thinking` — **HERO-3-25** pytest sync
- [ ] **EMO-2:** Rive state на **каждую** эмоцию (визуально различимы)
- [ ] **EMO-3 (настроение):** «мне грустно» → sad/comfort; «расскажи шутку» → playful + **юмор в тексте**
- [ ] **EMO-4:** «фишинг» → alert; обычный чат → не alert
- [ ] **EMO-5:** stream SSE `emotion` меняет Rive в реальном времени
- [ ] **GATE-EMO-SPEC:** 12 фраз из COMPANION_IMPLEMENTATION_TODOS § CX.4 — все ✅

---

## БЛОК 5 — P1+ Production · 0/12

| ID | Задача | Test / Verify |
|----|--------|---------------|
| P1-12 | Postgres + Redis | нет SQLite на VPS; smoke migration |
| P1-13 | Голос (SpeechManager + WS) | 13a–d чеклист; E2E голос |
| P1-14 | XCUITest | CI green |
| P1-15 | Prod verify полный | = OPS-02 |
| P1-16 | ADR hot path | док + комментарии |
| P1-17 | Accessibility | a11y QA |
| P1-18 | Rate limit | 429 tests |
| P1-19 | App Store pack | checklist §17 + **3 скриншота Hub** (unicorn / aladdin / genie) |
| P1-20 | RU/EN | переключение языка |
| P1-21 | Offline cache | airplane mode |
| P1-22 | Post-LLM moderation | blocklist tests |
| P1-23 | Эмоции Grok-level | = GATE-EMO |

### GATE-PROD

- [ ] 4 слоя ✅ на P1-12, P1-13, P1-14, P1-15
- [ ] TestFlight checklist P1-19

---

## БЛОК 6 — P2 Grok + аудитории · 0/15

| ID | Задача | Test / Verify |
|----|--------|---------------|
| P2-01 | Web search | citations в ответе |
| P2-02 | Orchestrator | feature flag + fallback tests |
| P2-03 | Fast/Reasoning/Think | mode switch |
| P2-04 | Фото/PDF | upload E2E |
| P2-05 | Trust decay/streak | unit trust |
| P2-06 | Family context | prompt contains family |
| P2-07 | Responses API | contract test |
| P2-08 | COGS dashboard | alert |
| P2-09 | Figma ↔ Rive assets | visual QA |
| P2-11 | Mood-aware (детализация) | = GATE-EMO-3 |
| P2-12 | Life domains API | GET /domains + iOS chips |
| P2-13 | Social bridge | loneliness → suggestion UI |
| P2-14 | **Senior 60+** вход | Main card → senior persona |
| P2-15 | **Teen loneliness** | playbook pytest |
| P2-16 | Trust за эмпатию | trust++ на support msg |
| P2-17 | A/B humor_density genie+teen | BE flag; после HERO-3 |

### GATE-P2

- [ ] Senior: «мне скучно» → nostalgic/calm, без security spam
- [ ] Teen: «нет друзей» → P2-15 tone + parent escalation path
- [ ] P2-01 search на «что за фильм X»

---

## БЛОК 7 — P3 · 0/6 · Adult · 0/3

| ID | Задача |
|----|--------|
| P3-01…P3-06 | image, video, workspaces, context, Android, Adult Store |
| A-01…A-03 | adult OpenAPI, policy tests, repo stub |

### GATE-P3

- [ ] После GATE-PROD + метрики §10 master plan

---

## Отменено (не в Cursor TODO)

X-01…X-07 (запись, push «вернись», daily backup, …)

---

## Cursor TODO — полный список (скопировать / синхронизировать)

### ✅ completed (49)

```
P0-01 … P0-19
P1-01 … P1-09 P1-11
P1-25 … P1-30
OPS-01 OPS-02 OPS-05
HERO-3-01 HERO-3-03 HERO-3-04 HERO-3-05
HERO-3-12 HERO-3-13 HERO-3-14 HERO-3-16 HERO-3-18 HERO-3-19
P2-11
```

### ⏳ pending (46)

```
P1-10
OPS-04
P1-12 … P1-23
HERO-3-02 … HERO-3-17 HERO-3-08 HERO-3-10 HERO-3-11 HERO-3-12 … HERO-3-16
P2-01 … P2-10 P2-12 … P2-16
P3-01 … P3-06
A-01 A-02 A-03
```

*(Полный список: [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md))*

### Контрольные ворота (блоки)

```
GATE-OPS GATE-CX GATE-P1 GATE-EMO GATE-PROD GATE-P2 GATE-P3
GATE-DIALOG-REGRESS (25 задач ✅)  GATE-DIALOG (10 сценариев — финал)
```

---

## GATE-DIALOG-REGRESS — тест всего, что уже сделано (25 задач)

> **Когда:** можно **сейчас** (до новых фич).  
> **Кто:** QA / ML на устройстве + `test_companion_p0_smoke.py` + verify prod после OPS-01.

| # | ID | Что проверить | Как (шаг) | Pass |
|---|-----|---------------|-----------|------|
| R1 | P0-01 | JWT age_band, consent | Login device → decode JWT child/parent | ✅ auto |
| R2 | P0-02 | policy block 18+ | Запрос NSFW в Kids → block | ✅ auto |
| R3 | P0-03 | trust/threads persist | 2 сообщения → kill app → trust/thread на месте | ⏳ device |
| R4 | P0-04/05 | voice WS + token | Mic → WS connect (не 401) | 🟡 token ✅, WS device |
| R5 | P0-06/07 | companion chat API | Отправить «привет» → ответ не mock SFM | ✅ auto |
| R6 | P0-08 | Hub + Conversation | Kids → Герои → чат открывается | ⏳ device |
| R7 | P0-09/10 | voice + emotion lite | Mic → emoji/scale меняется | ⏳ device |
| R8 | P0-11 | только Kids вход | Main без companion hub (или скрыт) | ⏳ device |
| R9 | P0-12 | no mock prod | verify script не SFM envelope | ✅ auto |
| R10 | P0-13 | usage meters | Много сообщений → лимит/счётчик (если настроен) | ⏳ device |
| R11 | P0-14 | smoke | `python3 Tests/test_companion_p0_smoke.py` 10 OK | ✅ auto |
| R12 | P0-15/17/18 | deploy, capabilities | capabilities скрывает mic если API off | ✅ auto |
| R13 | P0-16/19 | modules, env | health 200 на проде | ✅ auto |
| R14 | P1-01 | threads list | Hub → видна история / новый thread | ✅ auto API |
| R15 | P1-02 | parent consent | Без consent → блок; Family → вкл | ⏳ device |
| R16 | P1-03 | memory | Family memory off/on; export | ✅ auto API |
| R17 | P1-04 | personality preset | Family → calm/playful → тон ответа мягче/игривее | ✅ auto API |
| R18 | P1-05 | feedback | Лайк на сообщение → POST ok | ✅ auto |
| R19 | P1-06 | stream resume | Стрим → режим полёт → «Продолжить загрузку» → докачка | ✅ API stream; ⏳ resume UI |

**GATE-DIALOG-REGRESS = PASS:** автоматика **14/19** ✅ (см. [отчёт 2026-05-26](./COMPANION_GATE_DIALOG_REGRESS_REPORT_2026-05-26.md)); **5 пунктов** — только на устройстве; R4/R7 🟡 до P1-13.

**Прогон 2026-05-26:** smoke **10/10 OK** · verify prod **OK** · chat/threads/stream/feedback/profile/memory на проде **OK**.

---

## GATE-DIALOG — 10 сценариев «полноценного общения» (финал большой задачи)

> **Когда:** полный PASS — после **GATE-CX + GATE-EMO + P1-13** (минимум).  
> **Частичный PASS сейчас:** сценарии 2, 4, 6, 8, 9 — частично; 1, 3, 5, 7, 10 — после CX/EMO.

| ID | Сценарий | Реплика пользователя | Ожидание компаньона | Задачи | Сейчас |
|----|----------|----------------------|---------------------|--------|--------|
| **D01** | **Ребёнок шутит** | «Расскажи смешную историю про единорога!» | Ответ **с юмором** PG; герой **playful**; не про VPN | P1-26, P1-30, P1-08, P1-23, P1-04 | 🟡 текст; 🟡 emoji |
| **D02** | **Подросток без друзей** | «Мне 14, в классе никто не разговаривает, одиноко» | Эмпатия, советы PG-13; **не** лекция про VPN; comfort/sad | P1-28, P2-15, P1-25 L2, P2-13 | 🟡 |
| **D03** | **Бабушка скучает (60+)** | «Мне 68, дома одна, скучно, некому поговорить» | Тёплый неторопливый тон; nostalgic/calm; темы воспоминаний | P2-14, P1-28 senior, P1-26 | ❌ |
| **D04** | **Родитель устал** | «Устал на работе, всё раздражает» | Поддержка mentor/calm; вопрос «что помогло бы сейчас» | P1-28 parent, P1-04 | 🟡 |
| **D05** | **Обрыв сети в диалоге** | Длинный вопрос → стрим → offline → resume | Текст **докачался**; thread не потерян | P1-06 ✅, P1-21 | ✅ частично |
| **D06** | **Память разговора** | Вчера: «люблю динозавров» → сегодня: «о чём мы вчера?» | Вспоминает тему (memory on) | P1-03 ✅ | 🟡 |
| **D07** | **Согласие родителя** | Ребёнок без consent | Companion **недоступен** + понятный экран | P1-02 ✅ | ✅ |
| **D08** | **Security по запросу** | «Мне пришло подозрительное письмо со ссылкой» | alert + помощь; **режим защиты** | P1-29, P0-02 | 🟡 |
| **D09** | **Голосом как с другом** | Hold mic: «Как прошёл твой день?» | STT → ответ **голосом/текстом**; не stub-фраза WS | P1-13, P0-09 | 🟡 stub |
| **D10** | **Спектр эмоций за 5 мин** | ① «Ура, 5!» ② «Мне грустно» ③ «Анекдот!» ④ «Фишинг!» | happy→sad/playful→playful→alert (**разные** лица Rive) | P1-30, P1-23, P1-08 | ❌ |

### Критерий GATE-DIALOG (финал)

- [ ] **D01–D10** все ✅ на **TestFlight build** (prod API).
- [ ] **GATE-DIALOG-REGRESS** R1–R19 ✅.
- [ ] Ни один сценарий не уходит в **только VPN** без запроса (кроме D08).
- [ ] Юмор (D01, D10③) — **есть шутка в тексте**, не отказ «я только про безопасность».
- [ ] Протокол: tester, дата, build, скриншот/запись hero-зоны для D10.

### Порядок прогона

```
1. GATE-DIALOG-REGRESS (R1–R19)     ← сейчас
2. OPS-01 + GATE-OPS
3. P1-26…30 + GATE-CX
4. P1-08/23/30 + GATE-EMO
5. P1-13 + D09
6. P2-14/15 + D02/D03
7. GATE-DIALOG D01–D10 полный       ← финал большой задачи
8. GATE-PROD → GATE-P2 → GATE-P3
```

---

## Сводная таблица прогресса

| Блок | Задач | Готово | Gate |
|------|-------|--------|------|
| P0 | 19 | 19 | GATE-P0 |
| OPS | 4 | 3 | GATE-OPS |
| CX | 6 | 6 | GATE-CX ⏳ device |
| P1 | 11 | 10 | GATE-P1 |
| HERO-3 | 19 | 10 | → GATE-EMO / D10 |
| P1+ | 12 | 0 | GATE-PROD |
| P2 | 16 | 1 | GATE-P2 |
| P3 | 6 | 0 | GATE-P3 |
| Adult | 3 | 0 | (в GATE-P3) |
| **GATE-DIALOG** | 2 | 0 | REGRESS + D01–D10 |
| **Всего** | **95** | **49** | **52%** |

**Финал большой задачи Companion:** **GATE-DIALOG-REGRESS** ✅ + **GATE-DIALOG D01–D10** ✅.

---

*При закрытии задачи обновляй этот файл, COMPANION_IMPLEMENTATION_TODOS.md и Cursor TODO.*
