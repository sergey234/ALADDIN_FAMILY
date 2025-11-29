# 📱 ДИАГРАММА СТРУКТУРЫ ЭКРАНОВ ALADDIN

## 🏠 ОСНОВНЫЕ ЭКРАНЫ
```
MainScreen (3 варианта)
├── 01_MainScreen.swift
├── 01_MainScreen_Exact.swift
└── 01_MainScreen_Fixed.swift

FamilyScreen (3 варианта)
├── 02_FamilyScreen.swift
├── 02_FamilyScreen_Simple.swift
└── FamilyScreen.swift

VPNScreen (2 варианта)
├── 03_VPNScreen.swift
└── 03_VPNScreen_temp.swift

AnalyticsScreen
└── 04_AnalyticsScreen.swift

SettingsScreen
└── 05_SettingsScreen.swift
```

## 🤖 AI И ПОМОЩНИКИ
```
AIAssistantScreen
└── 06_AIAssistantScreen.swift

ParentalControlScreen
└── 07_ParentalControlScreen.swift
```

## 👥 ПОЛЬЗОВАТЕЛЬСКИЕ ИНТЕРФЕЙСЫ
```
ChildInterfaceScreen
└── 08_ChildInterfaceScreen.swift

ElderlyInterfaceScreen
└── 09_ElderlyInterfaceScreen.swift

ChildRewardsScreen
└── ChildRewardsScreen.swift

FamilyTournamentView
└── FamilyTournamentView.swift

GamesParentalControlView
└── GamesParentalControlView.swift
```

## 🎮 ИГРОВЫЕ ЭКРАНЫ
```
UnicornPetView
└── UnicornPetView.swift

UnicornUniverseView
└── UnicornUniverseView.swift

WheelOfFortuneView
└── WheelOfFortuneView.swift

RewardsModalView
└── RewardsModalView.swift

RewardsQuickModal
└── RewardsQuickModal.swift
```

## 💰 КОММЕРЧЕСКИЕ ЭКРАНЫ
```
TariffsScreen
└── 10_TariffsScreen.swift

ProfileScreen
└── 11_ProfileScreen.swift

PaymentQRScreen
└── 25_PaymentQRScreen.swift

ReferralScreen
└── 21_ReferralScreen.swift
```

## 🔔 УВЕДОМЛЕНИЯ И ПОДДЕРЖКА
```
NotificationsScreen
└── 12_NotificationsScreen.swift

SupportScreen
└── 13_SupportScreen.swift

NotificationSettingsScreen
└── NotificationSettingsScreen.swift
```

## 🚀 ONBOARDING И РЕГИСТРАЦИЯ
```
OnboardingScreen (2 варианта)
├── 14_OnboardingScreen.swift
└── OnboardingScreen.swift

MainScreenWithRegistration
└── MainScreenWithRegistration.swift
```

## 📄 ПРАВОВЫЕ ЭКРАНЫ
```
PrivacyPolicyScreen
└── 18_PrivacyPolicyScreen.swift

TermsOfServiceScreen
└── 19_TermsOfServiceScreen.swift
```

## 🔧 ТЕХНИЧЕСКИЕ ЭКРАНЫ
```
DevicesScreen
└── 20_DevicesScreen.swift

DeviceDetailScreen
└── 22_DeviceDetailScreen.swift

FamilyChatScreen
└── 23_FamilyChatScreen.swift

VPNEnergyStatsScreen
└── 24_VPNEnergyStatsScreen.swift
```

## ⚙️ НАСТРОЙКИ И КОНФИГУРАЦИЯ
```
LanguageSettingsScreen
└── LanguageSettingsScreen.swift

WidgetConfigurationScreen
└── WidgetConfigurationScreen.swift
```

## 🎨 HTML WIREFRAMES
```
VPNScreen.html
└── wireframe_analysis/VPNScreen.html
```

## 📊 СТАТИСТИКА ПО КАТЕГОРИЯМ

### 🏠 ОСНОВНЫЕ ФУНКЦИИ (40%)
- MainScreen, FamilyScreen, VPNScreen
- AnalyticsScreen, SettingsScreen
- AIAssistantScreen, ParentalControlScreen

### 👥 ПОЛЬЗОВАТЕЛЬСКИЕ ИНТЕРФЕЙСЫ (25%)
- ChildInterfaceScreen, ElderlyInterfaceScreen
- ChildRewardsScreen, FamilyTournamentView
- GamesParentalControlView

### 🎮 ИГРОВЫЕ И РАЗВЛЕКАТЕЛЬНЫЕ (15%)
- UnicornPetView, UnicornUniverseView
- WheelOfFortuneView, RewardsModalView
- RewardsQuickModal

### 💰 КОММЕРЧЕСКИЕ (10%)
- TariffsScreen, ProfileScreen
- PaymentQRScreen, ReferralScreen

### 🔧 ТЕХНИЧЕСКИЕ (5%)
- DevicesScreen, DeviceDetailScreen
- FamilyChatScreen, VPNEnergyStatsScreen

### 📄 ПРАВОВЫЕ И ПОДДЕРЖКА (5%)
- PrivacyPolicyScreen, TermsOfServiceScreen
- SupportScreen, NotificationsScreen

## 🎯 ОСНОВНЫЕ НАВИГАЦИОННЫЕ ПОТОКИ

### 1. **Главный поток**
```
MainScreen → FamilyScreen → VPNScreen → AnalyticsScreen
```

### 2. **Семейный поток**
```
FamilyScreen → ChildInterfaceScreen → ChildRewardsScreen
```

### 3. **Игровой поток**
```
ChildInterfaceScreen → UnicornPetView → WheelOfFortuneView
```

### 4. **Настройки поток**
```
SettingsScreen → LanguageSettingsScreen → NotificationSettingsScreen
```

### 5. **Коммерческий поток**
```
TariffsScreen → PaymentQRScreen → ProfileScreen
```

## 🚀 РЕКОМЕНДАЦИИ

### 1. **Консолидация**
- Объединить дублирующиеся экраны
- Удалить временные файлы

### 2. **Структурирование**
- Создать папки по категориям
- Унифицировать naming convention

### 3. **Оптимизация**
- Проверить использование всех экранов
- Удалить неиспользуемые экраны

**ИТОГО: 42 Swift экрана + 1 HTML wireframe = 43 экрана** 🎯
