# Local LLM — выбранный путь: Bonsai 2 27B на `/Volumes/Disk`

**Дата:** 2026-09-21 (решение владельца)  
**Выбор:** максимум качества local = **только Bonsai 2 27B** (не qwen3:8b, не оба)  
**Режим:** **narrow** = Disk + runtime + GGUF + CLI smoke · **orch wire = отдельный GO**  
**SSOT TODO:** `.cursor/PILOT_STACK_2026_TASK_REGISTRY.md` · `ps-d-*` · `ps-b-*`  
**Канон:** `docs/ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md` · research `PILOT_STACK_BONSAI_RUNTIME_RESEARCH_*`

---

## 0. Решение (зафиксировано)

| Вопрос | Ответ |
|--------|--------|
| Одна модель? | **Да — Bonsai 2 27B** |
| qwen3:8b / Ollama mid? | **Не ставим** как primary (отложено `ps-o-*`) |
| Оба? | **Нет** |
| Куда | `/Volumes/Disk/ALADDIN_LOCAL_LLM/bonsai2/` |
| Orch сейчас | без изменений (`draft: ollama` 0.5b) до `GO Bonsai orch wire` |
| Ollama 0.5b | оставить как есть (не мешает) |

---

## 1. Что уже было в плане ✅

| ID / блок | Содержание |
|-----------|------------|
| ps-b-00…01 | baseline + runtime research (Intel = CPU-only) |
| ps-orch-vs-bonsai | Orch ≠ модель |
| ps-d-00 | Disk layout (~63 ГБ free) |
| ps-b-02…05 | GO → install runtime → GGUF → smoke |
| ps-b-06…12 | orch wire + ROI — **после** smoke |
| GATES G1–G5 | load · budget · secrets · ROI · вердикт |
| Конституция | не VPS · не iPhone · не review на Bonsai |

---

## 2. Что дополняем сейчас (дыры закрыты)

| # | Дополнение | Зачем | TODO id |
|---|------------|-------|---------|
| 1 | **Решение: Bonsai-only** в registry/checklist | не качать 8b «заодно» | `ps-b-decision-quality` ✅ |
| 2 | Путь весов = **Disk**, не `~/` | SSD 5 ГБ тесный | `ps-d-*` + research update |
| 3 | Выбор GGUF: **PTQ1_0 (~5.95 ГБ)** на 16 ГБ RAM (меньше PQ2_0 ~7.2) | меньше давление RAM | `ps-b-04a-gguf-pick` |
| 4 | Preflight: закрыть лишнее (Cursor tabs / браузер) перед smoke | RAM | `ps-b-05a-ram-preflight` |
| 5 | Бинарь: prebuilt PrismML **или** build from fork x86_64 | Intel ≠ MLX | `ps-b-03` уточнён |
| 6 | Инструмент download: `huggingface-cli` / `hf` | не вручную | `ps-b-03a-hf-cli` |
| 7 | Journal шаблон: tok/s · RSS · swap · wall time | evidence | `ps-b-05b-journal-template` |
| 8 | Вердикт keep/drop **до** wire | не wire слепо | уже `ps-b-12` / после smoke mini-verdict `ps-b-05c` |
| 9 | Ollama mid (`ps-o-*`) → **deferred** | не параллелить | registry |
| 10 | README на Disk: запрет секретов | safety | `ps-d-03` |

---

## 3. Порядок выполнения (после этого документа)

```text
1  GO ✅ (владелец: максимум качества = Bonsai)
2  D: sudo mkdir + chown ALADDIN_LOCAL_LLM/{bonsai2/{bin,weights},journal}
3  D: README на Disk
4  B: hf/cli + PrismML llama.cpp → bonsai2/bin
5  B: download PTQ1_0.gguf → bonsai2/weights
6  B: smoke -ngl 0 -c 4096..8192 + journal
7  STOP → показать цифры владельцу
8  только потом: GO Bonsai orch wire (ps-b-06+)
```

**Не в этой волне:** qwen3:8b · orch adapter · review route · VPS · Tailscale a-10.

---

## 4. Целевые пути

```text
/Volumes/Disk/ALADDIN_LOCAL_LLM/
  README.md
  bonsai2/
    bin/          # llama-cli / llama-server (PrismML)
    weights/      # Ternary-Bonsai-2-27B-PTQ1_0.gguf
  journal/
    YYYY-MM-DD_bonsai_smoke.md
  ollama/         # пусто / не используем в этой волне
```

---

## 5. Smoke-команда (эталон)

```bash
# после install; пути уточнить по фактическому bin
/Volumes/Disk/ALADDIN_LOCAL_LLM/bonsai2/bin/llama-cli \
  -m /Volumes/Disk/ALADDIN_LOCAL_LLM/bonsai2/weights/Ternary-Bonsai-2-27B-PTQ1_0.gguf \
  -ngl 0 -c 8192 -n 64 \
  --temp 1.0 --top-p 0.95 --top-k 20 \
  -p "Say hello in one short sentence."
```

Записать: exit code · tokens · tok/s · peak RSS · был ли swap.

---

## 6. GATES этой волны (narrow)

| Gate | Доказательство |
|------|----------------|
| G-D1 | owner каталога = пилот |
| G-B1 | `llama-cli -h` или version из PrismML bin |
| G-B2 | файл GGUF на Disk, size ~6 ГБ |
| G-B3 | smoke prompt OK |
| G-B4 | journal с метриками |
| G-B5 | **нет** изменений orch wire без нового GO |

---

## 7. Фраза владельца (эта)

```text
Максимум качества local = Bonsai 2 27B.
GO Disk + Bonsai runtime narrow (PTQ1_0). Без qwen3:8b. Orch wire отдельно.
```
