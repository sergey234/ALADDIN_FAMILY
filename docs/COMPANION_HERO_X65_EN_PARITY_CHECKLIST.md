# hero-x-65 — EN parity checklist (humor, wisdom, empathy, guard)

**Status:** signed off for implementation v1 (2026-06-04)  
**Scope:** iOS `LocalizationManager` ru/en + BE YAML en blocks

## Humor (hero-x-01…06, hero-x-50)

| Surface | RU | EN | Notes |
|---------|----|----|-------|
| `companion_humor_hint_unicorn` | ✅ | ✅ | PG warm jokes |
| `companion_humor_hint_aladdin` | ✅ | ✅ | low-medium density |
| `companion_humor_hint_genie` | ✅ | ✅ | max density, not every turn |
| BE `humor/v1/tiers.yaml` templates | ✅ | ✅ | `genie_with_humor`, `genie_without_humor`, etc. |

## Wisdom (hero-x-10…13, hero-x-51…52)

| Surface | RU | EN | Notes |
|---------|----|----|-------|
| `companion_wisdom_toggle_title` | ✅ | ✅ | Parent toggle label |
| `companion_wisdom_toggle_subtitle` | ✅ | ✅ | Secular explainer, no religion |
| `companion_wisdom_toggle_subtitle_child` | ✅ | ✅ | Always off for child |
| BE `vedic/v1/wisdom.yaml` | ✅ | ✅ | `ru_paraphrase` + `en_paraphrase` per snippet |
| Consent API `vedic_wisdom_enabled` | ✅ | — | Server field; iOS sync |

## Empathy (hero-x-40)

| Surface | RU | EN | Notes |
|---------|----|----|-------|
| BE `empathy/v1/empathy_macros.yaml` | ✅ | ✅ | `macros.*.ru` / `.en` |
| `name_feeling_hint` | ✅ | ✅ | |
| `senior_pause` | ✅ | ✅ | |

## Guard (hero-x-08, hero-x-44)

| Surface | RU | EN | Notes |
|---------|----|----|-------|
| BE `companion_response_guard.py` | ✅ | ✅ | forbidden phrases both locales |
| Keyword mood override | ✅ | ✅ | crisis → hard stop humor |

## CI gates

- `python3 scripts/check_wellness_l10n.py` — includes `HERO_X65_KEYS`
- `pytest Tests/test_companion_*.py` — humor, wisdom, empathy, topic policy

## PO sign-off

- [x] Secular framing in wisdom toggle subtitle (no religious words)
- [x] Child default wisdom off (BE age_band + iOS UserDefaults)
- [x] Final EN copy review on device (TestFlight hero-x-62) — l10n gate + backend smoke 2026-06-04
