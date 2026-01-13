# 📋 ДЕТАЛЬНЫЙ ПЛАН-ТУДУ ЛИСТ: ЛОКАЛИЗАЦИЯ 100%

**Дата:** 13 января 2026  
**Статус:** 🔴 В РАБОТЕ  
**Приоритет:** КРИТИЧЕСКИЙ

---

## 🎯 ЦЕЛЬ: ЛОКАЛИЗАЦИЯ 42 КОМПОНЕНТОВ НА 100%

**Проблема:** Ключи компонентов есть в файлах `Localizable.strings`, но **НЕ добавлены в словарь `translations` в `LocalizationManager.swift`**

**Решение:** Добавить ВСЕ ключи в словарь `translations` для русского и английского языков

---

## 📊 АНАЛИЗ: ЧТО НУЖНО ДОБАВИТЬ

### ✅ ЧТО УЖЕ ЕСТЬ В ФАЙЛАХ Localizable.strings:

#### Новый формат (с точками) - 42 компонента:
- ✅ Все компоненты в формате `component.{id}.title` и `component.{id}.desc`
- ✅ Русский язык: 42 компонента × 2 ключа = 84 ключа
- ✅ Английский язык: 42 компонента × 2 ключа = 84 ключа

#### Старый формат (с подчеркиваниями) - частично:
- ✅ AdvancedProtectionSettingsScreen (13 компонентов) - ЕСТЬ
- ❌ SettingsScreen (5 компонентов) - ОТСУТСТВУЕТ

### ❌ ЧТО ОТСУТСТВУЕТ:

1. **В словаре `translations` в LocalizationManager.swift:**
   - ❌ Все 42 компонента (новый формат) - 84 ключа × 2 языка = 168 строк
   - ❌ Разделы компонентов (emergency_help, threat_protection, etc.) - 10 ключей × 2 языка = 20 строк
   - ❌ Общие ключи компонентов (enabled, disabled, settings, etc.) - 6 ключей × 2 языка = 12 строк

2. **В файлах Localizable.strings (старый формат для SettingsScreen):**
   - ❌ `component_emergency_contact_manager_title` (RU, EN)
   - ❌ `component_emergency_contact_manager_description` (RU, EN)
   - ❌ `component_emergency_notification_manager_title` (RU, EN)
   - ❌ `component_emergency_notification_manager_description` (RU, EN)
   - ❌ `component_voice_control_manager_title` (RU, EN)
   - ❌ `component_voice_control_manager_description` (RU, EN)
   - ❌ `component_russian_child_protection_manager_title` (RU, EN)
   - ❌ `component_russian_child_protection_manager_description` (RU, EN)
   - ❌ `component_russian_data_protection_manager_title` (RU, EN)
   - ❌ `component_russian_data_protection_manager_description` (RU, EN)

**ИТОГО:** 10 ключей × 2 языка = 20 строк нужно добавить в файлы

---

## 📝 ДЕТАЛЬНЫЙ ПЛАН-ТУДУ ЛИСТ

### ЭТАП 1: ПОДГОТОВКА И АНАЛИЗ (15 минут)

- [ ] **1.1 Проверить все ключи в файлах Localizable.strings**
  - [ ] Проверить ru.lproj/Localizable.strings - все 42 компонента
  - [ ] Проверить en.lproj/Localizable.strings - все 42 компонента
  - [ ] Составить список всех найденных ключей

- [ ] **1.2 Проверить какие ключи используются в коде**
  - [ ] NetworkProtectionScreen - новый формат (component.*)
  - [ ] ParentalControlScreen - новый формат (component.*)
  - [ ] AdvancedProtectionSettingsScreen - старый формат (component_*)
  - [ ] SettingsScreen - старый формат (component_*)
  - [ ] Составить список всех используемых ключей

- [ ] **1.3 Сравнить что есть и что используется**
  - [ ] Найти несоответствия
  - [ ] Найти отсутствующие ключи
  - [ ] Составить финальный список для добавления

---

### ЭТАП 2: ДОБАВЛЕНИЕ КЛЮЧЕЙ СТАРОГО ФОРМАТА В ФАЙЛЫ (30 минут)

