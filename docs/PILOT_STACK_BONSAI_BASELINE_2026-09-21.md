# Bonsai baseline cost — снимок 2026-09-21 (`ps-b-00`)

**Цель:** точка отсчёта **до** Bonsai. Сравнивать ROI недель 1–2 с этими цифрами.

---

## 1. Политика (лимиты, не факт расходов)

| Параметр | Значение | Файл |
|----------|----------|------|
| Soft / day | $15 | `coding_orchestrator/config/budget.yaml` |
| Hard / day | $40 | то же |
| Soft / week | $80 | то же |
| Hard / week | $200 | то же |
| Max agents | 4 | то же |
| Premium review | **обязателен** (`require_premium_review: true`) | то же |
| Draft route (профиль) | `ollama` | `profiles/*.yaml` · `routing.py` |

---

## 2. Факт счётчика orch (сейчас)

| Метрика | Значение | Источник |
|---------|----------|----------|
| `spent_day_usd` | **0.0** | `coding_orchestrator/data/budget.json` |
| `spent_week_usd` | **0.0** | то же |
| Kill switch | false | то же |
| runs.jsonl | 11 записей (smoke) | harness: stub×5, claude-code×4, codex×2 |
| Поля cost в runs | **нет** | счётчик $ по run ещё не пишется в jsonl |

**Вывод:** orch budget store **живой**, но реальных накопленных $ за draft **пока 0** (мало боевых прогонов / подписка Cursor-Claude вне этого счётчика).

---

## 3. Локальный LLM на Mac сейчас

| Факт | Значение |
|------|----------|
| `ollama` | установлен (`/usr/local/bin/ollama`) |
| Модели | только `qwen2.5-0.5b-instruct-q4km` (~397 MB) |
| Bonsai | **нет** |
| Железо Mac | **Intel i7-4850HQ · 16 GB RAM · x86_64** (не Apple Silicon) |

Draft-слот orch уже указывает на Ollama, но «боевой» draft = крошечная модель, не 27B.

---

## 4. Что считать baseline на практике (метод ROI)

Пока orch `$=0`, baseline для сравнения с Bonsai:

| Канал | Как мерить (вручную / журнал) |
|-------|-------------------------------|
| **A. Cursor / Claude / Codex** | Подписка + заметка: «сколько follow-up правок пилота на 1 задачу» |
| **B. Orch night/draft** | После появления cost в tracker — `spent_*` за неделю |
| **C. Tool pressure** | Число tool-calls / файлов, открытых агентом на типовой задаче (Repowise vs без) |

Шаблон строки журнала (копипаст):

```text
DATE | task | harness | est_$ | followups | notes
2026-09-21 | baseline snapshot | policy+ollama-0.5b | orch$=0 | — | Intel 16GB; Bonsai not installed
```

---

## 5. Статус `ps-b-00`

✅ Закрыто как **документированный снимок**.  
Повторный замер — перед `ps-b-10` (неделя 1 после wire).
