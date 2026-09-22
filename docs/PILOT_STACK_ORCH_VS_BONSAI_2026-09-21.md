# Coding Orchestrator vs Bonsai 2 — сравнительный анализ

**Дата:** 2026-09-21  
**Повод:** GO «Bonsai runtime» + вопрос владельца: чем отличается от Coding Orchestrator  
**Железо:** Intel i7-4850HQ · 16 GB · x86_64  
**Факт сейчас:** Orch.app ✅ · Ollama `qwen2.5-0.5b` (~397 MB) · Bonsai ❌ · `~/ALADDIN_LOCAL_LLM` ❌

---

## 0. Вердикт в одном абзаце

**Это не два конкурирующих приложения.**  
**Coding Orchestrator** = диспетчер (роли, бюджет, night, Telegram, Approve, worktree).  
**Bonsai 2** = одна из **моделей** для слота `draft` внутри того же orch (сейчас там Ollama).  
Сравнивать «Orch vs Bonsai» так же странно, как «Xcode vs Swift compiler».  
Сравнивать нужно: **Bonsai vs текущий Ollama 0.5b vs mid-size Ollama vs Claude на draft**.

---

## 1. Что есть что (разные слои)

```
Владелец / Telegram / CLI
        ↓
 Coding Orchestrator.app  ←── УЖЕ ЕСТЬ (115/115)
   orch serve :8765
   roles · budget · Approve · night · GraftQueue(merge)
        ↓
 CostRouter.choose(WorkKind)
   draft      → harness "ollama"   ← сюда целится Bonsai
   implement  → claude-code
   review     → claude-code (premium, никогда local)
   qa         → codex
        ↓
 Harness (программа на Mac)
   Ollama / (будущий) llama-server Bonsai / Claude CLI / Codex
        ↓
 Модель (веса)
   qwen2.5-0.5b  ← СЕЙЧАС
   Bonsai 27B ternary GGUF  ← ПИЛОТ Compute
```

| | **Coding Orchestrator** | **Bonsai 2** | **Ollama (сейчас)** | **Cursor / Claude** |
|--|-------------------------|--------------|---------------------|---------------------|
| Класс | Приложение + engine | LLM-веса + спец. runtime | Runtime + мелкие веса | IDE-агент / облако |
| Роль | Диспетчер агентов | «Мозг» для cheap draft | То же слот draft | Дневная работа пилота |
| Где живёт | `coding_orchestrator/` · `~/Applications/…app` | `~/ALADDIN_LOCAL_LLM/` (вне git) | `/usr/local/bin/ollama` | Cursor + Claude Code |
| Знает про Approve / kill switch / night | ✅ | ❌ (глупая модель) | ❌ | частично вне orch |
| Пишет код в worktree сам | через harness | только текст ответа | только текст | да (Cursor) |
| Нужен для ALADDIN iOS app | нет | нет | нет | нет |

**Итог:** Bonsai **не заменяет** Orch. Orch **уже** маршрутизирует draft→Ollama; Bonsai — кандидат **заменить/усилить** ту модель.

---

## 2. Чем они «отличаются» на практике

| Вопрос | Orch | Bonsai |
|--------|------|--------|
| «Кто решает, звать Coder или Reviewer?» | Orch | — |
| «Кто режет $40/день?» | Orch BudgetTracker | — |
| «Кто жмёт Approve в main?» | Человек через Orch | — |
| «Кто пишет черновик плана ночью без $ API?» | Orch **зовёт** local harness | Bonsai **генерирует** текст |
| «Можно ли без Orch поставить Bonsai?» | — | Да (CLI smoke), но **бессмысленно для ALADDIN стека** |
| «Можно ли без Bonsai жить с Orch?» | Да — уже живёте (Ollama 0.5b / Claude) | — |

Путаница имён (ещё раз):

| Имя | Что это |
|-----|---------|
| orch **GraftQueue** | Очередь merge в Orch |
| trailhq **Graft** | Внешний граф кода (опц. пилот) |
| **Repowise** | Наш MCP-граф |
| **Bonsai** | Локальная модель PrismML |

---

## 3. Сравнение кандидатов на слот `draft` (это правильная таблица)

