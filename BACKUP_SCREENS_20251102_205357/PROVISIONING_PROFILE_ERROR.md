# ⚠️ ОШИБКА PROVISIONING PROFILE

## 🔍 **ПРОБЛЕМА:**

```
Failed to create provisioning profile.
There are no devices registered in your account on the developer website.
```

---

## ✅ **РЕШЕНИЕ:**

### **СПОСОБ 1: Использовать СИМУЛЯТОР (РЕКОМЕНДУЕТСЯ)**

1. В Xcode нажмите на схему устройства (рядом с кнопкой Run)
2. Выберите **"iOS Simulator"** вместо физического устройства
3. Выберите симулятор (например, "iPhone 15")
4. Нажмите Run (▶️)

**Симулятор НЕ требует provisioning profile!**

---

### **СПОСОБ 2: Зарегистрировать устройство**

1. Подключите iPhone/iPad к Mac
2. В Xcode выберите ваше устройство
3. Xcode автоматически зарегистрирует устройство
4. Или зарегистрируйте вручную на developer.apple.com

---

## 💡 **БЫСТРОЕ РЕШЕНИЕ:**

**Просто выберите симулятор вместо устройства!**  
Симулятор работает без Team и provisioning profile.

