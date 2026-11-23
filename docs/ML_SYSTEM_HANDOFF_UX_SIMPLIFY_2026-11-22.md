# HANDOFF · UX «Проще и понятнее» → другой ML-агент (2026-11-22)

**Назначение:** один файл, чтобы новая ML-система **с нуля** поняла роль, SSOT, порядок работ, GO и куда смотреть.  
**Статус кода:** правки приложения **ещё не начаты**. Ждать фразы владельца.

---

## 0. Скопируй в начало сессии (промпт)

```
ROLE: Independent principal iOS UX expert (15+ yrs) + Mech Pilot executor for ALADDIN.
OWNER speaks Russian; answer plain Russian, short.

SSOT (only source of truth for work):
  docs/UX_SIMPLIFY_PLAN_2026-11-21.md
Read also (satellites, already merged into plan — do NOT wait for «согласовано»):
  docs/UX_WHERE_WE_PUT_EVERYTHING_2026-11-22.md
  docs/UX_EXPERT_ROLE_PROMPT_2026-11-22.md
  docs/UX_EXPERT_AUDIT_DRAFT_2026-11-22.md
  docs/UX_ADA_FINALISTS_VS_ALADDIN_2026-11-22.md
  docs/ML_SYSTEM_START_HERE.md  (pointer row «Проще и понятнее»)
  docs/UX_SIMPLIFY_BASELINE_RESTORE_POINTER.txt  (backup before edits)
Skill: .cursor/skills/aladdin-ux-clarity-expert/SKILL.md

WORKING ROOT (mandatory):
  /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
  git branch must be master for iOS commits.
  Before edits: git rev-parse --show-toplevel · branch · status --short

LOCKED DECISIONS (do not reopen without owner GO):
  D1–D22, D24–D26 as in plan §2
  D23 = Storm stays the default background. Do NOT paint screens white. Light only if the user toggles it · §8.6
  D27 = Antifake tab chips = WhereIsPhone gold chip pattern · §8.7
  Q6 = keep emoji in family push
  Q9 = Figma rule GO before stage 4 Onboarding_V2
  D9 = keep title «Aladdin start!»
  D2 = trial auto — do not touch
  D21 = ALADDIN does not sell VPN product
  D22 = keep Free/Personal location history at 24h as in code. Do NOT write or code 36h
  D10 dashes = CANCELLED. Do not edit em-dashes in LocalizationManager or .strings

ORDER (strict):
  1 texts → 2 profile+tariffs → 2.5 theme/contrast tokens → 3 style waves (+D27) → 4 onboarding LAST → 5 QA
  One ux-* task = one small diff. merge:true only on Cursor todos. Never delete ux-* ids.
  After EVERY LocalizationManager touch: ./scripts/verify_localization_manager_integrity.sh → OK
  No Path.write_text / full rewrite of LocalizationManager.swift (mega-file rule).

GO GATES (never skip):
  «GO на этап 1» before any copy edits
  «GO на этап 2» / «GO на этап 2.5» / next stage after each report
  «GO на дизайн тумблера» before theme toggle UI
  «GO на правку правила Figma» before stage 4 Figma work (Q9)
  «GO на сборку» before xcodebuild / Simulator / device
  Never push tag/branch without owner «GO на push»
  Do not change location hours and do not start the dash-cleanup task

BACKUP (already done — do not recreate unless owner asks):
  tag ux-simplify-baseline-2026-11-22 (local)
  safe ~/ALADDIN_VPN_SAFE/ux_simplify_pre_20261122_221602/
  Do NOT touch Oct29 pay-pains or Nov10 hub-map95 safes.

MISSION:
  Calm family-safety app. Readable contrast ≥4.5:1 in BOTH themes.
  Storm = brand default. Do not replace it with a white background.
  Light = optional toggle only.
  Copy: one language, glossary §4, no jargon, no raw keys on live screens.
  Do not rewrite em-dashes. Location history stays 24h.
  Adult UI: no XP/%/unicorns. Kids (D15) can stay brighter.
  Onboarding: keep existing hero PNGs; 6 screens; scrim; 1 haptic; genie ≠ game (D25).
  Antifake chips look like Where «Pets» gold chips (D27).

PER TASK:
  1) Open plan section for that stage
  2) List GATES (done criteria) in chat before coding
  3) Minimal diff; evidence (audit/verify/lints)
  4) Short owner report; wait GO for next

DO NOT: invent features; mass regex fonts; commit bot/telegram_stars_shop_bot; paste secrets; claim «готово» without evidence.
```

---

## 1. Роль и обязанности

| Роль | Кто | Обязанности |
|---|---|---|
| **Пилот** | Владелец | Цель, границы, GO на этапы/сборку/сервер/Figma/тумблер |
| **Меха / UX-эксперт** | Агент | Читать SSOT; 3 варианта A/B/C; минимальный diff; evidence; не хвалить себя |
| **Не делать** | Агент | Сборка без GO; rewrite LocManager; VPN как продукт; mock parental; auto-merge |

Полный текст роли: `docs/UX_EXPERT_ROLE_PROMPT_2026-11-22.md`.

---

## 2. Карта документов (все смежные)

