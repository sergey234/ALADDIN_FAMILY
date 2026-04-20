# Audit‑42: живая инвентаризация (канон для ML‑системы)

**Назначение:** одна таблица правды — откуда на проде берутся цифры и кто отвечает за свежесть.  
**Правило заполнения:** не гадать; смотреть код iOS (`AppConfig`, ViewModel), OpenAPI/роутер на сервере, `psql`/дашборд БД.

**Статусы колонок `inventory` / `verify`:** `TBD` | `draft` | `ok` | `n/a` (если компонент не тянет отчётный API).

Легенда **data_source:** `postgres` | `sfm` | `cache` | `mixed` | `TBD`.

---

## Таблица 1 — семь KPI‑карточек «Компоненты защиты» (отчёты `/api/reports/.../stats`)

| component_id | ios_surface (кратко) | read_api | data_source (ожид.) | owner_hint | sla_hint | inventory | verify |
|--------------|----------------------|----------|----------------------|------------|----------|-----------|--------|
| driving_reports_agent | Аналитика / дашборд KPI | `GET /api/reports/driving/stats?period=week` | postgres (`parental_reports` в роутере) | Backend on-call (L1) + Data/Analytics (L2) | freshness: по продукту; API SLO: p95 < 500ms, 5xx < 1% | ok | ok |
| dark_web_monitoring_agent | Аналитика / модалка DW | `GET /api/reports/dark-web/stats` | postgres (`darkweb.*` в роутере) | Backend on-call (L1) + Data/Analytics (L2) | freshness <= 72h; API SLO: p95 < 500ms, 5xx < 1% | ok | ok |
| russian_identity_theft_protection_agent | KPI Identity | `GET /api/reports/identity-theft/stats` | postgres (`identity.*`) | Backend on-call (L1) + Data/Analytics (L2) | freshness <= 24h; API SLO: p95 < 500ms, 5xx < 1% | ok | ok |
| location_bubble_agent | KPI Location | `GET /api/reports/privacy/location/stats` | postgres | Backend on-call (L1) + Data/Analytics (L2) | freshness <= 6h; API SLO: p95 < 500ms, 5xx < 1% | ok | ok |
| personal_data_cleanup_agent | KPI Cleanup | `GET /api/reports/privacy/cleanup/stats` | postgres | Backend on-call (L1) + Data/Analytics (L2) | freshness <= 168h; API SLO: p95 < 500ms, 5xx < 1% | ok | ok |
| anti_tracker_agent | KPI Tracker | `GET /api/reports/privacy/tracker/stats` | postgres | Backend on-call (L1) + Data/Analytics (L2) | freshness <= 12h; API SLO: p95 < 500ms, 5xx < 1% | ok | ok |
| ai_categories_agent | KPI AI | `GET /api/reports/ai-categories/stats` | postgres | Backend on-call (L1) + Data/Analytics (L2) | freshness: по продукту; API SLO: p95 < 500ms, 5xx < 1% | ok | ok |

> `draft` = путь и роутер подтверждены смоуками/контрактом; **не** `ok`, пока нет построчной UI‑приёмки на реальном устройстве и L2‑доказательства ingest->SLA->mini‑log.

---

## Таблица 2 — остальные 35 компонентов (заполнить до `ok`)

Идентификаторы совпадают с `docs/server/check_42_components_registry.py` (`ALL_42_COMPONENTS`).

Ниже — **черновик** по статическому коду (`Screens/*`, `AppConfig.Endpoint`): `ios_surface` и типовые пути компонентов; `data_source` и SLA требуют подтверждения на проде.

