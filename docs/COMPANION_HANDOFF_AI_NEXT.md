# Companion — handoff для следующей AI / аниматора / PO

**Обновлено:** 2026-05-28 (Node + RiveMCP + handoff ML)  
**Главный трекер:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) — **66 / 102** · **36 открыто**  
**ML handoff:** [COMPANION_ML_HANDOFF_2026-05-28.md](./COMPANION_ML_HANDOFF_2026-05-28.md) · **Завтра:** [PLAN_2026-05-29](./COMPANION_PLAN_TOMORROW_2026-05-29.md)  
**Rive / Node / MCP:** [COMPANION_RIVE_CONNECT_NODE_MCP.md](./COMPANION_RIVE_CONNECT_NODE_MCP.md)

---

## 1. С чего начать (5 минут)

1. Открыть **[COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)** — галочки `[x]` / `[ ]`.
2. Открыть **[COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md)** — что можно / нельзя для art.
3. Figma Companion: `vwKcGPUUEZjgayEHNn0BJM` — [Companion-Heroes](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes).
4. Onboarding (read-only): `KvkUdyb5Ll31Z9FSzCbpNl` — **не менять** без явного PO.
5. Критический путь: **PO lock master → 07 Rive → 11c → GATE-EMO**.

---

## 2. Что сделано в сессии 2026-05-27 (Figma + уточнения)

### Джин (`03_Genie`)

| Что | Статус |
|-----|--------|
| Ряд **OB_02–06** 360×480 FILL + headfix v1 | ✅ `PO_MASTER_OB02_06_360x480` · node `101:2` |
| Сетка **12× `genie/emotion/*`** с **OB_03 headfix** | ✅ `GRID_12_genie_emotions_OB03` · node `122:2` |
| PO lock master джина | ✅ **OB_03 headfix** в [CANON](./COMPANION_HERO_ART_CANON.md) 2026-05-28 |
| Старые сравнения «Джин 1/2/3», дубли | ❌ удалены по запросу (не восстанавливать без PO) |
| Онбординг в iOS (393×852) | **не трогали** |

**Ассеты (репо):** `docs/assets/onboarding_OB0{2..6}_APP_360x480_FILL_headfix_v1.png`, `onboarding_OB03_APP_360x480_FILL_headfix_v1.png`

### Единорог (`01_Unicorn`)

| Что | Статус |
|-----|--------|
| **12× emotion** = `unicorn/CONCEPT_PO_v2_Cinematic` (сиреневый 3D) | ✅ hash `91b43948…` во всех `18:2`…`18:72` |
| Старые **CONCEPT_v1, A–E** (круги/овалы) | ✅ **удалены** |
| Master reference | ✅ `25:2` `unicorn/CONCEPT_PO_v2_Cinematic` |

### Алладин (`02_Aladdin_Human`)

| Что | Статус |
|-----|--------|
| 12 frames | ✅ по канону **только OB_01** (`docs/assets/aladdin_master_OB01_crop_360x480.png`) — без изменений в этой сессии |

### Важно для Figma API

- **`imageTransform` не работает в FILL/FIT** — только **CROP** или **готовый PNG 360×480** (как headfix v1).
- Перед `use_figma` на нодах: `await figma.setCurrentPageAsync(page)`.

---

## 3. Как устроен продукт (простыми словами)

| Слой | Что |
|------|-----|
| **Онбординг** | 7 экранов 393×852, `OnboardingHero_*` в Xcode — **отдельно** от Companion |
| **Companion Figma** | 36 фреймов 360×480 — **макеты**; v1.1 = **один PNG × 12 имён** на героя |
| **Приложение** | Один **`.riv` на героя**; эмоции = `emotion` trigger + `mouth_open` 0…1 |
| **3 героя** | `unicorn`, `aladdin`, `genie` — **разные персонажи**, не один |

Код: `UI/Companion/CompanionHeroRiveHost.swift`, `CompanionHeroLayout.swift` (360×480).

---

## 4. Следующие задачи (порядок)

| # | ID | Кто | Действие |
|---|-----|-----|----------|
| 1 | ~~**PO**~~ | — | ✅ genie master = **OB_03 headfix** в CANON |
| 2 | **HERO-3-07** | Аниматор | Rive Editor 360×480 → `unicorn.riv`, `aladdin.riv`, `genie.riv` → [ANIMATOR_BRIEF](./COMPANION_RIVE_ANIMATOR_BRIEF.md) · [EXPORT](./COMPANION_RIVE_EXPORT_CHECKLIST.md) |
| 3 | **HERO-3-11b** | QA + iPhone | Device QA build **210+** (параллельно с 07) — [COMPANION_HERO3_11_QA_CHECKLIST.md](./COMPANION_HERO3_11_QA_CHECKLIST.md) |
| 4 | **HERO-3-11c** | QA | MIMIC-Q после **production** `.riv` |
| 5 | **GATE-P0 / GATE-EMO** | PO | После 11b + 07 |

