# Gate 0 — ALADDIN Apple Org Migration (заполнено владельцем)

**Дата:** 2026-09-07  
**Путь (актуально 2026-09-07 вечер):** **B** — личный TF оставить (`family.aladdin.ios`); компания — новое app **ALADDIN AI** / `ai.aladdin`.

## Из репозитория / после правки Xcode (компания)

| Поле | Значение |
|------|----------|
| Bundle ID (app, компания) | `ai.aladdin` |
| ASC name | ALADDIN AI |
| Personal Team (личный TF, не трогаем) | `6CJVBBUGSN` / `family.aladdin.ios` |
| **Team сейчас в pbxproj** | `B3WGHSWL79` |
| Content Blocker | `ai.aladdin.ContentBlocker` |
| Antifake Share | `ai.aladdin.AntifakeShare` |
| Call Directory | `ai.aladdin.CallDirectory` |
| App Group | `group.ai.aladdin` |
| Канон ID | `docs/APPLE_ORG_COMPANY_IDS_CANON.md` |
| Associated Domains | `applinks:aladdin-ai.ru` |

## Заполнено владельцем

| Поле | Значение |
|------|----------|
| Статус на личном ASC | **Только TestFlight** |
| Company Team ID | `B3WGHSWL79` |
| Account Holder / Admin | `aladdin.ai@tuta.io` (Владелец + Администратор) |
| Developer ID (Apple) | `282a8891-86a4-4288-92c8-923489a9f9f7` |
| Convert Individual→Org | **Нет** (личный и компания — отдельные) |
| Один разработчик | Да (личный + компания) |
| Paid Apps | Membership оплачен / кабинет есть — **проверить** Agreements → Paid Apps = Active |
| Цель | Выход в **App Store** под компанией |

## Решение по пути

- [x] **C.** Отдельная Org + только TestFlight → минимальный релиз на личном → **App Transfer** → дальше Store от компании

## Следующие шаги (путь C)

1. App Store Connect **компании**: Agreements → **Paid Apps** = Active (+ Tax/Banking).
2. Xcode: Accounts → войти `aladdin.ai@tuta.io` → Team `B3WGHSWL79` → для всех targets подпись Company → Archive (пока можно собирать под компанией для TF компании **только если** App ID уже на компании; иначе сначала релиз/Transfer — см. ниже).
3. На **личном** аккаунте: один минимальный релиз ALADDIN в App Store (чтобы Transfer стал доступен).
4. Transfer App: личный Account Holder → Team `B3WGHSWL79` + email `aladdin.ai@tuta.io` → Accept.
5. После Accept: новые profiles на `B3WGHSWL79`, TestFlight компании, IAP Product IDs из `APPLE_ORG_IAP_PRODUCT_IDS.md`, релиз в Store.

```bash
./scripts/ios_verify_signing_targets.sh
# Team уже: B3WGHSWL79
```
