# 🎯 КОНКРЕТНАЯ ИНСТРУКЦИЯ: Настройка GitHub Actions для App Store

**Репозиторий:** https://github.com/sergey234/ALADDIN_FAMILY  
**Статус:** ✅ Workflow файл создан, нужно настроить секреты

---

## ✅ ЧТО УЖЕ ГОТОВО

- ✅ Репозиторий подключен: `sergey234/ALADDIN_FAMILY`
- ✅ Workflow файл создан: `.github/workflows/appstore.yml`
- ✅ ExportOptions.plist обновлён с Team ID

---

## 🚀 ЧТО НУЖНО СДЕЛАТЬ (3 ШАГА)

### **ШАГ 1: Получить App-Specific Password** (2 минуты)

1. **Зайдите на:** https://appleid.apple.com
2. **Войдите** в ваш Apple ID
3. **Sign-In and Security** → **App-Specific Passwords**
4. Нажмите **"Generate an app-specific password"** (или "+")
5. **Название:** `GitHub Actions`
6. **Скопируйте пароль** (формат: `xxxx-xxxx-xxxx-xxxx`)
   - ⚠️ **ВАЖНО:** Пароль показывается только один раз! Сохраните его!

---

### **ШАГ 2: Добавить секреты в GitHub** (3 минуты)

1. **Зайдите на:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

2. **Нажмите "New repository secret"** (зелёная кнопка справа)

3. **Добавьте 3 секрета:**

   **Секрет 1: APPLE_ID**
   - Name: `APPLE_ID`
   - Secret: ваш email Apple ID (например, `sergey@example.com`)
   - Нажмите **"Add secret"**

   **Секрет 2: APPLE_APP_SPECIFIC_PASSWORD**
   - Name: `APPLE_APP_SPECIFIC_PASSWORD`
   - Secret: пароль из шага 1 (например, `abcd-efgh-ijkl-mnop`)
   - Нажмите **"Add secret"**

   **Секрет 3: APPLE_TEAM_ID**
   - Name: `APPLE_TEAM_ID`
   - Secret: `6CJVBBUGSN`
   - Нажмите **"Add secret"**

---

### **ШАГ 3: Закоммитить и запушить изменения** (2 минуты)

В терминале выполните:

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Добавить новые файлы
git add .github/workflows/appstore.yml
git add ExportOptions.plist

# Закоммитить
git commit -m "Add GitHub Actions workflow for App Store upload"

# Запушить
git push origin main
```

**Если ветка называется не `main`, а `master`:**
```bash
git push origin master
```

---

## 🎉 ЗАПУСК СБОРКИ

После того, как вы запушили изменения:

1. **Зайдите на:** https://github.com/sergey234/ALADDIN_FAMILY/actions

2. **В левом меню** найдите **"Build and Upload to App Store"**

3. **Нажмите "Run workflow"** (справа вверху)

4. **Выберите ветку** (обычно `main` или `master`)

5. **Нажмите зелёную кнопку "Run workflow"**

6. **Подождите 15-30 минут** — сборка выполнится на виртуальном Mac

---

## ✅ ПРОВЕРКА РЕЗУЛЬТАТА

После успешной сборки:

1. **Зайдите на:** https://appstoreconnect.apple.com
2. **My Apps → ALADDIN**
3. **TestFlight** (или **App Store → Versions**)
4. Проверьте, что билд появился в списке

---

## ⚠️ ЕСЛИ ОШИБКА

### **Ошибка: "No signing certificate"**

**Решение:**
1. Зайдите в **Apple Developer Center** → **Certificates, Identifiers & Profiles**
2. Убедитесь, что есть **Distribution Certificate**
3. Если нет — создайте новый (тип: **Apple Distribution**)

---

### **Ошибка: "Invalid credentials"**

**Решение:**
1. Проверьте, что **APPLE_ID** правильный в GitHub Secrets
2. Проверьте, что **APPLE_APP_SPECIFIC_PASSWORD** правильный
3. Создайте новый App-Specific Password, если нужно

---

### **Ошибка: "Bundle ID not found"**

**Решение:**
1. Зайдите в **Apple Developer Center** → **Identifiers**
2. Убедитесь, что `family.aladdin.ios` зарегистрирован
3. Если нет — создайте новый App ID

---

## 📝 КРАТКАЯ ПАМЯТКА

```
1. Получить App-Specific Password (appleid.apple.com)
2. Добавить 3 секрета в GitHub (Settings → Secrets)
3. Закоммитить и запушить изменения (git push)
4. Запустить workflow (Actions → Run workflow)
5. Проверить в App Store Connect
```

---

## 🔗 ССЫЛКИ

- **GitHub Actions:** https://github.com/sergey234/ALADDIN_FAMILY/actions
- **GitHub Secrets:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
- **App Store Connect:** https://appstoreconnect.apple.com
- **Apple ID:** https://appleid.apple.com

---

**Готово!** Выполните шаги 1-3, и ваш билд будет в App Store Connect! 🚀

