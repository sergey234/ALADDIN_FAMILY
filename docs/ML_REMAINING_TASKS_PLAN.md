# План оставшихся задач (после R2)

Обновлено: 2026-05-22. Очередь **строго по плану**: R3 → R4 → P0 (в конце).

---

## Уже сделано

| Блок | Статус |
|------|--------|
| P1 копирайт, opt-in, бейдж grounded | ✅ |
| P2 R1 корпус, chunks, pgvector, kb/search | ✅ |
| P2 R2 kb_rag, grounded+sources, fallback Hermes→SFM | ✅ на VPS |
| P2 R3 aggregates + strip_forbidden + Hermes с агрегатами для factual | ✅ код + деплой |
| P2 R4.2 A/B снимок путей (5 кейсов) | ✅ `smoke_ai_ab_rag_rules.py` |
| R4.3 флаг `AI_RAG_ENABLED` | ✅ в `kb_rag_service.py` |

---

## Очередь работ

### 1. P2 R4 — QA и rollout (сейчас)

| ID | Задача | DoD | Оценка |
|----|--------|-----|--------|
| R4.1a | Off-topic **батч 1–3** (30 кейсов) | ≥9/10 на батч, 0 kb_rag leaks | ~25–35 мин |
| | ✅ батч **1**: 9/10 (OT007 HTTP 404) | | ~2.3 мин |
| | ✅ батч **2**: 9/10 (OT014 HTTP 404) | | ~2.1 мин |
| | **сумма 1–2:** 18/20, kb_rag leaks 0 | | |
| R4.1b | Off-topic **батч 4–6** (30 кейсов) | то же | ~25–35 мин |
| R4.1c | Off-topic **батч 7–10** (40 кейсов) | то же | ~35–45 мин |
| R4.1d | Сводка 100 | `OFFTOPIC_PASS ≥90/100` суммарно | 5 мин |
| R4.2 | A/B метрики (опционально с `AI_RAG_ENABLED=0` на staging) | Таблица path по 5 кейсам | 10 мин |
| R4.3 | Зафиксировать rollback: `AI_RAG_ENABLED=0` в `.env` + restart | Чеклист в runbook | 5 мин |

**Почему 100 не одним куском:** ~40 с × 100 ≈ **66 мин** и обрыв по таймауту IDE. Батчи по **10** ≈ **7–12 мин** — можно остановиться между батчами.

#### Разбивка 100 off-topic (10 батчей)

| Батч | Кейсы | Темы (примеры) |
|------|-------|----------------|
| 1 | OT001–OT010 | погода, еда, медицина, спорт, стихи… |
| 2 | OT011–OT020 | курс валют, выборы, техника, код, космос… |
| 3 | OT021–OT030 | EN off-topic, рецепты, сон, путешествия… |
| 4 | OT031–OT040 | политика, резюме, акции, кино, музыка… |
| 5 | OT041–OT050 | математика, история, похудение, авто, WP… |
| 6 | OT051–OT060 | crypto, животные, сад, EN diet, перевод… |
| 7 | OT061–OT070 | NBA, JS, климат, отели, французский… |
| 8 | OT071–OT080 | витамины, марафон, свадьба, собаки, кофе… |
| 9 | OT081–OT090 | шутки, Musk, calculus, minecraft, налоги… |
| 10 | OT091–OT100 | ипотека, астрология, шахматы, wine, ML… |

#### Команды на VPS

```bash
cd /opt/aladdin-backend

# Один батч (JWT мінтится сам):
venv/bin/python3 tools/smoke_ai_offtopic100_prod.py
# с предустановкой:
export AI_OFFTOPIC_BATCH=1   # 1..10
venv/bin/python3 tools/smoke_ai_offtopic100.py

# Или shell-обёртка:
chmod +x tools/smoke_ai_offtopic_batches.sh
tools/smoke_ai_offtopic_batches.sh 3      # только батч 3
tools/smoke_ai_offtopic_batches.sh all    # все 10 подряд (~1–1.5 ч)
```

Переменные:

- `AI_OFFTOPIC_BATCH=1` … `10` — срез по 10
- `AI_OFFTOPIC_TIMEOUT=75` — таймаут одного чата (сек)
- `AI_OFFTOPIC_MIN_PASS=9` — порог для батча (по умолчанию 90% от среза)

| R4.1e | `smoke_ai_eval50` на проде | PASS ≥45/50 | ~20–40 мин (отдельный прогон) |

---

### 2. P0 — в конце очереди (как договорились)

| ID | Задача | DoD |
|----|--------|-----|
| P0-S1 | OpenRouter credits → Hermes doctor + E49 | Hermes chat без 402 |
| P0-S3 | `smoke_ai_eval50_prod` после credits | ≥45/50 |
| P0-iOS-A | TestFlight 201 краши A/B/C | Нет краша онбординг→AI→фон 2–3 мин |
| P0-iOS-B | Регрессия AI UI после R2/R3 | grounded/sources, opt-in |

---

### 3. Не в scope (blacklist)

- Fine-tune на чатах, история для обучения, raw logs в LLM, универсальный ChatGPT.

---

## Рекомендуемый порядок на ближайшую неделю

```mermaid
flowchart LR
  R41a[R4.1 батчи 1-3] --> R41b[R4.1 батчи 4-6]
  R41b --> R41c[R4.1 батчи 7-10]
  R41c --> R41d[Сводка 90/100]
  R41d --> R41e[smoke eval50]
  R41e --> P0[P0 credits + TestFlight]
```

1. Сегодня: батчи **1–2** (20 кейсов, ~15 мин).
2. Завтра: батчи **3–5**.
3. День 3: батчи **6–10** + сводка.
4. После зелёного R4.1: `smoke_ai_eval50_prod`.
5. Параллельно/после: OpenRouter credits (разблокирует Hermes, не блокирует SFM/RAG extractive).

---

## Критерии «R4 готов»

- [ ] Off-topic: **≥90/100** суммарно, **0** ответов с `kb_rag` + `sources` на off-topic
- [ ] Eval50: **≥45/50**
- [ ] A/B задокументирован (KB→kb_rag, factual→sfm_aggregates, off-topic→deflect)
- [ ] Runbook: отключение RAG одной переменной `AI_RAG_ENABLED=0`
