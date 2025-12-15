# ❌❌❌ КРИТИЧЕСКАЯ ОШИБКА: PROVISIONING_PROFILE_EXTENSION ❌❌❌

## 🔴 Проблема

Секрет `PROVISIONING_PROFILE_EXTENSION` **НЕ УСТАНОВЛЕН** в GitHub Secrets!

В логах workflow видно:
```
❌ Extension profile not found: /Users/runner/Library/MobileDevice/Provisioning Profiles/extension.mobileprovision
Available profiles:
total 24
drwxr-xr-x  3 runner  staff     96 Dec  1 21:50 .
drwxr-xr-x  3 runner  staff     96 Dec  1 21:50 ..
-rw-r--r--  1 runner  staff  12182 Dec  1 21:50 app.mobileprovision
```

**Файл `extension.mobileprovision` отсутствует**, потому что секрет `PROVISIONING_PROFILE_EXTENSION` не установлен или пустой.

## ✅ Решение

### ШАГ 1: Получить Extension Provisioning Profile

1. **Зайдите в Apple Developer Portal:**
   - https://developer.apple.com/account/resources/profiles/list

2. **Создайте или проверьте наличие App Store Distribution профиля для Extension:**
   - **Bundle ID:** `family.aladdin.ios.packetTunnel`
   - **Тип:** `App Store` (НЕ Development, НЕ Ad Hoc!)
   - **Capabilities:** Должен содержать:
     - ✅ Network Extensions
     - ✅ Personal VPN

3. **Скачайте профиль:**
   - Нажмите на профиль
   - Нажмите "Download"
   - Сохраните файл (например, `extension.mobileprovision`)

### ШАГ 2: Закодировать профиль в base64

Выполните команду на вашем Mac:

```bash
cat extension.mobileprovision | base64
```

**ВАЖНО:** Скопируйте **ВЕСЬ** вывод (может быть очень длинным, несколько тысяч символов!)

### ШАГ 3: Добавить секрет в GitHub

1. **Зайдите в GitHub Settings:**
   - https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

2. **Найдите или создайте секрет:**
   - Имя: `PROVISIONING_PROFILE_EXTENSION`
   - Значение: Вставьте весь base64 из шага 2

3. **Сохраните секрет**

### ШАГ 4: Проверить App Profile

Убедитесь, что секрет `PROVISIONING_PROFILE_APP` также установлен и содержит **App Store Distribution** профиль (не Development!).

**Bundle ID:** `family.aladdin.ios`

## 🔍 Проверка

После добавления секрета:

1. **Запустите workflow снова:**
   - https://github.com/sergey234/ALADDIN_FAMILY/actions

2. **Проверьте шаг "Decode Extension Profile":**
   - Должен показать: `✅ Extension profile decoded successfully`
   - Не должно быть ошибки: `❌ PROVISIONING_PROFILE_EXTENSION secret is not set!`

3. **Проверьте шаг "Build Archive":**
   - Должен показать: `✅ Extension profile found: ...`
   - Не должно быть ошибки: `❌ Extension profile not found`

## 📋 Требования к профилю

### Extension Profile (`family.aladdin.ios.packetTunnel`)

- ✅ **Тип:** App Store Distribution (НЕ Development, НЕ Ad Hoc!)
- ✅ **Bundle ID:** `family.aladdin.ios.packetTunnel`
- ✅ **Capabilities:**
  - Network Extensions (`com.apple.developer.networking.networkextension`)
  - Personal VPN (`com.apple.developer.networking.vpn.api`)
- ✅ **Сертификат:** Должен быть связан с `Apple Distribution: SERGEY KHLYSTOV`

### App Profile (`family.aladdin.ios`)

- ✅ **Тип:** App Store Distribution (НЕ Development, НЕ Ad Hoc!)
- ✅ **Bundle ID:** `family.aladdin.ios`
- ✅ **Сертификат:** Должен быть связан с `Apple Distribution: SERGEY KHLYSTOV`

## ⚠️ Важно

- **НЕ используйте Development профили** для App Store сборки!
- **НЕ используйте Ad Hoc профили** для App Store сборки!
- **Только App Store Distribution профили** подходят для публикации в App Store!

## 🔗 Полезные ссылки

- **Apple Developer Portal (Profiles):** https://developer.apple.com/account/resources/profiles/list
- **GitHub Secrets:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
- **Workflow Runs:** https://github.com/sergey234/ALADDIN_FAMILY/actions

