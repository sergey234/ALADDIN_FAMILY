# 📋 ПЛАН ЛОКАЛИЗАЦИИ: ТАРИФЫ И AI ЗАЩИТА

**Дата:** 2025-11-06  
**Статус:** 🔄 В РАБОТЕ

---

## 🎯 ЦЕЛЬ

Полностью локализовать:
1. **Экран тарифов (TariffsScreen)** - все элементы, включая AI защиту от угроз
2. **AI защита от всех типов угроз** - все разделы и угрозы внутри

---

## 📊 АНАЛИЗ НАЙДЕННЫХ ПРОБЛЕМ

### ✅ ЧТО УЖЕ ЛОКАЛИЗОВАНО:

#### TariffsScreen:
- ✅ Заголовок и подзаголовок экрана
- ✅ Названия тарифов (free, personal, family, premium)
- ✅ Периоды тарифов
- ✅ Список функций тарифов
- ✅ Кнопки (выбрать, оплатить QR)
- ✅ AI Protection заголовок и описание
- ✅ Кнопка сравнения тарифов
- ✅ TariffComparisonModal - большая часть локализована

#### AIAssistantScreen:
- ✅ Полностью локализован (все элементы используют localizationManager)

---

### ❌ ЧТО НЕ ЛОКАЛИЗОВАНО:

#### 1. TariffsScreen - ThreatCategory Enum (строки 695-770)

**Проблема:** Enum использует хардкод rawValue и массивы угроз

```swift
enum ThreatCategory: String, CaseIterable {
    case cyberThreats = "КИБЕРУГРОЗЫ"  // ❌ ХАРДКОД
    case fraud = "МОШЕННИЧЕСТВО"        // ❌ ХАРДКОД
    // ... и т.д.
    
    var threats: [String] {
        return ["Вирусы и трояны", "Ransomware", ...]  // ❌ ХАРДКОД
    }
}
```

**Что нужно:**
- ✅ `localizedTitle()` уже есть - работает
- ❌ `rawValue` не используется в UI - можно оставить как есть
- ❌ `threats` массив - ВСЕ УГРОЗЫ хардкод (100+ строк!)

**Всего угроз для локализации:**
- cyberThreats: 10 угроз
- fraud: 12 угроз
- childThreats: 17 угроз
- dataLeaks: 12 угроз
- deepfakes: 8 угроз
- internetThreats: 6 угроз
- mobileThreats: 10 угроз
- familyThreats: 15 угроз
- iotThreats: 10 угроз
- **ИТОГО: ~100 угроз**

#### 2. TariffsScreen - Error Messages (строки 395, 418, 451)

```swift
viewModel.errorMessage = "Ошибка создания тарифа. Попробуйте ещё раз."  // ❌ ХАРДКОД
viewModel.errorMessage = "Не удалось выбрать тариф. Попробуйте ещё раз."  // ❌ ХАРДКОД
viewModel.errorMessage = "Ошибка создания тарифа для покупки."  // ❌ ХАРДКОД
```

#### 3. TariffComparisonModal - Названия колонок (строки 868-886)

```swift
Text("FREE")      // ❌ ХАРДКОД
Text("BASIC")     // ❌ ХАРДКОД
Text("FAMILY")    // ❌ ХАРДКОД
Text("PREMIUM")   // ❌ ХАРДКОД
```

#### 4. TariffComparisonModal - Значения в таблице (строки 829-852)

Некоторые значения хардкод:
- "0₽", "290₽", "490₽", "990₽" - цены (можно оставить как есть)
- "1", "4", "6", "10" - количество устройств (можно оставить)
- "20+%", "50+%", "80+%", "100%" - защита (можно оставить)
- "50МБ/дн", "∞" - VPN трафик (нужно локализовать "∞" и "50МБ/дн")

---

## 📝 ПЛАН РАБОТЫ

### ЭТАП 1: Подготовка ключей локализации

