# ASC Wave B — localization SSOT (RU / EN)

**Rule:** App Store EN must not show raw Russian UI. In-app copy always via `Localizable.strings` (never baked CapCut in product UI).

## In-app (Where → Driving → reports)

Live UI: `DrivingReportsModal` — keys `driving_reports_*`, `drive_weekly_*`, `drive_max_speed`, units `driving_reports_unit_km` / `_kmh` / `_min`.

Tip card (ready, wire later GO):

| Key | EN | RU |
|-----|----|----|
| `asc_tip_driving_reports_title` | Family driving reports | Отчёты о поездках семьи |
| `asc_tip_driving_reports_body` | Mileage, max speed… | Пробег, макс. скорость… |
| `drive_total_mileage` | Total mileage | Общий пробег |
| `drive_total_trips` | Total trips | Всего поездок |
| `drive_stat_km_unit` | km | км |
| `drive_stat_kmh_unit` | km/h | км/ч |
| `drive_stat_min_unit` | min | мин |

## ASC in-phone status

| Pack | External headline | In-phone UI | Status |
|------|-------------------|-------------|--------|
| **H01** | Our RU+EN ✅ | Bubble **EN patched** «Mom is home» | ✅ |
| **H03 / H21** | Our RU+EN ✅ | CapCut EN 2026-11-12 evening → fitted 1290×2796 | ✅ EN replaced |
| H22–H24 | Our RU+EN ✅ | Faces/path; H24 bubble empty | OK |
| **H25–H26** | Our RU+EN ✅ | **EN patched** `12 km · 24 min` | ✅ |
| **H27–H28** | RU baked · EN our overlay ✅ | **EN patched** stats + units | ✅ |
| **Draft A–D EN** | fitted extras | Lock / WHO / Stats / TwoPhones | `ALADDIN_ASC_Draft*` · see `07_FITTED` |

## H27 EN in-phone (patched)

| RU | EN |
|----|----|
| 376 км | 376 km |
| Общий пробег | Total mileage |
| 122 км/ч | 122 km/h |
| Макс. скорость | Max speed |
| Всего поездок | Total trips |

## H25 / H26 / H28 EN in-phone (patched)

| RU | EN |
|----|----|
| 12 км · 24 мин | 12 km · 24 min |

## CapCut EN bubble prompts (re-export when convenient)

| Shot | RU bubble | EN bubble |
|------|-----------|-----------|
| H01 | Мама уже дома | Mom is home |
| H03 | Мария прибыла на секцию | Maria arrived at practice |
| H21 | Семья в пути · 58 км/ч | Family on the way · 58 km/h |
| H25–H28 cards | км / мин / labels | km / min / EN labels (already patched in ASC) |

## Finder

- `~/Downloads/ALADDIN_ASC_WaveB_All/`
- `~/Downloads/ALADDIN_ASC_H25_H26_DrivingHistory/`
- `~/Downloads/ALADDIN_ASC_H27_H28_DrivingReports/`
- **Loc check pack (2026-11-12):** `~/Downloads/ALADDIN_ASC_WaveB_LOC_CHECK_2026-11-12/`  
  · `01_NEW_CapCut_drafts_NEED_LOC` = 4 новых черновика (не H20–H23)  
  · `03_CapCut_EN_must` = H03+H21  
  · Checklist: `00_START/CHECKLIST_WAVE_B_H20_23_AND_LOC.md`

## Brand word «Aladdin» on ASC frames

**Not required** on each screenshot (App Store title already shows the name). Prefer navy+gold + product UI. Never bake Life360. Optional wordmark only with owner GO.

## New CapCut drafts (not plan H20–H23)

| Draft | Maps to | Action |
|-------|---------|--------|
| A DrivingStats UI | mood of H27, not H22 | Do not replace ASC H27; fix crash≠arrived; EN+1290 if GO |
| B LockScreen alerts | place-alert creative | EN bubbles + 1290 if GO as extra ASC |
| C WHO Mercedes facts | **new** safety-facts slide | Fix 20–50M; remove CapCut WM; EN if GO |
| D TwoPhones shield | security/scan, no text | Headline outside if used |

Plan **H20–H23 already done** — see `02_PLAN_H20_H23_DONE_do_not_replace/`.
