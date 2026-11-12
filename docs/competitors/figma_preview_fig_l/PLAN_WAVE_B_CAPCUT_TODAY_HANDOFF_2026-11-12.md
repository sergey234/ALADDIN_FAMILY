# Wave B CapCut → iOS — хэндофф за сессию 2026-11-11…12

**Verified 2026-11-12 ~11:15 Asia/Dubai:** imagesets ×14 в `Assets.xcassets` · wire Swift совпадает · READY PNG на месте · ветка `master` · strings SOS/pets/family RU+EN OK.

**Для другой ML-системы:** этот файл = SSOT «что сделали в той сессии». Не OB_*. Не bot. Не bump/push без GO владельца. Сборка Xcode — только после фразы владельца «GO на сборку».

| Поле | Значение |
|------|----------|
| Repo root | `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS` |
| Ветка | только **`master`** для iOS-коммитов |
| Канон Wave B | `docs/competitors/figma_preview_fig_l/PLAN_LIFE360_HERO_ART_WAVE_2026-11-11.md` |
| CapCut pack | `~/Downloads/ALADDIN_CapCut_Hero_Wave_B_2026-11-11/` |
| READY PNG | `~/Downloads/ALADDIN_CapCut_READY/` |
| Промпты | `…/KAPCUT_PROMPTY_V2_TOP.md` · папки `PO_PAPKAM_CAPCUT_01_23/NN_*` |
| Бренд | золото `#F59E0B` + storm (не Life360 purple) |
| Стекло UI | `aladdinProductCard` в коде — **не** печь в PNG |
| SOS hold | логика 3с **не менять**; illust SOS на картинке 11 = **красная** (канон владельца) |

---

## 0. Ритуал пайплайна (как делали каждую картинку)

1. Владелец кидает JPG из CapCut (часто белый фон, watermark CapCut AI).
2. Агент копирует в `ALADDIN_CapCut_READY/JOBnn_*_white_bg.jpg` + папку `PO_PAPKAM_CAPCUT_01_23/NN_*`.
3. Pillow: flood-fill белого с краёв → RGBA (для стикеров/изолированных объектов).  
   **Исключение:** family heroes JOB08–09 — **карту/abstract bg оставляем** (`SIZES.md`: soft map bg OK).
4. Fit в канон export (см. таблицу размеров) + лёгкий scrub watermark TL.
5. Imageset в `Assets.xcassets/ICON_ALIVE_HERO_*` @1x/@2x/@3x.
6. Wire SwiftUI слот + строки в `Resources/Localization/{ru,en}.lproj/Localizable.strings` (не rewrite `LocalizationManager.swift`).
7. Превью dark: `PREVIEW_JOB*_*.jpg` в READY.
8. **Не** `xcodebuild` без GO.

CLI Python: системный `python3` + Pillow OK для локальной обработки ассетов (не путать с repowise venv).

---

## 1. Таблица размеров (канон CapCut V2)

| JOB | Тема | UI pt | Export px | Alpha |
|-----|------|-------|-----------|-------|
| 01 | Place land pin | 120×120 | 360×360 | transparent |
| 02 / 10 | Calendar+pencil | 96×96 | 288×288 | transparent |
| 03 | SUV | 112×112 | 336×336 | transparent |
| 04 | Gold lock | 140×140 | 420×420 | transparent |
| 05–07 | Pet stickers | 88×88 (picker) / dog hero 120 | 264×264 | transparent |
| 08–09 | Family / hug | 320×220 | 960×660 | **map bg keep** |
| 11–12 | SOS tips | ~280×200 | 840×600 | transparent OK |

Источник размеров: `~/Downloads/…/export_targets/SIZES.md` + `KAPCUT_PROMPTY_V2_TOP.md`.

---

## 2. Что сделали сегодня (JOB → Assets → UI)

### JOB01 — Place land pin ✅
- **Asset:** `ICON_ALIVE_HERO_H14_PlaceLandPin`
- **Wire:** `WhereIsPhoneScreen.placesHeroLandPinRow` · Places chip · 120×120
- **READY:** `ALADDIN_01_PlaceLandPin_360.png`

