# Cursor batch — HERO-3-07 Rive (Companion)

> **Открывай в каждой сессии Cursor.** Единый порядок после Figma 02b ✅.  
> **Handoff:** [COMPANION_ML_RIVE_HANDOFF_MASTER.md](./COMPANION_ML_RIVE_HANDOFF_MASTER.md) · **Трекер:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)  
> **Обновлено:** 2026-06-04

---

## Статус батча (живое)

| # | ID | Кто | Статус | DoD |
|---|-----|-----|--------|-----|
| 0 | **BATCH-00** | ML | `[x]` | Этот файл + команды ниже |
| 1 | **07-prep** | ML/Dev | `[x]` | PNG masters OK · `companion_07_prepare_rive_import.sh` exit 0 · gate `--min-kb 25` |
| 2 | **07-unicorn** | Animator | `[x]` | `unicorn.riv` ≥ 25 KB в `Resources/Companion/` (**158 KB**) |
| 3 | **07-aladdin** | ML+Rive | `[~]` | `aladdin.riv` **302 KB** · SM+PNG ✅ · **12 мимик polish** в Rive ⏳ |
| 4 | **07-genie** | ML+Rive | `[~]` | `genie.riv` **229 KB** · SM+PNG ✅ · **12 мимик + дым** polish ⏳ |
| 5 | **07-gate** | ML/Dev | `[x]` | gate + bundle **PASS** 2026-06-04 |
| 6 | **07-build** | ML/Dev | `[x]` | `xcodebuild` **BUILD SUCCEEDED** 2026-06-04 |
| 7 | **08b-chat** | QA/Device | `[ ]` | iPhone: чат Rive + lip-sync · 🦄🧑🧞 · immersive голос |
| 8 | **07b-wellness** | QA/Device | `[ ]` | Wellness Hub 48 pt · child 2 карточки = один герой |
| 9 | **11c** | QA | `[ ]` | MIMIC-Q1…Q6 · 12×3 скриншоты — [11 QA](./COMPANION_HERO3_11_QA_CHECKLIST.md) |
| 10 | **GATE-EMO** | PO | `[ ]` | Sign-off визуала героя в чате |
| 11 | **tracker-x** | PO/ML | `[ ]` | `[x]` HERO-3-07 · 11c · GATE-EMO в PROGRESS_TRACKER |

**Путь:** **A — Rive-аниматор** ([PATH_A](./COMPANION_HERO_07_PATH_A_RIVE_ANIMATOR.md)) · Cadet export  
**Критический путь:** `07-aladdin` + `07-genie` → `07-gate` → `07-build` → `08b` + `07b` → `11c` → `GATE-EMO`.

---

## Команды (копировать в терминал)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Шаг 1 — подготовка
./scripts/companion_07_prepare_rive_import.sh

# Шаг 2 — Rive Editor (аниматор)
./scripts/companion_07_open_in_rive.sh aladdin   # затем genie
# Export → Resources/Companion/*.riv

# Шаг 3 — после каждого export
ls -la Resources/Companion/*.riv
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion --min-kb 25
./scripts/verify_companion_rive_ios_bundle.sh

# Шаг 4 — сборка
xcodebuild -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16' build
```

**Rive import PNG:**

| Герой | Export | PNG |
|-------|--------|-----|
| unicorn | `unicorn.riv` | `docs/assets/unicorn_master_crop_360x480.png` ✅ |
| aladdin | `aladdin.riv` | `docs/assets/aladdin_master_OB01_crop_360x480.png` |
| genie | `genie.riv` | `docs/assets/onboarding_OB03_APP_360x480_FILL_headfix_v1.png` |

**Чеклисты:** [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md) · [5_STEPS](./COMPANION_RIVE_EDITOR_5_STEPS.md)

---

## Не делать в этом батче

- 4× `wellness_*_hero.riv`
- Менять artboard Figma / AIL fractions (96 pt Hub · 48 pt Wellness)
- `[x]` в трекере без device proof

---

## Журнал сессий

| Дата | Шаг | Результат |
|------|-----|-----------|
| 2026-06-04 | BATCH-00 | Создан batch-файл |
| 2026-06-04 | 07-prep | PNG ×3 OK · bundle verify OK · gate `--min-kb 25` → FAIL aladdin/genie (ожидаемо) |
| 2026-06-04 | 07-aladdin | → Rive Editor (`companion_07_open_in_rive.sh aladdin`) |
| 2026-06-04 | MCP | **rive.app Cadet ✅** · RiveMCP в Cursor — Reload Window → Connected |
| 2026-06-04 | 07 ML | `patch_riv_hero_image.py` → aladdin **302KB** genie **229KB** · gate PASS · Rive.app opened |

---

*Следующая сессия: отметь строку в «Журнал» и обнови `[ ]`/`[x]` в таблице статуса.*
