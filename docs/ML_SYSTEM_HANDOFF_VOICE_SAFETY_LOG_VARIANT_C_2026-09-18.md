# ML System Handoff — Voice Safety Log (Variant C Hybrid)

**Date:** 2026-09-18  
**Repo root (mandatory):** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Product:** ALADDIN iOS — family security app (not a personal productivity menubar)  
**Decision owner:** product owner (Sergey) — Variant **C** approved  
**Cursor TODO track:** `vsl-c-*` (merge-only; do not wipe other TODO lists)  
**Status:** P0 **C1+coach implemented in code** · unit tests added · run A1–A12 smoke on device · P1/P2 pending  
**Mandatory companion (gaps + acceptance A9–A12):**  
`docs/ML_SYSTEM_HANDOFF_VOICE_SAFETY_LOG_VARIANT_C_REVIEW_RECS_2026-09-18.md`

### Implementation snapshot (2026-09-18)

| Deliverable | Path / change |
|-------------|----------------|
| Router | `Core/Voice/VoiceIntentRouter.swift` |
| ClipboardSafety | `Core/Security/ClipboardSafetyService.swift` |
| Tests | `Tests/UnitTests/VoiceIntentRouterTests.swift`, `ClipboardSafetyServiceTests.swift` |
| Wire STT → tags/nav | `ViewModels/VoiceNotesViewModel.applyVoiceIntentRouting` |
| Sheet → Antifake (A9) | `Screens/VoiceNotesScreen` dismiss then `navigateToAntifakeShareCheck` |
| Coach tip | one-shot banner + RU/EN strings |
| Choke point | `AntifakeTextCheckViewModel.applyPastedContent` |
| Kill-switch | `UserDefaults voiceIntentRouterEnabled` (default on) |
| EventKit / clipboard history / bg observer | **not** added |

---

## 0A. Amendments accepted from peer review (2026-09-18)

Peer ML review verified against code. **Owner direction (Variant C) unchanged.**  
Implementer MUST read the review file; this section is the binding delta to the original plan.

| ID | Amendment | Decision |
|----|-----------|----------|
| **M1** | VoiceNotes is a **sheet** (Settings / SimpleHome). Do **not** only `navigateTo(.antifakeHub)` under the sheet. Contract: parse → persist tags → **dismiss sheet** → `navigateToAntifakeShareCheck` (+ short toast). Acceptance **A9**. | **ACCEPT** |
| **M2** | ClipboardSafety at **one choke point**. Prefer start of `applyPastedContent` (already used by `pasteFromClipboard` + `applySharePayload`). Do not leave Share/deep-link unsanitized. Acceptance **A11**. | **ACCEPT** (choke = `applyPastedContent`) |
| **M3** | Order: router → persist intent tags → optional navigate → summary/structure later. Intent tags must survive merge (`Set` union OK; do not replace whole `tags` array). Acceptance **A12**. | **ACCEPT** |
| **M4** | `localOnlyMode` = note/audio on device; Antifake check may use network. Show clear copy. | **ACCEPT** |
| **S1** | One-shot coach tip with prefixes in VoiceNotes (P0.5 / same GO if owner allows). | **ACCEPT as C+ default in P0** |
| **S2** | Persist **full transcript**; Antifake/title body = remainder after prefix. | **ACCEPT** |
| **S3** | STT aliases + **leading tokens only** + mid-sentence negative tests (A10). | **ACCEPT** |
| **S4** | Concrete secret unit cases; phone ≠ OTP. | **ACCEPT** |
| **S5** | **Shortcut before Widget**; widget → optional **P2** (not P1 blocker). | **ACCEPT** |
| **S6** | **EventKit OUT** until separate owner GO. | **ACCEPT** |
| **A9–A12** | Sheet nav, mid-sentence, Share sanitize, tag survival. | **ACCEPT** |
| **Pivot map** | C / C1 default P0; C0 tags-only if blocked; C-lite / C+; A/B/VibeBar not default. | **ACCEPT** |