### JOB02 — Calendar+pencil ✅
- **Asset:** `ICON_ALIVE_HERO_H14_CalendarPencil`
- **Wire:** `eventsHeroCalendarRow` · Events chip · 96×96
- **READY:** `ALADDIN_02_CalendarPencil_288.png`

### JOB03 — две машинки ✅
- **Assets:** `ICON_ALIVE_HERO_H18_SUV_Gold` · `ICON_ALIVE_HERO_H18_SUV_Red`
- **Wire:** Gold → `DrivingReportsModal.drivingHeroSUVRow` **112** · Red → `memberWeeklyTripsCard` **96**
- **READY:** `ALADDIN_03_SUV_{Gold,Red}_336.png`
- Третья машинка **не нужна** (H16 = замок, не car).

### JOB04 — замок H16 ✅
- **Asset:** `ICON_ALIVE_HERO_H16_GoldLock`
- **Wire:** Driving weekly locked CTA **140** · member drive unlock **96**
- **READY:** `ALADDIN_04_GoldLock_420.png`

### JOB05–07 — петы ✅
- **Assets:** `ICON_ALIVE_HERO_H15_PetDog` · `PetCat` · `PetOther`
- **Wire:** Pets hero dog **120** · Wizard type picker **88×3** · list thumb по `FamilyPetProfile.kind`
- **Модель:** `FamilyPetProfile.kind` (`dog`/`cat`/`other`) + `heroAssetName` в `FamilySafetyRemainderHub.swift`
- **READY:** `ALADDIN_05_PetDog_264.png` · `06_PetCat` · `07_PetOther`
- Собака: соло JPG; кот/выдра: crop с листа 3-в-1 (flood, не убивать cream морду).

### JOB08 — семья на карте (2 варианта) ✅
- **Assets:** `ICON_ALIVE_HERO_H17_FamilyWalk` · `FamilyKneel`
- **Wire:** Walk → People chip hero **320×220** · Kneel → `softInviteSheet`
- **READY:** `ALADDIN_08_FamilyHero_{Walk,Kneel}_960x660.png` · `JOB08_VYBOR.md`
- Map bg **сохранён**.

### JOB09 — family hug (2 варианта) ✅
- **Assets:** `ICON_ALIVE_HERO_H25_FamilyHugStand` · `FamilyHugKneel`
- **Wire:** Stand → `alwaysAllowSheet` · Kneel → `FamilyGroupsModal` hero
- **READY:** `ALADDIN_09_FamilyHug_{Stand,Kneel}_960x660.png` · `JOB09_VYBOR.md`

### JOB10 — календарь ❌ не вставлять
- Дубль JOB02 (тот же 96/288 calendar+pencil). Events уже закрыт JOB02. Папка `10_EventsCalendar` = закрыта через 02.

### JOB11 — SOS intro H06 ✅ (исправлено)
- **Asset:** `ICON_ALIVE_HERO_H06_SOSIntro`
- **Illust SOS button:** **красная** (владелец; gold-recolor отменён)
- **Wire:** Safety · pager page 0 · `safetySOSEducationCarousel`
- **Копирайт (RU/EN в strings, на экране без сырых ключей):**
  - Title: «Кнопка «SOS» в ALADDIN пригодится, если вы в беде» / EN аналог
  - Bullets: темная улица · рядом с опасностью · срочно нужна медпомощь
  - CTA: «К удержанию SOS»
- Реф Life360: `refs/L360_H06.jpg` — бренд Life360 в тексте **заменён** на ALADDIN; «перестрелка» → «опасность».

### JOB12 — SOS release H13 ✅
- **Asset:** `ICON_ALIVE_HERO_H13_SOSRelease`
- **Wire:** Safety · pager page 1
- **Копирайт:** «Отпустите кнопку, чтобы беззвучно оповестить членов семьи и экстренные контакты» + «Понятно» / EN
- Реф: `refs/L360_H13.jpg` («круг» → «семья»).

**Hold 3с / `FamilySOSHoldButton`:** не менять логику. Цвет круга hold в коде сейчас `secondaryGold` — отдельно от illust; менять на red только по явному GO.

---

## 3. Ключевые файлы кода (взаимосвязи)