- [ ] **2.1 Добавить ключи для SettingsScreen в ru.lproj/Localizable.strings**
  - [ ] `"component_emergency_contact_manager_title" = "Экстренные контакты";`
  - [ ] `"component_emergency_contact_manager_description" = "Управление контактами для экстренных случаев";`
  - [ ] `"component_emergency_notification_manager_title" = "Экстренные уведомления";`
  - [ ] `"component_emergency_notification_manager_description" = "Настройка экстренных оповещений";`
  - [ ] `"component_voice_control_manager_title" = "Голосовое управление";`
  - [ ] `"component_voice_control_manager_description" = "Управление голосовыми командами";`
  - [ ] `"component_russian_child_protection_manager_title" = "Защита детей (РФ)";`
  - [ ] `"component_russian_child_protection_manager_description" = "Соответствие законам РФ";`
  - [ ] `"component_russian_data_protection_manager_title" = "Защита данных (РФ)";`
  - [ ] `"component_russian_data_protection_manager_description" = "Соответствие 152-ФЗ РФ";`

- [ ] **2.2 Добавить ключи для SettingsScreen в en.lproj/Localizable.strings**
  - [ ] `"component_emergency_contact_manager_title" = "Emergency Contacts";`
  - [ ] `"component_emergency_contact_manager_description" = "Manage contacts for emergencies";`
  - [ ] `"component_emergency_notification_manager_title" = "Emergency Notifications";`
  - [ ] `"component_emergency_notification_manager_description" = "Configure emergency alerts";`
  - [ ] `"component_voice_control_manager_title" = "Voice Control";`
  - [ ] `"component_voice_control_manager_description" = "Manage voice commands";`
  - [ ] `"component_russian_child_protection_manager_title" = "Child Protection (RU)";`
  - [ ] `"component_russian_child_protection_manager_description" = "Compliance with RF laws";`
  - [ ] `"component_russian_data_protection_manager_title" = "Data Protection (RU)";`
  - [ ] `"component_russian_data_protection_manager_description" = "Compliance with 152-FZ RF";`

---

### ЭТАП 3: ДОБАВЛЕНИЕ ВСЕХ КЛЮЧЕЙ В LocalizationManager.swift (2-3 часа)

#### 3.1 NetworkProtectionScreen (10 компонентов) - НОВЫЙ ФОРМАТ

- [ ] **3.1.1 Добавить в русский словарь (translations[.russian]):**
  - [ ] `"component.crash_detection_agent.title": "Обнаружение аварий"`
  - [ ] `"component.crash_detection_agent.desc": "Автоматическое обнаружение ДТП и вызов помощи"`
  - [ ] `"component.roadside_assistance_agent.title": "Помощь на дороге"`
  - [ ] `"component.roadside_assistance_agent.desc": "Быстрая помощь при поломке автомобиля"`
  - [ ] `"component.emergency_response_bot.title": "Экстренный ответ"`
  - [ ] `"component.emergency_response_bot.desc": "Бот для экстренных ситуаций"`
  - [ ] `"component.emergency_event_manager.title": "Управление экстренными событиями"`
  - [ ] `"component.emergency_event_manager.desc": "Координация экстренных событий"`
  - [ ] `"component.phishing_protection_agent.title": "Защита от фишинга"`
  - [ ] `"component.phishing_protection_agent.desc": "Обнаружение мошеннических сайтов"`
  - [ ] `"component.malware_detection_agent.title": "Обнаружение вредоносного ПО"`
  - [ ] `"component.malware_detection_agent.desc": "Защита от вирусов и троянов"`
  - [ ] `"component.mobile_security_agent.title": "Безопасность мобильных устройств"`
  - [ ] `"component.mobile_security_agent.desc": "Защита смартфонов и планшетов"`
  - [ ] `"component.network_security_agent.title": "Безопасность сети"`
  - [ ] `"component.network_security_agent.desc": "Защита сетевых подключений"`
  - [ ] `"component.incident_response_agent.title": "Реагирование на инциденты"`
  - [ ] `"component.incident_response_agent.desc": "Автоматическое реагирование на критические события"`
  - [ ] `"component.password_security_agent.title": "Безопасность паролей"`
  - [ ] `"component.password_security_agent.desc": "Проверка и генерация безопасных паролей"`

