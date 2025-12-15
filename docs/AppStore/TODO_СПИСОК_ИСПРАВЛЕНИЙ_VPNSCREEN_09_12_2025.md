# ✅ TODO СПИСОК ИСПРАВЛЕНИЙ VPNScreen

**Дата:** 9 декабря 2025  
**Бэкап:** `Screens/03_VPNScreen.swift.backup_09_12_2025`

---

## 📋 СПИСОК ЗАДАЧ

### ✅ Выполнено

- [x] **vpn_1:** Создать бэкап файла `Screens/03_VPNScreen.swift`

---

### 🔄 В процессе

---

### ⏳ Ожидает выполнения

#### 1. Удаление карточек

- [ ] **vpn_2:** Удалить Connection Info Card (строки 176-255)
  - Файл: `Screens/03_VPNScreen.swift`
  - Функция: `connectionInfoCard`
  - Удалить из body (строка 62)

- [ ] **vpn_3:** Удалить Server Selection Card (строки 294-395)
  - Файл: `Screens/03_VPNScreen.swift`
  - Функция: `serverSelectionCard`
  - Удалить из body (строка 68)

- [ ] **vpn_4:** Удалить Statistics Card (строки 448-519)
  - Файл: `Screens/03_VPNScreen.swift`
  - Функция: `statisticsCard`
  - Удалить из body (строка 74)

- [ ] **vpn_5:** Удалить Third-Party VPN Detection Card (строки 725-769)
  - Файл: `Screens/03_VPNScreen.swift`
  - Функция: `thirdPartyVPNDetectionCard`
  - Удалить из body (строка 83)

---

#### 2. Изменение порядка карточек

- [ ] **vpn_6:** Переместить Antivirus Card наверх (1-я позиция в ScrollView)
  - Файл: `Screens/03_VPNScreen.swift`
  - Текущая позиция: 8-я (строка 80)
  - Новая позиция: 1-я
  - Переместить в body перед `vpnStatusCard`

- [ ] **vpn_9:** Переместить Безопасное соединение Status Card вниз (5-я позиция в ScrollView)
  - Файл: `Screens/03_VPNScreen.swift`
  - Текущая позиция: 1-я (строка 59)
  - Новая позиция: 5-я (после Quick Actions Card)
  - Переместить в body после `quickActionsCard`

---

#### 3. Упрощение Безопасное соединение Status Card

- [ ] **vpn_7:** Упростить VPN Status Card
  - Файл: `Screens/03_VPNScreen.swift`
  - Функция: `vpnStatusCard` (строки 106-174)
  - Удалить:
    - Большую иконку щита (строки 109-121)
    - Текст статуса "Защищено" / "Не защищено" (строки 124-136)
    - Описание (строка 131)
  - Оставить:
    - Заголовок: "Безопасное соединение"
    - Индикатор (красный/зеленый)
    - Кнопка включить/выключить

- [ ] **vpn_8:** Добавить индикатор (красный/зеленый) небольшого размера
  - Файл: `Screens/03_VPNScreen.swift`
  - Функция: `vpnStatusCard`
  - Добавить индикатор:
    - 🟢 Зеленый = Включено (`viewModel.isVPNEnabled == true`)
    - 🔴 Красный = Выключено (`viewModel.isVPNEnabled == false`)
    - Размер: 20x20 или 24x24

---

#### 4. Изменение Security Features Card

- [ ] **vpn_10:** Убрать "Шифрование" из Security Features Card
  - Файл: `Screens/03_VPNScreen.swift`
  - Функция: `securityFeaturesCard` (строки 398-446)
  - Удалить SecurityFeatureCard с шифрованием (строки 427-432)
  - Оставить:
    - Блокировка рекламы
    - Антитрекинг
    - Защита от угроз
  - Изменить сетку с 2x2 на 2x1 или 3x1

---

#### 5. Изменение Battery Saving Tip Card

- [ ] **vpn_11:** Заменить "VPN" на "Безопасное соединение" в Battery Saving Tip Card
  - Файл: `Screens/03_VPNScreen.swift`
  - Функция: `batterySavingTipCard` (строки 257-292)
  - Найти все упоминания "VPN" в тексте
  - Заменить на "Безопасное соединение"

---

#### 6. Переименование и локализация

- [ ] **vpn_12:** Заменить заголовок экрана "VPN" на "Безопасное соединение"
  - Файл: `Screens/03_VPNScreen.swift`
  - Строка 45: `title: localizationManager.localized("vpn_title")`
  - Изменить на: `title: localizationManager.localized("secure_connection_title")`
  - Добавить локализацию в `LocalizationManager.swift`

- [ ] **vpn_13:** Переименовать функцию `vpnStatusCard` в `secureConnectionStatusCard`
  - Файл: `Screens/03_VPNScreen.swift`
  - Переименовать функцию (строка 106)
  - Обновить вызов в body

- [ ] **vpn_14:** Обновить локализацию: заменить "VPN" на "Безопасное соединение"
  - Файл: `Core/Localization/LocalizationManager.swift`
  - Заменять по 1 записи за раз
  - Начать с:
    - `"vpn_title"` → `"secure_connection_title"`
    - `"vpn_subtitle"` → `"secure_connection_subtitle"`
    - И другие упоминания VPN

---

## 📊 ИТОГОВАЯ СТРУКТУРА

### Порядок карточек (после изменений):

```
VPNScreen
├── Навигация
│   └── Заголовок: "Безопасное соединение"
│
└── ScrollView
    ├── 1. Antivirus Card ⭐ (СВЕРХУ)
    │   ├── Заголовок: "Антивирус"
    │   ├── Toggle: включить/выключить
    │   ├── Статистика (4 показателя)
    │   └── Кнопка: "Запустить проверку"
    │
    ├── 2. Battery Saving Tip Card
    │   └── Текст без слова "VPN"
    │
    ├── 3. Security Features Card
    │   ├── Блокировка рекламы
    │   ├── Антитрекинг
    │   └── Защита от угроз
    │
    ├── 4. Quick Actions Card
    │   ├── Настройки
    │   ├── Статистика
    │   └── Помощь
    │
    └── 5. Безопасное соединение Status Card (СНИЗУ)
        ├── Заголовок: "Безопасное соединение"
        ├── Индикатор: 🟢/🔴
        └── Кнопка: Включить/Выключить
```

---

## ✅ ЧЕКЛИСТ ПРОВЕРКИ

После выполнения всех задач проверить:

- [ ] Все 4 карточки удалены
- [ ] Antivirus Card наверху
- [ ] Безопасное соединение Status Card внизу
- [ ] Безопасное соединение Status Card упрощен (только заголовок, индикатор, кнопка)
- [ ] Индикатор работает (зеленый/красный)
- [ ] Security Features Card без шифрования
- [ ] Battery Saving Tip Card без слова "VPN"
- [ ] Заголовок экрана: "Безопасное соединение"
- [ ] Локализация обновлена
- [ ] Приложение компилируется без ошибок
- [ ] Линтер не показывает ошибок

---

**Дата создания:** 09.12.2025  
**Статус:** TODO список всех исправлений

