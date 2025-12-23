# КОММИТ: Build 12 + VPN → Network Protection

Дата: 19 декабря 2025

## ✅ ЧТО ИЗМЕНЕНО:

### 1. Версия сборки
- ✅ `CURRENT_PROJECT_VERSION` изменен с **11** на **12** во всех конфигурациях (6 мест)
  - Debug (основное приложение)
  - Release (основное приложение)
  - Debug (UnitTests)
  - Release (UnitTests)
  - Debug (UITests)
  - Release (UITests)

### 2. VPN → Network Protection изменения
- ✅ Все VPN классы, методы и идентификаторы переименованы
- ✅ Все VPN строки в UI обновлены
- ✅ Все VPN функциональность удалена

---

## 🚀 КОМАНДЫ ДЛЯ КОММИТА:

### Вариант 1: Использовать готовый скрипт

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./COMMIT_VPN_FIXES_BUILD_12.sh
```

Затем выполнить коммит (см. команды ниже)

---

### Вариант 2: Команды вручную

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# 1. Добавить все измененные файлы VPN
git add ALADDINWidgets/ALADDINWidgets.swift
git add ALADDINWidgets/SharedDataManager.swift
git add Core/Analytics/AnalyticsManager.swift
git add Core/Analytics/AnalyticsService.swift
git add Core/Cache/CachedAPIService.swift
git add Core/Localization/LocalizationManager.swift
git add Core/Models/APIModels.swift
git add Core/Navigation/NavigationManager.swift
git add Core/Network/NetworkManager.swift
git add Core/NetworkProtection/NetworkProtectionManager.swift
git add Core/Notifications/NotificationManager.swift
git add Core/Offline/OfflineStorageManager.swift
git add Screens/24_NetworkProtectionEnergyStatsScreen.swift
git add Screens/NotificationSettingsScreen.swift
git add Screens/SecurityEducationScreen.swift
git add Screens/SimpleTermsOfServiceScreen.swift

# 2. Добавить новые файлы
git add Core/NetworkProtection/NetworkProtectionBackgroundTasksManager.swift
git add Tests/NetworkProtectionIntegrationTest.swift

# 3. Добавить обновленный project.pbxproj (Build 12)
git add ALADDIN.xcodeproj/project.pbxproj

# 4. Проверить статус
git status

# 5. Коммит
git commit -m "Build 12: Remove all VPN references - Replace with Network Protection

- Update build version from 11 to 12
- Remove VPN domain from SSL pinning
- Rename all VPN classes, methods, and identifiers to Network Protection
- Update notification categories and settings
- Rename widgets and data managers
- Update UI strings
- Remove deprecated VPN navigation method

All changes comply with Apple Guideline 5.4 - VPN Apps
ALADDIN is NOT a VPN application"

# 6. Отправить в GitHub
git push
```

---

## 📋 СПИСОК ФАЙЛОВ ДЛЯ КОММИТА:

### Измененные файлы (16):
1. `ALADDIN.xcodeproj/project.pbxproj` - **Build 12**
2. `ALADDINWidgets/ALADDINWidgets.swift`
3. `ALADDINWidgets/SharedDataManager.swift`
4. `Core/Analytics/AnalyticsManager.swift`
5. `Core/Analytics/AnalyticsService.swift`
6. `Core/Cache/CachedAPIService.swift`
7. `Core/Localization/LocalizationManager.swift`
8. `Core/Models/APIModels.swift`
9. `Core/Navigation/NavigationManager.swift`
10. `Core/Network/NetworkManager.swift`
11. `Core/NetworkProtection/NetworkProtectionManager.swift`
12. `Core/Notifications/NotificationManager.swift`
13. `Core/Offline/OfflineStorageManager.swift`
14. `Screens/24_NetworkProtectionEnergyStatsScreen.swift`
15. `Screens/NotificationSettingsScreen.swift`
16. `Screens/SecurityEducationScreen.swift`
17. `Screens/SimpleTermsOfServiceScreen.swift`

### Новые файлы (2):
18. `Core/NetworkProtection/NetworkProtectionBackgroundTasksManager.swift`
19. `Tests/NetworkProtectionIntegrationTest.swift`

**ИТОГО: 19 файлов**

---

## ✅ ПРОВЕРКА ПЕРЕД КОММИТОМ:

```bash
# Проверить статус
git status

# Посмотреть что будет закоммичено
git diff --cached --stat

# Если все правильно - коммитить
```

---

## ⚠️ ВАЖНО:

**НЕ КОММИТИТЬ:**
- ❌ `ALADDIN.xcodeproj/project.xcworkspace/xcuserdata/` (пользовательские настройки)
- ❌ `docs/.DS_Store` (системные файлы)
- ❌ Папки `BACKUPS/`
- ❌ `*backup*.swift` файлы

**КОММИТИТЬ:**
- ✅ Только активные файлы с исправлениями VPN
- ✅ `project.pbxproj` с Build 12
- ✅ Новые файлы NetworkProtection

---

## 🎯 ПОСЛЕ КОММИТА:

1. ✅ Создать новую сборку IPA (Build 12)
2. ✅ Загрузить в App Store Connect
3. ✅ Отправить на проверку Apple

---

## ✅ ГОТОВО К КОММИТУ!

Все изменения готовы. Версия сборки обновлена на 12, все VPN упоминания удалены.
