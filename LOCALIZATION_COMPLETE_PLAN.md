# 🌍 ПОЛНЫЙ ПЛАН ЛОКАЛИЗАЦИИ ДЛЯ ПРОДАКШНА

**Дата:** 2026-02-10  
**Дедлайн:** ПРОДАКШН ЧЕРЕЗ 1 ДЕНЬ!  
**Статус:** 🔥 КРИТИЧНО

---

## 📊 СТАТИСТИКА ЛОКАЛИЗАЦИИ

### **Текущее состояние:**
- **Русский словарь:** ~3000+ ключей
- **Английский словарь:** ~3000+ ключей
- **Hardcoded строки:** Найдено в нескольких экранах
- **Дубли ключей:** Проверено, исправлено ранее

---

## ⚠️ ВАЖНО: ЧТО ЗАМЕНЯТЬ, А ЧТО ОСТАВИТЬ

### **✅ ЗАМЕНИТЬ (на локализацию):**
- ❌ `Text("Русский текст")` - заменить на `Text(localizationManager.localized("key"))`
- ❌ `Text("English text")` - заменить на `Text(localizationManager.localized("key"))`
- ❌ Hardcoded проверки строк (например, `"защита"`, `"protection"`)

### **✅ ОСТАВИТЬ (технические значения):**
- ✅ `"light"`, `"dark"`, `"system"` - ОСТАВИТЬ (технические значения)
- ✅ `"user"`, `"admin"` - ОСТАВИТЬ (технические значения)
- ✅ Имена системных функций - ОСТАВИТЬ
- ✅ Пути к файлам - ОСТАВИТЬ

**Почему:** Это технические значения, не требующие локализации.

---

## ⚠️ КРИТИЧЕСКИЕ ПРОБЛЕМЫ С ЛОКАЛИЗАЦИЕЙ

### **1. Hardcoded русские строки в экранах**

#### **Screens/27_ProtectionStatsScreen.swift:**
- ❌ `Text("🛡️ Общий статус защиты")` - строка 73
- ❌ `Text("📈 Детальная статистика")` - строка 128
- ❌ `Text("🔧 Активные компоненты защиты")` - строка 161
- ❌ `Text("Загрузка компонентов...")` - строка 180
- ❌ `Text("💡 Рекомендации по улучшению")` - строка 196
- ❌ `Text("Все рекомендации выполнены! 🎉")` - строка 216
- ❌ `Text("📊 График блокировки угроз")` - строка 232
- ❌ `Text("Все угрозы успешно заблокированы! 🛡️")` - строка 247
- ❌ `Text("Загрузка данных...")` - строка 254
- ❌ `Text("Последнее сканирование")` - строка 134
- ❌ `"Недавно"` - строка 135 (fallback значение)

#### **Screens/04_AnalyticsScreen.swift:**
- ❌ `"Средняя"` - строка 424 (hardcoded значение)

#### **Screens/12_NotificationsScreen.swift:**
- ❌ `"protection"` и `"защита"` - строки 398-399 (hardcoded проверки)

---

## 📋 ПЛАН ИСПРАВЛЕНИЯ ЛОКАЛИЗАЦИИ

### **ЭТАП 1: Добавление недостающих ключей локализации**

#### **1.1 Ключи для геймификации (30+ ключей)**

