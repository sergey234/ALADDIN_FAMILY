# 🎯 Руководство по настройке Widgets

## 📱 Шаг 1: Создание Widget Extension Target

1. Откройте `ALADDIN.xcodeproj` в Xcode
2. File → New → Target
3. Выберите **Widget Extension**
4. Настройки:
   - **Product Name**: `ALADDINWidgets`
   - **Bundle Identifier**: `family.aladdin.ios.widgets`
   - **Language**: Swift
   - **Use Core Data**: ❌ (не включать)

## 🔐 Шаг 2: Настройка App Groups

### Для основного приложения:
1. Выберите проект `ALADDIN` в навигаторе
2. Выберите target `ALADDIN`
3. Signing & Capabilities → + Capability → App Groups
4. Добавьте группу: `group.com.aladdin.family`

### Для Widget Extension:
1. Выберите target `ALADDINWidgets`
2. Signing & Capabilities → + Capability → App Groups
3. Добавьте ту же группу: `group.com.aladdin.family`

## 📁 Шаг 3: Добавление файлов виджетов

1. Перетащите файлы из папки `ALADDINWidgets/` в Xcode
2. Выберите target `ALADDINWidgets` при добавлении
3. Файлы для добавления:
   - `ALADDINWidgets.swift`
   - `SharedDataManager.swift`
   - `Info.plist`

## ⚙️ Шаг 4: Настройка Build Settings

### Для ALADDINWidgets target:
1. Build Settings → Swift Compiler - General
2. **Other Swift Flags**: `-D WIDGET_EXTENSION`
3. **Product Bundle Identifier**: `family.aladdin.ios.widgets`

## 🧪 Шаг 5: Тестирование

1. Выберите схему `ALADDIN` в Xcode
2. Build → Build (⌘+B)
3. Запустите на симуляторе
4. Добавьте виджет на главный экран
5. Проверьте работу виджетов

## 📊 Результат

После настройки у вас будет:
- ✅ Widget Extension target
- ✅ App Groups для обмена данными
- ✅ 3 виджета: Защита семьи, VPN статус, Аналитика
- ✅ Автоматическое обновление данных

## 🔧 Troubleshooting

**Ошибка "No such file or directory"**:
- Убедитесь, что все файлы добавлены в target

**Ошибка "App Groups not configured"**:
- Проверьте, что App Groups настроены для обоих targets

**Виджеты не обновляются**:
- Проверьте, что SharedDataManager использует правильный App Group
