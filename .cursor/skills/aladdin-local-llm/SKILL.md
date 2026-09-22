---
name: aladdin-local-llm
description: Local LLM / Bonsai 2 draft-only routing for orch. Use when owner mentions Bonsai, Ollama, local model, cheap night agents, or Pilot stack Compute.
---

# Aladdin Local LLM (Bonsai / Ollama)

**Роль:** дешёвый **draft / explore / night** контур.  
**Не роль:** review, security, parental, merge Approve, продукт в iPhone.

Канон: `docs/ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md`  
Budget: `coding_orchestrator/docs/BUDGET_POLICY.md`  
Вход: `docs/ML_SYSTEM_START_HERE.md` §0B

## Когда

- Владелец говорит Bonsai / локальная модель / «на картошке»  
- Orch: снизить $ на draft без смены review-модели  
- Offline brainstorm по коду (без секретов в промпте)

## Правила маршрута

| Задача | Модель |
|--------|--------|
| Draft, explore, cheap night | Local (Bonsai 2 / Ollama), если GO и runtime жив |
| Implement | Claude / Codex (как сейчас) |
| Review / security / merge | Strongest + **human Approve** — **никогда** только local |

## Шаги агента

1. Открыть пилот-док §4 GATES и §5 GO-чеклист.  
2. Если нет явного **GO Bonsai runtime / wire** — **не** ставить веса/runtime; только docs/advice.  
3. Не коммитить веса; каталог моделей: **`/Volumes/Disk/ALADDIN_LOCAL_LLM/`** (канон `docs/PILOT_STACK_LOCAL_LLM_DISK_PLAN_2026-09-21.md`), не системный SSD при ~5 ГБ free.  
4. Не трогать VPN doors, bot ports, Tailscale «закрой всё», Aperture vault.  
5. После пилота — вердикт keep/drop в journal.  
6. Порядок: Disk layout → Ollama 3b → (опц.) Bonsai narrow CLI → (опц.) orch wire.

## Не делать

- Constantly-on без ROI  
- Подмена Mech Pilot / orch Approve локальной моделью  
- Bonsai внутри ALADDIN iOS app без отдельного ТЗ  
- Путать **Repowise** / orch **GraftQueue** / trailhq **Graft**

## Связка

`@aladdin-mech-pilot` · `@aladdin-gates` · rule `ask-before-important-ops` · Repowise для карты кода