#### Шаг 1.1: Добавить ключи для ошибок тарифов
- `tariffs_error_create_tariff` - "Ошибка создания тарифа. Попробуйте ещё раз."
- `tariffs_error_select_tariff` - "Не удалось выбрать тариф. Попробуйте ещё раз."
- `tariffs_error_purchase_tariff` - "Ошибка создания тарифа для покупки."

#### Шаг 1.2: Добавить ключи для названий колонок сравнения
- `tariffs_comparison_column_free` - "FREE"
- `tariffs_comparison_column_basic` - "BASIC"
- `tariffs_comparison_column_family` - "FAMILY"
- `tariffs_comparison_column_premium` - "PREMIUM"

#### Шаг 1.3: Добавить ключи для VPN трафика
- `tariffs_comparison_vpn_limited` - "50МБ/дн"
- `tariffs_comparison_vpn_unlimited` - "∞"

#### Шаг 1.4: Добавить ключи для ВСЕХ угроз (100+ ключей)

**Формат ключей:**
```
tariffs_threat_cyber_1 = "Вирусы и трояны"
tariffs_threat_cyber_2 = "Ransomware"
tariffs_threat_cyber_3 = "Шпионское ПО"
...
tariffs_threat_fraud_1 = "Телефонное мошенничество"
...
```

**Всего категорий: 9**
**Всего угроз: ~100**

---

### ЭТАП 2: Изменение кода

#### Шаг 2.1: Исправить errorMessage в TariffsScreen
Заменить хардкод строки на `localizationManager.localized("key")`

#### Шаг 2.2: Исправить названия колонок в TariffComparisonModal
Заменить хардкод на локализованные ключи

#### Шаг 2.3: Исправить VPN трафик в TariffComparisonModal
Заменить хардкод на локализованные ключи

#### Шаг 2.4: Изменить ThreatCategory.threats
Создать метод `localizedThreats(_ localizationManager: LocalizationManager) -> [String]`

**Пример:**
```swift
func localizedThreats(_ localizationManager: LocalizationManager) -> [String] {
    switch self {
    case .cyberThreats:
        return [
            localizationManager.localized("tariffs_threat_cyber_1"),
            localizationManager.localized("tariffs_threat_cyber_2"),
            // ... и т.д.
        ]
    // ... для всех категорий
    }
}
```

#### Шаг 2.5: Обновить использование threats в UI
Заменить `category.threats` на `category.localizedThreats(localizationManager)`

---

### ЭТАП 3: Проверка

#### Шаг 3.1: Проверить на дубликаты ключей
```bash
python3 scripts/check_localization_duplicates.py
```

#### Шаг 3.2: Проверить компиляцию
```bash
# В Xcode: Build (Cmd+B)
```

#### Шаг 3.3: Проверить работу в приложении
- Переключить язык на английский
- Проверить все элементы тарифов
- Проверить AI защиту от угроз
- Проверить модальное окно сравнения

---

## 📋 ЧЕКЛИСТ ВЫПОЛНЕНИЯ

### Подготовка:
- [ ] Добавить ключи для ошибок (3 ключа)
- [ ] Добавить ключи для колонок сравнения (4 ключа)
- [ ] Добавить ключи для VPN трафика (2 ключа)
- [ ] Добавить ключи для всех угроз (~100 ключей)

### Изменение кода:
- [ ] Исправить errorMessage в TariffsScreen
- [ ] Исправить названия колонок в TariffComparisonModal
- [ ] Исправить VPN трафик в TariffComparisonModal
- [ ] Создать метод localizedThreats() в ThreatCategory
- [ ] Обновить использование threats в UI

### Проверка:
- [ ] Проверить на дубликаты ключей
- [ ] Проверить компиляцию
- [ ] Проверить работу в приложении

---

## 🔍 ДЕТАЛЬНЫЙ СПИСОК УГРОЗ

### 1. Киберугрозы (10):
1. Вирусы и трояны
2. Ransomware
3. Шпионское ПО
4. Ботнеты
5. DDoS атаки
6. Фишинговые сайты
7. Поддельные приложения
8. Вредоносные ссылки
9. Криптовалютные майнеры
10. Руткиты

