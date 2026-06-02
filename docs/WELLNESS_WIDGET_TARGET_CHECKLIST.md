# Wellness Widget — подключение Extension (p3-18)

> Код готов в `ALADDINWidgets/` (включая `WellnessCheckinWidget`). В `project.pbxproj` **нет** таргета `ALADDINWidgets.appex` — виджет на домашний экран появится только после шагов ниже.

## Быстрый путь (Xcode, ~15 мин)

Следуйте [MANUAL_WIDGET_SETUP.md](../MANUAL_WIDGET_SETUP.md):

1. **File → New → Target → Widget Extension**
2. Product Name: `ALADDINWidgets`
3. Bundle ID: `family.aladdin.ios.widgets` (как в manual)
4. Удалить автосгенерированный `ALADDINWidgets.swift`
5. Добавить в target **ALADDINWidgets** (не ALADDIN):
   - `ALADDINWidgets/ALADDINWidgets.swift` (`@main` + все виджеты)
   - `ALADDINWidgets/WellnessCheckinWidget.swift`
   - `ALADDINWidgets/SharedDataManager.swift`
   - `ALADDINWidgets/Info.plist`
6. **App Groups** `group.com.aladdin.family` — на таргетах **ALADDIN** и **ALADDINWidgets**
7. Собрать схему **ALADDINWidgets** → Run на симуляторе → добавить виджет на Home Screen

## Проверка

- Тап по виджету открывает `aladdin://wellness/checkin`
- Тексты из App Group / `SharedDataManager.getWellnessWidgetData()`

## Автоматизация (опционально)

`configure_widget_target.py` — экспериментальный патч `pbxproj`; предпочтительнее ручной target в Xcode.
