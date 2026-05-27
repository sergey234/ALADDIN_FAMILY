# GATE-DIALOG-REGRESS — отчёт прогона 2026-05-26

**Среда:** macOS · prod `https://aladdin-ai.ru` · репо `ALADDIN_iOS`  
**Исполнитель:** ML-агент (авто + код-ревью); **ручные UI** — отмечены отдельно.

---

## Итог

| Категория | PASS | Частично | Ручная проверка |
|-----------|------|----------|-----------------|
| **R1–R19** | **14** | **5** | **5** |
| **Smoke** | **10/10** | — | — |
| **Verify prod** | **полный OK (12 шагов)** | OPS-02 / P1-15 | ✅ 2026-05-26 |

**Вердикт:** **GATE-DIALOG-REGRESS — PASS с оговорками** (автоматика + prod API).  
Закрыть полностью после **1–2 ч на устройстве** (R3, R6–R8, R15, R19 resume UI).

---

## Smoke (R11) ✅

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
PYTHONPATH=. python3 Tests/test_companion_p0_smoke.py -v
# Ran 10 tests in 0.39s — OK
```

| Тест | Покрывает |
|------|-----------|
| test_jwt_enrich_device_child | R1 |
| test_age_policy_child_unicorn_only | R1, R8 |
| test_policy_child_meetup_block | R2 |
| test_companion_store_* | R3, R14 |
| test_companion_stream_cache | R19 (local) |
| test_companion_feedback_store | R18 |
| test_companion_memory/profile | R16, R17 |
| test_family_consent_overrides_jwt | R15 |

---

## Prod API / verify (R9, R12, R13)

`./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru` → **All checks passed**

Дополнительно (ручной скрипт регрессии):

| ID | Проверка | Результат |
|----|----------|-----------|
| **R1** | JWT `age_band=child`, `parent_consent.companion=true` | ✅ |
| **R2** | Встреча без родителей → `blocked` / safe redirect | ✅ |
| **R5** | POST `/api/ai/companion/chat` — не SFM mock, есть ответ | ✅ |
| **R12** | capabilities `mic_button=true`, streaming=true | ✅ |
| **R14** | GET `/threads` → 200, список | ✅ |
| **R16** | GET `/memory` → 200 | ✅ |
| **R17** | GET `/profile` → preset friendly | ✅ |
| **R18** | POST `/feedback` → recorded, trust_delta | ✅ |
| **R19** | POST `/stream` → SSE `emotion` + `token` | ✅ **на проде** |
| **R4** | POST `/voice/ephemeral-token` → token | ✅ |

---

## Код / статический (без устройства)

| ID | Проверка | Результат |
|----|----------|-----------|
| **R6** | `CompanionHubScreen`, `ChildRewardsScreen` → `.companionHub` | ✅ код |
| **R7** | `CompanionVoiceSession`, P0-10 emoji | ✅ код (🟡 stub WS) |
| **R8** | `companionHub` только из Kids path | ✅ код |
| **R9** | `ai_unavailable_no_mock_in_prod`, `AIOutboundTextGate` | ✅ код |
| **R10** | `usage_meters.py`, JWT limits | ✅ код |
| **R13** | `modules/registry`, FEATURE env example | ✅ код |
| **R19** | `CompanionStreamingService` + «Продолжить загрузку» UI | ✅ код |

---

## Требует устройства (чеклист QA)

| ID | Шаг | ☐ |
|----|-----|---|
| **R3** | 2 сообщения → force quit → trust/thread на месте | ☐ |
| **R6** | Kids → Игры/награды → Hub → Conversation | ☐ |
| **R7** | Mic → WS / emoji реакция | ☐ |
| **R8** | Main: нет входа в companion без Kids | ☐ |
| **R10** | 50+ сообщений → лимит/предупреждение (если включён) | ☐ |
| **R15** | Family: consent off → ребёнок не входит | ☐ |
| **R19** | Стрим → airplane mode → «Продолжить загрузку» | ☐ |

---

## Следующий шаг

1. QA на устройстве: таблица выше (≈45 мин).
2. ~~**OPS-02**~~ — verify полный (`verify_companion_p0_prod.sh` 12 шагов).
3. **P1-27…P1-30** + device QA → **GATE-DIALOG D01–D10**.

---

*Обновлять при повторном прогоне.*
