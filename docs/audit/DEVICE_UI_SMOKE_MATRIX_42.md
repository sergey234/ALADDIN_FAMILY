# Device/UI Smoke Matrix (42 components)

Цель: перевести `verify` в `docs/audit/AUDIT_42_INVENTORY.md` из `draft` в `ok` только после реальной device/UI-приемки.

Правило отметки:
- `api_check` — уже подтверждено прод-прогоном (`GET /api/components/configuration/{component_id}` = 200).
- `device_ui_smoke` — ручная проверка на устройстве (экран открыт, сценарий выполнен, данные/состояние корректны).
- `verify_ready` — можно переводить строку в `verify=ok`.

## KPI batch (7/42)

| component_id | api_check | device_ui_smoke | verify_ready | notes |
|---|---|---|---|---|
| driving_reports_agent | done | done | done | Device smoke confirmed: KPI card opened, stats rendered |
| dark_web_monitoring_agent | done | done | done | Device smoke confirmed: KPI card opened, stats rendered |
| russian_identity_theft_protection_agent | done | done | done | Device smoke confirmed: KPI card opened, stats rendered |
| location_bubble_agent | done | done | done | Device smoke confirmed: KPI card opened, stats rendered |
| personal_data_cleanup_agent | done | done | done | Device smoke confirmed: KPI card opened, stats rendered |
| anti_tracker_agent | done | done | done | Device smoke confirmed: KPI card opened, stats rendered |
| ai_categories_agent | done | done | done | Device smoke confirmed: KPI card opened, stats rendered |

## Batch 2 (7/42)

| component_id | api_check | device_ui_smoke | verify_ready | notes |
|---|---|---|---|---|
| crash_detection_agent | done | done | done | Device smoke confirmed: Screen 03, scenario executed |
| roadside_assistance_agent | done | done | done | Device smoke confirmed: Screen 03, scenario executed |
| emergency_response_bot | done | done | done | Device smoke confirmed: Screen 03, scenario executed |
| emergency_event_manager | done | done | done | Device smoke confirmed: Screen 03, scenario executed |
| phishing_protection_agent | done | done | done | Device smoke confirmed: Screen 03, scenario executed |
| malware_detection_agent | done | done | done | Device smoke confirmed: Screen 03, scenario executed |
| password_security_agent | done | done | done | Device smoke confirmed: Screen 03, scenario executed |

## Batch 3 (7/42)

| component_id | api_check | device_ui_smoke | verify_ready | notes |
|---|---|---|---|---|
| mobile_security_agent | done | done | done | Device smoke confirmed: Screen 03 settings flow |
| network_security_agent | done | done | done | Device smoke confirmed: Screen 03 settings flow |
| incident_response_agent | done | done | done | Device smoke confirmed: Screen 03 settings flow |
| self_harm_detection_agent | done | done | done | Device smoke confirmed: Screen 07 flow |
| grooming_detection_agent | done | done | done | Device smoke confirmed: Screen 07 flow |
| online_predators_agent | done | done | done | Device smoke confirmed: Screen 07 flow |
| psychological_support_agent | done | done | done | Device smoke confirmed: Screen 07 flow |

## Batch 4 (7/42)

| component_id | api_check | device_ui_smoke | verify_ready | notes |
|---|---|---|---|---|
| parental_control_bot | done | done | done | Device smoke confirmed: parental flow + games screen |
| telegram_security_bot | done | done | done | Device smoke confirmed: advanced protection flow |
| whatsapp_security_bot | done | done | done | Device smoke confirmed: advanced protection flow |
| instagram_security_bot | done | done | done | Device smoke confirmed: advanced protection flow |
| max_messenger_security_bot | done | done | done | Device smoke confirmed: advanced protection flow |
| gaming_security_bot | done | done | done | Device smoke confirmed: advanced protection flow |
| browser_security_bot | done | done | done | Device smoke confirmed: advanced protection flow |

## Batch 5 (7/42)

| component_id | api_check | device_ui_smoke | verify_ready | notes |
|---|---|---|---|---|
| emergency_contacts_manager | done | done | done | Device smoke confirmed after id-fix |
| emergency_notifications_manager | done | done | done | Device smoke confirmed after id-fix |
| voice_control_manager | done | done | done | Device smoke confirmed: settings flow |
| russian_child_protection_compliance_manager | done | done | done | Device smoke confirmed after id-fix |
| russian_data_protection_compliance_manager | done | done | done | Device smoke confirmed after id-fix |
| family_notification_manager | done | done | done | Device smoke confirmed: family modals flow |
| smart_notification_manager | done | done | done | Device smoke confirmed: notification settings flow |

## Batch 6 (7/42)

| component_id | api_check | device_ui_smoke | verify_ready | notes |
|---|---|---|---|---|
| child_interface_manager | done | done | done | Device smoke confirmed: child UI + gamification |
| elderly_interface_manager | done | done | done | Device smoke confirmed: elderly UI flow |
| subscription_manager | done | done | done | Device smoke confirmed: tariffs/paywall flow |
| referral_manager | done | done | done | Device smoke confirmed: referral screen |
| qr_payment_manager | done | done | done | Device smoke confirmed: payment QR flow |
| analytics_manager | done | done | done | Device smoke confirmed: analytics path |
| report_manager | done | done | done | Device smoke confirmed: reports modals |

## Acceptance for `verify=ok`

- Для каждой строки: `api_check=done` и `device_ui_smoke=done`.
- В `notes` зафиксирован короткий факт проверки (экран + действие + результат).
- После этого строка в `docs/audit/AUDIT_42_INVENTORY.md` переводится в `verify=ok`.
