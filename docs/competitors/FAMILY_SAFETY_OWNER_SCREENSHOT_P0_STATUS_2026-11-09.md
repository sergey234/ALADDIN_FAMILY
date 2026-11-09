# Family Safety — статус по скринам владельца (P0) · 2026-11-09

**Роль:** Principal iOS · Mech Pilot  
**⭐ МАСТЕР доделки:** `FAMILY_SAFETY_MASTER_FINISH_88_PLAN_2026-11-09.md`  
**SSOT полного ТЗ:** `FAMILY_SAFETY_DEVICE_QA_ROUND2_FULL_TZ_CHECKLIST_2026-11-09.md`  
**Code-fact:** `FAMILY_SAFETY_CODE_FACT_CHECKLIST_100_2026-11-09.md`  
**Матрица 88:** `FAMILY_SAFETY_DEVICE_QA_ROUND2_SCREEN_MATRIX_88.md`  
**Канон места B:** `FAMILY_LOCATION_CANON_B_PLAN_2026-11-09.md`  
**Сборка:** 19 · push/commit ⛔ · **не закрывать до 100%/88**

## Подтверждение ТЗ

| Вопрос | Ответ |
|--------|--------|
| Вижу полное ТЗ S01–S80 + S19a–h? | **Да** (в SSOT + в этом чате; вставка ТЗ в чате повторялась много раз) |
| Сколько слов в SSOT-чеклисте | **~4796** слов · **447** строк |
| Сколько экранных строк в матрице | **88** уникальных (S01–S80 + S19a–h) |
| Первое сообщение чата = весь TZ? | В **этом** продолженном чате TZ уже был разобран ранее в Round2 SSOT; свежая вставка — повтор того же ТЗ |

## Промпт агента (копировать в волны)

```text
Principal iOS + Family Safety ALADDIN. Mech Pilot. SSOT Round2 FULL_TZ + MATRIX_88 + CANON_B.
No mock GPS/speed. RU+EN strings first. No raw keys. No OB_* Figma edits without TZ.
Сборка только после «GO на сборку». Commit/push только после GO.
```

---

## Чеклист по 3 свежим скринам владельца

| # | Замечание владельца | В плане? | Сделано? | Факт в коде |
|---|---------------------|----------|----------|-------------|
| A | Онбординг обрезан / руки за край / отступы на всех 8 | S01–S02 R0 full-bleed | **КОД ✅** · device ⏳ | `fillsViewport` + soft zoom + hero-first; smoke на симе после GO |
| B | Sheet карты не закрывает карту на 90–95% | S03 / Life360 sheet | **КОД ✅** · device ⏳ | Snap full **1.0** → ~95%; any chip → full; sticky lost |
| C | Тап по аватару-пину на карте — ничего | S19 / member sheet | **КОД ✅** · device ⏳ | `didSelect` → `openMemberFromMapPin` |
| D | «Телефон потерян» уезжает вниз, нельзя нажать Локатор | S10 / lost phone card | **КОД ✅** · device ⏳ | chip Events → sheet 0.95 + scrollTo lost |
| E | 7 скринов Life360 member sheet (S19) | S19a–h | **КОД one-scroll ✅** · polish ⏳ | avatar+crop+stays+weekly+upsell+quiet; mini-map → S19-POLISH |

---

## Краткий план фикса (после GO на код)

1. **OB_00…07** — вернуть full-bleed (`scaledToFill` + zoom), без letterbox; проверить safe area текста  
2. **Sheet** — max expansion = **0.95** от высоты карты (оставить ~5–10% карты сверху)  
3. **Pin tap** — `FamilyHubLiveMapRepresentable` → callback → `selectedMember` + sheet как Life360  
4. **Телефон потерян** — при раскрытии Events/Семья поднимать sheet ≥0.55 и скроллить к кнопке / sticky CTA  
5. **S19** — после 7 скринов владельца  

**Чужой API / mock** — не делаем. Только реальные точки/скорость.