| Файл | Роль |
|------|------|
| `Screens/WhereIsPhoneScreen.swift` | Places/Events/Pets/People heroes · Safety SOS pager · soft invite · always allow · member weekly/unlock |
| `Shared/Components/Modals/DrivingReportsModal.swift` | Driving gold SUV hero · lock paywall 140 |
| `Screens/FamilySafetyRemainderHub.swift` | `FamilyPetProfile` + `FamilyPetWizardSheet` picker · `FamilySOSHoldButton` |
| `Screens/FamilyGroupsModal.swift` | Hug kneel hero |
| `Shared/Components/StormGlassCardStyle.swift` | `aladdinProductCard` |
| `Resources/Localization/ru.lproj/Localizable.strings` | RU copy |
| `Resources/Localization/en.lproj/Localizable.strings` | EN copy |
| `Assets.xcassets/ICON_ALIVE_HERO_*` | все imagesets Wave B сегодня |

**Не трогать без ТЗ:** `Screens/14_OnboardingScreen.swift` / OB_* Figma · pin/chips QR policy · parental bypass mock · `telegram_stars_shop_bot/`.

---

## 4. Карта Assets (имена для Image("…"))

```
ICON_ALIVE_HERO_H14_PlaceLandPin
ICON_ALIVE_HERO_H14_CalendarPencil
ICON_ALIVE_HERO_H18_SUV_Gold
ICON_ALIVE_HERO_H18_SUV_Red
ICON_ALIVE_HERO_H16_GoldLock
ICON_ALIVE_HERO_H15_PetDog
ICON_ALIVE_HERO_H15_PetCat
ICON_ALIVE_HERO_H15_PetOther
ICON_ALIVE_HERO_H17_FamilyWalk
ICON_ALIVE_HERO_H17_FamilyKneel
ICON_ALIVE_HERO_H25_FamilyHugStand
ICON_ALIVE_HERO_H25_FamilyHugKneel
ICON_ALIVE_HERO_H06_SOSIntro          ← красная SOS на телефоне
ICON_ALIVE_HERO_H13_SOSRelease
```

---

## 5. Локализация SOS education (технические ключи → смысл)

Пользователь на экране видит **только строки**, не ключи.

| Key | RU (смысл) | EN |
|-----|------------|-----|
| `sos_edu_nav_title` | SOS | SOS |
| `sos_edu_intro_title` | Кнопка «SOS» в ALADDIN пригодится, если вы в беде | The SOS button in ALADDIN helps when you’re in trouble |
| `sos_edu_intro_bullet_1` | Идете в одиночку по темной улице | Walking alone on a dark street |
| `sos_edu_intro_bullet_2` | Оказались рядом с опасностью | You’re near danger |
| `sos_edu_intro_bullet_3` | Срочно нужна медицинская помощь | You urgently need medical help |
| `sos_edu_intro_cta` | К удержанию SOS | Go to SOS hold |
| `sos_edu_release_title` | Отпустите кнопку… семья и экстренные контакты | Release the button… family and emergency contacts |
| `sos_edu_release_cta` | Понятно | Got it |

Pets/Family hero keys: `where_phone_pets_hero_*` · `where_phone_family_hero_*` · `pet_type_*`.

---

## 6. Откуда брать исходники

| Что | Путь |
|-----|------|
| CapCut upload folders 01–23 | `~/Downloads/ALADDIN_CapCut_Hero_Wave_B_2026-11-11/PO_PAPKAM_CAPCUT_01_23/` |
| Life360 refs | `…/refs/L360_H*.jpg` |
| Готовые PNG + preview | `~/Downloads/ALADDIN_CapCut_READY/` |
| Cursor inbox JPG от владельца | `~/.cursor/projects/…/assets/*.jpg` (копировать в READY, не оставлять только там) |
| Выбор вариантов | `JOB08_VYBOR.md` · `JOB09_VYBOR.md` в READY |

---

## 7. Что осталось (следующей ML / владельцу)

