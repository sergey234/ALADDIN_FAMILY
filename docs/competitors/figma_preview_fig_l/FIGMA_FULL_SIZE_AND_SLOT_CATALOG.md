# Полный каталог Figma FIG-L + Icons — размеры и куда вставляем

**Файл:** `b6gFc8GUtWC6ncPgb6X6II` · **Локально:** эта папка + `freeze_2026-11-11_clay_blue_disc/`  
**Дата:** 2026-11-11 · **App icons выбор:** Clay + G1 · disc `#2E5BFF`  
**Не только G1** — ниже **всё**, что нарисовали.

Канон хаба Where: phone **393×852** · tab **64** · chip **56×56** · FAB **48** · pin **52–56** · sheet radius **20** · H-pad **16** (UNIFIED §10.2).

---

## 0. Сохранено?

| Слой | Да/нет |
|------|--------|
| Figma pages 00–07 | ✅ |
| Local PNG 01–09 + V1–V3 + Clay_G1–G3 | ✅ |
| Freeze snapshot | ✅ |
| Этот каталог размеров | ✅ |

---

## 1. Page `01` — Hub skeleton

| ID / node | Figma size | Куда в приложении | UI slot |
|-----------|------------|-------------------|---------|
| **FIG-L34** `5:2` LocationSheetFull | **393×852** | WhereIsPhone full screen ref | canvas phone |
| **FIG-L15** `5:63` HubTabBar | **393×64** | нижние 4 таба Where | bar h **64** · icon ~**30** circle |
| **FIG-L25** `5:81` SheetSectionChips | **320×72** | чипы Семья/Питомцы/… | chip **56×56** gap **10** |

**Export:** L34 = full screen ref (не xcasset icon). L15/L25 = component PDF + PNG @2x/@3x иконок табов/чипов.

---

## 2. Page `02` — Pin + FAB

| ID | Figma size | Куда | UI slot |
|----|------------|------|---------|
| **FIG-L01** MapPinBattery `41:4` | **120×140** | map member pin | pin **52–56** pt |
| **FIG-L03** FABStack `41:16` | **64×228** | 4 FAB справа | каждая кнопка **48** |

Board preview: `41:2` 720×520 · local `05_Batch2_PinFAB.png`

---

## 3. Page `03` — Bubble / Member / Map type

| ID | Figma size | Куда | UI slot |
|----|------------|------|---------|
| **FIG-L02** LastSeenBubble `59:4` | **220×56** | bubble над pin | max width ~220 · h ~56 |
| **FIG-L04** MemberSheetHero `59:9` | **361×220** | верх member sheet | width content ~361 (pad 16) |
| **FIG-L12** MapTypeThumbs `59:20` | **320×140** | 3 thumbs Авто/Улицы/Спутник | thumb **96×96** (подпись в Figma) |

Board: `59:2` 980×640 · local `06_Batch3.png`

---

## 4. Page `04` Batch4 — Places / geofence / day / share / calendar / allow

| ID | Figma size | Куда | UI / note |
|----|------------|------|-----------|
| **FIG-L17** PlacesChips `60:4` | **381×56** | чипы мест | h 56 · full width-ish |
| **FIG-L08** GeofenceCircle `60:18` | **280×280** | quiet zone на карте | overlay circle art |
| **FIG-L09** DayJournal `60:24` | **320×280** | день/маршрут sheet block | card |
| **FIG-L13** ShareLinkCard `60:42` | **320×160** | шаринг ссылки | card |
| **FIG-L16** FamilyCalendar `60:54` | **340×360** | календарь семьи | month block |
| **FIG-L18** AlwaysAllow `60:96` | **360×360** | Always Allow perm art | modal/illustration |

Board `60:2` 1100×900 · local `07_Batch4_Places.png`

---

## 5. Page `04` Batch5 — Family / brand / subscription

