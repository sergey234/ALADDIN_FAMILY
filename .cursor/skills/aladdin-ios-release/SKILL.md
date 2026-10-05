---
name: aladdin-ios-release
description: iOS App Store release commits — exclude telegram bot and secrets from staging.
origin: ALADDIN
---

# ALADDIN iOS Release

Canonical rule: `.cursor/rules/no-telegram-bot-in-ios-release.mdc`  
Branch rule: `.cursor/rules/ios-commit-on-master.mdc`  
Build numbers: `docs/RELEASE_BUILD_PROMPT.md`

## Before release commit

`git branch --show-current` must be `master`. If it is not, stop. Do not commit on `hide-stars-public-2026-09` or any other branch.



```bash
git diff --cached --name-only | grep -E '^telegram_stars_shop_bot/|^\.env$' && echo STOP || echo OK
```

If STOP: `git restore --staged telegram_stars_shop_bot .env`

Bot work = separate commit/branch only when user explicitly asks.
