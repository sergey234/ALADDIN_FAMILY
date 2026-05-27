# Companion hero assets (P1-08)

- `unicorn.riv` / `aladdin.riv` / `genie.riv` — bundled placeholders; replace with Figma/Rive state machine
  where inputs match `CompanionHeroRiveMapping.riveStateName` (`idle`, `happy`, `listening`, …).
- Optional: add CocoaPods/SPM `RiveRuntime` — `CompanionHeroRiveHost.swift` will use `.riv` directly.
- Until RiveRuntime is linked, `CompanionHeroAnimatedView` provides procedural animation for all 12 emotions.
- **UI:** Conversation = rect full-body stage (`conversationFullBody`), artboard **360×480**; Hub = 96pt circle.
- **Dialogue:** `CompanionDialogueStrip` — subtitle + history sheet (Grok-style, not bubble feed).
