# 🎯 ДЕТАЛЬНЫЙ ПЛАН ОТКЛЮЧЕНИЯ КОМПОНЕНТОВ SETTINGS SCREEN

**Дата:** 2026-02-16  
**Версия сборки:** 40  
**Статус:** 📋 ПОЛНЫЙ ПЛАН ОТКЛЮЧЕНИЯ

---

## 📊 ПОЛНАЯ СТРУКТУРА SETTINGS SCREEN

### **ВСЕГО КОМПОНЕНТОВ:**

- **Основных секций:** 6
- **Подсекций в секции Защита:** 5
- **Модальных окон:** 15
- **Отдельный экран:** AdvancedProtectionSettingsScreen (с 6+ подсекциями)

---

## 🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ВСЕХ СЕКЦИЙ

### **1. СЕКЦИЯ ПРОФИЛЬ** (`profileSection`)

**Содержимое:**
- Аватар пользователя
- Имя пользователя
- Email/Alias
- Статус подписки
- Кнопка редактирования

**Модальные окна:** 1
- `ProfileEditView`

**Флаг отключения:**
```swift
@AppStorage("settings_disable_profile_section") private var disableProfileSection: Bool = false
```

**Как отключить:**
```swift
disableProfileSection = true
```

---

### **2. СЕКЦИЯ ЗАЩИТА** (`securitySection`) ⚠️ **САМАЯ СЛОЖНАЯ**

**Содержит 5 подсекций:**

#### **2.1. Переключатель "Защита сети"**
- Toggle для включения/выключения
- Использует `isNetworkProtectionEnabled`

**Флаг отключения:**
```swift
@AppStorage("settings_disable_security_network_toggle") private var disableSecurityNetworkToggle: Bool = false
```

#### **2.2. Переключатель "Биометрическая аутентификация"**
- Toggle для включения/выключения
- Использует `isBiometricEnabled`

**Флаг отключения:**
```swift
@AppStorage("settings_disable_security_biometric_toggle") private var disableSecurityBiometricToggle: Bool = false
```

#### **2.3. Уровень защиты** ⚠️ **САМАЯ СЛОЖНАЯ ЧАСТЬ**

**Содержит:**
- Заголовок с кнопкой Info
- Текст уровня защиты (`protectionLevelText`)
- Slider с уровнем (read-only)
- Процент защиты (0-100%)
- **3 кнопки:**
  - История защиты
  - **Расширенные настройки** (открывает `AdvancedProtectionSettingsScreen`)
  - Улучшить защиту

**Использует:**
- ⚠️ **`calculatedProtectionLevel`** - вычисление уровня (может быть дорогим)
- ⚠️ **`safeCurrentTariff`** - доступ к тарифу
- `tariff.createCard()` - создание карты тарифа

**Флаг отключения:**
```swift
@AppStorage("settings_disable_security_protection_level") private var disableSecurityProtectionLevel: Bool = false
```

**Флаг отключения кнопок:**
```swift
@AppStorage("settings_disable_security_protection_buttons") private var disableSecurityProtectionButtons: Bool = false
```

**Флаг отключения AdvancedProtectionSettingsScreen:**
```swift
@AppStorage("settings_disable_advanced_protection_screen") private var disableAdvancedProtectionScreen: Bool = false
```

#### **2.4. Менеджеры (5 компонентов)**

1. Emergency Contacts
2. Emergency Notifications
3. Voice Control
4. Child Protection Compliance
5. Data Protection Compliance

**Флаг отключения:**
```swift
@AppStorage("settings_disable_security_managers") private var disableSecurityManagers: Bool = false
```

**Флаг отключения всей секции:**
```swift
@AppStorage("settings_disable_security_section") private var disableSecuritySection: Bool = false
```

---

### **3. СЕКЦИЯ УВЕДОМЛЕНИЯ** (`notificationsSection`)

**Содержимое:**
- Переключатель "Push-уведомления"
- Переключатель "Звуковые уведомления"

**Флаг отключения:**
```swift
@AppStorage("settings_disable_notifications_section") private var disableNotificationsSection: Bool = false
```

---

### **4. СЕКЦИЯ ПРИЛОЖЕНИЕ** (`appSection`)

**Содержимое:**
- Кнопка "Язык"
- Кнопка "Тёмная тема"
- Кнопка "Обновления"
- Кнопка "Система позиционирования"

**Модальные окна:** 2
- `LanguageSettingsScreen`
- `PositioningSystemPickerView`

**Флаг отключения:**
```swift
@AppStorage("settings_disable_app_section") private var disableAppSection: Bool = false
```

---

### **5. СЕКЦИЯ СИСТЕМНЫЕ КОМПОНЕНТЫ** (`systemComponentsSection`)

**Содержимое:**
- Список системных компонентов (только для админов)
- Загружает компоненты через API

**Флаг отключения:**
```swift
@AppStorage("settings_disable_system_components_section") private var disableSystemComponentsSection: Bool = false
```

