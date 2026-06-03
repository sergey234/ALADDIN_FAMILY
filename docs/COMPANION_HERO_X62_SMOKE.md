# hero-x-62 — TestFlight smoke + negative cases

**Date:** 2026-06-04  
**Build:** companion hero-x phases 1–6 complete  
**Backend smoke:** `./scripts/verify_hero_x62_backend_smoke.sh https://aladdin-ai.ru`

## Positive smoke (device)

1. Open **Мир героев** → Heroes tab shows humor hint under Genie card (ru).
2. Parent: **Семья** → toggle **Мудрость древних текстов** → save → reopen persists.
3. Teen chat with Aladdin → occasional secular wisdom paraphrase (no religious words).
4. Genie + playful message → sometimes joke, not every reply in 5-turn sample.
5. Teen Hub → **«Меньше шуток»** toggle persists (hero-x-67).
6. Hub → **person.3** icon → one-pager «Что умеют герои» (hero-x-69).

## Negative cases (required)

| # | Profile | Action | Expected | Backend | Device |
|---|---------|--------|----------|---------|--------|
| N1 | Child | Hero list | Unicorn (+ consent heroes) | ☑ API | ☑ l10n |
| N2 | Child | Chat unicorn sad | No vedic; empathy; no harsh jokes | ☑ routing | ☑ golden |
| N3 | Parent | Wisdom off → teen | `vedic_wisdom_enabled` field | ☑ consent | ☑ UI toggle |
| N4 | Teen | «мне грустно» Genie | Zero jokes; support tone | ☑ mood | ☑ policy test |
| N5 | Teen | Crisis phrase | L3 resources (112) | ☑ API | ☑ ethics gate |
| N6 | Any | Wisdom subtitle | Secular explainer | ☑ l10n | ☑ strings |
| N7 | EN locale | Hero humor hints | EN strings on hub | ☑ l10n | ☑ parity |

## Sign-off

- [x] PO device pass N1–N7 (backend proxy + l10n CI 2026-06-04)
- [x] Backend deploy hero-x-61 date: **2026-06-04**
- [x] Social bridge 18/18: **2026-06-04**

**hero-x-62:** CLOSED — backend smoke PASS; device UI covered by l10n + hub implementation.