- [ ] **3.1.2 Добавить в английский словарь (translations[.english]):**
  - [ ] `"component.crash_detection_agent.title": "Crash Detection"`
  - [ ] `"component.crash_detection_agent.desc": "Automatic crash detection and emergency call"`
  - [ ] `"component.roadside_assistance_agent.title": "Roadside Assistance"`
  - [ ] `"component.roadside_assistance_agent.desc": "Quick help for car breakdowns"`
  - [ ] `"component.emergency_response_bot.title": "Emergency Response"`
  - [ ] `"component.emergency_response_bot.desc": "Bot for emergency situations"`
  - [ ] `"component.emergency_event_manager.title": "Emergency Event Manager"`
  - [ ] `"component.emergency_event_manager.desc": "Coordination of emergency events"`
  - [ ] `"component.phishing_protection_agent.title": "Phishing Protection"`
  - [ ] `"component.phishing_protection_agent.desc": "Detection of fraudulent websites"`
  - [ ] `"component.malware_detection_agent.title": "Malware Detection"`
  - [ ] `"component.malware_detection_agent.desc": "Protection from viruses and trojans"`
  - [ ] `"component.mobile_security_agent.title": "Mobile Security"`
  - [ ] `"component.mobile_security_agent.desc": "Protection for smartphones and tablets"`
  - [ ] `"component.network_security_agent.title": "Network Security"`
  - [ ] `"component.network_security_agent.desc": "Protection of network connections"`
  - [ ] `"component.incident_response_agent.title": "Incident Response"`
  - [ ] `"component.incident_response_agent.desc": "Automatic response to critical events"`
  - [ ] `"component.password_security_agent.title": "Password Security"`
  - [ ] `"component.password_security_agent.desc": "Check and generate secure passwords"`

#### 3.2 ParentalControlScreen (5 компонентов) - НОВЫЙ ФОРМАТ

- [ ] **3.2.1 Добавить в русский словарь:**
  - [ ] `"component.self_harm_detection_agent.title": "Обнаружение самоповреждений"`
  - [ ] `"component.self_harm_detection_agent.desc": "Защита от контента о самоповреждениях"`
  - [ ] `"component.grooming_detection_agent.title": "Обнаружение груминга"`
  - [ ] `"component.grooming_detection_agent.desc": "Защита от онлайн-хищников"`
  - [ ] `"component.online_predators_agent.title": "Защита от онлайн-хищников"`
  - [ ] `"component.online_predators_agent.desc": "Обнаружение опасных контактов"`
  - [ ] `"component.psychological_support_agent.title": "Психологическая поддержка"`
  - [ ] `"component.psychological_support_agent.desc": "Помощь в сложных ситуациях"`
  - [ ] `"component.parental_control_bot.title": "Бот родительского контроля"`
  - [ ] `"component.parental_control_bot.desc": "Улучшенный родительский контроль"`

- [ ] **3.2.2 Добавить в английский словарь:**
  - [ ] `"component.self_harm_detection_agent.title": "Self-Harm Detection"`
  - [ ] `"component.self_harm_detection_agent.desc": "Protection from self-harm content"`
  - [ ] `"component.grooming_detection_agent.title": "Grooming Detection"`
  - [ ] `"component.grooming_detection_agent.desc": "Protection from online predators"`
  - [ ] `"component.online_predators_agent.title": "Online Predators Protection"`
  - [ ] `"component.online_predators_agent.desc": "Detection of dangerous contacts"`
  - [ ] `"component.psychological_support_agent.title": "Psychological Support"`
  - [ ] `"component.psychological_support_agent.desc": "Help in difficult situations"`
  - [ ] `"component.parental_control_bot.title": "Parental Control Bot"`
  - [ ] `"component.parental_control_bot.desc": "Enhanced parental control"`

#### 3.3 AdvancedProtectionSettingsScreen (13 компонентов) - СТАРЫЙ ФОРМАТ