**Нужно добавить:**
```swift
// Баланс единорогов
"gamification_balance_title": "Баланс единорогов" / "Unicorn Balance"
"gamification_balance_current": "Текущий баланс: %d 🦄" / "Current balance: %d 🦄"
"gamification_balance_add": "Добавить единорогов" / "Add Unicorns"
"gamification_balance_subtract": "Списать единорогов" / "Subtract Unicorns"
"gamification_balance_history": "История баланса" / "Balance History"

// Награды
"gamification_rewards_title": "Награды" / "Rewards"
"gamification_rewards_claim": "Получить награду" / "Claim Reward"
"gamification_rewards_history": "История наград" / "Rewards History"
"gamification_rewards_give": "Выдать награду" / "Give Reward"
"gamification_rewards_shop": "Магазин наград" / "Rewards Shop"
"gamification_rewards_purchase": "Купить награду" / "Purchase Reward"

// Достижения
"gamification_achievements_title": "Достижения" / "Achievements"
"gamification_achievements_unlock": "Разблокировать достижение" / "Unlock Achievement"
"gamification_achievements_progress": "Прогресс достижений" / "Achievements Progress"
"gamification_achievements_get": "Получить достижение" / "Get Achievement"
"gamification_achievements_claim": "Получить награду за достижение" / "Claim Achievement Reward"

// Турниры
"gamification_tournaments_title": "Турниры" / "Tournaments"
"gamification_tournaments_join": "Присоединиться к турниру" / "Join Tournament"
"gamification_tournaments_get": "Получить турнир" / "Get Tournament"
"gamification_tournaments_leaderboard": "Таблица лидеров" / "Leaderboard"
"gamification_tournaments_leave": "Покинуть турнир" / "Leave Tournament"
"gamification_tournaments_history": "История турниров" / "Tournaments History"

// Настройки игр
"gamification_settings_title": "Настройки игр" / "Game Settings"
"gamification_settings_update": "Обновить настройки" / "Update Settings"
"gamification_settings_notifications": "Уведомления игр" / "Game Notifications"
"gamification_settings_notifications_update": "Обновить уведомления" / "Update Notifications"

// Прогресс игр
"gamification_progress_title": "Прогресс игр" / "Game Progress"
"gamification_progress_update": "Обновить прогресс" / "Update Progress"
"gamification_progress_stats": "Статистика прогресса" / "Progress Statistics"
"gamification_progress_level": "Уровень" / "Level"
"gamification_progress_reset": "Сбросить прогресс" / "Reset Progress"
```

#### **1.2 Ключи для родительского контроля (20+ ключей)**

**Нужно добавить:**
```swift
// Синхронизация настроек
"parental_control_sync_settings_title": "Синхронизация настроек" / "Settings Sync"
"parental_control_sync_settings_get": "Получить настройки" / "Get Settings"
"parental_control_sync_settings_update": "Обновить настройки" / "Update Settings"
"parental_control_sync_settings_history": "История настроек" / "Settings History"
"parental_control_sync_settings_sync": "Синхронизировать настройки" / "Sync Settings"
"parental_control_sync_settings_conflicts": "Конфликты настроек" / "Settings Conflicts"

// Синхронизация лимитов времени
"parental_control_sync_time_limits_title": "Лимиты времени" / "Time Limits"
"parental_control_sync_time_limits_get": "Получить лимиты времени" / "Get Time Limits"
"parental_control_sync_time_limits_update": "Обновить лимиты времени" / "Update Time Limits"
"parental_control_sync_time_limits_history": "История лимитов времени" / "Time Limits History"
"parental_control_sync_time_limits_reset": "Сбросить лимиты времени" / "Reset Time Limits"

// Синхронизация расписаний
"parental_control_sync_schedules_title": "Расписания" / "Schedules"
"parental_control_sync_schedules_get": "Получить расписания" / "Get Schedules"
"parental_control_sync_schedules_update": "Обновить расписания" / "Update Schedules"
"parental_control_sync_schedules_history": "История расписаний" / "Schedules History"
"parental_control_sync_schedules_delete": "Удалить расписание" / "Delete Schedule"

// Синхронизация геозон
"parental_control_sync_geofences_title": "Геозоны" / "Geofences"
"parental_control_sync_geofences_get": "Получить геозоны" / "Get Geofences"
"parental_control_sync_geofences_add": "Добавить геозону" / "Add Geofence"
"parental_control_sync_geofences_update": "Обновить геозону" / "Update Geofence"
"parental_control_sync_geofences_delete": "Удалить геозону" / "Delete Geofence"

// Синхронизация лимитов приложений
"parental_control_sync_app_limits_title": "Лимиты приложений" / "App Limits"
"parental_control_sync_app_limits_get": "Получить лимиты приложений" / "Get App Limits"
"parental_control_sync_app_limits_update": "Обновить лимиты приложений" / "Update App Limits"
"parental_control_sync_app_limits_history": "История лимитов приложений" / "App Limits History"
```

