# 📋 ИНСТРУКЦИЯ: НАСТРОЙКА PROVISIONING PROFILE ДЛЯ CONTENT BLOCKER EXTENSION

## 🎯 Что это такое простым языком?

**Provisioning Profile (Профиль подготовки)** — это файл, который связывает:
- Ваше приложение (bundle identifier)
- Ваш Apple Developer аккаунт
- Сертификат для подписи кода
- Устройства, на которые можно установить приложение

**Проблема:** Если у вас есть основное приложение (`family.aladdin.ios`) и расширение (`family.aladdin.ios.ALADDINContentBlocker`), то provisioning profile должен поддерживать **ОБА** bundle identifier.

---

## ✅ ШАГ 1: Проверить текущий профиль

### 1.1. Откройте Apple Developer Portal
- Перейдите на: https://developer.apple.com/account
- Войдите в свой аккаунт

### 1.2. Перейдите в раздел Profiles
- В левом меню нажмите **"Certificates, Identifiers & Profiles"**
- В разделе **"Profiles"** нажмите **"All"** (или **"All Profiles"**)

### 1.3. Найдите ваш профиль
- Найдите профиль с UUID: `4dc2e0ff-f7bd-4ac0-aca8-98143ea99e7f`
- Или найдите профиль с именем, содержащим "ALADDIN" или "family.aladdin.ios"
- Нажмите на него, чтобы открыть детали

### 1.4. Проверьте App ID
- В разделе **"App ID"** должно быть указано: `family.aladdin.ios`
- Нажмите на этот App ID, чтобы открыть его детали

---

## 🔍 ШАГ 2: Проверить, поддерживает ли App ID расширения

### 2.1. Откройте App ID детали
- В разделе **"App Services"** или **"Capabilities"** проверьте:
  - ✅ **App Groups** (должно быть включено)
  - ✅ **App Extensions** (должно быть включено)

### 2.2. Если App Extensions НЕ включено:
- Нажмите **"Edit"** (редактировать)
- Найдите **"App Extensions"** в списке
- Поставьте галочку ✅
- Нажмите **"Continue"**
- Нажмите **"Save"**

---

## 📝 ШАГ 3: Создать или обновить Provisioning Profile

### 3.1. Если профиль НЕ поддерживает расширение:

#### Вариант А: Обновить существующий профиль
1. Вернитесь в раздел **"Profiles"**
2. Найдите ваш профиль (`4dc2e0ff-f7bd-4ac0-aca8-98143ea99e7f`)
3. Нажмите **"Edit"** (редактировать)
4. Убедитесь, что выбран правильный **App ID** (`family.aladdin.ios`)
5. Убедитесь, что выбран правильный **Certificate** (Apple Distribution)
6. Нажмите **"Generate"** (сгенерировать)
7. Дождитесь создания нового профиля
8. Нажмите **"Download"** (скачать)
9. Сохраните файл `.mobileprovision` на компьютер

#### Вариант Б: Создать новый профиль (если обновление не помогло)
1. В разделе **"Profiles"** нажмите **"+"** (плюс) в правом верхнем углу
2. Выберите тип: **"App Store"** (для App Store)
3. Нажмите **"Continue"**
4. Выберите **App ID**: `family.aladdin.ios`
5. Нажмите **"Continue"**
6. Выберите **Certificate**: ваш Apple Distribution сертификат
7. Нажмите **"Continue"**
8. Введите **Profile Name**: например, "ALADDIN App Store with Content Blocker"
9. Нажмите **"Generate"**
10. Дождитесь создания
11. Нажмите **"Download"**
12. Сохраните файл `.mobileprovision` на компьютер

---

## 🔄 ШАГ 4: Обновить профиль в GitHub Secrets

### 4.1. Получить UUID нового профиля
1. Откройте скачанный файл `.mobileprovision` в текстовом редакторе
2. Найдите строку с `<key>UUID</key>`
3. Скопируйте значение UUID (например, `4dc2e0ff-f7bd-4ac0-aca8-98143ea99e7f`)

### 4.2. Обновить GitHub Secrets
1. Перейдите в ваш GitHub репозиторий: https://github.com/sergey234/ALADDIN_FAMILY
2. Нажмите **"Settings"** (Настройки)
3. В левом меню нажмите **"Secrets and variables"** → **"Actions"**
4. Найдите секрет **`APP_PROFILE_UUID`**
5. Нажмите **"Update"** (Обновить)
6. Вставьте новый UUID профиля
7. Нажмите **"Update secret"**

