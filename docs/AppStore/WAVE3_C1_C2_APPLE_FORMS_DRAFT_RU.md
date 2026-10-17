# WAVE3 · C1 / C2 — черновики заявок Apple (Account Holder)

**IDs:** `cap-C1` Critical Alerts · `cap-C2` Communication Notifications  
**Дата:** 2026-10-17  
**Важно:** обычные push для геозон/SOS **уже работают без этих форм**. C1/C2 — усиление (экран выкл. / звонок-стиль), не блокер L4.

Подаёт **Account Holder** команды **B3WGHSWL79** · app **ai.aladdin**.

---

## C1 — Critical Alerts

**Portal:** [Request a Critical Alerts entitlement](https://developer.apple.com/contact/request/notifications-critical-alerts-entitlement/) (или актуальная форма в Account)

### Suggested answers (EN)

| Field | Draft |
|-------|--------|
| App name / Bundle ID | ALADDIN / `ai.aladdin` |
| Why Critical Alerts | Family safety: SOS / “Need help”, elderly fall or scam-call urgency, optional geofence leave when a vulnerable member is expected home. Not marketing. |
| How used | Interrupt Do Not Disturb only for predefined high-urgency family categories (SOS, fall, urgent scam). User can disable in Settings. |
| Alternatives tried | Ordinary push + local notifications first; Critical only when silence would put a family member at risk. |
| Not used for | Ads, promos, engagement, news, social. |

### После Assigned
→ `cap-D1`…`D4` + optional `cap-L11` (geofence → critical). До Assigned: `AppConfig.allowsCriticalAlerts = false`.

---

## C2 — Communication Notifications

**Portal:** Communication Notifications entitlement request (Apple Developer → Capabilities / contact form — актуальный URL у Account Holder).

### Suggested answers (EN)

| Field | Draft |
|-------|--------|
| Why | Show incoming spam / unknown-caller style family alert with person/avatar semantics; pairs with Call Directory labeling. |
| How | Communication Notification category for suspected scam / labeled caller; not for marketing chat. |
| Related | Call Directory extension (already or planned) — spam/scam labels for family protection. |

### После Assigned
→ `cap-E1` / `E2`. До Assigned — не обещать в ASO.

---

## Чеклист владельца

- [ ] C1 форма отправлена  
- [ ] C2 форма отправлена  
- [ ] Дождаться Assigned → portal entitlements на App ID → новые profiles → secrets CI  

**Не путать с C3** (NE Content Filter / DNS Proxy — отдельная форма, не VPN).
