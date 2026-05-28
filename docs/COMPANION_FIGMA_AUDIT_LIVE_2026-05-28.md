# Figma Companion — live-аудит (Mac / MCP)

**Дата:** 2026-05-28 · **Файл:** `vwKcGPUUEZjgayEHNn0BJM` · [Companion-Heroes](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes)

---

## Итог

| Страница | 12 emotion 360×480 | Master / grid | Вердикт |
|----------|-------------------|---------------|---------|
| **01_Unicorn** | ✅ 12× `unicorn/emotion/*` · IMAGE fill | v2 в кадрах (отдельный `25:2` на canvas нет — эмоции на странице) | ✅ **PASS** |
| **02_Aladdin_Human** | ✅ 12× `aladdin/emotion/*` | OB_01 art | ✅ **PASS** |
| **03_Genie** | ✅ 12× внутри `GRID_12_genie_emotions_OB03` (`122:2`) | PO row `101:2` OB_02–06 | ✅ **PASS** |
| **00_Spec** | — | Motion / Mimic / Sign-off | ✅ (4 страницы в файле) |

**36 / 36 макетов** — подтверждено live API.

---

## Детали API

### Страницы

| id | name |
|----|------|
| `0:1` | `00_Spec` |
| `4:2` | `01_Unicorn` |
| `5:2` | `02_Aladdin_Human` |
| `6:2` | `03_Genie` |

### 01_Unicorn

- 12 фреймов: `idle` … `alert` (без отдельного `speaking` — верно для Figma).
- Размер: **360 × 480** · fill: **IMAGE**.
- Deprecated `CONCEPT_v1/A–E`: **не найдены**.
- Top-level: `HEADER_ref_OB05`, `GRID_12_emotions`, `NOTE_unicorn_cleanup`.

### 02_Aladdin_Human

- 12 фреймов `aladdin/emotion/*` · **360 × 480**.

### 03_Genie

- Сетка: `GRID_12_genie_emotions_OB03` · `122:2` · 12 дочерних `genie/emotion/*` · **360 × 480** · IMAGE.
- Сравнение PO: `PO_MASTER_OB02_06_360x480` · `101:2`.

---

## Следующий шаг (после Figma ✅)

**HERO-3-07** — Rive Editor на Mac:

1. Импорт PNG из `docs/assets/` (см. [ANIMATOR_BRIEF](./COMPANION_RIVE_ANIMATOR_BRIEF.md)).
2. Export 3× `.riv` → `Resources/Companion/`.
3. `python3 scripts/companion_riv_size_gate.py --dir Resources/Companion`.

Подготовка путей: `scripts/companion_07_prepare_rive_import.sh`

---

*Онбординг `KvkUdyb5Ll31Z9FSzCbpNl` не проверялся (read-only).*
