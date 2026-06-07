---
name: aladdin-figma-ios-sync
description: Full Figma ↔ iOS onboarding sync (SYNC-H+T). Use when user asks to sync onboarding with Figma or apply OB_* frames.
origin: ALADDIN
---

# Figma ↔ iOS Onboarding Sync

Canonical rule: `.cursor/rules/onboarding-figma-ios-sync-mandatory.mdc`  
Figma MCP: load skill `figma-use` before `use_figma`.

## Definition of Done (not done until all)

1. `get_metadata` on frame `OB_*`
2. Update `Screens/14_OnboardingScreen.swift` + `scripts/verify_onboarding_sync_01_03.py`
3. Upload hero to Figma layer `*:54` via MCP
4. `python3 scripts/verify_onboarding_sync_01_03.py` → PASS
5. User report: layer table + **Figma upload: yes/no**

**PASS verify ≠ sync complete.**

Read-only Figma OB_00–07: `.cursor/rules/companion-figma-onboarding-untouched.mdc`
