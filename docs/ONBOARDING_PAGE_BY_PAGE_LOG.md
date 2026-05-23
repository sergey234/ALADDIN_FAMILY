# Онбординг: журнал по страницам (Figma → iOS)

**Файл Figma:** `KvkUdyb5Ll31Z9FSzCbpNl` · открывать в **десктопном Figma** на Mac (`open -a Figma figma://file/...`).

**Правила:** `ONBOARDING_LAYER_RULES.md` · **код:** только `ALADDIN_iOS`.  
**План читаемости 01–06:** `ONBOARDING_OB_01_06_READABILITY_PLAN.md` (нижняя зона + белый body, OB_00/07 вне scope).  
**Финальный алгоритм (ML / вся картина):** `ONBOARDING_FINAL_ML_ALGORITHM.md` ← **начинать здесь**.  
**Координаты + SYNC по всем OB:** `ONBOARDING_COORDINATES_AND_SYNC.md` ← **эталон Y и таблица case 0–5**.  
**Мастер TODO (~30):** `ONBOARDING_TODO_MASTER.md` · **анти-регрессия hero/scrim:** §0.3 в ML-алгоритме.

| OB | `currentPage` | Figma frame | nodeId | Xcode asset | Статус | Что сделали / что дальше |
|----|---------------|-------------|--------|-------------|--------|---------------------------|
| **00** | 0 | `OB_00_Language_393x852` | `7:65` | `OnboardingHero_00` | ✅ **В порядке** | Full-bleed 393×852; hero без UI в PNG. Переходим дальше. |
| **01** | 1 | `OB_01_Family_393x852` | `81:53` | `OnboardingHero_01` | ✅ **SYNC-I/D** | Live Figma `81:53` = case 0: wordmark 10,**354**×360×121; title **536**; desc **615**×346. Build **203**. |
| **02** | 2 | `OB_02_AI_393x852` | `103:53` | `OnboardingHero_02` | ✅ **Принято** | Hero zone94. Title 479; desc 552. |
| **03** | 3 | `OB_03_Parents_393x852` | `108:53` | `OnboardingHero_03` | ✅ **H,T,I,C** ⏳ **D** | Hero `73cfae32…`. Scrim 500×320. Y 552/630. |
| **04** | 4 | `OB_04_Radar_393x852` | `117:53` | `OnboardingHero_04` | ✅ **SYNC-I** ⏳ **D** | Anchor **case 3**: Y 496/566, scrim 542×310 α0.35. Hero Figma+iOS. |
| **05** | 5 | `OB_05_Kids_393x852` | `117:70` | `OnboardingHero_05` | ✅ **SYNC-I** ⏳ **D** | Anchor **case 4**: Y 496/566, scrim 532×320 α0.38. Hero `22cd16a1…`. |
| **06** | 6 | `OB_06_Adults23_393x852` | `117:87` | `OnboardingHero_06` | ✅ **SYNC-I** ⏳ **D** | Anchor **case 5**: Y 496/566, scrim 552×300 α0.40. Hero `74ea6e9f…`. |
| **07** | 7 | `OB_07_Invite_393x852` | `122:53` | `OnboardingHero_07` | ✅ **SYNC-I** ⏳ **D** | case 6: wordmark 374, title 470, desc 508; `OnboardingOB07LegalBlock` |

---

## OB_01 — снимок на 2026-05-22

**Проблема:** полоса «вторых волос» сверху — артефакт в PNG (не двойной TabView).

**Исправление (2026-05-22, v2 после проверки):**
1. Бэкап: `docs/backup/onboarding_full_20260522_135203/`
2. Дефект: `OnboardingHero_01_DEFECT_20260522.png`
3. ~~inpaint 22px~~ — **не убрал** «вторую голову» (ошибочно отмечено готово)
4. **Финал:** `OnboardingHero_01_crop28.png` → `OnboardingHero_01.png` (crop **28px** + scale 393×852), метрика верха `hair_fraction=0`
5. Figma `81:54` upload, imageHash `2b1e8a9f6b31e61f2365d3a1372fb96cfb9672c2`
6. `build_onboarding_hero_imagesets.py` — MD5 `f3d6d7c38e5a2eee577f7941a56a9ee9` (HeroAssets = imageset)

**Figma (live):**
- `OnboardingHero_01` (`81:54`): **393×852**, (0, 0) — full-bleed
- `WORDMARK_V2` (`88:53`): 361×104 @ (16, 484) — **только в коде**, не в PNG hero
- `CHROME_bottom` @ y=710, 8 точек (активна **вторая**)

**iOS:** `OnboardingLogo_V2View` на `contentIndex == 0`.

**Чеклист:**
- [x] Hero PNG без текста/кнопок/логотипа
- [x] HeroAssets + imageset + скрипт
- [x] Визуально OK (пользователь 2026-05-22)
- [x] Анализ текста/вёрстки — § ниже

---

## OB_01 — типографика и вёрстка (анализ 2026-05-22)

**На экране в коде (не в PNG):** `OnboardingLogo_V2_Cinematic` + `onboarding_page1_title` + `onboarding_page1_desc`.

| Элемент | Figma (ориентир) | iOS (2026-05-22 readability) |
|---------|------------------|----------------------------|
| ALADDIN AI | WORDMARK 361×104, y≈484 | height 104, maxWidth 361, в `OnboardingBottomTextPanel` |
| Заголовок | y≈598, box h≈50 | 24pt Bold (22 SE), white, center, перенос по словам |
| Описание | y≈656, box h≈48 | 16pt Regular, **white 92%**, center, низ + scrim 0.45 |

**RU-тексты:** «Защита всей семьи в кармане» / «Комплексная система защиты от более 100 видов киберугроз».

---

## Deep links (Figma desktop, Mac)

```
OB_00: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=7-65
OB_01: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=81-53
OB_02: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=103-53
OB_03: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=108-53
OB_04: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=117-53
OB_05: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=117-70
OB_06: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=117-87
OB_07: figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=122-53
```

*Обновлять строки таблицы после каждой сессии правок.*
