# Phase 8.1 Validation (Content Correctness + Device Matrix)

Scope of this pass:

- `Track A · Phase 8` — Тестирование всего контента на корректность
- `Track A · Phase 8` — Валидация работы на разных устройствах

## Smoke command

Run:

`python3 scripts/phase8_content_device_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it checks

1. **Content correctness**
   - Runs `scripts/content_contract_smoke.py`
   - Verifies `/api/health`, OpenAPI routes for content manifest/delta,
     and response shape contracts for manifest + delta payloads.

2. **Device validation**
   - Runs simulator build for iPhone destination (`id=B98F9663-BB22-481C-B4C4-6D7E88F1E017`)
   - Runs simulator build for iPad destination (`id=02B945E1-9B6C-4F62-8DE4-E1544ABF2783`)
   - Requires `** BUILD SUCCEEDED **` marker for each.

## Notes

- This smoke is deterministic and reproducible in CI/local shell.
- Functional UI/manual QA across broader device matrix remains covered by open tasks in Phase 8/9.
