# Asmadey skills × ALADDIN × Coding Orchestrator — ML Handoff

**Сначала глобальный вход:** [`docs/ML_SYSTEM_START_HERE.md`](../docs/ML_SYSTEM_START_HERE.md) → затем этот файл (домен Asmadey).

**Для другой ML-системы / агента.** Это канонический снимок: что сделано, зачем, куда смотреть, что **не** делать, что осталось.

| Поле | Значение |
|------|----------|
| **Дата** | 2026-09-19 |
| **Статус инфраструктуры** | Фазы 0–6 плана **закрыты** (thin skills + audit + orch note) |
| **SSOT задач** | [`.cursor/ASMADY_SKILLS_TASK_REGISTRY.md`](ASMADY_SKILLS_TASK_REGISTRY.md) (`asm-*`) |
| **План остатков** | [`.cursor/ASMADY_SKILLS_REMAINING_PLAN.md`](ASMADY_SKILLS_REMAINING_PLAN.md) |
| **Исходный интеграционный план** | owner plan `asmadey_skills_integrate_*` (не править без GO) |
| **Канон orch** | [`coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md`](../coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md) § Asmadey |
| **Каталог-источник идей** | https://github.com/Asmadey/skills (идеи → thin `aladdin-*`, **не** dump) |

---

## 0. Ответ в одну фразу

**Asmadey не вшит в Coding Orchestrator.** Идеи → thin Cursor skills `aladdin-*` после sandbox + skillspector + GO владельца. В orch — только короткие GATES + запрет vendoring.

---

## 1. Куда интегрировали

| Куда | Что | Зачем |
|------|-----|--------|
| **Cursor** `.cursor/skills/aladdin-*` | Thin wrappers (свой текст) | Инструкции агенту в IDE |
| **Cursor** `.cursor/rules/` | `external-skill-audit.mdc`, `asmadey-skills-todo-ssot.mdc` | Аудит + TodoWrite merge-only |
| **Cursor** `.cursor/skills_sandbox/` | Песочница внешних skills | Не в iOS release path |
| **Orch** `firstmate/skills/orch-basics` | 3–5 строк GATES | Night/Coder не «ленит» закрытие |
| **Orch docs** MASTER | § Asmadey + запрет dump | Orch = runtime, не каталог skills |
| **Business docs** | `ASMADY_BUSINESS_OUT_OF_IOS.md` | pricing/SEO вне iOS commits |
| **Не интегрировали** | Полный каталог Asmadey, Dark Factory, RN/shadcn, diy-mcp, agent-reach | Skip / DEFERRED+GO |

```text
Asmadey catalog
    → sandbox + skillspector + owner GO
        → Cursor thin aladdin-*
        → orch: только GATES note
        → business: вне iOS
        → Dark Factory / RN → REJECT
```

---

## 2. Что сделали по фазам (и для чего)

### Фаза 0 — SSOT

| ID | Артефакт | Для чего |
|----|----------|----------|
| `asm-00` | `ASMADY_SKILLS_TASK_REGISTRY.md` + `asmadey-skills-todo-ssot.mdc` | Единый трекинг `asm-*`; не затирать `orch-*` / `af-*` |
| (ссылка) | MASTER § Asmadey | Другой ML сразу видит границу Cursor vs orch |

### Фаза 1 — Аудит (обязателен до чужих установок)

| ID | Артефакт | Для чего |
|----|----------|----------|
| `asm-01` | `external-skill-audit.mdc` | sandbox → audit → **GO владельца** |
| `asm-02` | `aladdin-skillspector` | Чеклист: секреты, auto-merge, обход ALADDIN, RN/web-only |
| `asm-03` | `.cursor/skills_sandbox/` | Безопасное место для чужого SKILL.md |

### Фаза 2 — Три пилотных skill + orch note

