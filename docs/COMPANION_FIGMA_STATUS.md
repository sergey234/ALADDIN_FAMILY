# Figma Companion — аудит план vs факт

**Файл:** [Companion-Heroes](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes)  
**Ключ:** `vwKcGPUUEZjgayEHNn0BJM`  
**Проверено:** 2026-05-27 · **live MCP:** [COMPANION_FIGMA_AUDIT_LIVE_2026-05-28.md](./COMPANION_FIGMA_AUDIT_LIVE_2026-05-28.md) ✅ **36/36**

---

## Страницы в файле

| Страница | По плану | В Figma сейчас |
|----------|----------|----------------|
| **00_Spec** | ADR, Motion, Mimic, Sign-off, export brief | ✅ **есть** |
| **01_Unicorn** | 12× `unicorn/emotion/*` 360×480 | ✅ **v2 cinematic** · CONCEPT круги удалены · master `25:2` |
| **02_Aladdin_Human** | 12× `aladdin/emotion/*` | ✅ **OB_01** master |
| **03_Genie** | 12× `genie/emotion/*` + PO row | ✅ **OB_03** в 12 frames (`122:2`) · ряд **OB_02–06** (`101:2`) |

**Итого макетов:** **36 / 36** ✅ **art-pass 2026-05-27** — согласованный PNG в каждом frame 360×480 ([CANON](./COMPANION_HERO_ART_CANON.md)).

> **v1 art-pass:** один master на героя × 12 эмоций (лицо/поза в Rive **07**). Отдельные 12 иллюстраций на эмоцию — опционально v2.

> Фрейм `02_DONE_36_frames` на `00_Spec` — **не «готово»**, а напоминание: «⛔ HERO-3-02 ЗАБЛОКИРОВАН — не рисовать 3×12 до sign-off».

---

## Что уже есть в `00_Spec` ✅

| Фрейм | Содержание | Задача |
|-------|------------|--------|
| `ADR_HERO-3-20` | 12 макетов CX.4; speaking только Motion/Rive | HERO-3-20 |
| `Motion_Spec §2.2` | listening → thinking → speaking → content; mouth_open | HERO-3-17 |
| `Mimic_Spec §2.3` | 12 сценариев CX.4, L1–L5, naming | HERO-3-17 |
| `REF_Onboarding_READ_ONLY` | Ссылки OB_01 / OB_02 / OB_05 (плейсхолдеры под скрин) | референсы |
| `Sign-off_HERO-3-17` | Чеклист PO | ✅ подписано 2026-05-26 |
| `RIVE_EXPORT_HERO-3-07` | 360×480, 3 файла, inputs | чеклист export |

---

## Что по плану осталось (Figma → Rive)

### Шаг A — **HERO-3-02b** (Figma art)

1. Создать 3 страницы: `01_Unicorn`, `02_Aladdin_Human`, `03_Genie`.
2. На каждой — **12 фреймов** 360×480 pt (имена: `unicorn/emotion/happy`, …).
3. Стиль: **согласованный art** — [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md) (PO ✅ 27.05); не wireframe-круг.
4. `speaking` — **не** 13-й постер; рот — в Motion/Rive.

### Шаг B — **HERO-3-07** (Rive export)

1. Импорт/перерисовка в **Rive Editor** artboard **360×480**.
2. State Machine: triggers `idle`…`excited` + Number `mouth_open`.
3. Export → `Resources/Companion/{unicorn,aladdin,genie}.riv`.
4. `python3 scripts/companion_riv_size_gate.py`
5. Device → **11c** MIMIC-Q.

**Альтернатива:** рисовать сразу в Rive (минуя 36 PNG), если аниматор не ведёт Figma-страницы — но **12 state × 3 героя** всё равно нужны.

---

## iOS (уже готово под приёмку `.riv`)

| Компонент | Статус |
|-----------|--------|
| Сцена 56% `conversationFullBody` | ✅ |
| `CompanionHeroRiveHost` + `mouth_open` | ✅ |
| Placeholder `.riv` ×3 | ✅ |
| TTS на текст (build 210) | ✅ |
| 08b device | ✅ |

---

## Следующие действия

| # | Кто | Действие |
|---|-----|----------|
| 1 | Дизайн | **02b** — 3 страницы × 12 фреймов в Figma |
| 2 | Аниматор | **07** — Rive export ×3 |
| 3 | QA | **11b** на build 210 (placeholder) |
| 4 | QA | **11c** после production `.riv` |

См. также: [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md) · [COMPANION_100_PERCENT_PARALLEL.md](./COMPANION_100_PERCENT_PARALLEL.md)
