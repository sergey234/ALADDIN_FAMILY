# План 100% — одна строка = один asset (всё из Figma + очередь P-MAIN)

**Дата:** 2026-11-11  
**Правило владельца:** до export — план без дыр. Export только после Approve этого файла + `GO export-icons-preview`.  
**Figma:** `b6gFc8GUtWC6ncPgb6X6II`  
**Откат:** tag `pre-alive-icons-2026-11-11` · flag `legacy` / `aliveBlue` / `aliveBlack`  
**Не трогать:** OB_* · Companion · VPN product icons · purple

Легенда статуса art:  
✅ нарисовано · ⏳ очередь (ещё нет в Figma) · 📎 reuse другого ID · ⛔ вне scope

---

## 0. Сводка покрытия

| Набор | Строк | Art | Детализация 1:1 |
|-------|------:|-----|-----------------|
| G1 blue A01–A12 | 12 | ✅ | ✅ |
| G1 black G1B A01–A12 | 12 | ✅ | ✅ |
| Alive page 06 | 27 | ✅ | ✅ (ниже §2) |
| FIG-L L01–L36 | 36 | ✅ | ✅ (§3) |
| Kaspersky FIG masters | 13+REUSE | ✅ | ✅ (§4) |
| P-MAIN доп. (не в G1) | 8 | ⏳ | ✅ план слотов (§5) |
| P-DOORS extras / P-TARIFF Personal | 4 | ⏳ | ✅ план (§5) |
| V2/V3 shells | архив | ✅ | не export (выбран Clay) |
| G2/G3 glyphs | архив | ✅ | не export (выбран G1) |

**Export wave 1 (после GO):** только §1 G1 blue+black (+ опц. Alive §2 если wire тот же пакет).  
FIG-L / Kaspersky — отдельные GO пакетами.

---

## 1. G1 Clay — Main / SimpleHome / Where chrome

Мастер Figma: **112×148** · disc Ø64  
Blue board `133:92` · Black board `137:2`

| # | Asset Blue | Asset Black | Figma Blue | Figma Black | Экран | Слот | UI pt | @2x | @3x | Art |
|---|------------|-------------|------------|-------------|-------|------|-------|-----|-----|-----|
| 1 | `ICON_G1_A01_Profile_Blue` | `…_Black` | `G1_A01_bust` | `G1B_A01_bust` | Main top-right | gold circle | 22–24 / hit 36–40 | 48·80 | 72·120 | ✅ |
| 1b | same asset | same | same | same | Main tab Профиль | tab | 20–22 | 44 | 66 | ✅ |
| 2 | `ICON_G1_A02_Notif_Blue` | `…_Black` | `G1_A02_bell` | `G1B_A02_bell` | Main tab Уведомления | tab | 20–22 | 44 | 66 | ✅ |
| 3 | `ICON_G1_A03_Devices_Blue` | `…_Black` | `G1_A03_phone` | `G1B_A03_phone` | Main tab Устройства | tab | 20–22 | 44 | 66 | ✅ |
| 4 | `ICON_G1_A04_Protect_Blue` | `…_Black` | `G1_A04_shield` | `G1B_A04_shield` | Main плитка Защита | tile | 28 · card h100 | 56 | 84 | ✅ |
| 5 | `ICON_G1_A05_Tariff_Blue` | `…_Black` | `G1_A05_diamond` | `G1B_A05_diamond` | Main плитка Тарифы | tile | 28 | 56 | 84 | ✅ |
| 6 | `ICON_G1_A06_Premium_Blue` | `…_Black` | `G1_A06_crown` | `G1B_A06_crown` | Tariffs / L36 / hub crown | tile 28 · tab 22 | 56/44 | 84/66 | ✅ |
| 7 | `ICON_G1_A07_Check_Blue` | `…_Black` | `G1_A07_search` | `G1B_A07_search` | SimpleHome дверь Проверить | leading | 28–32 (~36) | 64 | 96 | ✅ |
| 8 | `ICON_G1_A08_Child_Blue` | `…_Black` | `G1_A08_child` | `G1B_A08_child` | SimpleHome дверь Ребёнок | leading | 28–32 | 64 | 96 | ✅ |
| 9 | `ICON_G1_A09_Where_Blue` | `…_Black` | `G1_A09_pin` | `G1B_A09_pin` | SimpleHome дверь Где семья | leading | 28–32 | 64 | 96 | ✅ |
| 10 | `ICON_G1_A10_ChipFamily_Blue` | `…_Black` | `G1_A10_people` | `G1B_A10_people` | Where chip Семья L25 | chip 56 | in 56×56 | 112 | 168 | ✅ |
| 11 | `ICON_G1_A11_FabLocate_Blue` | `…_Black` | `G1_A11_radar` | `G1B_A11_radar` | Where FAB L03 | FAB 48 | ~24 in 48 | 96 | 144 | ✅ |
| 12 | `ICON_G1_A12_Kids_Blue` | `…_Black` | `G1_A12_spark` | `G1B_A12_spark` | Main tab Kids | tab | 20–22 | 44 | 66 | ✅ |

