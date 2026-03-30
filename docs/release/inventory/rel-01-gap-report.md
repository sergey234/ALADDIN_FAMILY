# rel-01 gap report (auto)

- total endpoints discovered: **381**
- distinct components/tags discovered: **45**
- verified now: **7**
- pending verify: **374**

## Gap to target 42/138
- target components: 42; discovered tags/components: 45
- target security functions: 138; discovered endpoints: 381
- Note: endpoints != security functions 1:1. Manual mapping is required in rel-01 finalization.

## Next actions
- Map endpoint rows to canonical 42 components and 138 function IDs.
- Fill db_source/status/auth strictly from runtime verification.
- Mark release blockers where status != verified for critical flows.
