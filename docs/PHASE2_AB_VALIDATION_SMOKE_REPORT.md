# Phase 2 A/B Validation Smoke Report

- generated_at: `2026-04-27T13:09:10.050759+00:00`
- checks: `8`
- failed: `0`
- category_level_failed: `0`
- item_level_failed: `0`

| ID | Level | Status | Description | Details |
|---|---|---|---|---|
| P2AB-FILE-FRAMEWORK | category | PASS | A/B framework document exists | docs/PHASE2_AB_VALIDATION_FRAMEWORK.md |
| P2AB-VARIANTS-CORE | category | PASS | Core format variants are declared (short/long, text/visual) | tokens: short,long,text,visual |
| P2AB-VARIANTS-GROUPS | category | PASS | All experiment groups A1/A2/B1/B2 are declared | groups: A1,A2,B1,B2 |
| P2AB-ASSIGNMENT | category | PASS | Deterministic assignment policy is declared | deterministic assignment contract |
| P2AB-TELEMETRY | item | PASS | Telemetry contract fields are declared | required telemetry fields |
| P2AB-QA-CATEGORY | category | PASS | Category-level QA matrix rules are present | category-level QA rules |
| P2AB-QA-ITEM | item | PASS | Item-level QA matrix rules are present | item-level QA rules |
| P2AB-ACCEPTANCE | category | PASS | Acceptance rule for framework validity is defined | framework acceptance criteria |