Wire chrome дверей: **G1 A07–A09**, не дублировать Alive DOOR в тот же слот (Alive DOOR = запас / illust).

---

## 2. Alive page 06 — все 27 (1 строка = 1 asset)

Мастер: двери **120×148** · остальное **96×124** · UI leading **28–32** · empty illust ~**160** wide  
Export default @2x/@3x от **квадратного** слота glyph (не от подписи): door **64×64→96×96** · list **56×56→84×84** · empty **160→320** @1x board optional.

| # | Figma component | id | Master | Экран / страница | Слот UI | UI pt | Asset name | Art | Примечание |
|---|-----------------|----|--------|------------------|---------|-------|------------|-----|------------|
| 1 | `ICON-DOOR-Verify` | `64:3` | 120×148 | SimpleHome дверь Проверить | leading | 28–32 | `ICON_ALIVE_DOOR_Verify` | ✅ | wire chrome → **G1 A07** предпочтительнее |
| 2 | `ICON-DOOR-Child` | `64:12` | 120×148 | SimpleHome дверь Ребёнок | leading | 28–32 | `ICON_ALIVE_DOOR_Child` | ✅ | → **G1 A08** |
| 3 | `ICON-DOOR-WhereFamily` | `64:20` | 120×148 | SimpleHome дверь Где семья | leading | 28–32 | `ICON_ALIVE_DOOR_Where` | ✅ | → **G1 A09** |
| 4 | `ICON-AF-Call` | `64:31` | 96×124 | Antifake hub · спокойный звонок | list leading | 28–32 | `ICON_ALIVE_AF_Call` | ✅ | + Kaspersky FIG-01 screen |
| 5 | `ICON-AF-Link` | `64:38` | 96×124 | Antifake · проверка ссылки | list leading | 28–32 | `ICON_ALIVE_AF_Link` | ✅ | |
| 6 | `ICON-AF-QR` | `64:45` | 96×124 | Antifake · Safe QR row | list leading | 28–32 | `ICON_ALIVE_AF_QR` | ✅ | + FIG-16 |
| 7 | `ICON-AF-Banner` | `64:58` | 96×124 | Antifake · Анти-Баннер | list leading | 28–32 | `ICON_ALIVE_AF_Banner` | ✅ | + FIG-14 |
| 8 | `ICON-AF-ShieldON` | `64:65` | 96×124 | Antifake · Shield ON status | list/status | 28–32 | `ICON_ALIVE_AF_ShieldON` | ✅ | + FIG-03 320 |
| 9 | `ICON-PR-Limits` | `64:72` | 96×124 | Ребёнок · лимиты | list leading | 28–32 | `ICON_ALIVE_PR_Limits` | ✅ | |
| 10 | `ICON-PR-Content` | `64:81` | 96×124 | Ребёнок · контент/категории | list leading | 28–32 | `ICON_ALIVE_PR_Content` | ✅ | + FIG-13 |
| 11 | `ICON-PR-Rewards` | `64:90` | 96×124 | Ребёнок · награды | list leading | 28–32 | `ICON_ALIVE_PR_Rewards` | ✅ | |
| 12 | `ICON-PR-ScreenTime` | `64:96` | 96×124 | Ребёнок · экранное время | list leading | 28–32 | `ICON_ALIVE_PR_ScreenTime` | ✅ | |
| 13 | `ICON-FAM-Members` | `64:104` | 96×124 | FamilyScreen · участники | card leading | 28–32 | `ICON_ALIVE_FAM_Members` | ✅ | |
| 14 | `ICON-FAM-Chat` | `64:113` | 96×124 | FamilyScreen · чат | card leading | 28–32 | `ICON_ALIVE_FAM_Chat` | ✅ | |
| 15 | `ICON-FAM-Groups` | `64:120` | 96×124 | FamilyScreen · группы | card leading | 28–32 | `ICON_ALIVE_FAM_Groups` | ✅ | |
| 16 | `ICON-FAM-Invite` | `64:127` | 96×124 | FamilyScreen · инвайт | card leading | 28–32 | `ICON_ALIVE_FAM_Invite` | ✅ | + FIG-07/08 |
| 17 | `ICON-TAR-Free` | `64:135` | 96×124 | Tariffs · Free | card/tile | 28 | `ICON_ALIVE_TAR_Free` | ✅ | |
| 18 | `ICON-TAR-Family` | `64:142` | 96×124 | Tariffs · Family | card/tile | 28 | `ICON_ALIVE_TAR_Family` | ✅ | |
| 19 | `ICON-TAR-Trial` | `64:148` | 96×124 | Tariffs · Trial | card/tile | 28 | `ICON_ALIVE_TAR_Trial` | ✅ | |
| 20 | `ICON-EMPTY-Mailbox` | `64:157` | 96×124 | Empty inbox | empty illust | ~160 wide | `ICON_ALIVE_EMPTY_Mailbox` | ✅ | + L05 |
| 21 | `ICON-EMPTY-Pets` | `64:164` | 96×124 | Pets empty/soon | empty | ~160 | `ICON_ALIVE_EMPTY_Pets` | ✅ | + L27 |
| 22 | `ICON-EMPTY-Items` | `64:174` | 96×124 | Items empty | empty | ~160 | `ICON_ALIVE_EMPTY_Items` | ✅ | + L28 |
| 23 | `ICON-EMPTY-Tile` | `64:182` | 96×124 | Tags/Tile soon | empty | ~160 | `ICON_ALIVE_EMPTY_Tile` | ✅ | + L19 |
| 24 | `ICON-EMPTY-Evac` | `64:189` | 96×124 | Evac soon | empty | ~160 | `ICON_ALIVE_EMPTY_Evac` | ✅ | + L20 |
| 25 | `ICON-HOME-Family` | `64:199` | 96×124 | SimpleHome · семья row | leading | 28–32 | `ICON_ALIVE_HOME_Family` | ✅ | |
| 26 | `ICON-HOME-AccessFull` | `64:207` | 96×124 | SimpleHome · Full access | card | 28–32 | `ICON_ALIVE_HOME_AccessFull` | ✅ | + L06 |
| 27 | `ICON-HOME-AccessLimited` | `64:215` | 96×124 | SimpleHome · Limited | card | 28–32 | `ICON_ALIVE_HOME_AccessLimited` | ✅ | + L06 |