| # | Задача | Статус |
|---|--------|--------|
| A | CapCut JOB13 Invite OG — см. **§11** ниже (C/B/A + фазы) | ⏳ план готов, wire по GO |
| A2 | CapCut JOB14+ (speedometer, ASC, dog hero 17, …) | ⏳ не начинали |
| B | Полный SOS carousel H07–H12 mid tips (сейчас только intro+release = 2 слайда) | ⏳ по GO |
| C | Owner Device QA: Places / Events / Driving / Pets / People / Groups / Always Allow / Safety pager | ⏳ без agent xcodebuild |
| D | Цвет **live** `FamilySOSHoldButton` (сейчас gold в коде) ↔ красный illust — согласовать с владельцем | ⏳ спросить |
| E | Commit на `master` + bump — только явный GO | ⏳ |
| F | OB-QA / DEV-88 / bump 20 | ⏳ старые open items Wave A |
| G | Не коммитить `telegram_stars_shop_bot/` · `.env` · VPN secrets handoff | инвариант |

---

## 8. QA чеклист (владелец, симулятор после GO)

1. Places → pin 120, без белого квадрата.  
2. Events → calendar 96.  
3. Driving → gold SUV 112; без тарифа → lock 140.  
4. Member sheet → red car 96 · unlock lock 96.  
5. Pets → dog hero; Add → dog/cat/other 88.  
6. People → family walk 320×220.  
7. Soft invite → kneel family.  
8. Always Allow → hug stand.  
9. Groups → hug kneel.  
10. Safety → pager 2 стр: intro (bullets) + release; SOS illust **красная**; hold 3с работает.  
11. Reduce Motion / chips Classic — без регрессий.

---

## 9. Запреты (не ломать)

- Onboarding OB_00…07 Figma / hero PNG pipeline.  
- Mock parental / `sfm_mock`.  
- Bot в iOS release commit.  
- Полный rewrite `LocalizationManager.swift`.  
- `xcodebuild` / Simulator / push без GO.

---

## 10. Короткий алгоритм для следующей картинки CapCut

```
1. Открыть KAPCUT_PROMPTY_V2_TOP.md → номер JOB → UI/export size
2. Взять JPG владельца → READY + PO_PAPKAM folder
3. Alpha (или keep map bg для family)
4. Imageset ICON_ALIVE_HERO_*
5. Найти слот в PLAN_LIFE360_HERO_ART_WAVE + WhereIsPhone / Modal
6. Strings RU+EN точечно
7. Accessibility id
8. Отчёт: таблица слой|size|asset|screen · Figma upload N/A для Wave B CapCut
9. Стоп → ждать GO на сборку
```

---

## 11. JOB13 Invite OG — разбор Life360 + план действий (2026-11-12)

### 11.1 Как у Life360 (скрин Telegram)

При шаре ссылки мессенджер тянет **Open Graph** с короткого URL (`i.lf360.co/…`):

| Слой | Life360 |
|------|---------|
| Текст сообщения | «Присоединяйся… Код…» + URL |
| Карточка | domain · title · description |
| Hero **1200×630-класс** | глобус + **пин с фото приглашающего** (+ логотип в углу) |

Фото в пине **не** зашито в CapCut навсегда — это **динамический композит** (шаблон + avatar пользователя) на стороне link-preview.

### 11.2 Как у ALADDIN сейчас (факт)

| Есть | Нет |
|------|-----|
| Share: текст + `https://aladdin-ai.ru/family/invite/{FAM-code}` (`RecoveryCodeModal` / family invite share) | **`og:image` / `og:title` на `landing/family-invite.html`** → Telegram часто **без** красивой карточки |
| Deep link `aladdin://family/invite?code=` | Серверный render PNG с фото приглашающего |
| На карте уже avatar-in-pin: `FamilyHubAvatarPinView` + `ProfileImageManager` | In-app invite preview card с глобусом JOB13 |

### 11.3 Три CapCut кадра JOB13 → роли (канон)

| ID | Кадр | Роль | Размер |
|----|------|------|--------|
| **C** | Глобус + золотой пин + **пустой/белый центр** | **Основной шаблон** под фото | Export **1200×630** |
| **B** | Глобус + пин + **силуэт** | Fallback без фото / статичный OG v1 | **1200×630** |
| **A** | Глобус + **2 пина** + линия | In-app beauty («семья на связи»), **не** OG | UI ~320×168 (тот же 1.91:1) |

Рекомендация владельцу подтверждена: **C = основной · B = fallback · A = второй in-app hero**.

