# 📋 ДЕТАЛЬНЫЙ ПЛАН ИЗМЕНЕНИЙ WORKFLOW - BUILD 9

**Дата:** 15 декабря 2025  
**Файл:** `.github/workflows/check-secrets.yml`  
**Цель:** Убрать все упоминания Extension/ALADDINPacketTunnel, так как target удален из проекта

---

## ✅ БЭКАП СОЗДАН

**Файл бэкапа:** `.github/workflows/check-secrets.yml.backup_20251215_182018`

---

## 🔍 АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

### Статистика:
- **Всего строк:** 1616
- **Упоминаний Extension/ALADDINPacketTunnel:** 180
- **Targets в проекте:** ALADDIN, ALADDINUnitTests, ALADDINUITests (нет ALADDINPacketTunnel)

### Основные места упоминания Extension:

1. **Строка 385-484:** `Decode Extension Profile` - декодирование профиля
2. **Строка 486-686:** `Extract Extension Profile UUID` - извлечение UUID
3. **Строка 688-840:** `Force Extract UUID and Rename Profiles` - принудительное извлечение
4. **Строка 842-867:** `Verify Profiles` - проверка профилей
5. **Строка 869-1016:** `Prepare Profiles for Build` - подготовка профилей
6. **Строка 1052-1172:** `Verify Profiles for Build` - проверка перед сборкой
7. **Строка 1174-1312:** `Create xcconfig for Build` - создание xcconfig с ALADDINPacketTunnel
8. **Строка 1314-1391:** `Prepare Build Environment` - подготовка окружения
9. **Строка 1393-1443:** `Diagnose Profiles and Certificates` - диагностика
10. **Строка 1506-1564:** `Export IPA` - создание ExportOptions.plist с extension

---

## 📋 ДЕТАЛЬНЫЙ ПЛАН ИЗМЕНЕНИЙ

### **ШАГ 1: Добавить проверку существования Extension target**

**Место:** После шага "Show Xcode version" (после строки 35)

**Действие:** Добавить новый шаг для проверки targets в проекте

```yaml
- name: Check Extension Target
  id: check_extension
  run: |
    echo "🔍 Checking if ALADDINPacketTunnel target exists..."
    TARGETS=$(xcodebuild -project ALADDIN.xcodeproj -list 2>&1 | grep -A 10 "Targets:" | grep -i "ALADDINPacketTunnel" || echo "")
    if [ -z "$TARGETS" ]; then
      echo "✅ ALADDINPacketTunnel target NOT found - Extension removed from project"
      echo "EXTENSION_EXISTS=false" >> $GITHUB_ENV
      echo "::set-output name=exists::false"
    else
      echo "⚠️  ALADDINPacketTunnel target found - Extension still exists"
      echo "EXTENSION_EXISTS=true" >> $GITHUB_ENV
      echo "::set-output name=exists::true"
    fi
```

**Проверка:** После добавления проверить, что переменная `EXTENSION_EXISTS` установлена

---

### **ШАГ 2: Изменить шаг "Decode Extension Profile"**

**Место:** Строка 385-484

**Текущее поведение:** 
- Требует `PROVISIONING_PROFILE_EXTENSION` секрет
- Exit 1 если секрет не установлен

**Новое поведение:**
- Проверяет `EXTENSION_EXISTS`
- Если `EXTENSION_EXISTS=false`, пропускает шаг (exit 0)
- Если `EXTENSION_EXISTS=true`, работает как раньше

**Изменения:**
```yaml
- name: Decode Extension Profile
  if: env.EXTENSION_EXISTS == 'true'
  run: |
    PROFILE_DIR="$HOME/Library/MobileDevice/Provisioning Profiles"
    
    # Проверка что секрет установлен
    if [ -z "${{ secrets.PROVISIONING_PROFILE_EXTENSION }}" ]; then
      echo "❌❌❌ КРИТИЧЕСКАЯ ОШИБКА ❌❌❌"
      echo "PROVISIONING_PROFILE_EXTENSION secret is not set!"
      # ... остальной код ...
      exit 1
    fi
    # ... остальной код без изменений ...
```

**Добавить в начало:**
```yaml
- name: Decode Extension Profile
  if: env.EXTENSION_EXISTS == 'true'
  run: |
    echo "📦 Extension target exists - decoding extension profile..."
    # ... весь существующий код ...
```

