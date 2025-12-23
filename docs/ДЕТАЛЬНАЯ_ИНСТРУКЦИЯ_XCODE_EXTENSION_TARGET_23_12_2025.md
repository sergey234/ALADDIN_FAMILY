# 📋 ДЕТАЛЬНАЯ ИНСТРУКЦИЯ: СОЗДАНИЕ EXTENSION TARGET И НАСТРОЙКА APP GROUPS В XCODE

**Дата:** 23 декабря 2025  
**Проект:** ALADDIN iOS  
**Extension:** Content Blocker Extension для Safari

---

## 🎯 ЧТО МЫ ДЕЛАЕМ

1. Создаем Extension Target для Content Blocker
2. Настраиваем App Groups для обмена данными между приложением и extension
3. Подключаем созданные файлы к проекту
4. Настраиваем зависимости и Bundle Identifier

---

## 📝 ШАГ 1: СОЗДАНИЕ EXTENSION TARGET

### 1.1 Открыть проект в Xcode

1. Откройте файл `ALADDIN.xcodeproj` в Xcode
2. Убедитесь, что проект загружен полностью

### 1.2 Создать новый Target

1. В верхнем меню Xcode выберите: **File → New → Target...**
   - Или нажмите комбинацию клавиш: `⌘ + Shift + N`
   - Или кликните правой кнопкой мыши на проект в навигаторе → **New Target...**

2. В открывшемся окне **Choose a template for your new target:**
   - В левой панели выберите раздел **iOS**
   - В правой панели найдите и выберите: **Content Blocker Extension**
   - Нажмите кнопку **Next** (внизу справа)

### 1.3 Настроить параметры Extension

В окне **Content Blocker Extension** заполните:

**Product Name:**
```
ALADDINContentBlocker
```

**Team:**
- Выберите вашу команду разработчика (если есть)

**Organization Identifier:**
```
family.aladdin.ios
```

**Bundle Identifier:**
- Должен автоматически заполниться как: `family.aladdin.ios.ALADDINContentBlocker`
- Если нет, введите вручную: `family.aladdin.ios.ContentBlocker`

**Language:**
- Выберите: **Swift**

**Embed in Application:**
- Выберите: **ALADDIN** (основное приложение)

**Include Unit Tests:**
- ❌ Снимите галочку (не нужно)

**Include UI Tests:**
- ❌ Снимите галочку (не нужно)

### 1.4 Завершить создание

1. Нажмите кнопку **Finish**

2. Xcode спросит: **"Activate 'ALADDINContentBlocker' scheme?"**
   - Нажмите **Activate** (это активирует схему для нового target)

3. Xcode может спросить: **"Copy items if needed?"**
   - ❌ Снимите галочку (файлы мы добавим вручную)
   - Нажмите **Finish**

### 1.5 Проверка создания

После создания вы должны увидеть:

1. В навигаторе проекта (левая панель) появилась новая папка:
   ```
   ALADDINContentBlocker/
   ├── ALADDINContentBlocker/
   │   ├── ActionRequestHandler.swift (автоматически создан Xcode)
   │   └── Info.plist
   └── ALADDINContentBlockerTests/ (если создали тесты)
   ```

2. В списке Targets (выберите проект в навигаторе → вкладка Targets) появился:
   ```
   ALADDINContentBlocker
   ```

3. В схеме сборки (scheme) появился:
   ```
   ALADDINContentBlocker
   ```

---

## 📝 ШАГ 2: НАСТРОЙКА APP GROUPS

### 2.1 Настроить App Groups для основного приложения (ALADDIN)

1. В навигаторе проекта выберите **проект ALADDIN** (самый верхний элемент)

2. В центральной панели выберите **target ALADDIN** (не extension!)

3. Перейдите на вкладку **Signing & Capabilities** (вверху)

4. Нажмите кнопку **+ Capability** (в левом верхнем углу секции Capabilities)

5. В открывшемся списке найдите и выберите: **App Groups**

6. В секции **App Groups** появится поле для ввода

7. Нажмите кнопку **+** (плюс) в секции App Groups

8. Введите идентификатор:
   ```
   group.com.aladdin.family
   ```

9. Нажмите **OK** или **Enter**

10. Убедитесь, что:
    - ✅ Галочка стоит напротив `group.com.aladdin.family`
    - ✅ В секции App Groups отображается: `group.com.aladdin.family`

### 2.2 Настроить App Groups для Extension (ALADDINContentBlocker)

1. В навигаторе проекта выберите **проект ALADDIN** (самый верхний элемент)

2. В центральной панели выберите **target ALADDINContentBlocker** (extension!)

3. Перейдите на вкладку **Signing & Capabilities** (вверху)

4. Нажмите кнопку **+ Capability** (в левом верхнем углу секции Capabilities)

5. В открывшемся списке найдите и выберите: **App Groups**

