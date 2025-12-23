#!/bin/bash
# Скрипт для коммита всех изменений VPN → Network Protection
# Дата: 19 декабря 2025

cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

echo "=========================================="
echo "КОММИТ ИЗМЕНЕНИЙ: VPN → Network Protection"
echo "=========================================="
echo ""

echo "Шаг 1: Добавляем измененные файлы..."
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

echo "Шаг 2: Добавляем новые файлы..."
git add Core/NetworkProtection/NetworkProtectionBackgroundTasksManager.swift
git add Tests/NetworkProtectionIntegrationTest.swift

echo "Шаг 3: Удаляем старые VPN файлы (если они еще в git)..."
# Эти файлы могут быть уже удалены, поэтому используем || true
git rm Core/VPN/VPNBackgroundTasksManager.swift 2>/dev/null || true
git rm Tests/VPNIntegrationTest.swift 2>/dev/null || true

echo ""
echo "Шаг 4: Проверяем статус..."
echo ""
git status --short | head -30

echo ""
echo "=========================================="
echo "Файлы готовы к коммиту!"
echo "=========================================="
echo ""
echo "Для коммита выполните:"
echo "git commit -m 'Remove all VPN references - Replace with Network Protection'"
echo ""
echo "Или используйте подробное сообщение:"
echo "git commit -m \"Remove all VPN references - Replace with Network Protection\n\n- Remove VPN domain from SSL pinning\n- Rename all VPN classes, methods, and identifiers to Network Protection\n- Update notification categories and settings\n- Rename widgets and data managers\n- Update UI strings\n- Remove deprecated VPN navigation method\n\nAll changes comply with Apple Guideline 5.4 - VPN Apps\nALADDIN is NOT a VPN application\""
echo ""
echo "После коммита выполните: git push"
