# 🔧 ДОБАВЛЯЕМ МОДУЛЬ ВРУЧНУЮ В ANDROID STUDIO

## ❌ **ПРОБЛЕМА**
В окне "Edit Configuration" модуль не появляется в списке.

## ✅ **РЕШЕНИЕ: ДОБАВЛЯЕМ МОДУЛЬ ЧЕРЕЗ PROJECT STRUCTURE**

### **Шаг 1: Откройте Project Structure**
1. **В верхнем меню Android Studio нажмите "File"**
2. **Выберите "Project Structure..."**

### **Шаг 2: Добавьте модуль**
1. **В левой панели выберите "Modules"**
2. **Нажмите кнопку "+" (плюс)**
3. **Выберите "Import Module"**

### **Шаг 3: Выберите папку модуля**
1. **Перейдите в папку:** `/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android/app`
2. **Выберите папку `app`**
3. **Нажмите "OK"**

### **Шаг 4: Настройте модуль**
1. **В поле "Module name" должно быть:** `app`
2. **В поле "Module file location" должно быть:** `/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android/app`
3. **Нажмите "OK"**

### **Шаг 5: Проверьте результат**
1. **В списке модулей должен появиться модуль `app`**
2. **Нажмите "Apply" и "OK"**

### **Шаг 6: Вернитесь в Edit Configuration**
1. **Run → Edit Configurations...**
2. **В поле Module должен появиться:** `app`
3. **Выберите `app`**
4. **В поле Deploy выберите:** `Default APK`
5. **Нажмите Apply и OK**

## 🚀 **АЛЬТЕРНАТИВНЫЙ СПОСОБ**

### **Если модуль все еще не появляется:**

1. **Закройте Android Studio**
2. **Удалите папку .idea:**
   ```bash
   rm -rf /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android/.idea
   ```
3. **Откройте проект заново:**
   ```bash
   open -a "Android Studio" /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android
   ```
4. **Дождитесь завершения "Gradle sync"**
5. **Попробуйте снова Run → Edit Configurations...**

## 📱 **ПРОВЕРКА РЕЗУЛЬТАТА**

После добавления модуля:
- ✅ В поле **Module** должно быть: `app`
- ✅ В поле **Deploy** должно быть: `Default APK`
- ✅ Ошибка "Module not specified" должна исчезнуть
- ✅ Кнопка **Run** должна стать активной

---
*Инструкция создана: 13 октября 2024*  
*Статус: Готово к исправлению* ✅
