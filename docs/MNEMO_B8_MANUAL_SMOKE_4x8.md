# MNEMO B8-T04 — Manual smoke matrix (4 ages × 8 mnemo categories)

**Date:** 2026-06-05  
**Device:** iOS Simulator (iPhone 16) or TestFlight build  
**Goal:** Each cell opens mnemo catalog → lesson shows 4 phases (Encode → Anchor → Recall → Reward).

## Matrix

| Age tab | Category | Expected mnemo label | 4 phases visible |
|---------|----------|----------------------|------------------|
| Kids (4–6) | Songs | child_mnemo_label_songs_kids | ☐ |
| School (7–12) | Games | child_mnemo_label_games_school | ☐ |
| School (7–12) | Study | child_mnemo_label_study_school | ☐ |
| School (7–12) | Cartoons | child_mnemo_label_cartoons_school | ☐ |
| Teen (13–17) | Music | child_mnemo_label_music_teen | ☐ |
| Teen (13–17) | Video | child_mnemo_label_video_teen | ☐ |
| Young (18–22) | Movies | child_mnemo_label_movies_young | ☐ |
| Young (18–22) | Education | child_mnemo_label_education_young | ☐ |

## Steps (repeat per row)

1. Launch app → Child interface → select age tab.
2. Tap category tile → catalog opens with **Академия памяти** banner.
3. Confirm banner shows 4 phase labels (Образ / Якорь / Вспомни / Награда).
4. Open first content item → lesson sheet shows phase dots + current phase name.
5. Tap through Encode → Anchor → Recall (pass or fail) → Reward.

## SRS / push (B10 cross-check)

- [ ] Badge «Сегодня повтори: N» opens first due item.
- [ ] Deep link `aladdin://mnemo/review?category=games` opens Games catalog.
- [ ] Local notification tap routes to mnemo category.

## Sign-off

| Tester | Date | Result |
|--------|------|--------|
| | | PASS / FAIL |

**Automated gates (run before manual):**

```bash
python3 scripts/child_localization_gate.py
xcodebuild test -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16' \
  -testPlan ALADDIN_MnemoCore.xctestplan
xcodebuild test -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16' \
  -only-testing:ALADDINUITests/MnemoAcademyUITests
```
