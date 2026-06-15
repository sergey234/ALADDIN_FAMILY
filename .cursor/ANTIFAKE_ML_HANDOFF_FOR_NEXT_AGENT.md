# Antifake — handoff для следующей ML-системы / агента

**Версия:** 1.1 · **Дата:** 2026-06-15  
**Читать вместе с:** [ANTIFAKE_UNIFIED_MASTER.md](./ANTIFAKE_UNIFIED_MASTER.md) · [ANTIFAKE_V4_TASK_REGISTRY.md](./ANTIFAKE_V4_TASK_REGISTRY.md) · [ANTIFAKE_TOP_TIER_PLAN.md](./ANTIFAKE_TOP_TIER_PLAN.md)

---

## 1. Что мы строим (одна фраза)

Семейное iOS-приложение **ALADDIN Antifake**: пользователь **сам** отправляет текст / ссылку / голос / видео / запись звонка на проверку; для входящих звонков — **метка** из базы известных номеров (Call Directory). **Не** перехват всех звонков, **не** Truecaller-масштаб.

**Prod:** `149.154.65.180:8002` · SSH key `~/.ssh/aladdin_server` · Deploy: `./scripts/deploy_antifake_m1.sh root 149.154.65.180 ~/.ssh/aladdin_server`

---

## 2. Простым языком — что сейчас работает

| Что видит пользователь | Что происходит на самом деле |
|------------------------|------------------------------|
| Вставил scam-текст → «Вероятно фейк» 99% | **real_agent** (SFM BERT) или **local_ml** fallback |
| Badge «AI» / «Правила» / «Быстрая проверка» | По `source` + A-15 honesty copy |
| Mock / фейковые ответы | **Заблокированы** — `sfm_mock`, `mock` → 503 |
| Call Directory «113+ номеров» | PostgreSQL + CSV import (C-batch ✅) |
| Free user без Premium | API → **403** (B-10 ✅); Hub UI bypass ON (G-03 ⏸) |

**100% «истина» по дизайну продукта невозможна** — ML даёт вероятность (`likely_fake` / `uncertain` / `likely_real`). Максимум: **реальные модели + честный source + disclaimer**.

---

## 3. Технический статус (2026-06-15)

### ✅ Закрыто

- **F-01 / F-12 / F-08 / Q-06 / F-05 / R-03** — SFM + tier-2 + golden scam + gate green
- **F-13 / F-14 / B-11 / Q-07 / P-06** — ML-100%: torch, SFM grace, `real_agent` on prod
- **F-02…F-11** — media probe DoD, metrics, model version runbook
- **C, A, M batches** — fraud DB, UX copy, security
- **J-01…J-03, J-05** — verdict UX (в `AntifakeVerdictCard`)

### 🟡 In progress

| Задача | Статус |
|--------|--------|
| **E-03** | deep link push → Hub «Звонок» |

### ⬜ Следующий батч — **B (B-03…B-09)**

OpenAPI media schemas, worker verify in gate, `antifake_jobs` migration SQL, nginx 25MB overwrite + reload, deploy rollback runbook, cron TTL cleanup, rate-limit unit test.

### ❌ Не делать (Apple reject)

Фоновый PSTN, auto-hangup, перехват FaceTime/WhatsApp, marketing «100% все мошенники».

---

## 4. Архитектура проверки текста (как читать код)

```
iOS Hub → POST /api/antifake/check/text
    → antifake_service.check_text()
        1. _sfm_execute() → http://127.0.0.1:8003/api/execute (fake_news_detection_agent)
        2. если fail → _try_local_ml_text() → FakeNewsDetectionAgent.detect_fake_news()
           (heuristic-only если нет torch)
        3. merge с regex heuristic → source local_ml
        4. FORBIDDEN_SOURCES → 503 (never mock)
```

**Ключевые файлы:**

| Файл | Роль |
|------|------|
| `app/services/antifake_service.py` | Оркестрация, fallback, heuristic |
| `app/security/ai_agents/fake_news_detection_agent.py` | Паттерны + BERT (если torch) |
| `app/security/safe_function_manager.py` | SFM execute, 422 purge |
| `start_sfm_core_http.py` | HTTP :8003 |
| `docs/server/test_antifake_prod_smoke.py` | Prod gate |
| `scripts/deploy_antifake_m1.sh` | Deploy + smoke |

**PYTHONPATH на prod:** `/opt/aladdin-backend/app` первым; есть shadow `/opt/aladdin-backend/security/` — импорты только через `app.security.*`.

---

## 5. План для следующего агента (2026-06-15)

### Сейчас — Batch B (backend prod)

B-03…B-09 — см. [ANTIFAKE_V4_DOC_INDEX.md](./ANTIFAKE_V4_DOC_INDEX.md) §4.

### Затем — E → N → R

E-03 (in progress), E-05…E-08, N-01…N-05, R-01/R-02.

### Device (в конце)

D-01…D-04 TestFlight, метка на экране звонка.

### Перед App Store

G-03 `bypassPremiumGate=false`, Q-01 CI assert.

---

## 6. Команды для проверки на prod

```bash
# Smoke
ssh root@149.154.65.180 'cd /opt/aladdin-backend && ANTIFAKE_SMOKE_BASE=http://127.0.0.1:8002 ./venv/bin/python3 docs/server/test_antifake_prod_smoke.py'

# SFM status
curl -s http://127.0.0.1:8003/api/sfm/status | jq .

# Text check (на сервере)
cd /opt/aladdin-backend && ./venv/bin/python3 -c "
from app.services.antifake_service import check_text
import json
print(json.dumps(check_text('шокирующая правда переведите деньги act now'), ensure_ascii=False))
"

# af-11 gate
ANTIFAKE_GATE_BASE=http://127.0.0.1:8002 ./venv/bin/python3 scripts/antifake_prod_gate_af11.py
```

---

## 7. Cursor TODO — правила

- ID = `af-{TASK-ID}` (пример `af-B-03`).
- **134 атомарных** + meta/hdr — **не удалять**, только `merge: true`.
- При закрытии: registry + TOP_TIER_PLAN + DOC_INDEX при новом doc.
- Device QA (D-batch) — **последними**.

---

## 8. Что уже ✅ (не переделывать)

**Закрытые батчи:** ML-100%, C, A, F (17), J (кроме J-04 P2), I, L, M, B-01/B-02/B-10/B-11, R-03, Q-06/Q-07, P-06.

**Не дублировать:** J-01…J-03/J-05 в `AntifakeVerdictCard`, fraud DB ingest, probe DoD tests.

---

## 9. Контакты с реальностью

- **local_ml с heuristic-only** — это **не обман**, если badge «AI» и copy честные (A-15).
- **real_agent** — когда SFM + torch работают end-to-end.
- **rule_engine** — только last resort; Q-06 smoke **fail** на rule_engine-only для golden scam.

---

*Документ для передачи контекста следующему ML-агенту без доступа к истории чата.*
