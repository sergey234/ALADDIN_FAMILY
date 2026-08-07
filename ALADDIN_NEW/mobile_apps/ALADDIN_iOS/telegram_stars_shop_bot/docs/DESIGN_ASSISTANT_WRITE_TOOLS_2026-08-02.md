# DESIGN ONLY — Assistant write-tools (refund / reprovision)

**Status:** draft · **MUST NOT SHIP** without separate ТЗ + admin gate + security review  
**Date:** 2026-08-02 · Plan `ds-p2-02`  
**Deny list:** `tools/deer-flow-sandbox/DENY.yaml` → `deny_assistant_tools`  
**Current prod:** `ALLOWED_TOOLS` in `bot/assistant/tools.py` = **read-only** + `open_human_ticket`

---

## 1. Problem

Stuck / failed flows today:

| Case | Today | Risk if LLM writes |
|------|-------|-------------------|
| Stars paid, ApiFragment 502 | operator / worker retry | double fulfill |
| VPN paid, no sub | `/admin_vpn_finalize`, ops | wrong user link |
| User wants money back | human ticket + policy | chargeback / fraud |
| VPN revoke/extend | `/admin_vpn_revoke` / `_extend` | free access abuse |

Goal of a future design: **narrow, gated tools** so support is faster — **not** «LLM freely refunds».

---

## 2. Non-goals (explicit)

- No auto-refund from chat without admin confirm.
- No tool that returns raw `/sub/` or peer keys to the model.
- No Fragment create-order from assistant (fulfill stays worker/admin).
- No shipping this design into `ALLOWED_TOOLS` in the same PR as the design doc.

---

## 3. Proposed tools (names only — denied in DENY.yaml)

| Tool | Intent | Actor |
|------|--------|-------|
| `refund_order` | Mark order refunded / trigger PSP path | admin confirm |
| `reprovision_vpn` | Re-run provision for **own** stuck VPN order | admin or dual-control |
| `revoke_vpn` | Disable VPN for user | admin only |
| `extend_vpn` | Extend `paid_until` | admin only |
| `force_complete_order` | paid→completed after manual verify | admin only |
| `admin_fulfill` | Manual Stars/Premium fulfill | admin only |

User-facing assistant may **propose** «создать заявку на refund #N» → ticket; execution = admin command or future gated API.

---

## 4. Gates (must all pass before any ship)

1. **Feature flag:** `ASSISTANT_WRITE_TOOLS_ENABLED=false` default.  
2. **Role:** only `ADMIN_IDS` (or separate `ASSISTANT_WRITE_ADMIN_IDS`).  
3. **Confirm step:** Telegram inline «Confirm / Cancel» with order_id + amount + kind; expire 5 min.  
4. **Idempotency:** store `assistant_write_actions(id, tool, order_id, status, actor, created_at)`; second call no-ops.  
5. **Audit:** every call → admin chat + DB row; never silent.  
6. **Rate limit:** ≤ N write actions / admin / day.  
7. **Scope:** tool receives `telegram_user_id` from update only (same as read tools); cannot target arbitrary users unless admin tool + explicit target id in confirm payload.  
8. **Money:** refund path must call existing PSP/admin flow — no «set status=refunded» alone if payment provider needs reverse.  
9. **VPN:** reprovision must reuse vpn-api HMAC contracts; no inventing sub URLs in LLM text.  
10. **Tests:** unit deny for non-admin; integration dry-run; no live Contabo in CI.

---

## 5. Suggested state machine (refund example)

```
user asks refund
  → escalate / open_human_ticket (today)  ✅ keep
  → [FUTURE] admin sees ticket + button "Prepare refund #id"
  → confirm card: amount, provider, reason
  → on Confirm: refund_order tool → PSP/admin service
  → user notified; assistant still cannot skip confirm
```

Reprovision:

```
stuck VPN paid
  → triage script (read-only)  ✅ exists
  → [FUTURE] admin "Reprovision #id" confirm
  → reprovision_vpn → existing finalize/provision code path
  → never from user chat directly
```

---

## 6. Mapping to existing admin commands

| Future tool | Existing ops (keep as SSOT until ship) |
|-------------|----------------------------------------|
| `reprovision_vpn` / finalize | `/admin_vpn_finalize` |
| `revoke_vpn` | `/admin_vpn_revoke` |
| `extend_vpn` | `/admin_vpn_extend` |
| Stars/Premium fulfill | admin order FF / auto-fulfill worker |
| Refund | support + PSP webhooks (e.g. cardlink refund) — **no** assistant entry yet |

Prefer **wrapping** these paths over reimplementing in orchestrator.

---

## 7. Prompt / policy changes (when ship)

- SYSTEM: «Write-tools only after Confirm; never invent success.»  
- Validator: reject assistant text claiming «возврат выполнен» without `assistant_write_actions.status=done`.  
- Gold answers T9 stay: «не обещаю возврат — человек».

---

## 8. Rollout phases (future ТЗ)

| Phase | Scope |
|-------|-------|
| A | Design review (this doc) — **current** |
| B | DB table + flag + admin-only dry-run logging (no money) |
| C | `reprovision_vpn` wrap `/admin_vpn_finalize` for admins in assistant UI |
| D | Refund — only after PSP owner sign-off |
| E | User-visible status; still no user-triggered money movement |

---

## 9. Acceptance for «ship» (not this PR)

- [ ] Written ТЗ signed by owner  
- [ ] `deny_assistant_tools` removed **only** for tools that shipped, one by one  
- [ ] `test_assistant_*` prove non-admin cannot call  
- [ ] Contabo smoke with `ASSISTANT_WRITE_TOOLS_ENABLED=0` default after deploy  
- [ ] Guardrails checklist still green  

---

## 10. STOP

Do **not** add these names to `ALLOWED_TOOLS` in the same change set as product features.  
Do **not** implement refund/reprovision from `/goal` deer-flow docs.  
If an agent starts coding write-tools: point here and refuse without ТЗ.
