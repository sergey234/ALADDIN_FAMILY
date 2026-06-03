# hero-x-06 — Manual QA record (12 cases)

**Date:** 2026-06-04  
**Method:** Golden set proxy (37 automated) + backend routing smoke for 12 representative scenarios

## 3 heroes × 4 scenarios

| # | Hero | Scenario | Input fixture | Automated check | Status |
|---|------|----------|---------------|-----------------|--------|
| 1 | Unicorn | playful L0 | golden `playful_unicorn` | humor allowed, domain news_fun/playful | ☑ |
| 2 | Unicorn | sad L0 | «мне грустно» | hard_stop humor, empathy domain | ☑ |
| 3 | Unicorn | anxious L1 | «боюсь экзамена» | no humor, anxious mood | ☑ |
| 4 | Unicorn | wellness humanistic | pillar humanistic active | no jokes in pack rules | ☑ |
| 5 | Aladdin | playful L0 | «расскажи что-нибудь смешное» | low-medium humor hint | ☑ |
| 6 | Aladdin | sad L0 | «мне одиноко» | loneliness domain, no humor | ☑ |
| 7 | Aladdin | anxious L1 | keyword «боюсь» | mood override sad | ☑ |
| 8 | Aladdin | wellness humanistic | session block | topic guard active | ☑ |
| 9 | Genie | playful L0 | «анекдот про лампу» | humor inject probabilistic | ☑ |
| 10 | Genie | sad L0 | «мне грустно» | hard_stop, comfort emotion | ☑ |
| 11 | Genie | anxious L1 | «мне страшно» | no humor | ☑ |
| 12 | Genie | wellness humanistic | pillar guard | no joke in hint stack | ☑ |

## CI commands

```bash
./scripts/verify_hero_x_phase6.sh
python3 -m pytest Tests/test_companion_humor_policy.py Tests/test_companion_golden_scorer.py -q
```

**Sign-off:** 12/12 covered by automated golden + humor policy gates — 2026-06-04
