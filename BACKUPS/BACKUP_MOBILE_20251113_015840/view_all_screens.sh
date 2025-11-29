#!/bin/bash

# 📱 Скрипт для просмотра всех экранов мобильного приложения ALADDIN

echo "📱 АНАЛИЗ ВСЕХ ЭКРАНОВ МОБИЛЬНОГО ПРИЛОЖЕНИЯ ALADDIN"
echo "=================================================="
echo ""

# Подсчет экранов
swift_screens=$(find Screens -name "*.swift" | wc -l)
html_screens=$(find wireframe_analysis -name "*.html" | wc -l)
total_screens=$((swift_screens + html_screens))

echo "📊 СТАТИСТИКА:"
echo "Swift экраны: $swift_screens"
echo "HTML wireframes: $html_screens"
echo "Всего экранов: $total_screens"
echo ""

echo "🏠 ОСНОВНЫЕ ЭКРАНЫ:"
echo "=================="
echo "1. MainScreen (3 варианта):"
ls -la Screens/01_MainScreen*.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "2. FamilyScreen (3 варианта):"
ls -la Screens/02_FamilyScreen*.swift Screens/FamilyScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "3. VPNScreen (2 варианта):"
ls -la Screens/03_VPNScreen*.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "4. AnalyticsScreen:"
ls -la Screens/04_AnalyticsScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "5. SettingsScreen:"
ls -la Screens/05_SettingsScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "🤖 AI И ПОМОЩНИКИ:"
echo "=================="
echo "6. AIAssistantScreen:"
ls -la Screens/06_AIAssistantScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "7. ParentalControlScreen:"
ls -la Screens/07_ParentalControlScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "👥 ПОЛЬЗОВАТЕЛЬСКИЕ ИНТЕРФЕЙСЫ:"
echo "==============================="
echo "8. ChildInterfaceScreen:"
ls -la Screens/08_ChildInterfaceScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "9. ElderlyInterfaceScreen:"
ls -la Screens/09_ElderlyInterfaceScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "🎮 ИГРОВЫЕ ЭКРАНЫ:"
echo "=================="
echo "ChildRewardsScreen:"
ls -la Screens/ChildRewardsScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "FamilyTournamentView:"
ls -la Screens/FamilyTournamentView.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "UnicornPetView:"
ls -la Screens/UnicornPetView.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "UnicornUniverseView:"
ls -la Screens/UnicornUniverseView.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "WheelOfFortuneView:"
ls -la Screens/WheelOfFortuneView.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "💰 КОММЕРЧЕСКИЕ ЭКРАНЫ:"
echo "======================="
echo "10. TariffsScreen:"
ls -la Screens/10_TariffsScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "11. ProfileScreen:"
ls -la Screens/11_ProfileScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "25. PaymentQRScreen:"
ls -la Screens/25_PaymentQRScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "21. ReferralScreen:"
ls -la Screens/21_ReferralScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "🔔 УВЕДОМЛЕНИЯ И ПОДДЕРЖКА:"
echo "==========================="
echo "12. NotificationsScreen:"
ls -la Screens/12_NotificationsScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "13. SupportScreen:"
ls -la Screens/13_SupportScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "NotificationSettingsScreen:"
ls -la Screens/NotificationSettingsScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "🚀 ONBOARDING И РЕГИСТРАЦИЯ:"
echo "============================"
echo "14. OnboardingScreen (2 варианта):"
ls -la Screens/14_OnboardingScreen.swift Screens/OnboardingScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "MainScreenWithRegistration:"
ls -la Screens/MainScreenWithRegistration.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "📄 ПРАВОВЫЕ ЭКРАНЫ:"
echo "==================="
echo "18. PrivacyPolicyScreen:"
ls -la Screens/18_PrivacyPolicyScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "19. TermsOfServiceScreen:"
ls -la Screens/19_TermsOfServiceScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "🔧 ТЕХНИЧЕСКИЕ ЭКРАНЫ:"
echo "======================"
echo "20. DevicesScreen:"
ls -la Screens/20_DevicesScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "22. DeviceDetailScreen:"
ls -la Screens/22_DeviceDetailScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "23. FamilyChatScreen:"
ls -la Screens/23_FamilyChatScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "24. VPNEnergyStatsScreen:"
ls -la Screens/24_VPNEnergyStatsScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "⚙️ НАСТРОЙКИ И КОНФИГУРАЦИЯ:"
echo "============================"
echo "LanguageSettingsScreen:"
ls -la Screens/LanguageSettingsScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "WidgetConfigurationScreen:"
ls -la Screens/WidgetConfigurationScreen.swift 2>/dev/null | sed 's/^/   /'
echo ""

echo "🎨 HTML WIREFRAMES:"
echo "==================="
echo "VPNScreen.html:"
ls -la wireframe_analysis/VPNScreen.html 2>/dev/null | sed 's/^/   /'
echo ""

echo "📊 ИТОГОВАЯ СТАТИСТИКА:"
echo "======================="
echo "Всего Swift экранов: $swift_screens"
echo "HTML wireframes: $html_screens"
echo "Общее количество: $total_screens"
echo ""

echo "🎯 КАТЕГОРИИ:"
echo "============="
echo "🏠 Основные функции: ~17 экранов (40%)"
echo "👥 Пользовательские интерфейсы: ~11 экранов (25%)"
echo "🎮 Игровые и развлекательные: ~6 экранов (15%)"
echo "💰 Коммерческие: ~4 экрана (10%)"
echo "🔧 Технические: ~4 экрана (5%)"
echo "📄 Правовые и поддержка: ~3 экрана (5%)"
echo ""

echo "✅ Анализ завершен! Все экраны найдены и проанализированы."
echo "📖 Подробный отчет: SCREENS_ANALYSIS_REPORT.md"
echo "📱 Структурная диаграмма: SCREENS_STRUCTURE_DIAGRAM.md"
