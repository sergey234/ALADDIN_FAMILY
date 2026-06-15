# App Store Privacy — Antifake mapping (G-05)

**Source of truth:** `PrivacyInfo.xcprivacy` (main app) + sections in `18_PrivacyPolicyScreen.swift`.

Use this when filling **App Privacy** in App Store Connect for build with Antifake Hub.

---

## Data collected (App Store questionnaire)

| App Store category | Collected? | Linked to user? | Tracking? | Purpose | Privacy manifest |
|--------------------|------------|-----------------|-----------|---------|------------------|
| User Content (other) | Yes | No | No | App Functionality | `NSPrivacyCollectedDataTypeOtherUserContent` |
| Phone Number | Yes | No | No | App Functionality | `NSPrivacyCollectedDataTypePhoneNumber` |
| Audio | Yes | No | No | App Functionality | `NSPrivacyCollectedDataTypeAudioData` |
| Photos or Videos | Yes | No | No | App Functionality | `NSPrivacyCollectedDataTypePhotosorVideos` |
| Contacts | **No** | — | — | — | Not declared (G-07) |

---

## What to say in review / privacy nutrition

- Text/links/media sent **only after user taps Check or Share**.
- Phone numbers: optional caller ID fields + Call Directory sync; **hashed in server logs**.
- Audio/video: temporary server storage (~15 min), then deleted (B-08 cron).
- **No** address-book upload for antifake.
- Call Directory extension: reads synced snapshot from App Group, not live call audio.

---

## Required APIs (Privacy Manifest)

| API | Reason |
|-----|--------|
| User Defaults | CA92.1 — app settings, Call Directory snapshot keys |
| File timestamp | C617.1 — media upload metadata |

---

## Extensions

| Target | PrivacyInfo | Notes |
|--------|-------------|-------|
| ALADDIN (main) | `PrivacyInfo.xcprivacy` | Hub uploads |
| ALADDINCallDirectory | `ALADDINCallDirectory/PrivacyInfo.xcprivacy` | Phone numbers from App Group |
| ALADDINAntifakeShare | `ALADDINAntifakeShare/PrivacyInfo.xcprivacy` | Share extension handoff |

**Verify:** `python3 scripts/verify_antifake_release_readiness.py` (N-01 + G-05 files).
