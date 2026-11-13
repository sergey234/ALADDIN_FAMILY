# Карта картинок в приложении ALADDIN — для следующей ML-системы

**Дата:** 2026-11-14 · **Build в git:** **23** · Version **1.0.2**  
**Канон релиза:** `docs/RELEASE_BUILD_PROMPT.md`  
**UX-волна / Удобный HYBRID:** `docs/PLAN_UX_PHONE_QA_WAVE_2026-11-13.md`

---

## 0. Одно правило (не путать слои)

| Слой | Где | Что делать |
|------|-----|------------|
| **В приложении (SSOT runtime)** | `Assets.xcassets/*.imageset` | Только отсюда грузит Xcode / `Image("…")` |
| **Figma (макет)** | ключи в `docs/FIGMA_*.env` | Координаты / референс; не копировать OB в SimpleHome |
| **CapCut / Downloads (первоисточник арта)** | `~/Downloads/ALADDIN_*` | Генерация; после выбора → imageset |
| **Маркетинг ASC / копии** | `docs/competitors/figma_preview_fig_l/…` | Store / сравнение; не подменять runtime без GO |
| **Бэкапы до правок** | `BACKUPS/…`, `Resources/HeroAssets/*_BEFORE_*` | Откат; не ship как основной ассет |

**Не трогать** onboarding Figma `KvkUdyb5Ll31Z9FSzCbpNl` (OB_00…07) при работах SimpleHome — rule `companion-figma-onboarding-untouched` / `docs/FIGMA_ONBOARDING.env`.

---

## 1. Удобный режим · HYBRID (build 23)

| UI | Image name (Assets) | Figma | Первоисточник CapCut |
|----|---------------------|-------|----------------------|
| Hero центр | `SimpleHome_Hero_5811` | `docs/FIGMA_SIMPLEHOME.env` · file `3xbmhXxfMNMBmIbeJdUDpW` · frame `1:2` | `~/Downloads/ALADDIN_SimpleHome_CAP_5811_HYBRID_2026-11-13/` (interim; Original — опц.) |
| Дверь Проверить | `SimpleHome_Door_Check` | placeholder → canon PNG | `…DoorIcons_CANON_2026-11-14/` · **5943** |
| Дверь Ребёнок | `SimpleHome_Door_Child` | | **5904** |
| Дверь Где семья | `SimpleHome_Door_Where` | | **5944** |

Код: `Screens/SimpleHomeScreen.swift` · флаг `aladdin.simpleHomeHybridOrbit`.  
Backup UI до HYBRID: `BACKUPS/SimpleHome_PRE_HYBRID_P7_20261114_010010/`.

---

## 2. Онбординг heroes (OB_00…08)

| Экран | Assets.xcassets | Figma onboarding | Примечание |
|-------|-----------------|------------------|------------|
| OB_00…07 | `OnboardingHero_00` … `OnboardingHero_07` | `docs/FIGMA_ONBOARDING.env` · `KvkUdyb5Ll31Z9FSzCbpNl` | SYNC-H+T · `docs/ONBOARDING_COORDINATES_AND_SYNC.md` |
| OB_01 | `OnboardingHero_01` | | **FROZEN** wordmark y — `docs/ONBOARDING_OB01_FREEZE_2026-11-13.md` |
| OB_08 (если есть) | `OnboardingHero_08` | | |

Бэкапы PNG: `Resources/HeroAssets/OnboardingHero_*_BEFORE_*`.

---

## 3. Wave C · Child / Check heroes (уже в app)

| Экран / боль | Assets name | Копии / ASC masters |
|--------------|-------------|---------------------|
| Ребёнок · контроль | `ICON_ALIVE_HERO_ChildControl` | `docs/competitors/figma_preview_fig_l/wave_c_hero_child_check/in_app/` + `marketing_asc/` |
| Ребёнок · угрозы | `ICON_ALIVE_HERO_ChildThreats` | то же |
| Проверить · scam | `ICON_ALIVE_HERO_CheckScam` | то же |
| Проверить · семья | `ICON_ALIVE_HERO_CheckFamily` | то же |

Манифест: `docs/competitors/figma_preview_fig_l/wave_c_hero_child_check/MANIFEST.md`.  
AliveGlyph doors/icons ряды: `docs/competitors/figma_preview_fig_l/PLAN_100_PERCENT_ASSET_ROWS.md`.

---

## 4. Family Hub / SOS / Invite / Pets (Alive H*)

Все runtime: `Assets.xcassets/ICON_ALIVE_HERO_H*`  
Примеры: H06 SOS Intro · H13 SOS Release · H14 place/calendar · H15 pets · H16 lock · H17/H25 family · H18 SUV · H20 Invite OG.

Код: `AliveGlyph` / `AliveIconID` → `Shared/Components/AliveIconStyle.swift`.

---

## 5. Wordmark / App Icon

| Что | Runtime | Источник |
|-----|---------|----------|
| Wordmark V2 | brand assets + onboarding layout | `Resources/BrandAssets/ALADDIN_AI_V2_Logo/` · Figma WORDMARK_V2 |
| App Icon | `Assets.xcassets/AppIcon.appiconset` | ASC 1024; бэкап `*_BEFORE_*` рядом |

---

## 6. Где смотреть «всё в одном месте» (индекс)

1. **Этот файл** — карта слоёв + пути.  
2. **`Assets.xcassets/`** — единственный runtime каталог.  
3. **`docs/PLAN_UX_PHONE_QA_WAVE_2026-11-13.md`** — задачи UX + HYBRID A–G + NAV.  
4. **`docs/competitors/figma_preview_fig_l/PLAN_100_PERCENT_ASSET_ROWS.md`** — таблица Alive doors/icons.  
5. **`docs/FIGMA_SIMPLEHOME.env`** + **`docs/FIGMA_ONBOARDING.env`** — ключи файлов (не смешивать).  
6. CapCut папки в Downloads — первоисточник; после pick копировать в imageset.

Симлинк/копия «все PNG в одну папку» **не** делается автоматически (объём + дубли). Для ML: читать этот индекс → открывать imageset / Downloads / Figma по таблице.

---

## 7. Build 23 — что вошло (кратко)

- SimpleHome HYBRID MAX (orbit + glass doors + chips AI/Меню + «Добавить в семью»)
- New York / gold header · пульс дверей · list fallback
- Root nav fade (фикс «уезд влево» Settings→Удобный + reopen Меню)
- Trial slots heal (client + `app/routers/family.py` + subscription_service)
- UX wave P0–P6 / H1–H8 / FNT (код; Device QA часть ещё на телефоне)

---

## 8. Запреты

- Не коммитить `telegram_stars_shop_bot/`, `.env`, VPN §32 handoff  
- Не rewrite `LocalizationManager.swift` целиком  
- Не bump marketing 1.0.2→1.0.3 без ASC «+» version + GO  
- След. build только **24** после нового GO на bump  