---

## 3. FIG-L L01–L36 — каждый кадр

Канон UI Where: phone **393×852** · tab **64** · chip **56** · FAB **48** · pin **52–56** · pad **16** · radius **20**.

| ID | Figma size | Экран | Слот / роль | Asset / export | Art |
|----|------------|-------|-------------|----------------|-----|
| L34 | 393×852 | Where full | layout ref | `FIG_L34_LocationSheet` (screen) | ✅ |
| L15 | 393×64 | Where tabs | bar h64 · icon~30 | `FIG_L15_HubTabBar` + per-tab glyphs | ✅ |
| L25 | 320×72 | Where chips | 56×56 gap10 | `FIG_L25_Chips` + 5 chip assets | ✅ |
| L01 | 120×140 | map pin | pin 52–56 | `FIG_L01_MapPinBattery` | ✅ |
| L03 | 64×228 | FAB stack | each 48 | `FIG_L03_FABStack` / 4× FAB | ✅ |
| L02 | 220×56 | bubble | ~220×56 | `FIG_L02_LastSeenBubble` | ✅ |
| L04 | 361×220 | member hero | content | `FIG_L04_MemberHero` | ✅ |
| L12 | 320×140 | map type | thumb 96 | `FIG_L12_MapTypeThumbs` | ✅ |
| L17 | 381×56 | places chips | h56 | `FIG_L17_PlacesChips` | ✅ |
| L08 | 280×280 | quiet zone | map overlay | `FIG_L08_GeofenceCircle` | ✅ |
| L09 | 320×280 | day journal | card | `FIG_L09_DayJournal` | ✅ |
| L13 | 320×160 | share link | card | `FIG_L13_ShareLink` | ✅ |
| L16 | 340×360 | family calendar | month | `FIG_L16_Calendar` | ✅ |
| L18 | 360×360 | Always Allow | modal art | `FIG_L18_AlwaysAllow` | ✅ |
| L05 | 300×280 | empty mailbox | empty | `FIG_L05_EmptyMailbox` | ✅ |
| L06 | 360×252 | Full/Limited | cards | `FIG_L06_AccessCards` | ✅ |
| L07 | 400×140 | invite roles | chips | `FIG_L07_ChipsRoles` | ✅ |
| L14 | 220×400 | splash optional | tall | `FIG_L14_Splash` | ✅ |
| L35 | 340×360 | role modal | modal | `FIG_L35_RoleModal` | ✅ |
| L36 | 400×420 | subscription tab | tab→Tariffs | `FIG_L36_Subscription` | ✅ |
| L10 | 200×240 | SOS hold | big circle | `FIG_L10_SOSHold` | ✅ |
| L11 | 360×120 | crash tip | row | `FIG_L11_CrashTip` | ✅ |
| L19 | 220×160 | Tile soon | empty | `FIG_L19_TagsSoon` | ✅ |
| L20 | 220×160 | Evac soon | empty | `FIG_L20_EvacSoon` | ✅ |
| L21 | 250×64 | pet soon | row h64 | `FIG_L21_PetSoon` | ✅ |
| L22 | 280×160 | driving soon | card | `FIG_L22_DrivingSoon` | ✅ |
| L23 | 280×160 | pin preview | card | `FIG_L23_PinPreview` | ✅ |
| L24 | 300×200 | routes | card | `FIG_L24_Routes` | ✅ |
| L26 | 340×240 | soft paywall | card | `FIG_L26_SoftPaywall` | ✅ |
| L27 | 240×160 | pets empty | empty | `FIG_L27_PetsSoon` | ✅ |
| L28 | 240×160 | items empty | empty | `FIG_L28_ItemsSoon` | ✅ |
| L29 | 360×220 | pet wizard | card | `FIG_L29_PetWizard` | ✅ |
| L30 | 340×200 | driving weekly | card | `FIG_L30_DrivingWeekly` | ✅ |
| L31 | 340×200 | safety tab | tab | `FIG_L31_SafetyTab` | ✅ |
| L32 | 300×220 | places list | list | `FIG_L32_PlacesList` | ✅ |
| L33 | 320×260 | create event | form | `FIG_L33_CreateEvent` | ✅ |

