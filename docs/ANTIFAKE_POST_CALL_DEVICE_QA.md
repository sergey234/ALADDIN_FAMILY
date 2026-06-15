# Post-call device QA (E-06)

**Must:** ≤ 2 taps from notification to Call upload panel.

## Prerequisites

- Physical iPhone, TestFlight or dev build with `CallKit` + notification permission
- Antifake Hub available (Premium or QA bypass)
- Toggle **«Напоминать проверить запись после звонка»** ON (Call Directory card)

## Steps

1. Place or receive a **cellular** call lasting ≥ 5 s; hang up.
2. Within ~15 min cooldown window, expect local notification «Проверить запись звонка?»
3. Tap notification → app opens **Antifake Hub** → **Звонок** tab.
4. Confirm post-call banner visible; optional caller_id prefill if previously entered (`E-07`).
5. Pick recording file → consent alert on first upload (`N-05`) → **Проверить**.

## Pass criteria

- Deep link `aladdin://antifake/call-check` resolves (`E-03`)
- ≤ 2 user taps after notification to file picker / check button
- Cooldown: second call within 15 min does **not** spam notifications (`E-08`)

## Known limitations

- iOS does not provide caller number to third-party apps — user enters manually from Recents.
- Wi-Fi-only / FaceTime calls may not trigger `CXCallObserver` the same way as cellular.

## Toggle OFF test (E-05)

1. Disable reminder toggle on Call Directory card.
2. Repeat call — **no** notification expected.