---

### **6. СЕКЦИЯ ДОПОЛНИТЕЛЬНО** (`additionalSection`)

**Содержимое:**
- Кнопка "Помощь и поддержка"
- Кнопка "Политика конфиденциальности"
- Кнопка "Условия использования"
- Кнопка "Согласие на обработку ПДн"
- Кнопка "Поделиться приложением"

**Модальные окна:** 4
- `SupportScreen`
- `PrivacyPolicyScreen`
- `TermsOfServiceScreen`
- `ShareSheet`

**Флаг отключения:**
```swift
@AppStorage("settings_disable_additional_section") private var disableAdditionalSection: Bool = false
```

---

## 🎯 ПЛАН ОТКЛЮЧЕНИЯ: ПОШАГОВАЯ ИНСТРУКЦИЯ

### **ЭТАП 1: БЫСТРАЯ ДИАГНОСТИКА (5 минут)**

**Цель:** Найти проблемную основную секцию

#### **Шаг 1.1: Отключите секцию Защита**

1. **Откройте файл:** `Screens/05_SettingsScreen.swift`
2. **Найдите строку 102:**
   ```swift
   @AppStorage("settings_disable_security_section") private var disableSecuritySection: Bool = false
   ```
3. **Измените на:**
   ```swift
   @AppStorage("settings_disable_security_section") private var disableSecuritySection: Bool = true
   ```
4. **Соберите проект:** Cmd + B
5. **Протестируйте на реальном устройстве**

**Результат:**
- ✅ Если краш **исчез** - проблема в секции **Защита**
- ❌ Если краш **остался** - проблема в другой секции (переходите к Шагу 1.2)

---

#### **Шаг 1.2: Отключите все секции кроме Профиль**

1. **Измените флаги:**
   ```swift
   disableProfileSection = false      // ✅ ВКЛЮЧЕНО
   disableSecuritySection = true       // ❌ ОТКЛЮЧЕНО
   disableNotificationsSection = true  // ❌ ОТКЛЮЧЕНО
   disableAppSection = true            // ❌ ОТКЛЮЧЕНО
   disableSystemComponentsSection = true // ❌ ОТКЛЮЧЕНО
   disableAdditionalSection = true     // ❌ ОТКЛЮЧЕНО
   ```

2. **Протестируйте:**
   - ✅ Если краш **исчез** - секция Профиль работает
   - ❌ Если краш **остался** - проблема в секции Профиль

---

#### **Шаг 1.3: Включайте секции по одной**

**Порядок (от простой к сложной):**

1. **Включите секцию Дополнительно:**
   ```swift
   disableAdditionalSection = false
   ```
   - Протестируйте
   - Если краш - проблема здесь

2. **Включите секцию Приложение:**
   ```swift
   disableAppSection = false
   ```
   - Протестируйте
   - Если краш - проблема здесь

3. **Включите секцию Уведомления:**
   ```swift
   disableNotificationsSection = false
   ```
   - Протестируйте
   - Если краш - проблема здесь

4. **Включите секцию Защита:**
   ```swift
   disableSecuritySection = false
   ```
   - Протестируйте
   - Если краш - проблема здесь (переходите к Этапу 2)

5. **Включите секцию Системные компоненты** (если вы админ):
   ```swift
   disableSystemComponentsSection = false
   ```
   - Протестируйте
   - Если краш - проблема здесь

---

### **ЭТАП 2: ДИАГНОСТИКА ПОДСЕКЦИЙ СЕКЦИИ ЗАЩИТА**

**Если проблема в секции Защита, нужно найти проблемную подсекцию**

#### **Шаг 2.1: Отключите уровень защиты (самая сложная часть)**

1. **Найдите строку 107:**
   ```swift
   @AppStorage("settings_disable_security_protection_level") private var disableSecurityProtectionLevel: Bool = false
   ```
2. **Измените на:**
   ```swift
   @AppStorage("settings_disable_security_protection_level") private var disableSecurityProtectionLevel: Bool = true
   ```
3. **Протестируйте:**
   - ✅ Если краш **исчез** - проблема в `calculatedProtectionLevel`
   - ❌ Если краш **остался** - проблема в другой подсекции

---

#### **Шаг 2.2: Отключите менеджеры**

1. **Найдите строку 111:**
   ```swift
   @AppStorage("settings_disable_security_managers") private var disableSecurityManagers: Bool = false
   ```
2. **Измените на:**
   ```swift
   @AppStorage("settings_disable_security_managers") private var disableSecurityManagers: Bool = true
   ```
3. **Протестируйте:**
   - ✅ Если краш **исчез** - проблема в одном из менеджеров
   - ❌ Если краш **остался** - проблема в переключателях

---

#### **Шаг 2.3: Отключите переключатели**

1. **Отключите Network Protection:**
   ```swift
   disableSecurityNetworkToggle = true
   ```
