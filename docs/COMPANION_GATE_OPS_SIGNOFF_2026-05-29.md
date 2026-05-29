# GATE-OPS — закрытие (2026-05-29)

**Ворота:** GATE-OPS = health + полный prod verify (OPS-02 / P1-15)  
**Прод:** `https://aladdin-ai.ru` · VPS `149.154.65.180`  
**Связано:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) · [OPS-05](./COMPANION_OPS05_DOD_2026-05-26.md)

---

## Критерии GATE-OPS

| # | Критерий | Статус | Доказательство |
|---|----------|--------|----------------|
| 1 | Health `GET /api/health` → 200 | ✅ | verify шаг 1 |
| 2 | Register device + JWT (child, 3 героя в consent) | ✅ | verify шаг 2 |
| 3 | `/characters`, `/capabilities`, `/consent`, `/profile`, `/memory` | ✅ | verify 3–8 |
| 4 | `/state` usage + `/legal` | ✅ | verify 8b |
| 5 | POST `/chat` + domain/mood/emotion meta | ✅ | verify 9 |
| 6 | `/threads` + messages | ✅ | verify 10 |
| 7 | POST `/feedback` | ✅ | verify 11 |
| 8 | POST `/stream` + resume (SSE) | ✅ | verify 12 |
| 9 | Stream + `chat_mode` (Sprint 5) | ✅ | verify 12b |
| 10 | age_policy 3 героя (local + prod) | ✅ | verify 13–14 |
| 11 | GET `/domains`, `/workspaces`, `/cogs` | ✅ | verify 15–17 |
| 12 | Social bridge E2E (2× loneliness) | ✅ | verify 18 |
| 13 | VPS: Redis stream cache + orchestrator env | ✅ | deploy 2026-05-29 |

---

## Команда (повторить)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
curl -sS -m 8 https://aladdin-ai.ru/api/health
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
# Ожидание: exit 0, «All checks passed», 18 шагов
```

**Прогон закрытия:** 2026-05-29 — **exit 0**.

---

## Вне скоупа GATE-OPS (отдельные ворота)

| Что | Куда |
|-----|------|
| Stream + resume **на iPhone** (UI «Продолжить загрузку») | GATE-DIALOG-REGRESS R19, device QA |
| Полный GATE-DIALOG D01–D10 | TestFlight, PO |

---

**Вердикт:** **GATE-OPS ✅ CLOSED** (2026-05-29).
