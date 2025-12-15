# 📋 ИНСТРУКЦИЯ: Создание конфигурации Release-CI для Manual Signing

## 🎯 ЦЕЛЬ

Создать отдельную конфигурацию `Release-CI` с Manual signing, чтобы:
- ✅ Не влиять на локальную разработку (Release остается с Automatic signing)
- ✅ CI использует Manual signing через Release-CI
- ✅ Минимальные изменения в проекте

---

## 📝 ПОШАГОВАЯ ИНСТРУКЦИЯ

### ШАГ 1: Открыть проект в Xcode

```bash
open ALADDIN.xcodeproj
```

---

### ШАГ 2: Открыть настройки проекта

1. В Xcode выберите **ALADDIN** в левом верхнем углу (проект)
2. В средней панели выберите **PROJECT** → **ALADDIN** (не TARGETS!)
3. Откройте вкладку **Info**

---

### ШАГ 3: Создать новую конфигурацию Release-CI

1. В разделе **Configurations** найдите **Release**
2. Нажмите на кнопку **+** (внизу списка конфигураций)
3. Выберите **Duplicate "Release" Configuration**
4. Переименуйте новую конфигурацию в **Release-CI**
   - Дважды кликните на "Release copy"
   - Введите: `Release-CI`
   - Нажмите Enter

**Результат:** Теперь у вас есть 3 конфигурации:
- Debug
- Release
- Release-CI (новая)

---

### ШАГ 4: Настроить Manual signing для Release-CI (таргет ALADDIN)

1. В средней панели выберите **TARGETS** → **ALADDIN**
2. Откройте вкладку **Build Settings**
3. В поиске введите: `code sign`
4. Найдите **Code Signing Style**
5. Раскройте настройку (нажмите на стрелку слева)
6. Для конфигурации **Release-CI** установите значение **Manual**
   - Кликните на значение "Automatic" для Release-CI
   - Выберите **Manual** из выпадающего списка

7. Найдите **Provisioning Profile Specifier**
8. Для конфигурации **Release-CI** оставьте пустым (будет переопределено через xcconfig)

**Результат:** Таргет ALADDIN использует Manual signing только для Release-CI

---

### ШАГ 5: Настроить Manual signing для Release-CI (таргет ALADDINPacketTunnel)

1. В средней панели выберите **TARGETS** → **ALADDINPacketTunnel**
2. Откройте вкладку **Build Settings**
3. В поиске введите: `code sign`
4. Найдите **Code Signing Style**
5. Раскройте настройку
6. Для конфигурации **Release-CI** установите значение **Manual**

7. Найдите **Provisioning Profile Specifier**
8. Для конфигурации **Release-CI** оставьте пустым (будет переопределено через xcconfig)

**Результат:** Таргет ALADDINPacketTunnel использует Manual signing только для Release-CI

---

### ШАГ 6: Сохранить проект

Нажмите **⌘S** (Cmd + S) для сохранения проекта

---

### ШАГ 7: Проверить изменения

1. Откройте `ALADDIN.xcodeproj/project.pbxproj` в текстовом редакторе
2. Найдите `Release-CI` в файле
3. Убедитесь, что для Release-CI установлено:
   - `CODE_SIGN_STYLE = Manual;`
   - Для обоих таргетов (ALADDIN и ALADDINPacketTunnel)

---

## ✅ РЕЗУЛЬТАТ

После выполнения этих шагов:

- ✅ Конфигурация **Release-CI** создана
- ✅ **Release-CI** использует Manual signing
- ✅ **Release** остается с Automatic signing (для локальной разработки)
- ✅ **Debug** остается с Automatic signing (для локальной разработки)

---

## 🔍 ПРОВЕРКА

### Проверить в Xcode:

1. Выберите **TARGETS** → **ALADDIN**
2. Откройте **Build Settings**
3. Найдите **Code Signing Style**
4. Убедитесь, что:
   - Debug: **Automatic** ✅
   - Release: **Automatic** ✅
   - Release-CI: **Manual** ✅

### Проверить в project.pbxproj:

```bash
grep -A 5 "Release-CI" ALADDIN.xcodeproj/project.pbxproj | grep "CODE_SIGN_STYLE"
```

Должно быть: `CODE_SIGN_STYLE = Manual;`

---

## 🚀 СЛЕДУЮЩИЙ ШАГ

После создания конфигурации Release-CI:
1. Workflow будет обновлен для использования `-configuration Release-CI`
2. Запустить workflow и проверить результат

---

## ⚠️ ВАЖНО

- **НЕ изменяйте** конфигурации Debug и Release
- **ТОЛЬКО** Release-CI должна использовать Manual signing
- Это гарантирует, что локальная разработка не затронута

---

**Дата создания:** 2 декабря 2024  
**Статус:** Готово к выполнению

