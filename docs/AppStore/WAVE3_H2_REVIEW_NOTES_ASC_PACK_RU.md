# WAVE3 · H2 — Review Notes + ASO honesty (paste pack)

**ID:** `cap-H2` · **Дата:** 2026-10-17  
**Связка:** location → [`WAVE3_L15_ASC_PRIVACY_LOCATION_PACK_RU.md`](WAVE3_L15_ASC_PRIVACY_LOCATION_PACK_RU.md)  
**Куда:** App Store Connect → версия → **App Review Information → Notes**

---

## Review Notes (EN — вставить целиком)

```text
ALADDIN FAMILY — REVIEW NOTES (WAVE3 / build 10+)

WHAT THE APP IS
Family safety: parental Screen Time limits (FamilyControls), family place alerts (geofence enter/exit), soft presence (“I’m OK” without GPS), SOS share-location-now, anti-scam / elderly alerts (ordinary push). Optional AI companion with parental gate.

SCREEN TIME / FAMILY CONTROLS
Uses Apple FamilyControls + DeviceActivity + ManagedSettings + Shield.
Shield Action (ask parent / dismiss) uses the same Family Controls entitlement.
Usage minutes sync parent↔child for parental control only — not advertising, not third-party tracking.
System Family Controls may be gated in some builds until Device QA; UI shows honest empty / setup states (no fake minutes).

LOCATION
See also dedicated LOCATION block: family place alerts + SOS only.
No UIBackgroundModes "location". No continuous GPS / route line. No location for ads.
Adult members opt in via “My places for the family”. Parent enables place alerts explicitly.

PUSH
Ordinary local + remote notifications for family alerts.
Critical Alerts / Communication Notifications — only after Apple entitlement Assigned (forms submitted separately). Until then we do not claim critical/interrupt delivery.

NETWORK / FILTER
No in-app Packet Tunnel VPN. Any future system Content Filter / DNS Proxy is parental web filter only and requires a separate Apple Network Extension entitlement — not present as VPN.

WE DO NOT
- Call recording
- MDM / device supervision
- Silent GPS analytics
- Fake Screen Time statistics
- Claim Critical Alerts before entitlement is Assigned

TEST ACCOUNT
(Use existing family test credentials from App Review notes / demo account field.)

CONTACT
(Owner email / phone in ASC App Review Information.)
```

---

## ASO / listing — запрещённые формулировки

| Не писать | Писать вместо |
|-----------|----------------|
| «записываем звонки» | «метка спам-звонка» / Call Directory (когда есть) |
| «MDM», «корпоративный контроль устройства» | «родительский контроль Screen Time» |
| «live GPS 24/7», «трекинг маршрута» | «алерты о местах: пришёл / ушёл» |
| «VPN внутри приложения» | не обещать; VPN — отдельный продукт/бот, не WAVE3 iOS |
| «Critical Alerts» в сторе до Assigned | «важные семейные уведомления» |

---

## DoD

| Критерий | Статус |
|----------|--------|
| Pack в репо | ✅ |
| Notes вставлены в ASC на версию | ⏳ владелец |
| Listing без запрещённых фраз | ⏳ владелец перед Submit |
