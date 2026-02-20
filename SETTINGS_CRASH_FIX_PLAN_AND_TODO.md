# 🚨 SETTINGS SCREEN CRASH - ПОЛНЫЙ ПЛАН ИСПРАВЛЕНИЙ & TODO LIST

## 📊 СТАТУС ПРОЕКТА: BUILD 69

**Дата:** 20 февраля 2026
**Текущий статус:** ❌ Краш продолжается, но архитектура исправлена на 80%
**Следующие шаги:** Полная миграция на MVVM

---

## 🎯 ПРОБЛЕМА

**SettingsScreen крашится с EXC_BAD_ACCESS (SIGSEGV)** из-за бесконечной рекурсии в SwiftUI:
- Thread stack size exceeded due to excessive recursion
- Бесконечные вызовы `swift_getTypeByMangledName`
- Краш происходит при инициализации ScrollView/ZStack

**Корень проблемы:** Циклические зависимости в SwiftUI View identity через `@EnvironmentObject localizationManager`

---

## ✅ ЧТО УЖЕ СДЕЛАНО

### ✅ КОМПЛЕКТНО ВЫПОЛНЕННЫЕ ЗАДАЧИ:

#### 🔴 CRITICAL (Критические)
- [x] **Убрать 4 .id() modifiers с localizationManager.currentLanguage**
- [x] **Создать протоколы сервисов (NavigationService, LocalizationService, NotificationService, SecurityService, TariffService, APIService, PositioningService)**
- [x] **Создать LocalizedStrings struct с 58 ключами локализации**
- [x] **Создать SettingsViewModel с 23 @Published свойствами и dependency injection конструктором**
- [x] **Обновить номер сборки с 68 на 69 в project.pbxproj и Info.plist**
- [x] **Сделать коммит и push на GitHub со всеми изменениями**

---

## ❌ ЧТО ОСТАЛОСЬ СДЕЛАТЬ

### 🔴 CRITICAL (Критические - без этого краш не уйдет)

#### 1. ПОДКЛЮЧИТЬ VIEWMODEL К VIEW
- [ ] **Полностью подключить SettingsViewModel к SettingsScreen**
  - Убрать все `@EnvironmentObject localizationManager`
  - Убрать все `@State` переменные (20+ штук)
  - Убрать singleton менеджеры из View
  - Заменить на dependency injection через ViewModel

#### 2. ИСПРАВИТЬ КОМПИЛЯЦИЮ
- [ ] **Исправить конфликты mock классов**
- [ ] **Добавить правильные typealias**
- [ ] **Протестировать компиляцию без ошибок**

---

### 🟡 HIGH PRIORITY (Высокий приоритет)

#### 3. МИГРАЦИЯ СЕКЦИЙ НАСТРОЕК
- [ ] **Мигрировать Profile Section**
  - Перенести `storedName`/`storedAlias` в ViewModel
  - Кэшировать 8 локализаций
  - Заменить `localizationManager.localized()` на `viewModel.localizedStrings`

- [ ] **Мигрировать Security Section**
  - Перенести 9 @State переменных в ViewModel
  - Мигрировать `handleBiometricToggle()`
  - Мигрировать `initializeProtectionLevel()`
  - Кэшировать 15 локализаций

---

### 🟢 MEDIUM PRIORITY (Средний приоритет)

#### 4. ДОПОЛНИТЕЛЬНЫЕ СЕКЦИИ
- [ ] **Мигрировать Notifications Section**
  - Перенести `securityEnabled`/`soundEnabled` в ViewModel
  - Добавить синхронизацию с NotificationService

- [ ] **Мигрировать App Section**
  - Перенести `selectedTheme` в ViewModel
  - Мигрировать `cycleTheme()`/`applyTheme()`/`checkForUpdates()`
  - Кэшировать 8 локализаций

- [ ] **Мигрировать System Components Section**
  - Перенести `components`/`isLoadingComponents`/`componentsError` в ViewModel
  - Мигрировать `loadComponents()`/`toggleComponent()`
  - Кэшировать 5 локализаций

#### 5. ЛОГИКА ИНИЦИАЛИЗАЦИИ
- [ ] **Перенести всю логику из onAppear в ViewModel**
  - `initializeNotifications()`
  - Инициализацию состояний
  - `initializeProtectionLevel()`

---

### 🟣 LOW PRIORITY (Низкий приоритет - после устранения краша)

#### 6. ДОПОЛНИТЕЛЬНЫЕ ЗАДАЧИ
- [ ] **Мигрировать Additional Section**
  - Перенести `consentAccepted` в ViewModel
  - Создать навигационные методы
  - Кэшировать 10 локализаций

- [ ] **Сохранить все UI helper функции**
  - `settingRow()`, `settingsButton()`, `protectionActionButton()`
  - `percentText()`, `ComponentRow struct`

- [ ] **Создать AppCoordinator для dependency injection**
  - Реализовать все протоколы существующими сервисами
  - Фабрику для SettingsViewModel

- [ ] **Обновить модальные окна**
  - Заменить @EnvironmentObject на переданные сервисы в 15 sheet() вызовах

