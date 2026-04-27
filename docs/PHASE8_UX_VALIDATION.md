# Phase 8.2 UX Validation

Scope of this pass:

- `Track A · Phase 8` — Тестирование с реальными детьми разных возрастов
- `Track A · Phase 8` — Проверка доступности (VoiceOver, крупный шрифт)
- `Track A · Phase 8` — Проверка Reduce Motion, contrast и читабельности интерфейса для детских сценариев
- `Track A · Phase 8` — Тестирование производительности анимаций
- `Track A · Phase 8` — Валидация работы на разных размерах экранов

## Smoke command

Run:

`python3 scripts/phase8_ux_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What is validated

1. **Age coverage**
   - `ChildProfile` age groups exist and are explicit.
   - Seed content covers age-bands from early-child to young-adult segments.
2. **Accessibility baseline**
   - VoiceOver + Dynamic Type observers are present in `AccessibilityManager`.
   - Accessibility labels and readability constraints are present on core family/parental screens.
3. **Reduce Motion and readability**
   - Reduce Motion hooks exist across animation-heavy child flows.
4. **Animation performance contract**
   - Performance suite includes UI rendering / stability / load test coverage.
5. **Screen-size matrix**
   - Build succeeded for small iPhone, large iPhone, and iPad simulator destinations.

## Notes

- This smoke is deterministic and repeatable in local shell/CI.
- Live moderated sessions with real families can be tracked as an additional qualitative UX activity.
