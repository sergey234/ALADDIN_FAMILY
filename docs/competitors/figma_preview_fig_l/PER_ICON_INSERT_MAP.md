# ПАМЯТЬ АГЕНТА — по каждой иконке: что вставляем + куда + размер

**SSOT 100% строк (Alive 27 + L01–36 + Kaspersky + P-MAIN очередь):**  
→ **`PLAN_100_PERCENT_ASSET_ROWS.md`**

**Правило (владелец 2026-11-11):** при любом export / wire / правке — **сверять план 100%**.  
Не «примерно»; не массово без слотов. Откат: flag `legacy` · tag `pre-alive-icons-2026-11-11` · blue/black комплекты рядом.

**Figma:** `b6gFc8GUtWC6ncPgb6X6II`  
- Blue: `Clay_G1_Board` `133:92` · comps `G1_A0x_*`  
- Black A/B: `Clay_G1_Black_Board` `137:2` · comps `G1B_A0x_*`  
**Мастер tile:** **112×148** · disc Ø**64** · glow Ø**78**  
**Disc blue:** `#2E5BFF` · **Disc black:** `#0F172A` · **Glyph:** GOLD `#F59E0B`

Asset имена (черновик): `ICON_G1_A0x_*_Blue` / `ICON_G1_A0x_*_Black`

---

## A. G1 app chrome (12 якорей) — Main / SimpleHome / Where

| ID | Blue Figma | Black Figma | Фигура | Экран / страница | Слот UI | UI size (pt) | Export @2x | Export @3x |
|----|------------|-------------|--------|------------------|---------|--------------|------------|------------|
| **A01** | `G1_A01_bust` | `G1B_A01_bust` | bust | **Main** top-right Профиль | gold circle | glyph **22–24** · circle **36–40** | 48 / 80 | 72 / 120 |
| **A01** | same | same | bust | **Main** tab Профиль | tab icon | **20–22** | 44 | 66 |
| **A02** | `G1_A02_bell` | `G1B_A02_bell` | bell | **Main** tab Уведомления | tab | **20–22** | 44 | 66 |
| **A03** | `G1_A03_phone` | `G1B_A03_phone` | phone | **Main** tab Устройства | tab | **20–22** | 44 | 66 |
| **A04** | `G1_A04_shield` | `G1B_A04_shield` | shield | **Main** плитка Защита | tile | **28** · card h **100** | 56 | 84 |
| **A05** | `G1_A05_diamond` | `G1B_A05_diamond` | diamond | **Main** плитка Тарифы | tile | **28** | 56 | 84 |
| **A06** | `G1_A06_crown` | `G1B_A06_crown` | crown | **Tariffs** / Where hub crown / L36 | tile **28** · tab **22** | 56 / 44 | 84 / 66 |
| **A07** | `G1_A07_search` | `G1B_A07_search` | search | **SimpleHome** дверь Проверить | leading | **28–32** (frame ~**36**) | 64 | 96 |
| **A08** | `G1_A08_child` | `G1B_A08_child` | child | **SimpleHome** дверь Ребёнок | leading | **28–32** | 64 | 96 |
| **A09** | `G1_A09_pin` | `G1B_A09_pin` | pin | **SimpleHome** дверь Где семья | leading | **28–32** | 64 | 96 |
| **A10** | `G1_A10_people` | `G1B_A10_people` | people | **Where** chip Семья (L25) | chip | glyph in **56×56** | 112 | 168 |
| **A11** | `G1_A11_radar` | `G1B_A11_radar` | radar | **Where** FAB Locate (L03) | FAB | glyph ~**24** in **48** | 96 | 144 |
| **A12** | `G1_A12_spark` | `G1B_A12_spark` | spark | **Main** tab Aladdin Kids | tab | **20–22** | 44 | 66 |

**Не вставлять G1 в:** OB_*, Companion, VPN product icons.

---

## B. FIG-L Where / Family Safety — что вставляем (не G1 glyph)

| ID | Figma size | Экран | UI slot |
|----|------------|-------|---------|
| L34 | 393×852 | Where full | canvas ref |
| L15 | 393×64 | Where tabs | bar 64 · icon ~30 |
| L25 | 320×72 | Where chips | chip **56×56** |
| L01 | 120×140 | map pin | pin **52–56** |
| L03 | 64×228 | FAB stack | each **48** |
| L02 | 220×56 | last-seen bubble | ~220×56 |
| L04 | 361×220 | member sheet hero | content pad 16 |
| L12 | 320×140 | map type thumbs | thumb **96** |
| L17…L18 | см. FULL catalog | places / geofence / day / share / calendar / allow | per card |
| L05…L36 | см. FULL catalog | empty / access / roles / splash / role / subscription | per card |
| L10…L33 | см. FULL catalog | SOS / soon / driving / pets / safety / places / event | per card |

Полные w×h: `FIGMA_FULL_SIZE_AND_SLOT_CATALOG.md`.

---

## C. Kaspersky / Alive (двери Проверить·Ребёнок и rows)

| Набор | Master | UI |
|-------|--------|-----|
| FIG-01…08, 13–17 | **393×852** (FIG-03 **320×320**) | full screens Antifake/Child |
| Alive DOOR | **120×148** | SimpleHome doors (предпочитать **G1 A07–A09** при wire chrome) |
| Alive AF/PR/FAM/TAR/EMPTY | **96×124** | leading **28–32** · empty ~**160** |

---

## D. Порядок wire (безопасность)

1. Flag: `legacy` | `aliveBlue` | `aliveBlack`  
2. Пакеты по экранам (Main → SimpleHome → Where), **отдельные коммиты**  
3. На каждый asset: строка из таблицы A/B/C выше  
4. Device QA: tab / safe area / clip  

⛔ Export / wire / build — только отдельный GO владельца.
