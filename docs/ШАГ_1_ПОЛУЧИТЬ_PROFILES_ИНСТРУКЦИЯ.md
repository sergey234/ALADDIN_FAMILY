# 📋 ШАГ 1: ПОЛУЧИТЬ PROVISIONING PROFILES - ПОШАГОВАЯ ИНСТРУКЦИЯ

**Дата:** 29 ноября 2025  
**Этап:** ЭТАП 1 из детального плана

---

## 🎯 ЦЕЛЬ

Создать provisioning profiles для подписи приложения на GitHub Actions.

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### Шаг 1.1: Открыть проект в Xcode

1. **Найти Xcode:**
   - Открыть Finder
   - Перейти в Applications
   - Найти "Xcode"
   - Или через Spotlight: Cmd+Space → ввести "Xcode" → Enter

2. **Открыть проект:**
   - В Xcode: File → Open (или Cmd+O)
   - Перейти в папку: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`
   - Выбрать `ALADDIN.xcodeproj` или `ALADDIN.xcworkspace`
   - Нажать "Open"

**Результат:**
- ✅ Проект открыт в Xcode

---

### Шаг 1.2: Настроить Signing для основного приложения (ALADDIN)

1. **Выбрать проект:**
   - В левой панели (Navigator) выбрать самый верхний элемент
   - Это должен быть проект "ALADDIN" (синяя иконка)

2. **Выбрать target "ALADDIN":**
   - В центральной панели выбрать вкладку "TARGETS"
   - Найти и выбрать "ALADDIN" (основное приложение)

3. **Перейти на вкладку "Signing & Capabilities":**
   - Вверху центральной панели найти вкладки
   - Нажать на "Signing & Capabilities"

4. **Настроить Signing:**
   - Найти раздел "Signing"
   - Поставить галочку "Automatically manage signing" ✅
   - В поле "Team" выбрать: `6CJVBBUGSN` (или ваше имя)
   - Если Team не видно:
     - Нажать "Add Account..."
     - Войти с Apple ID: `sergey21-02-84@list.ru`
     - После входа Team появится в списке

5. **Проверить результат:**
   - Должно появиться: "Provisioning Profile: Xcode Managed Profile"
   - Должно появиться: "Signing Certificate: Apple Development"
   - Не должно быть ошибок (красных предупреждений)

**Результат:**
- ✅ Provisioning profile создан для основного приложения
- ✅ Профиль сохранён в `~/Library/MobileDevice/Provisioning Profiles/`

**Если есть ошибки:**
- Проверить, что вы вошли в Apple ID
- Проверить, что у вас есть доступ к Team `6CJVBBUGSN`
- Если ошибка "No profiles for...", попробовать:
  - Xcode → Preferences → Accounts → выбрать Apple ID → Download Manual Profiles

---

### Шаг 1.3: Настроить Signing для Network Extension (ALADDINPacketTunnel)

1. **Выбрать target "ALADDINPacketTunnel":**
   - В центральной панели выбрать вкладку "TARGETS"
   - Найти и выбрать "ALADDINPacketTunnel" (Network Extension)

2. **Перейти на вкладку "Signing & Capabilities":**
   - Вверху центральной панели нажать на "Signing & Capabilities"

3. **Настроить Signing:**
   - Найти раздел "Signing"
   - Поставить галочку "Automatically manage signing" ✅
   - В поле "Team" выбрать: `6CJVBBUGSN` (тот же, что и для основного приложения)

4. **Проверить результат:**
   - Должно появиться: "Provisioning Profile: Xcode Managed Profile"
   - Должно появиться: "Signing Certificate: Apple Development"
   - Не должно быть ошибок (красных предупреждений)

**Результат:**
- ✅ Provisioning profile создан для Network Extension
- ✅ Профиль сохранён в `~/Library/MobileDevice/Provisioning Profiles/`

---

### Шаг 1.4: Найти и проверить provisioning profiles

1. **Открыть Finder:**
   - Нажать Cmd+Shift+G (Go to Folder)
   - Ввести: `~/Library/MobileDevice/Provisioning Profiles`
   - Нажать Enter

2. **Проверить файлы:**
   - Должны быть файлы с расширением `.mobileprovision`
   - Искать файлы с именами, содержащими:
     - `family.aladdin.ios` (основное приложение)
     - `family.aladdin.ios.packetTunnel` (Network Extension)

3. **Запомнить имена файлов:**
   - Записать полные имена файлов
   - Или скопировать их в отдельную папку (например, на Desktop)

**Результат:**
- ✅ Provisioning profiles найдены
- ✅ Готовы к экспорту

---

## ✅ ПРОВЕРКА РЕЗУЛЬТАТА

### Что должно быть:

1. **В Xcode:**
   - ✅ Target "ALADDIN": Signing настроен, нет ошибок
   - ✅ Target "ALADDINPacketTunnel": Signing настроен, нет ошибок
   - ✅ Оба target используют Team `6CJVBBUGSN`

2. **В Finder:**
   - ✅ Файлы `.mobileprovision` в `~/Library/MobileDevice/Provisioning Profiles/`
   - ✅ Файлы содержат `family.aladdin.ios` в имени

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После успешного создания provisioning profiles:
- **ЭТАП 2:** Добавить в GitHub Secrets
- Инструкция: `docs/ШАГ_2_ДОБАВИТЬ_В_GITHUB_SECRETS.md`

---

**Дата:** 29 ноября 2025  
**Инструкция:** Пошаговая инструкция для получения provisioning profiles

