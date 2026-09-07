# ALADDIN — перенос на корпоративный Apple Developer (runbook)

**Дата:** 2026-09-07  
**Канон:** сохранить bundle `family.aladdin.ios`, Seller = компания (Transfer или Convert).  
**Не делать:** новый bundle ID «с нуля».

Связанные файлы:

| Файл | Зачем |
|------|--------|
| [APPLE_ORG_MIGRATION_GATE0_WORKSHEET.md](APPLE_ORG_MIGRATION_GATE0_WORKSHEET.md) | Gate 0 — заполнить Team ID / статус ASC |
| [APPLE_ORG_IAP_PRODUCT_IDS.md](APPLE_ORG_IAP_PRODUCT_IDS.md) | Product IDs для ASC |
| [APPLE_ORG_RELEASE_NOTES_RELOGIN.md](APPLE_ORG_RELEASE_NOTES_RELOGIN.md) | Текст What’s New после смены Team |
| [APPLE_ORG_MIGRATION_OWNER_CHECKLIST.md](APPLE_ORG_MIGRATION_OWNER_CHECKLIST.md) | Чеклист владельца по фазам |
| `../scripts/ios_set_development_team.sh` | Массовая смена `DEVELOPMENT_TEAM` |
| `../scripts/ios_verify_signing_targets.sh` | Проверка teams/bundles/entitlements |
| `../ALADDIN/StoreKit/ALADDINSubscriptions.storekit` | Локальный StoreKit Configuration |

---

## Исходное состояние репо

- Team в Xcode: `6CJVBBUGSN` (личный)
- Targets: ALADDIN, ALADDINContentBlocker, ALADDINAntifakeShare, ALADDINCallDirectory
- App Group: `group.com.aladdin.family`
- Associated Domains: `applinks:aladdin-ai.ru`

---

## Фаза 0 — Gate 0

1. Заполнить [APPLE_ORG_MIGRATION_GATE0_WORKSHEET.md](APPLE_ORG_MIGRATION_GATE0_WORKSHEET.md).
2. Выбрать путь A (Convert) / B (Transfer) / C (релиз → Transfer).

---

## Фаза 1 — Organization (ASC / developer.apple.com)

### 1.1 Компания

1. Membership Active.
2. ASC → Agreements → **Paid Apps** + Free Apps → Active.
3. Tax / Banking заполнены.
4. Users and Access: ваш Apple ID = Admin (или App Manager + Developer).
5. Записать Company Team ID в worksheet + `~/ALADDIN_VPN_SAFE/` (не в git с лишними PII).

### 1.2 Личный → Transfer (пути B/C)

1. Backup метаданных ASC (описание, скрины, privacy).
2. Нет сабмитов In Review / Pending Developer Release.
3. Если только TestFlight (путь C): минимальный релиз 1.0 на личном.
4. Account Holder личного: Transfer App → Team ID + email Account Holder компании.
5. Account Holder компании: Accept ≤ 60 дней.
6. Shared secret подписок (если уже были IAP) — сохранить offline до Accept, обновить после.

Официально: [App transfer criteria](https://developer.apple.com/help/app-store-connect/transfer-an-app/app-transfer-criteria).

### 1.3 После Accept / Convert

1. Приложение только в ASC компании.
2. Certificates, Identifiers & Profiles (Company Team):
   - Explicit App IDs всех 4 bundle
   - Capabilities: App Groups, Associated Domains, Push (если нужно), Call Directory, Content Blocker, Share
   - Новые Development + Distribution profiles (имена можно оставить похожими)
3. APNs Auth Key `.p8` под Company → обновить `APNS_*` на Mac/MAIN (не в git).

---

## Фаза 2 — Xcode

```bash
# после появления Company Team ID:
./scripts/ios_set_development_team.sh YOUR_COMPANY_TEAM_ID
./scripts/ios_verify_signing_targets.sh
```

В Xcode:

1. Settings → Accounts → Apple ID с доступом к Organization.
2. Каждый target → Signing: Team = Company.
3. Capabilities синхронизировать с порталом.
4. Clean → Run на устройстве → Archive → Validate → Upload в ASC **компании**.

После смены Team: возможен повторный логин (Keychain) — текст в `APPLE_ORG_RELEASE_NOTES_RELOGIN.md`.

---

## Фаза 3 — Подписки

1. Создать продукты с ID из `APPLE_ORG_IAP_PRODUCT_IDS.md`.
2. Sandbox tester.
3. Scheme → StoreKit Configuration → `ALADDINSubscriptions.storekit` (локально).
4. На устройстве — sandbox покупка.
5. Server Notifications V2 → MAIN; обновить shared secret.

---

## Фаза 4 — Closeout

1. What’s New с текстом re-login.
2. Обновить master-index в сейфе: Company Team ID (путь к `.p8`, без секретов в git).
3. Личный membership не удалять, пока TF + sandbox IAP стабильны.
4. Seller на карточке App Store = юримя компании.

---

## Запреты

- Не менять `family.aladdin.ios`
- Не грузить билд со старым Team после Transfer
- Не коммитить `.p8` / профили / ASC API keys
- Не класть открытый `.env` на флешку
