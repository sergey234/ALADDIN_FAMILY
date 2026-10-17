# Capabilities WAVE 3 — Task Registry (`cap-*`)

**SSOT:** `docs/AppStore/CAPABILITIES_WAVE3_BUILD11_MASTER_PLAN_2026-10-17_RU.md`  
**Rule:** `.cursor/rules/capabilities-wave3-todo-ssot.mdc`  
**Build:** TF **10** ship · NEXT **11** (только после GO)  
**OUT:** Packet Tunnel / in-app VPN — не делаем

## Mandatory TodoWrite

1. Close with `merge: true` + matching `cap-*` id(s).  
2. **Never** `merge: false` unless owner: «восстанови TODO WAVE3 из REGISTRY».  
3. On close: registry ✅ → plan checklist ☑ → TodoWrite merge.

## Work order

```
L0 diag ✅ → L3/L5/L1/L2/L10 (code, no device)
∥ L4 server APNs (GO deploy)
A0 Device QA build10 + geofence walk (G11/G12)
→ A1 FC on → A2–A4 → B Shield Action (MUST 11)
∥ C Apple forms → D/E/F/G + L11 → H → I ship 11
```

**OUT:** Packet Tunnel · `UIBackgroundModes location` · continuous GPS

| ID | Фаза | Задача | Статус |
|----|------|--------|--------|
| cap-meta | — | Plan + registry + rule | ✅ |
| st-report-ek | ST | DeviceActivityReport → ExtensionKit (ASC 409) | ✅ код · push ⏳ GO |
| cap-L0 | L | Диагноз geofence no-push (15 причин + who-checks L.0b) | ✅ |
| cap-L1 | L | Always gate + honest monitoring status | ✅ |
| cap-L2 | L | requestState after start monitoring | ✅ |
| cap-L3 | L | Important types: all geofence enter/exit | ✅ |
| cap-L4 | L | Server geofence-event → APNs parents | ✅ deployed MAIN 2026-10-17 · walk-test ⏳ |
| cap-L5 | L | Purpose strings + Review Notes location | ✅ plist/strings · Notes ⏳ |
| cap-L6 | L | Place coords map/GPS (no silent skip) | ✅ |
| cap-L7 | L | SOS / share location When In Use | ✅ |
| cap-L8 | L | Soft presence polish (no GPS) | ✅ |
| cap-L9 | L | Location Bubble honesty | ✅ |
| cap-L10 | L | Verify no UIBackgroundModes location | ✅ script |
| cap-L11 | L | Geofence → Critical Alerts (after D) | ⏳ |
| cap-L12 | L | UX: WhenInUse → explain → Always only for places | ✅ |
| cap-L13 | L | Sync geofences :8002 + kill fake/demo coords | ✅ code · soft upsert |
| cap-L14 | L | Precise Location only setup zone / SOS | ✅ setup helper · SOS later |
| cap-L15 | L | ASC Privacy labels + Notes «alerts not track» | ✅ pack `WAVE3_L15_ASC_PRIVACY_LOCATION_PACK_RU.md` · ⏳ галочки ASC |
| cap-L16 | L | Member toggle: no track without explicit opt-in | ✅ parent consent |
| cap-L16-copy | L | Owner pick P1–P3 / A1–A3 names → apply RU/EN | ✅ P1+A3 |
| cap-L16-teen | L | Teen Always honesty copy (no under-18 signature) | ✅ |
| cap-L16-adult | L | Adult member opt-in toggle (A* label, no «следить») | ✅ A3 |
| cap-A0 | A | Device QA ST 2 iPhone (build 10) | ⏳ |
| cap-A1 | A | allowsSystemFamilyControls=true after QA+GO | ⏳ |
| cap-A2 | A | Honest parent↔child minutes sync prod | ⏳ |
| cap-A3 | A | ManagedSettings limits + honesty | ✅ FC-gate apply + UI honesty |
| cap-A4 | A | Archive entitlements FC+appex | ⏳ |
| cap-B1 | B | Shield Action target + FC profile | ✅ code · portal profile ⏳ |
| cap-B2 | B | Ask Parent / Close + App Group + Loc | ✅ |
| cap-B3 | B | CI secrets + Fastfile Shield Action | ✅ Fastfile · secret ⏳ |
| cap-B4 | B | Parent notify on shield ask | ✅ local banner · APNs ⏳ |
| cap-C1 | C | Apple form Critical Alerts | ✅ draft `WAVE3_C1_C2_APPLE_FORMS_DRAFT_RU.md` · ⏳ submit AH |
| cap-C2 | C | Apple form Communication Notifications | ✅ draft · ⏳ submit AH |
| cap-C3 | C | Apple form NE Content Filter/DNS Proxy (not VPN) | ✅ draft `WAVE3_C3_NE_CONTENT_FILTER_FORM_DRAFT_RU.md` · ⏳ submit AH |
| cap-C4 | C | Assigned → App IDs + profiles + secrets | ⏳ |
| cap-D1 | D | Critical Alerts entitlement + auth | ⏳ |
| cap-D2 | D | Server critical push SOS/fall/scam | ⏳ |
| cap-D3 | D | iOS critical payload → UI | ⏳ |
| cap-D4 | D | allowsCriticalAlerts policy flag | ✅ false + UN auth gate · Comm/NE flags too |
| cap-E1 | E | Communication Notifications + Call UI | ⏳ |
| cap-E2 | E | Call Directory sync/setup polish | ⏳ |
| cap-F1 | F | NE Filter/DNSProxy design (no tunnel) | ✅ ADR `WAVE3_F1_NE_FILTER_ADR_RU.md` |
| cap-F2 | F | FilterProvider + parental rules | ⏳ |
| cap-F3 | F | Parental UI Safari vs system filter | ✅ honesty copy Safari + gated system |
| cap-F4 | F | CI NE Filter profiles | ⏳ |
| cap-G1 | G | HealthKit capability + privacy strings | ⏳ |
| cap-G2 | G | Fall → family incident push | ⏳ |
| cap-G3 | G | allowsHealthKitIntegration=true + GO | ⏳ |
| cap-H1 | H | Info.plist privacy audit | ✅ `WAVE3_H1_INFOPLIST_PRIVACY_AUDIT_2026-10-17_RU.md` · removed unused |
| cap-H2 | H | ASO / Review Notes honesty | ✅ pack `WAVE3_H2_REVIEW_NOTES_ASC_PACK_RU.md` · ⏳ ASC paste |
| cap-I1 | I | verify_capabilities_wave3_static.sh | ✅ + H1 unused keys + L16 strings |
| cap-I2 | I | Bump 10→11 (GO) | ⏳ |
| cap-I3 | I | Commit+push CI Upload TF 11 | ⏳ |
| cap-I4 | I | Device QA build 11 | ⏳ |
| cap-I5 | I | Submit / Review Notes | ⏳ |

**Легенда:** ✅ done · ⏳ pending · 🚧 in progress · ❌ blocked

### Связь Screen Time WAVE2

| st-* | WAVE3 |
|------|-------|
| st-E1 Device QA | = cap-A0 |
| st-D11 FC flag on | = cap-A1 |
| st-F1 Shield Action | = cap-B1…B4 |

При закрытии обновлять **оба** registry (merge TodoWrite оба id).