#### **1.3 Ключи для ProtectionStatsScreen (10+ ключей)**

**Нужно добавить:**
```swift
"protection_stats_overall_status": "🛡️ Общий статус защиты" / "🛡️ Overall Protection Status"
"protection_stats_detailed_stats": "📈 Детальная статистика" / "📈 Detailed Statistics"
"protection_stats_active_components": "🔧 Активные компоненты защиты" / "🔧 Active Protection Components"
"protection_stats_loading_components": "Загрузка компонентов..." / "Loading components..."
"protection_stats_recommendations": "💡 Рекомендации по улучшению" / "💡 Improvement Recommendations"
"protection_stats_all_recommendations_done": "Все рекомендации выполнены! 🎉" / "All recommendations completed! 🎉"
"protection_stats_threats_chart": "📊 График блокировки угроз" / "📊 Threats Blocking Chart"
"protection_stats_all_threats_blocked": "Все угрозы успешно заблокированы! 🛡️" / "All threats successfully blocked! 🛡️"
"protection_stats_loading_data": "Загрузка данных..." / "Loading data..."
"protection_stats_last_scan": "Последнее сканирование" / "Last Scan"
"protection_stats_recently": "Недавно" / "Recently"
```

#### **1.4 Ключи для других экранов (10+ ключей)**

**AnalyticsScreen:**
```swift
"analytics_average": "Средняя" / "Average"
```

**NotificationsScreen:**
```swift
"notifications_protection_keyword": "защита" / "protection"
```

---

### **ЭТАП 2: Замена hardcoded строк на локализацию**

#### **2.1 ProtectionStatsScreen.swift**

**Заменить:**
```swift
// ❌ БЫЛО:
Text("🛡️ Общий статус защиты")
Text("📈 Детальная статистика")
Text("🔧 Активные компоненты защиты")
Text("Загрузка компонентов...")
Text("💡 Рекомендации по улучшению")
Text("Все рекомендации выполнены! 🎉")
Text("📊 График блокировки угроз")
Text("Все угрозы успешно заблокированы! 🛡️")
Text("Загрузка данных...")
Text("Последнее сканирование")
viewModel.protectionStats?.lastScan ?? "Недавно"

// ✅ СТАНЕТ:
Text(localizationManager.localized("protection_stats_overall_status"))
Text(localizationManager.localized("protection_stats_detailed_stats"))
Text(localizationManager.localized("protection_stats_active_components"))
Text(localizationManager.localized("protection_stats_loading_components"))
Text(localizationManager.localized("protection_stats_recommendations"))
Text(localizationManager.localized("protection_stats_all_recommendations_done"))
Text(localizationManager.localized("protection_stats_threats_chart"))
Text(localizationManager.localized("protection_stats_all_threats_blocked"))
Text(localizationManager.localized("protection_stats_loading_data"))
Text(localizationManager.localized("protection_stats_last_scan"))
viewModel.protectionStats?.lastScan ?? localizationManager.localized("protection_stats_recently")
```

#### **2.2 AnalyticsScreen.swift**

**Заменить:**
```swift
// ❌ БЫЛО:
(localizationManager.localized("component_location_bubble_metric_accuracy"), "Средняя")

// ✅ СТАНЕТ:
(localizationManager.localized("component_location_bubble_metric_accuracy"), localizationManager.localized("analytics_average"))
```

#### **2.3 NotificationsScreen.swift**

**Заменить:**
```swift
// ❌ БЫЛО:
if titleLower.contains("protection") || titleLower.contains("защита") ||
   messageLower.contains("protection") || messageLower.contains("защита") {

// ✅ СТАНЕТ:
let protectionKeyword = localizationManager.localized("notifications_protection_keyword")
if titleLower.contains("protection") || titleLower.contains(protectionKeyword) ||
   messageLower.contains("protection") || messageLower.contains(protectionKeyword) {
```

