# ALADDIN iOS Agent Workspace Rule

All AI/ML agents working on ALADDIN iOS mobile app tasks must use this repository as the only project root:

`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

Before any edits, commits, rebases, or pushes, verify:

1. `git rev-parse --show-toplevel`
2. `git branch --show-current`
3. `git status --short`

If the git top-level path is different, stop and switch to this repository first.

## Onboarding: preserve layout when adding Aladdin story art

When onboarding work adds **only** colorful hero illustrations (`OnboardingHero_00`…`07`):

- Do **not** refactor `languageStepView` / `onboardingPage` or `Spacing.*` unless the task explicitly asks for layout changes.
- After hero/asset or readability-gradient changes, **smoke all** `currentPage` **0…N** and confirm text positions match the pre-art baseline.
- Full policy: **`docs/ONBOARDING_MAIN_HERO_HANDOFF.md` §1.8** (Russian; acceptance §8).

## Onboarding Figma: mandatory QA gate per screen

After each `OB_00`…`OB_07` (and Main) Figma frame:

1. **`hero-0N-figma`** — real PNG in layer `OnboardingHero_0N` (not solid-color placeholder).
2. Run **`docs/ONBOARDING_MASTER_IMPLEMENTATION_PLAN.md` §4.1** (G1–G6), including **`get_screenshot`** on the hero node only.
3. Only then mark **`ob-0N-qa`** done and proceed to the next screen.

Master plan: **`docs/ONBOARDING_MASTER_IMPLEMENTATION_PLAN.md`**. Never report «100%» without passing the gate.
