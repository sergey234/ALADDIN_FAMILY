# A-03 — Adult iOS app scaffold (no Store)

Separate repository placeholder — backend ready via `app_id=aladdin_adult`.

```
ALADDIN_Adult_iOS/          # future repo
  App/
  Core/Network/             # same JWT + /api/ai/companion/*
  Screens/Companion/        # reuse Family UX without child gates
```

Wire checklist:

1. Copy `CompanionAPIService` + models from Family target.
2. JWT issuer sets `app_id=aladdin_adult`, `age_verified=true` after 18+ gate.
3. Do **not** ship child Rewards / unicorn pet entry points.
4. Enable `FEATURE_ADULT_APP_ENABLED` on backend only until Store listing.