| ID | Figma size | Куда | UI / note |
|----|------------|------|-----------|
| **FIG-L05** EmptyMailbox `61:4` | **300×280** | empty inbox | empty illustration |
| **FIG-L06** AccessCards `61:10` | **360×252** | Full/Limited access | cards |
| **FIG-L07** ChipsRoles `61:30` | **400×140** | роли инвайта chips | chips row |
| **FIG-L14** Splash `61:46` | **220×400** | splash/brand (optional) | tall art |
| **FIG-L35** RoleModal `61:52` | **340×360** | role modal | modal |
| **FIG-L36** SubscriptionTab `61:62` | **400×420** | таб Подписка → Tariffs | tab content |

Board `61:2` 1200×980 · local `08_Batch5_Family.png`

---

## 6. Page `04` Batch6 — Safety / soon / driving / places list

| ID | Figma size | Куда | UI / note |
|----|------------|------|-----------|
| **FIG-L10** SOSHold `62:4` | **200×240** | SOS hold | circle visual · hold logic keep · ~56+ bar → big circle |
| **FIG-L11** CrashTipRow `62:10` | **360×120** | crash tip row | row |
| **FIG-L19** TagsSoon `62:22` | **220×160** | Tile soon | empty soon |
| **FIG-L20** EvacSoon `62:28` | **220×160** | Evac soon | empty soon |
| **FIG-L21** PetSoonRow `62:34` | **250×64** | pet soon row | row h 64 |
| **FIG-L22** DrivingSoon `62:40` | **280×160** | driving empty/teaser | card |
| **FIG-L23** PinPreview `62:45` | **280×160** | pin preview | card |
| **FIG-L24** RoutesSheet `62:51` | **300×200** | routes sheet block | card |
| **FIG-L26** FamilySoftPaywall `62:60` | **340×240** | soft paywall | card |
| **FIG-L27** PetsSoon `62:72` | **240×160** | pets empty | empty |
| **FIG-L28** ItemsSoon `62:76` | **240×160** | items empty | empty |
| **FIG-L29** PetWizard `62:80` | **360×220** | pet wizard | card |
| **FIG-L30** DrivingWeekly `62:92` | **340×200** | driving weekly | card |
| **FIG-L31** SafetyTab `62:104` | **340×200** | Safety tab 2 cards | tab |
| **FIG-L32** PlacesList `62:112` | **300×220** | places list | list card |
| **FIG-L33** CreateEvent `62:123` | **320×260** | create event | form card |

Board `62:2` 1400×1600 · local `09_Batch6_Safety.png`

---

## 7. Page `05` — Kaspersky gaps (двери Проверить / Ребёнок)

| ID | Figma size | Куда |
|----|------------|------|
| FIG-01 CalmCall Hero `67:2` | **393×852** | Antifake / спокойный звонок screen |
| FIG-02 CallDirectory Steps `67:17` | **393×852** | Call Directory 5 steps |
| FIG-03 ShieldON Status `67:45` | **320×320** | status widget / hub |
| FIG-04 EmptyLists `67:54` | **393×852** | empty lists |
| FIG-05 ChildOverview Empty `67:74` | **393×852** | дверь Ребёнок empty |
| FIG-06 AvatarGrid AddChild `67:92` | **393×852** | add child avatars |
| FIG-07 InviteQR Share `67:121` | **393×852** | invite QR |
| FIG-08 InviteWaiting `67:157` | **393×852** | waiting |
| FIG-13 ContentCategories `68:2` | **393×852** | категории светофор |
| FIG-14 AntiBanner `68:42` | **393×852** | Анти-Баннер |
| FIG-15 HomeNetwork Empty `68:58` | **393×852** | Дом/сеть |
| FIG-16 SafeQR `68:74` | **393×852** | Safe QR |
| FIG-17 SocialConnect Empty `68:100` | **393×852** | соцсеть empty |
| FIG-REUSE Legend `68:112` | **393×520** | карта reuse (не UI) |

**Export:** full-screen refs @2x/@3x или PDF; FIG-03 как **320** status asset.

Reuse (не рисовали): FIG-09→L01 · 11→L18 · 18→L10/11 · 19→L19 · 20→L20 · 10→L17/L32 · 21→L36.

---

## 8. Page `06` — Alive Icons (ранний набор, до G1)

