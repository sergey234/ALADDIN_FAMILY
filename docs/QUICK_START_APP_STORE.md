# ⚡ БЫСТРЫЙ СТАРТ: Загрузка в App Store за 5 шагов

**Время:** 30-60 минут  
**Сложность:** Простая  
**Результат:** Билд в App Store Connect

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ

### **ШАГ 1: Получить App-Specific Password** (2 минуты)

1. Зайдите на **appleid.apple.com**
2. Войдите в аккаунт
3. **Sign-In and Security → App-Specific Passwords**
4. Нажмите **"Generate an app-specific password"**
5. Название: **"GitHub Actions"**
6. **Скопируйте пароль** (показывается только один раз!)
   - Формат: `xxxx-xxxx-xxxx-xxxx`

---

### **ШАГ 2: Добавить секреты в GitHub** (3 минуты)

1. Зайдите на **GitHub.com** → ваш репозиторий
2. **Settings → Secrets and variables → Actions**
3. Нажмите **"New repository secret"**
4. Добавьте 3 секрета:

   **Секрет 1:**
   - Name: `APPLE_ID`
   - Value: ваш email (например, `sergey@example.com`)

   **Секрет 2:**
   - Name: `APPLE_APP_SPECIFIC_PASSWORD`
   - Value: пароль из шага 1 (например, `abcd-efgh-ijkl-mnop`)

   **Секрет 3:**
   - Name: `APPLE_TEAM_ID`
   - Value: `6CJVBBUGSN`

---

### **ШАГ 3: Проверить файлы** (1 минута)

Убедитесь, что файлы на месте:
- ✅ `.github/workflows/appstore.yml` — создан автоматически
- ✅ `ExportOptions.plist` — обновлён с Team ID `6CJVBBUGSN`

---

### **ШАГ 4: Запустить сборку** (1 минута)

1. Зайдите на **GitHub.com** → ваш репозиторий
2. Вкладка **Actions**
3. В левом меню выберите **"Build and Upload to App Store"**
4. Нажмите **"Run workflow"** (справа)
5. Выберите ветку (обычно `main` или `master`)
6. Нажмите **"Run workflow"** (зелёная кнопка)

---

### **ШАГ 5: Дождаться завершения** (15-30 минут)

1. **Следите за прогрессом** в GitHub Actions
2. **Жёлтый кружок** = выполняется
3. **Зелёная галочка** = успешно
4. **Красный крестик** = ошибка (см. логи)

**После успешной сборки:**
- Билд автоматически загрузится в App Store Connect
- Вы получите уведомление на email

---

## ✅ ПРОВЕРКА РЕЗУЛЬТАТА

1. Зайдите на **appstoreconnect.apple.com**
2. **My Apps → ALADDIN**
3. **TestFlight** (или **App Store → Versions**)
4. Проверьте, что билд появился в списке

---

## ⚠️ ЕСЛИ ОШИБКА

### **Ошибка: "No signing certificate"**

**Решение:**
1. Зайдите в **Apple Developer Center**
2. **Certificates, Identifiers & Profiles**
3. Убедитесь, что есть **Distribution Certificate**
4. Если нет — создайте новый

---

### **Ошибка: "Invalid credentials"**

**Решение:**
1. Проверьте, что **APPLE_ID** правильный
2. Проверьте, что **APPLE_APP_SPECIFIC_PASSWORD** правильный
3. Создайте новый App-Specific Password, если нужно

---

### **Ошибка: "Bundle ID not found"**

**Решение:**
1. Зайдите в **Apple Developer Center**
2. **Identifiers → App IDs**
3. Убедитесь, что `family.aladdin.ios` зарегистрирован
4. Если нет — создайте новый App ID

---

## 📝 КРАТКАЯ ПАМЯТКА

```
1. Получить App-Specific Password (appleid.apple.com)
2. Добавить секреты в GitHub (Settings → Secrets)
3. Проверить файлы (appstore.yml, ExportOptions.plist)
4. Запустить workflow (Actions → Run workflow)
5. Проверить в App Store Connect
```

---

## 🎉 ГОТОВО!

После выполнения этих шагов ваш билд будет в App Store Connect, и вы сможете отправить его на ревью!

**Время:** 30-60 минут  
**Стоимость:** Бесплатно (GitHub Actions бесплатен для публичных репозиториев)

---

**Следующий шаг:** Выполните шаги 1-5 выше! 🚀