### 2. Мошенничество (12):
1. Телефонное мошенничество
2. Финансовое мошенничество
3. Медицинские аферы
4. Социальная инженерия
5. Поддельные банки
6. Фишинговые письма
7. Мошенничество с картами
8. Инвестиционные пирамиды
9. Лотерейные мошенничества
10. Романтические аферы
11. Vishing (голосовой фишинг)
12. Smishing (SMS фишинг)

### 3. Детские угрозы (17):
1. Неподходящий контент
2. Кибербуллинг
3. Опасные знакомства
4. Игровая зависимость
5. Случайные покупки
6. Взрослые сайты
7. Насилие в играх
8. Наркотики и алкоголь
9. Азартные игры
10. Экстремистский контент
11. Self-harm content
12. Inappropriate advertisements
13. Online predators
14. Grooming атаки
15. Catfishing
16. Toxic gaming communities
17. Online gambling addiction

### 4. Утечки данных (12):
1. Кража паролей
2. Компрометация аккаунтов
3. Утечки персональных данных
4. Нарушение приватности
5. Слежка за семьей
6. Утечки в темной сети
7. Утечки метаданных
8. Keyloggers
9. Session hijacking
10. Tracking cookies
11. Location tracking
12. EXIF data leaks

### 5. Подделки (8):
1. Deepfake видео
2. Поддельные голоса
3. Спуфинг номеров
4. Поддельные сайты
5. Фейковые новости
6. Поддельные документы
7. Fake dating profiles
8. Email spoofing

### 6. Интернет-угрозы (6):
1. Опасные сайты
2. Вредоносная реклама
3. Подозрительные загрузки
4. Небезопасные Wi-Fi
5. DNS-спуфинг
6. Man-in-the-middle атаки

### 7. Мобильные угрозы (10):
1. Вредоносные приложения
2. SMS-мошенничество
3. Поддельные уведомления
4. Кража данных с телефона
5. Геолокационные угрозы
6. Bluetooth-атаки
7. SIM swapping
8. Fake mobile banking apps
9. Mobile ransomware
10. Screen recorders

### 8. Семейные угрозы (15):
1. Домашнее насилие в сети
2. Семейные конфликты
3. Изоляция от семьи
4. Эмоциональные проблемы
5. Психологическое давление
6. Cyberstalking
7. Digital harassment
8. Online disputes
9. Family member impersonation
10. Digital isolation
11. Online depression triggers
12. Online manipulation
13. Gaslighting в сети
14. Family privacy violations
15. Unauthorized family member access

### 9. Умный дом (10):
1. Взлом умных устройств
2. Вторжение в умный дом
3. Скомпрометированные камеры
4. Подслушивание через умную колонку
5. Взлом домашней сети
6. Утечка данных умных устройств
7. Манипуляция голосовыми командами
8. Слабые пароли устройств
9. Использование паролей по умолчанию
10. Кража умного устройства

**ИТОГО: 100 угроз**

---

## ✅ СОГЛАСОВАННЫЕ ПРАКТИКИ

### Используем:
1. ✅ `localizationManager.localized("key")` для всех строк
2. ✅ Методы локализации в enums (`localizedTitle()`, `localizedThreats()`)
3. ✅ `.id("screen_lang_\(localizationManager.currentLanguage.rawValue)")` для перерисовки
4. ✅ Проверка на дубликаты перед коммитом
5. ✅ Добавление ключей в оба словаря одновременно

### Формат ключей:
- `tariffs_*` - для тарифов
- `tariffs_threat_<category>_<number>` - для угроз
- `tariffs_comparison_*` - для сравнения
- `tariffs_error_*` - для ошибок

---

## 🚀 НАЧАЛО РАБОТЫ

Готов начать локализацию по этому плану. Все элементы будут использовать `localizationManager.localized()` согласно нашим согласованным практикам.



