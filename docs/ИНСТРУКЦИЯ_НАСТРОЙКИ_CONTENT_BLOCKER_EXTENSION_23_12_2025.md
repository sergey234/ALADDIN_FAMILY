# 📋 ИНСТРУКЦИЯ: НАСТРОЙКА CONTENT BLOCKER EXTENSION В XCODE

**Дата:** 23 декабря 2025  
**Статус:** ✅ ФАЙЛЫ СОЗДАНЫ, ТРЕБУЕТСЯ НАСТРОЙКА В XCODE

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ ВРУЧНУЮ В XCODE

### ШАГ 1: СОЗДАТЬ EXTENSION TARGET

1. Откройте проект `ALADDIN.xcodeproj` в Xcode
2. В меню выберите: **File → New → Target...**
3. В списке шаблонов выберите: **Content Blocker Extension**
4. Нажмите **Next**
5. Заполните:
   - **Product Name:** `ALADDINContentBlocker`
   - **Bundle Identifier:** `family.aladdin.ios.ContentBlocker`
   - **Language:** Swift
6. Нажмите **Finish**
7. Xcode спросит "Activate scheme?" - нажмите **Activate**

---

### ШАГ 2: НАСТРОИТЬ APP GROUPS

#### Для основного приложения:

1. Выберите проект `ALADDIN` в навигаторе
2. Выберите target **ALADDIN**
3. Перейдите на вкладку **Signing & Capabilities**
4. Нажмите **+ Capability**
5. Выберите **App Groups**
6. Нажмите **+** и добавьте: `group.com.aladdin.family`
7. Убедитесь, что галочка стоит ✅

#### Для Extension:

1. Выберите target **ALADDINContentBlocker**
2. Перейдите на вкладку **Signing & Capabilities**
3. Нажмите **+ Capability**
4. Выберите **App Groups**
5. Нажмите **+** и добавьте: `group.com.aladdin.family`
6. Убедитесь, что галочка стоит ✅

**ВАЖНО:** Оба target должны использовать ОДИН И ТОТ ЖЕ App Group!

---

### ШАГ 3: НАСТРОИТЬ INFO.PLIST ДЛЯ EXTENSION

1. Выберите файл `ALADDINContentBlocker/Info.plist`
2. Убедитесь, что есть следующие ключи:

```xml
<key>NSExtension</key>
<dict>
    <key>NSExtensionPointIdentifier</key>
    <string>com.apple.Safari.content-blocker</string>
    <key>NSExtensionPrincipalClass</key>
    <string>$(PRODUCT_MODULE_NAME).ActionRequestHandler</string>
</dict>
```

Если ключей нет - добавьте их.

---

### ШАГ 4: ПОДКЛЮЧИТЬ СОЗДАННЫЕ ФАЙЛЫ К ПРОЕКТУ

#### Файлы уже созданы, нужно добавить их в Xcode:

1. **ActionRequestHandler.swift:**
   - Файл уже создан: `ALADDINContentBlocker/ActionRequestHandler.swift`
   - Убедитесь, что он добавлен в target **ALADDINContentBlocker**
   - Если нет - перетащите файл в проект и выберите target **ALADDINContentBlocker**

2. **ContentBlockerRule.swift:**
   - Файл создан: `Core/ContentBlocker/ContentBlockerRule.swift`
   - Нужно добавить в target **ALADDINContentBlocker** (в дополнение к основному target)
   - Выберите файл → File Inspector → Target Membership → ✅ ALADDINContentBlocker

---

### ШАГ 5: НАСТРОИТЬ DEPENDENCIES

1. Выберите target **ALADDINContentBlocker**
2. Перейдите на вкладку **Build Phases**
3. В разделе **Dependencies** убедитесь, что есть зависимость от **ALADDIN**
4. Если нет - нажмите **+** и добавьте **ALADDIN**

---

### ШАГ 6: ПРОВЕРИТЬ BUNDLE IDENTIFIER

Убедитесь, что Bundle Identifier для Extension:
- **ALADDIN:** `family.aladdin.ios`
- **ALADDINContentBlocker:** `family.aladdin.ios.ContentBlocker`

---

## ✅ ПРОВЕРКА НАСТРОЙКИ

После настройки проверьте:

1. ✅ Extension Target создан
2. ✅ App Groups настроены для обоих targets
3. ✅ Info.plist содержит правильные ключи
4. ✅ Файлы добавлены в правильные targets
5. ✅ Bundle Identifier правильный
6. ✅ Проект компилируется без ошибок

---

## 🧪 ТЕСТИРОВАНИЕ

1. Запустите приложение на симуляторе или устройстве
2. Перейдите в **Настройки iOS → Safari → Content Blockers**
3. Убедитесь, что **ALADDIN** появился в списке
4. Включите переключатель для **ALADDIN**
5. Откройте Safari и попробуйте зайти на заблокированный сайт
6. Сайт должен быть заблокирован

---

## 📝 ПРИМЕЧАНИЯ

- Extension Target создается автоматически Xcode, но файлы нужно добавить вручную
- App Groups должны быть настроены для обоих targets
- Bundle Identifier Extension должен быть под Bundle ID основного приложения
- После настройки нужно пересобрать проект

---

**Готово!** После настройки Content Blocker Extension будет работать в Safari! 🚀