6. В секции **App Groups** появится поле для ввода

7. Нажмите кнопку **+** (плюс) в секции App Groups

8. Введите **ТОТ ЖЕ** идентификатор:
   ```
   group.com.aladdin.family
   ```

9. Нажмите **OK** или **Enter**

10. Убедитесь, что:
    - ✅ Галочка стоит напротив `group.com.aladdin.family`
    - ✅ В секции App Groups отображается: `group.com.aladdin.family`
    - ✅ **ВАЖНО:** Идентификатор должен быть **ИДЕНТИЧНЫМ** для обоих targets!

### 2.3 Проверка App Groups

Убедитесь, что:

1. ✅ Target **ALADDIN** имеет App Group: `group.com.aladdin.family`
2. ✅ Target **ALADDINContentBlocker** имеет App Group: `group.com.aladdin.family`
3. ✅ Оба используют **ОДИН И ТОТ ЖЕ** идентификатор

---

## 📝 ШАГ 3: ПОДКЛЮЧИТЬ СОЗДАННЫЕ ФАЙЛЫ К ПРОЕКТУ

### 3.1 Заменить ActionRequestHandler.swift

1. В навигаторе проекта найдите файл:
   ```
   ALADDINContentBlocker/ALADDINContentBlocker/ActionRequestHandler.swift
   ```

2. Откройте этот файл (дважды кликните)

3. **УДАЛИТЕ** весь содержимое файла (выделите все `⌘ + A` → Delete)

4. Откройте файл, который мы создали:
   ```
   ALADDINContentBlocker/ActionRequestHandler.swift
   ```
   (в корне проекта, рядом с папкой Core)

5. Скопируйте весь код из созданного файла (`⌘ + A` → `⌘ + C`)

6. Вставьте в файл в Xcode (`⌘ + V`)

7. Сохраните файл (`⌘ + S`)

### 3.2 Добавить ContentBlockerRule.swift в Extension Target

1. В навигаторе проекта найдите файл:
   ```
   Core/ContentBlocker/ContentBlockerRule.swift
   ```

2. Выберите этот файл (один клик)

3. В правой панели (File Inspector) найдите секцию **Target Membership**

4. Убедитесь, что стоят галочки:
   - ✅ **ALADDIN** (основное приложение)
   - ✅ **ALADDINContentBlocker** (extension)

5. Если галочки нет напротив **ALADDINContentBlocker**:
   - Поставьте галочку ✅

### 3.3 Проверить, что файлы в правильных targets

Проверьте Target Membership для следующих файлов:

**Core/ContentBlocker/ContentBlockerRule.swift:**
- ✅ ALADDIN
- ✅ ALADDINContentBlocker

**Core/ContentBlocker/ContentBlockerManager.swift:**
- ✅ ALADDIN
- ❌ ALADDINContentBlocker (НЕ должен быть здесь!)

**Components/Modals/FamilyContentBlockModal.swift:**
- ✅ ALADDIN
- ❌ ALADDINContentBlocker (НЕ должен быть здесь!)

**Screens/07_ParentalControlScreen.swift:**
- ✅ ALADDIN
- ❌ ALADDINContentBlocker (НЕ должен быть здесь!)

---

## 📝 ШАГ 4: НАСТРОИТЬ INFO.PLIST ДЛЯ EXTENSION

### 4.1 Открыть Info.plist Extension

1. В навигаторе проекта найдите файл:
   ```
   ALADDINContentBlocker/ALADDINContentBlocker/Info.plist
   ```

2. Откройте этот файл (дважды кликните)

3. Если файл открывается как Property List (таблица):
   - Кликните правой кнопкой мыши на файл
   - Выберите **Open As → Source Code**

### 4.2 Проверить содержимое Info.plist

Убедитесь, что в файле есть следующие ключи:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>$(DEVELOPMENT_LANGUAGE)</string>
    <key>CFBundleDisplayName</key>
    <string>ALADDIN Content Blocker</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>$(PRODUCT_BUNDLE_PACKAGE_TYPE)</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSExtension</key>
    <dict>
        <key>NSExtensionPointIdentifier</key>
        <string>com.apple.Safari.content-blocker</string>
        <key>NSExtensionPrincipalClass</key>
        <string>$(PRODUCT_MODULE_NAME).ActionRequestHandler</string>
    </dict>
</dict>
</plist>
```

### 4.3 Если ключей нет - добавить

Если в Info.plist нет секции `NSExtension`:

1. Добавьте перед закрывающим тегом `</dict>`:

```xml
    <key>NSExtension</key>
    <dict>
        <key>NSExtensionPointIdentifier</key>
        <string>com.apple.Safari.content-blocker</string>
        <key>NSExtensionPrincipalClass</key>
        <string>$(PRODUCT_MODULE_NAME).ActionRequestHandler</string>
    </dict>
