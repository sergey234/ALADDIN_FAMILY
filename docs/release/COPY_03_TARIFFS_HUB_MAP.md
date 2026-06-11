# B-COPY-03 — Tariffs ↔ Hub Screen Map

**Дата:** 2026-06-11 · **Источники:** `TariffCard.swift`, `ThreatProtectionCategory`, Hub screens, `TariffManager`.

---

## Hub navigation map

| Hub | Screen | Min tariff | Premium gate | L3 gate |
|-----|--------|------------|--------------|---------|
| Antifake | `AntifakeHubScreen` | Premium | `PremiumGateHandler` | GATE-E |
| Privacy | `PrivacyHubScreen` | Family+ | category toggles | GATE-F |
| Identity | `IdentityHubScreen` | Personal+ | detect tab | GATE-G |
| Device | `DeviceHubScreen` | Free (partial) | scan premium tiers | GATE-H |
| Family | `02_FamilyScreen` | Family | member limits | GATE-I |
| Network / VPN | `03_NetworkProtectionScreen` | Personal+ VPN | component toggles | B7-04 pending |
| Elderly | `09_ElderlyInterfaceScreen` | Family+ | role elderly | B7-03 ✅ |
| Emergency | Roadside + Crash (Network Protection) | Personal+ | component rows | B7 🔄 |

---

## 9 protection categories → Hub

| Category ID | Hub / screen | Tariff (`requiredTariff`) |
|-------------|--------------|---------------------------|
| `deepfakes` | Antifake Hub | Premium |
| `fraud` | Identity Hub | Personal+ |
| `dataLeaks` | Privacy Hub | Family+ |
| `childThreats` | Family monitoring | Family |
| `cyberThreats` | Device Hub | Free partial / Personal full |
| `networkThreats` | Network Protection | Personal+ |
| `mobileThreats` | Device Hub Mobile tab | Personal+ |
| `iotThreats` | Device Hub IoT | Family+ |
| `familyThreats` | Family | Family |

---

## Tariff marketing bullets → verify

| Tariff | Claim in UI | Must map to |
|--------|-------------|-------------|
| Free | Basic scans, limited categories | Device Hub quick scan only |
| Personal | Identity + fraud + VPN | Identity Hub + Network Protection |
| Family | Parental + children + elderly | Family + Elderly screens |
| Premium | Deepfakes + antifake full | Antifake Hub all tabs |

---

## Gaps for App Store

1. Premium antifake — указать async processing для video/audio (job poll).
2. VPN — не в premium bullets до B7-04 PASS.
3. «138 functions» — привязать к `%` в `TariffCard.protectionPercentage`, не absolute count in store text.

---

## PASS B-COPY-03

- [x] Hub ↔ tariff matrix documented
- [ ] Tariff screen copy edits — post B-QA-02 (UI optional)
