# Checkout captcha auto-continue — TODO Tracker

**SSOT Cursor TODO** · ids `cc-*`  
**План:** `PLAN_CHECKOUT_CAPTCHA_AUTO_CONTINUE_2026-07-14.md`

**Синхрон с Cursor (2026-07-14):** код+unit+arch ✅ · smoke/deploy/E2E — **конец** (один Contabo с `br-a4`).

- [x] `cc-00-canon`
- [x] `cc-00-copy`
- [x] `cc-1-extract-finalize`
- [x] `cc-1-order-submit-uses-helper`
- [x] `cc-1-keep-ttl`
- [x] `cc-2-captcha-handler-fsm`
- [x] `cc-2-auto-finalize`
- [x] `cc-2-delete-captcha-msg`
- [x] `cc-2-stale-session`
- [x] `cc-2-wrong-answer`
- [x] `cc-3-fsm-flag`
- [x] `cc-3-clear-flag`
- [x] `cc-3-interval-cap`
- [x] `cc-4-test-auto-continue`
- [x] `cc-4-test-fail-no-order`
- [x] `cc-4-test-ttl-skip`
- [x] `cc-4-arch-doc` — `BOT_ARCHITECTURE_REFERENCE_RU.md` § капча → `finalize_checkout_order`
- [ ] `cc-4-smoke` — конец (бот)
- [x] `cc-5-deploy` — конец
- [ ] `cc-5-e2e` — конец

Соседи: `br-*`, `rb-*`, `pf-*`, `ha-*` — не удалять из Cursor.
