#!/bin/bash
# Скрипт для создания архивного бэкапа всех страниц

cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="backups/all_screens_backup_${BACKUP_DATE}.tar.gz"

echo "📦 Создание архивного бэкапа всех страниц..."
echo ""

# Список основных экранов (22 файла)
MAIN_SCREENS=(
  "01_MainScreen.swift"
  "02_FamilyScreen.swift"
  "03_VPNScreen.swift"
  "04_AnalyticsScreen.swift"
  "05_SettingsScreen.swift"
  "06_AIAssistantScreen.swift"
  "07_ParentalControlScreen.swift"
  "08_ChildInterfaceScreen.swift"
  "09_ElderlyInterfaceScreen.swift"
  "10_TariffsScreen.swift"
  "11_ProfileScreen.swift"
  "12_NotificationsScreen.swift"
  "13_SupportScreen.swift"
  "14_OnboardingScreen.swift"
  "18_PrivacyPolicyScreen.swift"
  "19_TermsOfServiceScreen.swift"
  "20_DevicesScreen.swift"
  "21_ReferralScreen.swift"
  "22_DeviceDetailScreen.swift"
  "23_FamilyChatScreen.swift"
  "24_VPNEnergyStatsScreen.swift"
  "25_PaymentQRScreen.swift"
)

# Список дополнительных компонентов (16 файлов)
ADDITIONAL_SCREENS=(
  "ChildRewardsScreen.swift"
  "FamilyTournamentView.swift"
  "GamesParentalControlView.swift"
  "LanguageSettingsScreen.swift"
  "MainScreenWithRegistration.swift"
  "NotificationSettingsScreen.swift"
  "RewardsModalView.swift"
  "RewardsQuickModal.swift"
  "UnicornPetView.swift"
  "UnicornUniverseView.swift"
  "WheelOfFortuneView.swift"
  "WidgetConfigurationScreen.swift"
  "AdvancedProtectionSettingsScreen.swift"
  "ChildContentScreen.swift"
  "FamilyProtectorView.swift"
  "SecurityEducationScreen.swift"
)

# Создаем список файлов для архива
FILES_TO_ARCHIVE=()

echo "✅ Проверка основных экранов (22 файла)..."
for file in "${MAIN_SCREENS[@]}"; do
  if [ -f "Screens/$file" ]; then
    FILES_TO_ARCHIVE+=("Screens/$file")
    echo "  ✅ $file"
  else
    echo "  ⚠️  $file - не найден"
  fi
done

echo ""
echo "✅ Проверка дополнительных компонентов (16 файлов)..."
for file in "${ADDITIONAL_SCREENS[@]}"; do
  if [ -f "Screens/$file" ]; then
    FILES_TO_ARCHIVE+=("Screens/$file")
    echo "  ✅ $file"
  else
    echo "  ⚠️  $file - не найден"
  fi
done

echo ""
echo "📦 Создание архива..."
tar -czf "$ARCHIVE_NAME" "${FILES_TO_ARCHIVE[@]}"

if [ $? -eq 0 ]; then
  echo "✅ Архив создан: $ARCHIVE_NAME"
  echo ""
  echo "📊 Статистика архива:"
  ls -lh "$ARCHIVE_NAME" | awk '{print "  Размер: " $5}'
  FILE_COUNT=$(tar -tzf "$ARCHIVE_NAME" 2>/dev/null | grep -c "\.swift$")
  echo "  Всего файлов: $FILE_COUNT"
  echo ""
  echo "✅ Архивный бэкап готов!"
else
  echo "❌ Ошибка при создании архива!"
  exit 1
fi


