# Budget Policy

**Id:** `orch-05-budget-policy`

## Defaults (можно переопределить в `config/budget.yaml`)

| Limit | Default | Action |
|-------|---------|--------|
| Soft warn / day | $15 | Notify UI / log WARN |
| Hard cap / day | $40 | **Kill switch** — stop new spawns |
| Soft warn / week | $80 | Notify |
| Hard cap / week | $200 | Kill switch until next week or owner GO |
| Max concurrent agents | 4 | Reject spawn |
| Max spawn depth | 3 | Reject spawn |

## Routing (cost-aware)

1. **Draft / explore** → Ollama / **Bonsai 2 (local, после GO)** / NIM / cheap API via CLIProxyAPI  
2. **Implement** → Codex or Claude Code (subscription preferred over pay-as-you-go)  
3. **Review / security** → strongest available (Claude / Codex)  
4. Never send review to cheapest-only if policy `require_premium_review: true`

### Bonsai 2 / local LLM (Pilot stack Compute)

- Канон: `docs/ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md` · skill `@aladdin-local-llm`  
- **Разрешено:** draft, explore, cheap night, offline brainstorm  
- **Запрещено:** review, security, parental decisions, merge Approve «только local»  
- Install runtime/весов — только явный **GO владельца**; веса **не** в git  
- Не путать с product LLM в iOS app (отдельное ТЗ)

## Kill switch

- Triggered by BudgetTracker when hard cap hit or manual `orch kill`.
- Persists in SessionStore until cleared by human.
- Audit event: `budget.kill_switch`.

## Owner GO

Поднятие hard cap или temporary bypass — только явный GO владельца (не агент).
