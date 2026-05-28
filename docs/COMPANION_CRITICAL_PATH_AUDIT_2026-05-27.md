# Companion — аудит критического пути (2026-05-27)

> Проверка **до** работы: что уже сделано, что блокируется человеком/инструментом.

## Критический путь

| ID | Было (утро 27.05) | Сейчас | Блокер закрытия `[x]` |
|----|-------------------|--------|------------------------|
| **02b** | 0/36 frames | **36/36** в Figma (MCP) | PO: финальный art как OB (опционально) |
| **07** | 3× placeholder ~15 KB | **без изменений** | **Rive Editor** → export `.riv` ×3 |
| **11b** | ⏳ | ⏳ | **Реальный iPhone**, build **210** |
| **11c** | ⏳ | ⏳ | После **07** + device |
| **GATE-P0** | ждёт 11b | ждёт 11b | 11b PASS |
| **GATE-EMO** | ждёт 07+11c | ждёт 07+11c | 07 + 11c |

## Автопроверки (сегодня)

```bash
cd ALADDIN_iOS
PYTHONPATH=. python3 -m pytest Tests/test_companion*.py -q   # 46 passed
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion  # OK placeholder
```

## HERO-3-07 — почему агент не закрыл

- Production `.riv` создаётся только в **Rive Editor** (State Machine, `emotion`, `mouth_open`).
- В бандле: `unicorn.riv`, `aladdin.riv`, `genie.riv` — **placeholder** (~14.8 KB каждый).
- Следующий шаг: аниматор по [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md) → замена в `Resources/Companion/` → `riv gate` → **11c**.

## HERO-3-11b — протокол на устройстве

Заполни таблицу в [COMPANION_HERO3_11_QA_CHECKLIST.md](./COMPANION_HERO3_11_QA_CHECKLIST.md) § «Протокол».

1. Kids → Игры → **Мир героев** → build **210**
2. D10 (4 реплики × герои)
3. MOTION-Q1–5, MIMIC-Q1–6, SPEECH-Q6 (TTS в «Моё»)
4. Итог: PASS/FAIL → `[x]` **11b** в TRACKER

## Полный backlog (36 задач) — не в этом спринте одной сессией

| Блок | Открыто | Комментарий |
|------|---------|-------------|
| P1+ | 12 | Postgres, prod voice, XCUITest… |
| P2 | 16 | search, orchestrator… |
| P3 | 6 | media, Android… |
| Adult | 3 | отдельное приложение |
| GATE | 11 | после HERO-3 + P1+ |
| TestFlight | 1 | после GATE-P0 |

**Прогресс TRACKER:** 66/102 → после `[x]` 02b+07+11+GATE — пересчитать вручную.