**Recommended P0 package for GO:** **C1 + coach tip (C+)** = full router + ClipboardSafety + sheet→Antifake + one-shot tip.  
**Shrink path:** **C0** (tags only, no navigate) if sheet glue slips schedule — do not invent a second voice stack.

---

## 0. Confidence (read first — do not claim 100%)

| Layer | Confidence | Notes |
|-------|------------|--------|
| **Product direction (Variant C vs A/B/full VibeBar clone)** | **~90%** | Best fit for ALADDIN brand, App Store risk, and existing code. Not 100%: if owner later wants pure productivity, path B would diverge. |
| **Architecture (glue on VoiceNotes + Antifake, not new app)** | **~92%** | Strong reuse evidence in repo. |
| **P0 scope (router + clipboard safety)** | **~85%** | Right first slice; exact API shapes may shift ±1 file. |
| **P1/P2 details (widget, weekly digest, EventKit)** | **~70%** | Directionally correct; validate after P0 usage. |
| **Keyword list (RU/EN prefixes)** | **~75%** | Start with fixed list; expand after 1–2 weeks of real phrases (do not hard-freeze forever). |

**Honest verdict for the next ML system:**  
Variant C is the **optimal default path for ALADDIN today**. It is **not** a mathematical 100% guarantee — it is the best trade-off among brand, security, reuse, and Review risk. If P0 shows parents never use voice for security, pivot diary layer earlier; if they only use «ссылка», drop diary UI in P2.

**Do NOT:**
- Clone macOS menu bar / SwiftBar / VibeBar as a product inside ALADDIN  
- Build clipboard history of last 15 items  
- Add background `UIPasteboard` observer  
- Add child screen-time spy via this feature  
- Build a new speech engine (reuse `SpeechRecognizerFactory`)

---

## 1. Origin story (what the Instagram screens taught us)

Source: carousel @margulan_seissembai (VibeBar-style personal tool).

| Idea from screens | Keep? | How in ALADDIN |
|-------------------|-------|----------------|
| Plan vs fact (evening recall) | Yes | Day / week recap of **parent** security + light notes |
| Hotkey + voice → log | Yes | Mic gesture / Shortcut (iOS has no true always-on-top bar) |
| Glue existing STT + thin router | Yes | ~small Swift glue on existing VoiceNotes |
| First word routes category | Yes | `VoiceIntentRouter` |
| Timer without Start/Stop | Soft / later | Optional parent “now segment” only — **never** child spy timer |
| Clipboard history ×15 | **No** | Replace with **Clipboard Safety** (on-demand check) |
| Terminal noise strip | Yes (security form) | Strip tracking params / spoof chars; warn on secrets |
| Evening + Sunday summary | Yes | Extend `VoiceDayRecap`; weekly digest in P2 |
| Obsidian export | No | Stay in ALADDIN encrypted / local stores + existing APIs |

---

## 2. Product decision: Variant C (hybrid)

### What we build
- **Core (~80%) — protection:** voice intents `ссылка` / `проверка` / `тревога` / `статус` + button **«Проверить скопированное»**.  
- **Addon (~20%) — light diary:** intents `идея` / `не забыть` + evening summary.  
- **Persona:** parent/guardian on their device; teen only with parental consent + local-first.

### What we explicitly do not build
- Full VibeBar / menu bar clone  
- Clipboard history manager (15 items)  
- Hidden child time tracking  
- Background pasteboard monitoring  
- New standalone “productivity hub” screen that competes with Main/Antifake/VoiceNotes

### Why this is optimal for ALADDIN
1. Matches brand (family safety), not office productivity.  
2. Reuses mature modules already in the app.  
3. Lower App Review / privacy risk than clipboard history.  
4. Delivers user value in days (P0), not weeks of greenfield.  
5. Diary layer is thin enough to not dilute security positioning.

### Rejected alternatives (for context)
| Variant | Why not default |
|---------|-----------------|
| **A — security only** | Safer/smaller, but loses “thought not lost” value from the inspiration screens; C adds diary cheaply on same router. |
| **B — diary/productivity only** | Wrong product identity inside ALADDIN; weak App Store story. |
| **Full VibeBar port** | Wrong platform UX (menu bar), high risk clipboard history, huge scope. |

