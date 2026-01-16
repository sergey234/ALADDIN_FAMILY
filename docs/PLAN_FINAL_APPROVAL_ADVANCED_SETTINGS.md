# ✅ План финального согласования: “Расширенные настройки” + сохранение + локализация (RU/EN)
**Дата:** 2026‑01‑15  
**Цель:** зафиксировать согласованную структуру “Расширенных настроек”, источники истины для всех тумблеров/переключателей, навигацию (без переходов на другие экраны — только модалки), гарантии сохранения при выходе из приложения, и полный список локализаций RU/EN, необходимых для UI.

---

## 0) Правила (как работаем)
- **Один источник истины** на каждую настройку: либо `ComponentStatusService` (42 компонента), либо `@AppStorage/UserDefaults` (семья), либо `ContentBlockerManager` (Safari).
- **Автосохранение сразу** — только там, где нет кнопки “Сохранить”.
- Где кнопка **“Сохранить”** есть — **не меняем UX**, проверяем сохранение/загрузку.
- Исправляем **по одному пункту** и проверяем сценарий “вышел → зашёл → не сбросилось”.

---

## 1) Итоговая структура страницы `Screens/AdvancedProtectionSettingsScreen.swift`

### 1.0 Визуальные акценты (цвета в “Настройках”)
Цель: в UI “Настроек” получить 3 понятных цветовых зоны:
- **Улучшить защиту** — **золотой** (оставляем как сейчас)
- **Расширенные настройки** — **фиолетовый** (как цвет иконки премиум тарифа на экране тарифов)
- **История защиты** — **синий** (оставляем как сейчас)

Требование к реализации:
- фиолетовый акцент применяется к заголовку/иконке/рамке (не к фону всего экрана), чтобы не ломать читабельность
- цвет берём из существующего дизайн‑токена/палитры “премиум” (не создаём случайный новый оттенок)

### 1.1 Аккордеон: **Safari**
**Две отдельные карточки (как в бэкапе по смыслу):**

1) **Фильтрация сайтов**
- **Тумблер:** “честный” — показывает реальный `SFContentBlockerManager state.isEnabled`.
- **Статус:** `enabled / needsActivation / error`.
- **Детали:** `.sheet` → `FamilyContentBlockModal` (категории/правила).
- **Preset категорий (без ads/trackers):** `adult + violence + gambling + forums + fileSharing` (обсуждаемо).

2) **Ограничение соцсетей**
- **Тумблер:** “честный” — тот же реальный статус Safari blocker.
- **Смысл:** быстрый включатель пресета категории `socialMedia` (и только её).
- **Детали:** `.sheet` → `FamilyContentBlockModal` (если хотим дать ручную настройку).

**Источник истины:** `ContentBlockerManager` (`Core/ContentBlocker/ContentBlockerManager.swift`)  
**Персистентность:** правила в App Group (`contentBlockerRules`) + выбранные категории в `UserDefaults` (`contentBlockerActiveCategories`).  
**Сервер:** не требуется (это системная настройка Safari).

### 1.2 Аккордеон: **Контроль и мониторинг (семья)**
Цель: без переходов на другие экраны — только `.sheet` модалки.

Карточки:
- **Мониторинг активности**
  - Метрики: сайты/приложения (серверные `getParentalControlStats` + локальные детали из `parental_monitoring_stats`).
  - 2 тумблера внутри: `parental_messages_monitoring`, `parental_screenshots_enabled` (оба `@AppStorage`).
  - Детали: `.sheet` → `FamilyMonitoringModal`.

- **Контроль времени**
  - Метрики: время/лимит (локально из `parental_time_stats`, плюс серверные stats где есть).
  - Детали: `.sheet` → `FamilyTimeControlModal`.

- **Лимиты приложений**
  - Источник: `UserDefaults` ключ `app_limits_settings` (в `AppLimitsSettingsModal`).
  - Детали: `.sheet` → `AppLimitsSettingsModal`.

**Источник истины:** `@AppStorage` (включатели) + `UserDefaults` (детальные настройки) + серверные метрики через `APIService.getParentalControlStats`.

### 1.3 Аккордеон: **Защита от угроз (42 компонента)**
**Одна агрегирующая карточка “Блокировка угроз”** (без переходов):
- Управляет/отражает группу компонент:
  - `phishing_protection_agent`
  - `malware_detection_agent`
  - `mobile_security_agent`
  - `network_security_agent`