**Команды после `.riv`:**

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion
./scripts/verify_companion_rive_ios_bundle.sh
```

---

## 5. Сколько осталось из 102 задач

**Источник:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)

| | Готово | Всего |
|---|--------|-------|
| **Всего** | **66** | **102** |
| **Осталось** | | **36** |

### Открытые блоки (37 задач)

| Блок | Открыто | Ключевые ID |
|------|---------|-------------|
| **HERO-3** (критический хвост) | 2 (+ подзадачи) | **07** production `.riv` ×3 · **11** QA (**11b** device, **11c** после 07) |
| **P1+ Production** | 12 | P1-12 … P1-23 |
| **P2** | 16 | P2-01 … P2-17 (кроме P2-11 ✅) |
| **P3** | 6 | P3-01 … P3-06 |
| **Adult** | 3 | A-01 … A-03 |
| **GATE** | 11 | GATE-P0 (ждёт 11b), GATE-EMO, GATE-PROD, … |

### Уже закрыто (не переделывать без причины)

- **P0** 19/19 · **P1** 11/11 · **CX** 6/6 · **OPS** 4/4  
- **HERO-3** ядро: 01–06, 08–10, 12–26, 02b Figma 36 frames, 11a pytest  
- iOS build **210**, **08b** device PASS (placeholder Rive)

---

## 6. Figma — прямые ссылки

| Страница | Node | Назначение |
|----------|------|------------|
| `01_Unicorn` | [18-2](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes?node-id=18-2) | emotion/idle v2 |
| `01_Unicorn` | [25-2](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes?node-id=25-2) | master v2 |
| `03_Genie` | [122-2](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes?node-id=122-2) | 12× OB_03 |
| `03_Genie` | [101-2](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes?node-id=101-2) | OB_02–06 выбор |

---

## 7. Документы (полный список)

| Документ | Зачем |
|----------|--------|
| [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) | **Галочки 102 задач** |
| [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md) | Детали задач |
| [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md) | PO art, node ID онбординга |
| [COMPANION_FIGMA_STATUS.md](./COMPANION_FIGMA_STATUS.md) | Figma аудит |
| [COMPANION_02B_ART_PASS_LOG.md](./COMPANION_02B_ART_PASS_LOG.md) | Почему 12 одинаковых PNG |
| [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md) | Export **07** |
| [COMPANION_RIVE_ANIMATOR_BRIEF.md](./COMPANION_RIVE_ANIMATOR_BRIEF.md) | Brief аниматору (3 masters) |
| [COMPANION_100_PERCENT_PARALLEL.md](./COMPANION_100_PERCENT_PARALLEL.md) | Runbook 100% |
| [COMPANION_ML_HANDOFF_START_HERE.md](./COMPANION_ML_HANDOFF_START_HERE.md) | BE/SSH handoff |
| [COMPANION_ML_HANDOFF_2026-05-28.md](./COMPANION_ML_HANDOFF_2026-05-28.md) | **ML сессия 28.05** |
| [COMPANION_RIVE_CONNECT_NODE_MCP.md](./COMPANION_RIVE_CONNECT_NODE_MCP.md) | Node + RiveMCP + Editor |
| [COMPANION_PLAN_TOMORROW_2026-05-29.md](./COMPANION_PLAN_TOMORROW_2026-05-29.md) | План дня |
| [COMPANION_RIVE_EDITOR_5_STEPS.md](./COMPANION_RIVE_EDITOR_5_STEPS.md) | Export 07 пошагово |
| [COMPANION_HERO3_11_QA_CHECKLIST.md](./COMPANION_HERO3_11_QA_CHECKLIST.md) | Device QA |
| [ONBOARDING_COORDINATES_AND_SYNC.md](./ONBOARDING_COORDINATES_AND_SYNC.md) | 393×852 онбординг |
| [FIGMA_COMPANION.env](./FIGMA_COMPANION.env) | file keys |

---

## 8. Ошибки прошлых сессий (не повторять)

1. **Не удалять** `genie/emotion×12` и ряд OB_02–06 одновременно — PO нужны оба блока.
2. **Не путать** онбординг (393×852) и Companion preview (360×480).
3. **Не использовать** `imageTransform` для сдвига в FILL — делать PNG crop или CROP mode.
4. **Не коммитить** без запроса пользователя.

---

*Следующая модель: начни с §4 порядок задач + обнови галочки в TRACKER после каждого закрытия.*