| Критерий | Ollama 0.5b **сейчас** | Mid Ollama (3B–7B Q4) | **Bonsai 2 27B** | Claude draft |
|----------|------------------------|------------------------|------------------|--------------|
| Качество кода/плана | Слабое | Среднее | Высокое среди local (~база 27B) | Лучшее |
| Размер | 0.4 GB | ~2–5 GB | ~6–7 GB | — |
| Runtime на **нашем** Mac | ✅ готово | ✅ stock Ollama | ⚠️ **только** PrismML fork, **CPU** (`-ngl 0`) | облако |
| Скорость Intel 16GB | Быстро | Норм | **Медленно** (ожидание thrashing) | Сеть |
| Orch wire | ✅ `draft: ollama` | ✅ тот же | ❌ нужен adapter `llama-server` + GO wire | ✅ implement/review |
| Риск «съест Mac» | Низкий | Средний | **Высокий** (16 GB + 7 GB model + OS) | Нет |
| Offline / $ | ✅ / $0 | ✅ / $0 | ✅ / $0 | ❌ / $ |
| Время до пользы | 0 | ~30 мин | часы (fork+download+smoke+wire) | 0 |

---

## 4. Плюсы / минусы Bonsai **именно у нас**

### Плюсы
- Сильнее текущего `0.5b` на coding-бенчах (заявка PrismML).  
- $0 на night draft после wire.  
- Offline brainstorm без утечки черновика в API (секреты всё равно нельзя в промпт).  
- Уже заложено в `BUDGET_POLICY` как draft-only.

### Минусы / красные флаги
- **Не Apple Silicon** → MLX и Metal отпадают; только CPU.  
- **16 GB** + модель ~6–7 GB + Orch + Cursor = риск swap и «Mac умер ночью».  
- Stock Ollama **не** ест ternary GGUF → отдельный runtime (сложность ops).  
- Orch **ещё не умеет** harness `bonsai` — wire = отдельный GO (`ps-b-06`).  
- Baseline orch `$=0` → ROI «сэкономили $» пока нечем мерить; выигрыш скорее «качество draft vs 0.5b».

---

## 5. Рекомендации (ранжировано)

### A — Рекомендую сейчас (лучшее ROI на этом Mac)

**Усилить draft через stock Ollama** (3B или 7B Q4), **не** трогая Orch код:

1. `ollama pull qwen2.5:3b` (или `7b` если после теста RAM ок).  
2. Оставить профили `draft: ollama`.  
3. Smoke через orch night/draft.  
4. Через 3–7 дней сравнить follow-up правки vs 0.5b.

**Почему:** тот же слот, нулевой новый runtime, совместимо с Intel, меньше риск kill Mac, сразу польза для Orch.

### B — Узкий пилот Bonsai (только если хочется «пощупать 27B»)

1. Install runtime + веса **только** smoke CLI (`ps-b-03…05`).  
2. **Не** wire в orch, пока latency/RSS не записаны.  
3. Вердикт: keep / drop / narrow.  
4. Wire (`ps-b-06`) — только если tok/s и RAM приемлемы.

**Почему:** GO runtime без wire соответствует чеклисту пилота; не ломает night на 0.5b.

### C — Не делать сейчас

| Действие | Почему нет |
|----------|------------|
| «Заменить Orch на Bonsai» | Категориальная ошибка |
| Bonsai на VPS бота / MAIN | Конституция + ask-before-ops |
| Wire Bonsai в review/merge | `require_premium_review` |
| Bonsai в iPhone app | `ps-x-03` |
| Полный install + wire одной фразой на Intel 16GB | Высокий риск без smoke evidence |

### D — Отложить Bonsai совсем

Если цель только «дешевле night» — **A** закрывает это. Bonsai имеет смысл, когда появится **Apple Silicon Mac** или eGPU / больше RAM.

---

## 6. Решение владельца (нужна одна фраза)

| Фраза | Что сделает агент |
|-------|-------------------|
| `GO Ollama mid-size` | pull 3B/7B + smoke; Bonsai install **отложить** |
| `GO Bonsai runtime narrow` | только download+CLI smoke; **без** orch wire |
| `GO Bonsai runtime full` | install + smoke; потом отдельно ждать `GO Bonsai orch wire` |
| `Skip Bonsai` | закрыть `ps-b-02…` как deferred; Orch без изменений |

**Рекомендация агента:** одна фраза владельца  
`GO модели на Disk + Ollama 3b`  
→ каталог на `/Volumes/Disk` · pull 3b · Orch env · smoke.  
Bonsai narrow — **после** этого и замера RAM. Full wire — не на Intel 16GB в первую очередь.

Канон диска: [`PILOT_STACK_LOCAL_LLM_DISK_PLAN_2026-09-21.md`](PILOT_STACK_LOCAL_LLM_DISK_PLAN_2026-09-21.md).

---

## 7. Связь с GO от 2026-09-21

Владелец сказал: `GO Bonsai runtime — install на Mac` **и** попросил сравнительный анализ.  
После анализа **install на паузе**, пока не выбрана фраза из §6 (Mech Pilot: evidence → human re-confirm при смене картины).