---

## 3. Existing code map (reuse — do not rewrite)

Work only under iOS repo root. Before edits: `git rev-parse --show-toplevel` must be the path above.

| Area | Path / symbol | Role |
|------|----------------|------|
| Voice notes UI | `Screens/VoiceNotesScreen.swift` | Recorder, Day Recap sheet, structure |
| Voice VM | `ViewModels/VoiceNotesViewModel.swift` | Record → transcript → tags/summary; `localOnlyMode` |
| STT factory | `Core/Audio/SpeechRecognizerFactory.swift` | ru-RU, on-device → Siri cloud |
| Structure | `Core/Audio/VoiceNotesStructureService.swift` | LLM structure (tasks/people/urgent) — **orthogonal** to prefix router; keep both |
| Day recap | `Core/Audio/VoiceDayRecapService.swift` + sheet | Evening summary + deep link |
| Deep link | `CompanionDeepLinkRouter.isVoiceDayRecapDeepLink` | Opens recap |
| Antifake paste | `ViewModels/AntifakeTextCheckViewModel.swift` → `pasteFromClipboard` | Classify URL/phone/text |
| Classifier | `Core/Security/AntifakeTextInputClassifier.swift` | Existing classify/normalize — **extend via ClipboardSafety, don’t fork blindly** |
| Antifake UI | `Screens/AntifakeHubScreen.swift` | Paste row |
| Share / deep link | `NavigationManager.pendingAntifakeSharePayload` | Prefill hub |
| Nav | `Core/Navigation/NavigationManager.swift` | Screen enum |
| Widgets | `ALADDINWidgets/` | Later “Now” surface (P1) |
| Focus | `Screens/FocusSessionScreen.swift` | Optional later link — not P0 |
| Tests pattern | `Tests/UnitTests/AntifakeTextInputClassifierTests.swift` | Mirror for new unit tests |

**Important:** VoiceNotes may be presented as modal (not always in `ALADDINScreen` enum). Follow existing open paths (Settings / notifications / AI draft bridge). Do not invent a second voice stack.

---

## 4. Target architecture (glue layer)

```
[Mic / Shortcut] → SpeechRecognizerFactory / VoiceNotesTranscription
        ↓
 VoiceIntentRouter.parse(transcript) → Intent + remainder text
        ↓
 ┌──────────────────────────────────────────────────────────┐
 │ security_check / antifake_url → tag + navigate Antifake  │
 │ incident (тревога) → VoiceNote tag incident (+ optional) │
 │ status → show Network/Family status                      │
 │ idea / remind → VoiceNote tags (diary)                   │
 │ note (default) → normal VoiceNote                        │
 │ break → clear “now” segment if enabled (P1+)             │
 └──────────────────────────────────────────────────────────┘

[Button «Проверить буфер»] → ClipboardSafetyService
        → secret? warn & do not persist
        → sanitize URL → AntifakeTextCheckViewModel.applyPastedContent
```

### New files (P0 — recommended names)
1. `Core/Voice/VoiceIntentRouter.swift` — pure Swift, no UIKit dependency if possible  
2. `Core/Clipboard/ClipboardSafetyService.swift` — sanitize + secret heuristics  
3. `Tests/UnitTests/VoiceIntentRouterTests.swift`  
4. `Tests/UnitTests/ClipboardSafetyServiceTests.swift`

### Touch existing (minimal)
- After successful transcript in VoiceNotes flow → call router → set tags / optional navigation  
- `AntifakeTextCheckViewModel.pasteFromClipboard` → run through ClipboardSafety first  
- Optionally surface sanitize status in Antifake paste row (copy only)

---

## 5. Intent dictionary (P0 starter — RU + EN)