| ID | Артефакт | Для чего |
|----|----------|----------|
| `asm-10` | `aladdin-gates` | Acceptance/GATES до кода (Voice / Antifake) |
| `asm-11` | `aladdin-humanizer-ru` | Живой RU для App Review / онбординг |
| `asm-12` | `aladdin-ajtbd` | «Работа родителя» (ссылка / голос) |
| `asm-13` | GATES в `orch-basics/SKILL.md` | Не закрывать orch-задачу без доказательств |
| `asm-14` | Запрет dump в MASTER | Не vendor Asmadey в `coding_orchestrator/` |

### Фаза 3 — «Брать сейчас» (thin)

| ID | Skill | Для чего |
|----|-------|----------|
| `asm-20` | `aladdin-no-mistakes` | Blast-radius рядом с `verification-loop` (не дубль) |
| `asm-21` | `aladdin-slop-monster` | Анти-вода рядом с humanizer |
| `asm-22` | `aladdin-quality-check` | Trust gate перед «готово» / handoff |
| `asm-23` | `aladdin-low-token` | Сжимать длинные rules без потери инвариантов |
| `asm-24` | `aladdin-skill-creator` | Шаблон новых `aladdin-*` |

### Фаза 4 — ROI stubs (файлы ready, прогон по нужде)

| ID | Skill | Для чего |
|----|-------|----------|
| `asm-30` | `aladdin-dual-review` | Вторая пара глаз к `swift-reviewer` / matt |
| `asm-31` | `aladdin-ui-stress` | UI stress Antifake / Voice |
| `asm-32` | `aladdin-anti-slop-design` | Anti-slop визуал |
| `asm-33` | `aladdin-hypothesis` | Гипотезы + AJTBD |

### Фаза 5 — Документировано «позже» / DEFERRED

| ID | Артефакт | Статус |
|----|----------|--------|
| `asm-40` | `aladdin-adhd-brainstorm` | Ready, **не** constantly-on |
| `asm-41` | `ASMADY_SGR_CORE_VS_ORCH.md` | Идеи only; orch runtime уже есть — **не форкать** |
| `asm-42` | `aladdin-mobile-ux-notes` | UX-идеи без RN/Material dump |
| `asm-50` | `ASMADY_DEFERRED_DIY_MCP.md` | ⏸ нужен GO + ToS/security |
| `asm-51` | `ASMADY_DEFERRED_AGENT_REACH.md` | ⏸ нужен GO + ToS; **вне iOS** |

### Фаза 6 — Business note

| ID | Артефакт | Для чего |
|----|----------|----------|
| `asm-60` | `ASMADY_BUSINESS_OUT_OF_IOS.md` | pricing/growth/SEO не в iOS release commits |

---

## 3. Явно НЕ делаем (конституция)

- Весь каталог Asmadey в git `ALADDIN_iOS`
- Dark Factory / auto-merge из Cursor или Telegram
- RN / shadcn / MagicUI / GSAP как стек приложения
- WhatsApp-мост / watermarks-remover
- Ломать: no-mock bypass · VPN secrets handoff · bot≠iOS
- Vendoring Asmadey пачкой в `coding_orchestrator/profiles`
- Внедрять `asm-50` / `asm-51` без явного GO владельца

Приоритет: **ALADDIN rules + orch Approve > чужой каталог.**

---

## 4. Как проверить (smoke для ML)

Из корня `ALADDIN_iOS`:

```bash
test -f .cursor/ASMADY_SKILLS_TASK_REGISTRY.md \
 && test -f .cursor/ASMADY_SKILLS_ML_HANDOFF.md \
 && test -f .cursor/ASMADY_SKILLS_REMAINING_PLAN.md \
 && test -f .cursor/rules/external-skill-audit.mdc \
 && test -f .cursor/skills/aladdin-gates/SKILL.md \
 && test -f .cursor/skills/aladdin-skillspector/SKILL.md \
 && test -d .cursor/skills_sandbox \
 && rg -q "GATES \(asm-13" coding_orchestrator/firstmate/skills/orch-basics/SKILL.md \
 && rg -q "Asmadey / Cursor skills" coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md \
 && echo "ASMADY handoff smoke OK"
```

