# 🚀 БЫСТРАЯ УСТАНОВКА GITHUB CLI

**Дата:** 29 ноября 2025

---

## ⚡ БЫСТРЫЙ СПОСОБ (РЕКОМЕНДУЕТСЯ)

### Установить Homebrew и GitHub CLI вручную:

1. **Открыть Terminal:**
   - Cmd+Space → "Terminal" → Enter

2. **Установить Homebrew:**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   - Ввести пароль администратора, когда попросит
   - Подождать завершения (5-10 минут)

3. **После установки Homebrew, добавить в PATH:**
   ```bash
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. **Установить GitHub CLI:**
   ```bash
   brew install gh
   ```

5. **Авторизоваться:**
   ```bash
   gh auth login
   ```
   - Выбрать: GitHub.com
   - Выбрать: HTTPS
   - Выбрать: "Login with a web browser"
   - Нажать Enter
   - В браузере авторизоваться
   - Вернуться в терминал

6. **Проверить:**
   ```bash
   gh --version
   gh auth status
   ```

---

## ✅ АЛЬТЕРНАТИВА: ДОБАВИТЬ СЕКРЕТЫ ВРУЧНУЮ

**Если установка занимает много времени, можно добавить секреты вручную:**

1. **Открыть в браузере:**
   https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

2. **Добавить секреты:**
   - `PROVISIONING_PROFILE_APP` (скопировать из `app_profile_base64.txt`)
   - `PROVISIONING_PROFILE_EXTENSION` (скопировать из `extension_profile_base64.txt`)
   - `APPLE_TEAM_ID` = `6CJVBBUGSN`

3. **Файлы уже открыты в TextEdit для копирования**

**Это займёт 2-3 минуты!** ⚡

---

**Дата:** 29 ноября 2025  
**Инструкция:** Быстрая установка GitHub CLI

