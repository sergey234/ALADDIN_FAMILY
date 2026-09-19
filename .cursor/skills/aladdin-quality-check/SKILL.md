---
name: aladdin-quality-check
description: Trust gate for AI artifacts before marking done or handoff. Use before PRD/sign-off/demo.
---

# Aladdin Quality Check

Идея Asmadey `quality-check`: не верить артефакту ИИ без проверки.

## Перед «готово»

| Вопрос | Ответ |
|--------|-------|
| Есть доказательства (тест/скрин/curl)? | |
| Секреты не утекли? | |
| Соответствует GATES / ТЗ? | |
| Не сломан соседний контур (bot/iOS/orch)? | |

FAIL → не закрывать задачу.