| Prefix (first tokens) | Intent | Action |
|-----------------------|--------|--------|
| `ссылка`, `link`, `url` | `antifake_url` | Extract URL → Antifake url mode |
| `проверка`, `проверь`, `check` | `security_check` | Antifake text/url or tagged security note |
| `тревога`, `alert`, `срочно` | `incident` | Tag `incident`; keep local note |
| `статус`, `status` | `status` | Navigate / show protection status |
| `идея`, `idea` | `idea` | Tag `idea` (diary) |
| `не забыть`, `напомни`, `remind` | `remind` | Tag `remind` (diary; local notification in P2) |
| `перерыв`, `break` | `break` | End “now” segment (P1+) |
| *(none)* | `note` | Default VoiceNote |

**Rules:**
- Case-insensitive; strip punctuation on first word(s).  
- Multi-word prefix: try longest match first (`не забыть` before `не`).  
- Remainder text = body after prefix.  
- No server call for routing in P0 (deterministic).  
- Telemetry: optional anonymous intent counts later — **no raw audio in analytics**.

---

## 6. Clipboard Safety (not history)

**Trigger:** user taps paste / «Проверить скопированное» / Share Extension only.  
**Never:** continuous pasteboard polling.

| Step | Behavior |
|------|----------|
| Read | `UIPasteboard.general.string` once |
| Secret detect | Password-like / OTP-length / seed-like → warn UI; **do not write to disk/history** |
| Sanitize | Remove common tracking query params (`utm_*`, `fbclid`, etc.); normalize URL via existing classifier helpers where possible |
| Route | Reuse `AntifakeTextInputClassifier` + `applyPastedContent` |
| Storage | No rolling list of 15 clips |

---

## 7. Phased plan

### P0 — Foundation (3–5 days) — START HERE after GO (C1 + coach)

Order (amended):
1. TDD `VoiceIntentRouter` (aliases, longest match, **mid-sentence negative**)  
2. TDD `ClipboardSafetyService` (secrets, utm strip, phone≠OTP)  
3. Wire choke point → **`applyPastedContent`** (covers paste + Share)  
4. Wire VoiceNotes after transcript → intent tags + full-transcript policy  
5. **Sheet dismiss → Antifake** navigate (M1)  
6. One-shot coach tip (S1) if GO includes C+  
7. Acceptance **A1–A12**  
8. Simulator/device build only at end of phase  

**Acceptance A1–A12**
- A1: Voice «ссылка …» opens/prefills Antifake with URL  
- A2: No prefix → normal VoiceNote  
- A3: Secrets from clipboard not persisted  
- A4: Tracking params stripped before check  
- A5: `localOnlyMode` VoiceNotes behavior preserved  
- A6: Unit tests for router + sanitize  
- A7: No background pasteboard observer  
- A8: RU + EN prefixes work  
- A9: From VoiceNotes **sheet**: dismiss then Antifake with URL  
- A10: Mid-sentence «…проверка…» → note, **not** security_check  
- A11: Share / share payload passes ClipboardSafety  
- A12: Intent tags survive summary/structure merge  

### P1 — Convenience (1–1.5 weeks)
- `NowStatusChip` on Main / SimpleHome  
- Richer `VoiceDayRecap` (security bullets + idea/remind counts)  
- **Siri Shortcut / App Intent “ALADDIN log” (priority)**  
- *(Widget moved to P2)*  

### P2 — Diary + week
- Simple UI lists for idea / remind  
- Local `UNUserNotification` for remind  
- Weekly Family Safety Digest (Sunday)  
- Optional widget chip  
- **EventKit still OUT** unless separate GO  

### Guard (every PR)
- No clipboard history ×15  
- No child time-spy  
- No background UIPasteboard observer  
- No new STT stack  

---

## 8. Cursor TODO IDs (SSOT for this track)

Use `TodoWrite` with **`merge: true`** only. Do not replace antifake/log-analysis TODO lists.

