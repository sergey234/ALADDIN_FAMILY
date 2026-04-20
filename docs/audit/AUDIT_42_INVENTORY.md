# Audit‑42: живая инвентаризация (канон для ML‑системы)

**Назначение:** одна таблица правды — откуда на проде берутся цифры и кто отвечает за свежесть.  
**Правило заполнения:** не гадать; смотреть код iOS (`AppConfig`, ViewModel), OpenAPI/роутер на сервере, `psql`/дашборд БД.

**Статусы колонок `inventory` / `verify`:** `TBD` | `draft` | `ok` | `n/a` (если компонент не тянет отчётный API).

Легенда **data_source:** `postgres` | `sfm` | `cache` | `mixed` | `TBD`.

---

## Таблица 1 — семь KPI‑карточек «Компоненты защиты» (отчёты `/api/reports/.../stats`)

| component_id | ios_surface (кратко) | read_api | data_source (ожид.) | sla_hint | inventory | verify |
|--------------|----------------------|----------|----------------------|----------|-----------|--------|
| driving_reports_agent | Аналитика / дашборд KPI | `GET /api/reports/driving/stats?period=week` | postgres (`parental_reports` в роутере) | по продукту | draft | draft |
| dark_web_monitoring_agent | Аналитика / модалка DW | `GET /api/reports/dark-web/stats` | postgres (`darkweb.*` в роутере) | см. THRESHOLDS | draft | draft |
| russian_identity_theft_protection_agent | KPI Identity | `GET /api/reports/identity-theft/stats` | postgres (`identity.*`) | см. THRESHOLDS | draft | draft |
| location_bubble_agent | KPI Location | `GET /api/reports/privacy/location/stats` | postgres | см. THRESHOLDS | draft | draft |
| personal_data_cleanup_agent | KPI Cleanup | `GET /api/reports/privacy/cleanup/stats` | postgres | см. THRESHOLDS | draft | draft |
| anti_tracker_agent | KPI Tracker | `GET /api/reports/privacy/tracker/stats` | postgres | см. THRESHOLDS | draft | draft |
| ai_categories_agent | KPI AI | `GET /api/reports/ai-categories/stats` | postgres | по продукту | draft | draft |

> `draft` = путь и роутер подтверждены смоуками/контрактом; **не** `ok`, пока нет записи владельца SLA + приёмки по реальным данным на проде.

---

## Таблица 2 — остальные 35 компонентов (заполнить до `ok`)

Идентификаторы совпадают с `docs/server/check_42_components_registry.py` (`ALL_42_COMPONENTS`).

Ниже — **черновик** по статическому коду (`Screens/*`, `AppConfig.Endpoint`): `ios_surface` и типовые пути компонентов; `data_source` и SLA требуют подтверждения на проде.