- [ ] **Обновить SettingsScreen конструктор**
  - Убрать @EnvironmentObject
  - Добавить @StateObject с ViewModel
  - Заменить все @State на $viewModel.property

#### 7. ТЕСТИРОВАНИЕ
- [ ] **Создать unit tests для SettingsViewModel**
  - Тестировать инициализацию, state changes, biometric toggle
  - Theme cycling, protection level calculation

- [ ] **Создать UI tests для SettingsScreen**
  - Загрузку без crash, отображение секций
  - Модальные окна, работу toggles

- [ ] **Интеграционное тестирование**
  - С real сервисами, изменения языка, изменения темы, API вызовы

- [ ] **Проверить Instruments**
  - Time Profiler для бесконечных циклов
  - Memory Graph для проверки leaks

#### 8. ДОКУМЕНТАЦИЯ
- [ ] **Обновить навигацию**
  - Заменить `navigationManager.navigateTo()` на `viewModel.navigateTo*()` методы

- [ ] **Документировать изменения**
  - Обновить `SETTINGS_CRASH_COMPLETE_ANALYSIS.md` с результатами миграции

---

## 🎯 ТЕКУЩИЙ СТАТУС И СЛЕДУЮЩИЕ ШАГИ

### 📍 НА ЧЕМ ОСТАНОВИЛИСЬ:
```
❌ SettingsScreen все еще использует старую архитектуру
❌ ViewModel не подключен к View
❌ Есть проблемы с компиляцией
❌ Краш продолжается
```

### 🚀 СЛЕДУЮЩИЕ ШАГИ (ПО ПРИОРИТЕТУ):

#### ЭТАП 1: УСТРАНИТЬ КРАШ (1-2 дня)
1. **Исправить компиляцию** - убрать конфликты mock классов
2. **Подключить ViewModel** - заменить @EnvironmentObject на ViewModel
3. **Протестировать без краша** - запустить приложение

#### ЭТАП 2: МИГРИРОВАТЬ СЕКЦИИ (2-3 дня)
4. **Мигрировать Profile и Security секции** - основные функциональные части
5. **Тестировать каждую секцию** - убедиться в работоспособности

#### ЭТАП 3: ДОСТРОИТЬ АРХИТЕКТУРУ (1-2 дня)
6. **Мигрировать остальные секции**
7. **Создать AppCoordinator**
8. **Интеграционное тестирование**

#### ЭТАП 4: ДОКУМЕНТАЦИЯ И ТЕСТЫ (1 день)
9. **Написать unit tests**
10. **Обновить документацию**
11. **Финальное тестирование**

---

## 📈 ПРОГРЕСС И МЕТРИКИ

### ✅ ВЫПОЛНЕНО: 30%
- Архитектура MVVM: **100% готова**
- Протоколы сервисов: **100% готовы**
- Локализации: **100% готовы**
- ViewModel: **80% готов**
- Build версия: **Обновлена**

### 🔄 В ПРОЦЕССЕ: 20%
- Подключение ViewModel к View: **0%**
- Миграция секций: **0%**

### ❌ ОСТАЛОСЬ: 50%
- Исправление компиляции
- Полная миграция UI
- Тестирование
- Документация

---

## 🏆 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После выполнения всех задач:
- ✅ **SettingsScreen не крашится**
- ✅ **Чистая MVVM архитектура**
- ✅ **Полная изоляция зависимостей**
- ✅ **Улучшенная поддерживаемость**
- ✅ **Unit и UI тесты**
- ✅ **Документация обновлена**

---

## 📋 ПРОВЕРКА ГОТОВНОСТИ К РЕЛИЗУ

### ТЕСТОВЫЕ СЦЕНАРИИ:
- [ ] Запуск SettingsScreen без краша
- [ ] Все секции отображаются корректно
- [ ] Переключение тем работает
- [ ] Биометрия включается/выключается
- [ ] Уведомления настраиваются
- [ ] Системные компоненты загружаются
- [ ] Все модальные окна открываются

### ПЕРФОРМАНС:
- [ ] Нет бесконечных циклов в Instruments
- [ ] Нет memory leaks
- [ ] Время загрузки < 2 секунд

### КОД КАЧЕСТВО:
- [ ] Unit tests coverage > 80%
- [ ] UI tests проходят
- [ ] Код соответствует MVVM паттерну
- [ ] Документация обновлена

---

## 🎯 КЛЮЧЕВЫЕ РИСКИ

1. **Комплексность миграции** - много секций для миграции
2. **Конфликты зависимостей** - нужно аккуратно заменить все сервисы
3. **Регрессии функциональности** - не сломать существующую логику
4. **Тестирование** - сложно тестировать все комбинации настроек

---

## 📞 КОНТАКТЫ И ПОДДЕРЖКА

**Ответственный:** iOS Developer Team
**Приоритет:** CRITICAL (краш приложения)
**Дедлайн:** 3-5 дней на полную миграцию
**Тестирование:** Требуется полное интеграционное тестирование

---

*Документ создан: 20 февраля 2026*
*Последнее обновление: 20 февраля 2026*
*Версия плана: 2.0*