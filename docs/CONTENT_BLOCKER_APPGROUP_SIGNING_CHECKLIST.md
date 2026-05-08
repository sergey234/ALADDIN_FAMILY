# Content Blocker: Проверка App Group и подписи

Этот чеклист нужен, чтобы Safari Content Blocker реально появился в iOS и включался без ошибок.

## 1) Что проверить в Apple Developer (веб)

Откройте [Apple Developer](https://developer.apple.com/account/resources/identifiers/list).

### Шаг 1. App ID приложения
- Найдите App ID: `family.aladdin.ios`
- Откройте его.
- Проверьте, что capability **App Groups** включен.
- В списке групп должна быть: `group.com.aladdin.family`

### Шаг 2. App ID extension
- Найдите App ID extension: `family.aladdin.ios.ALADDINContentBlocker`
- Откройте его.
- Проверьте, что capability **App Groups** включен.
- В списке групп должна быть та же группа: `group.com.aladdin.family`

### Шаг 3. Provisioning Profiles
Откройте [Profiles](https://developer.apple.com/account/resources/profiles/list).

Проверьте 2 профиля:
- профиль для `family.aladdin.ios`
- профиль для `family.aladdin.ios.ALADDINContentBlocker`

В каждом профиле:
- App Groups должны быть включены,
- должна быть выбрана `group.com.aladdin.family`.

Если группы нет:
- сначала добавьте App Group в Identifiers,
- затем пересоздайте профили.

---

## 2) Что проверить в Xcode

Откройте проект `ALADDIN.xcodeproj`.

### Target: ALADDIN
- Signing & Capabilities:
  - Team: ваш team
  - App Groups: включено
  - Есть `group.com.aladdin.family`

### Target: ALADDINContentBlocker
- Signing & Capabilities:
  - Team: тот же team
  - App Groups: включено
  - Есть `group.com.aladdin.family`

### Важно
- Bundle IDs должны совпадать с Apple Developer:
  - `family.aladdin.ios`
  - `family.aladdin.ios.ALADDINContentBlocker`

---

## 3) Обновить профили в Xcode

- Xcode -> Settings -> Accounts -> Apple ID -> Download Manual Profiles
  (или просто откройте Signing & Capabilities и дайте Xcode обновить автоматически)
- Product -> Clean Build Folder

---

## 4) Проверка на iPhone (не на Simulator)

1. Удалите старую версию приложения с iPhone.
2. Установите новую сборку из Xcode.
3. На iPhone откройте:
   - `Settings -> Apps -> Safari -> Extensions` (или `Content Blockers`)
4. Найдите `ALADDIN` и включите его.

---

## 5) Проверка в приложении

В приложении:
- Откройте расширенные настройки Safari-блокировки.
- Нажмите диагностику (`Run Safari diagnostics`).
- Ожидаемый результат:
  - статус не `extensionMissing`,
  - статус не `needsActivation` (после включения в iOS),
  - правила применяются без ошибки.

---

## 6) Если не работает

Проверьте по порядку:
- App Group не совпадает (опечатка в имени группы),
- профиль extension старый (без App Groups),
- extension не подписалась вашим Team,
- старая сборка не удалена с устройства,
- тест идёт на Simulator вместо iPhone.

