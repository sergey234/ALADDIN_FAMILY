---
name: aladdin-ios-release
description: iOS App Store release commits — exclude telegram bot and secrets from staging.
origin: ALADDIN
---

# ALADDIN iOS Release

Canonical rule: `.cursor/rules/no-telegram-bot-in-ios-release.mdc`

## Before release commit

```bash
git diff --cached --name-only | grep -E '^telegram_stars_shop_bot/|^\.env$' && echo STOP || echo OK
```

If STOP: `git restore --staged telegram_stars_shop_bot .env`

Bot work = separate commit/branch only when user explicitly asks.
