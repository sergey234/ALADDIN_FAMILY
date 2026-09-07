# ALADDIN — канон ID компании (путь B)

**Дата:** 2026-09-07  
**ASC app name:** ALADDIN AI  
**Team:** `B3WGHSWL79` (`aladdin.ai@tuta.io`)

Личный TestFlight (`family.aladdin.ios` / Team `6CJVBBUGSN`) **не трогаем** — отдельное приложение.

## Identifiers

| Роль | ID |
|------|-----|
| App | `ai.aladdin` |
| Content Blocker | `ai.aladdin.ContentBlocker` |
| Antifake Share | `ai.aladdin.AntifakeShare` |
| Call Directory | `ai.aladdin.CallDirectory` |
| App Group | `group.ai.aladdin` |
| Unit tests | `ai.aladdin.unitTests` |
| UI tests | `ai.aladdin.uitests` |

## IAP Product IDs (создать в ASC компании)

| Product ID |
|------------|
| `ai.aladdin.subscription.basic.v2` |
| `ai.aladdin.subscription.individual.v2` |
| `ai.aladdin.subscription.family` |
| `ai.aladdin.subscription.premium` |

Paid in code: individual, family, premium (`StoreManager.ProductID.paidSubscriptions`).

## Xcode

- `DEVELOPMENT_TEAM` = `B3WGHSWL79`
- Entitlements App Group = `group.ai.aladdin`
- Associated Domains (app): `applinks:aladdin-ai.ru` (как было)

## Проверка

```bash
./scripts/ios_verify_signing_targets.sh
```

Ожидание: один Team `B3WGHSWL79`, bundles как в таблице выше, group `group.ai.aladdin`.
