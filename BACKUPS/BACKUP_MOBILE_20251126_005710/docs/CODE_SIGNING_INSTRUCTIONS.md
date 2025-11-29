# 🔐 CODE SIGNING - ИНСТРУКЦИИ

**Дата:** 15 ноября 2025  
**Статус:** 🔄 **ГОТОВ К ВЫПОЛНЕНИЮ**

---

## 📋 ЧТО НУЖНО ПРОВЕРИТЬ В XCODE

### Шаг 1: Открыть проект в Xcode

1. Откройте `ALADDIN.xcodeproj` в Xcode
2. Выберите проект `ALADDIN` в левой панели (синяя иконка вверху)

---

### Шаг 2: Проверить Bundle ID

**Путь:** Project → Target → General → Identity

**Проверить:**
- ✅ **Bundle Identifier:** `family.aladdin.ios`
- ✅ **Version:** `1.0.0`
- ✅ **Build:** `1`

**Если не совпадает:**
- Измените Bundle Identifier на `family.aladdin.ios`
- Установите Version: `1.0.0`
- Установите Build: `1`

---

### Шаг 3: Проверить Code Signing

**Путь:** Project → Target → Signing & Capabilities

**Проверить:**

1. **Team:**
   - ✅ Выберите вашу команду (Apple Developer Account)
   - ⚠️ Если команды нет, нужно:
     - Зарегистрироваться в Apple Developer Program
     - Или добавить аккаунт в Xcode: Preferences → Accounts → Add Apple ID

2. **Signing Certificate:**
   - ✅ Должен быть выбран автоматически: `Apple Development` или `Apple Distribution`
   - ⚠️ Для Release нужен: `Apple Distribution`

3. **Provisioning Profile:**
   - ✅ Должен быть: `Automatic` или конкретный профиль для App Store
   - ⚠️ Для Release нужен профиль типа: `App Store Distribution`

4. **Automatically manage signing:**
   - ✅ Должно быть включено (галочка стоит)

---

### Шаг 4: Проверить Capabilities

**Путь:** Project → Target → Signing & Capabilities

**Проверить наличие:**
- ✅ **Push Notifications** (если используется)
- ✅ **Personal VPN** или **Network Extensions** (для VPN)
- ✅ **Keychain Sharing** (если используется)
- ✅ **App Groups** (если используется)

**Если чего-то не хватает:**
- Нажмите "+ Capability" вверху
- Добавьте нужные Capabilities

---

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### Проблема 1: "No signing certificate found"

**Решение:**
1. Зайдите в Xcode → Preferences → Accounts
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

## ✅ ЧЕКЛИСТ ПЕРЕД ARCHIVE

- [ ] Bundle ID: `family.aladdin.ios`
- [ ] Version: `1.0.0`
- [ ] Build: `1`
- [ ] Team выбран
- [ ] Signing Certificate валидный
- [ ] Provisioning Profile для App Store
- [ ] Все Capabilities добавлены
- [ ] "Automatically manage signing" включено

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После проверки Code Signing:
1. ✅ Создать Archive (Product → Archive)
2. ✅ Upload в App Store Connect

---

**Дата создания:** 15 ноября 2025




