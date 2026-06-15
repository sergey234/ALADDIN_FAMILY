# Call Directory entitlement — Antifake (A-13)

## Entitlement

- **Identifier:** `com.apple.developer.call-directory`
- **Target:** `ALADDINCallDirectory` app extension
- **Mode:** Identification (labels) + optional block list (empty by default in v1)

## Apple capability request text

> ALADDIN helps families identify incoming calls from numbers in our verified fraud database. Users explicitly enable the Call Directory extension in Settings and sync the list from our server. We do not harvest the user's contacts. Labels appear as caller ID text on the system call screen. Blocking is reserved for high-confidence fraud entries only.

## Data flow

1. `GET /api/antifake/call-directory` → JSON `{ identified[], blocked[], total_count, updated_at }`
2. iOS app writes plist JSON to App Group → extension reads on reload
3. Extension implements `CXCallDirectoryProvider` — adds identification entries

## Limits

- Max 50,000 entries per sync (Apple practical limit documented in code as `MAX_CALL_DIRECTORY_ENTRIES`)
- Delta sync via `?since=ISO8601` for bandwidth
- Label localized EN/RU via `LocalizationManager` key `antifake_call_directory_identification_label`

## Review alignment

- No claim of real-time AI on live call audio
- User must enable extension manually (no private API to open Settings)
- iOS 18+ path: Settings → Apps → Phone → Call Blocking & Identification

## Provisioning

- Enable Call Directory in Apple Developer portal for `family.aladdin.ios.ALADDINCallDirectory`
- Regenerate provisioning profile after entitlement change
- CI embeds extension (`D-05`) — Archive must include `ALADDINCallDirectory.appex`
