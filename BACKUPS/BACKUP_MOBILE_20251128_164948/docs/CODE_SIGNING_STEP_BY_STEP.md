# 🔐 CODE SIGNING - ПОШАГОВАЯ ИНСТРУКЦИЯ

**Дата:** 15 ноября 2025  
**Время выполнения:** 15 минут

---

## 📋 ШАГ 1: ОТКРЫТЬ ПРОЕКТ В XCODE

### 1.1. Открыть Xcode

1. **Найти Xcode** на Mac:
   - Нажмите `Cmd + Space` (Spotlight)
   - Введите: `Xcode`
   - Нажмите `Enter`

2. **Или через Finder:**
   - Откройте Finder
   - Перейдите в `Applications`
   - Найдите `Xcode.app`
   - Двойной клик для открытия

---

### 1.2. Открыть проект ALADDIN

**Вариант 1: Через меню Xcode**
1. В Xcode нажмите: **File** → **Open** (или `Cmd + O`)
2. Перейдите в папку: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`
3. Найдите файл: `ALADDIN.xcodeproj`
4. Выберите файл и нажмите **Open**

**Вариант 2: Через Finder**
1. Откройте Finder
2. Перейдите в: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`
3. Найдите файл: `ALADDIN.xcodeproj` (синяя иконка)
4. Двойной клик на файл
5. Проект откроется в Xcode

---

## 📋 ШАГ 2: ВЫБРАТЬ ПРОЕКТ В ЛЕВОЙ ПАНЕЛИ

### 2.1. Найти проект в Navigator

1. **Слева в Xcode** вы увидите панель **Navigator** (если не видно, нажмите `Cmd + 1`)
2. **В самом верху** панели Navigator найдите:
   - Синяя иконка с буквой "A" или иконка проекта
   - Название: **ALADDIN** (самый первый элемент в списке)
3. **Кликните один раз** на **ALADDIN** (синяя иконка вверху)

**Что вы увидите:**
- В центральной панели откроется окно с настройками проекта
- Вверху будут вкладки: **General**, **Signing & Capabilities**, **Resource Tags**, и т.д.

---

## 📋 ШАГ 3: ВЫБРАТЬ TARGET "ALADDIN"

### 3.1. Найти список Targets

1. **В центральной панели** (где открылись настройки проекта)
2. **Слева** вы увидите список **TARGETS**:
   - ALADDIN (основное приложение)
   - ALADDINUnitTests (тесты)
   - и другие (если есть)

3. **Кликните один раз** на **ALADDIN** (первый в списке TARGETS)

**Что вы увидите:**
- Вкладки вверху изменятся
- Появятся: **General**, **Signing & Capabilities**, **Resource Tags**, и т.д.

---

## 📋 ШАГ 4: ПРОВЕРИТЬ BUNDLE ID И ВЕРСИЮ

### 4.1. Перейти на вкладку "General"

1. **Вверху центральной панели** найдите вкладки
2. **Кликните** на вкладку **General** (первая вкладка)

**Что вы увидите:**
- Раздел **Identity**
- Поля: **Display Name**, **Bundle Identifier**, **Version**, **Build**

---

### 4.2. Проверить Bundle Identifier

1. **Найдите поле** **Bundle Identifier**
2. **Проверьте значение:**
   - Должно быть: `family.aladdin.ios`
   - ✅ Если совпадает - ничего не меняйте
   - ❌ Если не совпадает - измените на `family.aladdin.ios`

**Как изменить (если нужно):**
- Кликните в поле **Bundle Identifier**
- Удалите старое значение
- Введите: `family.aladdin.ios`
- Нажмите `Enter`

---

### 4.3. Проверить Version

1. **Найдите поле** **Version**
2. **Проверьте значение:**
   - Должно быть: `1.0.0`
   - ✅ Если совпадает - ничего не меняйте
   - ❌ Если не совпадает - измените на `1.0.0`

**Как изменить (если нужно):**
- Кликните в поле **Version**
- Удалите старое значение
- Введите: `1.0.0`
- Нажмите `Enter`

---

### 4.4. Проверить Build

1. **Найдите поле** **Build**
2. **Проверьте значение:**
   - Должно быть: `1`
   - ✅ Если совпадает - ничего не меняйте
   - ❌ Если не совпадает - измените на `1`

**Как изменить (если нужно):**
- Кликните в поле **Build**
- Удалите старое значение
- Введите: `1`
- Нажмите `Enter`