- Статус: “Вкл / Выкл / Частично”.
- Детали: открываем существующие модалки настроек (как `.sheet`) без навигации на другой экран.

**Источник истины:** `ComponentStatusService` (+ кэш `ComponentCacheService` + попытка серверного обновления).

### 1.4 Остальные аккордеоны (уже есть)
- **Защита в мессенджерах** (13 экран уже содержит 6 карточек)
- **Приватность**
- **Мониторинг**

---

## 2) Навигация и модалки (чтобы “не было переходов”)
Всё открываем через `.sheet`:
- `FamilyContentBlockModal`
- `FamilyMonitoringModal`
- `FamilyTimeControlModal`
- `AppLimitsSettingsModal`
- 4 модалки Threat protection (phishing/malware/mobile/network)

**Правило:** никаких `NavigationLink` на отдельные страницы ради этих 7 карточек.

---

## 3) Сохранение при выходе из приложения (гарантии)
### 3.1 Safari (Content Blocker)
- Правила сохраняются в App Group сразу при применении.
- “Честный тумблер” отражает только системный `state.isEnabled` (не пытаемся “принудительно включить Safari”, это невозможно).
- При возвращении в приложение: обновляем статус через `checkBlockingStatus()` (в идеале — на `onAppear` и при возврате из background).

### 3.2 Семья (Monitoring/Time/App limits)
- Тумблеры должны быть только `@AppStorage` (уже так).
- Детальные значения:
  - monitoring: `parental_monitoring_stats`
  - time: `parental_time_stats`
  - app limits: `app_limits_settings`
- Проверка: kill app → launch → значения на месте.

### 3.3 42 компонента
- Используем `ComponentStatusService.updateStatus` (пишет в кэш и пытается на сервер).
- Если сервер не поддерживает метод (405/patch fallback), локальный кэш должен сохранять состояние.
- Проверка: toggle → выйти → зайти → состояние восстановлено из кэша.

---

## 4) Локализация RU/EN (полный охват для новых элементов)
### 4.1 Уже есть ключи
Для ContentBlockModal уже есть `content_block_*` RU/EN и `family_content_block_modal_title`.

### 4.2 Нужно добавить новые ключи для 2 Safari‑карточек (если отсутствуют)
Новые ключи (предлагаемый нейминг):
- `advanced_safari_section_title` / `advanced_safari_section_subtitle`
- `advanced_safari_sites_filter_title` / `advanced_safari_sites_filter_subtitle`
- `advanced_safari_social_restriction_title` / `advanced_safari_social_restriction_subtitle`
- `advanced_safari_status_enabled` / `advanced_safari_status_needs_activation` / `advanced_safari_status_error`
- `advanced_open_settings` (если нужен отдельный текст на карточке, а не reuse `content_block_open_settings`)
- `advanced_configure` (если нужен отдельный текст, иначе reuse существующих)

### 4.3 Missing‑аудит
После добавления новых UI‑ключей: пересобрать `docs/AUDIT_LOCALIZATION_MISSING_KEYS_ACTIVE.json` и убедиться, что новые ключи не попали в missing.

---

## 5) Факт‑чек документации
Документ `docs/ПОЛНАЯ_КАРТА_42_КОМПОНЕНТОВ.md` **расходится** с фактическим `ParentalControlScreen` по `componentId`.  
Требуется обновить документ по реальным `componentId`:
- `self_harm_detection_agent`
- `grooming_detection_agent`
- `online_predators_agent`
- `psychological_support_agent`
- `parental_control_bot`

---

## 6) План “по шагам” (последовательность работ)
1) Добавить в Advanced Settings аккордеон Safari + 2 карточки (фильтрация сайтов / соцсети) с честным статусом.
2) Подключить `.sheet` → `FamilyContentBlockModal` и обновление статуса при возвращении из настроек.
3) Добавить “Контроль и мониторинг (семья)” с 3 карточками (Monitoring/Time/App limits) и `.sheet` модалками.
4) Добавить агрегирующую карточку “Блокировка угроз” (группа 4 компонент) + sheets на настройки.
5) Добавить RU/EN ключи для новых названий/статусов (если не reuse).
6) Прогнать аудит missing keys + проверить ручной сценарий сохранения (kill app).


