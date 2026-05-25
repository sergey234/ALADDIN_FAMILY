# OB_03 — Родительский контроль: эталон Figma ↔ iOS

**Зафиксировано:** 2026-05-23 (live read из Figma file `KvkUdyb5Ll31Z9FSzCbpNl`).

Использовать как единственный источник правды для экрана 03. При правках в Figma — обновить этот файл и `OnboardingFigmaAnchor` case 2.

---

## Идентификаторы

| Поле | Значение |
|------|----------|
| Figma file key | `KvkUdyb5Ll31Z9FSzCbpNl` |
| Страница | `OnboardingHero_00` |
| Frame | `OB_03_Parents_393x852` · node **`108:53`** |
| Deep link | [figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=108-53](figma://file/KvkUdyb5Ll31Z9FSzCbpNl?node-id=108-53) |
| iOS TabView page | **3** (`-OnboardingPage3`) |
| `contentIndex` / anchor | **`case 2`** |
| Xcode hero asset | **`OnboardingHero_03`** (imageset) |
| Figma hero layer | `OnboardingHero_03` · **`108:54`** |

### Канвас (после выравнивания ряда OB, 2026-05-23)

| Параметр | Значение |
|----------|----------|
| canvas X | **3183** |
| canvas Y | **40** |
| visible | **true** (ранее был скрыт и перекрыт OB_04) |
| Шаг от OB_02 | +441 px (как у всего ряда OB_00…07) |

---

## Корневой frame `108:53`

| Параметр | Значение |
|----------|----------|
| Размер | **393 × 852** |
| `clipsContent` | true |
| `cornerRadius` | 12 |
| Фон (fill) | **`#0a1128`** opacity 1 |

---

## Слой 1 — Hero `OnboardingHero_03` (`108:54`)

| Параметр | Значение |
|----------|----------|
| Тип | RECTANGLE |
| Позиция в frame | **x=0, y=0** |
| Размер | **393 × 852** (full-bleed) |
| Fill | **IMAGE**, `scaleMode: **CROP**` |
| imageHash (Figma) | `5d1418b461cede93b389d3e7c61ce9ff070fe999` (после правки 2026-05-24: без лампы, сдвиг героя) |
| opacity | 1 |

### PNG в Xcode (letterbox)

| Параметр | Значение |
|----------|----------|
| Первая строка контента в PNG | y ≈ **70** (как OB_04/05) |
| Compose | zone **×1.10** в слот 361×460, paste canvas **(16, 42)** → margins **L/R=16** |
| iOS hero | **`scaledToFit`** + aspect **393:852** (не `scaledToFill` — на реальном iPhone резало руки) |
| iOS zoom | **нет** (1.0 implicit) |
| iOS ambient wash | purple 0.12 → pink 0.08 (`HeroAmbientPresentation`) |

---

## Слой 2 — Scrim `READABILITY_scrim_bottom` (`217:55`)

| Параметр | Значение |
|----------|----------|
| Позиция | **x=0, y=500** |
| Размер | **393 × 320** |
| Тип градиента | LINEAR (вертикальный, снизу вверх) |

### Stops (Figma → iOS `scrimGradientStops`, case `500, 0.40`)

| Stop | position | alpha (чёрный) |
|------|----------|----------------|
| 0 | **0** | **0** |
| mid | **0.4** | **0.16** |
| 1 | **1** | **0.40** (`scrimMaxOpacity`) |

`gradientTransform` в Figma: `[[0,1,0],[0.5,0,0.5]]`.

---

## Слой 3 — Title `TITLE_page3` (`108:68`)

| Параметр | Значение |
|----------|----------|
| Текст (RU) | **Родительский контроль** |
| Позиция | **x=16, y=552** |
| Размер box | **361 × 60** |
| Шрифт | **SF Pro Bold**, 24 pt |
| Выравнивание | CENTER |
| Цвет | **`#FFFFFF`** opacity 1 |
| lineHeight | AUTO |
| letterSpacing | 0% |

---

## Слой 4 — Description `DESC_page3` (`108:69`)

| Параметр | Значение |
|----------|----------|
| Текст (RU) | Система обучения детей безопасности. Вы видите всю активность детей в интернете. Самообучающаяся система защиты AI |
| Позиция | **x=14, y=630** |
| Размер box | **361 × 80** |
| Шрифт | **SF Pro Regular**, 16 pt |
| Выравнивание | CENTER |
| Цвет | **`#FFFFFF`** opacity **0.92** |
| Зазор title → desc | **630 − (552+60) = 18 pt** |

---

## Слой 5 — Chrome `CHROME_bottom` (`108:55`)

| Параметр | Значение |
|----------|----------|
| Позиция в frame | **x=16, y=710** |
| Размер | **361 × 118** |

### Точки `CHROME_page_dots` (`108:56`)

| Параметр | Значение |
|----------|----------|
| Внутри chrome | x=105, y=0 |
| Размер | 152 × 32 |
| Фон pill | `#000000` @ **35%** |
| cornerRadius | 999 |
| Активная точка (4-я) | 12×12 @ x=62; остальные 8×8 |

### Кнопка `CHROME_btn_continue` (`108:65`)

| Параметр | Значение |
|----------|----------|
| Внутри chrome | x=0, y=48 |
| Размер | **361 × 50** |
| cornerRadius | **16** |
| Градиент | **#2E5BFF** (0%) → **#3373F2** (100%) |
| Label `LABEL_continue` (`108:66`) | «Продолжить», Inter Semi Bold 17, `#FFFFFF`, в кнопке x=126 y=15 |

### Home indicator `GUIDE_home_indicator` (`108:67`)

| Параметр | Значение |
|----------|----------|
| x, y | 114, 73 (внутри chrome) |
| Размер | 134 × 5 |
| cornerRadius | 3 |
| Fill | `#FFFFFF` @ **25%** |

---

## iOS — `OnboardingFigmaAnchor` case 2

Должно совпадать с Figma (проверено):

```swift
title: CGRect(x: 16, y: 552, width: 361, height: 60)
desc:  CGRect(x: 14, y: 630, width: 361, height: 80)
scrim: CGRect(x: 0, y: 500, width: 393, height: 320)
scrimMaxOpacity: 0.40
maxBodyLines: 5
layoutMode: .standard
```

Локализация: `onboarding_page3_title` / `onboarding_page3_desc` в `14_OnboardingScreen.swift`.

---

## Чеклист «не сломать OB_03»

1. Frame на канвасе **видим**, X=**3183**, не накладывать на OB_04.
2. Hero — **CROP** full-bleed, не SOLID-заглушка.
3. Scrim **500×320**, stops **0 / 0.16@0.4 / 0.40@1** — не подменять stops от OB_02 или OB_04.
4. Title Y=**552**, Desc Y=**630** — не путать с OB_04 (496/566).
5. В симуляторе: `-OnboardingPage3`.

---

## Связанные документы

- `docs/ONBOARDING_COORDINATES_AND_SYNC.md` § OB_03
- `docs/ONBOARDING_OB_02_03_04_HERO_ANALYSIS.md`
- `.cursor/rules/onboarding-ob03-figma-spec.mdc`
