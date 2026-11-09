# S18 Snowball — канон цвета (для любой ML-системы)

**Дата lock:** 2026-11-09 · **Владелец:** скрин эталон  
**Эталон-файл:** `docs/competitors/snowball_s18_ref/OWNER_SNOWBALL_COLOR_REF_2026-11-09.jpg`  
**Задачи матрицы:** **S18** (sections_color) + **S09** (parent без белых полей) + **S43/S51** (liked UI / compare)  
**SSOT план:** `FAMILY_SAFETY_MASTER_FINISH_88_PLAN_2026-11-09.md` § WAVE VISUAL / § S18 ниже  

---

## 0. Что это (одно предложение)

**Snowball-цвет = вертикальный «свечение» фон: почти чёрно-фиолетовый сверху → насыщенный magenta/розово-фиолетовый в середине → мягкий lavender-pink снизу.** Иконка snowball на скрине — только маркер бренда; **на экраны приложения иконку не клеим**, берём **только градиент/токены**.

---

## 1. Факт vs код (важно)

| | Статус 2026-11-09 вечер |
|--|--------|
| Эталон владельца | purple → magenta glow (jpg выше) |
| `Shared/Theme/AladdinSnowballPalette.swift` | ✅ multi-stop vertical HEX §2 (не navy) |
| Rollout | ParentDashboard · Parental · WhereIsPhone sheets · DrivingReports · FamilySafetyRemainderHub · FamilyModalBaseView |
| Device evidence | ⏳ после GO на сборку |

---

## 2. Точные стопы (сэмпл с эталон-jpg, 576×1024)

Сэмпл полос **мимо иконки** (края кадра). Другая ML **обязана** читать jpg + эти стопы, не выдумывать «фиолетовый».

| Stop (Y %) | HEX | SwiftUI `Color(red:green:blue:)` |
|------------|-----|----------------------------------|
| 0.05 top | `#110B13` | `(0.067, 0.043, 0.075)` |
| 0.12 | `#231727` | `(0.137, 0.090, 0.153)` |
| 0.22 | `#4D3353` | `(0.302, 0.200, 0.325)` |
| 0.32 | `#7E5483` | `(0.494, 0.329, 0.514)` |
| 0.42 | `#90618F` | `(0.565, 0.380, 0.561)` |
| 0.52 mid hot | `#AC76A6` | `(0.675, 0.463, 0.651)` |
| 0.62 glow | `#D09CC9` | `(0.816, 0.612, 0.788)` |
| 0.72 | `#D0A2CB` | `(0.816, 0.635, 0.796)` |
| 0.82 | `#C89FC8` | `(0.784, 0.624, 0.784)` |
| 0.92 bottom | `#B091B8` | `(0.690, 0.569, 0.722)` |

**Минимум для кода (4-stop, если надо упростить):**  
`#110B13` → `#7E5483` → `#D09CC9` → `#B091B8`  
`LinearGradient` **top → bottom** (не diagonal navy).

**Текст/акцент поверх (ALADDIN, не со скрина):**
- `ink` = белый / near-white  
- `inkMuted` = white ~0.78  
- `gold` = существующий `Color.secondaryGold` (кнопки/CTA)  
- `glass` = white 0.10–0.14 + stroke white 0.18  

**Не делать:** сплошной белый card-фон (ломает S09); синий navy canvas; фиолетовый Inter/AI-purple «другой».

---

## 3. Как описать другой ML (копипаст)

```text
S18 Snowball COLOR CANON (ALADDIN Family Safety):
Source of truth photo:
  docs/competitors/snowball_s18_ref/OWNER_SNOWBALL_COLOR_REF_2026-11-09.jpg
DO NOT use current navy AladdinSnowballPalette values — they are WRONG vs owner.
Replace canvasTop/Bottom/canvasGradient with multi-stop vertical LinearGradient
matching sampled HEX stops in SNOWBALL_S18_COLOR_CANON_FOR_ML_2026-11-09.md §2
(#110B13 → … → #D09CC9 → #B091B8).
Apply ONLY as screen/sheet BACKGROUND via AladdinSnowballPalette.canvasGradient.
Keep ALADDIN gold CTA + glass cards; no white full-bleed panels (S09).
Do NOT paste the snowball icon onto product screens.
Do NOT change Onboarding OB_* hero / Main StormMesh map tiles / MapKit map itself.
Target screens: list in §4 of the same doc.
Evidence: side-by-side screenshot vs OWNER jpg (gradient match), then device QA S18/S09.
No xcodebuild without owner GO. No commit/push without owner GO.
```