Фото приглашающего: **runtime overlay** из `ProfileImageManager.shared.loadProfileImage(for: .main)` в круг центра пина C (как Life360). Не генерить CapCut на каждого юзера.

### 11.4 Куда вставлять

| Приоритет | Место | Кадр | Механика |
|-----------|--------|------|----------|
| P0 | Share preview **в приложении** перед/в `UIActivityViewController` | C+фото | SwiftUI/`UIGraphicsImageRenderer` композит |
| P0 | Assets шаблоны | C, B, A | `ICON_ALIVE_HERO_H20_*` |
| P1 | `landing/family-invite.html` | сначала **B** статично | meta `og:image` / `og:title` / `og:description` ALADDIN |
| P2 | Настоящий Telegram/WhatsApp OG с **личностью** | C+фото | **Сервер** endpoint (нужен GO) — без этого crawler не увидит аватар с телефона |
| P3 | People inviteBanner / soft invite | A или C | опционально; soft invite уже JOB08 Kneel — не дублировать без GO |
| — | OB_* | — | запрет |

### 11.5 Фазы работ (порядок)

**Фаза 0 — ассеты (iOS, без сервера)**  
1. Сохранить A/B/C JPG → READY `13_InviteOG/` · fit **1200×630**.  
2. Imagesets: `ICON_ALIVE_HERO_H20_InviteOG_EmptyPin` (C) · `_Silhouette` (B) · `_TwoPins` (A).  
3. Замерить центр пина на C (нормализованный CGRect) → константа для маски аватара.

**Фаза 1 — in-app Life360-like preview (рекомендуемый первый ship)**  
4. Компонент `InviteOGComposeView` / renderer: фон C + circular avatar + fallback B.  
5. Встроить в family invite share UI (`RecoveryCodeModal` / invite share sheet): карточка «как будет выглядеть» + share text/link.  
6. Опционально `LPLinkMetadata` / кастомный item для share sheet (iOS), чтобы в системном share тоже была картинка.  
7. Copy RU/EN: title/description в духе ALADDIN (не Life360), код FAM в тексте как сейчас.

**Фаза 2 — статичный web OG (landing, отдельный GO на деплой сайта)**  
8. Положить `og-invite-default-1200x630.png` (B) на CDN/сайт.  
9. В `family-invite.html` добавить:
   - `og:title` = «Приглашение в семью ALADDIN»
   - `og:description` = коротко про карту семьи
   - `og:image` = абсолютный URL 1200×630
   - `twitter:card` = `summary_large_image`  
10. Проверить Telegram → «Отправить себе» / link preview.

**Фаза 3 — динамический OG как Life360 (backend GO обязателен)**  
11. Endpoint вида `GET /family/invite/{code}/og.jpg` или query `?v=` на aladdin-ai.ru.  
12. Сервер: шаблон C + avatar (из профиля owner семьи / upload при create invite) → JPEG 1200×630.  
13. `og:image` указывает на этот URL.  
14. Кэш + TTL; без секретов в URL; rate limit.  
15. Без этого **невозможно** полностью повторить Telegram-карточку Life360 только из iOS.

### 11.6 Что НЕ делать

- Не печь чужие лица / Life360 logo в PNG.  
- Не путать A (2 пина) с OG 1200×630 primary.  
- Не ждать Phase 3, чтобы закрыть Wave B beauty — Phase 0–1 дают UX в приложении сразу.  
- Не деплоить landing/API без GO владельца (`ask-before-important-ops`).

### 11.7 Definition of Done (по фазам)

| Фаза | Done |
|------|------|
| 0 | 3 PNG 1200×630 + imagesets + pin center rect задокументирован |
| 1 | Share sheet показывает глобус+пин+фото приглашающего; fallback силуэт |
| 2 | Telegram на `aladdin-ai.ru/family/invite/…` показывает карточку со статичным OG |
| 3 | Карточка в Telegram с **реальным** фото owner (как Life360) |

**Владельцу выбрать GO:** `JOB13-F0` · `JOB13-F0+F1` · `JOB13-F2` (site) · `JOB13-F3` (server).

### 11.8 Статус реализации (код готов, деплой ждёт GO)