| component_id | ios_surface | read_api / write_api | data_source | owner_team | sla | inventory | verify |
|--------------|-------------|----------------------|-------------|------------|-----|-----------|--------|
| crash_detection_agent | `Screens/03_NetworkProtectionScreen.swift` (ДТП / авария) | компоненты: `GET /api/components/status` · `GET/POST /api/components/configuration/crash_detection_agent` · `POST /api/components/enable` · `POST /api/components/disable` · ДТП: `GET/POST /api/crash-detection/*` (sync, report, notifications, setup, status — см. `AppConfig.Endpoint`) | mixed | Backend on-call (L1) + iOS Client + Data/Analytics (L2) | API SLO: p95 < 500ms, 5xx < 1%; crash-flow SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| roadside_assistance_agent | `Screens/03_NetworkProtectionScreen.swift` (помощь на дороге) | компоненты (как выше для id) · `POST /api/roadside-assistance/call` · `GET /api/roadside-assistance/status/{id}` · `GET /api/roadside-assistance/history` | mixed | Backend on-call (L1) + iOS Client | API SLO: p95 < 500ms, 5xx < 1%; roadside SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| emergency_response_bot | `Screens/03_NetworkProtectionScreen.swift` (экстренный отклик) | компоненты · `GET/POST /api/crash-detection/notifications*` · `GET /api/network-protection/status` · connect/disconnect | mixed | Backend on-call (L1) + iOS Client | API SLO: p95 < 500ms, 5xx < 1%; incident SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| emergency_event_manager | `Screens/03_NetworkProtectionScreen.swift` (события / экстренный блок) | компоненты · `GET/POST /api/crash-detection/sync` · `POST /api/crash-detection/report` | mixed | Backend on-call (L1) + iOS Client + Data/Analytics (L2) | API SLO: p95 < 500ms, 5xx < 1%; event ingestion SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| phishing_protection_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/PhishingProtectionSettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client | API SLO: p95 < 500ms, 5xx < 1%; threat-detection SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| malware_detection_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/MalwareDetectionSettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Data/Analytics (L2) | API SLO: p95 < 500ms, 5xx < 1%; malware pipeline SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| mobile_security_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/MobileSecuritySettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client | API SLO: p95 < 500ms, 5xx < 1%; mobile-protection SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| network_security_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/NetworkSecuritySettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + SRE (L3) | API SLO: p95 < 500ms, 5xx < 1%; network-protection SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| incident_response_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/IncidentResponseSettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Data/Analytics (L2) | API SLO: p95 < 500ms, 5xx < 1%; incident-response SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| password_security_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/PasswordGeneratorSettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client | API SLO: p95 < 500ms, 5xx < 1%; password-policy SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| self_harm_detection_agent | `Screens/07_ParentalControlScreen.swift` | компоненты · родительский контур: `GET/POST /api/parental-control/settings*` · `GET/POST /api/parental-control/time-limits*` · `GET/POST /api/v1/parental-control/*` (см. `AppConfig.Endpoint`) | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; child-safety SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| grooming_detection_agent | `Screens/07_ParentalControlScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; child-safety SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| online_predators_agent | `Screens/07_ParentalControlScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; child-safety SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| psychological_support_agent | `Screens/07_ParentalControlScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; child-safety SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| parental_control_bot | `Screens/07_ParentalControlScreen.swift` · `GamesParentalControlScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; parental-control SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| telegram_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же + отчёты см. таблицу 1 для пересечений | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; messenger-safety SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| whatsapp_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; messenger-safety SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| instagram_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; messenger-safety SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| max_messenger_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; messenger-safety SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| gaming_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; gaming-safety SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| browser_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; browser-safety SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| emergency_contacts_manager | `Screens/05_SettingsScreen.swift` · `Screens/Views/EmergencyContactsView.swift` | **В коде id (fixed):** `emergency_contacts_manager` — `GET/POST /api/components/configuration/emergency_contacts_manager` + локально UserDefaults (`component_emergency_contact_manager_contacts`) | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; emergency-contact SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| emergency_notifications_manager | `Screens/05_SettingsScreen.swift` · `Screens/Views/EmergencyNotificationsView.swift` | **В коде id (fixed):** `emergency_notifications_manager` — компонентная конфигурация + `GET/POST /api/crash-detection/notifications*` · `GET /api/notifications*` | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; emergency-notifications SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| voice_control_manager | `Screens/05_SettingsScreen.swift` · `Screens/Views/VoiceControlView.swift` | `GET/POST /api/components/configuration/voice_control_manager` (+ компонентный статус) | mixed | Backend on-call (L1) + iOS Client | API SLO: p95 < 500ms, 5xx < 1%; voice-control SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| russian_child_protection_compliance_manager | `Screens/05_SettingsScreen.swift` · `Screens/Views/ComplianceView.swift` | **В коде id (fixed):** `russian_child_protection_compliance_manager` — `GET/POST /api/components/configuration/russian_child_protection_compliance_manager` · связка `GET/PATCH /api/user/profile/privacy*` | mixed | Backend on-call (L1) + iOS Client + Legal/Compliance | API SLO: p95 < 500ms, 5xx < 1%; RU child-compliance SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| russian_data_protection_compliance_manager | `Screens/05_SettingsScreen.swift` · `Screens/Views/ComplianceView.swift` | **В коде id (fixed):** `russian_data_protection_compliance_manager` — конфигурация компонента + `GET/PATCH /api/user/profile/privacy*` | mixed | Backend on-call (L1) + iOS Client + Legal/Compliance | API SLO: p95 < 500ms, 5xx < 1%; RU data-compliance SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| family_notification_manager | `Screens/02_FamilyScreen.swift` · `Shared/Components/Modals/FamilyNotificationSettingsModal.swift` | `GET/POST /api/components/configuration/family_notification_manager` · при push-инфраструктуре — `GET /api/notifications` / `GET /api/notifications/stats` | mixed | Backend on-call (L1) + iOS Client + Product Safety | API SLO: p95 < 500ms, 5xx < 1%; family-notification SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| smart_notification_manager | `Screens/NotificationSettingsScreen.swift` | `GET/POST /api/components/configuration/smart_notification_manager` · `GET/PATCH /api/settings/notifications*` · `GET /api/notifications/categories` | mixed | Backend on-call (L1) + iOS Client | API SLO: p95 < 500ms, 5xx < 1%; notification-routing SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| child_interface_manager | `Screens/08_ChildInterfaceScreen.swift` · `ChildContentScreen.swift` | UX + `GET /api/gamification/balance` и др. геймификация; настройки компонента — `GET/POST /api/components/configuration/child_interface_manager` (если включено в тарифе) | mixed | Backend on-call (L1) + iOS Client + Product | API SLO: p95 < 500ms, 5xx < 1%; child-interface SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| elderly_interface_manager | `Screens/09_ElderlyInterfaceScreen.swift` · `Screens/02_FamilyScreen.swift` (роль elderly) | `GET/POST /api/elderly/medications/*` · `GET/POST /api/elderly/appointments/*` · `GET /api/family/members` | mixed | Backend on-call (L1) + iOS Client + Product | API SLO: p95 < 500ms, 5xx < 1%; elderly-interface SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| subscription_manager | `Screens/10_TariffsScreen.swift` и связанные paywall | `GET /api/subscription/tariffs` · `GET /api/subscription/status` · `POST /api/subscription/subscribe` · `POST /api/subscription/sync` · др. `AppConfig.Endpoint.subscription*` | mixed | Backend on-call (L1) + iOS Client + Billing/Product | API SLO: p95 < 500ms, 5xx < 1%; subscription SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| referral_manager | `Screens/21_ReferralScreen.swift` | `GET /api/referral/code` · `GET /api/referral/stats` · `GET /api/referral/history` · `GET /api/referral/rewards` | postgres | Backend on-call (L1) + iOS Client + Growth/Product | API SLO: p95 < 500ms, 5xx < 1%; referral SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| qr_payment_manager | `Screens/25_PaymentQRScreen.swift` | `POST /api/payments/qr/create` · `GET /api/payments/qr/status/test` (+ актуальный prod-путь статуса при отличии от test) | mixed | Backend on-call (L1) + iOS Client + Billing/Product | API SLO: p95 < 500ms, 5xx < 1%; qr-payment SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| analytics_manager | фон + `AppConfig.Endpoint.analytics` · `metricsUpload` | `POST /api/metrics/upload` · `POST /api/analytics` | mixed | Backend on-call (L1) + Data/Analytics (L2) + iOS Client | API SLO: p95 < 500ms, 5xx < 1%; analytics-ingest SLA по продукту | ok | ok *(device/UI smoke confirmed)* |
| report_manager | `Shared/Components/Modals/DrivingReportsModal.swift` и др. отчёты | `GET /api/reports/*` (см. таблицу 1 для KPI) | postgres | Backend on-call (L1) + Data/Analytics (L2) + iOS Client | API SLO: p95 < 500ms, 5xx < 1%; reports SLA по продукту | ok | ok *(device/UI smoke confirmed)* |

