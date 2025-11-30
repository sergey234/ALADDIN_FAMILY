# ✅ ПРОВЕРКА API КЛЮЧЕЙ И ЗАПУСК WORKFLOW

## 🔍 ШАГ 1: Проверка GitHub Secrets

### Откройте страницу Secrets:
https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

### Проверьте наличие следующих секретов:

#### ✅ Обязательные для Automatic signing:
1. **APP_STORE_CONNECT_API_KEY** 
   - Должен содержать содержимое файла `.p8` (приватный ключ)
   - Формат: `-----BEGIN PRIVATE KEY-----...-----END PRIVATE KEY-----`

2. **APP_STORE_CONNECT_ISSUER_ID**
   - UUID вида: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - Находится в App Store Connect → Users and Access → Keys

3. **APP_STORE_CONNECT_API_KEY_ID**
   - ID ключа (например: `ABC123DEF4`)
   - Находится в App Store Connect → Users and Access → Keys

#### ✅ Дополнительные (для Manual signing, если Automatic не сработает):
4. **APPLE_TEAM_ID**
   - Team ID (например: `6CJVBBUGSN`)

5. **IOS_DISTRIBUTION_CERTIFICATE** (опционально)
   - Base64-encoded `.p12` файл

6. **IOS_DISTRIBUTION_CERTIFICATE_PASSWORD** (опционально)
   - Пароль от `.p12` файла

7. **PROVISIONING_PROFILE_APP** (опционально)
   - Base64-encoded `.mobileprovision` файл для основного приложения

8. **PROVISIONING_PROFILE_EXTENSION** (опционально)
   - Base64-encoded `.mobileprovision` файл для Extension

---

## 🚀 ШАГ 2: Запуск Workflow

### Способ 1: Автоматический запуск (через push)
Workflow запустится автоматически при push в master.

### Способ 2: Ручной запуск (через GitHub UI)
1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
2. Нажмите **"Run workflow"** (справа вверху)
3. Выберите ветку: **master**
4. Нажмите зеленую кнопку **"Run workflow"**

---

## 📊 ШАГ 3: Проверка результата

### Откройте страницу Actions:
https://github.com/sergey234/ALADDIN_FAMILY/actions

### Что проверять:

#### ✅ Успешный запуск:
- Статус: **зеленый** (Success)
- Время выполнения: ~5-10 минут
- Артефакты: должен быть создан `ALADDIN-IPA`

#### ❌ Ошибки:

**Ошибка 1: "No Accounts"**
```
error: No Accounts: Add a new account in Accounts settings.
```
**Решение:** Automatic signing не работает в CI. Нужно использовать Manual signing с пересозданными профилями.

**Ошибка 2: "Provisioning profile doesn't include signing certificate"**
```
error: Provisioning profile doesn't include signing certificate
```
**Решение:** Профили не связаны с сертификатом. Нужно пересоздать профили в Developer Portal.

**Ошибка 3: "API keys not set"**
```
❌ App Store Connect API keys not set!
```
**Решение:** Добавить API ключи в GitHub Secrets.

---

## 📝 ЛОГИ И ДИАГНОСТИКА

### Просмотр логов:
1. Откройте запуск workflow
2. Нажмите на job **"Build and Upload to App Store Connect"**
3. Разверните шаг **"Building archive with manual signing..."**
4. Проверьте логи на наличие ошибок

### Ключевые сообщения в логах:

**✅ Успех:**
```
✅ Using Automatic signing with App Store Connect API
✅ App Store Connect API keys configured
** ARCHIVE SUCCEEDED **
```

**❌ Ошибка:**
```
❌ xcodebuild archive failed with exit code 65
** ARCHIVE FAILED **
```

---

## 🔄 СЛЕДУЮЩИЕ ШАГИ ПОСЛЕ УСПЕШНОЙ СБОРКИ

1. **Проверить артефакты:**
   - В конце workflow должен быть артефакт `ALADDIN-IPA`
   - Скачайте и проверьте, что файл существует

2. **Проверить загрузку в App Store Connect:**
   - Если настроены API ключи, IPA должен автоматически загрузиться
   - Проверьте: https://appstoreconnect.apple.com/apps

3. **Если загрузка не произошла:**
   - Скачайте IPA из артефактов
   - Загрузите вручную через Transporter или Xcode

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Automatic signing в CI может не работать** даже с API ключами, если Xcode требует аккаунт
2. **Если Automatic не работает** - используйте Manual signing с правильно пересозданными профилями
3. **API ключи должны иметь правильные права** в App Store Connect (App Manager или Admin)

