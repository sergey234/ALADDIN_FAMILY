# Место семьи — канон B (2026-11-09)

**SSOT продукта «Где семья».**  
В пользовательских текстах **не пишем** слово Always / «Всегда». Говорим: **доступ к месту, когда приложение закрыто**.

Юридический пакет: `docs/legal/FAMILY_LOCATION_LIFE360_PARITY_LEGAL_PACK_2026-11-09.md`  
Сайт: опубликован на MAIN `…180`.

---

## 1. Как у Life360 и чем мы не как Life360

| | Life360 типично | ALADDIN канон B |
|---|---|---|
| Карта «где сейчас» | Да | **Да** (свежая / недавняя точка) |
| Места + пришёл/ушёл | Да | **Да** |
| Точка когда приложение закрыто | Да | **Да** (нужен доступ при закрытом приложении) |
| След всего дня дома | Часто да | **Нет** |
| Линия маршрута | Из фона | **При движении** / данные поездки (Start не обязателен) |
| Приватность | Quiet zone | **Тихая зона** |

---

## 2. Логика работы

1. Свежая точка на карте (вне тихой зоны).  
2. Доступ к месту при закрытом приложении → точка и «пришёл/ушёл» обновляются.  
3. Тихая зона → точку семье **не отправляем** (все пути: live, report, share).  
4. Маршрут → авто при движении (`FamilyMapAutoTripTracker`) или API; не след дня дома.  
5. Полный стоп → Настройки iPhone → ALADDIN.

---

## 3. Сделано в коде (этот проход)

- [x] Copy без Always / «Всегда» (strings + LocManager + Info.plist / InfoPlist.strings)  
- [x] `FamilyMapQuietZoneStore` в Core; gate в `LocationManager.reportCurrentLocation`  
- [x] Live map: не шлёт точку из тихой зоны; иначе report + авто-поездка  
- [x] Significant-change при доступе «при закрытом приложении»  
- [x] `FamilyMapAutoTripTracker` (скорость → сегмент маршрута)  
- [x] Юртексты сайт под движение (не обязательный Start) + republish  
- [x] S45 / S46 / S47 / GPS polyline без mock (ранее)

---

## 4. Осталось

| # | Что | GO |
|---|---|---|
| FIG-L | Figma Family Safety | отдельный |
| Сборка / Device QA | xcodebuild + телефон | GO на сборку |
| ASC портал | Nutrition Labels руками | с билдом |
| Commit | тексты+код | если попросите |

---

## 5. Файлы кода

- `Core/Family/FamilyMapQuietZoneStore.swift`  
- `Core/Family/FamilyMapAutoTripTracker.swift`  
- `Core/Family/DrivingTripTrackStore.swift`  
- `Core/Managers/LocationManager.swift` (`reportCurrentLocation` + quiet + auto trip)  
- `Screens/FamilySafetyRemainderHub.swift` (live + significant)  