---

## 📋 ШАГ 5: ПРОВЕРИТЬ CODE SIGNING

### 5.1. Перейти на вкладку "Signing & Capabilities"

1. **Вверху центральной панели** найдите вкладки
2. **Кликните** на вкладку **Signing & Capabilities** (вторая вкладка)

**Что вы увидите:**
- Раздел **Signing**
- Поля: **Team**, **Signing Certificate**, **Provisioning Profile**
- Чекбокс: **Automatically manage signing**

---

### 5.2. Проверить Team

1. **Найдите выпадающий список** **Team**
2. **Кликните** на выпадающий список (стрелка вниз)

**Вариант 1: Если есть команда**
- Выберите вашу команду (Apple Developer Account)
- ✅ Готово!

**Вариант 2: Если команды нет (None)**
- Нужно добавить Apple ID:
  1. Нажмите **Add Account...** (внизу списка)
  2. Введите ваш **Apple ID** (email)
  3. Введите **пароль**
  4. Нажмите **Sign In**
  5. После входа выберите команду из списка

**✅ ВАЖНО: Персональный Apple Developer Account (Personal Team)**
- ✅ **МОЖНО использовать** для публикации в App Store, если:
  - Вы зарегистрированы в **Apple Developer Program** ($99/год)
  - В Xcode видно: **"Your Name (Personal Team)"** или **"Your Name (Individual)"**
  - В Signing Certificate видно: **"Apple Distribution"** (не только Development)
- ⚠️ **НЕЛЬЗЯ использовать** для публикации, если:
  - Это бесплатный Apple ID (без регистрации в Developer Program)
  - В Xcode видно только: **"Your Name (Personal Team)"** без возможности выбрать Distribution
  - В Signing Certificate видно только: **"Apple Development"** (нет Distribution)

**Как проверить:**
1. После выбора Team посмотрите на **Signing Certificate**
2. Если видно **"Apple Distribution"** - ✅ можно публиковать
3. Если видно только **"Apple Development"** - ⚠️ нужно зарегистрироваться в Apple Developer Program

**Вариант 3: Если команды нет и нужно зарегистрироваться**
- Зарегистрируйтесь в Apple Developer Program ($99/год):
  1. Перейдите на: https://developer.apple.com/programs/
  2. Нажмите **Enroll**
  3. Следуйте инструкциям
  4. После регистрации добавьте аккаунт в Xcode (см. Вариант 2)

---

### 5.3. Проверить "Automatically manage signing"

1. **Найдите чекбокс** **Automatically manage signing**
2. **Проверьте:**
   - ✅ Должна стоять **галочка** (включено)
   - ❌ Если галочки нет - **кликните** на чекбокс, чтобы включить

**Что произойдет:**
- Xcode автоматически создаст Signing Certificate и Provisioning Profile
- Может появиться сообщение "Creating provisioning profile..." - подождите

---

### 5.4. Проверить Signing Certificate

1. **Найдите поле** **Signing Certificate**
2. **Проверьте значение:**
   - Должно быть: `Apple Distribution` (для Release)
   - Или: `Apple Development` (для Debug)
   - ✅ Если видно - все хорошо
   - ⚠️ Если пусто - Xcode создаст автоматически после выбора Team

**Если не видно:**
- Убедитесь, что выбрана **Team**
- Убедитесь, что включен **Automatically manage signing**
- Подождите несколько секунд - Xcode создаст автоматически

---

### 5.5. Проверить Provisioning Profile

1. **Найдите поле** **Provisioning Profile**
2. **Проверьте значение:**
   - Должно быть: `Automatic` или `App Store Distribution`
   - ✅ Если видно - все хорошо
   - ⚠️ Если пусто - Xcode создаст автоматически после выбора Team

**Если не видно:**
- Убедитесь, что выбрана **Team**
- Убедитесь, что включен **Automatically manage signing**
- Подождите несколько секунд - Xcode создаст автоматически

---

## 📋 ШАГ 6: ПРОВЕРИТЬ CAPABILITIES

### 6.1. Найти раздел Capabilities

1. **На вкладке** **Signing & Capabilities**
2. **Прокрутите вниз** от раздела Signing
3. **Найдите раздел** **Capabilities**

**Что вы увидите:**
- Список добавленных Capabilities (если есть)
- Кнопку **+ Capability** (вверху справа от списка)

---

### 6.2. Проверить Push Notifications

