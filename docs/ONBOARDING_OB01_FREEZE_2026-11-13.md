# OB_01 FREEZE — не съезжает (2026-11-13)

**Статус:** FROZEN по GO владельца («всё получилось — зафиксируй»).  
**Ветка:** `master` · hero в Assets = мастер без текста · wordmark = отдельный transparent слой.

## Канон (не менять без явного GO)

| Слой | Значение |
|------|----------|
| Hero PNG | `Assets.xcassets/OnboardingHero_01.imageset/OnboardingHero_01.png` · **1179×2556** · **без** букв/watermark |
| Wordmark PNG | `OnboardingLogo_V2_Cinematic` · **прозрачный** (углы alpha=0), без чёрной плашки |
| Wordmark якорь OB_01 | `CGRect(x: 17, y: 32, width: 360, height: 121)` в `Screens/14_OnboardingScreen.swift` case 0 |
| Verify эталон | `scripts/verify_onboarding_sync_01_03.py` → `"wordmark": (17, 32, 360, 121)` |
| Title / desc / scrim OB_01 | как сейчас: title (14,450,361,60) · desc (22,546,346,66) · scrim (0,528,393,324) |
| Figma `88:53` | live Figma может быть y=271 — **iOS канон сейчас y=32**; не «чинить» iOS под старый Figma без GO |

Копия мастера: `~/Downloads/ALADDIN_OB01_Hero_куда_Аладдин_2026-11-13/FROZEN_OnboardingHero_01_1179x2556_NO_TEXT.png`

## Как не съезжает дальше

1. **Hero и wordmark — разные файлы.** Не вшивать «ALADDIN AI» в hero CapCut.  
2. **Не двигать** case 0 wordmark Y / title / desc / scrim без GO + скрина до/после.  
3. **Новый арт:** только PNG ≥1179×2556 (не превью ~470×800 / ~60 KB). Экспорт с телефона → Файлы / Original, не скрин и не сжатый чат.  
4. **Перед правкой OB_01:** `./scripts/verify_onboarding_sync_01_03.py` (хотя бы case 0 wordmark) + `git diff Screens/14_OnboardingScreen.swift`.  
5. **Не** `git restore` mega LocManager / не mass-rewrite онбординга «заодно».  
6. Figma OB_00…07 — не трогать Companion-задачами; sync Figma→iOS только по фразе SYNC-H+T + GO.

## Откат

```bash
# hero
cp ~/Downloads/ALADDIN_OB01_Hero_куда_Аладдин_2026-11-13/FROZEN_OnboardingHero_01_1179x2556_NO_TEXT.png \
  Assets.xcassets/OnboardingHero_01.imageset/OnboardingHero_01.png
# якоря — git checkout Screens/14_OnboardingScreen.swift scripts/verify_onboarding_sync_01_03.py
```

## Device QA (ещё не закрыт)

Сборка только по «GO на сборку»: OB_01 — лого над головой у Сатурна, без чёрной плашки, без CapCut watermark, title/кнопки читаемы.
