# TODO: ЗАДАЧИ ПО РЕКОМЕНДАЦИЯМ APPLE

**Дата создания:** 11 декабря 2025  
**Версия:** 1.0.0 (Build 7)  
**3-й возврат от Apple**

---

## 📋 5 КРИТИЧЕСКИХ ЗАДАЧ

### ✅ ЗАДАЧА 1: ИСПРАВИТЬ КРАШ ПРИ SUBSCRIBE

**Проблема:** Приложение крашится при нажатии "Subscribe"  
**Причина:** Обращение к nil или не загруженные продукты из StoreKit

**Статус:** ✅ **ВЫПОЛНЕНО**

**Что сделано:**
- ✅ Добавлена защита от nil в `StoreManager.swift`
- ✅ Добавлена проверка загрузки продуктов в `TariffsViewModel.swift`
- ✅ Добавлены новые ошибки: `.storeNotReady`, `.purchaseInProgress`

**Файлы изменены:**
- ✅ `Core/Store/StoreManager.swift` - добавлены guard проверки
- ✅ `ViewModels/TariffsViewModel.swift` - добавлены проверки перед покупкой

**Что еще нужно:**
- ⏳ Создать и одобрить 4 продукта подписки в App Store Connect
- ⏳ Добавить скриншоты для App Review для каждого продукта

---

### ✅ ЗАДАЧА 2: ДОБАВИТЬ ССЫЛКИ НА PRIVACY POLICY И TERMS OF USE

**Проблема:** Apple требует ссылки на Privacy Policy и Terms of Use перед кнопкой Subscribe

**Статус:** ✅ **ВЫПОЛНЕНО**

**Что сделано:**
- ✅ Добавлены ссылки на Privacy Policy и Terms of Use в `TariffsScreen.swift`
- ✅ Текст: "Нажимая 'Subscribe', вы соглашаетесь с [Terms of Use] и [Privacy Policy]"
- ✅ Ссылки открывают экраны `PrivacyPolicyScreen` и `TermsOfServiceScreen`
- ✅ Локализация на русском и английском

**Файлы изменены:**
- ✅ `Screens/10_TariffsScreen.swift` - добавлены ссылки и sheet модальные окна
- ✅ `Core/Localization/LocalizationManager.swift` - добавлены ключи:
  - `tariffs_subscribe_agreement_text`
  - `tariffs_subscribe_agreement_and`
  - `terms_of_service`
  - `privacy_policy`

**Что еще нужно:**
- ⏳ Настроить роутинг на сервере: `/privacy` → `privacy.html`, `/terms` → `terms.html`
- ⏳ Добавить URL в App Store Connect:
  - Privacy Policy URL: `https://aladdin-ai.ru/privacy`
  - Terms of Use URL: `https://aladdin-ai.ru/terms`

---

### ⏳ ЗАДАЧА 3: НАСТРОИТЬ РОУТИНГ НА СЕРВЕРЕ

**Проблема:** `/privacy` и `/terms` редиректят на главную страницу  
**Требование Apple:** Должны работать прямые ссылки

**Статус:** ⏳ **В ПРОЦЕССЕ**

**Что нужно сделать:**
1. Подключиться к серверу: `ssh root@149.154.65.180`
2. Найти конфиг nginx: `/etc/nginx/sites-available/aladdin-ai.ru`
3. Добавить location блоки:
   ```nginx
   location = /privacy {
       return 301 /privacy.html;
   }
   location = /terms {
       return 301 /terms.html;
   }
   ```
4. Проверить: `nginx -t`
5. Перезагрузить: `systemctl reload nginx`
6. Проверить работу: `curl -I https://aladdin-ai.ru/privacy`

**Инструкция:** `docs/AppStore/ИНСТРУКЦИЯ_НАСТРОЙКА_РОУТИНГА_СЕРВЕР_11_12_2025.md`

**Файлы на сервере:**
- `/var/www/aladdin-ai.ru/privacy.html` - существует ✅
- `/var/www/aladdin-ai.ru/terms.html` - существует ✅

---

### ✅ ЗАДАЧА 4: УБРАТЬ ВНЕШНИЕ ССЫЛКИ НА ОПЛАТУ

**Проблема:** Apple запрещает ссылки на внешние платежные системы  
**Требование:** Только In-App Purchase или коды активации

**Статус:** ✅ **ВЫПОЛНЕНО**

**Что сделано:**
- ✅ Убраны упоминания `aladdin-ai.ru` из текстов локализации
- ✅ Изменены тексты:
  - Было: "Оплата на сайте aladdin-ai.ru"
  - Стало: "Используйте код активации для подписки"

**Файлы изменены:**
- ✅ `Core/Localization/LocalizationManager.swift` - обновлены ключи:
  - `tariffs_website_info`
  - `tariffs_activation_code_description`

