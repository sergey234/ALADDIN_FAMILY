# Antifake v4 — индекс документов (куда смотреть)

**Версия:** 2.0 · **Синхронизация:** 2026-06-15  
**Единая точка входа:** **[ANTIFAKE_UNIFIED_MASTER.md](./ANTIFAKE_UNIFIED_MASTER.md)** — ~280 задач, архитектура, gates, каталог  
**SSOT статусов v4:** [ANTIFAKE_V4_TASK_REGISTRY.md](./ANTIFAKE_V4_TASK_REGISTRY.md)  
**Прогресс v4:** **111 ✅ · 7 ⬜ · 13 ⏸ · 3 ❌ · 134 total**  
**Cursor:** ~156 строк (134 `af-*` + 22 meta/hdr) — **не удалять**, только `merge: true`.

---

## 0. С чего начать

| Роль | Документ |
|------|----------|
| **Любой агент / новый ML** | [ANTIFAKE_UNIFIED_MASTER.md](./ANTIFAKE_UNIFIED_MASTER.md) |
| Закрыть задачу `af-*` | [REGISTRY](./ANTIFAKE_V4_TASK_REGISTRY.md) + [WORKFLOW](./ANTIFAKE_V4_WORKFLOW.md) |
| Deploy / ML prod | [ML_HANDOFF](./ANTIFAKE_ML_HANDOFF_FOR_NEXT_AGENT.md) |
| iPhone QA | `docs/release/ANTIFAKE_DEVICE_BATCH_RUNBOOK.md` |

---

## 1. Планирование и исполнение

| Документ | Роль | Обновлять при закрытии? |
|----------|------|-------------------------|
| **[ANTIFAKE_UNIFIED_MASTER.md](./ANTIFAKE_UNIFIED_MASTER.md)** | **Итоговый** — всё направление | При смене фазы / сводки |
| [ANTIFAKE_V4_TASK_REGISTRY.md](./ANTIFAKE_V4_TASK_REGISTRY.md) | **SSOT** — ID, статусы | **Да** |
| [ANTIFAKE_TOP_TIER_PLAN.md](./ANTIFAKE_TOP_TIER_PLAN.md) | План v4.2, DoD | **Да** |
| [ANTIFAKE_V4_WORKFLOW.md](./ANTIFAKE_V4_WORKFLOW.md) | Правила агентов | При смене фазы |
| [ANTIFAKE_ML_HANDOFF_FOR_NEXT_AGENT.md](./ANTIFAKE_ML_HANDOFF_FOR_NEXT_AGENT.md) | Deploy/ML | После ML/deploy |
| [ANTIFAKE_V4_DOC_INDEX.md](./ANTIFAKE_V4_DOC_INDEX.md) | Этот индекс | При новом doc |

---

## 2. Архитектура и legacy

| Документ | Роль |
|----------|------|
| [ANTIFAKE_MASTER_ROADMAP.md](./ANTIFAKE_MASTER_ROADMAP.md) | Компоненты, риски |
| [ANTIFAKE_PRODUCTION_TODO.md](./ANTIFAKE_PRODUCTION_TODO.md) | Legacy `af-1…af-12` |
| [IMPLEMENTATION_BATCHES_TODO.md](./IMPLEMENTATION_BATCHES_TODO.md) | B2 iOS, R-08 |
| [BUILD_232_AGREED_TRACKER.md](./BUILD_232_AGREED_TRACKER.md) | Build 232 M2/M3 |

---

## 3. Static gates (код без xcodebuild)

```bash
bash scripts/verify_antifake_all_static.sh   # master — все gates
```

| Скрипт | Задачи |
|--------|--------|
| `verify_antifake_q_static.sh` | Q-01…Q-05 |
| `verify_antifake_release_readiness.py` | R-01 |
| `verify_antifake_open_tasks_code.sh` | J-04, D-07/08/10, G-03 |
| `verify_antifake_device_readiness.sh` | D-05, D-06 infra |
| `verify_antifake_bypass_off.py` | G-03, Q-01 |
| `verify_antifake_marketing_claims.py` | G-01 |
| `verify_antifake_no_mock_pre_submit.py` | Q-05 |

---

## 4. Apple, QA, release, backend

Полные таблицы — в [UNIFIED §11](./ANTIFAKE_UNIFIED_MASTER.md#11-каталог-документов-129-файлов-antifake).

Ключевые:
- `docs/ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md` — A-06  
- `docs/release/ANTIFAKE_TESTFLIGHT_CHECKLIST.md` — R-01  
- `docs/release/ANTIFAKE_DEVICE_BATCH_RUNBOOK.md` — D-01…D-04  
- `docs/server/test_antifake_prod_smoke.py` — R-03, Q-06  

---

## 5. Порядок СЕЙЧАС (2026-06-15)

```
✅ C → A → F → J → B → E → N → R → Ф2 (I,L,M,P,G,Q) → G-03/Q-01
⬜ DEVICE: D-01…D-04, D-09, E-06, R-02  (Xcode + iPhone)
⏸ v2: H (PIR), K (on-device ML)
```

---

## 6. Закрытые батчи (не переделывать)

C, A, F, J, B, N, I, L, M, P, G, Q, G-03/Q-01 — **111/134 ✅**

---

## 7. Синхронизация при закрытии `af-{ID}`

1. REGISTRY ✅  
2. TOP_TIER_PLAN ✅  
3. UNIFIED (сводка при смене фазы)  
4. Cursor todo `merge: true`  
5. Runbook/smoke при необходимости  

**При расхождении:** побеждает **ANTIFAKE_V4_TASK_REGISTRY.md**; контекст — **ANTIFAKE_UNIFIED_MASTER.md**.