Мастера → UI leading **28–32** (door large **40** ok) · empty illust ~**160** wide.

| Component | Figma tile | Куда |
|-----------|------------|------|
| ICON-DOOR-Verify/Child/WhereFamily | **120×148** | SimpleHome двери (см. также G1 A07–A09) |
| ICON-AF-* (Call/Link/QR/Banner/ShieldON) | **96×124** | Antifake hub rows |
| ICON-PR-* (Limits/Content/Rewards/Screen) | **96×124** | Parental / Ребёнок |
| ICON-FAM-* (Members/Chat/Groups/Invite) | **96×124** | FamilyScreen cards |
| ICON-HOME-* (Family/AccessFull/Limited) | **96×124** | SimpleHome secondary |
| ICON-TAR-* (Free/Family/Trial) | **96×124** | Tariffs (**Premium** → G1 A06) |
| ICON-EMPTY-* (Mailbox/Pets/Items/Tile/Evac) | **96×124** | empty states |

Board `64:222` 1200×980 · local `01_Alive_Icons.png`  
**При wire предпочитать G1** для Main/tabs/дверей; Alive 06 — запас / внутренние AF/PR/FAM/EMPTY.

---

## 9. Page `07` — Variants + Clay G1/G2/G3

| Board | Size | Назначение |
|-------|------|------------|
| V1_Clay_Board | 1480×520 | выбор оболочки ✅ Clay |
| V2_Glass_Board | 1480×520 | архив |
| V3_Emboss_Board | 1480×520 | архив |
| **Clay_G1_Board** | 1480×560 | **LOCK** · 12× `G1_*` **112×148** · disc `#2E5BFF` |
| **Clay_G1_Black_Board** `137:2` | 1480×560 | A/B · 12× `G1B_*` · disc `#0F172A` |
| Clay_G2_Board | 1480×560 | альтернативные фигуры (архив выбора) |
| Clay_G3_Board | 1480×560 | ещё метафоры (архив) |

**Слоты UI для G1** — `G1_SIZE_SLOT_MATRIX.md`.  
**План 100% одна строка = один asset:** `PLAN_100_PERCENT_ASSET_ROWS.md`.

---

## 10. План вставки (порядок wire, без путаницы)

1. **Where hub:** L15 tabs · L25 chips · L03 FAB · L01 pin · (L34 = layout ref)  
2. **Where extras:** L02 bubble · L12 thumbs · L08 circle · L09/L16/L17… по GO WIRE-*  
3. **Main + SimpleHome chrome:** **G1** A01–A12 (синий disc) + later black A/B  
4. **Antifake / Child screens:** Kaspersky FIG-01… + Alive AF/PR  
5. **Family / Tariffs / Empty:** Alive FAM/TAR/EMPTY + L36  
6. **Safety/soon:** Batch6 L10–L33  

Превью в приложении: `aliveBlue` → `aliveBlack` → `legacy` (`FREEZE_AND_ROLLBACK.md`).

---

## 11. Чеклист «ничего не забыли из Figma»

- [x] 00 Spec  
- [x] 01 L34+L15+L25  
- [x] 02 L01+L03  
- [x] 03 L02+L04+L12  
- [x] 04 Batch4 L17/L08/L09/L13/L16/L18  
- [x] 04 Batch5 L05/L06/L07/L14/L35/L36  
- [x] 04 Batch6 L10–L33  
- [x] 05 Kaspersky 01–08, 13–17 + REUSE  
- [x] 06 Alive icon set (27)  
- [x] 07 V1–V3 + G1–G3 + **G1 Black**  
- [x] Local PNG + freeze  
- [x] Black-disc G1  
- [x] План 100% строк (`PLAN_100_PERCENT_ASSET_ROWS.md`)  
- [ ] Export xcassets — после Approve плана + GO  
- [ ] Wire + flag + device QA  

**Конец каталога.** Детали слотов → `G1_SIZE_SLOT_MATRIX.md` · полный 1:1 → `PLAN_100_PERCENT_ASSET_ROWS.md`.  