1. **Посмотрите в список Capabilities**
2. **Найдите** **Push Notifications**
3. **Проверьте:**
   - ✅ Если есть - все хорошо
   - ❌ Если нет - добавьте (см. ниже)

**Как добавить (если нужно):**
1. Нажмите кнопку **+ Capability** (вверху справа)
2. В появившемся списке найдите **Push Notifications**
3. Кликните на **Push Notifications**
4. Capability добавится автоматически

---

### 6.3. Проверить Personal VPN / Network Extensions

1. **Посмотрите в список Capabilities**
2. **Найдите** **Personal VPN** или **Network Extensions**
3. **Проверьте:**
   - ✅ Если есть - все хорошо
   - ❌ Если нет - добавьте (см. ниже)

**Как добавить (если нужно):**
1. Нажмите кнопку **+ Capability** (вверху справа)
2. В появившемся списке найдите **Personal VPN** или **Network Extensions**
3. Кликните на нужную Capability
4. Capability добавится автоматически

**Примечание:** Для VPN обычно нужна **Personal VPN** или **Network Extensions**

---

### 6.4. Проверить Keychain Sharing

1. **Посмотрите в список Capabilities**
2. **Найдите** **Keychain Sharing**
3. **Проверьте:**
   - ✅ Если есть - все хорошо
   - ❌ Если нет - добавьте (см. ниже)

**Как добавить (если нужно):**
1. Нажмите кнопку **+ Capability** (вверху справа)
2. В появившемся списке найдите **Keychain Sharing**
3. Кликните на **Keychain Sharing**
4. Capability добавится автоматически

---

## ✅ ЧЕКЛИСТ ПРОВЕРКИ

После выполнения всех шагов проверьте:

- [ ] Bundle Identifier: `family.aladdin.ios` ✅
- [ ] Version: `1.0.0` ✅
- [ ] Build: `1` ✅
- [ ] Team: выбрана ваша команда ✅
- [ ] Automatically manage signing: включено ✅
- [ ] Signing Certificate: видно (Apple Distribution или Apple Development) ✅
- [ ] Provisioning Profile: видно (Automatic или App Store Distribution) ✅
- [ ] Push Notifications: добавлена (если используется) ✅
- [ ] Personal VPN / Network Extensions: добавлена (если используется) ✅
- [ ] Keychain Sharing: добавлена (если используется) ✅

---

## ⚠️ ВОЗМОЖНЫЕ ОШИБКИ И РЕШЕНИЯ

### Ошибка 1: "No signing certificate found"

**Что делать:**
1. Убедитесь, что выбрана **Team**
2. Убедитесь, что включен **Automatically manage signing**
3. Подождите 10-15 секунд - Xcode создаст автоматически
4. Если не помогло:
   - Xcode → Preferences → Accounts
   - Выберите ваш Apple ID
   - Нажмите **Download Manual Profiles**

---

### Ошибка 2: "Bundle identifier is already in use"

**Что делать:**
1. Измените Bundle Identifier на уникальный:
   - Например: `family.aladdin.ios.yourname`
   - Или: `com.yourname.aladdin`
2. Или используйте существующий Bundle ID из App Store Connect

---

### Ошибка 3: "Provisioning profile doesn't match"

**Что делать:**
1. Убедитесь, что Bundle ID совпадает в Xcode и App Store Connect
2. Xcode → Preferences → Accounts
3. Выберите ваш Apple ID
4. Нажмите **Download Manual Profiles**
5. Вернитесь в Signing & Capabilities и обновите

---

### Ошибка 4: "Team not found" или "No team selected"

**Что делать:**
1. Убедитесь, что вы зарегистрированы в Apple Developer Program
2. Добавьте Apple ID в Xcode:
   - Xcode → Preferences → Accounts
   - Нажмите **+** (Add Apple ID)
   - Введите Apple ID и пароль
3. Вернитесь в Signing & Capabilities и выберите Team

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После успешной проверки Code Signing:

1. ✅ **Задача 12:** Создать Archive
   - Product → Archive
   - Дождаться завершения
   - Проверить в Organizer

2. ✅ **Задача 12:** Upload в App Store Connect
   - В Organizer выбрать Archive
   - Distribute App → App Store Connect
   - Следовать инструкциям

---

**Дата создания:** 15 ноября 2025  
**Статус:** ✅ **ПОШАГОВАЯ ИНСТРУКЦИЯ ГОТОВА**

