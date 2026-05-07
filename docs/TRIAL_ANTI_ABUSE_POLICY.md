# Trial Anti-Abuse Policy (Privacy-Safe)

## Goal

Prevent repeated 14-day trial abuse without storing personal data (no email, phone, name).

## Data minimization principles

- No PII in anti-abuse pipeline.
- Use only technical risk signals.
- Prefer irreversible hashes.
- Keep short retention windows for velocity checks.

## Client signals (iOS)

Sent in `POST /api/auth/register-device-trial` under `anti_abuse`:

- `install_fingerprint_hash` (salted SHA-256, rotating salt)
- `velocity_1h` (local attempts in last hour)
- `velocity_24h` (local attempts in last 24h)
- `cooldown_seconds` (local cooldown active or `0`)
- `app_version`
- `os_version`
- `risk_version`

## Server decision policy (current)

Trial is denied (fallback to free) if one of these is true:

- `cooldown_seconds > 0`
- `velocity_1h >= 3`
- `velocity_24h >= 8`

When denied, backend returns a valid subscription payload with `free` level.

## Security/privacy notes

- Signals are technical and non-personal.
- Hashes are one-way and salted on client.
- No user identity attributes required.

## Next hardening (recommended)

- Add DeviceCheck/App Attest verdict token verification on backend.
- Add TTL-based server risk store for hashed signals.
- Add rotating server salt for risk-linking windows.
- Add anomaly challenge step before granting trial for medium-risk events.
- Add audit counters and dashboard (denied vs granted, false positives).

