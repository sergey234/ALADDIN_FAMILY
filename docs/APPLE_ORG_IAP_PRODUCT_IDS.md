# ALADDIN — IAP / Subscription Product IDs (канон для ASC компании)

**SSOT в коде:** `Core/Store/StoreManager.swift` → `enum ProductID`

| Product ID | Case | Назначение |
|------------|------|------------|
| `ai.aladdin.subscription.basic.v2` | `.basic` | Базовый (не в `paidSubscriptions`) |
| `ai.aladdin.subscription.individual.v2` | `.individual` | Индивидуальный |
| `ai.aladdin.subscription.family` | `.family` | Семейный |
| `ai.aladdin.subscription.premium` | `.premium` | Премиум |

Загрузка StoreKit: только `ProductID.paidSubscriptions` = individual, family, premium.

## Что создать в App Store Connect (компания)

1. Agreements → **Paid Apps** Active.
2. Monetization → Subscriptions → Subscription Group (например `ALADDIN Premium`).
3. Создать auto-renewable products с **точно этими** Product IDs (не менять без правки Swift).
4. Локализации, цены, trial — по продукту.
5. Sandbox Apple ID → Users and Access → Sandbox.
6. Server Notifications V2 → URL MAIN backend (после Transfer обновить shared secret).

## Backend

Клиентские endpoints в `AppConfig.Endpoint`: `/api/subscription/*`.  
После миграции проверить, что сервер валидирует чеки под **новым** app / shared secret компании.

## Локальный тест без ASC

Файл: `ALADDIN/StoreKit/ALADDINSubscriptions.storekit`  
Xcode → Scheme → Run → Options → StoreKit Configuration → выбрать этот файл.
