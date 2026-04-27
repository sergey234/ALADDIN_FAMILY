# Phase 2 Content Freshness SLA Report

- generated_at: `2026-04-27T18:07:06.167434+00:00`
- checks: `9`
- failed: `0`
- category_level_failed: `0`
- item_level_failed: `0`

| ID | Level | Status | Description | Details |
|---|---|---|---|---|
| P2F-FILE-SLA | category | PASS | SLA policy document exists | docs/PHASE2_CONTENT_FRESHNESS_SLA.md |
| P2F-FILE-SEED | item | PASS | Seed provider exists | Core/Content/Seed/ContentSeedProvider.swift |
| P2F-POLICY-CORE | category | PASS | SLA policy includes cadence and thresholds | cadence + warning/fail thresholds |
| P2F-POLICY-FALLBACK | category | PASS | SLA includes emergency fallback window | fallback <=24h |
| P2F-SCOPE-TOP | category | PASS | All top categories are included in SLA scope | scope_count=8/8 |
| P2F-CONTRACT-META | category | PASS | Metadata contract fields are declared | metadata contract |
| P2F-ITEM-MIN | item | PASS | Top categories satisfy minimum item baseline | required>=3 each top category |
| P2F-ITEM-NONEMPTY | item | PASS | Top-category items are non-empty | items=24 |
| P2F-ITEM-NOPLACEHOLDER | item | PASS | Top-category items have no placeholder tokens | blocked: todo/tbd/placeholder/replace_me/fixme/lorem |
