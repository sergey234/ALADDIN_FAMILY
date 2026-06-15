# DEVICE batch runbook — D-01…D-04 (then G-03)

**Order:** static gate → sim build → archive → TestFlight → on-device QA → G-03 bypass off.

---

## 1. Static (no Mac signing)

```bash
bash scripts/verify_antifake_device_readiness.sh
bash scripts/verify_antifake_q_static.sh
```

---

## 2. D-01 — Build

**Simulator (compile all targets):**

```bash
./scripts/archive_antifake_device_build.sh --simulator-only
```

**Archive (TestFlight / real device):**

```bash
# Set provisioning UUIDs — see docs/CI_ANTIFAKE_SHARE_SIGNING_HANDOFF.md
./scripts/archive_antifake_device_build.sh
# or: bundle exec fastlane ios build_archive
```

---

## 3. D-02 — TestFlight → iPhone

1. Upload archive via Xcode Organizer or `fastlane deliver`
2. Install on physical iPhone (iOS 15.2+)
3. Record build number in `docs/release/device_qa/antifake/DEVICE_QA_RECORD.json`

---

## 4. D-03 / D-04 — Call Directory (real device only)

Follow `docs/ANTIFAKE_CALL_DIRECTORY_DEVICE_QA.md`:

1. Hub → enable extension in Settings
2. Sync → N ≥ 100
3. Incoming call from QA number → label on screen (D-04)

Attachments → `docs/release/qa_signoff/antifake/`

---

## 5. E-06 / R-02 — Post-call + sign-off

- `docs/ANTIFAKE_POST_CALL_DEVICE_QA.md`
- `docs/release/ANTIFAKE_QA_SIGNOFF.md`

---

## 6. After DEVICE QA — G-03 + Q-01

```bash
# bypassPremiumGate must be false in AntifakeAccessPolicy.swift
python3 scripts/verify_antifake_bypass_off.py
```

Re-archive and re-test Hub with **real Premium** account.

---

## XCUITest (simulator)

```bash
xcodebuild test \
  -project ALADDIN.xcodeproj \
  -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 13 Pro Max 15.2' \
  -only-testing:ALADDINUITests/AntifakeHubTabsUITests
```

Simulator does **not** satisfy D-04 (incoming call UI).
