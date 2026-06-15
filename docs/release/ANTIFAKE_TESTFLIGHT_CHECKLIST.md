# TestFlight checklist — Antifake (R-01)

**Order:** D-04 → C-03 → B-02 → F-05 → N-01 (per v4 registry)

**Code gate (no device):** `bash scripts/verify_antifake_all_static.sh` → all gates pass  
**Legacy:** `./scripts/verify_antifake_release_readiness.py` → `pass: true`

---

## A. Code / static (run now)

- [x] Call Directory + Share extensions in Xcode embed phase (`D-05` CI signing)
- [x] `PrivacyInfo.xcprivacy` — main + Call Directory + Share (`N-01`)
- [x] Hub 4 tabs in `AntifakeHubScreen` (text · audio · video · call)
- [x] Post-call deep link + privacy wipe + phone hash (`E-03`, `N-02`, `N-03`)
- [x] Media upload consent (`N-05`)
- [x] App Store Review Notes draft (`A-07`)
- [x] QA sign-off template + attachment folder (`R-02` infrastructure)
- [x] `bypassPremiumGate = false` in `AntifakeAccessPolicy` (G-03) — UITest uses `-UITestAntifakeHubSmoke`
- [x] Deploy script + prod smoke + gate af-11 artifacts (`B-07`, `R-03`)

**Verify:** `python3 scripts/verify_antifake_release_readiness.py`

---

## B. Server (before external beta)

- [x] `./scripts/deploy_antifake_m1.sh` — fraud DB + SFM + B batch (`B-07`)
- [x] `ANTIFAKE_SMOKE_POLL_JOB=1` smoke pass (`R-03` / `B-02`)
- [x] nginx snippet 25MB + 300s (`B-06`)
- [x] Cron: `antifake_cleanup_uploads.py` every 15 min (`B-08`)

---

## C. TestFlight internal — **device phase (deferred)**

- [ ] Install on physical iPhone (iOS 15.2+) (`D-02`)
- [ ] Premium account or bypass ON
- [ ] **C-03:** Sync call-directory → N ≥ 100 (`C-08`)
- [ ] **D-04:** Incoming test call shows label for QA number (`74951234567` / `78005553535`)
- [ ] Text/url check returns non-mock source (`F-01`)
- [ ] Verdict v2 UI: reasons + disclaimer + next steps (`J-01…J-03`)
- [ ] Post-call notification → Hub Call tab (`E-03`, `E-06`)
- [ ] Media upload consent first time on device (`N-05`)

---

## D. External beta criteria

- [x] No «mock» / `sfm_mock` in antifake prod paths (`Q-05` — `verify_antifake_no_mock_pre_submit.py`)
- [x] App Store Review Notes attached (`A-07`)
- [ ] QA sign-off doc signed with attachments (`R-02` — device)

---

## E. Deferred to end of queue

- Archive → TestFlight production (`D-01`, `D-02`)
- PIR / bypass off (`H-*`, `G-03`, `B-10` prod already `ANTIFAKE_ALLOW_FREE=0`)