**Добавить альтернативный шаг:**
```yaml
- name: Skip Extension Profile (Extension removed)
  if: env.EXTENSION_EXISTS == 'false'
  run: |
    echo "✅ Extension target removed from project - skipping extension profile setup"
    echo "EXT_PROFILE_UUID=" >> $GITHUB_ENV
    echo "EXT_PROFILE_PATH=" >> $GITHUB_ENV
```

**Проверка:** Убедиться, что переменные `EXT_PROFILE_UUID` и `EXT_PROFILE_PATH` установлены в пустые значения

---

### **ШАГ 3: Изменить шаг "Extract Extension Profile UUID"**

**Место:** Строка 486-686

**Текущее поведение:** Всегда пытается извлечь UUID

**Новое поведение:**
- Проверяет `EXTENSION_EXISTS`
- Если `EXTENSION_EXISTS=false`, пропускает шаг

**Изменения:**
```yaml
- name: Extract Extension Profile UUID
  if: env.EXTENSION_EXISTS == 'true'
  run: |
    # ... весь существующий код без изменений ...
```

**Проверка:** Убедиться, что шаг пропускается, если Extension не существует

---

### **ШАГ 4: Изменить шаг "Force Extract UUID and Rename Profiles"**

**Место:** Строка 688-840

**Текущее поведение:** Всегда пытается извлечь UUID для extension

**Новое поведение:**
- Проверяет `EXTENSION_EXISTS`
- Если `EXTENSION_EXISTS=false`, пропускает обработку extension (но обрабатывает app)

**Изменения:**
Внутри шага, в секции обработки extension (после строки 767):
```yaml
        # КРИТИЧЕСКИ ВАЖНО: Извлечь UUID из extension.mobileprovision и переименовать
        if [ "${{ env.EXTENSION_EXISTS }}" = "true" ] && [ -f "$PROFILE_DIR/extension.mobileprovision" ]; then
          echo "🔄 Извлечение UUID из extension.mobileprovision..."
          # ... весь существующий код обработки extension ...
        else
          echo "✅ Extension target removed - skipping extension profile processing"
        fi
```

**Проверка:** Убедиться, что extension профиль не обрабатывается, если target не существует

---

### **ШАГ 5: Изменить шаг "Verify Profiles"**

**Место:** Строка 842-867

**Текущее поведение:** Всегда проверяет extension профиль

**Новое поведение:**
- Проверяет `EXTENSION_EXISTS`
- Если `EXTENSION_EXISTS=false`, пропускает проверку extension

**Изменения:**
Внутри шага, в секции проверки extension (после строки 860):
```yaml
        if [ "${{ env.EXTENSION_EXISTS }}" = "true" ]; then
          if [ -n "$EXT_PROFILE_UUID" ] && [[ "$EXT_PROFILE_UUID" =~ ^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-f]{12}$ ]]; then
            # ... весь существующий код проверки extension ...
          fi
        else
          echo "✅ Extension target removed - skipping extension profile verification"
        fi
```

**Проверка:** Убедиться, что проверка extension пропускается

---

### **ШАГ 6: Изменить шаг "Prepare Profiles for Build"**

**Место:** Строка 869-1016

**Текущее поведение:** Всегда пытается подготовить extension профиль

**Новое поведение:**
- Проверяет `EXTENSION_EXISTS`
- Если `EXTENSION_EXISTS=false`, пропускает подготовку extension профиля

**Изменения:**
Внутри шага, в секции обработки extension (после строки 904):
```yaml
        if [ "${{ env.EXTENSION_EXISTS }}" = "true" ]; then
          if [ -z "$EXT_PROFILE_UUID" ] && [ -f "$PROFILE_DIR/extension.mobileprovision" ]; then
            # ... весь существующий код обработки extension ...
          fi
        else
          echo "✅ Extension target removed - skipping extension profile preparation"
          echo "EXT_PROFILE_UUID=" >> $GITHUB_ENV
          echo "EXT_PROFILE_PATH=" >> $GITHUB_ENV
        fi
```

**Также изменить проверку (строка 982):**
```yaml
        # Проверить что у нас есть хотя бы bundle ID для профилей
        if [ -z "$APP_PROFILE_UUID" ]; then
          echo "❌ Failed to extract provisioning profile UUID for app!"
          echo "APP_PROFILE_UUID: $APP_PROFILE_UUID"
          exit 1
        fi
        
        # Проверка extension профиля только если target существует
        if [ "${{ env.EXTENSION_EXISTS }}" = "true" ] && [ -z "$EXT_PROFILE_UUID" ]; then
          echo "❌ Failed to extract provisioning profile UUID for extension!"
          echo "EXT_PROFILE_UUID: $EXT_PROFILE_UUID"
          exit 1
        fi
```

