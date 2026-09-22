---
name: aladdin-mech-pilot
description: Mech Pilot briefing — set goal, constraints, GATES, detect agent BS, report for human approve. Use at task start or when owner says pilot/mech.
---

# Aladdin Mech Pilot

**Пилот** = владелец (цель, GO, ответственность).  
**Меха** = агент (исполнение). Кода руками может быть меньше — **думать и принимать решения** обязан пилот.

Вдохновение: инженеры → «пилоты мех»; ~83% follow-up правок после агентов всё ещё делают люди. Смысл не в споре «вайб vs настоящая разработка», а в **постановке задач и ответе за результат**.

## Когда звать

- Старт фичи / волны / handoff новой ML  
- Ощущение «агент просто наваливает код»  
- Перед закрытием крупной задачи  

## Бриф пилота (заполнить в чате, коротко)

| Поле | Вопрос |
|------|--------|
| **Цель** | Что должно стать правдой для родителя/продукта? |
| **Домен** | iOS / orch / bot / VPN / business — один |
| **Канон** | Какой файл START_HERE / MASTER открыт? |
| **GATES** | 3–8 пунктов + доказательства (`@aladdin-gates`) |
| **Не делать** | Scope creep, auto-merge, mock, secrets |
| **GO нужен на** | commit / DEVICE / prod / Critical-фиксы |

## Красные флаги «агент несёт херню»

- API/эндпоинты «из головы» без кода в репо  
- Закрытие без теста/скрина/verify  
- Рефактор «заодно» соседних экранов  
- Уверенный тон при дырах в GATES  
- Предложение merge в master без Approve  

→ Остановиться, сказать пилоту риски, ждать GO.

## Отчёт в конце (пилот принимает)

```text
Сделано: …
Доказательства: …
Риски / не сделано: …
Нужен GO на: … (или не нужен)
```

## Связка

- Rule always-on: `.cursor/rules/mech-pilot.mdc`  
- GATES: `@aladdin-gates` · Trust: `@aladdin-quality-check`  
- Orch: human Approve на merge — night job ≠ done  
- Вход: `docs/ML_SYSTEM_START_HERE.md` § Mech Pilot  
