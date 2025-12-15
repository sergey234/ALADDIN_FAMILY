# 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ: Настройка GitHub Actions для App Store

**Дата:** 27 ноября 2025  
**Репозиторий:** https://github.com/sergey234/ALADDIN_FAMILY  
**Статус:** ✅ Workflow файл уже в репозитории

---

## ✅ ШАГ 1: Получить App-Specific Password (2 минуты)

### **Если у вас ЕЩЁ НЕТ App-Specific Password:**

1. **Откройте:** https://appleid.apple.com
2. **Войдите** в ваш Apple ID
3. **Sign-In and Security** → **App-Specific Passwords**
4. Нажмите **"Generate an app-specific password"** (или кнопку "+")
5. **Название:** `GitHub Actions`
6. **Скопируйте пароль** (формат: `xxxx-xxxx-xxxx-xxxx`)
   - ⚠️ **ВАЖНО:** Пароль показывается только один раз! Сохраните его!

### **Если у вас УЖЕ ЕСТЬ App-Specific Password:**
- Используйте существующий пароль для "GitHub Actions"
- Или создайте новый, если забыли старый

---

## ✅ ШАГ 2: Добавить секреты в GitHub (3 минуты)

### **2.1. Открыть страницу секретов:**

1. **Откройте:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
2. Если попросит авторизацию — войдите в GitHub

### **2.2. Добавить первый секрет: APPLE_ID**

1. Нажмите **"New repository secret"** (зелёная кнопка справа вверху)
2. **Name:** `APPLE_ID`
3. **Secret:** ваш email Apple ID (например, `sergey@example.com`)
4. Нажмите **"Add secret"**

### **2.3. Добавить второй секрет: APPLE_APP_SPECIFIC_PASSWORD**

1. Снова нажмите **"New repository secret"**
2. **Name:** `APPLE_APP_SPECIFIC_PASSWORD`
3. **Secret:** пароль из шага 1 (например, `abcd-efgh-ijkl-mnop`)
4. Нажмите **"Add secret"**

### **2.4. Добавить третий секрет: APPLE_TEAM_ID**

1. Снова нажмите **"New repository secret"**
2. **Name:** `APPLE_TEAM_ID`
3. **Secret:** `6CJVBBUGSN`
4. Нажмите **"Add secret"**

### **✅ Проверка:**

После добавления всех трёх секретов вы должны увидеть в списке:
- ✅ `APPLE_ID`
- ✅ `APPLE_APP_SPECIFIC_PASSWORD`
- ✅ `APPLE_TEAM_ID`

---

## ✅ ШАГ 3: Запустить сборку (1 минута)

### **3.1. Открыть страницу Actions:**

1. **Откройте:** https://github.com/sergey234/ALADDIN_FAMILY/actions
2. В левом меню найдите **"Build and Upload to App Store"**
   - Если не видите — обновите страницу (F5 или Cmd+R)

### **3.2. Запустить workflow:**

1. Нажмите **"Run workflow"** (справа вверху, зелёная кнопка)
2. В выпадающем списке **"Use workflow from"** выберите: **`master`**
3. Нажмите зелёную кнопку **"Run workflow"**

### **3.3. Следить за прогрессом:**

1. Вы увидите новый запуск workflow в списке
2. **Жёлтый кружок** = выполняется
3. **Зелёная галочка** = успешно
4. **Красный крестик** = ошибка (см. логи)

**Время выполнения:** 15-30 минут

---

## ✅ ШАГ 4: Проверить результат (2 минуты)

### **4.1. Проверить в GitHub Actions:**

1. **Откройте:** https://github.com/sergey234/ALADDIN_FAMILY/actions
2. Найдите ваш запуск workflow (самый верхний)
3. Кликните на него
4. Проверьте, что все шаги завершились успешно (зелёные галочки)

### **4.2. Проверить в App Store Connect:**

1. **Откройте:** https://appstoreconnect.apple.com
2. Войдите в ваш Apple ID
3. **My Apps** → **ALADDIN**
4. Перейдите на вкладку **"TestFlight"** (или **"App Store"** → **"Versions"**)
5. Проверьте, что билд появился в списке

**Если билд есть:**
- ✅ Всё работает! Билд готов к отправке на ревью.

**Если билда нет:**
- Проверьте логи в GitHub Actions на наличие ошибок
- Убедитесь, что все секреты добавлены правильно

---

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### **Проблема 1: "No signing certificate"**

**Решение:**
1. Зайдите в **Apple Developer Center** → **Certificates, Identifiers & Profiles**
2. Убедитесь, что есть **Distribution Certificate**
3. Если нет — создайте новый (тип: **Apple Distribution**)

---

### **Проблема 2: "Invalid credentials"**

**Решение:**
1. Проверьте, что **APPLE_ID** правильный в GitHub Secrets
2. Проверьте, что **APPLE_APP_SPECIFIC_PASSWORD** правильный
3. Создайте новый App-Specific Password, если нужно

---

### **Проблема 3: "Bundle ID not found"**

**Решение:**
1. Зайдите в **Apple Developer Center** → **Identifiers**
2. Убедитесь, что `family.aladdin.ios` зарегистрирован
3. Если нет — создайте новый App ID

---

### **Проблема 4: Workflow не запускается**

**Решение:**
1. Убедитесь, что файл `.github/workflows/appstore.yml` есть в репозитории
2. Проверьте, что вы нажали "Run workflow" для ветки `master`
3. Обновите страницу и попробуйте снова

---

## 📝 КРАТКАЯ ПАМЯТКА

```
1. Получить App-Specific Password (appleid.apple.com)
2. Добавить 3 секрета в GitHub (Settings → Secrets)
3. Запустить workflow (Actions → Run workflow)
4. Дождаться завершения (15-30 минут)
5. Проверить в App Store Connect
```

---

## 🔗 ССЫЛКИ

- **GitHub Secrets:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
- **GitHub Actions:** https://github.com/sergey234/ALADDIN_FAMILY/actions
- **App Store Connect:** https://appstoreconnect.apple.com
- **Apple ID:** https://appleid.apple.com

---

**Готово!** Выполните шаги 1-4 по порядку, и ваш билд будет в App Store Connect! 🚀