---

## 4. Kaspersky page 05

| ID | Figma size | Экран | Asset | Art |
|----|------------|-------|-------|-----|
| FIG-01 | 393×852 | Calm call hero | `FIG_K_01_CalmCall` | ✅ |
| FIG-02 | 393×852 | Call Directory steps | `FIG_K_02_CallDirectory` | ✅ |
| FIG-03 | 320×320 | Shield ON status | `FIG_K_03_ShieldON` | ✅ |
| FIG-04 | 393×852 | Empty lists | `FIG_K_04_EmptyLists` | ✅ |
| FIG-05 | 393×852 | Child overview empty | `FIG_K_05_ChildEmpty` | ✅ |
| FIG-06 | 393×852 | Add child avatars | `FIG_K_06_AvatarGrid` | ✅ |
| FIG-07 | 393×852 | Invite QR | `FIG_K_07_InviteQR` | ✅ |
| FIG-08 | 393×852 | Invite waiting | `FIG_K_08_InviteWait` | ✅ |
| FIG-13 | 393×852 | Content categories | `FIG_K_13_Categories` | ✅ |
| FIG-14 | 393×852 | Anti-Banner | `FIG_K_14_AntiBanner` | ✅ |
| FIG-15 | 393×852 | Home network empty | `FIG_K_15_HomeNet` | ✅ |
| FIG-16 | 393×852 | Safe QR | `FIG_K_16_SafeQR` | ✅ |
| FIG-17 | 393×852 | Social connect empty | `FIG_K_17_Social` | ✅ |
| FIG-REUSE | 393×520 | legend only | — не UI | ✅ |
| FIG-09 | — | 📎 → L01 | | 📎 |
| FIG-10 | — | 📎 → L17/L32 | | 📎 |
| FIG-11 | — | 📎 → L18 | | 📎 |
| FIG-18 | — | 📎 → L10/L11 | | 📎 |
| FIG-19 | — | 📎 → L19 | | 📎 |
| FIG-20 | — | 📎 → L20 | | 📎 |
| FIG-21 | — | 📎 → L36 | | 📎 |

---

## 5. Очередь art (дыры закрыты **в плане**, не в Figma)

Пока ⏳ — **не входят** в `GO export-icons-preview`. Рисовать отдельным GO `icons-p-main` / `icons-p-tariff` / `icons-p-doors-extra`.

### 5.1 P-MAIN доп. плитки + tab Игра (Clay+G1 язык)

