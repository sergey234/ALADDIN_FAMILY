# BRIEF для другой ML: все оставшиеся задачи

**Дата:** 2026-07-20 (rev: R1 gates + metrics + deps; **весь P2 scope оставляем**)  
**Канон iOS:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Планы:**  
- Unicorn: `docs/HANDOFF_HYBRID_RARE_APPS_UNICORN_20260720.md`  
- Wellness: `docs/HANDOFF_WELLNESS_GUIDE_HYBRID_20260720.md`  

**Сборка:** `xcodebuild` **только** по явной команде пользователя в конце.  
**Валюта:** только Unicorn (`UnicornCareReward`).  
**Навигация:** `goBackToPreviousScreen` / `returnTo` — не форсить `.main`.  
**i18n:** каждый UI-ключ RU+EN в `LocalizationManager`.

---

## С чего начать

| Трек | Первый тикет | Почему |
|------|--------------|--------|
| **Unicorn** | `p2-10a` или `p2-9d` | R1 Due+medicine ✅; дальше breath или streak (не `p2-9h` до smoke) |
| **Wellness Gaps** | `psych-05` | if-then из close (после 01c/02/09 ✅) |

Треки **параллельны**. `psych-07` (C части/тело) — **не** в релизе A+B.  
**Scope:** `p2-pol`, `p2-10d–e`, `psych-04b`, Moments с фото — **оставляем** (не урезать).

---

## Глобальные правила

1. Читать **As-built** в MD перед кодом — не переписывать sheets/role с нуля.  
2. Не плодить вторую валюту / второго питомца.  
3. XP только за Done-действия, не за длину чата.  
4. Wellness: mode ≠ pillar switch; оба Guide + PSYCH; Guide побеждает по роли.  
5. Звук дыхания / медали серий — **не** тикеты `psych-*` (другие эпики Unicorn P2).  
6. Не трогать: Qalta, iForget, aicar, Holli, Motra, DAF, Sleep Cycle.  
7. **Anti-scope:** не начинать `p2-9h` (FamilyChallenge), пока `p1-7a–c` + `p1-8a–c` не ✅.  
8. **`psych-05b` зависит от `p2-9h`** — CTA челлендж gated; до челленджей скрывать/не обещать.

---

## R1 gates (выгодно — добавить в работу)

### `r1-smoke` — Smoke-чеклист (~5 мин на устройстве, до финального xcodebuild)

| # | Проверка | Pass |
|---|----------|------|
| 1 | Due-ping → Done → Unicorn XP (идемпотентно) | ☐ |
| 2 | Medicine preset: enable → push → Done → XP; ping стоп | ☐ |
| 3 | Guide: «кто ты?» → проводник самопомощи (не терапевт) | ☐ |
| 4 | Mode `presence` / L1 nudge → опора, без deep | ☐ |
| 5 | Nav Back / returnTo не форсит Main | ☐ |

### `r1-metrics` — метрики успеха эпика (хотя бы вручную / лог)

| Метрика | Зачем |
|---------|--------|
| % Done после ping (из отправленных due-ping) | пинг полезен, не бесит |
| Число семей с medicine enabled | R1 окупается |
| Число session closes (Wellness B) | ритуал живой |
| (опц.) число guide mode switches | режимы используются |

Зафиксировать в конце R1 в заметке / analytics event stubs — иначе P2 без сигнала.

---

## UNICORN — оставшееся

### P1.7 Due-ping (NEXT)

| Id | Что | Как | DoD | Не делать |
|----|-----|-----|-----|-----------|
| **p1-7a** | Поля `ping_until_done`, interval 15–30, `max N/day`. Water default **OFF** | Расширить модель + BE `family_habit_reminders_store` normalize | save/load; water ping=false | Пинг ON на всю воду/детей |
| **p1-7b** | Scheduler повторяет пуши до Done/cap; flag `due_ping` | Хуки в `FamilyHabitRemindersScheduler`; clear на Done (p0-1) | repeats stop; flag работает | Бесконечные пуши |
| **p1-7c** | UI toggle + warning детям; `family_habit_ping_*` RU+EN | Accordion habits | родитель включает за ~30с | Спрятать настройки |

### P1.8 Лекарство (после 1.7)

| Id | Что | Как | DoD | Не делать |
|----|-----|-----|-----|-----------|
| **p1-8a** | Preset `medicine`: 09:00, ping ON, interval 20, max 6 | iOS enum + BE `_VALID_PRESETS` | save/load | Аптека / много препаратов |
| **p1-8b** | UI строка + disclaimer «не врач» | Accordion как water | enable ~30с | Дозы/рецепты |
| **p1-8c** | 1 слот + Due; пуш 💊; Done→XP | Category как habits | push→Done→XP | Медclaims |

### P2.8 Focus

