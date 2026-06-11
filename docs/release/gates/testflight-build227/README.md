# TestFlight build 227 — Hub demo screenshots

**Задачи:** R-08, R-09, R-10 · **Инструкция:** `docs/release/QA_HUB_DEMO_R08_R10.md`

## Capture on device (TestFlight)

После загрузки Archive на App Store Connect, на **физическом iPhone** с Premium test account:

| File | Hub | a11y anchor |
|------|-----|-------------|
| `R08_antifake_text_verdict.png` | Antifake | `antifake_verdict_card` |
| `R08_antifake_tabs.png` | Antifake | `antifake_hub_root` |
| `R09_privacy_darkweb_scan.png` | Privacy | `privacy_hub_darkweb_scan_cta` result |
| `R10_identity_snils_verdict.png` | Identity | `identity_hub_detect_verdict` |

Сохранять PNG в эту папку → приложить к App Store Review Notes при submit.

## Status

- [ ] PNG files captured
- [x] Backend VPS smokes PASS (`hub-demo-smoke-report.json`)