**Проверка:** Убедиться, что проверка extension пропускается, если target не существует

---

### **ШАГ 7: Изменить шаг "Verify Profiles for Build"**

**Место:** Строка 1052-1172

**Текущее поведение:** Всегда проверяет extension профиль

**Новое поведение:**
- Проверяет `EXTENSION_EXISTS`
- Если `EXTENSION_EXISTS=false`, пропускает проверку extension

**Изменения:**
Внутри шага, в секции проверки extension (после строки 1082):
```yaml
        if [ "${{ env.EXTENSION_EXISTS }}" = "true" ]; then
          if [[ "$EXT_PROFILE_UUID" =~ ^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$ ]]; then
            # ... весь существующий код проверки extension ...
          fi
        else
          echo "✅ Extension target removed - skipping extension profile verification"
        fi
```

**Также изменить проверку типа профиля (строка 1156):**
```yaml
          # КРИТИЧЕСКАЯ ПРОВЕРКА: Профили должны быть App Store Distribution
          if [ -n "$APP_PROFILE_TYPE" ]; then
            echo ""
            echo "❌❌❌ КРИТИЧЕСКАЯ ОШИБКА ❌❌❌"
            echo "App profile является Development/Ad Hoc, а не App Store Distribution!"
            # ... остальной код ...
          fi
          
          # Проверка extension профиля только если target существует
          if [ "${{ env.EXTENSION_EXISTS }}" = "true" ] && [ -n "$EXT_PROFILE_TYPE" ]; then
            echo ""
            echo "❌❌❌ КРИТИЧЕСКАЯ ОШИБКА ❌❌❌"
            echo "Extension profile является Development/Ad Hoc, а не App Store Distribution!"
            # ... остальной код ...
          fi
```

**Проверка:** Убедиться, что проверка extension пропускается

---

### **ШАГ 8: Изменить шаг "Create xcconfig for Build"**

**Место:** Строка 1174-1312

**Текущее поведение:** Всегда создает настройки для ALADDINPacketTunnel

**Новое поведение:**
- Проверяет `EXTENSION_EXISTS`
- Если `EXTENSION_EXISTS=false`, не добавляет настройки для ALADDINPacketTunnel

**Изменения:**
Внутри шага, в секции создания xcconfig (после строки 1286):
```yaml
            echo ""
            echo "// Extension target"
            if [ "${{ env.EXTENSION_EXISTS }}" = "true" ]; then
              echo "ALADDINPacketTunnel_CODE_SIGN_STYLE = Manual"
              echo "ALADDINPacketTunnel_DEVELOPMENT_TEAM = $APPLE_TEAM_ID"
              echo "ALADDINPacketTunnel_CODE_SIGN_IDENTITY = $DIST_CERT_NAME"
              echo "ALADDINPacketTunnel_PRODUCT_BUNDLE_IDENTIFIER = family.aladdin.ios.packetTunnel"
              # ... весь существующий код настройки extension ...
            else
              echo "// Extension target removed - no configuration needed"
            fi
```

**Проверка:** Убедиться, что настройки ALADDINPacketTunnel не добавляются в xcconfig

---

### **ШАГ 9: Изменить шаг "Prepare Build Environment"**

**Место:** Строка 1314-1391

**Текущее поведение:** Всегда пытается найти extension профиль

**Новое поведение:**
- Проверяет `EXTENSION_EXISTS`
- Если `EXTENSION_EXISTS=false`, пропускает поиск extension профиля