2. **Отключите Biometric:**
   ```swift
   disableSecurityBiometricToggle = true
   ```
3. **Протестируйте:**
   - Если краш исчез - проблема в одном из переключателей

---

#### **Шаг 2.4: Отключите кнопки уровня защиты**

1. **Найдите строку 110:**
   ```swift
   @AppStorage("settings_disable_security_protection_buttons") private var disableSecurityProtectionButtons: Bool = false
   ```
2. **Измените на:**
   ```swift
   @AppStorage("settings_disable_security_protection_buttons") private var disableSecurityProtectionButtons: Bool = true
   ```
3. **Протестируйте:**
   - ✅ Если краш **исчез** - проблема в одной из кнопок
   - ❌ Если краш **остался** - проблема в другом компоненте

---

#### **Шаг 2.5: Отключите AdvancedProtectionSettingsScreen**

1. **Найдите строку 112:**
   ```swift
   @AppStorage("settings_disable_advanced_protection_screen") private var disableAdvancedProtectionScreen: Bool = false
   ```
2. **Измените на:**
   ```swift
   @AppStorage("settings_disable_advanced_protection_screen") private var disableAdvancedProtectionScreen: Bool = true
   ```
3. **Протестируйте:**
   - ✅ Если краш **исчез** - проблема в `AdvancedProtectionSettingsScreen`
   - ❌ Если краш **остался** - проблема в другом компоненте

---

### **ЭТАП 3: ДИАГНОСТИКА ADVANCED PROTECTION SETTINGS SCREEN**

**Если проблема в AdvancedProtectionSettingsScreen, нужно добавить флаги для его подсекций**

**Подсекции AdvancedProtectionSettingsScreen:**
1. Safari Card (2 карточки)
2. Threat Protection Aggregator Card
3. Messengers Card
4. Privacy Card
5. Monitoring Card
6. Family Card

**Рекомендация:** Добавьте флаги для каждой подсекции в `AdvancedProtectionSettingsScreen.swift`

---

## 📋 ВСЕ ФЛАГИ ОТКЛЮЧЕНИЯ

### **Основные секции (6 флагов):**

```swift
@AppStorage("settings_disable_profile_section") private var disableProfileSection: Bool = false
@AppStorage("settings_disable_security_section") private var disableSecuritySection: Bool = false
@AppStorage("settings_disable_notifications_section") private var disableNotificationsSection: Bool = false
@AppStorage("settings_disable_app_section") private var disableAppSection: Bool = false
@AppStorage("settings_disable_system_components_section") private var disableSystemComponentsSection: Bool = false
@AppStorage("settings_disable_additional_section") private var disableAdditionalSection: Bool = false
```

### **Подсекции секции Защита (6 флагов):**

```swift
@AppStorage("settings_disable_security_network_toggle") private var disableSecurityNetworkToggle: Bool = false
@AppStorage("settings_disable_security_biometric_toggle") private var disableSecurityBiometricToggle: Bool = false
@AppStorage("settings_disable_security_protection_level") private var disableSecurityProtectionLevel: Bool = false
@AppStorage("settings_disable_security_protection_buttons") private var disableSecurityProtectionButtons: Bool = false
@AppStorage("settings_disable_security_managers") private var disableSecurityManagers: Bool = false
@AppStorage("settings_disable_advanced_protection_screen") private var disableAdvancedProtectionScreen: Bool = false
```

**Всего флагов:** 12

---

## 🎯 РЕКОМЕНДУЕМЫЙ ПОРЯДОК ДИАГНОСТИКИ

### **ВАРИАНТ 1: БЫСТРАЯ ДИАГНОСТИКА (5 минут)**

1. **Отключите секцию Защита:**
   ```swift
   disableSecuritySection = true
   ```
2. **Протестируйте:**
   - ✅ Если краш исчез - проблема в секции Защита
   - ❌ Если краш остался - проблема в другой секции

---

### **ВАРИАНТ 2: ПОЛНАЯ ДИАГНОСТИКА (30+ минут)**

1. **Отключите все секции**
2. **Включайте по одной**, начиная с Профиль
3. **Когда краш произойдет:**
   - Если это секция Защита - переходите к Этапу 2
   - Если это другая секция - проблема найдена

4. **Если проблема в секции Защита:**
   - Отключите уровень защиты
   - Если краш исчез - проблема в `calculatedProtectionLevel`
   - Если краш остался - отключите другие подсекции

---

## 📝 ШАБЛОН ОТЧЕТА

```
Дата: _______________
Версия: _______________

ОСНОВНАЯ СЕКЦИЯ:
- Проблемная секция: _______________

ПОДСЕКЦИЯ (если секция Защита):
- Проблемная подсекция: _______________

ОТКЛЮЧЕННЫЕ ФЛАГИ:
- _______________
- _______________

РЕЗУЛЬТАТ: _______________
```

---

**Дата создания:** 2026-02-16  
**Версия:** 1.0  
**Автор:** AI Assistant
