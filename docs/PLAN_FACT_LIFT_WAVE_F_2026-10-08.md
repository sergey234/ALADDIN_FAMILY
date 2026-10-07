# План-факт Wave F (store-lift) — 2026-10-08

**Evidence:** `python3 scripts/verify_lift_wave_f.py` → PASS  
**Симулятор / Xcode:** ещё не запускались (по ТЗ — после verify).

| ID | План | Факт в коде | Evidence |
|----|------|-------------|----------|
| geo-01 | Пуш «домой» | `GeofenceEventStore` + `geofence_home_push_*` | marker |
| geo-02 | No Show | `GeofenceNoShowMonitor` + UI в геозонах | marker |
| geo-03 | История 7д | `retentionDays = 7` | marker |
| geo-04 | Согласие 152-ФЗ | `GeofencePlacesConsentStore` | marker |
| consent-01 | Crash consent | `CrashDetectionSettingsModal` gate | marker |
| crash-02 | «Я ок» / 112 / семья | `CrashDetectionAlertModal` | marker |
| browse-01 | Share+виджет+Siri | `AntifakeHubScreen` 3 path | marker |
| browse-02 | Safari blocker | `FamilyNetworkLayersLocalStatusBlock` how-to | marker |
| browse-03 | Sources | уже gai-01 / verdict card | prior |
| pwd-01 | Не сейф | honest scope banner | marker |
| pwd-02 | Покрытие + урок | coverage note + lesson 10 | marker |
| av-01 | Итог файла + Hub | summary + Privacy Hub CTA | marker |
| call-01 | 3 шага 60+ | `elderly_scam_call_step1…3` | marker |
| ux-01 | Day strip на виду | badge + larger title | marker |
| pay-01 | 3 уровня без страховки | `pay_tiers_plain_*` | marker |
| priv-01 / gai-08 / id-01 | Уроки 8–10 | `YoungDefenderView` | marker |
| sos-01 | Крупный SOS семье | `sos_alarm_*` | marker |
| bat-01 | Батарея critical | `FamilyBatteryCriticalMonitor` | marker |
| foot-02 | Цепочка в Hub | `dark_web_flow_*` | marker |
| darkweb-01 | Без паспорта/СНИЛС | form без полей | marker |
| legal-01 | Юрист | ⬜ | — |
| geo-05 | «В пути 30 мин» | ⏸ | — |
| crash-01 / fsl-qa-device | Device QA | ⬜ | — |
| foot-03 | HIBP email ops | ⬜ после GO | — |

## Как тестировали (до сборки)

1. Статический verify: маркеры файлов + код + RU/EN ключи.  
2. Локализация: каждый новый ключ в обоих словарях `LocalizationManager`.  
3. Unit/UI XCTest для Wave F не добавлялись в этом проходе — канон владельца: verify → план-факт → потом симулятор/Xcode.

## Следующий шаг владельца

1. Симулятор + сборка Xcode.  
2. Device QA: crash, геозоны, SOS, батарея.  
3. GO на `foot-03` (ops).  
4. `legal-01` с юристом.
