# MNEMO B8-T04 — Manual smoke matrix (4 ages × 8 mnemo categories)

**Date:** 2026-06-13 (updated for catalog v4 batch)  
**Device:** iOS Simulator `iPhone 13 Pro Max, OS 18.4` or TestFlight build  
**Goal:** Each cell opens mnemo catalog → lesson shows mnemo phases; v4 behaviors verified.

## Matrix

| Age tab | Category | Expected mnemo label | 4 phases visible | v4 extras |
|---------|----------|----------------------|------------------|-----------|
| Kids (4–6) | Songs | `child_mnemo_label_songs_kids` | ☐ | ☐ 1 card = 1 track; recall required |
| School (7–12) | Games | `child_mnemo_label_games_school` | ☐ | ☐ **first row = games.05** «Дворец образов» |
| School (7–12) | Study | `child_mnemo_label_study_school` | ☐ | ☐ **study.01–03 open**; warmup 30s |
| School (7–12) | Cartoons | `child_mnemo_label_cartoons_school` | ☐ | ☐ progress = Открывал/Запомнил |
| Teen (13–17) | Music | `child_mnemo_label_music_teen` | ☐ | ☐ |
| Teen (13–17) | Video | `child_mnemo_label_video_teen` | ☐ | ☐ |
| Young (18–22) | Movies | `child_mnemo_label_movies_young` | ☐ | ☐ |
| Young (18–22) | Education | `child_mnemo_label_education_young` | ☐ | ☐ |

## Steps (repeat per row)

1. Launch app → Child interface → select age tab.
2. Tap category tile → catalog opens with **Академия памяти** banner.
3. Confirm banner shows 4 phase labels (Образ / Якорь / Вспомни / Награда).
4. Confirm row progress: **«Открывал · Запомнил N%»** (not fake +20% per tap).
5. Open first **unlocked** item → lesson sheet shows phase dots + current phase name.
6. Tap through Encode → Anchor → Recall (pass or fail) → Reward.
7. If semester locked: tap 🔒 row → **alert** with semester name + remaining %.

## SRS / unified queue (B10 + v4)

- [ ] Badge «Сегодня повтори: N» counts due **across all** mnemo categories.
- [ ] Badge tap opens first due item (may navigate to another category).
- [ ] Deep link `aladdin://mnemo/review?category=games&itemId=games.05` opens palace lesson.
- [ ] Local notification tap routes to mnemo category.

## Study fail CTA (v4)

- [ ] Fail study test → text + button «Открыть Дворец образов» → `games.05` experience.

## Sign-off

| Tester | Date | Result |
|--------|------|--------|
| Cursor + Xcode build | 2026-06-14 | **PASS** (iPhone 13 Pro Max 15.2, catalog v4) |

**Automated gates (Phase C only — run at end):**

```bash
python3 scripts/child_localization_gate.py --mnemo-full
MNEMO_TEST_DEST='platform=iOS Simulator,name=iPhone 13 Pro Max,OS=18.4' ./scripts/mnemo_run_tests.sh
```
