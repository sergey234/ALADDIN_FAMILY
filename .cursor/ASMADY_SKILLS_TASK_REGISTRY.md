# Asmadey skills × ALADDIN — Task Registry (`asm-*`)

**SSOT** · rule: `.cursor/rules/asmadey-skills-todo-ssot.mdc`  
**ML handoff:** [`ASMADY_SKILLS_ML_HANDOFF.md`](ASMADY_SKILLS_ML_HANDOFF.md)  
**План остатков:** [`ASMADY_SKILLS_REMAINING_PLAN.md`](ASMADY_SKILLS_REMAINING_PLAN.md) (`asm-r-*`)  
**Источник вердиктов:** canvas `asmadey-decisions-per-skill` · `asmadey-skills-aladdin-analysis`  
**Каталог:** https://github.com/Asmadey/skills  

## Куда ставить (канон)

| Куда | Что |
|------|-----|
| **Cursor** `.cursor/skills/` | Thin `aladdin-*` skills (свои тексты, не слепой copy всего Asmadey) |
| **Orch** | Только короткие GATES-строки в `firstmate` — **не** vendoring каталога |
| **Business** | pricing/growth/SEO — вне iOS-коммитов |
| **Skip** | Dark Factory, RN/shadcn/MagicUI, WhatsApp, watermarks |

## Правила TodoWrite

1. Только `merge: true` — не затирать `orch-*` / `af-*` / `jam-*` / …
2. Закрыл → ✅ здесь → `completed` в Cursor TODO
3. `asm-50` / `asm-51` — **не внедрять** без явного GO владельца

---

## Фаза 0 — SSOT

| ID | Задача | Куда | Статус |
|----|--------|------|--------|
| `asm-00-registry` | Этот registry + todo-ssot rule | Cursor | ✅ 2026-09-19 |

## Фаза 1 — Аудит

| ID | Задача | Куда | Статус |
|----|--------|------|--------|
| `asm-01-audit-rule` | Rule: sandbox → audit → GO | Cursor | ✅ 2026-09-19 |
| `asm-02-skillspector` | Чеклист аудита внешнего skill | Cursor | ✅ 2026-09-19 |
| `asm-03-sandbox-path` | Путь песочницы skills | Cursor | ✅ 2026-09-19 |

## Фаза 2 — Три пилота + orch note

| ID | Задача | Куда | Статус |
|----|--------|------|--------|
| `asm-10-unlazy` | Skill `aladdin-gates` (GATES/unlazy) | Cursor | ✅ 2026-09-19 ready |
| `asm-11-humanizer-ru` | Skill `aladdin-humanizer-ru` | Cursor | ✅ 2026-09-19 ready |
| `asm-12-ajtbd` | Skill `aladdin-ajtbd` | Cursor | ✅ 2026-09-19 ready |
| `asm-13-orch-gates-note` | GATES в orch-basics | Orch | ✅ 2026-09-19 |
| `asm-14-orch-no-dump` | Запрет Asmadey dump в MASTER | Orch docs | ✅ 2026-09-19 |

## Фаза 3 — Брать (thin)

| ID | Задача | Куда | Статус |
|----|--------|------|--------|
| `asm-20-no-mistakes` | `aladdin-no-mistakes` ↔ verification-loop | Cursor | ✅ 2026-09-19 |
| `asm-21-slop-monster` | `aladdin-slop-monster` | Cursor | ✅ 2026-09-19 |
| `asm-22-quality-check` | `aladdin-quality-check` | Cursor | ✅ 2026-09-19 |
| `asm-23-low-token` | `aladdin-low-token` | Cursor | ✅ 2026-09-19 |
| `asm-24-skill-creator` | `aladdin-skill-creator` template | Cursor | ✅ 2026-09-19 |

## Фаза 4 — Доп. пилоты (ready, ROI)

| ID | Задача | Куда | Статус |
|----|--------|------|--------|
| `asm-30-code-reviewer` | `aladdin-dual-review` stub | Cursor | ✅ 2026-09-19 ready |
| `asm-31-better-interface` | `aladdin-ui-stress` stub | Cursor | ✅ 2026-09-19 ready |
| `asm-32-tastemaker` | `aladdin-anti-slop-design` stub | Cursor | ✅ 2026-09-19 ready |
| `asm-33-hypothesis` | `aladdin-hypothesis` stub | Cursor | ✅ 2026-09-19 ready |

## Фаза 5 — Позже / GO

| ID | Задача | Куда | Статус |
|----|--------|------|--------|
| `asm-40-adhd` | Brainstorm multi-role — только по запросу | Cursor | ✅ documented later |
| `asm-41-sgr-core` | Идеи multi-agent — сверить с orch, не форк | Docs | ✅ documented later |
| `asm-42-mobile` | UX-идеи без RN/Material dump | Cursor | ✅ documented later |
| `asm-50-diy-mcp` | diy-mcp-connector | Sandbox | ⏸ DEFERRED — нужен GO + ToS/security |
| `asm-51-agent-reach` | agent-reach соцсети | Business | ⏸ DEFERRED — нужен GO + ToS; вне iOS |

## Фаза 6 — Business

| ID | Задача | Куда | Статус |
|----|--------|------|--------|
| `asm-60-business-note` | pricing/growth/SEO вне iOS commits | Docs | ✅ 2026-09-19 |

## Явно skip (не задачи на внедрение)

Dark Factory · RN/shadcn/MagicUI/GSAP · WhatsApp · watermarks · supabase/vercel как основа app · полный dump Asmadey в git.

## Журнал

| Дата | Событие |
|------|---------|
| 2026-09-19 | Registry + phase 0–6 артефакты (thin skills, audit rule, orch GATES note) |
| 2026-09-19 | ML handoff + remaining plan (`ASMADY_SKILLS_ML_HANDOFF.md`, `ASMADY_SKILLS_REMAINING_PLAN.md`) |
| 2026-09-19 | Commit handoff `71be91e7` + sandbox `.gitignore` `66d27a06` |
| 2026-09-19 | Волна A pilots `asm-r-01`…`03` → `ASMADY_PILOT_JOURNAL.md` (on-demand) |