| Id | Что | Как | DoD |
|----|-----|-----|-----|
| **p2-8a** | Focus 25/60 + flag `focus_session` | Parental/Games UI | flag gates |
| **p2-8b** | Успех→XP; срыв без штрафа | `focusSuccess` grant | abort ≠ penalty |
| **p2-8c** | Back + `focus_session_*` RU+EN | nav contract | EN OK |

### P2.9 Moments + медали + челленджи

| Id | Что | Как | DoD |
|----|-----|-----|-----|
| **p2-9a** | Moments API text/photo/date/childId | BE+iOS CRUD | list на child |
| **p2-9b** | UI child card; голос→момент | Family + day-recap hook | manual+voice |
| **p2-9c** | Не соцлента; `family_moments_*` | private family | EN+Back |
| **p2-9d** | `HabitStreakStore` + Done hook; вехи 3/7/14/30 | local stamps | streak растёт |
| **p2-9e** | Веха→Moment 🏅 + `streakMedal` | once per milestone | 7д=1 Moment |
| **p2-9f** | Чекбоксы источников; default water+medicine | parent settings | выбор родителя |
| **p2-9g** | Done→streak multi-source если ON | hooks | каждый source своя серия |
| **p2-9h** | `FamilyChallenge` BE; **max 5** | normalize | CRUD+лимит |
| **p2-9i** | UI аккордеон свои челленджи | glass accordion | Done сегодня |
| **p2-9j** | Challenge Done→XP+streak+медали | `challenge:<id>` | 7д=Moment |
| **p2-9k** | `family_challenge_*` + smoke | i18n+nav | EN+стек |

**Gate:** `p2-9h`+ **не начинать**, пока `p1-7*` и `p1-8*` не ✅ (`anti-scope-p2-9h`).  
Moments с фото (`p2-9a`) — **в scope**, не урезать.

### P2.10 Дыхание + звук

| Id | Что | Как | DoD |
|----|-----|-----|-----|
| **p2-10a** | Дыхание 2 мин (без звука ok) | WellnessExercise preset | сессия завершается |
| **p2-10b** | Companion→exercise returnTo; complete→XP | `navigateToWellnessScreen` | Back OK |
| **p2-10c** | Без медclaims; `wellness_breath_2min_*` | i18n | EN |
| **p2-10d** | Soft audio loops ambient | **exercise track**, не psych-* | play/stop |
| **p2-10e** | Настройки звука persist | UserDefaults | relaunch OK |

### Прочее

| Id | Что |
|----|-----|
| **p2-pol** | Planwoo-lite: только чипы/слоты habits — **не** календарь |
| **inf-deeplink** | Единый router: habit/medicine/recap/check-in/focus |
| **inf-flags** | `due_ping` + `focus_session` (default OFF для риска) |

---

## WELLNESS GUIDE — Gaps (остаток)

Порядок: `psych-00` → **`01c`** → `02` → `09` → `05` → `05b` → опц. `04b`.  
**Не стартовать с нуля:** 01, 01b, 03, 04 UI, 06, 08 (уже ✅).

| Id | Статус | Что | Как | DoD | Не делать |
|----|--------|-----|-----|-----|-----------|
| **psych-00** | ⚠️ | Контракт PR: mode≠pillar + merge Guide↔PSYCH | Чеклист в PR / MD §0–3 | PR = MD | Viral therapist prompt |
| **psych-01c** | ✅ | Merge: Guide identity > PSYCH; presence бьёт deepen | `merge_guide_over_psych` + router + tests | Guide побеждает | Удалить PSYCH |
| **psych-02** | ⚠️ | SSOT Swift↔JSON ids; mode **не** меняет pillar | Unit ids; audit selectMode | ids match; no pillar switch | Deep→Jung auto |
| **psych-09** | ❌ | Reset default на **новую** сессию | `structured_view` / child `presence` | не sticky deep | Вчерашний blind_spots |
| **psych-05** | ⚠️ | if-then из close надёжно; XP только Done | ключи draft из close sheet | no chat XP | XP за сообщения |
| **psych-05b** | ⚠️ | CTA челлендж **gated** | **Depends on `p2-9h`**; скрыть если challenges нет | optional | Обязать челлендж; не делать до P1.7+1.8 |
| **psych-04b** | ❌ опц. | Soft nudge ~12 мин (**оставляем в плане**) | баннер→close; чат жив | нет hard cutoff | Обрыв чата |
| **psych-07** | ❌ P2 | C части/тело | flag OFF + review | позже | В релизе A+B |

---

## Уже сделано (не трогать без нужды)

Unicorn: `00`…`p1-6*`, `qa-hats`.  
Wellness: `psych-01`, `01b`, `03`, `04` UI, `06`, `08`.

---

## Definition of Done для агента на тикет

1. Код в канон-корне + pbxproj если новый `.swift`.  
2. RU+EN ключи.  
3. Nav/Back контракт.  
4. Не ломать Unicorn XP идемпотентность.  
5. Не запускать xcodebuild без команды пользователя.

**Конец brief.**
