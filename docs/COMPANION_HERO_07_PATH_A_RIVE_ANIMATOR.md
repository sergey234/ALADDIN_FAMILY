# HERO-3-07 — Путь A: Rive-аниматор (production 100%)

> **Выбрано:** 2026-06-04 · **Не MVP** — 12 различимых мимик + `speaking` + `mouth_open` на героя.  
> **Cadet rive.app** — unlimited export. **Figma v1.1** = референс имён; лица делаем **в Rive** §2.3.

**Связано:** [COMPANION_RIVE_EDITOR_5_STEPS.md](./COMPANION_RIVE_EDITOR_5_STEPS.md) · [PLAN §2.2–2.3](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) · [EXPORT_CHECKLIST](./COMPANION_RIVE_EXPORT_CHECKLIST.md) · [batch](./COMPANION_RIVE_HERO307_CURSOR_BATCH.md)

---

## За 1 минуту

| Герой | Статус `.riv` | Действие |
|-------|---------------|----------|
| **unicorn** | ✅ ~158 KB production | Эталон SM — **не ломать** |
| **aladdin** | ⏳ ~15 KB placeholder | Duplicate unicorn → art OB_01 → export |
| **genie** | ⏳ ~15 KB placeholder | Duplicate unicorn → art OB_03 → export |

**iOS ждёт:** 13 triggers (имена ниже) + Number `mouth_open` 0…1 · artboard **360×480**.

---

## Шаг 0 — Терминал (2 мин)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/companion_07_sync_master_png_to_bundle.sh
./scripts/companion_07_prepare_rive_import.sh
```

---

## Шаг 1 — Единорог (проверка эталона)

Файл: `Resources/Companion/unicorn.riv`

- [ ] Artboard **360×480**
- [ ] State Machine **HeroSM** (или как в файле — **не переименовывать** без правки iOS)
- [ ] **13 Trigger inputs** (точные имена):

```
idle listening thinking speaking happy playful sad comfort
celebrate curious nostalgic excited alert
```

- [ ] **Number** input: `mouth_open` (0…1)
- [ ] Preview: `idle` → `listening` → `thinking` → `speaking` (двигать `mouth_open`) → `happy` → `sad`
- [ ] Лицо в **верхних ~45–60%** кадра

Если всё OK — единорог = **шаблон** для копирования.

---

## Шаг 2 — Аладдин (основная работа)

### 2.1 Открыть

```bash
./scripts/companion_07_open_in_rive.sh unicorn
# File → Duplicate → сохранить проект как ALADDIN_aladdin_companion
# или открыть: Resources/Companion/aladdin_work_in_progress.riv (копия SM)
```

**PNG:** `docs/assets/aladdin_master_OB01_crop_360x480.png`

### 2.2 Art

- [ ] Заменить персонажа на **Аладдина** (OB_01), **не** единорога
- [ ] Лицо вверху кадра (AIL immersive = crop снизу)
- [ ] Слои (минимум): `brow_L/R`, `eye_L/R`, `mouth`, `head`, `body` — см. [§2.3](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md)

### 2.3 Мимика — 12 states (отличимы без текста)

| Trigger | Рот (код) | Аладдин — акцент |
|---------|-----------|------------------|
| idle | M0 | спокойный наставник |
| listening | M1 | лёгкий кивок |
| thinking | M7 | взгляд вверх |
| **speaking** | **M4** + `mouth_open` | спокойный рот |
| happy | M2 | тёплая улыбка |
| playful | M3 | **без** прыжка |
| sad | M6 | **без** «веселья» |
| comfort | M1 | тепло |
| celebrate | M3 | сдержанно |
| curious | M5 | |
| nostalgic | M1 | |
| excited | M3 | |
| alert | M0 | серьёзный взгляд |

**Запрещено:** дым джина, звёзды на sad, сарказм в позе.

### 2.4 Export

- [ ] **File → Export → `.riv`**
- [ ] Путь: `Resources/Companion/aladdin.riv` (заменить ~15 KB)
- [ ] Размер: **≥ 25 KB**, **< 500 KB**

### 2.5 Gate (терминал или чат «aladdin готов»)

```bash
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion --min-kb 25
./scripts/verify_companion_rive_ios_bundle.sh
```

---

## Шаг 3 — Джин (после Аладдина)

```bash
cp Resources/Companion/unicorn.riv Resources/Companion/genie_work_in_progress.riv
./scripts/companion_07_open_in_rive.sh genie
open docs/assets/onboarding_OB03_APP_360x480_FILL_headfix_v1.png
```

**PNG master:** OB_03 headfix (канон PO).

| Правило | Джин |
|---------|------|
| Дым / искры | **только** `playful`, `excited`, `speaking` |
| sad / comfort | **без** дыма |
| Лицо | OB_03, верх кадра |

- [ ] 12 states + `speaking` + `mouth_open`
- [ ] Export → `Resources/Companion/genie.riv`
- [ ] Gate (как §2.5)

---

## Шаг 4 — iPhone (вы)

| Место | Проверка |
|-------|----------|
| Мир героев → Главное | 🦄 🧑 🧞 — **Rive**, не статичный PNG |
| Голос / TTS | `mouth_open`, immersive — глаза не обрезаны |
| Wellness Hub | 48 pt, **один** выбранный герой на карточках |

---

## Шаг 5 — QA + sign-off

- [ ] [COMPANION_HERO3_11_QA_CHECKLIST.md](./COMPANION_HERO3_11_QA_CHECKLIST.md) — **11c** MIMIC-Q1…Q6
- [ ] **GATE-EMO** — PO
- [ ] [x] **HERO-3-07**, **11c**, **GATE-EMO** в [TRACKER](./COMPANION_PROGRESS_TRACKER.md)

---

## Частые ошибки

| Ошибка | Последствие |
|--------|-------------|
| `Happy` вместо `happy` | iOS не переключит эмоцию |
| Нет `speaking` | TTS без «говорящего» лица |
| Нет `mouth_open` | рот не синхронизируется |
| Export в wrong path | бандл старый placeholder |
| Сохранить unicorn art в aladdin.riv | в Hub 🧑 будет единорог |

---

## Что делает ML после «aladdin готов» / «genie готов»

- `companion_riv_size_gate.py --min-kb 25`
- `verify_companion_rive_ios_bundle.sh`
- `xcodebuild` (по запросу)
- Обновление [COMPANION_RIVE_HERO307_CURSOR_BATCH.md](./COMPANION_RIVE_HERO307_CURSOR_BATCH.md)

---

*Путь B (12 PNG из Figma) — отложен до 02b v2. См. [COMPANION_HERO_07_PRODUCTION_100_PIPELINE.md](./COMPANION_HERO_07_PRODUCTION_100_PIPELINE.md).*