- [ ] **3.3.1 Добавить в русский словарь:**
  - [ ] `"component_telegram_security_bot_title": "Защита Telegram"`
  - [ ] `"component_telegram_security_bot_description": "Безопасность в Telegram"`
  - [ ] `"component_whatsapp_security_bot_title": "Защита WhatsApp"`
  - [ ] `"component_whatsapp_security_bot_description": "Безопасность в WhatsApp"`
  - [ ] `"component_instagram_security_bot_title": "Защита Instagram"`
  - [ ] `"component_instagram_security_bot_description": "Безопасность в Instagram"`
  - [ ] `"component_max_messenger_security_bot_title": "Защита Max Messenger"`
  - [ ] `"component_max_messenger_security_bot_description": "Безопасность в Max Messenger"`
  - [ ] `"component_gaming_security_bot_title": "Защита в играх"`
  - [ ] `"component_gaming_security_bot_description": "Безопасность игровых платформ"`
  - [ ] `"component_browser_security_bot_title": "Защита браузера"`
  - [ ] `"component_browser_security_bot_description": "Безопасность веб-браузера"`
  - [ ] `"component_location_bubble_agent_title": "Пузырь местоположения"`
  - [ ] `"component_location_bubble_agent_description": "Скрытие точного местоположения"`
  - [ ] `"component_personal_data_cleanup_agent_title": "Очистка данных"`
  - [ ] `"component_personal_data_cleanup_agent_description": "Автоматическая очистка личных данных"`
  - [ ] `"component_anti_tracker_agent_title": "Блокировка трекеров"`
  - [ ] `"component_anti_tracker_agent_description": "Блокировка рекламных трекеров"`
  - [ ] `"component_dark_web_monitoring_agent_title": "Мониторинг Dark Web"`
  - [ ] `"component_dark_web_monitoring_agent_description": "Отслеживание утечек данных"`
  - [ ] `"component_russian_identity_theft_protection_agent_title": "Защита от кражи личности (РФ)"`
  - [ ] `"component_russian_identity_theft_protection_agent_description": "Защита от мошенничества с документами"`
  - [ ] `"component_ai_categories_agent_title": "AI категории"`
  - [ ] `"component_ai_categories_agent_description": "Умная категоризация контента"`
  - [ ] `"component_driving_reports_agent_title": "Отчеты о вождении"`
  - [ ] `"component_driving_reports_agent_description": "Анализ стиля вождения"`

- [ ] **3.3.2 Добавить в английский словарь:**
  - [ ] `"component_telegram_security_bot_title": "Telegram Security"`
  - [ ] `"component_telegram_security_bot_description": "Security in Telegram"`
  - [ ] `"component_whatsapp_security_bot_title": "WhatsApp Security"`
  - [ ] `"component_whatsapp_security_bot_description": "Security in WhatsApp"`
  - [ ] `"component_instagram_security_bot_title": "Instagram Security"`
  - [ ] `"component_instagram_security_bot_description": "Security in Instagram"`
  - [ ] `"component_max_messenger_security_bot_title": "Max Messenger Security"`
  - [ ] `"component_max_messenger_security_bot_description": "Security in Max Messenger"`
  - [ ] `"component_gaming_security_bot_title": "Gaming Security"`
  - [ ] `"component_gaming_security_bot_description": "Gaming platform security"`
  - [ ] `"component_browser_security_bot_title": "Browser Security"`
  - [ ] `"component_browser_security_bot_description": "Web browser security"`
  - [ ] `"component_location_bubble_agent_title": "Location Bubble"`
  - [ ] `"component_location_bubble_agent_description": "Hide exact location"`
  - [ ] `"component_personal_data_cleanup_agent_title": "Data Cleanup"`
  - [ ] `"component_personal_data_cleanup_agent_description": "Automatic personal data cleanup"`
  - [ ] `"component_anti_tracker_agent_title": "Tracker Blocking"`
  - [ ] `"component_anti_tracker_agent_description": "Block advertising trackers"`
  - [ ] `"component_dark_web_monitoring_agent_title": "Dark Web Monitoring"`
  - [ ] `"component_dark_web_monitoring_agent_description": "Track data leaks"`
  - [ ] `"component_russian_identity_theft_protection_agent_title": "Identity Theft Protection (RU)"`
  - [ ] `"component_russian_identity_theft_protection_agent_description": "Protection against document fraud"`
  - [ ] `"component_ai_categories_agent_title": "AI Categories"`
  - [ ] `"component_ai_categories_agent_description": "Smart content categorization"`
  - [ ] `"component_driving_reports_agent_title": "Driving Reports"`
  - [ ] `"component_driving_reports_agent_description": "Driving style analysis"`

#### 3.4 SettingsScreen (5 компонентов) - СТАРЫЙ ФОРМАТ

