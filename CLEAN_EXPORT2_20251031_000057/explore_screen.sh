#!/bin/bash

# 📱 Интерактивный скрипт для изучения экранов ALADDIN

echo "📱 ИНТЕРАКТИВНЫЙ ПРОСМОТР ЭКРАНОВ ALADDIN"
echo "========================================="
echo ""

# Функция для отображения меню
show_menu() {
    echo "🎯 ВЫБЕРИТЕ КАТЕГОРИЮ ЭКРАНОВ:"
    echo "1. 🏠 Основные экраны (MainScreen, FamilyScreen, VPNScreen, etc.)"
    echo "2. 🤖 AI и помощники (AIAssistantScreen, ParentalControlScreen)"
    echo "3. 👥 Пользовательские интерфейсы (Child, Elderly, Rewards)"
    echo "4. 🎮 Игровые экраны (Unicorn, WheelOfFortune, Tournaments)"
    echo "5. 💰 Коммерческие экраны (Tariffs, Payment, Profile)"
    echo "6. 🔔 Уведомления и поддержка (Notifications, Support)"
    echo "7. 🚀 Onboarding и регистрация"
    echo "8. 📄 Правовые экраны (Privacy, Terms)"
    echo "9. 🔧 Технические экраны (Devices, Chat, Energy)"
    echo "10. ⚙️ Настройки и конфигурация"
    echo "11. 🎨 HTML Wireframes"
    echo "12. 📊 Показать все экраны"
    echo "13. 🔍 Поиск по названию экрана"
    echo "0. ❌ Выход"
    echo ""
    echo -n "Введите номер (0-13): "
}

# Функция для отображения экранов категории
show_category() {
    local category=$1
    local title=$2
    
    echo ""
    echo "📱 $title"
    echo "=================="
    
    case $category in
        1)
            echo "MainScreen (3 варианта):"
            ls -la Screens/01_MainScreen*.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "FamilyScreen (3 варианта):"
            ls -la Screens/02_FamilyScreen*.swift Screens/FamilyScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "VPNScreen (2 варианта):"
            ls -la Screens/03_VPNScreen*.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "AnalyticsScreen:"
            ls -la Screens/04_AnalyticsScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "SettingsScreen:"
            ls -la Screens/05_SettingsScreen.swift 2>/dev/null | sed 's/^/   /'
            ;;
        2)
            echo "AIAssistantScreen:"
            ls -la Screens/06_AIAssistantScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "ParentalControlScreen:"
            ls -la Screens/07_ParentalControlScreen.swift 2>/dev/null | sed 's/^/   /'
            ;;
        3)
            echo "ChildInterfaceScreen:"
            ls -la Screens/08_ChildInterfaceScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "ElderlyInterfaceScreen:"
            ls -la Screens/09_ElderlyInterfaceScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "ChildRewardsScreen:"
            ls -la Screens/ChildRewardsScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "FamilyTournamentView:"
            ls -la Screens/FamilyTournamentView.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "GamesParentalControlView:"
            ls -la Screens/GamesParentalControlView.swift 2>/dev/null | sed 's/^/   /'
            ;;
        4)
            echo "UnicornPetView:"
            ls -la Screens/UnicornPetView.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "UnicornUniverseView:"
            ls -la Screens/UnicornUniverseView.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "WheelOfFortuneView:"
            ls -la Screens/WheelOfFortuneView.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "RewardsModalView:"
            ls -la Screens/RewardsModalView.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "RewardsQuickModal:"
            ls -la Screens/RewardsQuickModal.swift 2>/dev/null | sed 's/^/   /'
            ;;
        5)
            echo "TariffsScreen:"
            ls -la Screens/10_TariffsScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "ProfileScreen:"
            ls -la Screens/11_ProfileScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "PaymentQRScreen:"
            ls -la Screens/25_PaymentQRScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "ReferralScreen:"
            ls -la Screens/21_ReferralScreen.swift 2>/dev/null | sed 's/^/   /'
            ;;
        6)
            echo "NotificationsScreen:"
            ls -la Screens/12_NotificationsScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "SupportScreen:"
            ls -la Screens/13_SupportScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "NotificationSettingsScreen:"
            ls -la Screens/NotificationSettingsScreen.swift 2>/dev/null | sed 's/^/   /'
            ;;
        7)
            echo "OnboardingScreen (2 варианта):"
            ls -la Screens/14_OnboardingScreen.swift Screens/OnboardingScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "MainScreenWithRegistration:"
            ls -la Screens/MainScreenWithRegistration.swift 2>/dev/null | sed 's/^/   /'
            ;;
        8)
            echo "PrivacyPolicyScreen:"
            ls -la Screens/18_PrivacyPolicyScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "TermsOfServiceScreen:"
            ls -la Screens/19_TermsOfServiceScreen.swift 2>/dev/null | sed 's/^/   /'
            ;;
        9)
            echo "DevicesScreen:"
            ls -la Screens/20_DevicesScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "DeviceDetailScreen:"
            ls -la Screens/22_DeviceDetailScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "FamilyChatScreen:"
            ls -la Screens/23_FamilyChatScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "VPNEnergyStatsScreen:"
            ls -la Screens/24_VPNEnergyStatsScreen.swift 2>/dev/null | sed 's/^/   /'
            ;;
        10)
            echo "LanguageSettingsScreen:"
            ls -la Screens/LanguageSettingsScreen.swift 2>/dev/null | sed 's/^/   /'
            echo ""
            echo "WidgetConfigurationScreen:"
            ls -la Screens/WidgetConfigurationScreen.swift 2>/dev/null | sed 's/^/   /'
            ;;
        11)
            echo "VPNScreen.html:"
            ls -la wireframe_analysis/VPNScreen.html 2>/dev/null | sed 's/^/   /'
            ;;
        12)
            ./view_all_screens.sh
            ;;
    esac
}

