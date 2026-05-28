# Companion — план на завтра (2026-05-29)

**Handoff:** [COMPANION_ML_HANDOFF_2026-05-28.md](./COMPANION_ML_HANDOFF_2026-05-28.md)  
**Трекер:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) — **66/102**  
**Rive:** [COMPANION_RIVE_CONNECT_NODE_MCP.md](./COMPANION_RIVE_CONNECT_NODE_MCP.md)

---

## Цель дня

Закрыть оставшийся хвост **HERO-3-07**: `aladdin.riv` + `genie.riv` (unicorn уже >25 KB), и продвинуть **11b** на iPhone.

---

## Утро (приоритет 1) — Rive Editor, aladdin + genie

| # | Время | Действие | DoD |
|---|-------|----------|-----|
| 1 | 30–45 мин | Открыть `aladdin.riv` и импортировать `docs/assets/aladdin_master_OB01_crop_360x480.png` | hero full-cover 360×480 |
| 2 | 30–45 мин | Открыть `genie.riv` и импортировать `docs/assets/onboarding_OB03_APP_360x480_FILL_headfix_v1.png` | hero full-cover 360×480 |
| 3 | 15 мин | Export обоих: `aladdin.riv`, `genie.riv` (заменить placeholder) | каждый **> 25 KB** |
| 4 | 5 мин | Gate: `companion_riv_size_gate.py` + `verify_companion_rive_ios_bundle.sh` | exit 0 |
| 5 | 15 мин | Xcode → iPhone: все 3 героя **живые** (не PNG bridge) | визуально OK |

**Параллельно не блокирует:** iPhone **11b** на placeholder для aladdin/genie.

---

## День (приоритет 2) — закрыть 07 и перейти к 11b

| # | Действие | Референс |
|---|----------|----------|
| 6 | Проверить, что `unicorn.riv` = production partial (уже >25 KB) | `Resources/Companion/unicorn.riv` |
| 7 | Закрыть `aladdin.riv` + `genie.riv` ручным export в Rive Editor | [5 STEPS](./COMPANION_RIVE_EDITOR_5_STEPS.md) |
| 8 | Прогнать gate + iPhone smoke на всех 3 героях | [EXPORT_CHECKLIST](./COMPANION_RIVE_EXPORT_CHECKLIST.md) |
| 9 | Сообщить **«07 готов»** → TRACKER `[x]` HERO-3-07 | |

---

## Параллельно — QA 11b

| # | Действие | Документ |
|---|----------|----------|
| 10 | Build **210+** на iPhone | [11B session](./COMPANION_HERO3_11B_DEVICE_SESSION.md) |
| 11 | MOTION-Q1–5, SPEECH-Q6, D10 | [11 QA checklist](./COMPANION_HERO3_11_QA_CHECKLIST.md) |
| 12 | Отметить **11b** в TRACKER после прохода | |

---

## Вечер (приоритет 3) — после 07

| # | Действие |
|---|----------|
| 13 | **HERO-3-11c** — MIMIC-Q1–6 на production `.riv` |
| 14 | Обновить [READINESS_MATRIX](./COMPANION_HERO3_READINESS_MATRIX.md) |
| 15 | Подготовка **GATE-EMO** (не обязательно закрыть за день) |

---

## Опционально (только если время)

- RiveMCP: free exports исчерпаны (**3/3**) — нужен `RIVEMCP_LICENSE_KEY` для автогенерации.
- Открыть Figma Companion для сверки 12 лиц vs states.

---

## TODO-лист (копировать в чат / трекер)

```
Завтра 2026-05-29
[ ] unicorn.riv production export + gate
[ ] aladdin.riv production export
[ ] genie.riv production export
[ ] TRACKER [x] HERO-3-07
[ ] iPhone: unicorn Rive (не PNG)
[ ] HERO-3-11b device QA
[ ] HERO-3-11c MIMIC (после 07)
[ ] Обновить HANDOFF / TRACKER датой
```

---

## Не делать завтра без PO

- Миграция на Lottie / отказ от Rive
- Правки онбординга `KvkUdyb5Ll31Z9FSzCbpNl`
- `git commit` без явной просьбы
- Перезапись production `.riv` из MCP-черновика без проверки в Editor

---

*Включено в главный runbook:* [COMPANION_100_PERCENT_PARALLEL.md](./COMPANION_100_PERCENT_PARALLEL.md)
