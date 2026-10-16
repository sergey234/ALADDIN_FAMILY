# Screen Time WAVE 2 — Task Registry (`st-*`)

**SSOT исполнения:** `docs/AppStore/SCREEN_TIME_WAVE2_FULL_UI_MAP_AND_CHECKLIST_2026-10-16_RU.md` (PROD-100)  
**Правило трекинга:** обновлять статусы здесь и в Cursor TODO через **merge-only** (`st-*`). Не заменять весь список короткой пачкой.

**Стоп:** код W2-B…E только после фразы владельца **`FC Assigned — GO на WAVE 2`**.

| ID | Фаза | Задача | Статус |
|----|------|--------|--------|
| st-meta | — | PROD-100 план + registry | ✅ |
| st-A1 | A | Identifiers FC + App Groups | ✅ |
| st-A2 | A | Profiles 4/4 на Mac | ✅ |
| st-A3 | A | FC Distribution Assigned | ✅ |
| st-A4 | A | App Approved | ✅ |
| st-A5 | A | Фраза GO на WAVE 2 | ✅ |
| st-B1 | B | Entitlement family-controls | ✅ |
| st-B2 | B | Targets Monitor/Report/ShieldConfig embed | ✅ |
| st-B3 | B | App Group на ST targets | ✅ |
| st-B4 | B | ScreenTimeUsageStore schema | ✅ |
| st-B5 | B | pbx новые swift в git | ✅ |
| st-B6 | B | Debug readiness extension_missing | 🚧 |
| st-B7 | B | Shield Action не в v1 (backlog ok) | ✅ |
| st-C1 | C | Auth UI child + guided entry | ✅ |
| st-C2 | C | FamilyActivityPicker на child only | ✅ |
| st-C3 | C | Report filter/context | ✅ |
| st-C4 | C | Monitor primary writer + thresholds | ✅ |
| st-C5 | C | ManagedSettings shields | ✅ |
| st-C6 | C | apply pipeline / pull rules | 🚧 |
| st-C7 | C | fetchRealScreenTimeStats ← store/server | ✅ |
| st-C8 | C | **MUST** POST/GET usage sync + TTL 6h | ✅ deploy MAIN :8002 2026-10-16 |
| st-C9 | C | AppLimits ↔ tokenHash | ✅ |
| st-C10 | C | multi-child memberId+deviceId | 🚧 (schema + selected child pull) |
| st-C11 | C | ST eligibility all child ages (kids→youngAdult/20+) | ✅ taxonomies mapped; flag OFF |
| st-D1 | D | FamilyTimeControlModal real used/limit | 🚧 (path wired; needs Device QA) |
| st-D2 | D | Advanced time card | 🚧 (already source-gated) |
| st-D3 | D | Parental 07 time + readiness | ✅ |
| st-D4 | D | ScreenTimeSettings / AppLimits tokens | ✅ |
| st-D5 | D | Devices / Detail ST status | ✅ |
| st-D6 | D | Notifications ST v1.1 (не блокер) | ⏳ |
| st-D7 | D | FamilyDayStrip chip MUST | ⏳ |
| st-D8 | D | Tariffs claims gate | 🚧 (flag still false until QA) |
| st-D9 | D | Main/Analytics no fake minutes | ✅ |
| st-D10 | D | honesty script new contract + Loc | ✅ |
| st-D11 | D | allowsSystemFamilyControls=true after QA | ⏳ |
| st-D12 | D | **MUST** kill ViewModel `"2:45"` | ✅ |
| st-D13 | D | **MUST** kill FamilyModals live path | ✅ (not in pbx) |
| st-D14 | D | Child guided setup CTA | ✅ |
| st-D15 | D | Empty/TTL copy RU+EN | ✅ |
| st-E1 | E | Device QA 2 iPhone | ⏳ |
| st-E2 | E | E2E auth→picker→sync→parent→shield | ⏳ |
| st-E3 | E | Archive entitlements check | ⏳ |
| st-E4 | E | Bump 9→10 (GO) | ⏳ |
| st-E5 | E | Commit+push (GO) | ⏳ |
| st-E6 | E | TestFlight → Submit | ⏳ |
| st-E7 | E | Review Notes / ASO honest | ⏳ |
| st-E8 | E | Privacy Nutrition parental-only | ⏳ |
| st-E9 | E | Sync stats-план §11 + POST_BUILD8 | ⏳ |
| st-F1 | F | Shield Action backlog | ⏳ |
| st-F2 | F | Main chip v1.1 | ⏳ |
| st-F3 | F | Analytics ST section v1.1 | ⏳ |
| st-F4 | F | Push parent on limit | ⏳ |
| st-F5 | F | Weekly digest | ⏳ |

**Легенда:** ✅ done · ⏳ pending · 🚧 in progress · ❌ blocked

При закрытии задачи: `✅` здесь + Cursor TodoWrite `merge: true` на тот же `st-*`.
