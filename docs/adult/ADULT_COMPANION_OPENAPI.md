# A-01 — OpenAPI sketch: `app_id=aladdin_adult`

Companion platform endpoints mirror Family (`/api/ai/companion/*`) with JWT claims:

| Claim | Family | Adult |
|-------|--------|-------|
| `app_id` | `aladdin_family` | `aladdin_adult` |
| `content_policy` | `family_pg13` | `adult_18` (requires `age_verified`) |
| `age_band` | child / teen / parent / senior | `adult_app` |

## Auth

`Authorization: Bearer <access_token>` with enriched claims from `jwt_claims.enrich_access_token_data`.

## Core routes (shared router)

- `POST /api/ai/companion/chat` — same body; policy engine gates NSFW.
- `GET /api/ai/companion/capabilities` — `media_gen.video_gen` enabled for verified adult.
- `GET /api/ai/companion/cogs` — unit economics per user.

## Policy

See `policy_engine.evaluate_request_policy` and tests in `Tests/test_adult_companion_policy.py`.
