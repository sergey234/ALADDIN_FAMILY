#!/bin/bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

echo "🚀 Начинаю коммит продакшен файлов..."

# Группа 1: Основной Swift код
echo "📁 Добавляю основную группу файлов..."
git add ALADDINApp.swift
git add Core/Config/AppConfig.swift
git add ViewModels/MainViewModel.swift
git add ViewModels/FamilyRegistrationViewModel.swift
git add Screens/14_OnboardingScreen.swift
git add Core/Network/APIService.swift

# Группа 2: Все остальные модифицированные .swift файлы
echo "📁 Добавляю остальные модифицированные .swift файлы..."
git add Core/Managers/ParentalControlManager.swift
git add Core/Navigation/NavigationManager.swift
git add Core/Network/NetworkManager.swift
git add Core/Notifications/NotificationManager.swift
git add Core/Security/JWTTokenManager.swift
git add Core/Security/KeychainManager.swift
git add Core/Services/ComponentStatusService.swift
git add Screens/01_MainScreen.swift
git add Screens/05_SettingsScreen.swift
git add Screens/20_DevicesScreen.swift
git add Screens/23_FamilyChatScreen.swift
git add ViewModels/NetworkProtectionViewModel.swift
git add ViewModels/PaymentQRViewModel.swift
git add ViewModels/ProfileViewModel.swift

# Группа 3: Новые компоненты защиты
echo "📁 Добавляю новые компоненты защиты..."
git add Core/Antivirus/QuarantineManager.swift
git add Core/Antivirus/ScanScheduler.swift
git add Screens/IncidentResponseSettingsScreen.swift
git add Screens/MalwareDetectionSettingsScreen.swift
git add Screens/MobileSecuritySettingsScreen.swift
git add Screens/NetworkSecuritySettingsScreen.swift
git add Screens/PasswordGeneratorSettingsScreen.swift
git add Screens/PhishingProtectionSettingsScreen.swift
git add ViewModels/IncidentResponseSettingsViewModel.swift
git add ViewModels/MalwareSettingsViewModel.swift
git add ViewModels/MobileSecuritySettingsViewModel.swift
git add ViewModels/NetworkSecuritySettingsViewModel.swift
git add ViewModels/PasswordGeneratorSettingsViewModel.swift
git add ViewModels/PhishingSettingsViewModel.swift
git add Shared/Components/Modals/DarkWebDataInputView.swift
git add Shared/Components/Modals/DarkWebScanExplanationView.swift
git add Shared/Components/Modals/DarkWebScanMethodSelector.swift
git add ALADDIN.xcodeproj/xcshareddata/xcschemes/ALADDINContentBlocker.xcscheme

# Группа 4: План продакшена
echo "📁 Добавляю план продакшена..."
git add PRODUCTION_READINESS_PLAN.md

# Группа 5: Xcode проект
echo "📁 Добавляю Xcode проект..."
git add ALADDIN.xcodeproj/project.pbxproj

echo "✅ Все файлы добавлены в staging area"
echo "📝 Выполняю коммит..."

git commit -m "feat: Продакшен готовность ALADDIN iOS

✅ Исправления демо режима и бесконечных логов
✅ Новая система создания семей с recovery codes
✅ Компоненты защиты (антивирус, карантин, сканирование)
✅ Исправления API и JWT токенов
✅ Финализация плана продакшен готовности

🚀 Приложение готово к App Store"

echo "🎉 Коммит выполнен успешно!"
echo "📊 Статистика коммита:"
git show --stat HEAD