# Функция для поиска экрана
search_screen() {
    echo ""
    echo -n "Введите название экрана для поиска: "
    read search_term
    
    echo ""
    echo "🔍 РЕЗУЛЬТАТЫ ПОИСКА:"
    echo "===================="
    
    find Screens -name "*$search_term*" -type f 2>/dev/null | while read file; do
        echo "   $file"
    done
    
    find wireframe_analysis -name "*$search_term*" -type f 2>/dev/null | while read file; do
        echo "   $file"
    done
}

# Функция для просмотра содержимого экрана
view_screen() {
    echo ""
    echo -n "Введите полный путь к файлу экрана: "
    read file_path
    
    if [ -f "$file_path" ]; then
        echo ""
        echo "📱 СОДЕРЖИМОЕ ЭКРАНА: $file_path"
        echo "================================="
        echo ""
        
        # Показываем первые 50 строк
        head -50 "$file_path"
        
        echo ""
        echo "..."
        echo ""
        echo "📊 Статистика файла:"
        echo "Строк: $(wc -l < "$file_path")"
        echo "Размер: $(ls -lh "$file_path" | awk '{print $5}')"
        echo ""
        echo "Для просмотра полного содержимого используйте: cat $file_path"
    else
        echo "❌ Файл не найден: $file_path"
    fi
}

# Основной цикл
while true; do
    show_menu
    read choice
    
    case $choice in
        1) show_category 1 "🏠 ОСНОВНЫЕ ЭКРАНЫ" ;;
        2) show_category 2 "🤖 AI И ПОМОЩНИКИ" ;;
        3) show_category 3 "👥 ПОЛЬЗОВАТЕЛЬСКИЕ ИНТЕРФЕЙСЫ" ;;
        4) show_category 4 "🎮 ИГРОВЫЕ ЭКРАНЫ" ;;
        5) show_category 5 "💰 КОММЕРЧЕСКИЕ ЭКРАНЫ" ;;
        6) show_category 6 "🔔 УВЕДОМЛЕНИЯ И ПОДДЕРЖКА" ;;
        7) show_category 7 "🚀 ONBOARDING И РЕГИСТРАЦИЯ" ;;
        8) show_category 8 "📄 ПРАВОВЫЕ ЭКРАНЫ" ;;
        9) show_category 9 "🔧 ТЕХНИЧЕСКИЕ ЭКРАНЫ" ;;
        10) show_category 10 "⚙️ НАСТРОЙКИ И КОНФИГУРАЦИЯ" ;;
        11) show_category 11 "🎨 HTML WIREFRAMES" ;;
        12) show_category 12 "📊 ВСЕ ЭКРАНЫ" ;;
        13) search_screen ;;
        0) 
            echo ""
            echo "👋 До свидания! Спасибо за использование анализатора экранов ALADDIN!"
            exit 0
            ;;
        *)
            echo "❌ Неверный выбор. Пожалуйста, введите число от 0 до 13."
            ;;
    esac
    
    echo ""
    echo "Нажмите Enter для продолжения..."
    read
done
