# Wellness Widget — подключение Extension (r100-2-06 / p3-18)

> **Статус:** код в `ALADDINWidgets/` готов; в `project.pbxproj` **нет** таргета `ALADDINWidgets.appex`.  
> **После check-in:** `WellnessWidgetBridge` пишет в App Group (`Core/Services/WellnessSessionStore` → bridge).  
> **Владелец:** iOS в Xcode (~15 мин), PO не блокирует деплой batch4.

## Перед началом

- [ ] Основное приложение **ALADDIN** собирается (⌘B).
- [ ] App Group на main target: `group.com.aladdin.family` (Signing & Capabilities).
- [ ] Прочитать [MANUAL_WIDGET_SETUP.md](../MANUAL_WIDGET_SETUP.md).

## Шаги в Xcode

1. **File → New → Target → Widget Extension**
2. Product Name: `ALADDINWidgets`, Bundle ID: `family.aladdin.ios.widgets`
3. Удалить автосгенерированный `ALADDINWidgets.swift` (если Xcode создал дубликат).
4. В target **ALADDINWidgets** (не ALADDIN) добавить Compile Sources:
   - `ALADDINWidgets/ALADDINWidgets.swift`
   - `ALADDINWidgets/WellnessCheckinWidget.swift`
   - `ALADDINWidgets/SharedDataManager.swift`
5. **App Groups** `group.com.aladdin.family` — на **ALADDIN** и **ALADDINWidgets**.
6. `Info.plist` виджета — из `ALADDINWidgets/Info.plist` (не путать с main app).
7. Схема **ALADDINWidgets** → Run на симуляторе → Home Screen → «+» → ALADDIN wellness widget.

## Проверка (DoD r100-2-06)

- [ ] Виджет отображает последний check-in / placeholder из App Group.
- [ ] Тап открывает `aladdin://wellness/checkin` (или deep link из `WellnessCheckinWidget`).
- [ ] После check-in в приложении данные виджета обновляются (`WellnessWidgetBridge`).
- [ ] `SharedDataManager.swift` **только** в таргете виджета (убрать из main ALADDIN, если дублируется).

## Не делать

- Не запускать `configure_widget_target.py` на прод-ветке без бэкапа `project.pbxproj`.
- Не включать HealthKit в widget target.

## После подключения

Отметить **r100-2-06** в [WELLNESS_ML_HANDOFF_R100.md](./WELLNESS_ML_HANDOFF_R100.md) и строку widget в [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md) § Wellness*.swift.
