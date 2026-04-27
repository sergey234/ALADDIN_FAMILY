# Phase 8.3 Performance Validation

Scope of this pass:

- `Track A · Phase 8` — Оптимизация загрузки и кеширования контента
- `Track A · Phase 8` — Уменьшение размера приложения
- `Track A · Phase 8` — Оптимизация анимаций и звуков
- `Track A · Phase 8` — Тестирование на старых устройствах

## Smoke command

Run:

`python3 scripts/phase8_performance_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. **Content loading and caching**
   - Cache hit/write wiring in `ContentManager`.
   - TTL/budget/policy contracts in `ContentCacheManager`.
2. **Animation and audio optimization**
   - Reduce Motion + bounded particle budget/fps contracts in `ParticleSystem`.
   - Priority throttling in `SoundEffectPlayer`.
   - Audio data/player cache contracts in `AudioManager`.
3. **Old-device readiness**
   - Successful simulator build for iPhone 11 destination.
4. **App size sanity gate**
   - Built simulator app bundle size is below `500 MB`.

## Notes

- This smoke is deterministic and suitable for repeated local/CI validation.
- It verifies optimization contracts and build-readiness, not runtime battery profiling.