---

### **ЭТАП 3: Проверка дублей переводов**

#### **3.1 Автоматическая проверка**

**Скрипт проверки:**
```bash
# Проверить дубли ключей в русском словаре
grep -o '"[^"]*":' Core/Localization/LocalizationManager.swift | grep -A 1 "\.russian" | sort | uniq -d

# Проверить дубли ключей в английском словаре
grep -o '"[^"]*":' Core/Localization/LocalizationManager.swift | grep -A 1 "\.english" | sort | uniq -d
```

#### **3.2 Ручная проверка**

**Что проверить:**
- [ ] Нет дублей ключей в русском словаре
- [ ] Нет дублей ключей в английском словаре
- [ ] Все ключи имеют переводы на оба языка
- [ ] Нет пустых значений переводов

---

### **ЭТАП 4: Проверка всех экранов**

#### **4.1 Поиск hardcoded строк**

**Команда для поиска:**
```bash
# Найти все hardcoded русские строки
grep -r 'Text("[А-Яа-яЁё]' Screens/ --include="*.swift"

# Найти все hardcoded английские строки
grep -r 'Text("[A-Z]' Screens/ --include="*.swift" | grep -v "localized\|NSLocalizedString"
```

#### **4.2 Список экранов для проверки:**

- [ ] Screens/27_ProtectionStatsScreen.swift
- [ ] Screens/04_AnalyticsScreen.swift
- [ ] Screens/12_NotificationsScreen.swift
- [ ] Screens/02_FamilyScreen.swift
- [ ] Screens/07_ParentalControlScreen.swift
- [ ] Screens/08_ChildInterfaceScreen.swift
- [ ] Screens/09_ElderlyInterfaceScreen.swift
- [ ] Screens/20_DevicesScreen.swift
- [ ] Screens/22_DeviceDetailScreen.swift
- [ ] Screens/23_FamilyChatScreen.swift
- [ ] Screens/ChildRewardsScreen.swift
- [ ] Screens/FamilyTournamentView.swift
- [ ] Screens/UnicornPetView.swift
- [ ] Все остальные экраны

---

## 📋 TODO ЛИСТ ДЛЯ ЛОКАЛИЗАЦИИ

### **🔥 КРИТИЧНО:**

#### **1. Добавление ключей локализации:**
- [ ] Добавить 30+ ключей для геймификации (RU + EN)
- [ ] Добавить 20+ ключей для родительского контроля (RU + EN)
- [ ] Добавить 10+ ключей для ProtectionStatsScreen (RU + EN)
- [ ] Добавить 10+ ключей для других экранов (RU + EN)
- [ ] Проверить что все ключи добавлены в оба языка

#### **2. Замена hardcoded строк:**
- [ ] Заменить все hardcoded строки в ProtectionStatsScreen.swift
- [ ] Заменить все hardcoded строки в AnalyticsScreen.swift
- [ ] Заменить все hardcoded строки в NotificationsScreen.swift
- [ ] Проверить все остальные экраны на hardcoded строки

#### **3. Проверка дублей:**
- [ ] Проверить дубли ключей в русском словаре
- [ ] Проверить дубли ключей в английском словаре
- [ ] Удалить все дубли ключей
- [ ] Проверить что все ключи уникальны

#### **4. Проверка всех экранов:**
- [ ] Проверить все 60+ экранов на hardcoded строки
- [ ] Заменить все найденные hardcoded строки
- [ ] Убедиться что все используют `localizationManager.localized()`

---

## ✅ КРИТЕРИИ УСПЕХА

1. ✅ Все hardcoded строки заменены на локализацию
2. ✅ Все ключи локализации добавлены (RU + EN)
3. ✅ Нет дублей ключей в словарях
4. ✅ Все экраны используют локализацию
5. ✅ Приложение работает на русском и английском
6. ✅ Нет крашей из-за отсутствующих ключей

---

**🚀 ГОТОВНОСТЬ К ПРОДАКШНУ: 0% → 100%**
