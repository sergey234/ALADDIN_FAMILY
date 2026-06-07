# Figma Companion — live-аудит HERO-3-02b (100%)

**Дата:** 2026-06-04 · **MCP:** `user-figma` · **Аккаунт:** Sergey21 · `sergey21.02.84@gmail.com` · team `1634136191275652287`  
**Файл:** [Companion-Heroes](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes) · key `vwKcGPUUEZjgayEHNn0BJM`

---

## Итог: ✅ **HERO-3-02b PASS — 36 / 36**

| Страница | node | Production frames 360×480 | 12 эмоций | Вердикт |
|----------|------|---------------------------|-----------|---------|
| **01_Unicorn** | `4:2` | 12× `unicorn/emotion/*` | ✅ все | ✅ **PASS** |
| **02_Aladdin_Human** | `5:2` | 12× `aladdin/emotion/*` | ✅ все | ✅ **PASS** |
| **03_Genie** | `6:2` | 12× в `GRID_12_genie_emotions_OB03` (`122:2`) | ✅ все | ✅ **PASS** |
| **00_Spec** | `0:1` | spec + `02_DONE_36_frames` ✅ | — | ✅ |

**Нет** отдельного `speaking` в Figma (верно — только Rive/Motion).

---

## 01_Unicorn (`4:2`)

| Frame | size |
|-------|------|
| `unicorn/emotion/idle` … `alert` (12) | **360 × 480** each |

- `NOTE_unicorn_cleanup`: master v2, CONCEPT круги удалены  
- Master на `00_Spec`: `unicorn/CONCEPT_PO_v2_Cinematic` (`25:2`) 360×480  

---

## 02_Aladdin_Human (`5:2`)

| Frame | size |
|-------|------|
| `aladdin/emotion/idle` … `alert` (12) | **360 × 480** each |

- Header: ref **OB_01** only ✅  

---

## 03_Genie (`6:2`)

| Frame | size |
|-------|------|
| `genie/emotion/idle` … `alert` (12) в `GRID_12_genie_emotions_OB03` | **360 × 480** each |

- PO row: `PO_MASTER_OB02_06_360x480` (`101:2`) — сравнение, не export  
- Production: **OB_03 headfix** (banner в grid)  

---

## 00_Spec (`0:1`)

- `02_DONE_36_frames`: «✅ HERO-3-02b — 36 frames созданы»  
- `Sign-off_HERO-3-17`, Motion, Mimic, `RIVE_EXPORT_HERO-3-07` — на месте  

---

## PO gate 02b → 07

| Критерий | Статус |
|----------|--------|
| 36/36 frames | ✅ |
| 360×480 | ✅ |
| 3 masters (unicorn v2, aladdin OB_01, genie OB_03) | ✅ |
| v1.1: 12 имён / мимика в Rive 07 | ✅ по плану |

**Следующий шаг:** **HERO-3-07** — export `unicorn.riv` · `aladdin.riv` · `genie.riv` → `Resources/Companion/`

---

*Live MCP `get_metadata` 2026-06-04. См. [COMPANION_FIGMA_STATUS.md](./COMPANION_FIGMA_STATUS.md) · [RIVE_MASTER_PLAN.md](./RIVE_MASTER_PLAN.md).*
