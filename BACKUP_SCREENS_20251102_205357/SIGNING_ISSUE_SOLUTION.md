# ⚠️ ОШИБКА SIGNING - РЕШЕНИЕ

## 🔍 **ПРОБЛЕМА:**

`DEVELOPMENT_TEAM = ""` — пустая строка в project.pbxproj

---

## ✅ **РЕШЕНИЕ (2 СПОСОБА):**

### **СПОСОБ 1: Через Xcode (РЕКОМЕНДУЕТСЯ)**
1. Откройте Xcode
2. Проект ALADDIN
3. Target "ALADDIN"
4. Вкладка "Signing & Capabilities"
5. В разделе "Team":
   - Если Team выбран — нажмите на него и выберите другой
   - Если Team НЕ выбран — выберите Team из списка
6. Сохраните (⌘+S)
7. Попробуйте собрать снова

### **СПОСОБ 2: Через терминал**
```bash
# Сбросить подпись
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
xcodebuild clean
rm -rf ~/Library/Developer/Xcode/DerivedData/ALADDIN-*
```

---

## 🔍 **ПОЧЕМУ:**

"Automatically manage signing" включён, но Team не выбран в выпадающем списке.

---

## 💡 **ПОДСКАЗКА:**

Если в списке Team ничего нет:
- Проверьте авторизацию в Xcode → Preferences → Accounts
- Добавьте Apple ID, если его нет

