# Wellness Escalation Ladder L0–L3

> **Code:** `wellness_escalation.py` (p1-20) · **Ethics:** `companion_ethics.py` (L3 overrides all)

| Level | Name | Triggers | User-visible | System |
|-------|------|----------|--------------|--------|
| L0 | Self-help | Default chat | 4 pillars, exercises | `primary_pillar` session |
| L1 | Monitor | 3 days low mood / no check-in | PHQ-lite offer | `wellness_triggers.py` |
| L2 | Specialist | PHQ-lite ≥10; GAD severe; trauma/EMDR keywords (teen+) | Referral sheet | `wellness_referral.py` |
| L3 | Crisis | Self-harm/suicide patterns | 112 + static message | `evaluate_companion_ethics` — **no LLM** |

## L3 (crisis)

Use existing `companion_ethics.py` response; block Jung/deep mode and witty genie tone.

## L2 referral (RU)

- **112** — экстренная помощь  
- **8-800-2000-122** — телефон доверия  
- **051** — МЧС психологическая помощь  

Copy: «ALADDIN — цифровой друг, не заменяет очного специалиста.»

## API (Phase 1)

`GET /api/wellness/escalation/level` → `{ "level", "reason", "actions": [] }`
