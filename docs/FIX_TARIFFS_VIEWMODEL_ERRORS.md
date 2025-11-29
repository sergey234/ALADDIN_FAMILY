# 🔧 Исправление ошибок в TariffsViewModel

## Проблема

`TariffsViewModel.swift` компилируется для таргета `ALADDINPacketTunnel`, но он не должен там быть. Также отсутствуют необходимые импорты.

## Решение

### 1. Убрать TariffsViewModel.swift из таргета ALADDINPacketTunnel

В Xcode:
1. Откройте проект `ALADDIN.xcodeproj`
2. Выберите файл `ViewModels/TariffsViewModel.swift` в навигаторе
3. Откройте панель "File Inspector" (⌘⌥1)
4. В разделе "Target Membership" снимите галочку с `ALADDINPacketTunnel`
5. Оставьте только `ALADDIN`

### 2. Проверить, что все необходимые файлы включены в таргет ALADDIN

Убедитесь, что следующие файлы включены в таргет `ALADDIN`:
- `Core/Store/StoreManager.swift`
- `Core/Config/AppConfig.swift`
- `Core/Notifications/NotificationManager.swift`
- `Core/Managers/TariffManager.swift`
- `Shared/Models/ThreatProtectionCategory.swift`

### 3. Пересобрать проект

После исправления:
1. Очистите проект: Product → Clean Build Folder (⇧⌘K)
2. Соберите проект: Product → Build (⌘B)
3. Запустите на симуляторе iPhone 13 Pro Max

## Ошибки, которые должны быть исправлены

- ✅ `cannot find type 'StoreManager' in scope`
- ✅ `cannot find type 'TariffType' in scope`
- ✅ `cannot find 'AppConfig' in scope`
- ✅ `cannot find 'NotificationManager' in scope`