| # | Proposed Figma | Экран | Слот | UI pt | Asset | Art |
|---|----------------|-------|------|-------|-------|-----|
| M1 | `G1_M01_AIFriends` | Удобный AI Друзья | row | **28** | `ICON_G1_M01_AIFriends_{Glyph\|Black}` | ✅ |
| M2 | `G1_M02_Senior60` | Main плитка 60+ | tile | **40** | `ICON_G1_M02_Senior60_*` | ✅ |
| M3 | `G1_M03_Analytics` | Main плитка Аналитика | tile | **40** | `ICON_G1_M03_Analytics_*` | ✅ |
| M4 | `G1_M04_Settings` | Main плитка Настройки | tile | **40** | `ICON_G1_M04_Settings_*` | ✅ |
| M5 | `G1_M05_SimpleHome` | Main плитка Удобный | tile | **32** | `ICON_G1_M05_SimpleHome_*` | ✅ |
| M6 | `G1_M06_Play` / U01 | Main tab Игра | tab | **28** | `ICON_G1_U01_Unicorn_*` | ✅ |

(Защита/Тарифы/tabs/profile/doors/Premium — уже §1 A04/A05/A01–A03/A06/A12.)

### 5.2 P-DOORS extras (SimpleHome secondary)

| # | Proposed | Экран | UI pt | Asset | Art |
|---|----------|-------|-------|-------|-----|
| D1 | `G1_D01_AIFriendsRow` | Удобный · AI Друзья row | 28 | = **M01** | ✅ reuse |
| D2 | `G1_D02_Menu` | Удобный · Меню | 28 | `ICON_G1_D02_Menu_{Glyph\|Black}` | ✅ |
| D3 | `G1_D03_FullApp` | Удобный · Полная версия | 28 | `ICON_G1_D03_FullApp_*` | ✅ |

HOME Family/Access — уже Alive §2 #25–27.

### 5.3 P-TARIFF добить

| # | Proposed | Экран | UI pt | Asset | Art |
|---|----------|-------|-------|-------|-----|
| T1 | `G1_T01_Free` | Tariffs Free | 32 | `ICON_G1_T01_Free_*` | ✅ |
| T2 | `G1_T02_Personal` | Tariffs Personal | 32 | `ICON_G1_T02_Personal_*` | ✅ |
| T3 | `G1_T03_Family` | Tariffs Family | 32 | `ICON_G1_T03_Family_*` | ✅ |
| T4 | `G1_T04_Trial` | Tariffs Trial | 32 | `ICON_G1_T04_Trial_*` | ✅ |
| T5 | Premium | Tariffs Premium | 32 | = **A06** | ✅ |

Free/Family/Trial Alive §2 — в Assets не было; закрыто G1 Glyph/Black.

---

## 6. Порядок после Approve плана

1. **Owner Approve** этот файл = «план 100% строк»  
2. `GO export-icons-preview` → **только §1** (G1 blue+black @2x/@3x) в Assets/preview  
3. `GO wire-icons-preview-flag` → Main/SimpleHome/Where chrome  
4. `GO на сборку` → симе blue→black→legacy  
5. Потом GO art §5 → export Alive/FIG-L/Kaspersky пакетами  

---

## 7. Чеклист «дыры плана закрыты»

- [x] G1 blue поштучно  
- [x] G1 black поштучно  
- [x] Alive 27 поштучно  
- [x] FIG-L 36 поштучно  
- [x] Kaspersky masters + reuse map  
- [x] P-MAIN / doors-extra / Personal — слоты+имена+размеры (art ⏳)  
- [x] Что не exportить (G2/G3/V2/V3)  
- [x] Overlap G1 doors vs Alive DOOR зафиксирован  
- [x] Owner Approve плана  
- [x] Export wave1 G1 blue+black → `export_wave1_g1/` + 24× `Assets.xcassets/ICON_G1_*`  
- [x] Wire + flag (`AliveIconStyle` · Settings picker · Main/SimpleHome/Where)  
- [ ] Сборка / симе — **только владелец** (агент не запускает xcodebuild)  
- [ ] Wire A06 Premium на Tariffs/L36 (asset есть, экран ещё emoji/SF)  
- [ ] Art очередь §5 P-MAIN / Personal / doors-extra  

**SSOT этого файла.** Дубли: `PER_ICON_INSERT_MAP.md` · `FIGMA_FULL_SIZE_AND_SLOT_CATALOG.md` · UNIFIED §13 → ссылка сюда.  
**Manifest wave1:** `export_wave1_g1/MANIFEST.md`