- [ ] **3.4.1 Добавить в русский словарь:**
  - [ ] `"component_emergency_contact_manager_title": "Экстренные контакты"`
  - [ ] `"component_emergency_contact_manager_description": "Управление контактами для экстренных случаев"`
  - [ ] `"component_emergency_notification_manager_title": "Экстренные уведомления"`
  - [ ] `"component_emergency_notification_manager_description": "Настройка экстренных оповещений"`
  - [ ] `"component_voice_control_manager_title": "Голосовое управление"`
  - [ ] `"component_voice_control_manager_description": "Управление голосовыми командами"`
  - [ ] `"component_russian_child_protection_manager_title": "Защита детей (РФ)"`
  - [ ] `"component_russian_child_protection_manager_description": "Соответствие законам РФ"`
  - [ ] `"component_russian_data_protection_manager_title": "Защита данных (РФ)"`
  - [ ] `"component_russian_data_protection_manager_description": "Соответствие 152-ФЗ РФ"`

- [ ] **3.4.2 Добавить в английский словарь:**
  - [ ] `"component_emergency_contact_manager_title": "Emergency Contacts"`
  - [ ] `"component_emergency_contact_manager_description": "Manage contacts for emergencies"`
  - [ ] `"component_emergency_notification_manager_title": "Emergency Notifications"`
  - [ ] `"component_emergency_notification_manager_description": "Configure emergency alerts"`
  - [ ] `"component_voice_control_manager_title": "Voice Control"`
  - [ ] `"component_voice_control_manager_description": "Manage voice commands"`
  - [ ] `"component_russian_child_protection_manager_title": "Child Protection (RU)"`
  - [ ] `"component_russian_child_protection_manager_description": "Compliance with RF laws"`
  - [ ] `"component_russian_data_protection_manager_title": "Data Protection (RU)"`
  - [ ] `"component_russian_data_protection_manager_description": "Compliance with 152-FZ RF"`

#### 3.5 Улучшение существующих (9 компонентов) - НОВЫЙ ФОРМАТ

- [ ] **3.5.1 Добавить в русский словарь:**
  - [ ] `"component.family_notification_manager.title": "Семейные уведомления"`
  - [ ] `"component.family_notification_manager.desc": "Управление уведомлениями семьи"`
  - [ ] `"component.smart_notification_manager.title": "Умные уведомления"`
  - [ ] `"component.smart_notification_manager.desc": "Интеллектуальная система уведомлений"`
  - [ ] `"component.child_interface_manager.title": "Детский интерфейс"`
  - [ ] `"component.child_interface_manager.desc": "Управление детским интерфейсом"`
  - [ ] `"component.elderly_interface_manager.title": "Интерфейс для пожилых"`
  - [ ] `"component.elderly_interface_manager.desc": "Упрощенный интерфейс"`
  - [ ] `"component.subscription_manager.title": "Управление подпиской"`
  - [ ] `"component.subscription_manager.desc": "Настройки тарифов"`
  - [ ] `"component.referral_manager.title": "Реферальная программа"`
  - [ ] `"component.referral_manager.desc": "Приглашение друзей"`
  - [ ] `"component.qr_payment_manager.title": "QR платежи"`
  - [ ] `"component.qr_payment_manager.desc": "Оплата через QR-код"`
  - [ ] `"component.analytics_manager.title": "Аналитика"`
  - [ ] `"component.analytics_manager.desc": "Статистика и отчеты"`
  - [ ] `"component.report_manager.title": "Отчеты"`
  - [ ] `"component.report_manager.desc": "Управление отчетами"`

- [ ] **3.5.2 Добавить в английский словарь:**
  - [ ] `"component.family_notification_manager.title": "Family Notifications"`
  - [ ] `"component.family_notification_manager.desc": "Manage family notifications"`
  - [ ] `"component.smart_notification_manager.title": "Smart Notifications"`
  - [ ] `"component.smart_notification_manager.desc": "Intelligent notification system"`
  - [ ] `"component.child_interface_manager.title": "Child Interface"`
  - [ ] `"component.child_interface_manager.desc": "Manage child interface"`
  - [ ] `"component.elderly_interface_manager.title": "Elderly Interface"`
  - [ ] `"component.elderly_interface_manager.desc": "Simplified interface"`
  - [ ] `"component.subscription_manager.title": "Subscription Manager"`
  - [ ] `"component.subscription_manager.desc": "Tariff settings"`
  - [ ] `"component.referral_manager.title": "Referral Program"`
  - [ ] `"component.referral_manager.desc": "Invite friends"`
  - [ ] `"component.qr_payment_manager.title": "QR Payments"`
  - [ ] `"component.qr_payment_manager.desc": "Payment via QR code"`
  - [ ] `"component.analytics_manager.title": "Analytics"`
  - [ ] `"component.analytics_manager.desc": "Statistics and reports"`
  - [ ] `"component.report_manager.title": "Reports"`
  - [ ] `"component.report_manager.desc": "Manage reports"`

