# App Store Review Notes Checklist

Используйте этот шаблон при каждой загрузке сборки в App Store Connect.

## 1. Флоу оплаты и активации

1. **TariffsScreen** → нажать кнопку `Перейти на сайт` (открывается Safari).
2. На сайте https://aladdin-ai.ru выбрать тариф и оплатить.
3. После оплаты пользователь получает код вида `ALDN-XXXX-XXXX-XXXX`.
4. Вернуться в приложение → открыть `ActivationCodeScreen`.
5. Ввести код → нажать `Активировать` (подключаются функции тарифа).

🔐 **Важно:** в приложении мы не продаём цифровой контент, а только активируем подписку, купленную на сайте. Это соответствует Guideline 3.1.1 (восстановление доступа к покупкам вне приложения). Мы участвуем в App Store Small Business Program, поэтому комиссия 15% (при выручке < $1M).

## 2. Текст для поля “Review Notes”

```
Our iOS app only activates subscriptions purchased on https://aladdin-ai.ru (outside the app).
Flow: Main → Tariffs → “Перейти на сайт” (opens Safari) → user pays → receives activation code (ALDN-XXXX-XXXX-XXXX) → ActivationCodeScreen → enters code → access unlocked.
No digital goods are sold inside the app. This follows App Store Guideline 3.1.1 (restore purchases acquired elsewhere). Small Business Program participant.
Test code: ALDN-TEST-1234 (unlocks Premium for review).
```

При необходимости можно добавить шаги навигации или дополнительные тестовые аккаунты.

## 3. Что приложить к ревью

- Скриншоты RU/EN: Tariffs, Website CTA, ActivationCodeScreen, Settings → Terms → Payments.
- Видео (опционально) с переходом на сайт и вводом тестового кода.
- Убедиться, что на сайте и в приложении одинаковый текст: “Оплата происходит на сайте aladdin-ai.ru. После оплаты вы получите код и введёте его в приложении”.

## 4. Проверка локализаций перед релизом

- `tariffs_website_button`, `tariffs_website_info`, `activation_code_*`, `settings_improve_protection`.
- `terms_section_payments_*` (в Настройках → Условия использования).
- Сайт aladdin-ai.ru (RU/EN) — тексты про оплату вне App Store.

## 5. Ссылки на документы

- Guideline 3.1.1: https://developer.apple.com/appstore/review/guidelines/#payments
- Приложение 2 к Apple Developer Program License Agreement (версия 125, 08.10.2025)
- Приложение 3 (Custom App Distribution) при необходимости B2B распространения

Обновляйте этот документ при любом изменении флоу или текстов, чтобы ревью команда всегда получала актуальную информацию.

