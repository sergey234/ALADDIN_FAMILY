# App Store Review Notes — Antifake (A-07)

**App:** ALADDIN iOS · Build 233+  
**Feature:** Network Protection → «Проверить подлинность» (Antifake Hub)

## What reviewers should test

1. Open **Network Protection** → **Проверить подлинность**.
2. **Text tab:** paste suspicious Russian/English text → **Проверить** → verdict card (likely fake / uncertain / likely real) with disclaimer.
3. **Share extension:** Safari → Share → «Проверить в ALADDIN» → opens Hub with prefilled check.
4. **Call Directory:** tap **Как включить** → follow Settings path → enable **ALADDIN** extension → **Синхронизировать** (requires Premium test account).
5. **Post-call:** after a cellular call, local notification may appear → tap → Hub **Звонок** tab with upload prompt (no background call recording).

## P1 limits (Review must not miss)

| Limit | Implementation |
|-------|----------------|
| Call Directory **DB only** | `/api/antifake/call-directory` from PostgreSQL; no hardcoded seed in API (C-03) |
| **No PSTN** intercept | No VoIP/CallKit provider; user uploads recordings only |
| **`uncertain` valid** | Verdict card shows uncertain + disclaimer; not marketed as 100% |
| Ingest ≥ **0.72** | `antifake_fraud_ingest.MIN_CONFIDENCE_FOR_INGEST = 0.72` for auto DB ingest |
| Media **probe ≠ full ML** | UI copy A-15: audio/video probe footnotes; badge «Quick check» vs «Checked by AI» |

## Honest claims (Guideline 2.1)

| We say | Reality |
|--------|---------|
| Check text, links, audio, video **on user action** | Yes — no background scanning of SMS/messengers |
| Label known scam numbers on incoming calls | Call Directory extension + synced fraud DB |
| Analyze call **recordings after** the call | User uploads file; iOS does not expose live call audio to third-party apps |
| AI assessment, not legal proof | Verdict card shows disclaimer inline |

## What we do **not** claim

- Real-time listening to all phone calls
- Automatic hang-up based on AI alone
- Intercepting FaceTime / WhatsApp / Zoom
- 100% accuracy — «uncertain» is a valid outcome

## Premium / test account

- Antifake Hub requires Premium (Family tariff). Provide review credentials or enable `ANTIFAKE_ALLOW_FREE=1` on staging only.
- QA builds may ship with `bypassPremiumGate = true` — **production release sets it to `false`** (Phase 3 G-03).

## Entitlements

- **Call Directory** (`com.apple.developer.call-directory`) — identification labels only; blocking list empty by default.
- **App Groups** — share extension payload + Call Directory JSON store.
- No VoIP, no CallKit provider, no microphone background mode for call interception.

## Privacy

- `PrivacyInfo.xcprivacy` declares phone number (Call Directory), audio, photos/video for user-initiated checks.
- Media uploads TTL ~15 min on server; phone numbers hashed in server logs.

## Support contact

Telegram: @AladdinchatAI_bot · In-app Support / FAQ entries: `faq_antifake_*`