*(Строки 1–7 дублируют KPI из таблицы 1 только по id; в таблице 2 их нет — полный список 42 = 7 + 35.)*

**Несовпадения id:** в `ALL_42_COMPONENTS` vs строка, передаваемая в `ComponentConfigurationService` на iOS:

| id в реестре 42 | id в Swift / UI |
|-----------------|-----------------|
| `emergency_contacts_manager` | `emergency_contact_manager` |
| `emergency_notifications_manager` | `emergency_notification_manager` |
| `russian_child_protection_compliance_manager` | `russian_child_protection_manager` |
| `russian_data_protection_compliance_manager` | `russian_data_protection_manager` |

Пока не выровнять реестр и клиент, смоук и OpenAPI нужно писать **по фактическому** id из колонки Swift.

### P0 результат проверки mismatch-id на проде (2026-04-20)

Проверка выполнена через `POST /api/auth/register-device` (JWT) и далее `GET /api/components/configuration/{component_id}`.

| pair | Swift id | Реестр id | Прод результат |
|------|----------|-----------|----------------|
| Emergency contacts | `emergency_contact_manager` | `emergency_contacts_manager` | Swift id -> 404, реестр id -> 200 |
| Emergency notifications | `emergency_notification_manager` | `emergency_notifications_manager` | Swift id -> 404, реестр id -> 200 |
| RU child compliance | `russian_child_protection_manager` | `russian_child_protection_compliance_manager` | Swift id -> 404, реестр id -> 200 |
| RU data compliance | `russian_data_protection_manager` | `russian_data_protection_compliance_manager` | Swift id -> 404, реестр id -> 200 |

