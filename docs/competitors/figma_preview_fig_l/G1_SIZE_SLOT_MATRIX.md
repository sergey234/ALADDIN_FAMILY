# G1 Classic — куда вставляем + точные размеры (без подгонки потом)

**Выбор владельца:** Clay + **G1** · круг disc = `#2E5BFF` (`primaryBlue`) · фигуры GOLD  
**Дата:** 2026-11-11  
**Figma tile (мастер):** каждый `G1_A0x_*` = **112×148** pt artboard (круг глифа Ø64 внутри)  
**Export канон:** PDF/SVG + PNG **@2× и @3×** из квадратного слота ниже (не из 112×148 целиком с подписью)

---

## Правила wire (чтобы не вылезало)

1. В UI: `Image("ICON_…").resizable().scaledToFit().frame(width: W, height: H)`  
2. Padding внутри asset ≥ **12%** от края слота (уже заложено в круге Ø64 на тайле 112)  
3. Не ставить asset шире слота; hit-area может быть больше glyph  
4. Tab bar: glyph **20–22**, label отдельно (как сейчас emoji 20)  
5. Main tile: glyph **28**, карточка height **100** (код Main)  

---

## Матрица G1 → экран → слот UI → export px

| ID | Фигура G1 | Экран / слот | UI glyph (pt) | Hit / container (pt) | Export PNG @2x | Export PNG @3x | Asset name (черновик) |
|----|-----------|--------------|---------------|----------------------|----------------|----------------|------------------------|
| **A01** | bust Профиль | Main **top-right** gold circle | **22–24** | circle **36–40** | 48×48 / 80×80 | 72×72 / 120×120 | `ICON_G1_A01_Profile` |
| **A01** | bust Профиль | Main **tab** Профиль | **20–22** | tab col ~20% width | 44×44 | 66×66 | same asset, smaller frame |
| **A02** | bell Уведомления | Main tab Уведомления | **20–22** | tab | 44×44 | 66×66 | `ICON_G1_A02_Notif` |
| **A03** | phone Устройства | Main tab Устройства | **20–22** | tab | 44×44 | 66×66 | `ICON_G1_A03_Devices` |
| **A04** | shield Защита | Main **плитка** Защита | **28** | card h **100**, glyph area ~36 | 56×56 | 84×84 | `ICON_G1_A04_Protect` |
| **A05** | diamond Тарифы | Main плитка Тарифы | **28** | card h 100 | 56×56 | 84×84 | `ICON_G1_A05_Tariff` |
| **A06** | crown Premium | Tariffs / tab Подписка (Where L15 crown) | **28** плитка · **22** tab hub | — | 56×56 / 44×44 | 84×84 / 66×66 | `ICON_G1_A06_Premium` |
| **A07** | search Проверить | SimpleHome **дверь** | **28–32** leading (код сейчас frame w **36**) | door card pad L | 64×64 | 96×96 | `ICON_G1_A07_Check` |
| **A08** | child Ребёнок | SimpleHome дверь | **28–32** | frame w 36 | 64×64 | 96×96 | `ICON_G1_A08_Child` |
| **A09** | pin Где семья | SimpleHome дверь | **28–32** | frame w 36 | 64×64 | 96×96 | `ICON_G1_A09_Where` |
| **A10** | people Chip Семья | Where sheet **chip** | glyph in **56×56** circle | chip 56×56 gap 10 (§10.2) | 112×112 | 168×168 | `ICON_G1_A10_ChipFamily` |
| **A11** | radar FAB Locate | Where **FAB** | glyph ~**24** in FAB **48** | FAB 48 (§10.2) | 96×96 | 144×144 | `ICON_G1_A11_FabLocate` |
| **A12** | spark Kids | Main tab Aladdin Kids | **20–22** | tab | 44×44 | 66×66 | `ICON_G1_A12_Kids` |

### Доп. слоты Main (ещё не якоря G1 — очередь P-MAIN)

| Слот сейчас | UI size | Статус |
|-------------|---------|--------|
| AI Друзья плитка | 28 | ⏳ после G1 approve полного P-MAIN |
| 60+ / senior плитка | 28 | ⏳ |
| Аналитика | 28 | ⏳ |
| Настройки | 28 | ⏳ |
| Удобный режим | 24 | ⏳ |
| Игра (unicorn tab) | 20 | ⏳ (можно A12-сосед / отдельный) |

---

## Where hub (уже в FIG-L — размеры канон §10.2)

| Элемент | Size (pt) | Figma |
|---------|-----------|-------|
| Phone canvas | 393×852 | masters |
| Tab bar L15 | 393×64 · icon circle ~30 | `5:63` |
| Chips L25 | chip **56×56** gap 10 | `5:81` |
| FAB | **48** | Batch2 |
| Pin | **52–56** | Batch2 |
| Sheet radius | 20 · H-pad 16 | §10.2 |

A10/A11 при wire **совмещать** с L25/L03 языком (не второй стиль).

---

## Два комплекта для A/B в приложении

| Комплект | Disc fill | Имена |
|----------|-----------|-------|
| **aliveBlue** | `#2E5BFF` | `ICON_G1_*_Blue` (текущий freeze) |
| **aliveBlack** | `#0F172A` storm | `ICON_G1_*_Black` · Figma `Clay_G1_Black_Board` `137:2` · `G1B_A0x_*` ✅ |
| **legacy** | — | emoji/SF как сейчас |

Одинаковые **frame pt** из таблицы выше — меняется только заливка круга.  
**SSOT по каждой иконке:** `PER_ICON_INSERT_MAP.md` (помнить при любом insert).

---

## Чеклист «размеры готовы к export»

- [x] Слоты UI сняты с Main (20 / 28) + SimpleHome (36 leading) + §10.2 (56 / 48)  
- [x] G1 выбран  
- [x] Матрица ID→slot→px записана  
- [x] Black-disc комплект (`G1B_*` · PNG `Clay_G1_Black_12.png`)  
- [ ] Export @2x/@3x по таблице  
- [ ] Wire + flag  
- [ ] Device QA: ни одна иконка не клипит tab/safe area  