| Проверка | Путь |
|----------|------|
| Registry статусы | `.cursor/ASMADY_SKILLS_TASK_REGISTRY.md` |
| Skills | `ls .cursor/skills/aladdin-*/SKILL.md` |
| Orch GATES | `coding_orchestrator/firstmate/skills/orch-basics/SKILL.md` |
| Запрет dump | MASTER § Asmadey |
| Deferred | `ASMADY_DEFERRED_*.md` |

В чате: `@aladdin-gates` · `@aladdin-humanizer-ru` · `@aladdin-ajtbd` · `@aladdin-skillspector`.

---

## 5. Как пользоваться дальше (операционка)

1. Новый чужой skill → положить в `.cursor/skills_sandbox/` → `@aladdin-skillspector` → **ждать GO владельца** → thin `aladdin-*` своими словами.
2. Фича Voice / Antifake → `@aladdin-gates` + `@aladdin-ajtbd` до кода.
3. Тексты App Review / OB → `@aladdin-humanizer-ru` (+ при воде `@aladdin-slop-monster`).
4. Перед handoff → `@aladdin-quality-check` + при необходимости `verification-loop` / `aladdin-no-mistakes`.
5. diy-mcp / agent-reach → **только** после фразы владельца с GO (см. deferred docs).

TodoWrite: только `merge: true` на `asm-*`; не replace списков `orch-*` / `af-*`.

---

## 6. Что осталось (кратко)

Инфраструктура плана **готова**. Осталось **исполнение на живых задачах** и **GO-гейты**:

| # | Остаток | Блокер |
|---|---------|--------|
| R1–R3 | Реальные пилоты gates / humanizer / ajtbd | ✅ 2026-09-19 — [`ASMADY_PILOT_JOURNAL.md`](ASMADY_PILOT_JOURNAL.md); G6 device у владельца |
| R4–R7 | ROI-прогон dual-review / ui-stress / anti-slop / hypothesis | После R1–R3 или по запросу |
| R8 | adhd / mobile — только по запросу | Не constantly-on |
| R9–R10 | diy-mcp · agent-reach | **Явный GO** + ToS |
| R11 | Business session | Когда владелец попросит pricing/SEO |
| R12 | git commit артефактов | Только по явной просьбе владельца |

Детальный план остатков с acceptance: **[`ASMADY_SKILLS_REMAINING_PLAN.md`](ASMADY_SKILLS_REMAINING_PLAN.md)**.

---

## 7. Карта файлов

| Файл | Роль |
|------|------|
| `ASMADY_SKILLS_TASK_REGISTRY.md` | SSOT статусов `asm-*` |
| `ASMADY_SKILLS_ML_HANDOFF.md` | Этот handoff |
| `ASMADY_SKILLS_REMAINING_PLAN.md` | План остатков |
| `ASMADY_DEFERRED_DIY_MCP.md` | asm-50 |
| `ASMADY_DEFERRED_AGENT_REACH.md` | asm-51 |
| `ASMADY_SGR_CORE_VS_ORCH.md` | asm-41 |
| `ASMADY_BUSINESS_OUT_OF_IOS.md` | asm-60 |
| `rules/external-skill-audit.mdc` | Аудит |
| `rules/asmadey-skills-todo-ssot.mdc` | Todo policy |
| `skills_sandbox/README.md` | Песочница |
| `skills/aladdin-*/SKILL.md` | Thin skills |

---

## 8. Чеклист следующей ML-системы (5 минут)

- [ ] Прочитал этот handoff + registry  
- [ ] Smoke из §4 = OK  
- [ ] Не копирую Asmadey tree в orch / iOS release  
- [ ] Не трогаю asm-50/51 без GO  
- [ ] Следующий шаг — только из `ASMADY_SKILLS_REMAINING_PLAN.md` после выбора владельца  

**Конец handoff.**