**Что еще нужно:**
- ⏳ Убрать из App Store Connect Description: "Для России: оплата на сайте https://aladdin-ai.ru"
- ⏳ Проверить что нет кнопок "Перейти на сайт" в приложении

---

### ⏳ ЗАДАЧА 5: РЕШИТЬ ПРОБЛЕМУ С VPN (Guideline 5.4)

**Проблема:** Apple отклоняет VPN приложения от индивидуальных аккаунтов  
**Требование:** VPN приложения только от компаний

**Статус:** ⏳ **ТРЕБУЕТ РЕШЕНИЯ**

**Варианты решения (см. ниже):**
1. Удалить NetworkExtension полностью
2. URLSession с прокси (псевдо-VPN)
3. Сделать VPN опциональным

**Файлы которые нужно будет изменить:**
- ⏳ `ALADDIN/ALADDINPacketTunnel/` - удалить target
- ⏳ `Core/VPN/VPNManager.swift` - переделать или удалить
- ⏳ `Screens/03_VPNScreen.swift` - переделать UI
- ⏳ `Core/Localization/LocalizationManager.swift` - убрать VPN тексты
- ⏳ `Screens/18_PrivacyPolicyScreen.swift` - убрать VPN разделы
- ⏳ `Screens/19_TermsOfServiceScreen.swift` - убрать VPN раздел
- ⏳ Entitlements - убрать `com.apple.developer.networking.vpn.api`

**VPN тексты сохранены:** `docs/AppStore/VPN_ТЕКСТЫ_ДЛЯ_КОПИРОВАНИЯ_11_12_2025.md`

---

## 📊 СВОДКА ПО ФАЙЛАМ

### ✅ ФАЙЛЫ УЖЕ ИЗМЕНЕНЫ:

1. **`Core/Store/StoreManager.swift`**
   - Добавлены guard проверки для предотвращения краша
   - Добавлены новые ошибки: `.storeNotReady`, `.purchaseInProgress`
   - Проверка `product.id.isEmpty`, `isLoading`, `products.contains`

2. **`ViewModels/TariffsViewModel.swift`**
   - Добавлены проверки перед покупкой
   - Проверка загрузки продуктов
   - Автоматическая перезагрузка продуктов если пусто

3. **`Screens/10_TariffsScreen.swift`**
   - Добавлены ссылки на Privacy Policy и Terms of Use
   - Добавлены sheet модальные окна
   - Текст согласия перед кнопкой Subscribe

4. **`Core/Localization/LocalizationManager.swift`**
   - Добавлены ключи для согласия: `tariffs_subscribe_agreement_text`, `tariffs_subscribe_agreement_and`
   - Обновлены тексты: убраны ссылки на `aladdin-ai.ru`
   - Добавлены ключи: `terms_of_service`, `privacy_policy`

### ⏳ ФАЙЛЫ КОТОРЫЕ НУЖНО ИЗМЕНИТЬ:

5. **Сервер nginx конфиг** (на сервере)
   - `/etc/nginx/sites-available/aladdin-ai.ru` - добавить роутинг

6. **App Store Connect** (веб-интерфейс)
   - Description - убрать упоминание сайта
   - Privacy Policy URL - добавить `https://aladdin-ai.ru/privacy`
   - Terms of Use URL - добавить `https://aladdin-ai.ru/terms`
   - In-App Purchases - создать 4 продукта, добавить скриншоты

7. **VPN файлы** (если выберем вариант удаления)
   - `ALADDIN/ALADDINPacketTunnel/` - удалить
   - `Core/VPN/VPNManager.swift` - переделать
   - `Screens/03_VPNScreen.swift` - переделать
   - `Screens/18_PrivacyPolicyScreen.swift` - убрать VPN разделы
   - `Screens/19_TermsOfServiceScreen.swift` - убрать VPN раздел
   - `Core/Localization/LocalizationManager.swift` - убрать VPN ключи
   - Entitlements - убрать VPN capability

---

## 🎯 ПРОГРЕСС

- ✅ **Задача 1:** Исправить краш - **ВЫПОЛНЕНО** (код готов, нужны продукты в App Store Connect)
- ✅ **Задача 2:** Добавить ссылки на Privacy/Terms - **ВЫПОЛНЕНО** (код готов, нужен роутинг на сервере)
- ⏳ **Задача 3:** Настроить роутинг - **В ПРОЦЕССЕ** (инструкция готова)
- ✅ **Задача 4:** Убрать внешние ссылки - **ВЫПОЛНЕНО** (код готов, нужно убрать из App Store Connect)
- ⏳ **Задача 5:** Решить проблему VPN - **ТРЕБУЕТ РЕШЕНИЯ** (см. варианты ниже)

**Общий прогресс:** 3/5 задач выполнено в коде, 2 требуют действий на сервере/App Store Connect

---

**Дата обновления:** 11 декабря 2025
