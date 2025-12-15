# 🔍 ПРОВЕРКА API КЛЮЧЕЙ ДЛЯ APP STORE CONNECT

**Дата:** 30 ноября 2025  
**Цель:** Проверить наличие и правильность настройки API ключей для автоматической загрузки в App Store Connect

---

## 📋 НЕОБХОДИМЫЕ API КЛЮЧИ

Для автоматической загрузки IPA в App Store Connect нужны **3 секрета** в GitHub Secrets:

1. **APP_STORE_CONNECT_API_KEY** - содержимое .p8 файла
2. **APP_STORE_CONNECT_ISSUER_ID** - UUID из App Store Connect
3. **APP_STORE_CONNECT_API_KEY_ID** - Key ID (например: 53NRCU2SU2)

---

## ✅ ПРОВЕРКА ПО ДОКУМЕНТАЦИИ

Согласно `ПОЛНАЯ_СВОДКА_СЕРТИФИКАТОВ_И_КЛЮЧЕЙ.md`:

### 1. APP_STORE_CONNECT_API_KEY
- **Статус:** ✅ Установлен (по документации)
- **Источник файла:** `~/Desktop/ALADDIN_Profiles/Certificates/AuthKey_53NRCU2SU2.p8`
- **Key ID:** 53NRCU2SU2
- **Использование:** Для автоматической загрузки в App Store Connect

### 2. APP_STORE_CONNECT_ISSUER_ID
- **Статус:** ✅ Установлен (по документации)
- **Где найти:** 
  - App Store Connect → Users and Access → Keys
  - На странице с API ключами, в разделе "Issuer ID"
- **Формат:** UUID (например: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### 3. APP_STORE_CONNECT_API_KEY_ID
- **Статус:** ✅ Установлен (по документации)
- **Значение:** `53NRCU2SU2`
- **Где найти:** 
  - В имени файла API ключа: `AuthKey_53NRCU2SU2.p8`
  - App Store Connect → Users and Access → Keys

---

## 🔍 КАК ПРОВЕРИТЬ РЕАЛЬНО В GITHUB

### Шаг 1: Открыть GitHub Secrets
```
https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
```

### Шаг 2: Проверить наличие секретов
Убедитесь, что в списке есть:
- ✅ `APP_STORE_CONNECT_API_KEY`
- ✅ `APP_STORE_CONNECT_ISSUER_ID`
- ✅ `APP_STORE_CONNECT_API_KEY_ID`

### Шаг 3: Проверить значения (если возможно)
- **APP_STORE_CONNECT_API_KEY** должен начинаться с `-----BEGIN PRIVATE KEY-----`
- **APP_STORE_CONNECT_ISSUER_ID** должен быть UUID формата
- **APP_STORE_CONNECT_API_KEY_ID** должен быть `53NRCU2SU2`

---

## 📁 ПРОВЕРКА ЛОКАЛЬНЫХ ФАЙЛОВ

### Проверить наличие API ключа:
```bash
ls -lh ~/Desktop/ALADDIN_Profiles/Certificates/AuthKey_53NRCU2SU2.p8
```

### Проверить формат файла:
```bash
head -3 ~/Desktop/ALADDIN_Profiles/Certificates/AuthKey_53NRCU2SU2.p8
```

Должно начинаться с:
```
-----BEGIN PRIVATE KEY-----
```

---

## ⚠️ ЕСЛИ КЛЮЧИ НЕ НАСТРОЕНЫ

### Как добавить API ключи в GitHub Secrets:

#### 1. APP_STORE_CONNECT_API_KEY
1. Откройте файл: `~/Desktop/ALADDIN_Profiles/Certificates/AuthKey_53NRCU2SU2.p8`
2. Скопируйте **ВСЁ содержимое** (включая BEGIN/END строки)
3. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
4. Нажмите "New repository secret"
5. **Name:** `APP_STORE_CONNECT_API_KEY`
6. **Secret:** Вставьте содержимое файла
7. Нажмите "Add secret"

#### 2. APP_STORE_CONNECT_ISSUER_ID
1. Откройте: https://appstoreconnect.apple.com
2. Перейдите: Users and Access → Keys
3. Найдите раздел "Issuer ID" (UUID)
4. Скопируйте UUID
5. В GitHub Secrets создайте:
   - **Name:** `APP_STORE_CONNECT_ISSUER_ID`
   - **Secret:** Вставьте UUID

#### 3. APP_STORE_CONNECT_API_KEY_ID
1. В GitHub Secrets создайте:
   - **Name:** `APP_STORE_CONNECT_API_KEY_ID`
   - **Secret:** `53NRCU2SU2`

---

## ✅ ПРОВЕРКА РАБОТЫ

### После настройки ключей:

1. **Запустите workflow:**
   ```bash
   git tag -a "v1.0.0-test" -m "Test API keys"
   git push origin --tags
   ```

2. **Проверьте логи workflow:**
   - Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions
   - Найдите последний запуск
   - Проверьте шаг "Upload to App Store Connect using apple-actions"
   - Должно быть: ✅ "Upload successful"

3. **Проверьте App Store Connect:**
   - Откройте: https://appstoreconnect.apple.com
   - My Apps → ALADDIN X AI → TestFlight → Builds
   - Должен появиться новый билд

---

## 📊 СТАТУС (по документации)

| Секрет | Статус | Значение/Источник |
|--------|--------|-------------------|
| APP_STORE_CONNECT_API_KEY | ✅ Установлен | AuthKey_53NRCU2SU2.p8 |
| APP_STORE_CONNECT_ISSUER_ID | ✅ Установлен | App Store Connect |
| APP_STORE_CONNECT_API_KEY_ID | ✅ Установлен | 53NRCU2SU2 |

**⚠️ ВАЖНО:** Это статус по документации. Для реальной проверки откройте GitHub Secrets вручную.

---

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- **GitHub Secrets:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
- **App Store Connect Keys:** https://appstoreconnect.apple.com/access/api
- **GitHub Actions:** https://github.com/sergey234/ALADDIN_FAMILY/actions
- **Полная сводка:** `~/Desktop/ALADDIN_Profiles/ПОЛНАЯ_СВОДКА_СЕРТИФИКАТОВ_И_КЛЮЧЕЙ.md`

---

**Дата проверки:** 30 ноября 2025  
**Статус:** ✅ По документации все ключи установлены

