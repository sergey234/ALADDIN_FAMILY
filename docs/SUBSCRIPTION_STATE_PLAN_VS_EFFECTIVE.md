# Подписка: план (plan) vs эффективный доступ (effective)

Краткий гайд для разработки и разбора логов.

## Поля и хранилища

| Смысл | Где живёт | Примечание |
|--------|-----------|------------|
| Снимок уровня в JWT-обёртке | `JWTToken.subscriptionLevel` в Keychain (`jwt_token`) | Может отличаться от подписки, если обновляли не атомарно. |
| План / тариф в UI и лимитах | `SubscriptionStatus.level` в Keychain (`subscription_status`) | Часто совпадает с ответом API после синка. |
| Отдельный кэш триала | `trialStatus` (`TrialInfo`) в Keychain (`trial_info`) | Используется для приоритета «на триале». |
| Что видит логика доступа | `getCurrentLevel()` | Если `trialStatus?.isActive` → `.trial`, иначе `currentSubscription?.level ?? .free`. |

## Источник правды

- **Авторизация и платные действия** — сервер.
- После **успешного** `syncWithServer` / `updateFromServerStatus` локальное состояние **перезаписывается** ответом сервера.
- Локальная проверка истечения триала (`checkTrialExpiration`) и вызовы при возврате в active — **UX и кэш**; при следующем синке сервер может скорректировать.

## Логи

После загрузки Keychain в DEBUG печатается строка `SUBSCRIPTION_KEYCHAIN_SNAPSHOT`: `token_level`, `plan_level`, `trialStatus` (active + end), `getCurrentLevel`.

## Аналитика

В `trackEvent` в `metadata` добавляются:

- `plan_level` — `currentSubscription?.level.rawValue`
- `effective_level` — `getCurrentLevel().rawValue`

Поле `subscriptionLevel` в теле события сохраняется для обратной совместимости (как раньше — план из подписки, если не передан явно).

## Регистрация устройства

После успешного `registerDeviceAnonymously`, если в ответе есть `trialInfo`, вызывается `updateTrialStatus` — `trial_status` в Keychain совпадает с сервером, как и для `register-device-trial`.
