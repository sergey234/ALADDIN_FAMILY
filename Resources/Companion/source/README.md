# Companion — Rive Editor import (Variant B)

Import **body-only** PNG (face neutralized) into artboard **Hero360** 360×480.

| Hero | Body PNG (Variant B) |
|------|----------------------|
| unicorn | `docs/assets/unicorn_body_360x480.png` |
| aladdin | `docs/assets/aladdin_body_360x480.png` |
| genie | `docs/assets/genie_body_360x480.png` |

Generate bootstrap body PNG (until Figma export):

```bash
python3 scripts/companion_07_prepare_body_png.py unicorn
```

**Editor prompt:** `docs/COMPANION_RIVE_AI_AGENT_PROMPT_UNICORN.md`  
**After export:** `Resources/Companion/{hero}.riv` → `./scripts/companion_07_verify_all_riv.sh --strict-variant-b`