| Файл | Зачем |
|---|---|
| **`UX_SIMPLIFY_PLAN_2026-11-21.md`** | **SSOT** — решения D*, этапы 1–5, тексты A/B/C, TODO `ux-*` |
| `UX_WHERE_WE_PUT_EVERYTHING_2026-11-22.md` | Простая карта «что → куда» для человека |
| `UX_EXPERT_ROLE_PROMPT_2026-11-22.md` | Роль 15+ + copy-paste промпт |
| `UX_EXPERT_AUDIT_DRAFT_2026-11-22.md` | Детали ляпов (влито; не ждать «согласовано») |
| `UX_ADA_FINALISTS_VS_ALADDIN_2026-11-22.md` | Harvee/Opal/Watch Duty / HIG — уроки, не копия тёмного UI |
| `ML_SYSTEM_START_HERE.md` | Роутер репо; строка текущей задачи |
| `UX_SIMPLIFY_BASELINE_RESTORE_POINTER.txt` | Бэкап до правок |
| `UX_COPY_AUDIT_REPORT.md` | Цифры аудита (генерит скрипт) |
| `.cursor/skills/aladdin-ux-clarity-expert/SKILL.md` | Skill агента |
| Rules: `localization-megafile-safe`, `ask-before-ios-build`, `ask-before-important-ops`, `mech-pilot`, `ios-working-root`, `ios-commit-on-master` | Жёсткие запреты |

---

## 3. Порядок этапов (не путать)

```
1 Тексты  →  2 Профиль+Тарифы  →  2.5 Тема/контраст  →  3 Стиль(+D27)  →  4 Онбординг  →  5 QA
```

Внутри этапа: задачи из §12 плана, **по одной**.  
После этапа: §11 checks + отчёт → ждать GO.

---

## 4. Что где в приложении (экраны)

| Зона | Файлы (якоря) | Текст | Фон/тема | Стиль |
|---|---|---|---|---|
| Главная «Aladdin start!» | `SimpleHomeScreen.swift` | D9 не трогать title; P1–P3 двери | Default Шторм; токены | New York волна `ux-s3-home` |
| Семья | `02_FamilyScreen.swift` | словарь, без жаргона | токены | без фиолетового |
| Где семья | `WhereIsPhoneScreen.swift` | + эталон чипов | токены | **эталон D27** `sheetChipStrip` |
| Проверка на обман | `AntifakeHubScreen.swift` | Antifake→«Проверка на обман» | токены | **D27** tabPicker = эталон |
| Тарифы | `10_TariffsScreen.swift` | §7; история **24ч**; без % галереи | токены | D17/D20 |
| Профиль edit | `ProfileEditView.swift` | Почта, одна Готово | без своего градиента | этап 2 |
| Профиль хаб | `11_ProfileScreen.swift` | — | токены | волна 3 |
| Поддержка / 60+ / Devices… | §8.3 | этап 1 строки | токены волнами | этап 3 |
| Онбординг | `14_OnboardingScreen.swift` + Heroes | §9.4 A; 6 экранов | картинки+scrim | этап 4 LAST |
| Детские | D15 | свой словарь 4.2 | ярче ок | не «серые Настройки» |
| Тумблер темы | Профиль/Настройки (после GO дизайна) | «Шторм» / «Светлый» | D23 | этап 2.5 |

Детали чипов Antifake: план **§8.7**.  
Детали темы: план **§8.6**.

---

## 5. Тема и контраст (D23) — шпаргалка

| Режим | Фон | Текст | Когда |
|---|---|---|---|
| **Шторм (DEFAULT)** | `StormMeshBackground` | светлые буквы на тёмном. Белый экран не делаем | первый запуск |
| **Светлый** | `systemBackground` | `label` / тёмный | пользователь включил |

Обе ≥ 4.5:1. Токены сначала (`ux-s25-contrast-tokens`), потом волны.  
Apple: тёмный бренд ок (как Harvee), если контраст ок. Не копировать dark-first Harvee как единственный UI.

---

## 6. Первые команды после GO на этап 1

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
git rev-parse --show-toplevel   # must be …/ALADDIN_iOS
git branch --show-current       # master
git status --short
python3 scripts/audit_ux_copy.py --report docs/UX_COPY_AUDIT_REPORT.md
python3 scripts/localization_lint.py
# Каждая правка текста: до и после, RU и EN, без сырых ключей (§5.0 плана).
# after LocManager:
./scripts/verify_localization_manager_integrity.sh
```

---

## 7. Definition of Done (весь проект)

- [ ] Этап 1: audit targets §11; push семьи с эмодзи (Q6)
- [ ] Этап 2: профиль 1×Готово; тарифы D17/D20; история **24ч как в коде** (36ч не писать)
- [ ] Этап 2.5: токены 2 тем; контраст Шторма; тумблер после GO дизайна; Light волны
- [ ] Этап 3: New York волнами; D27 Antifake=Where chips; без лишнего purple
- [ ] Этап 4: Figma V2 после Q9 GO; 6 экранов; scrim; 1 haptic; тексты A
- [ ] Этап 5: скрины обеих тем; Inspector; friend test «что делает приложение?»
- [ ] Нет «готово» без evidence

---

## 8. Бэкап (не ломать)

| | |
|---|---|
| SHA | `745edb4f9f1d325097aea2998361786251274480` |
| Tag | `ux-simplify-baseline-2026-11-22` (local only) |
| Safe | `~/ALADDIN_VPN_SAFE/ux_simplify_pre_20261122_221602/` |
| Zip | `BACKUP_ALADDIN_CLEAN_20261122_2216.zip` (~799M) |
| Untouched | Oct29 `pay_pains_pre_*` · Nov10 `hub_map95_pre_*` |

---

## 9. Что сказать владельцу в первом сообщении

1. Прочитал SSOT + этот HANDOFF.  
2. Подтверждаю: код не трогаю без «GO на этап 1».  
3. GATES этапа 1 (3–8 пунктов) → жду GO.
