# HERO-3-02b — art-pass log (2026-05-27)

**Статус:** ✅ **36/36** frames · ⚠️ **layout v1.1** (кадрирование) · ⏳ **12× мимика** → **Rive 07** (как Grok)

## Что сейчас в Figma (честно)

| Вопрос | Ответ |
|--------|--------|
| Почему все 12 фреймов **одинаковые**? | **Да, намеренно для v1:** один master на героя × 12 **имён** эмоций. Это **не** финальная мимика. |
| Где 12 **разных** лиц? | **Rive 07** (слои брови/глаза/рот + SM `emotion` + `mouth_open`) — см. [§2.2–2.3](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md). Опционально позже **02b v2**: 12 отдельных PNG на героя. |
| Как в **Grok**? | Grok = **анимация + lip-sync**, не 12 статичных постеров. У нас то же: **2D Rive** + `mouth_open` при TTS + смена `emotion` от BE. |
| Джин не виден / смещение вверх? | **Исправлено 2026-05-27:** вместо полного OB-экрана — crop **360×480** с лицом в safe zone. |

## 12 имён эмоций (все 3 героя)

`idle` · `listening` · `thinking` · `happy` · `playful` · `sad` · `comfort` · `celebrate` · `curious` · `nostalgic` · `excited` · `alert`

> `speaking` — **фаза Motion**, не 13-й постер в сетке 02; в Rive + `mouth_open` 0…1.

## Masters в Figma (после crop)

| Герой | Файл в репо | Figma frames |
|-------|-------------|--------------|
| unicorn | `docs/assets/unicorn_master_crop_360x480.png` | `01_Unicorn` · `unicorn/emotion/*` |
| aladdin | `docs/assets/aladdin_master_OB01_crop_360x480.png` | `02_Aladdin_Human` · `aladdin/emotion/*` |
| genie | `docs/assets/onboarding_OB03_APP_360x480_FILL_headfix_v1.png` | `03_Genie` · `genie/emotion/*` (OB_03 headfix) |

Источники OB: [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md)

## v1 → v1.1 → v2

| Этап | Содержание |
|------|------------|
| **v1** ❌ | Полный PNG onboarding в FILL → голова обрезана, джин «не видно», пустое низом |
| **v1.1** ✅ | Crop 360×480, герой по центру, **один** кадр на все 12 имён |
| **v2** (опц.) | 12 **разных** иллюстраций лица на героя по `00_Spec/Mimic` |
| **07** ✅ цель | Production `.riv` — мимика, позы, `mouth_open`; приёмка **MIMIC-Q1** |

## Следующий шаг

**HERO-3-07** — [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md)
