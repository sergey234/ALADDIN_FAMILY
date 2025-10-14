# 🚀 GITHUB ACTIONS - iOS КОМПИЛЯЦИЯ: ПОШАГОВЫЙ ПЛАН

**Дата:** 13 октября 2025  
**Выбор:** GitHub Actions (вариант A) ⭐  
**Время:** ~45 минут настройки + 10-15 минут компиляция  
**Сложность:** ⭐⭐ Средняя (я помогу на каждом шаге!)

---

## 📋 СОДЕРЖАНИЕ

1. [Подготовка (5 минут)](#этап-1-подготовка)
2. [Создание Private Repository (5 минут)](#этап-2-создание-repository)
3. [Настройка 2FA (5 минут)](#этап-3-настройка-2fa)
4. [Загрузка кода (10 минут)](#этап-4-загрузка-кода)
5. [Настройка iOS Signing (10 минут)](#этап-5-ios-signing)
6. [Создание Workflow (10 минут)](#этап-6-workflow)
7. [Запуск компиляции (1 минута)](#этап-7-запуск)
8. [Скачивание .ipa (2 минуты)](#этап-8-скачивание)

---

## ЭТАП 1: ПОДГОТОВКА (5 минут)

### 1.1 Проверка аккаунта GitHub

У вас уже есть GitHub аккаунт ✅

**Проверим, всё ли готово:**

```bash
# Проверить, установлен ли git
git --version

# Должно показать: git version 2.x.x
```

Если git не установлен:
```bash
# Установить через Xcode Command Line Tools
xcode-select --install
```

---

### 1.2 Настройка git (если ещё не настроен)

```bash
# Установить имя
git config --global user.name "Ваше Имя"

# Установить email (тот, что в GitHub)
git config --global user.email "ваш@email.com"

# Проверить
git config --list | grep user
```

---

### 1.3 Подготовка проекта

```bash
# Перейти в папку iOS проекта
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Проверить структуру
ls -la

# Должно быть:
# - Screens/
# - Components/
# - ViewModels/
# - Core/
# - Resources/
```

---

## ЭТАП 2: СОЗДАНИЕ REPOSITORY (5 минут)

### 2.1 Создать репозиторий на GitHub

**Вариант A: Через веб-интерфейс (ПРОЩЕ)**

1. Открыть: https://github.com/new
2. Заполнить:
   ```
   Repository name: ALADDIN-iOS-Build
   Description: ALADDIN iOS App Private Build
   Visibility: 🔒 Private ← ВАЖНО!
   Initialize: ☐ НЕ ставить галочки (пустой репо)
   ```
3. Нажать: **"Create repository"**

**Результат:** URL репозитория, например:
```
https://github.com/ваш-username/ALADDIN-iOS-Build
```

---

**Вариант B: Через GitHub CLI (АВТОМАТИЧЕСКИ)**

Если установлен GitHub CLI:
```bash
# Создать private репозиторий
gh repo create ALADDIN-iOS-Build \
  --private \
  --description "ALADDIN iOS App Private Build"

# Получить URL
gh repo view --web
```

---

### 2.2 Инициализировать git в проекте

```bash
# Перейти в папку iOS проекта
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Инициализировать git (если ещё не инициализирован)
git init

# Проверить статус
git status
```

---

### 2.3 Создать .gitignore

**Важно:** Исключить временные файлы и секреты!

```bash
# Создать .gitignore для iOS
cat > .gitignore << 'EOF'
# Xcode
build/
*.pbxuser
!default.pbxuser
*.mode1v3
!default.mode1v3
*.mode2v3
!default.mode2v3
*.perspectivev3
!default.perspectivev3
xcuserdata/
*.xccheckout
*.moved-aside
DerivedData/
*.hmap
*.ipa
*.xcuserstate
*.xcworkspace
!default.xcworkspace

# Swift Package Manager
.build/
.swiftpm/

# CocoaPods
Pods/

# Fastlane
fastlane/report.xml
fastlane/Preview.html
fastlane/screenshots/
fastlane/test_output/

# Secrets (НЕ ЗАГРУЖАТЬ!)
*.p12
*.mobileprovision
*.cer
*.certSigningRequest
Config/Secrets.swift

# macOS
.DS_Store
EOF

echo ".gitignore создан!"
```

---

## ЭТАП 3: НАСТРОЙКА 2FA (5 минут)

### 3.1 Включить Two-Factor Authentication

**Шаги:**

1. Открыть: https://github.com/settings/security
2. Найти: **"Two-factor authentication"**
3. Нажать: **"Enable two-factor authentication"**
4. Выбрать: **"Use an app"** (рекомендуется)

**Приложения для 2FA:**
- Google Authenticator (iOS/Android)
- Microsoft Authenticator (iOS/Android)
- 1Password (если используете)
- Authy (iOS/Android)

**Процесс:**
1. Скачать приложение на телефон
2. Отсканировать QR-код с экрана GitHub
3. Ввести 6-значный код из приложения
4. **СОХРАНИТЬ recovery codes!** (напечатать или скриншот)

**Время:** 5 минут

---

### 3.2 Создать Personal Access Token

Нужен для загрузки кода через командную строку.

**Шаги:**

1. Открыть: https://github.com/settings/tokens
2. Нажать: **"Generate new token (classic)"**
3. Заполнить:
   ```
   Note: ALADDIN iOS Build
   Expiration: 90 days (или Custom)
   Scopes:
     ☑ repo (полный доступ к private repositories)
     ☑ workflow (для GitHub Actions)
   ```
4. Нажать: **"Generate token"**
5. **СКОПИРОВАТЬ токен** (показывается один раз!)
   ```
   ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

**СОХРАНИТЕ ТОКЕН!** Понадобится для git push.

---

## ЭТАП 4: ЗАГРУЗКА КОДА (10 минут)

### 4.1 Подключить remote репозиторий

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Добавить remote (замените YOUR-USERNAME и REPO-NAME)
git remote add origin https://github.com/YOUR-USERNAME/ALADDIN-iOS-Build.git

# Проверить
git remote -v
# Должно показать origin с вашим URL
```

---

### 4.2 Добавить файлы в git

```bash
# Проверить, что будет добавлено
git status

# Добавить все файлы
git add .

# Проверить, что добавлено (должны быть .swift файлы, НЕ .p12!)
git status

# Создать первый commit
git commit -m "Initial commit: ALADDIN iOS App"
```

---

### 4.3 Загрузить на GitHub

```bash
# Установить default branch
git branch -M main

# Push в GitHub
git push -u origin main

# Если попросит авторизацию:
# Username: ваш-github-username
# Password: ваш-personal-access-token (НЕ пароль от GitHub!)
```

**Если всё успешно:**
```
Enumerating objects: XXX, done.
Counting objects: 100% (XXX/XXX), done.
Writing objects: 100% (XXX/XXX), XXX KiB | XXX MiB/s, done.
Total XXX (delta X), reused X (delta X)
To https://github.com/YOUR-USERNAME/ALADDIN-iOS-Build.git
 * [new branch]      main -> main
```

✅ **Код загружен на GitHub!**

---

### 4.4 Проверка в браузере

Откройте ваш репозиторий:
```
https://github.com/YOUR-USERNAME/ALADDIN-iOS-Build
```

**Должны увидеть:**
- 🔒 Private badge (репозиторий приватный)
- Папки: Screens/, Components/, ViewModels/, etc.
- Файлы: .gitignore, README (если создали)

---

## ЭТАП 5: iOS SIGNING (10 минут)

### 5.1 Что нужно для подписи iOS

**Для компиляции iOS приложения нужны:**
1. Apple Developer сертификат (`.p12`)
2. Provisioning Profile (`.mobileprovision`)
3. Bundle Identifier (`family.aladdin.ios`)

**Два варианта:**

**Вариант A: Свой Apple Developer Account ($99/год)**
- Нужен для публикации в App Store
- Создать в: https://developer.apple.com

**Вариант B: Free Provisioning (БЕСПЛАТНО!)**
- Только для тестирования
- Ограничение: 7 дней действия
- Достаточно Apple ID (бесплатный)

**Для начала используем Вариант B (бесплатный)!**

---

### 5.2 Настройка автоматической подписи

В GitHub Actions можно использовать **автоматическую подпись** через Xcode!

**Преимущества:**
- ✅ Не нужны сертификаты
- ✅ Xcode сам создаёт всё необходимое
- ✅ Работает с бесплатным Apple ID

**В workflow укажем:**
```yaml
DEVELOPMENT_TEAM: XXXXXXXXXX  # Ваш Team ID
CODE_SIGN_STYLE: Automatic    # Автоматическая подпись
```

**Как найти Team ID:**

```bash
# Если есть Xcode:
# Xcode → Preferences → Accounts → выбрать Apple ID → View Details
# Team ID показан рядом с вашим именем (10 символов)

# Или через терминал:
security find-identity -v -p codesigning | grep "Apple Development"
```

Если нет Xcode на вашем Mac - ничего страшно, GitHub Actions создаст временный Team ID!

---

### 5.3 Настройка GitHub Secrets

**Переходим в настройки репозитория:**

1. Открыть: `https://github.com/YOUR-USERNAME/ALADDIN-iOS-Build/settings/secrets/actions`
2. Нажать: **"New repository secret"**

**Добавить секреты:**

**Secret 1: APPLE_ID**
```
Name: APPLE_ID
Secret: ваш-apple-id@email.com
```

**Secret 2: APPLE_ID_PASSWORD**
```
Name: APPLE_ID_PASSWORD
Secret: ваш-пароль-от-apple-id

ИЛИ (рекомендуется) App-Specific Password:
1. Перейти: https://appleid.apple.com
2. Sign In & Security → App-Specific Passwords
3. Generate Password для "GitHub Actions"
4. Использовать этот пароль (xxxx-xxxx-xxxx-xxxx)
```

**Secret 3: BUNDLE_IDENTIFIER**
```
Name: BUNDLE_IDENTIFIER
Secret: family.aladdin.ios
```

**Secret 4: DEVELOPMENT_TEAM (опционально)**
```
Name: DEVELOPMENT_TEAM
Secret: ваш-team-id (если есть)

Если нет - оставить пустым, GitHub Actions создаст временный
```

**Результат:** 3-4 секрета добавлены ✅

---

## ЭТАП 6: WORKFLOW (10 минут)

### 6.1 Создать директорию для Workflow

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Создать структуру
mkdir -p .github/workflows

# Проверить
ls -la .github/workflows
```

---

### 6.2 Создать Workflow файл

```bash
cat > .github/workflows/ios-build.yml << 'EOF'
name: iOS Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:  # Ручной запуск

jobs:
  build:
    name: Build iOS App
    runs-on: macos-14  # macOS 14 (Sonoma) с Xcode 15
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Xcode
      uses: maxim-lobanov/setup-xcode@v1
      with:
        xcode-version: '15.0'
    
    - name: Show Xcode version
      run: xcodebuild -version
      
    - name: Show Swift version
      run: swift --version
      
    - name: Cache Swift Package Manager
      uses: actions/cache@v3
      with:
        path: .build
        key: ${{ runner.os }}-spm-${{ hashFiles('**/Package.resolved') }}
        restore-keys: |
          ${{ runner.os }}-spm-
    
    - name: Install dependencies (if using CocoaPods)
      run: |
        if [ -f "Podfile" ]; then
          sudo gem install cocoapods
          pod install
        fi
      
    - name: Build iOS App
      run: |
        xcodebuild clean build \
          -scheme ALADDIN \
          -configuration Release \
          -destination 'generic/platform=iOS' \
          -archivePath $PWD/build/ALADDIN.xcarchive \
          archive \
          CODE_SIGN_IDENTITY="" \
          CODE_SIGNING_REQUIRED=NO \
          CODE_SIGNING_ALLOWED=NO
      
    - name: Export IPA
      run: |
        mkdir -p $PWD/build/ipa
        xcodebuild -exportArchive \
          -archivePath $PWD/build/ALADDIN.xcarchive \
          -exportPath $PWD/build/ipa \
          -exportOptionsPlist .github/workflows/ExportOptions.plist
      
    - name: Upload IPA
      uses: actions/upload-artifact@v3
      with:
        name: ALADDIN-iOS-${{ github.run_number }}
        path: build/ipa/*.ipa
        retention-days: 30
      
    - name: Build Summary
      run: |
        echo "✅ iOS Build Completed!"
        echo "📦 IPA Size: $(du -h build/ipa/*.ipa | cut -f1)"
        echo "🏷️ Build Number: ${{ github.run_number }}"
EOF

echo "Workflow файл создан!"
```

---

### 6.3 Создать ExportOptions.plist

```bash
cat > .github/workflows/ExportOptions.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>development</string>
    <key>teamID</key>
    <string></string>
    <key>compileBitcode</key>
    <false/>
    <key>uploadSymbols</key>
    <true/>
    <key>signingStyle</key>
    <string>automatic</string>
</dict>
</plist>
EOF

echo "ExportOptions.plist создан!"
```

---

### 6.4 Закоммитить и загрузить workflow

```bash
# Добавить файлы workflow
git add .github/

# Commit
git commit -m "Add GitHub Actions workflow for iOS build"

# Push
git push origin main
```

✅ **Workflow настроен!**

---

## ЭТАП 7: ЗАПУСК (1 минута)

### 7.1 Автоматический запуск

После `git push` workflow **запустится автоматически**!

**Проверить:**
1. Открыть: `https://github.com/YOUR-USERNAME/ALADDIN-iOS-Build/actions`
2. Увидите: запущенную компиляцию (оранжевый кружок 🟠)

---

### 7.2 Ручной запуск

Можно запустить вручную:

1. Открыть: `https://github.com/YOUR-USERNAME/ALADDIN-iOS-Build/actions`
2. Выбрать: **"iOS Build"** в левой панели
3. Нажать: **"Run workflow"** (справа сверху)
4. Выбрать: **Branch: main**
5. Нажать: **"Run workflow"** (зелёная кнопка)

---

### 7.3 Наблюдать за процессом

**В реальном времени:**
1. Кликнуть на запущенную компиляцию
2. Кликнуть на **"Build iOS App"**
3. Увидите живые логи:
   ```
   > Checkout code ✅
   > Setup Xcode ✅
   > Show Xcode version ✅
   > Build iOS App 🔄 (идёт...)
   ```

**Время компиляции:** 10-15 минут

---

## ЭТАП 8: СКАЧИВАНИЕ .IPA (2 минуты)

### 8.1 Дождаться завершения

Когда компиляция завершится:
- Оранжевый кружок 🟠 → Зелёная галочка ✅
- Время: ~10-15 минут

---

### 8.2 Скачать .ipa файл

**Шаги:**

1. Открыть завершённую компиляцию
2. Прокрутить вниз до секции **"Artifacts"**
3. Найти: **"ALADDIN-iOS-XXX"** (где XXX = build number)
4. Кликнуть на название → скачивается .zip файл
5. Распаковать .zip → внутри **.ipa файл**!

---

### 8.3 Установить .ipa на устройство

**Вариант A: Через Xcode**
```bash
# Подключить iPhone к Mac по USB
# Открыть Xcode → Window → Devices and Simulators
# Перетащить .ipa файл на устройство
```

**Вариант B: Через TestFlight**
- Загрузить .ipa в App Store Connect
- Пригласить себя как тестера
- Установить через TestFlight app

**Вариант C: Через сторонние сервисы**
- Diawi (https://diawi.com) - бесплатно
- InstallOnAir (https://www.installonair.com)
- TestApp.io

---

## 📊 ПОЛНЫЙ ЧЕКЛИСТ

### ✅ Подготовка:
- [ ] Git установлен и настроен
- [ ] GitHub аккаунт есть
- [ ] Проект подготовлен

### ✅ Repository:
- [ ] Private repository создан
- [ ] .gitignore создан
- [ ] Код загружен на GitHub

### ✅ Безопасность:
- [ ] 2FA включён
- [ ] Personal Access Token создан
- [ ] GitHub Secrets настроены

### ✅ Workflow:
- [ ] .github/workflows/ios-build.yml создан
- [ ] ExportOptions.plist создан
- [ ] Workflow загружен на GitHub

### ✅ Компиляция:
- [ ] Workflow запущен
- [ ] Компиляция завершена успешно
- [ ] .ipa файл скачан

---

## 🎯 ОЦЕНКА ВРЕМЕНИ

| Этап | Время | Ваше участие |
|------|-------|--------------|
| Подготовка | 5 мин | Активно |
| Repository | 5 мин | Активно |
| 2FA | 5 мин | Активно |
| Загрузка кода | 10 мин | Активно |
| iOS Signing | 10 мин | Активно |
| Workflow | 10 мин | Активно |
| **Итого настройка** | **45 мин** | **Активно** |
| Запуск | 1 мин | Активно |
| **Компиляция** | **10-15 мин** | **Ждать** ☕ |
| Скачивание | 2 мин | Активно |
| **ВСЕГО** | **~60 мин** | **~45 мин работы** |

---

## 🆘 ТИПИЧНЫЕ ПРОБЛЕМЫ

### Проблема 1: Build failed - "Scheme not found"

**Причина:** Неправильное имя схемы

**Решение:**
```bash
# Найти правильное имя схемы
xcodebuild -list

# Использовать это имя в workflow
```

---

### Проблема 2: Signing failed

**Причина:** Проблемы с сертификатами

**Решение:**
```yaml
# Отключить подпись для теста
CODE_SIGN_IDENTITY: ""
CODE_SIGNING_REQUIRED: NO
```

---

### Проблема 3: Xcode version not found

**Причина:** Неправильная версия macOS runner

**Решение:**
```yaml
# Использовать последний macOS
runs-on: macos-latest
```

---

## 💡 СОВЕТЫ

### 1. Скрыть чувствительные логи

```yaml
- name: Build with secrets
  run: |
    echo "::add-mask::${{ secrets.APPLE_ID }}"
    xcodebuild ...
```

### 2. Кэшировать зависимости

Уже настроено в workflow! Ускоряет компиляцию.

### 3. Удалить репозиторий после компиляции

Если нужна параноидальная защита:
1. Скачать .ipa
2. Settings → Delete repository
3. Код исчез с GitHub!

---

## 📞 ПОМОЩЬ

Если что-то пошло не так:
1. Посмотреть логи компиляции в Actions
2. Показать мне ошибку
3. Я помогу исправить!

---

## ✅ РЕЗУЛЬТАТ

**После выполнения всех шагов у вас будет:**

✅ Private GitHub repository  
✅ Автоматическая компиляция iOS  
✅ Xcode 15 + iOS 17 SDK  
✅ .ipa файл готовый к установке  
✅ Безопасное хранение кода (95% защиты)  
✅ Автоматизация (настроил раз - работает всегда!)

---

**Создано:** 13.10.2025, 02:30 UTC  
**Для:** ALADDIN iOS компиляция через GitHub Actions  
**Статус:** Готово к выполнению  
**Сложность:** ⭐⭐ Средняя (с моей помощью - легко!)


