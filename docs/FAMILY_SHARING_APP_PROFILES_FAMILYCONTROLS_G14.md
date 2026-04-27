# G14: Family Sharing vs App Profiles vs FamilyControls

## Purpose

This note separates three layers that are often mixed in support requests and QA reports.

## 1) Apple Family Sharing (iOS / Apple ID layer)

- Scope: purchases, subscriptions, Ask to Buy, and Apple account family ownership.
- Controlled by: system settings and Apple account relationships.
- Important: this does **not** grant ALADDIN in-app role permissions by itself.

## 2) ALADDIN App Profiles (application role layer)

- Scope: who can manage family roster, edit limits, and apply sensitive parental actions inside ALADDIN.
- Roles: `parent`, `elderly`, `child`, `teenager`.
- Policy source: `FamilyAccessPolicy`.
- Practical rule:
  - `parent` / `elderly` can manage app profiles and family settings.
  - only `parent` can manage Family Sharing related app actions.

## 3) FamilyControls / Screen Time (system control framework layer)

- Scope: iOS runtime enforcement using `AuthorizationCenter`, `ManagedSettings`, `DeviceActivity`.
- Used by ALADDIN when system pipeline is available.
- If unavailable, ALADDIN keeps server-side fallback policies active.
- Important: system FamilyControls availability does not disable ALADDIN role checks.

## Support flow (recommended)

1. Confirm role in ALADDIN Family roster.
2. Confirm Family Sharing state in iOS settings.
3. Confirm FamilyControls readiness banner in parental UI.
4. If conflicts appear, parent selects merge strategy (`Use server` / `Keep local`) from Family conflict banner.

## UI entry points added for Wave 6

- `Screens/02_FamilyScreen.swift`:
  - help button: **Family roles & profiles**
  - help button: **Family Controls & Screen Time**
  - parent-only conflict resolution banner for roster/profile merge strategy.
- `Screens/07_ParentalControlScreen.swift`:
  - concise boundary hint banner with quick guide action.
