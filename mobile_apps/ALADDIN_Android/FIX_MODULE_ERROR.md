# 🔧 Исправление ошибки "Module not specified" в Android Studio

## ❌ **ПРОБЛЕМА**
При попытке запуска приложения в Android Studio появляется ошибка:
```
Error: Module not specified
```

## ✅ **РЕШЕНИЕ**

### 1. **Откройте проект в Android Studio**
```bash
open -a "Android Studio" /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android
```

### 2. **Проверьте конфигурацию модуля**
1. В Android Studio перейдите в **Run → Edit Configurations**
2. Убедитесь, что в поле **Module** выбрано: `ALADDIN.app`
3. Если поле пустое, выберите `ALADDIN.app` из выпадающего списка

### 3. **Если модуль не отображается**
1. Перейдите в **File → Sync Project with Gradle Files**
2. Дождитесь завершения синхронизации
3. Перейдите в **Build → Clean Project**
4. Затем **Build → Rebuild Project**

### 4. **Альтернативный способ**
1. Закройте Android Studio
2. Удалите папку `.idea` (если есть)
3. Откройте проект заново
4. Android Studio автоматически создаст правильную конфигурацию

### 5. **Проверьте настройки проекта**
1. **File → Project Structure**
2. В разделе **Modules** должен быть модуль `app`
3. Убедитесь, что **Module SDK** установлен на Android API 34

## 🚀 **ЗАПУСК ПРИЛОЖЕНИЯ**

### **Вариант 1: Через Android Studio**
1. Откройте проект
2. Выберите конфигурацию "ALADDIN Debug"
3. Нажмите кнопку **Run** (▶️) или **Debug** (🐛)

### **Вариант 2: Через командную строку**
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android
./install_app.sh
```

### **Вариант 3: Прямая установка APK**
```bash
# Установка на подключенное устройство
adb install app/build/outputs/apk/debug/app-debug.apk

# Запуск приложения
adb shell am start -n family.aladdin.android/.MainActivity
```

## 📱 **ТЕСТИРОВАНИЕ**

После исправления ошибки вы сможете:
- ✅ Запустить приложение на эмуляторе
- ✅ Запустить приложение на физическом устройстве
- ✅ Использовать отладчик Android Studio
- ✅ Просматривать логи в Logcat

## 🎯 **РЕЗУЛЬТАТ**

После исправления ошибки "Module not specified":
- ✅ Android Studio корректно распознает модуль
- ✅ Приложение запускается без ошибок
- ✅ Доступны все функции отладки
- ✅ APK готов к установке и тестированию

---
*Инструкция создана: 13 октября 2024*  
*Статус: Готово к исправлению* ✅

