# 🔐 СЛЕДУЮЩИЙ ШАГ: Code Signing проверка

**Дата:** 15 ноября 2025  
**Задача:** Задача 11 - Code Signing проверка  
**Приоритет:** 🔴 Критический  
**Время:** 15 минут

---

## 📋 ЧТО НУЖНО СДЕЛАТЬ

### ✅ Шаг 1: Открыть проект в Xcode

1. Откройте `ALADDIN.xcodeproj` в Xcode
2. Выберите проект `ALADDIN` в левой панели (синяя иконка вверху)

---

### ✅ Шаг 2: Проверить Bundle ID и версию

**Путь:** Project → Target → General → Identity

**Проверить:**
- ✅ **Bundle Identifier:** `family.aladdin.ios` (уже установлен ✅)
- ✅ **Version:** `1.0.0` (нужно проверить в Xcode)
- ✅ **Build:** `1` (нужно проверить в Xcode)

**Если не совпадает:**
- Измените Version на `1.0.0`
- Измените Build на `1`

---

### ✅ Шаг 3: Проверить Code Signing

**Путь:** Project → Target → Signing & Capabilities

**Что проверить:**

#### 3.1. Team
- [ ] Выберите вашу команду (Apple Developer Account)
- ⚠️ Если команды нет:
  - Зарегистрируйтесь в Apple Developer Program ($99/год)
  - Или добавьте аккаунт: Xcode → Preferences → Accounts → Add Apple ID

#### 3.2. Signing Certificate
- [ ] Должен быть выбран: `Apple Distribution` (для Release)
- ⚠️ Если нет:
  - Xcode создаст автоматически при выборе Team
  - Или создайте вручную в Apple Developer Portal

#### 3.3. Provisioning Profile
- [ ] Должен быть: `Automatic` или `App Store Distribution`
- ⚠️ Если нет:
  - Включите "Automatically manage signing"
  - Xcode создаст автоматически

#### 3.4. Automatically manage signing
- [ ] Должно быть включено (галочка стоит)

---

### ✅ Шаг 4: Проверить Capabilities

**Путь:** Project → Target → Signing & Capabilities

**Проверить наличие:**
- [ ] **Push Notifications** (если используется)
- [ ] **Personal VPN** или **Network Extensions** (для VPN)
- [ ] **Keychain Sharing** (если используется)
- [ ] **App Groups** (если используется)

**Если чего-то не хватает:**
- Нажмите "+ Capability" вверху
- Добавьте нужные Capabilities

---

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### Проблема 1: "No signing certificate found"

**Решение:**
1. Xcode → Preferences → Accounts
2. Выберите ваш Apple ID
3. Нажмите "Download Manual Profiles"
4. Или зарегистрируйтесь в Apple Developer Program

---

### Проблема 2: "Bundle identifier is already in use"

**Решение:**
- Измените Bundle Identifier на уникальный (например, `family.aladdin.ios.yourname`)
- Или используйте существующий Bundle ID из App Store Connect

---

### Проблема 3: "Provisioning profile doesn't match"

**Решение:**
1. Убедитесь, что Bundle ID совпадает в Xcode и App Store Connect
2. Нажмите "Download Manual Profiles" в Accounts
3. Или создайте новый Provisioning Profile в Apple Developer Portal

---

## ✅ ЧЕКЛИСТ ПЕРЕД ПРОДОЛЖЕНИЕМ

- [ ] Bundle ID: `family.aladdin.ios` ✅ (уже установлен)
- [ ] Version: `1.0.0` (проверить в Xcode)
- [ ] Build: `1` (проверить в Xcode)
- [ ] Team выбран
- [ ] Signing Certificate валидный
- [ ] Provisioning Profile для App Store
- [ ] Все Capabilities добавлены
- [ ] "Automatically manage signing" включено

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После проверки Code Signing:
1. ✅ **Задача 12:** Создать Archive (Product → Archive)
2. ✅ **Задача 12:** Upload в App Store Connect

---

## 📄 ДОПОЛНИТЕЛЬНЫЕ ИНСТРУКЦИИ

Полные инструкции: `docs/CODE_SIGNING_INSTRUCTIONS.md`

---

**Дата создания:** 15 ноября 2025  
**Статус:** ⏳ **ГОТОВ К ВЫПОЛНЕНИЮ**