| ID | Content |
|----|---------|
| `vsl-c-meta` | Track active (Variant C) |
| `vsl-c-p0-01` | VoiceIntentRouter |
| `vsl-c-p0-02` | Unit tests router |
| `vsl-c-p0-03` | Wire into VoiceNotes |
| `vsl-c-p0-04` | ClipboardSafetyService |
| `vsl-c-p0-05` | Unit tests clipboard |
| `vsl-c-p0-06` | Antifake paste via safety |
| `vsl-c-p0-07` | Acceptance A1–A12 |
| `vsl-c-p0-08` | Sheet dismiss → Antifake navigate glue |
| `vsl-c-p0-09` | Coach tip prefixes (C+) |
| `vsl-c-p0-10` | ClipboardSafety on `applyPastedContent` choke (Share too) |
| `vsl-c-p0-11` | STT alias + mid-sentence negative tests |
| `vsl-c-p1-01` | NowStatusChip |
| `vsl-c-p1-02` | Enhance Day Recap |
| `vsl-c-p1-03` | Shortcut / App Intent (before widget) |
| `vsl-c-p1-04` | ~~Widget~~ → demoted; use `vsl-c-p2-04` |
| `vsl-c-p2-01` | Weekly digest |
| `vsl-c-p2-02` | Idea/remind UI |
| `vsl-c-p2-03` | Local reminders |
| `vsl-c-p2-04` | Optional widget chip |
| `vsl-c-guard` | Hard constraints + EventKit OUT |

Related canvas (optional UI summary): Cursor canvas `vibebar-aladdin-integration-tz`.

---

## 9. Security / privacy / App Store

- Mic + Speech only on explicit user gesture.  
- Prefer VoiceNotes `localOnlyMode` defaults.  
- Do not send audio to ALADDIN servers unless existing Companion consent path is used (out of P0 scope).  
- Never persist OTP/passwords/seeds from clipboard.  
- Parental / child surfaces: this feature is **parent-primary**; do not enable silent logging on child profiles.  
- Follow repo rules: `prod-no-mock-bypass`, no secrets in commits, no `telegram_stars_shop_bot/` in iOS release commits.

---

## 10. How the next ML system should work

1. Read **this file** end-to-end.  
2. Verify repo root + branch + `git status`.  
3. Confirm Variant C still owner-approved.  
4. Wait for **GO on P0** before coding (unless owner already said GO).  
5. Implement **TDD**: tests for router → implement → tests for clipboard → implement → wire UI minimally.  
6. Close Cursor todos with `merge: true` as items complete.  
7. Do not expand into P1/P2 until P0 acceptance passes or owner reprioritizes.  
8. If blocked: prefer shrinking P0 (router-only) over inventing new screens.

### Definition of Done — P0
- [ ] Router + clipboard services exist with unit tests green  
- [ ] Voice path tags/navigates for security prefixes  
- [ ] Antifake paste uses sanitize path  
- [ ] A1–A8 checked  
- [ ] Guard constraints verified in diff  
- [ ] No bot/VPN secrets / no unrelated drive-by refactors  

---

## 11. Six Hats summary (decision record)

| Hat | Conclusion |
|-----|------------|
| White | Reuse VoiceNotes + Antifake + DayRecap; gaps = router + clipboard safety |
| Red | Must feel like family shield, not office tracker |
| Black | History clipboard / child spy / product dilution are main failure modes |
| Yellow | Fast glue win; strong brand fit |
| Green | Deterministic prefixes first; learn vocabulary from usage |
| Blue | P0 → P1 → P2; security before diary UI |

---

## 12. Open questions for owner (non-blocking for P0)

1. Should «статус» open Network Protection, Main badge, or speak via AI? (Default: navigate Network Protection / Main status.)  
2. Should «тревога» also draft Family Chat? (Default P0: local tagged note only.)  
3. Teen access: off until consent UX exists? (Default: parent-only.)  

---

## 13. One-paragraph verdict (copy for status updates)

**Делаем Variant C (рекомендуемый P0 пакет = C1 + coach): ядро — защита голосом + ClipboardSafety на choke point `applyPastedContent`, сверху — лёгкий дневник; sheet VoiceNotes → dismiss → Antifake; leading-only prefixes + STT aliases; EventKit/widget history/out. Не клонируем VibeBar. Уверенность направления ~90%. Код — после GO на P0. Полные дыры/acceptance: REVIEW_RECS companion file.**

---

*End of handoff. Next agent: start at §10 + review §9 + this §0A.*