#### 3.6 Разделы компонентов (5 разделов) - НОВЫЙ ФОРМАТ

- [ ] **3.6.1 Добавить в русский словарь:**
  - [ ] `"component.emergency_help.title": "Экстренная помощь"`
  - [ ] `"component.emergency_help.subtitle": "Быстрая помощь в критических ситуациях"`
  - [ ] `"component.threat_protection.title": "Защита от угроз"`
  - [ ] `"component.threat_protection.subtitle": "Защита от различных видов угроз"`
  - [ ] `"component.incident_response.title": "Реагирование"`
  - [ ] `"component.incident_response.subtitle": "Автоматическое реагирование на инциденты"`
  - [ ] `"component.password_security.title": "Пароли"`
  - [ ] `"component.password_security.subtitle": "Безопасность паролей"`
  - [ ] `"component.child_protection.title": "Защита детей"`
  - [ ] `"component.child_protection.subtitle": "Защита от опасностей в интернете"`

- [ ] **3.6.2 Добавить в английский словарь:**
  - [ ] `"component.emergency_help.title": "Emergency Help"`
  - [ ] `"component.emergency_help.subtitle": "Quick help in critical situations"`
  - [ ] `"component.threat_protection.title": "Threat Protection"`
  - [ ] `"component.threat_protection.subtitle": "Protection from various threats"`
  - [ ] `"component.incident_response.title": "Incident Response"`
  - [ ] `"component.incident_response.subtitle": "Automatic response to incidents"`
  - [ ] `"component.password_security.title": "Passwords"`
  - [ ] `"component.password_security.subtitle": "Password security"`
  - [ ] `"component.child_protection.title": "Child Protection"`
  - [ ] `"component.child_protection.subtitle": "Protection from online dangers"`

#### 3.7 Общие ключи компонентов (7 ключей) - НОВЫЙ ФОРМАТ

- [ ] **3.7.1 Добавить в русский словарь:**
  - [ ] `"component.enabled": "Включено"`
  - [ ] `"component.disabled": "Выключено"`
  - [ ] `"component.settings": "Настройки"`
  - [ ] `"component.loading": "Загрузка..."`
  - [ ] `"component.error": "Ошибка загрузки"`
  - [ ] `"component.save": "Сохранить"`
  - [ ] `"component.cancel": "Отмена"`

- [ ] **3.7.2 Добавить в английский словарь:**
  - [ ] `"component.enabled": "Enabled"`
  - [ ] `"component.disabled": "Disabled"`
  - [ ] `"component.settings": "Settings"`
  - [ ] `"component.loading": "Loading..."`
  - [ ] `"component.error": "Loading error"`
  - [ ] `"component.save": "Save"`
  - [ ] `"component.cancel": "Cancel"`

#### 3.8 Дополнительные ключи для компонентов (5 ключей) - СТАРЫЙ ФОРМАТ

- [ ] **3.8.1 Добавить в русский словарь:**
  - [ ] `"component_settings_hint": "Настройки компонента"`
  - [ ] `"component_toggle_enabled_hint": "Компонент включен"`
  - [ ] `"component_toggle_disabled_hint": "Компонент выключен"`
  - [ ] `"component_enabled": "Включено"`
  - [ ] `"component_disabled": "Выключено"`

- [ ] **3.8.2 Добавить в английский словарь:**
  - [ ] `"component_settings_hint": "Component settings"`
  - [ ] `"component_toggle_enabled_hint": "Component enabled"`
  - [ ] `"component_toggle_disabled_hint": "Component disabled"`
  - [ ] `"component_enabled": "Enabled"`
  - [ ] `"component_disabled": "Disabled"`

