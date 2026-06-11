# B-QA-02 — TestFlight Archive checklist

**Дата:** 2026-06-11 · **Build:** 227 · **Статус:** blocked on signing (локальная машина)

## Pre-flight ✅ (автоматически закрыто)

| Step | Evidence |
|------|----------|
| VPN `vpn_prod_smoke.sh` 10/10 VPS | 2026-06-11, nonce fix deployed |
| `xcodebuild build` Simulator | BUILD SUCCEEDED |
| Unit tests 62/62 | B7-UT-01 + B2-00c PASS |
| Emergency smoke | `test_emergency_prod_smoke.py` pass:true |

## Archive blocker (требует Xcode на Mac с сертификатами)

```
error: No signing certificate "iOS Distribution" found (team 6CJVBBUGSN)
error: No profile matching 'ALADDIN App Store Distribution new'
```

**Действия:**
1. Xcode → Settings → Accounts → Download Manual Profiles
2. Или установить Distribution certificate + profiles для:
   - `family.aladdin.ios`
   - `family.aladdin.ios.ALADDINContentBlocker`
   - `family.aladdin.ios.ALADDINAntifakeShare`
3. Product → Archive (Release, Manual signing как в pbxproj)
4. Distribute App → TestFlight → `ExportOptions.plist`

## TestFlight L3 demo path (R-08…10) ✅ backend

**Полный гайд:** `docs/release/QA_HUB_DEMO_R08_R10.md`  
**VPS evidence:** `docs/release/gates/hub-demo-smoke-report.json`

| ID | Hub | Сценарий | Backend | UI PNG |
|----|-----|----------|---------|--------|
| B2-09 R-08 | Antifake | text «переведите деньги» → dfk matrix | ✅ | ☐ device |
| B3-08 R-09 | Privacy | dark web scan CTA → real job | ✅ | ☐ device |
| B4-06 R-10 | Identity | SNILS detect → SecurityVerdict card | ✅ | ☐ device |
| B7 | Network Protection | Roadside + Crash | ✅ emergency smoke | ☐ device |
| B6 | Family | parental monitoring → PDF export | ✅ GATE-I | ☐ device |

Скриншоты: `docs/release/gates/testflight-build227/` (capture at Archive session)

## Sign-off

- [ ] Archive uploaded to App Store Connect
- [ ] TestFlight build processed
- [ ] 138 matrix walkthrough on device
- [ ] `security-l3-report.json` → `xcode_archive_allowed: true`, QA-138 pass
