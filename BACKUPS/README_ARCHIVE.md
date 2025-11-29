# 📦 АРХИВНЫЕ БЭКАПЫ ВСЕХ СТРАНИЦ

## 📋 ИНФОРМАЦИЯ

Архивные бэкапы содержат все 38 файлов (22 основных экрана + 16 дополнительных компонентов) в сжатом формате `.tar.gz`.

---

## 📁 СТРУКТУРА АРХИВА

```
backup_screens_YYYYMMDD_HHMMSS/
└── Screens/
    ├── 01_MainScreen.swift
    ├── 02_FamilyScreen.swift
    ├── ... (все 38 файлов)
```

---

## 🔄 ВОССТАНОВЛЕНИЕ ИЗ АРХИВА

### Распаковать архив:
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
tar -xzf backups/all_screens_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Скопировать файлы обратно:
```bash
cp -r backup_screens_YYYYMMDD_HHMMSS/Screens/* Screens/
```

### Очистить временные файлы:
```bash
rm -rf backup_screens_YYYYMMDD_HHMMSS
```

---

## 📊 СПИСОК АРХИВОВ

Все архивы находятся в папке `backups/` с именами:
- `all_screens_backup_YYYYMMDD_HHMMSS.tar.gz`

---

## ✅ СОДЕРЖИМОЕ АРХИВА

### Основные экраны (22 файла):
1. 01_MainScreen.swift
2. 02_FamilyScreen.swift
3. 03_VPNScreen.swift
4. 04_AnalyticsScreen.swift
5. 05_SettingsScreen.swift
6. 06_AIAssistantScreen.swift
7. 07_ParentalControlScreen.swift
8. 08_ChildInterfaceScreen.swift
9. 09_ElderlyInterfaceScreen.swift
10. 10_TariffsScreen.swift
11. 11_ProfileScreen.swift
12. 12_NotificationsScreen.swift
13. 13_SupportScreen.swift
14. 14_OnboardingScreen.swift
15. 18_PrivacyPolicyScreen.swift
16. 19_TermsOfServiceScreen.swift
17. 20_DevicesScreen.swift
18. 21_ReferralScreen.swift
19. 22_DeviceDetailScreen.swift
20. 23_FamilyChatScreen.swift
21. 24_VPNEnergyStatsScreen.swift
22. 25_PaymentQRScreen.swift

### Дополнительные компоненты (16 файлов):
1. ChildRewardsScreen.swift
2. FamilyTournamentView.swift
3. GamesParentalControlView.swift
4. LanguageSettingsScreen.swift
5. MainScreenWithRegistration.swift
6. NotificationSettingsScreen.swift
7. RewardsModalView.swift
8. RewardsQuickModal.swift
9. UnicornPetView.swift
10. UnicornUniverseView.swift
11. WheelOfFortuneView.swift
12. WidgetConfigurationScreen.swift
13. AdvancedProtectionSettingsScreen.swift
14. ChildContentScreen.swift
15. FamilyProtectorView.swift
16. SecurityEducationScreen.swift


