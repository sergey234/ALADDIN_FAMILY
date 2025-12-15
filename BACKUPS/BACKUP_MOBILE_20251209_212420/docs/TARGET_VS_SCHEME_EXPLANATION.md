# 🎯 Разница между Таргетами и Схемами в Xcode

## 📋 Что вы видите в Target Membership

В разделе **"Target Membership"** (File Inspector) должны отображаться только **ТАРГЕТЫ**, а не схемы.

### ✅ Правильные таргеты в вашем проекте:

1. **ALADDIN** ✅ - основной таргет приложения (ПРАВИЛЬНЫЙ!)
2. **ALADDINPacketTunnel** ❌ - таргет для VPN расширения (НЕ НУЖЕН для TariffsViewModel)
3. **ALADDINUnitTests** - для unit тестов (обычно не нужен)
4. **ALADDINUITests** - для UI тестов (обычно не нужен)

## 🔍 Что такое "ALADDIN 1"?

**"ALADDIN 1"** - это **СХЕМА** (Scheme), а не таргет!

### Разница:

- **Таргет (Target)** = что компилируется (ALADDIN, ALADDINPacketTunnel)
- **Схема (Scheme)** = как запускается (ALADDIN, ALADDIN 1, ALADDINPacketTunnel)

### Где видны схемы:

Схемы видны в:
- Верхняя панель Xcode (рядом с кнопкой Play)
- Product → Scheme → Manage Schemes...

### Где видны таргеты:

Таргеты видны в:
- File Inspector → Target Membership (правая панель)
- Настройки проекта → Targets (центральная панель)

## ✅ Правильная настройка для TariffsViewModel.swift

В разделе **"Target Membership"** для файла `TariffsViewModel.swift`:

### Должно быть:
- ✅ **ALADDIN** - включено (галочка стоит)
- ❌ **ALADDINPacketTunnel** - выключено (галочка НЕ стоит)
- ❌ Все остальные - выключено

### Если видите "ALADDIN 1":

Если в Target Membership видите "ALADDIN 1", это может быть:
1. Ошибка отображения в Xcode
2. Дубликат таргета (редко)
3. Старая схема, которая отображается как таргет

**Решение:** Используйте только **ALADDIN** (без "1")

## 🎯 Итоговая инструкция

1. Откройте `TariffsViewModel.swift` в Xcode
2. Откройте File Inspector (⌘⌥1)
3. Найдите раздел "Target Membership"
4. Убедитесь, что:
   - ✅ **ALADDIN** - включено
   - ❌ **ALADDINPacketTunnel** - выключено
   - ❌ Все остальное - выключено

5. Если видите "ALADDIN 1":
   - Выключите его (снимите галочку)
   - Оставьте только **ALADDIN** (без "1")

## 🔧 Если "ALADDIN 1" не исчезает

Если "ALADDIN 1" продолжает появляться:
1. Закройте Xcode
2. Откройте проект заново
3. Очистите проект: Product → Clean Build Folder (⇧⌘K)
4. Проверьте Target Membership снова

