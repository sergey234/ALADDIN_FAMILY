# P3-05 — Android companion (out of iOS repo)

Parity checklist when Android app starts:

- `GET /api/ai/companion/capabilities`
- `POST /api/ai/companion/chat` with `chat_mode`, `attachments`
- Voice: same ephemeral token + WS as iOS
- Entry: Family hub card equivalent to «Друзья»

Backend contracts are platform-agnostic; reuse OpenAPI from `docs/adult/ADULT_COMPANION_OPENAPI.md`.
