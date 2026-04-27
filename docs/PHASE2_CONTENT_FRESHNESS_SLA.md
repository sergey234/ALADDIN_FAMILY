# Phase 2 Content Freshness SLA

Task ID: `P2-407`

## Goal

Guarantee regular refresh cadence for top child content categories so engagement quality does not degrade from stale content.

## Top Categories Scope

- `child_interface_category_games`
- `child_interface_category_study`
- `child_interface_category_safety`
- `child_interface_category_cartoons`
- `child_interface_category_programming`
- `child_interface_category_social`
- `child_interface_category_music`
- `child_interface_category_education`

## SLA Policy

- **Refresh cadence:** at least once every `14` days for each top category.
- **Hard warning threshold:** `10` days since last refresh.
- **Hard fail threshold:** `14` days since last refresh.
- **Emergency fallback:** if refresh misses threshold, trigger expedited content patch within `24h`.

## Metadata Contract

Each top category should carry:
- `category_id`
- `freshness_tier` (`top`)
- `last_refresh_at`
- `refresh_due_at`
- `owner`

## Operational Checks

Category-level:
- all top categories are declared in SLA scope;
- each category has owner and cadence.

Item-level:
- each top category has at least `3` active seed items;
- item titles are non-empty and non-placeholder;
- refresh windows are computed from `last_refresh_at`.

## Acceptance Rule

SLA framework is valid when:
- SLA policy document exists and includes cadence/threshold/fallback;
- smoke check passes with `0` failed checks;
- report artifacts are generated in `docs/`.