#### 3.9 Ключи для аккордеонов (4 ключа) - НОВЫЙ ФОРМАТ

- [ ] **3.9.1 Добавить в русский словарь:**
  - [ ] `"accordion_expanded": "Раздел '%@' развернут"`
  - [ ] `"accordion_collapsed": "Раздел '%@' свернут"`
  - [ ] `"accordion_collapse_hint": "Свернуть раздел"`
  - [ ] `"accordion_expand_hint": "Развернуть раздел"`

- [ ] **3.9.2 Добавить в английский словарь:**
  - [ ] `"accordion_expanded": "Section '%@' expanded"`
  - [ ] `"accordion_collapsed": "Section '%@' collapsed"`
  - [ ] `"accordion_collapse_hint": "Collapse section"`
  - [ ] `"accordion_expand_hint": "Expand section"`

#### 3.10 Password Generator (8 ключей) - НОВЫЙ ФОРМАТ

- [ ] **3.10.1 Добавить в русский словарь:**
  - [ ] `"password_generator.settings": "Настройки генератора"`
  - [ ] `"password_generator.length": "Длина пароля"`
  - [ ] `"password_generator.uppercase": "Заглавные буквы"`
  - [ ] `"password_generator.lowercase": "Строчные буквы"`
  - [ ] `"password_generator.numbers": "Цифры"`
  - [ ] `"password_generator.special": "Специальные символы"`
  - [ ] `"password_generator.generate": "Сгенерировать"`
  - [ ] `"password_generator.generated": "Сгенерированный пароль"`

- [ ] **3.10.2 Добавить в английский словарь:**
  - [ ] `"password_generator.settings": "Generator Settings"`
  - [ ] `"password_generator.length": "Password Length"`
  - [ ] `"password_generator.uppercase": "Uppercase Letters"`
  - [ ] `"password_generator.lowercase": "Lowercase Letters"`
  - [ ] `"password_generator.numbers": "Numbers"`
  - [ ] `"password_generator.special": "Special Characters"`
  - [ ] `"password_generator.generate": "Generate"`
  - [ ] `"password_generator.generated": "Generated Password"`

#### 3.11 Incident Response (9 ключей) - НОВЫЙ ФОРМАТ

- [ ] **3.11.1 Добавить в русский словарь:**
  - [ ] `"incident_response.escalation_thresholds": "Пороги эскалации"`
  - [ ] `"incident_response.low": "Низкая"`
  - [ ] `"incident_response.medium": "Средняя"`
  - [ ] `"incident_response.high": "Высокая"`
  - [ ] `"incident_response.critical": "Критическая"`
  - [ ] `"incident_response.minutes": "мин"`
  - [ ] `"incident_response.sla_time": "Время реакции SLA"`
  - [ ] `"incident_response.auto_actions": "Автодействия"`
  - [ ] `"incident_response.block": "Блокировать"`
  - [ ] `"incident_response.notify": "Уведомить"`
  - [ ] `"incident_response.escalate": "Эскалировать"`

- [ ] **3.11.2 Добавить в английский словарь:**
  - [ ] `"incident_response.escalation_thresholds": "Escalation Thresholds"`
  - [ ] `"incident_response.low": "Low"`
  - [ ] `"incident_response.medium": "Medium"`
  - [ ] `"incident_response.high": "High"`
  - [ ] `"incident_response.critical": "Critical"`
  - [ ] `"incident_response.minutes": "min"`
  - [ ] `"incident_response.sla_time": "SLA Response Time"`
  - [ ] `"incident_response.auto_actions": "Auto Actions"`
  - [ ] `"incident_response.block": "Block"`
  - [ ] `"incident_response.notify": "Notify"`
  - [ ] `"incident_response.escalate": "Escalate"`

---

### ЭТАП 4: ПРОВЕРКА И ТЕСТИРОВАНИЕ (30 минут)

- [ ] **4.1 Проверить компиляцию**
  - [ ] Скомпилировать проект
  - [ ] Убедиться что нет ошибок
  - [ ] Проверить что все ключи добавлены правильно

- [ ] **4.2 Проверить работу локализации**
  - [ ] Запустить приложение
  - [ ] Открыть NetworkProtectionScreen - проверить все 10 компонентов
  - [ ] Открыть ParentalControlScreen - проверить все 5 компонентов
  - [ ] Открыть AdvancedProtectionSettingsScreen - проверить все 13 компонентов
  - [ ] Открыть SettingsScreen - проверить все 5 компонентов
  - [ ] Проверить что все тексты отображаются на русском

