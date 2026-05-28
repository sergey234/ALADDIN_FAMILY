# HERO-3-07 — brief для аниматора (старт)

**Дата:** 2026-05-28 · **PO lock:** genie = **OB_03 headfix**

| Документ | Назначение |
|----------|------------|
| **Этот файл** | 1 страница — что сдать |
| **[PLAN_SUPPLEMENT](./COMPANION_RIVE_ANIMATOR_PLAN_SUPPLEMENT.md)** | **Полный план:** workflow, DoD, motion/mimic, 13 triggers |
| **[6_HATS_AUDIT](./COMPANION_RIVE_ANIMATOR_6_HATS_AUDIT.md)** | Проверка целостности 100% |
| [EXPORT_CHECKLIST](./COMPANION_RIVE_EXPORT_CHECKLIST.md) | Gate + bundle |
| [CANON](./COMPANION_HERO_ART_CANON.md) | Masters PO |

---

## Сдать 3 файла

| Файл | Master | Figma |
|------|--------|-------|
| `unicorn.riv` | v2 cinematic | `01_Unicorn` · `25:2` |
| `aladdin.riv` | OB_01 | `02_Aladdin_Human` |
| `genie.riv` | **OB_03 headfix** | `03_Genie` · `122:2` |

PNG: `docs/assets/unicorn_master_crop_360x480.png` · `aladdin_master_OB01_crop_360x480.png` · `onboarding_OB03_APP_360x480_FILL_headfix_v1.png`

---

## Rive (контракт iOS)

| Параметр | Значение |
|----------|----------|
| Artboard | **360 × 480** |
| Triggers | **13×** `emotion`: `idle` `listening` `thinking` **`speaking`** `happy` `playful` `sad` `comfort` `celebrate` `curious` `nostalgic` `excited` `alert` |
| Number | **`mouth_open`** 0…1 |

Детали motion/mimic по героям → **SUPPLEMENT §4–5**.

---

## Куда и проверка

```
ALADDIN_iOS/Resources/Companion/{unicorn,aladdin,genie}.riv
```

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion
./scripts/verify_companion_rive_ios_bundle.sh
```

**&lt; 500 KB** каждый · iOS-код **не менять**.

---

## Приёмка

| QA | Когда |
|----|--------|
| **11c** | после ваших `.riv` — MIMIC-Q, лицо ≥96 pt |
| **GATE-EMO** | после 11c |

---

*Начать с **[DAY1 пошагово](./COMPANION_RIVE_EDITOR_DAY1_UNICORN.md)** (unicorn.riv).*