### 4.3. Обновить сам профиль в GitHub Secrets
1. В том же разделе **"Secrets and variables"** → **"Actions"**
2. Найдите секрет **`APP_PROFILE`** (или похожий)
3. Нажмите **"Update"**
4. Откройте скачанный файл `.mobileprovision` в текстовом редакторе
5. Скопируйте **ВЕСЬ** содержимое файла (от начала до конца)
6. Вставьте в поле секрета
7. Нажмите **"Update secret"**

---

## 🧪 ШАГ 5: Проверить, что профиль поддерживает оба bundle identifier

### 5.1. Проверить через команду (локально)
Откройте терминал и выполните:

```bash
# Замените путь на путь к вашему профилю
security cms -D -i ~/Downloads/ваш_профиль.mobileprovision | grep -A 1 "application-identifier"
```

Вы должны увидеть что-то вроде:
```
<key>application-identifier</key>
<string>6CJVBBUGSN.family.aladdin.ios</string>
```

### 5.2. Проверить через Apple Developer Portal
1. Откройте ваш App ID (`family.aladdin.ios`)
2. В разделе **"App Services"** проверьте:
   - ✅ **App Groups** включено
   - ✅ **App Extensions** включено
3. Если все включено, профиль должен поддерживать оба bundle identifier

---

## ⚠️ ВАЖНО: Проверка bundle identifier

### Правильные bundle identifier:
- ✅ `family.aladdin.ios` (основное приложение)
- ✅ `family.aladdin.ios.ALADDINContentBlocker` (Content Blocker Extension)

### Проверка в Xcode:
1. Откройте проект в Xcode
2. Выберите проект **"ALADDIN"** в Project Navigator
3. Выберите таргет **"ALADDIN"**
4. Перейдите на вкладку **"Signing & Capabilities"**
5. Проверьте **Bundle Identifier**: должно быть `family.aladdin.ios`
6. Выберите таргет **"ALADDINContentBlocker"**
7. Проверьте **Bundle Identifier**: должно быть `family.aladdin.ios.ALADDINContentBlocker`

---

## 🔧 ШАГ 6: Если ничего не помогло

### Альтернативное решение: Использовать отдельный профиль для расширения

1. Создайте **новый App ID** для расширения:
   - В разделе **"Identifiers"** → **"App IDs"**
   - Нажмите **"+"**
   - Выберите **"App"**
   - Введите **Description**: "ALADDIN Content Blocker Extension"
   - Введите **Bundle ID**: `family.aladdin.ios.ALADDINContentBlocker`
   - Включите **App Groups**
   - Нажмите **"Continue"** → **"Register"**

2. Создайте **новый Provisioning Profile** для расширения:
   - В разделе **"Profiles"** → **"+"**
   - Выберите **"App Store"**
   - Выберите новый App ID: `family.aladdin.ios.ALADDINContentBlocker`
   - Выберите сертификат
   - Скачайте профиль

3. Обновите **Fastfile**:
   - Добавьте новый UUID профиля в `EXT_PROFILE_UUID` (если нужно)
   - Или используйте тот же профиль, если он поддерживает оба bundle identifier

---

## ✅ Чеклист проверки

- [ ] App ID `family.aladdin.ios` имеет включенное **App Extensions**
- [ ] Provisioning Profile содержит правильный App ID
- [ ] Provisioning Profile скачан и обновлен в GitHub Secrets
- [ ] UUID профиля обновлен в `APP_PROFILE_UUID`
- [ ] Содержимое профиля обновлено в `APP_PROFILE`
- [ ] Bundle identifiers в Xcode правильные
- [ ] GitHub Actions запущен с новыми настройками

---

## 📞 Если нужна помощь

Если после выполнения всех шагов сборка все еще не работает:
1. Проверьте логи GitHub Actions
2. Убедитесь, что профиль действительно поддерживает оба bundle identifier
3. Проверьте, что сертификат не истек
4. Убедитесь, что Team ID правильный (`6CJVBBUGSN`)

---

**Дата создания:** 24 декабря 2025  
**Версия:** 1.0