**Изменения:**
Внутри шага, в секции определения путей к профилям (после строки 1354):
```yaml
        if [ "${{ env.EXTENSION_EXISTS }}" = "true" ]; then
          if [[ "$EXT_PROFILE_UUID" =~ ^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$ ]]; then
            EXT_PROFILE_FILE="$PROFILE_DIR/${EXT_PROFILE_UUID}.mobileprovision"
          elif [ -n "$EXT_PROFILE_PATH" ] && [ -f "$EXT_PROFILE_PATH" ]; then
            EXT_PROFILE_FILE="$EXT_PROFILE_PATH"
          else
            EXT_PROFILE_FILE="$PROFILE_DIR/extension.mobileprovision"
          fi
          
          # Проверить что файл существует
          if [ ! -f "$EXT_PROFILE_FILE" ]; then
            if [[ "$EXT_PROFILE_UUID" =~ ^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$ ]]; then
              echo "❌ Extension profile not found: $EXT_PROFILE_FILE"
              ls -la "$PROFILE_DIR" || true
              exit 1
            else
              echo "⚠️  Extension profile file not found, but using bundle ID: $EXT_PROFILE_UUID"
              EXT_PROFILE_FILE=""
            fi
          else
            echo "✅ Extension profile found: $EXT_PROFILE_FILE"
          fi
        else
          echo "✅ Extension target removed - skipping extension profile file check"
          EXT_PROFILE_FILE=""
        fi
```

**Проверка:** Убедиться, что поиск extension профиля пропускается

---

### **ШАГ 10: Изменить шаг "Diagnose Profiles and Certificates"**

**Место:** Строка 1393-1443

**Текущее поведение:** Всегда диагностирует extension профиль

**Новое поведение:**
- Проверяет `EXTENSION_EXISTS`
- Если `EXTENSION_EXISTS=false`, пропускает диагностику extension

**Изменения:**
Внутри шага, в секции диагностики extension (после строки 1425):
```yaml
        if [ "${{ env.EXTENSION_EXISTS }}" = "true" ] && [ -f "$EXT_PROFILE_FILE" ]; then
          echo "📋 Extension Profile:"
          EXT_PROFILE_XML=$(security cms -D -i "$EXT_PROFILE_FILE" 2>/dev/null)
          if [ -n "$EXT_PROFILE_XML" ]; then
            EXT_PROFILE_NAME=$(echo "$EXT_PROFILE_XML" | plutil -extract Name raw -o - - 2>/dev/null || echo "unknown")
            EXT_PROFILE_BUNDLE_ID=$(echo "$EXT_PROFILE_XML" | plutil -extract Entitlements.application-identifier raw -o - - 2>/dev/null || echo "unknown")
            echo "   Name: $EXT_PROFILE_NAME"
            echo "   Bundle ID: $EXT_PROFILE_BUNDLE_ID"
          fi
        else
          echo "✅ Extension target removed - skipping extension profile diagnosis"
        fi
```

**Проверка:** Убедиться, что диагностика extension пропускается

---

### **ШАГ 11: Изменить шаг "Export IPA"**

**Место:** Строка 1506-1564

**Текущее поведение:** Всегда добавляет extension bundle ID в ExportOptions.plist

**Новое поведение:**
- Проверяет `EXTENSION_EXISTS`
- Если `EXTENSION_EXISTS=false`, не добавляет extension в ExportOptions.plist