Следствие (исторически): до унификации id на стороне iOS/backend нельзя было ставить `verify=ok` для этих 4 компонентов.

Статус устранения (код iOS, 2026-04-20):
- В `Screens/Views/EmergencyContactsView.swift` переключено на `emergency_contacts_manager`.
- В `Screens/Views/EmergencyNotificationsView.swift` переключено на `emergency_notifications_manager`.
- В `Screens/Views/ComplianceView.swift` переключено на `russian_*_protection_compliance_manager`.
- В `Core/Managers/ComponentTariffManager.swift` и `Core/Models/SubscriptionModels.swift` id выровнены с реестром.

Статус закрытия блока:
1. iOS id унифицированы с реестром.
2. Device/UI-smoke подтвержден.
3. `verify` для 4 строк переведен в `ok`.

---

## Следующий шаг к «100% идеально»

1. Назначить **владельца** колонки (команда iOS / backend / data).  
2. Для каждой строки таблицы 2: 30–60 минут — найти Swift‑экран и вызовы API, дописать `read_api`/`write_api` и `data_source`.  
3. Перевести `inventory` из `TBD` → `draft` → `ok`.  
4. Запустить прод‑смоук по сценарию → `verify` = `ok`.  
5. Параллельно завести **`docs/audit/EXTENDED_138_CHECKLIST.md`** по категориям из старых отчётов (`ПОЛНЫЙ_АНАЛИЗ_42_КОМПОНЕНТОВ_И_138_ФУНКЦИЙ.md` и др.) — не дублировать легенду, а ссылаться сюда.
