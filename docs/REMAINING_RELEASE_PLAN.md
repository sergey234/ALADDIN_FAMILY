# 📝 ФИНАЛЬНЫЙ ПЛАН: ЧТО ЕЩЁ СДЕЛАТЬ

Сводный список составлен на основе `FINAL_TODO_STATUS_WITH_CHECKMARKS.md`, `VPN_CURRENT_IMPLEMENTATION_ANALYSIS.md` и `PRODUCTION_READINESS_ANALYSIS.md`.

---

## 1. Релизная сборка и MITM-проверка
- Собрать реальный Release-билд (Xcode → Product → Archive).
- Прогнать трафик через Charles или Burp в режиме MITM.
- Зафиксировать логи, подтверждающие работу SSL pinning (задача S4-08).

---

## 2. VPN и entitlements
- Добавить `Network Extension` target, `PacketTunnelProvider` и требуемые entitlements (`com.apple.networkextension.packet-tunnel`).
- Настроить подписи и App Groups, убедиться, что Xcode видит профили.
- Пересобрать приложение и проверить подключение VPN.

---

## 3. TestFlight и загрузка билда
- После code signing выполнить Archive → Distribute App → Upload в App Store Connect.
- Дождаться обработки и запустить внутренний цикл TestFlight.
- При необходимости собрать логи и исправить замечания тестировщиков.

---

## 4. App Store Connect
- Создать карточку приложения, заполнить все поля (описания RU/EN, ключевые слова, скриншоты, иконка).
- Указать публичные URL: `https://aladdin-ai.ru/privacy_full.html` и `https://aladdin-ai.ru/terms_full.html`.
- Добавить IAP из `IAP_PRODUCT_IDS_COMPLETE.md`, заполнить App Privacy и Review Notes.
- Нажать Submit for Review и подготовиться к ответам по Guideline 3.1.1.

---

## 5. Дополнительные технические задачи
- Настроить Alertmanager и централизованное логирование (S3-11, S3-12).
- Настроить восстановление из backup (S3-16).
- Провести нагрузочные тесты (S4-05…S4-07) и тесты безопасности (S4-08, S4-09).
- Завершить оптимизацию производительности (S4-10).

---

**Как только все пункты закрыты, можно сразу отправлять билд на ревью.**

