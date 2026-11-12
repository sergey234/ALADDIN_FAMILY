# ВСЕ промпты CapCut / AI · ALADDIN Wave B

**Как пользоваться:**  
1) Открой секцию ассета  
2) Приложи файл из `refs/`  
3) Скопируй блок **EN VISUAL PROMPT** в AI CapCut / image model  
4) Экспорт по **OUTPUT**  
5) Клади в `export_targets/out/`

**Общий negative (добавляй ко всем):**  
`Life360 logo, purple brand clone, watermark, blurry, low-res, cropped fingers, extra limbs, text letters, UI buttons, iPhone bezel unless asked, photoreal horror, blood`

---

# BATCH 1 — СНАЧАЛА (in-app, сразу видно)

---

## H14_A — 3D кусочек земли + пин места

| | |
|--|--|
| **Зачем** | Карточка «Место» (Дом/Школа) — справа от адреса |
| **Куда в ALADDIN** | Where → Places → detail sheet |
| **Реф приложить** | `refs/L360_H14.png` (обведено маркером сверху) |
| **UI size** | **120×120 pt** |
| **Export** | **360×360 px** PNG, **прозрачный фон** |
| **Имя out** | `ALADDIN_H14_A_PlaceLandPin_360.png` |

**RU (что нужно):**  
Маленький изометрический «ломтик» местности: трава, бордюр, кусок асфальта, кустик. Над ним объёмный пин **золотой** `#F59E0B` (не фиолетовый). Без текста, без карты улиц целиком, без UI.

**EN VISUAL PROMPT:**
```
Isolated isometric 3D clay product illustration, small floating landscape slice: green grass patch, gray asphalt curb edge, tiny bush, soft studio lighting. Above center a premium location map pin in warm gold #F59E0B with soft shadow, slightly glossy. Clean transparent background. No text, no logos, no phone UI, no purple pin. Style: friendly soft 3D like modern family-safety app marketing, high detail, centered, square composition 1:1.
```

---

## H14_B — 3D календарь + жёлтый карандаш

| | |
|--|--|
| **Зачем** | Блок «Добавить событие здесь» |
| **Куда** | Place detail + Events empty |
| **Реф** | `refs/L360_H14.png` (маркер снизу) · также `L360_H09.jpg` |
| **UI** | **96×96 pt** |
| **Export** | **288×288 px** PNG transparent |
| **Out** | `ALADDIN_H14_B_CalendarPencil_288.png` |

**EN VISUAL PROMPT:**
```
Isolated 3D clay desk calendar spiral-bound, colorful month grid squares (gold, teal, soft blue accents — NOT purple brand), yellow pencil leaning diagonally across calendar. Soft shadow on transparent background. Cute premium product render, square 1:1, no text readable, no logos, no hands, high detail.
```

---

## H18 — 3D машина (SUV) на подставке

| | |
|--|--|
| **Зачем** | Карточка поездки в Вождении |
| **Куда** | Driving trip history row |
| **Реф** | `refs/L360_H18.png` (машина обведена) |
| **UI** | **112×112 pt** |
| **Export** | **336×336 px** PNG transparent |
| **Out** | `ALADDIN_H18_SUV_Clay_336.png` |

**EN VISUAL PROMPT:**
```
Isolated stylized soft-3D SUV car, light blue-silver body, friendly rounded shapes, sitting on small gray oval ground shadow/platform. Three-quarter front view. Premium clay render, transparent background, no people, no text, no logos, no purple. Square 1:1, centered.
```

---

## H16 — золотой замок + ключи

| | |
|--|--|
| **Зачем** | «Откройте отчёты водителя» |
| **Куда** | Driving soft-paywall card |
| **Реф** | `refs/L360_H16.png` |
| **UI** | **140×140 pt** |
| **Export** | **420×420 px** PNG transparent |
| **Out** | `ALADDIN_H16_GoldLockKeys_420.png` |

**EN VISUAL PROMPT:**
```
Isolated premium 3D gold padlock #F59E0B / warm metallic gold, silver shackle, keyring with one classic silver key and one small teal/green electronic key fob. Soft studio light, transparent background, product hero centered, square 1:1. No text, no logos, no purple plastic toy look — elegant family-app unlock metaphor.
```

---

## H15_PICK — собака / кошка / «другое» (3 арта)

| | |
|--|--|
| **Зачем** | Экран «Какой у вас питомец?» |
| **Куда** | Pets add flow |
| **Реф** | `refs/L360_H15.png` |
| **UI** | каждый арт **88×88** (потом в круг) |
| **Export** | **264×264** ×3 transparent |
| **Out** | `ALADDIN_H15_Dog_264.png` · `…_Cat_264.png` · `…_Other_264.png` |

**EN — DOG:**
```
Cute hand-drawn sticker style dog head side profile, tongue out, collar tag, thick white outline, black line art with minimal fill, transparent background, centered, square. Friendly family app mascot, no text.
```

**EN — CAT:**
```
Cute hand-drawn sticker style cat face front view, thick white outline, black line art, slightly grumpy cute, transparent background, square, no text.
```

**EN — OTHER:**
```
Cute hand-drawn sticker style round smiling otter-or-seal pet face, thick white outline, black line art, transparent background, square, no text.
```

---

## H15_HERO / empty dog (если нужна «большая собака»)

| | |
|--|--|
| **Реф** | тот же pets / family dog from H17 |
| **UI** | **160×160** |
| **Export** | **480×480** |
| **Out** | `ALADDIN_H15_DogHero_480.png` |

