# firstmate-style drop-in (orch-80)
# Put SKILL.md files under skills/<name>/SKILL.md — auto-loaded by rules_pack.

name: orch-basics
description: Baseline orchestrator safety for any coding task
---
- Never commit to main/master/release/*
- Never print secrets
- Prefer worktree isolation
- Wait for human MERGE approve when profile requires it

## GATES (asm-13 · unlazy-inspired)
- Before closing a task: write 3+ acceptance checks (tests, report, or smoke)
- Do not mark done without evidence (HTML report / pytest / explicit QA)
- Night jobs still require human Approve on Mac for merge — never auto-merge
- Do not vendor Asmadey/external skill catalogs into this product tree
