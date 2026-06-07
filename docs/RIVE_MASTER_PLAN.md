# Rive — единый план ALADDIN (PO ✅ 2026-06-04)

> **Handoff для ML:** [COMPANION_ML_RIVE_HANDOFF_MASTER.md](./COMPANION_ML_RIVE_HANDOFF_MASTER.md) — открыть первым.

> **Один art-пайплайн:** только **3 героя** · **3×** `.riv` · **360×480** · [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md)  
> **Wellness Hub** = **HERO-3-07b** (те же файлы, без 4× `wellness_*.riv`) — [WELLNESS_PILLAR_RIVE_PLAN.md](./WELLNESS_PILLAR_RIVE_PLAN.md)

---

## Что делать (только Rive)

| # | Кто | Действие |
|---|-----|----------|
| 1 | Дизайн | ~~**02b**~~ ✅ 36/36 — [live audit 2026-06-04](./COMPANION_FIGMA_AUDIT_LIVE_2026-06-04.md) · [MASTER_ONE_FILE](./COMPANION_ML_MASTER_ONE_FILE.md) |
| 2 | Аниматор | **07** — export `unicorn.riv` · `aladdin.riv` · `genie.riv` → [EXPORT_CHECKLIST](./COMPANION_RIVE_EXPORT_CHECKLIST.md) |
| 3 | Dev | `Resources/Companion/` + `companion_riv_size_gate.py` |
| 4 | iOS | **07b** Wellness Hub — ✅ в коде; ждёт production `.riv` |
| 5 | QA | iPhone: **чат** + **Wellness Hub** (child: 2 карточки, **один** выбранный герой) |

**Не заказывать:** 4× `wellness_*_hero.riv` · artboard 160×160 · `WellnessPillarRiveHost`.

---

## Где что лежит

| Документ | Роль |
|----------|------|
| [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md) | PNG, Figma node ID, шаги 02b → 07 → **07b** |
| [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) | 6 шляп, motion, mimic, 13 states |
| [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md) | Export из Rive.app |
| [WELLNESS_PILLAR_RIVE_PLAN.md](./WELLNESS_PILLAR_RIVE_PLAN.md) | r100-7-07 = 07b, маппинг pillar→emotion |
| [RIVE_TWO_TRACKS_MASTER_PLAN.md](./RIVE_TWO_TRACKS_MASTER_PLAN.md) | Справка «чат vs Hub» (без второго art) |

---

## Wellness на Hub (07b)

- **Файлы:** те же 3 `.riv` в `Resources/Companion/`
- **Герой на карточке:** `companion_selected_character_id` (не отдельный персонаж на дорожку)
- **Дорожка:** заголовок + `color_hex` + `CompanionHeroEmotion` (`thinking` / `happy` / `comfort` / `curious`)
- **Размер на плитке:** 48pt (из 360×480 master)

---

## DoD (закрыть Rive целиком)

- [ ] **HERO-3-07** — 3 production `.riv` (≥25 KB each, &lt;500 KB)
- [ ] Companion чат — Rive на device, lip-sync, GATE-EMO
- [ ] Wellness Hub — выбранный герой на всех видимых pillar-карточках; child 2 карточки — тот же герой
- [ ] **r100-7-07** → completed в [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md)

---

*Единый канон 2026-06-04. Любой старый текст про «4 wellness riv» — deprecated.*