| Слой | Статус | Где |
|------|--------|-----|
| 1 Deep link `…/family/invite/{FAM}` | ✅ как было | `FamilyInviteShareModal.inviteLink` |
| 2 Meta title/desc/og:image/twitter | ✅ в репо | `landing/family-invite.html` |
| 3 C+avatar JPEG (Life360) | ✅ in-app compose + upload | `InviteOGComposer` → `POST /api/family/invite/og.jpg` |
| 4 Fallback B | ✅ | assets H20 Silhouette + default JPG в `landing/og/` |
| 5 In-app preview при шаре | ✅ | `InviteOGPreviewCard` + JPEG в `ShareSheet` |

**Код (локально, без prod):**
- Assets `ICON_ALIVE_HERO_H20_InviteOG_{EmptyPin,Silhouette,TwoPins}`
- `Shared/Components/InviteOGComposer.swift` (+ pbxproj)
- `FamilyInviteShareModal` preview + share JPEG + best-effort upload
- `app/routers/family_invite_og.py` + mount в `main.py`
- `landing/og/*` + `landing/og/README_INVITE_OG.md`

**Выкат 2026-11-12 (GO владельца получен):**
1. ✅ **site** — `/var/www/aladdin-ai.ru/family-invite.html` + `/og/*.jpg` · nginx `location ^~ /family/invite` → `https://aladdin-ai.ru/family/invite/FAM-…` отдаёт meta OG (карточка B).
2. ✅ **API** — `family_invite_og` на 🇷🇺 MAIN FirstVDS (`…180`):8002 · `GET/POST /api/family/invite/og.jpg` · dir `/og/family-invite/`.
3. ⏳ Сборка / Device QA — владелец сам в конце (**без agent xcodebuild**).

### 11.9 ASC Top-3 (H01 / H03 / H21) — 2026-11-12

| Shot | Файл 1290×2796 | Заголовок снаружи |
|------|----------------|-------------------|
| H01 | `docs/AppStore/asc_screenshots_wave_b_2026-11-12/ALADDIN_ASC_H01_MomHome_*` | Узнайте, где сейчас ваши близкие |
| H03 | `…/ALADDIN_ASC_H03_MariaSection_*` | Узнайте, когда близкие на месте |
| H21 | `…/ALADDIN_ASC_H21_DrivingSpeed_*` | Семья в пути — спокойнее за рулём |

Готово RU+EN · navy/gold · не purple · не in-app Where chrome. Copy: `ASC_TOP3_COPY_RU_EN.md`.

### 11.10 ASC H22–H24 — map-path phone pack (GO 2026-11-12)

| Shot | Смысл | Файл |
|------|-------|------|
| H22 | Круг семьи · 4 пина · путь | `ALADDIN_ASC_H22_FamilyCircle_MapPath_*` |
| H23 | Lifestyle sunset · 3 пина | `ALADDIN_ASC_H23_FamilySunset_LiveMap_*` |
| H24 | Путь + машина · Driving | `ALADDIN_ASC_H24_DrivingPath_Bubble_*` |

Папка та же: `docs/AppStore/asc_screenshots_wave_b_2026-11-12/` · copy `ASC_H22_H24_COPY_RU_EN.md`.  
In-app tip D/E — отдельно по GO (crop ~361×220). Не OB_* · не замена H20 OG.

---

**Конец хэндоффа 2026-11-12 (+ §11 JOB13).** Следующий CapCut после JOB13: JOB14 speedometer / ASC по GO.

### 11.11 ASC H25–H26 — Driving History (GO 2026-11-12)

| Shot | Смысл | Файл |
|------|-------|------|
| H25 | Список поездок · км/мин | `ALADDIN_ASC_H25_DrivingTrips_List_*` |
| H26 | День · таймлайн остановок | `ALADDIN_ASC_H26_DayTimeline_Route_*` |

- Repo: `docs/AppStore/asc_screenshots_wave_b_2026-11-12/`
- READY: `READY/18_ASC_DrivingHistory/`
- Finder Downloads: `~/Downloads/ALADDIN_ASC_H25_H26_DrivingHistory/` · полный пакет `~/Downloads/ALADDIN_ASC_WaveB_All/`
- In-app feature: **Where → Езда → отчёты** (`DrivingReportsModal`). Tip crop — later GO.