---

## 4. Куда вставляем (IN) / куда НЕ (OUT)

### IN — фон `AladdinSnowballPalette.canvasGradient` (после правки токенов)

| # | Экран / поверхность | Файл (якорь) | Зачем |
|---|---------------------|--------------|-------|
| 1 | Parent dashboard | `Screens/ParentDashboardView.swift` | S09 + S18 |
| 2 | Parental control shell (где белые поля) | `Screens/07_ParentalControlScreen.swift` | S09 |
| 3 | WhereIsPhone sheets (member / quiet / places / lost…) | `Screens/WhereIsPhoneScreen.swift` | S18 + S19 chrome |
| 4 | Driving reports / trip detail / play chrome | `Shared/Components/Modals/DrivingReportsModal.swift` | S23–28 / S61–62 UI chrome |
| 5 | Family remainder hub | `Screens/FamilySafetyRemainderHub.swift` | S18 sections |
| 6 | Family groups / circle labels UI | `FamilyGroupsModal` (или актуальный groups sheet) | S41/S55–57 chrome |
| 7 | SecondHand / 17-checks shell (если отдельный canvas) | `FamilySecondHandPackViews` / threat coverage host | S59/S65 chrome |
| 8 | Filter hub shell (если family visual wave) | filter hub screen | S67–69 **только фон**, не менять copy |

Раскат: **сначала 1–5** (ядро Family Safety), потом 6–8.

### OUT — не перекрашивать этим градиентом

| Поверхность | Почему |
|-------------|--------|
| Onboarding OB_00…07 | другой продукт / hero full-bleed |
| MapKit карта (тайлы) | карта остаётся картой; Snowball = sheet/chrome вокруг |
| App Store / splash системный | отдельный asset pipeline |
| Чистый белый Legal/WebView | читаемость документов |
| Иконка snowball по центру каждого экрана | только цвет; иконка ≠ UI chrome |

---

## 5. Можно ли повторить на 100%?

| Уровень | Реалистично? | Как |
|---------|--------------|-----|
| **Цвет фона UI ~95–98%** | ✅ Да | Multi-stop `LinearGradient` по §2 + те же start/end `.top`→`.bottom` |
| **Фото-glow / bloom jpg 100% pixel** | ⚠️ Не градиентом | Либо `Image("…ref")` + `scaledToFill` как ambient (редко), либо принять ~2–5% дельту soft-glow |
| **Иконка snowball на каждом экране** | ❌ Не цель | Иконка только на эталон-скрине |

**Ответ владельцу:** цвет разделов — **да, повторяем токенами на ≥95%** (и закрываем S18 по device side-by-side). Пиксель-в-пиксель jpg со свечением — только если явно скажете «класть jpg фоном», иначе градиент-канон.

**Definition of Done S18 (код):**
1. `AladdinSnowballPalette` стопы = §2 (не navy).  
2. Экраны IN §4 п.1–5 используют `canvasGradient`.  
3. Нет full-bleed white panels на ParentDashboard.  
4. Device: владелец сверяет с `OWNER_SNOWBALL_COLOR_REF_*.jpg`.  

---

## 6. Порядок работ (агент)

1. Правка **только** `Shared/Theme/AladdinSnowballPalette.swift` (стопы + комментарий «owner jpg 2026-11-09»).  
2. Grep `AladdinSnowballPalette` / белые `.background(Color.white` на Parent/Family — точечно.  
3. Не трогать OB_*, bot, VPN.  
4. Static verify / device — после **GO на сборку**.  
5. FIG-L (L*) — **после** device, отдельный GO; в Figma те же HEX.