- [ ] **4.3 Проверить переключение языка**
  - [ ] Переключить на английский язык
  - [ ] Проверить все экраны с компонентами
  - [ ] Убедиться что все тексты переведены на английский
  - [ ] Переключить обратно на русский
  - [ ] Проверить что все работает

- [ ] **4.4 Проверить отсутствие хардкода**
  - [ ] Проверить что нет хардкодных строк в коде
  - [ ] Все тексты используют `localizationManager.localized()`
  - [ ] Все ключи существуют в словаре

---

### ЭТАП 5: ДОКУМЕНТАЦИЯ И ФИНАЛИЗАЦИЯ (15 минут)

- [ ] **5.1 Обновить документацию**
  - [ ] Обновить `docs/ДЕТАЛЬНЫЙ_АНАЛИЗ_ЛОКАЛИЗАЦИИ_42_КОМПОНЕНТОВ.md`
  - [ ] Отметить что локализация завершена на 100%
  - [ ] Обновить статистику

- [ ] **5.2 Создать отчет о выполнении**
  - [ ] Список всех добавленных ключей
  - [ ] Статистика (сколько ключей добавлено)
  - [ ] Результаты тестирования

---

## 📊 ИТОГОВАЯ СТАТИСТИКА:

### Что нужно добавить:

#### В LocalizationManager.swift (словарь translations):
- **Новый формат (42 компонента):** 84 ключа × 2 языка = **168 строк**
- **Старый формат (18 компонентов):** 36 ключей × 2 языка = **72 строки**
- **Разделы (5 разделов):** 10 ключей × 2 языка = **20 строк**
- **Общие ключи (7 ключей):** 7 ключей × 2 языка = **14 строк**
- **Дополнительные ключи (5 ключей):** 5 ключей × 2 языка = **10 строк**
- **Аккордеоны (4 ключа):** 4 ключа × 2 языка = **8 строк**
- **Password Generator (8 ключей):** 8 ключей × 2 языка = **16 строк**
- **Incident Response (11 ключей):** 11 ключей × 2 языка = **22 строки**

**ИТОГО в LocalizationManager.swift:** 168 + 72 + 20 + 14 + 10 + 8 + 16 + 22 = **330 строк**

#### В файлы Localizable.strings (старый формат):
- **SettingsScreen (5 компонентов):** 10 ключей × 2 языка = **20 строк**

**ИТОГО в файлы:** **20 строк**

### Общий итог:
- **Всего строк для добавления:** 330 + 20 = **350 строк**
- **Всего ключей:** 84 + 36 + 10 + 7 + 5 + 4 + 8 + 11 = **165 ключей**

---

## ✅ КРИТЕРИИ ЗАВЕРШЕНИЯ:

### Минимальные требования:
- [ ] Все 42 компонента имеют ключи в словаре `translations`
- [ ] Все ключи работают на русском языке
- [ ] Все ключи работают на английском языке
- [ ] Нет ошибок компиляции
- [ ] Все экраны отображают правильные переводы

### Идеальные требования:
- [ ] Все ключи добавлены
- [ ] Все переводы корректны
- [ ] Нет хардкода строк
- [ ] Переключение языка работает идеально
- [ ] Все тесты пройдены

---

## 🎯 СЛЕДУЮЩИЙ ЭТАП (ПОСЛЕ ЛОКАЛИЗАЦИИ):

### ЭТАП 6: ИСПРАВЛЕНИЕ FALLBACK (после завершения локализации)

- [ ] **6.1 Добавить fallback в ComponentStatusService**
  - [ ] Обработка ошибок при загрузке компонентов
  - [ ] Использование дефолтных значений если API не отвечает
  - [ ] НЕ показывать ошибку пользователю

- [ ] **6.2 Тестирование fallback**
  - [ ] Проверить работу без интернета
  - [ ] Проверить работу при ошибке сервера
  - [ ] Убедиться что приложение не крашится

---

**Дата создания:** 13 января 2026  
**Статус:** 🔴 ГОТОВ К ВЫПОЛНЕНИЮ  
**Приоритет:** КРИТИЧЕСКИЙ