**Изменения:**
Внутри шага, в секции создания ExportOptions.plist (строка 1521-1546):
```yaml
        # Если UUID не извлечены, используем bundle ID (Xcode найдет профили автоматически)
        if [ -z "$APP_PROFILE_UUID" ]; then
          APP_PROFILE_UUID="family.aladdin.ios"
        fi
        
        # Extension UUID только если target существует
        if [ "${{ env.EXTENSION_EXISTS }}" = "true" ]; then
          if [ -z "$EXT_PROFILE_UUID" ]; then
            EXT_PROFILE_UUID="family.aladdin.ios.packetTunnel"
          fi
        else
          EXT_PROFILE_UUID=""
          echo "✅ Extension target removed - will not include extension in ExportOptions.plist"
        fi
        
        # ... остальной код определения SIGNING_STYLE ...
        
        # Создать ExportOptions.plist
        if [ "$SIGNING_STYLE" = "automatic" ]; then
          # Automatic signing - Xcode выберет профили автоматически
          printf '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n  <key>method</key>\n  <string>app-store</string>\n  <key>teamID</key>\n  <string>%s</string>\n  <key>signingStyle</key>\n  <string>automatic</string>\n  <key>uploadBitcode</key>\n  <false/>\n  <key>uploadSymbols</key>\n  <true/>\n  <key>compileBitcode</key>\n  <false/>\n</dict>\n</plist>\n' "$APPLE_TEAM_ID" > ./build/ExportOptions.plist
        else
          # Manual signing - используем установленные профили
          if [ "${{ env.EXTENSION_EXISTS }}" = "true" ] && [ -n "$EXT_PROFILE_UUID" ]; then
            # С extension
            printf '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n  <key>method</key>\n  <string>app-store</string>\n  <key>teamID</key>\n  <string>%s</string>\n  <key>signingStyle</key>\n  <string>manual</string>\n  <key>signingCertificate</key>\n  <string>Apple Distribution</string>\n  <key>provisioningProfiles</key>\n  <dict>\n    <key>family.aladdin.ios</key>\n    <string>%s</string>\n    <key>family.aladdin.ios.packetTunnel</key>\n    <string>%s</string>\n  </dict>\n  <key>uploadBitcode</key>\n  <false/>\n  <key>uploadSymbols</key>\n  <true/>\n  <key>compileBitcode</key>\n  <false/>\n</dict>\n</plist>\n' "$APPLE_TEAM_ID" "$APP_PROFILE_UUID" "$EXT_PROFILE_UUID" > ./build/ExportOptions.plist
          else
            # Без extension
            printf '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n  <key>method</key>\n  <string>app-store</string>\n  <key>teamID</key>\n  <string>%s</string>\n  <key>signingStyle</key>\n  <string>manual</string>\n  <key>signingCertificate</key>\n  <string>Apple Distribution</string>\n  <key>provisioningProfiles</key>\n  <dict>\n    <key>family.aladdin.ios</key>\n    <string>%s</string>\n  </dict>\n  <key>uploadBitcode</key>\n  <false/>\n  <key>uploadSymbols</key>\n  <true/>\n  <key>compileBitcode</key>\n  <false/>\n</dict>\n</plist>\n' "$APPLE_TEAM_ID" "$APP_PROFILE_UUID" > ./build/ExportOptions.plist
          fi
        fi
```

**Проверка:** Убедиться, что ExportOptions.plist не содержит extension bundle ID, если target не существует

---

## ✅ ПРОВЕРКА ПОСЛЕ ИЗМЕНЕНИЙ

### 1. Синтаксис YAML:
```bash
# Проверить синтаксис YAML
yamllint .github/workflows/check-secrets.yml
```

### 2. Проверка переменных:
- ✅ `EXTENSION_EXISTS` устанавливается в начале workflow
- ✅ Все шаги проверяют `EXTENSION_EXISTS` перед обработкой extension
- ✅ `EXT_PROFILE_UUID` и `EXT_PROFILE_PATH` устанавливаются в пустые значения, если extension не существует

### 3. Проверка ExportOptions.plist:
- ✅ Не содержит `family.aladdin.ios.packetTunnel`, если extension не существует
- ✅ Содержит только `family.aladdin.ios`

### 4. Проверка xcconfig:
- ✅ Не содержит настройки `ALADDINPacketTunnel_*`, если extension не существует

---

## 📝 ПОРЯДОК ВЫПОЛНЕНИЯ

1. ✅ **ШАГ 1:** Добавить проверку существования Extension target
2. ✅ **ШАГ 2:** Изменить шаг "Decode Extension Profile"
3. ✅ **ШАГ 3:** Изменить шаг "Extract Extension Profile UUID"
4. ✅ **ШАГ 4:** Изменить шаг "Force Extract UUID and Rename Profiles"
5. ✅ **ШАГ 5:** Изменить шаг "Verify Profiles"
6. ✅ **ШАГ 6:** Изменить шаг "Prepare Profiles for Build"
7. ✅ **ШАГ 7:** Изменить шаг "Verify Profiles for Build"
8. ✅ **ШАГ 8:** Изменить шаг "Create xcconfig for Build"
9. ✅ **ШАГ 9:** Изменить шаг "Prepare Build Environment"
10. ✅ **ШАГ 10:** Изменить шаг "Diagnose Profiles and Certificates"
11. ✅ **ШАГ 11:** Изменить шаг "Export IPA"

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Все изменения должны быть условными** - использовать `if: env.EXTENSION_EXISTS == 'true'` или проверки внутри скриптов
2. **Не удалять код** - только оборачивать в условия, чтобы можно было вернуть, если понадобится
3. **Всегда устанавливать пустые значения** для `EXT_PROFILE_UUID` и `EXT_PROFILE_PATH`, если extension не существует
4. **Проверять синтаксис YAML** после каждого изменения
5. **Тестировать на локальной машине** перед коммитом (если возможно)

---

**Статус:** ✅ **ПЛАН ГОТОВ** - можно начинать выполнение по шагам