```

2. Сохраните файл (`⌘ + S`)

---

## 📝 ШАГ 5: НАСТРОИТЬ BUNDLE IDENTIFIER

### 5.1 Проверить Bundle Identifier основного приложения

1. Выберите проект в навигаторе
2. Выберите target **ALADDIN**
3. Перейдите на вкладку **General**
4. Найдите секцию **Identity**
5. Убедитесь, что **Bundle Identifier:** `family.aladdin.ios`

### 5.2 Проверить Bundle Identifier Extension

1. Выберите проект в навигаторе
2. Выберите target **ALADDINContentBlocker**
3. Перейдите на вкладку **General**
4. Найдите секцию **Identity**
5. Убедитесь, что **Bundle Identifier:** `family.aladdin.ios.ContentBlocker`

**ВАЖНО:** Bundle Identifier Extension должен быть под Bundle ID основного приложения!

---

## 📝 ШАГ 6: НАСТРОИТЬ DEPENDENCIES (ОПЦИОНАЛЬНО)

### 6.1 Проверить зависимости

1. Выберите проект в навигаторе
2. Выберите target **ALADDINContentBlocker**
3. Перейдите на вкладку **Build Phases**
4. Найдите секцию **Dependencies**

Обычно зависимости настраиваются автоматически, но если нужно:

1. Нажмите **+** в секции Dependencies
2. Выберите **ALADDIN**
3. Нажмите **Add**

---

## 📝 ШАГ 7: ПРОВЕРКА НАСТРОЙКИ

### 7.1 Чеклист

Проверьте, что все настроено правильно:

- [ ] Extension Target создан: **ALADDINContentBlocker**
- [ ] App Groups настроены для **ALADDIN**: `group.com.aladdin.family`
- [ ] App Groups настроены для **ALADDINContentBlocker**: `group.com.aladdin.family`
- [ ] Оба используют **ОДИН И ТОТ ЖЕ** App Group
- [ ] Info.plist Extension содержит `NSExtension` с правильными ключами
- [ ] Bundle Identifier основного приложения: `family.aladdin.ios`
- [ ] Bundle Identifier Extension: `family.aladdin.ios.ContentBlocker`
- [ ] ActionRequestHandler.swift содержит наш код
- [ ] ContentBlockerRule.swift добавлен в оба targets
- [ ] Проект компилируется без ошибок

### 7.2 Попробовать собрать проект

1. Выберите схему сборки: **ALADDINContentBlocker**
2. Выберите устройство или симулятор
3. Нажмите **⌘ + B** (Build)
4. Убедитесь, что проект компилируется без ошибок

Если есть ошибки:
- Проверьте, что все файлы добавлены в правильные targets
- Проверьте, что App Groups настроены правильно
- Проверьте, что Bundle Identifier правильный

---

## 📝 ШАГ 8: ТЕСТИРОВАНИЕ

### 8.1 Запустить приложение

1. Выберите схему сборки: **ALADDIN** (основное приложение)
2. Выберите устройство или симулятор
3. Нажмите **⌘ + R** (Run)

### 8.2 Проверить Content Blocker в настройках iOS

1. На устройстве откройте **Настройки iOS**
2. Перейдите в **Safari**
3. Перейдите в **Content Blockers** (Блокировщики контента)
4. Убедитесь, что **ALADDIN** появился в списке
5. Включите переключатель для **ALADDIN**

### 8.3 Протестировать блокировку

1. Откройте Safari на устройстве
2. Попробуйте зайти на заблокированный сайт (например, сайт с взрослым контентом)
3. Сайт должен быть заблокирован

---

## ❌ ЧАСТЫЕ ОШИБКИ И РЕШЕНИЯ

### Ошибка 1: "No such module 'SafariServices'"

**Решение:**
- Убедитесь, что в ActionRequestHandler.swift есть `import SafariServices`
- Проверьте, что файл добавлен в target ALADDINContentBlocker

### Ошибка 2: "App Group not found"

**Решение:**
- Убедитесь, что App Groups настроены для обоих targets
- Убедитесь, что используется один и тот же идентификатор: `group.com.aladdin.family`
- Пересоберите проект

### Ошибка 3: "Content Blocker not appearing in Settings"

**Решение:**
- Убедитесь, что Info.plist содержит правильные ключи NSExtension
- Убедитесь, что Bundle Identifier правильный
- Переустановите приложение на устройстве

### Ошибка 4: "Rules not loading"

**Решение:**
- Убедитесь, что App Groups настроены правильно
- Проверьте, что правила сохраняются в правильный App Group
- Проверьте логи в консоли Xcode

---

## ✅ ГОТОВО!

После выполнения всех шагов Content Blocker Extension должен работать!

Если возникнут проблемы - проверьте логи в консоли Xcode и убедитесь, что все шаги выполнены правильно.

---

**Дата создания:** 23 декабря 2025  
**Версия:** 1.0

