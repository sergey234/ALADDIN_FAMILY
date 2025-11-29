# 🎯 Какой таргет использовать для TariffsViewModel.swift

## Таргеты в проекте

В вашем проекте есть следующие таргеты:

1. **ALADDIN** - основной таргет приложения ✅ **ПРАВИЛЬНЫЙ**
2. **ALADDINPacketTunnel** - таргет для VPN расширения (Network Extension) ❌ **НЕ НУЖЕН**
3. **ALADDINUnitTests** - для unit тестов
4. **ALADDINUITests** - для UI тестов

## Схемы (Schemes)

Схемы - это конфигурации для запуска и сборки:
- **ALADDIN** - основная схема для запуска приложения ✅
- **ALADDIN 1** - возможно, дубликат или старая схема
- **ALADDINPacketTunnel** - схема для VPN расширения

## ✅ Правильная настройка для TariffsViewModel.swift

Для файла `ViewModels/TariffsViewModel.swift` нужно:

1. **Включить** ✅ галочку на **ALADDIN** (основной таргет приложения)
2. **Выключить** ❌ галочку на **ALADDINPacketTunnel** (VPN расширение)
3. **Выключить** ❌ галочки на тестовые таргеты (если они есть)

## Почему?

- `TariffsViewModel.swift` - это ViewModel для экрана тарифов
- Он использует `StoreManager`, `AppConfig`, `NotificationManager` - все это часть основного приложения
- VPN расширение (`ALADDINPacketTunnel`) - это отдельный модуль, который не должен содержать UI логику
- В VPN расширении нет доступа к StoreKit, UI компонентам и другим модулям приложения

## Что делать с "ALADDIN 1"?

Если видите "ALADDIN 1" в списке схем:
- Это может быть дубликат схемы
- Проверьте в Xcode: Product → Scheme → Manage Schemes...
- Если "ALADDIN 1" - это дубликат, можно удалить его
- Для Target Membership используйте только **ALADDIN**

## Итоговая настройка

В разделе "Target Membership" для `TariffsViewModel.swift`:
- ✅ **ALADDIN** - включено
- ❌ **ALADDINPacketTunnel** - выключено
- ❌ Все остальные - выключено

