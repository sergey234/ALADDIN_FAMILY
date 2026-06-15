# QA sign-off — Antifake Call Directory (R-02)

**Template:** fill on device · **Attachments:** `docs/release/qa_signoff/antifake/`  
**Machine record:** `docs/release/qa_signoff/antifake/signoff_record.json`

**Tester:** _______________  
**Date:** _______________  
**Build:** _______________  
**Device / iOS:** _______________

## Code prerequisites (static — done)

- [x] R-01 static gate: `python3 scripts/verify_antifake_release_readiness.py`
- [x] Prod smoke + af-11 gate green (`R-03`)
- [x] Privacy manifests + policy section (`N-01`, `N-04`)

## Must capture (device)

| # | Check | Pass | Attachment file | Notes |
|---|-------|------|-----------------|-------|
| 1 | Extension ON in Settings | ☐ | `NNN_01_extension_on_*.png` | Settings → Phone → ALADDIN ON |
| 2 | Sync «Синхронизировано N» N ≥ 100 | ☐ | `NNN_02_sync_n*.png` | Hub card after sync |
| 3 | Incoming call label on QA number | ☐ | `NNN_03_incoming_label.*` | `74951234567` / `78005553535` |
| 4 | Extension OFF → orange status | ☐ | `NNN_04_ext_off_orange.png` | `D-08` |
| 5 | EN locale label text | ☐ | `NNN_05_en_label.png` | `D-10` |

## Post-call (E-06)

| # | Check | Pass | Attachment | Notes |
|---|-------|------|------------|-------|
| 6 | After call → notification ~2 s | ☐ | | |
| 7 | Tap → Hub **Звонок** ≤ 2 taps | ☐ | | See `docs/ANTIFAKE_POST_CALL_DEVICE_QA.md` |
| 8 | Toggle reminder OFF → no push | ☐ | | `E-05` |

## Sign-off

- [ ] All MUST rows passed or waived with Apple/platform limitation documented
- [ ] Attachments stored in `docs/release/qa_signoff/antifake/`
- [ ] `signoff_record.json` updated (`status`: `signed`)

**Signature:** _______________
