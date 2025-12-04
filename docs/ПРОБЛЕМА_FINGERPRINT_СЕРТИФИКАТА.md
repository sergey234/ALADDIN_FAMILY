# 🔍 ПРОБЛЕМА: Несоответствие Fingerprint Сертификата

**Дата:** 2 декабря 2024  
**Ошибка:** `Provisioning profile "ALADDIN App Store Distribution" doesn't include signing certificate "Apple Distribution: SERGEY KHLYSTOV (***)"`

---

## ✅ ДИАГНОСТИКА ПОКАЗАЛА

**Сертификаты совпадают по имени:**
- Keychain: `Apple Distribution: SERGEY KHLYSTOV (***)`
- App Profile: `CN = Apple Distribution: SERGEY KHLYSTOV (***)`
- Extension Profile: `CN = Apple Distribution: SERGEY KHLYSTOV (***)`

**НО:** Xcode все еще говорит, что профили не содержат сертификат!

---

## 🔍 ПРИЧИНА

**Xcode проверяет сертификаты по fingerprint (SHA-1), а не по имени!**

Даже если имена совпадают, если fingerprint сертификата в keychain не совпадает с fingerprint сертификата в профиле, Xcode выдаст ошибку.

---

## ✅ РЕШЕНИЕ

### Вариант 1: Обновить профили с правильным сертификатом (РЕКОМЕНДУЕТСЯ)

1. Зайдите в Apple Developer Portal: https://developer.apple.com/account/resources/profiles/list
2. Найдите профили:
   - "ALADDIN App Store Distribution" (UUID: d2857d1f-a7a0-49b0-b803-c006d8ad053b)
   - "ALADDINPacketTunnel App Store Distribution" (UUID: 039a47c4-b057-4712-a90a-5bb21d9a500e)
3. Убедитесь, что они связаны с сертификатом, который установлен в keychain
4. Если нет - отредактируйте профили и выберите правильный сертификат
5. Скачайте обновленные профили
6. Закодируйте в base64 и обновите GitHub Secrets

### Вариант 2: Использовать сертификат из профилей

1. Проверьте fingerprint сертификата в профилях (через диагностику)
2. Убедитесь, что этот сертификат установлен в keychain
3. Используйте этот сертификат вместо текущего

---

## 📊 ДИАГНОСТИКА FINGERPRINT

Добавлена диагностика для сравнения fingerprint:
- SHA-1 Fingerprint сертификата в keychain
- SHA-1 Fingerprint сертификата в профилях
- Serial Number для дополнительной проверки

Это поможет точно определить, совпадают ли сертификаты.

---

**Дата:** 2 декабря 2024  
**Статус:** Требуется проверка fingerprint сертификатов

