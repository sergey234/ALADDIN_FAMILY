# 🔧 ПОШАГОВОЕ ИСПРАВЛЕНИЕ "Module not specified"

## ❌ **ПРОБЛЕМА**
В Android Studio в диалоге "Edit Configuration":
- **Module:** показывает `<no module>` и не дает выбрать
- **Ошибка:** `Error: Module not specified`

## ✅ **ПОШАГОВОЕ РЕШЕНИЕ**

### **Шаг 1: Закройте Android Studio**
```bash
# Закройте Android Studio полностью
```

### **Шаг 2: Удалите папку .idea**
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android
rm -rf .idea
```

### **Шаг 3: Синхронизируйте Gradle**
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
./gradlew clean
./gradlew build
```

### **Шаг 4: Откройте проект заново**
```bash
open -a "Android Studio" /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android
```

### **Шаг 5: Дождитесь синхронизации**
- Android Studio автоматически создаст правильную конфигурацию
- Дождитесь завершения "Gradle sync"
- Дождитесь завершения "Indexing"

### **Шаг 6: Проверьте конфигурацию**
1. **Run → Edit Configurations**
2. Выберите "ALADDIN Debug" или создайте новую
3. В поле **Module** должно появиться: `ALADDIN.app`
4. Если не появилось, выберите из выпадающего списка

### **Шаг 7: Если модуль все еще не появляется**
1. **File → Project Structure**
2. В разделе **Modules** должен быть модуль `app`
3. Если нет, нажмите **+** и добавьте модуль `app`

### **Шаг 8: Запустите приложение**
1. Нажмите **Run** (▶️) или **Debug** (🐛)
2. Выберите устройство или эмулятор
3. Приложение должно запуститься

## 🚀 **АЛЬТЕРНАТИВНЫЙ СПОСОБ**

### **Если ничего не помогает:**

1. **Создайте новую конфигурацию:**
   - **Run → Edit Configurations**
   - Нажмите **+** → **Android App**
   - Название: "ALADDIN New"
   - Module: выберите `ALADDIN.app`
   - Deploy: `Default APK`

2. **Или используйте готовую конфигурацию:**
   - В списке конфигураций выберите "ALADDIN Debug Fixed"
   - Эта конфигурация уже исправлена

## 📱 **ПРОВЕРКА РЕЗУЛЬТАТА**

После исправления:
- ✅ В поле **Module** должно быть: `ALADDIN.app`
- ✅ В поле **Deploy** должно быть: `Default APK`
- ✅ Ошибка "Module not specified" должна исчезнуть
- ✅ Кнопка **Run** должна стать активной

## 🎯 **ЕСЛИ ВСЕ ЕЩЕ НЕ РАБОТАЕТ**

1. **Перезагрузите компьютер**
2. **Обновите Android Studio**
3. **Проверьте, что Android SDK установлен**
4. **Убедитесь, что Java 17 доступна**

---
*Инструкция создана: 13 октября 2024*  
*Статус: Готово к исправлению* ✅

