# ⚡ БЫСТРОЕ РЕШЕНИЕ: Xcode Managed Profiles

**Дата:** 29 ноября 2025  
**Проблема:** Provisioning profiles являются "Xcode managed", а нужны "manually managed"

---

## 🔍 ПРОБЛЕМА

```
Provisioning profile "iOS Team Store Provisioning Profile: family.aladdin.ios" 
is Xcode managed, but signing settings require a manually managed profile.
```

---

## ✅ РЕШЕНИЕ (3 ВАРИАНТА)

### Вариант 1: Скачать manually managed profiles (РЕКОМЕНДУЕТСЯ)

**Инструкция:** `docs/КАК_СКАЧАТЬ_MANUALLY_MANAGED_PROFILES.md`

**Время:** 10-15 минут

**Шаги:**
1. Открыть https://developer.apple.com/account/resources/profiles/list
2. Создать новые профили типа "App Store" (не "iOS Team")
3. Скачать их
4. Закодировать в base64
5. Обновить GitHub Secrets

---

### Вариант 2: Использовать сертификат подписи

**Инструкция:** `docs/КАК_ДОБАВИТЬ_СЕРТИФИКАТ_ПОДПИСИ.md`

**Время:** 5-10 минут

**Шаги:**
1. Экспортировать сертификат из Keychain Access
2. Закодировать в base64
3. Добавить в GitHub Secrets:
   - `IOS_DISTRIBUTION_CERTIFICATE`
   - `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD`

---

### Вариант 3: Использовать Automatic signing с API ключами

**Проблема:** На GitHub Actions нет авторизованного Apple ID, поэтому Automatic signing не работает.

**Решение:** Использовать fastlane с App Store Connect API ключами (но это сложнее).

---

## 🎯 РЕКОМЕНДАЦИЯ

**Используйте Вариант 1** - это самый простой и надежный способ.

После обновления секретов workflow должен заработать!

---

**Дата:** 29 ноября 2025  
**Быстрое решение:** Xcode Managed Profiles