**EN:**
```
Friendly 3D clay small dog sitting, black-and-tan, purple replaced by soft gold collar tag #F59E0B, transparent or soft shadow only, cute, centered, no text, no logos.
```

---

## H17 — большая 3D семья (+ пёс)

| | |
|--|--|
| **Зачем** | «Создайте семью» empty / шаг |
| **Куда** | Family empty / Where invite hero — **НЕ** Onboarding OB_* |
| **Реф** | `refs/L360_H17.png` (семья в рамке маркера) |
| **UI** | **320×220** |
| **Export** | **960×660** PNG |
| **Out** | `ALADDIN_H17_FamilyHero_960x660.png` |
| **Фон** | мягкая «карта» green/beige abstract OK |

**EN VISUAL PROMPT:**
```
Warm stylized 3D clay family group: mother with glasses, father with beard, teen boy, young girl petting small dog, standing on soft abstract map-like green and beige ground. Soft daylight, friendly diverse, premium app illustration. No logos, no Life360, no purple UI chrome, no readable text. Landscape 960x660 composition, characters centered.
```

---

## H19 / H25 — семья для разрешений (обнимаются)

| | |
|--|--|
| **Реф** | `refs/L360_H25.png` или H19 |
| **UI** | **320×220** |
| **Export** | **960×660** |
| **Out** | `ALADDIN_H25_FamilyHug_960x660.png` |

**EN:**
```
Soft 3D clay family hug: father, mother with glasses, young daughter, on simplified map background with soft green streets. Warm emotional safety mood. No logos, no text, no purple brand. Landscape composition.
```

---

# BATCH 2 — SOS tips (иллюстрации)

## H06 — человек + телефон с SOS

| Реф | `L360_H06.jpg` |
| UI | 280×200 → export **840×600** |
| Out | `ALADDIN_H06_SOS_Phone_840x600.png` |

**EN:**
```
Minimal line-art mixed with soft 3D: person walking atop a smartphone screen featuring a large circular gold SOS button (not purple). Clean white/transparent background, educational safety illustration, no logos, no blood, no weapons.
```

## H13 — девушка с телефоном + аватары семьи дугой

| Реф | `L360_H13.jpg` |
| Export | **840×600** |
| Out | `ALADDIN_H13_SOS_Release_840x600.png` |

**EN:**
```
Black-and-white line illustration of a young woman holding a glowing phone upward; above her head an arc of 4 circular friendly family avatar faces. Soft gold glow on phone. Transparent or white background. No logos, no text in image.
```

---

# BATCH 3 — Marketing / App Store (CapCut композит)

## H01 / H02 — телефон с картой семьи (реклама)

| Реф | `L360_H01.jpg`, `L360_H02.jpg` |
| Export ASC | **1290×2796** |
| Out | `ALADDIN_ASC_H01_LiveMap_1290x2796.png` |

**EN (сцена):**
```
App Store screenshot style: modern iPhone mockup centered on soft storm-dark to gold gradient (NOT purple). Phone screen shows family map with 3 circular photo pins and bottom sheet list. ALADDIN gold accents #F59E0B. No Life360 logo. Clean marketing, Cyrillic headline space at top leave empty for text overlay later OR omit text.
```

## H21 — спидометр + crash toggle

| Реф | `L360_H21.jpg` |
| Export | ASC **1290×2796** + prop speedometer **600×600** |
| Out | `ALADDIN_H21_Speedo_600.png` · `ALADDIN_ASC_H21_…` |

**EN prop:**
```
Isolated circular speedometer widget, white face, gold/red accent rim, needle, reading aesthetic 82, soft "MAX" area blank (no letters if possible), transparent background, glossy glass, square.
```

## H20 — OG приглашение · глобус + пин с аватаром

| Реф | `L360_H20.jpg` |
| Export | **1200×630** |
| Out | `ALADDIN_H20_InviteOG_1200x630.png` |

**EN:**
```
Open Graph share card 1200x630: stylized soft 3D Earth globe, center circular avatar pin with gold ring, tiny gold lamp or ALADDIN mark corner (simple), friendly, no Life360, no URL text. Landscape.
```

## H22–H24, H26–H28 — рекламные кадры

| Реф | соответствующие `L360_H22…H28` |
| Export | **1290×2796** каждый |
| Метод | CapCut: фон градиент storm/gold + phone mockup + наш UI скрин (позже подставим реальный) |

**EN template:**
```
Premium App Store frame 1290x2796, soft gold and deep navy gradient background, centered iPhone mockup, generous top margin for headline, no competitor logos, no purple Life360 branding.
```

## H27 — три stat-карточки (можно Figma, опц. CapCut иконки)

Лучше **Figma** для цифр. CapCut только если нужны 3D иконки скорости/км.

---

# BATCH 4 — лучше в Figma (НЕ обязательный CapCut)

Эти можно **не** гонять в CapCut — сверстать в Figma:

- H07 / H08 — «Всегда» гео-инструкция  
- H09 layout empty (календарь уже H14_B)  
- H25 notification rows UI  
- H03–H05 line tips (если не хотите 3D)

Промпты CapCut для них **не обязательны**.

---

# Чеклист качества перед сдачей

- [ ] Нет логотипа / названия Life360  
- [ ] Пин/акцент **золото**, не фиолетовый бренд  
- [ ] Размер px = таблица  
- [ ] Прозрачный фон где указано  
- [ ] Объект не обрезан краями  
- [ ] Имя файла = Out из промпта  
