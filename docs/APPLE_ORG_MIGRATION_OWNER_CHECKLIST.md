# ALADDIN Org Migration — чеклист владельца

Отмечайте по мере выполнения в Apple / Xcode. Агент подготовил runbook и скрипты; портал Apple — только вы.

## gate0

- [ ] Заполнен `docs/APPLE_ORG_MIGRATION_GATE0_WORKSHEET.md`
- [ ] Известен Company Team ID
- [ ] Выбран путь A / B / C

## org-agreements

- [ ] Paid Apps Agreement Active (компания)
- [ ] Free Apps Agreement
- [ ] Tax / Banking
- [ ] Users and Access: Admin/Developer для вашего Apple ID

## transfer-or-convert

- [ ] Convert выполнен **или**
- [ ] (C) Минимальный App Store релиз на личном
- [ ] Transfer инициирован + Accepted
- [ ] App виден только в ASC компании

## identifiers-profiles

- [ ] App IDs 4 bundles на Company Team
- [ ] App Group `group.com.aladdin.family`
- [ ] Associated Domains `applinks:aladdin-ai.ru`
- [ ] Profiles Debug + App Store для app + 3 appex
- [ ] APNs `.p8` компании (путь записан в сейф)

## xcode-resign

- [ ] `./scripts/ios_set_development_team.sh <COMPANY_TEAM_ID>`
- [ ] `./scripts/ios_verify_signing_targets.sh` → OK
- [ ] Xcode Accounts → Organization team
- [ ] Archive → Validate → Upload OK

## testflight-org

- [ ] Билд в TestFlight компании
- [ ] Внутренний тестер установил
- [ ] Smoke: запуск, семья, сеть, antifake share (если нужно)

## iap-subscriptions

- [ ] Product IDs как в `APPLE_ORG_IAP_PRODUCT_IDS.md`
- [ ] Sandbox покупка individual/family/premium
- [ ] Server Notifications V2 на MAIN
- [ ] QR-ветка RU не сломана (`useIAP`)

## closeout

- [ ] What’s New с re-login текстом
- [ ] Сейф / master-index: Company Team ID
- [ ] Личный аккаунт сохранён до стабилизации
- [ ] Seller = компания на карточке магазина
