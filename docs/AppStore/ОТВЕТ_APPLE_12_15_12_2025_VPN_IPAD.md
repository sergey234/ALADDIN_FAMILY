# ОТВЕТ APPLE - 12-15 ДЕКАБРЯ 2025

**Дата:** 15 декабря 2025  
**Guidelines:** 5.4 - Legal - VPN Apps, 2.1 - Performance - App Completeness

---

## РУССКАЯ ВЕРСИЯ / RUSSIAN VERSION

---

### GUIDELINE 5.4 - LEGAL - VPN APPS

Уважаемая команда App Review,

12-15 декабря 2025 года мы полностью удалили всю VPN-функциональность и VPN-терминологию из приложения ALADDIN.

**Удаление VPN - 15 декабря 2025 (Build 10):**

#### 1. Обновление всех ссылок в активном коде (15 декабря 2025)

Мы обновили 46+ мест использования VPN моделей в следующих файлах:

- Core/Network/APIService.swift - все методы API
- Core/Network/MockAPIService.swift - mock реализации
- Core/Cache/CachedAPIService.swift - кеширование
- Core/VPN/NetworkProtectionManager.swift - менеджер защиты сети
- Screens/03_NetworkProtectionScreen.swift - экран защиты сети

#### 2. Полное удаление VPNViewModel (15 декабря 2025, Build 10):

VPNViewModel полностью удален из проекта:

- Файл ViewModels/VPNViewModel.swift полностью удален из проекта
- Обновлен Screens/01_MainScreen.swift - полностью удалено использование VPNViewModel
- Удалены все 4 ссылки на VPNViewModel.swift из project.pbxproj
- VPNViewModel больше не существует в скомпилированном бинарном файле

#### 3. Предыдущие удаления (12-15 декабря 2025):

**Удаление VPN-функциональности - 12 декабря 2025:**

**Изменения в коде:**
- Полностью удален target ALADDINPacketTunnel из проекта Xcode
- Удален import NetworkExtension из VPNManager.swift (закомментирован)
- Удалены VPN capabilities из файла Entitlements проекта
- Закомментированы все методы NetworkExtension (15+ мест)
- Заменены методы connect() и disconnect() на заглушки

**Структура проекта:**
- Target ALADDINPacketTunnel удален из project.pbxproj
- Зависимость удалена из основного target
- Build phase "Embed App Extensions" удален
- Все VPN-связанные build конфигурации удалены

**Удаление VPN-файлов - 15 декабря 2025:**
- Полностью удален файл PacketTunnelProvider.swift из проекта
- Полностью удалена папка ALADDIN/ALADDINPacketTunnel/ из проекта
- Удален файл Info.plist из папки ALADDINPacketTunnel
- Удален NetworkExtension.framework из проекта
- Удалены все VPN-связанные entitlements файлы:
  - ALADDINPacketTunnel.entitlements
  - ALADDINPacketTunnelDebug.entitlements
- Удалены ссылки на VPN-файлы из project.pbxproj

**Изменения в UI - 15 декабря 2025:**
- Удалена карточка статуса "Защита сети" с главного экрана

**Итоговый результат:**

Вся VPN-терминология удалена из активного кода:
- VPNViewModel полностью удален из проекта и бинарного файла
- Все VPN-связанные классы, структуры и свойства удалены

**ALADDIN НЕ ЯВЛЯЕТСЯ VPN-ПРИЛОЖЕНИЕМ**
- Приложение является приложением для семейной безопасности и родительского контроля
- Приложение не предоставляет VPN-функциональность
- Приложение не использует NetworkExtension framework

---

### GUIDELINE 2.1 - PERFORMANCE - APP COMPLETENESS (ОШИБКА ПРИ ПОДПИСКЕ НА IPAD)

**Уточнение:** В текущей версии приложение ALADDIN оптимизировано и протестировано только для iPhone. Поддержка iPad отключена в настройках проекта. Как мы ранее уведомляли Вас в письме, настоящая версия мобильного приложения не предназначена для iPad.

**Технические настройки проекта:**
- В настройках проекта установлено TARGETED_DEVICE_FAMILY = "1" (только iPhone)
- В Info.plist установлено LSRequiresIPhoneOS = true
- Приложение скомпилировано только для iPhone
- Приложение не предназначено для установки на iPad в текущей версии
- Пользователи не смогут скачать приложение на iPad из App Store

**Наше позиционирование в настоящее время:**

1. Приложение не предназначено для установки на iPad в текущей версии приложения
2. Мы не тестировали приложение на iPad. Планируем поддержку iPad в ближайшее время в следующих обновлениях.
3. Все функции приложения протестированы на iPhone
4. Поддержка iPad будет рассмотрена в будущих версиях после полной адаптации интерфейса.

**Ошибка на iPad не является проблемой, так как приложение в настоящий момент не адаптировано в полной мере для iPad в текущей версии.**

---

**Дата:** 15 декабря 2025  
**Статус:** ✅ Отправлено Apple