| component_id | ios_surface | read_api / write_api | data_source | owner_team | sla | inventory | verify |
|--------------|-------------|----------------------|-------------|------------|-----|-----------|--------|
| crash_detection_agent | `Screens/03_NetworkProtectionScreen.swift` (ДТП / авария) | компоненты: `GET /api/components/status` · `GET/POST /api/components/configuration/crash_detection_agent` · `POST /api/components/enable` · `POST /api/components/disable` · ДТП: `GET/POST /api/crash-detection/*` (sync, report, notifications, setup, status — см. `AppConfig.Endpoint`) | mixed | TBD | TBD | draft | TBD |
| roadside_assistance_agent | `Screens/03_NetworkProtectionScreen.swift` (помощь на дороге) | компоненты (как выше для id) · `POST /api/roadside-assistance/call` · `GET /api/roadside-assistance/status/{id}` · `GET /api/roadside-assistance/history` | mixed | TBD | TBD | draft | TBD |
| emergency_response_bot | `Screens/03_NetworkProtectionScreen.swift` (экстренный отклик) | компоненты · `GET/POST /api/crash-detection/notifications*` · `GET /api/network-protection/status` · connect/disconnect | mixed | TBD | TBD | draft | TBD |
| emergency_event_manager | `Screens/03_NetworkProtectionScreen.swift` (события / экстренный блок) | компоненты · `GET/POST /api/crash-detection/sync` · `POST /api/crash-detection/report` | mixed | TBD | TBD | draft | TBD |
| phishing_protection_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/PhishingProtectionSettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| malware_detection_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/MalwareDetectionSettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| mobile_security_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/MobileSecuritySettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| network_security_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/NetworkSecuritySettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| incident_response_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/IncidentResponseSettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| password_security_agent | `Screens/03_NetworkProtectionScreen.swift` · `Screens/PasswordGeneratorSettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| self_harm_detection_agent | `Screens/07_ParentalControlScreen.swift` | компоненты · родительский контур: `GET/POST /api/parental-control/settings*` · `GET/POST /api/parental-control/time-limits*` · `GET/POST /api/v1/parental-control/*` (см. `AppConfig.Endpoint`) | mixed | TBD | TBD | draft | TBD |
| grooming_detection_agent | `Screens/07_ParentalControlScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| online_predators_agent | `Screens/07_ParentalControlScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| psychological_support_agent | `Screens/07_ParentalControlScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| parental_control_bot | `Screens/07_ParentalControlScreen.swift` · `GamesParentalControlScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| telegram_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же + отчёты см. таблицу 1 для пересечений | mixed | TBD | TBD | draft | TBD |
| whatsapp_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| instagram_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| max_messenger_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| gaming_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| browser_security_bot | `Screens/AdvancedProtectionSettingsScreen.swift` | то же | mixed | TBD | TBD | draft | TBD |
| emergency_contacts_manager | `Screens/05_SettingsScreen.swift` · `Screens/Views/EmergencyContactsView.swift` | **В коде id:** `emergency_contact_manager` — `GET/POST /api/components/configuration/emergency_contact_manager` + локально UserDefaults (`component_emergency_contact_manager_contacts`) | mixed | TBD | TBD | draft | TBD |
| emergency_notifications_manager | `Screens/05_SettingsScreen.swift` · `Screens/Views/EmergencyNotificationsView.swift` | **В коде id:** `emergency_notification_manager` — компонентная конфигурация + `GET/POST /api/crash-detection/notifications*` · `GET /api/notifications*` | mixed | TBD | TBD | draft | TBD |
| voice_control_manager | `Screens/05_SettingsScreen.swift` · `Screens/Views/VoiceControlView.swift` | `GET/POST /api/components/configuration/voice_control_manager` (+ компонентный статус) | mixed | TBD | TBD | draft | TBD |
| russian_child_protection_compliance_manager | `Screens/05_SettingsScreen.swift` · `Screens/Views/ComplianceView.swift` | **В коде id:** `russian_child_protection_manager` — `GET/POST /api/components/configuration/russian_child_protection_manager` · связка `GET/PATCH /api/user/profile/privacy*` | mixed | TBD | TBD | draft | TBD |
| russian_data_protection_compliance_manager | `Screens/05_SettingsScreen.swift` · `Screens/Views/ComplianceView.swift` | **В коде id:** `russian_data_protection_manager` — конфигурация компонента + `GET/PATCH /api/user/profile/privacy*` | mixed | TBD | TBD | draft | TBD |
| family_notification_manager | `Screens/02_FamilyScreen.swift` · `Shared/Components/Modals/FamilyNotificationSettingsModal.swift` | `GET/POST /api/components/configuration/family_notification_manager` · при push-инфраструктуре — `GET /api/notifications` / `GET /api/notifications/stats` | mixed | TBD | TBD | draft | TBD |
| smart_notification_manager | `Screens/NotificationSettingsScreen.swift` | `GET/POST /api/components/configuration/smart_notification_manager` · `GET/PATCH /api/settings/notifications*` · `GET /api/notifications/categories` | mixed | TBD | TBD | draft | TBD |
| child_interface_manager | `Screens/08_ChildInterfaceScreen.swift` · `ChildContentScreen.swift` | UX + `GET /api/gamification/balance` и др. геймификация; настройки компонента — `GET/POST /api/components/configuration/child_interface_manager` (если включено в тарифе) | mixed | TBD | TBD | draft | TBD |
| elderly_interface_manager | `Screens/09_ElderlyInterfaceScreen.swift` · `Screens/02_FamilyScreen.swift` (роль elderly) | `GET/POST /api/elderly/medications/*` · `GET/POST /api/elderly/appointments/*` · `GET /api/family/members` | mixed | TBD | TBD | draft | TBD |
| subscription_manager | `Screens/10_TariffsScreen.swift` и связанные paywall | `GET /api/subscription/tariffs` · `GET /api/subscription/status` · `POST /api/subscription/subscribe` · `POST /api/subscription/sync` · др. `AppConfig.Endpoint.subscription*` | mixed | TBD | TBD | draft | TBD |
| referral_manager | `Screens/21_ReferralScreen.swift` | `GET /api/referral/code` · `GET /api/referral/stats` · `GET /api/referral/history` · `GET /api/referral/rewards` | postgres | TBD | TBD | draft | TBD |
| qr_payment_manager | `Screens/25_PaymentQRScreen.swift` | `POST /api/payments/qr/create` · `GET /api/payments/qr/status/test` (+ актуальный prod-путь статуса при отличии от test) | mixed | TBD | TBD | draft | TBD |
| analytics_manager | фон + `AppConfig.Endpoint.analytics` · `metricsUpload` | `POST /api/metrics/upload` · `POST /api/analytics` | mixed | TBD | TBD | draft | TBD |
| report_manager | `Shared/Components/Modals/DrivingReportsModal.swift` и др. отчёты | `GET /api/reports/*` (см. таблицу 1 для KPI) | postgres | TBD | TBD | draft | TBD |

*(Строки 1–7 дублируют KPI из таблицы 1 только по id; в таблице 2 их нет — полный список 42 = 7 + 35.)*

**Несовпадения id:** в `ALL_42_COMPONENTS` vs строка, передаваемая в `ComponentConfigurationService` на iOS:

| id в реестре 42 | id в Swift / UI |
|-----------------|-----------------|
| `emergency_contacts_manager` | `emergency_contact_manager` |
| `emergency_notifications_manager` | `emergency_notification_manager` |
| `russian_child_protection_compliance_manager` | `russian_child_protection_manager` |
| `russian_data_protection_compliance_manager` | `russian_data_protection_manager` |

Пока не выровнять реестр и клиент, смоук и OpenAPI нужно писать **по фактическому** id из колонки Swift.

---

## Следующий шаг к «100% идеально»

1. Назначить **владельца** колонки (команда iOS / backend / data).  
2. Для каждой строки таблицы 2: 30–60 минут — найти Swift‑экран и вызовы API, дописать `read_api`/`write_api` и `data_source`.  
3. Перевести `inventory` из `TBD` → `draft` → `ok`.  
4. Запустить прод‑смоук по сценарию → `verify` = `ok`.  
5. Параллельно завести **`docs/audit/EXTENDED_138_CHECKLIST.md`** по категориям из старых отчётов (`ПОЛНЫЙ_АНАЛИЗ_42_КОМПОНЕНТОВ_И_138_ФУНКЦИЙ.md` и др.) — не дублировать легенду, а ссылаться сюда.
