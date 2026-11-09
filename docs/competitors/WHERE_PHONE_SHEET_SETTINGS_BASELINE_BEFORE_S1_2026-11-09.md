# WhereIsPhone sheet — baseline ДО S1 (запомнить / откат)

**SSOT очереди:** [`FAMILY_SAFETY_UNIFIED_ML_PLAN_2026-11-09.md`](FAMILY_SAFETY_UNIFIED_ML_PLAN_2026-11-09.md) §2–3  
**Дата:** 2026-11-09 · **Файл:** `Screens/WhereIsPhoneScreen.swift`  
**Зачем:** владелец — «сейчас всё работает, только поднять на 95%». Эти настройки = рабочий mid/full до абсолютной высоты S1.  
**Статус 2026-11-09 вечер:** S1+S1b+S2 на device **не дали** 95% — дальше только по UNIFIED §3 (не повторять S1/S2 вслепую).

## Состояние до S1

| Параметр | Значение |
|----------|----------|
| `sheetExpansion` start | `0.08` |
| Peek snap | `0.08` |
| Half snap | `0.42` |
| Full snap | `1.0` |
| Drag thresholds | `<0.22` → peek · `<0.62` → half · else full |
| Высота | `fraction = 0.22 + 0.73 * sheetExpansion` · `min(usable*0.95, usable*fraction)` |
| Чип (не Events) | если `expansion < 0.55` → `0.55` |
| Чип Events | `expansion = 1.0` + scrollTo lost |
| Lost CTA | только scroll-карточка (sticky **откат**) |
| FAB dim | `expansion > 0.85` |
| Map interaction | `expansion < 0.55` и не drag |

## Откат S1

Вернуть `locationSheetHeight` + chip button к формулам выше (этот файл = SSOT).

## После S1 (цель)

- Full height = `usable − mapStrip(6%)` ≈ **94%** usable (полоска карты 5–8%)
- **Любой** чип → `sheetExpansion = 1.0`
- Peek/half snaps без изменения чисел `0.08` / `0.42` / `1.0`

## S1 на скрине mid — почему

Header+FAB+sheet были в **одном VStack** → SwiftUI сжимал `sheetH`.  
**S1b (2026-11-09):** sheet+tab якорь снизу; header/FAB — overlay на карте.

## Если S1b мало → следующий из трёх = **S2**

Системные detents `.medium` + `.fraction(0.95)`. Потом **S3** (scroll→expand).

## S2 в коде (2026-11-09)

- iOS 16+: `.sheet` + `presentationDetents([.medium, .fraction(0.95)])`
- Любой чип / pin → `locationDetent = .fraction(0.95)`
- Tab bar sticky **внутри** system sheet
- iOS 15: fallback S1b
- Если S2 мало на device → **S3**
