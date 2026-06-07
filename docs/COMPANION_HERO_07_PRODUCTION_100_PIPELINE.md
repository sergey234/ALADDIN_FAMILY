# HERO-3-07 — production 100% (3 героя × 12 эмоций)

> **Не MVP.** Полноценный герой = 12 **различимых** лиц + `speaking` + `mouth_open` в Rive.  
> **Handoff:** [COMPANION_ML_RIVE_HANDOFF_MASTER.md](./COMPANION_ML_RIVE_HANDOFF_MASTER.md)

---

## 1. Честный статус Figma (проверено 2026-06-04)

| Версия | Что в Figma | 12 разных лиц? |
|--------|-------------|----------------|
| **02b v1.1** ✅ сейчас | 36 фреймов 360×480, **12 имён** на героя | ❌ **Один master** на все 12 (idle = happy = …) |
| **02b v2** (цель art) | 12 **разных** иллюстраций на героя | ✅ нужно для «12 PNG → Rive» |
| **07 Rive (канон PO)** | Слои `brow` / `eye` / `mouth` + SM §2.3 | ✅ **12 мимик в анимации**, один master PNG |

**Live-проверка:** `aladdin/emotion/idle` и `aladdin/emotion/happy` — **одинаковый SHA256** PNG.

Источник: [COMPANION_02B_ART_PASS_LOG.md](./COMPANION_02B_ART_PASS_LOG.md) · MCP `get_screenshot` 2026-06-04.

**Вывод:** «Автоматически взять 12 лиц из Figma» **сейчас** даст 12 **копий одной** картинки — это **не** production 100%. Сначала **art** (v2 или Rive rig).

---

## 2. Два production-пути (оба = 100%)

### Путь A — **Rive Editor + Cadet** (утверждённый канон §2.3)

| Шаг | Кто | Действие |
|-----|-----|----------|
| A1 | Аниматор | Открыть `unicorn.riv` (эталон SM) → Duplicate → **aladdin** / **genie** |
| A2 | Аниматор | Import master PNG + **слои лица** по [PLAN §2.3](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) |
| A3 | Аниматор | 12 states + **`speaking`** + Number **`mouth_open`** |
| A4 | Аниматор | Motion §2.2 (genie: дым только playful/excited/speaking) |
| A5 | Dev | `companion_riv_size_gate.py --min-kb 25` · device · **11c** · **GATE-EMO** |

**DoD:** MIMIC-Q1…Q6 — лица **различимы** без текста.

### Путь B — **Figma 02b v2 → export PNG → Rive 12 raster states**

| Шаг | Кто | Действие |
|-----|-----|----------|
| B1 | Дизайн | 12 **разных** лиц на героя в Figma (матрица §2.3) |
| B2 | Dev/ML | `python3 scripts/companion_07_export_figma_emotions.py` |
| B3 | Dev/ML | `python3 scripts/companion_07_check_emotion_png_uniqueness.py` → **12 unique** |
| B4 | Аниматор | Rive: 12 PNG → 12 SM states + speaking + mouth_open |
| B5 | Dev | gate · QA · GATE-EMO |

Manifest node IDs: [companion_figma_emotion_manifest.json](./companion_figma_emotion_manifest.json)

---

## 3. Что автоматизировано в репо

| Скрипт | Назначение |
|--------|------------|
| `scripts/companion_07_export_figma_emotions.py` | 36 PNG из Figma API → `Resources/Companion/figma_exports/{hero}/{emotion}.png` |
| `scripts/companion_07_check_emotion_png_uniqueness.py` | SHA256: должно быть **12 unique** / герой |
| `scripts/companion_07_prepare_rive_import.sh` | PNG masters + gate |
| `scripts/companion_07_open_in_rive.sh` | Открыть `.riv` в Rive.app |
| `scripts/companion_riv_size_gate.py` | &lt;500 KB, `--min-kb 25` |

**Не production:** `companion_07_patch_riv_hero_image.py` — одна PNG внутри `.riv` (MVP), **без** 12 мимик.

---

## 4. Rive — да, используем

| Слой | Инструмент |
|------|------------|
| Art / мимика 100% | **Rive.app** + Cadet |
| Файл в iPhone | **`.riv`** + `RiveRuntime` |
| Figma | Референс + (v2) 12 PNG |
| RiveMCP | Опционально; 3/3 free исчерпаны; не заменяет аниматора |

---

## 5. Блокер → разблокировка

```
Сейчас:  Figma v1.1 = 1 лицо × 12 имён
         ↓
Выбор:   A) Rive rig §2.3  ИЛИ  B) Figma v2 art
         ↓
         export 3× .riv → gate → iPhone → GATE-EMO
```

**Токен Figma** (для export скрипта): `docs/FIGMA_COMPANION.env` → `FIGMA_ACCESS_TOKEN=figd_...`

---

## 6. Сессия ML 2026-06-04

- Figma MCP: manifest 36 node IDs, проверка aladdin idle=hapy (дубликат).
- Док + скрипты export/uniqueness.
- **Не** закрыт HERO-3-07: нужен аниматор (путь A) или дизайн v2 (путь B).

---

*Обновлять при закрытии 07 / 02b v2.*
