# hero-x-64 — Companion persona metrics

Events recorded via `record_hero_persona_metric()` → `ai_history_store` (no raw message text).

| Event | When | Extra fields |
|-------|------|--------------|
| `humor_injected` | `should_inject_humor()` true for turn | `domain`, `mood` |
| `wisdom_used` | `[WISDOM v1]` block injected | `domain`, `mood` |
| `guard_triggered` | `apply_companion_response_guard` replaced reply | `reason`, `guard=free_chat` |

## Log grep (prod)

```bash
# analytics rows (resolved_by=companion_metrics)
grep 'companion_metric:humor_injected' /var/log/aladdin-backend/*.log
grep 'companion_metric:wisdom_used' /var/log/aladdin-backend/*.log
grep 'companion_metric:guard_triggered' /var/log/aladdin-backend/*.log
grep 'companion_forbidden_phrase' /var/log/aladdin-backend/*.log
```

## Tuning

- High `humor_injected` + low satisfaction → lower genie frequency in `humor/v1/tiers.yaml`
- High `guard_triggered` → review LLM prompt / post-moderation
- `wisdom_used` near cap → expected (1/5 turns)
