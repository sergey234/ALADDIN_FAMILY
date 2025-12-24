# 📋 ИНСТРУКЦИЯ: СОЗДАНИЕ PROVISIONING PROFILE ДЛЯ CONTENT BLOCKER EXTENSION

## ❌ Проблема

Ошибка сборки:
```
error: Provisioning profile "ALADDIN App Store Distribution" has app ID "family.aladdin.ios", 
which does not match the bundle ID "family.aladdin.ios.ALADDINContentBlocker".
```

**Причина:** Provisioning profile создан только для основного приложения, но не поддерживает App Extension.

## ✅ Решение

Нужно создать **отдельный provisioning profile** для Content Blocker Extension.

---

## 📝 ШАГ 1: Проверка App ID для Extension

1. Откройте **Apple Developer Portal**: https://developer.apple.com/account/resources/identifiers/list
2. Найдите App ID: **`family.aladdin.ios.ALADDINContentBlocker`**
3. Если его **НЕТ** - нужно создать (см. ШАГ 2)
4. Если он **ЕСТЬ** - переходите к ШАГ 3

---

## 📝 ШАГ 2: Создание App ID для Extension (если не существует)

1. В **Apple Developer Portal** → **Certificates, Identifiers & Profiles** → **Identifiers**
2. Нажмите **"+"** (синяя кнопка вверху справа)
3. Выберите **"App IDs"** → **Continue**
4. Выберите **"App"** → **Continue**
5. Заполните:
   - **Description**: `ALADDIN Content Blocker Extension`
   - **Bundle ID**: Выберите **"Explicit"** и введите: `family.aladdin.ios.ALADDINContentBlocker`
6. В разделе **"Capabilities"** включите:
   - ✅ **App Groups** (если еще не включено)
   - ✅ **App Extensions** (если доступно)
7. Нажмите **"Continue"** → **"Register"**

---

## 📝 ШАГ 3: Создание Provisioning Profile для Extension

1. В **Apple Developer Portal** → **Certificates, Identifiers & Profiles** → **Profiles**
2. Нажмите **"+"** (синяя кнопка вверху справа)
3. Выберите **"App Store"** (для App Store Distribution) → **Continue**
4. В разделе **"App ID"** выберите: **`family.aladdin.ios.ALADDINContentBlocker`** → **Continue**
5. Выберите **сертификат** "Apple Distribution: SERGEY KHLYSTOV" → **Continue**
6. Введите **Name**: `ALADDINContentBlocker App Store Distribution` → **Generate**
7. **Скачайте** профиль (`.mobileprovision` файл)

---

## 📝 ШАГ 4: Извлечение UUID нового профиля

1. Откройте скачанный файл `.mobileprovision` в текстовом редакторе
2. Найдите строку: `<key>UUID</key>`
3. Скопируйте UUID из следующей строки: `<string>XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX</string>`
4. **Сохраните этот UUID** - он понадобится для GitHub Secrets

**Пример:**
```xml
<key>UUID</key>
<string>a1b2c3d4-e5f6-7890-abcd-ef1234567890</string>
```
UUID: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

---

## 📝 ШАГ 5: Base64 кодирование профиля

1. Откройте терминал
2. Выполните команду (замените путь на ваш):
```bash
base64 -i ~/Downloads/ALADDINContentBlocker_App_Store_Distribution.mobileprovision | pbcopy
```
3. Base64 содержимое скопировано в буфер обмена

**Или сохраните в файл:**
```bash
base64 -i ~/Downloads/ALADDINContentBlocker_App_Store_Distribution.mobileprovision > ~/Downloads/extension_profile_base64.txt
```

---

## 📝 ШАГ 6: Обновление GitHub Secrets

1. Откройте **GitHub** → Ваш репозиторий → **Settings** → **Secrets and variables** → **Actions**
2. Добавьте/обновите следующие секреты:

### Секрет 1: `PROVISIONING_PROFILE_EXTENSION_UUID`
- **Name**: `PROVISIONING_PROFILE_EXTENSION_UUID`
- **Value**: UUID из ШАГ 4 (например: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

### Секрет 2: `PROVISIONING_PROFILE_EXTENSION`
- **Name**: `PROVISIONING_PROFILE_EXTENSION`
- **Value**: Base64 содержимое из ШАГ 5 (весь текст из файла)

---

## 📝 ШАГ 7: Обновление Fastfile

Нужно обновить `fastlane/Fastfile`, чтобы использовать отдельный профиль для extension.

**Текущая проблема:** Fastfile использует один и тот же профиль для обоих таргетов.

**Решение:** Использовать отдельные секреты для extension:
- `PROVISIONING_PROFILE_APP` - для основного приложения
- `PROVISIONING_PROFILE_EXTENSION` - для extension

---

## 📋 Чек-лист

- [ ] App ID `family.aladdin.ios.ALADDINContentBlocker` создан в Apple Developer Portal
- [ ] Provisioning Profile для extension создан и скачан
- [ ] UUID профиля извлечен
- [ ] Base64 профиля создан
- [ ] GitHub Secrets обновлены:
  - [ ] `PROVISIONING_PROFILE_EXTENSION_UUID`
  - [ ] `PROVISIONING_PROFILE_EXTENSION`
- [ ] Fastfile обновлен для использования отдельного профиля extension

---

## ⚠️ Важно

- **Не используйте** один и тот же provisioning profile для основного приложения и extension
- Extension требует **отдельный App ID** и **отдельный provisioning profile**
- Оба профиля должны использовать **один и тот же сертификат** (Apple Distribution)

---

## 🔗 Полезные ссылки

- Apple Developer Portal: https://developer.apple.com/account/resources/identifiers/list
- GitHub Secrets: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

