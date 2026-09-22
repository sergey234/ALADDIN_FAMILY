# Pilot Stack 2026 — Task Registry (`ps-*`)

**SSOT** · гибрид C (Context / Compute / Admin)  
**Вход:** [`docs/ML_SYSTEM_START_HERE.md`](../docs/ML_SYSTEM_START_HERE.md) §0B  
**Bonsai:** [`docs/ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md`](../docs/ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md)  
**Tailscale:** [`docs/ADMIN_MESH_TAILSCALE_HYBRID_PLAN_2026-07-27.md`](../docs/ADMIN_MESH_TAILSCALE_HYBRID_PLAN_2026-07-27.md)  
**Rule:** `.cursor/rules/pilot-stack-todo-ssot.mdc`

## Правила TodoWrite

1. Только `merge: true` — не затирать `orch-*` / `asm-*` / `af-*` / `jam-*` / `vsl-*`.  
2. Закрыл задачу → ✅ здесь → `completed` в Cursor TODO.  
3. Железо / SSH / Tailscale / download весов — **только после явного GO** владельца (`ask-before-ops`).  
4. Не постоянно включать trailhq Graft / Aperture-vault / «закрой все порты».

## Порядок работы (рекомендуемый)

```text
Docs ✅ → (опц.) Context Graft ROI → Compute Bonsai GO → Admin Phase0 SSH → Tailscale dual → ROI вердикты
Параллельно можно: Voice DEVICE, Asmadey B3/B4 (другие id)
```

---

## Фаза D0 — Документы (инфра стека)

| ID | Задача | Статус |
|----|--------|--------|
| `ps-00-registry` | Этот registry + todo-ssot rule | ✅ 2026-09-21 |
| `ps-01-start-here-0b` | START_HERE §0B: 3 слоя + имена Graft/Repowise | ✅ 2026-09-21 |
| `ps-02-bonsai-pilot-doc` | `ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md` + GO-чеклист | ✅ 2026-09-21 |
| `ps-03-skill-local-llm` | Skill `@aladdin-local-llm` | ✅ 2026-09-21 |
| `ps-04-budget-policy` | BUDGET_POLICY: Bonsai = draft only | ✅ 2026-09-21 |
| `ps-05-agents-links` | AGENTS.md ссылки на стек | ✅ 2026-09-21 |

---

## Фаза C — Context (карта кода)

| ID | Задача | GO? | Статус |
|----|--------|-----|--------|
| `ps-c-00-repowise-ssot` | Закрепить Repowise как SSOT (не дублировать constantly) | — | ✅ уже (rule `repowise-first`) |
| `ps-c-01-graft-naming-note` | Журнал/START: orch GraftQueue ≠ trailhq Graft | — | ✅ в §0B |
| `ps-c-02-GO-graft-pilot` | **GO владельца:** пилот trailhq Graft 1–2 нед. | **GO** | ⬜ |
| `ps-c-03-graft-slim-install` | Install только на slim iOS или bot worktree | после c-02 | ⬜ |
| `ps-c-04-graft-baseline` | Baseline: tool-calls / tokens / $ без Graft (7д или 1 типовая задача) | после c-02 | ⬜ |
| `ps-c-05-graft-measure` | Замер с Graft vs baseline | после c-03 | ⬜ |
| `ps-c-06-graft-verdict` | Вердикт keep / drop / narrow → journal | после c-05 | ⬜ |

---

## Фаза B — Compute (Bonsai / local LLM)

| ID | Задача | GO? | Статус |
|----|--------|-----|--------|
| `ps-b-00-baseline-cost` | Зафиксировать baseline draft $ / tokens orch (без Bonsai) | — | ✅ 2026-09-21 `docs/PILOT_STACK_BONSAI_BASELINE_2026-09-21.md` |
| `ps-b-01-runtime-research` | Записать точный runtime (PrismML fork / MLX) из HF — docs only | — | ✅ 2026-09-21 `docs/PILOT_STACK_BONSAI_RUNTIME_RESEARCH_2026-09-21.md` (Intel Mac!) |
| `ps-orch-vs-bonsai` | Сравнение Orch (диспетчер) vs Bonsai (модель draft) | — | ✅ `docs/PILOT_STACK_ORCH_VS_BONSAI_2026-09-21.md` |
| `ps-d-00-disk-plan` | План хранения на `/Volumes/Disk` + раскладка | — | ✅ → **Bonsai-only** `docs/PILOT_STACK_LOCAL_LLM_DISK_PLAN_2026-09-21.md` |
| `ps-b-decision-quality` | Владелец: max quality = **только Bonsai 27B** (не 8b, не оба) | — | ✅ 2026-09-21 |
| `ps-d-01-GO-disk` | **GO:** Disk layout для Bonsai | **GO** | ✅ вместе с Bonsai narrow |
| `ps-d-02-mkdir-chown` | `sudo mkdir` + `chown` `…/{bonsai2/{bin,weights},journal}` | после d-01 | ⬜ |
| `ps-d-03-readme-secrets` | README на Disk: что хранить / запрет секретов | после d-02 | ⬜ |
| `ps-d-04-mount-preflight` | Preflight: `/Volumes/Disk` mounted | после d-02 | ⬜ |
| `ps-d-05-ollama-path` | Symlink Ollama → Disk | — | ⏸ **deferred** (Ollama mid не в этой волне) |
| `ps-d-06-verify-path` | Verify Ollama path | — | ⏸ deferred |
| `ps-o-01-GO-ollama-mid` | Ollama mid / qwen3:8b | — | ⏸ **deferred** (выбран Bonsai) |
| `ps-o-02-pull-3b` | pull mid Ollama | — | ⏸ deferred |
| `ps-o-03-orch-env-model` | ORCH_OLLAMA_MODEL mid | — | ⏸ deferred |
| `ps-o-04-smoke-ollama` | Smoke Ollama mid | — | ⏸ deferred |
| `ps-o-05-journal-metrics` | Journal Ollama | — | ⏸ deferred |
| `ps-o-06-optional-7b` | Опц. 7b | — | ⏸ deferred |
| `ps-b-02-GO-runtime` | **GO Bonsai runtime narrow** | **GO** | ✅ 2026-09-21 (max quality) |
| `ps-b-03a-hf-cli` | Убедиться `huggingface-cli`/`hf` на Mac | после b-02 | ⬜ |
| `ps-b-03-install-runtime` | PrismML llama.cpp → `…/bonsai2/bin/` (Intel CPU) | после d-02 | ⬜ |
| `ps-b-04a-gguf-pick` | GGUF = **PTQ1_0** (~5.95 ГБ) на 16GB RAM | — | ✅ решение в disk plan |
| `ps-b-04-download-weights` | Download PTQ1_0 → `…/bonsai2/weights/` | после b-03 | ⬜ |
| `ps-b-05a-ram-preflight` | Перед smoke: мало лишних apps; отметить free RAM | после b-04 | ⬜ |
| `ps-b-05-smoke-load` | Smoke CLI `-ngl 0` + prompt | после b-05a | ⬜ |
| `ps-b-05b-journal-template` | Journal: tok/s · RSS · swap · wall | вместе с smoke | ⬜ |
| `ps-b-05c-mini-verdict` | Mini-verdict keep→wire / drop / retry PQ2 | после smoke | ⬜ |
| `ps-b-06-GO-orch-wire` | **GO:** «GO Bonsai orch wire» | **GO** | ⬜ **стоп** до 05c |
| `ps-b-07-budget-route` | Draft → Bonsai adapter | после b-06 | ⬜ |
| `ps-b-08-reject-review` | Тест: review → local = reject | после b-07 | ⬜ |
| `ps-b-09-secrets-check` | Чеклист секретов | после b-05 | ⬜ |
| `ps-b-10-roi-week1` | Неделя 1 ROI | после b-07 | ⬜ |
| `ps-b-11-roi-week2` | Неделя 2 | после b-10 | ⬜ |
| `ps-b-12-verdict` | Вердикт keep / drop / narrow | после b-11 | ⬜ |

**Вне скоупа Bonsai:** модель в iPhone app (`ps-x-03`).  
**Канон хранения:** `docs/PILOT_STACK_LOCAL_LLM_DISK_PLAN_2026-09-21.md`.  
**Рекомендуемый старт GO:** `GO модели на Disk + Ollama 3b` (не Bonsai full).

---

## Фаза A — Admin mesh (Tailscale)

| ID | Задача | GO? | Статус |
|----|--------|-----|--------|
| `ps-a-00-read-plan` | Перечитать ADMIN_MESH план §0–§2 | — | ✅ 2026-09-21 подтверждено в working checklist |
| `ps-a-01-GO-phase0` | **GO:** Phase 0 SSH harden (MAIN + Contabo) | **GO** | ✅ 2026-09-21 |
| `ps-a-02-ssh-main` | MAIN: keys-only, fail2ban, password off (по runbook) | после a-01 | ✅ 2026-09-21: `PasswordAuthentication no` effective; key `aladdin-server` OK; health OK; bak `/root/aladdin_phase0_bak/` |
| `ps-a-03-ssh-contabo` | Contabo 🇩🇪 Brain (`…150`): то же | после a-01 | ✅ 2026-09-21 keys-only + fail2ban installed/active; `ssh aladdin-contabo` OK |
| `ps-a-04-breakglass` | Документ break-glass + IP-алиасы в `~/.ssh/config` | после a-02 | ✅ 2026-09-21 `docs/ADMIN_MESH_PHASE0_BREAKGLASS_2026-09-21.md` (IP Hosts уже были) |
| `ps-a-05-GO-tailscale` | **GO:** Tailscale admin-only Mac+MAIN+Contabo | **GO** | ✅ 2026-09-21 шаги 1–5 |
| `ps-a-06-ts-mac` | Tailscale up на Mac | после a-05 | ✅ |
| `ps-a-07-ts-main` | Tailscale на 🇷🇺 MAIN FirstVDS (`…180`) | после a-05 | ✅ `aladdin-main` / `100.124.156.3` |
| `ps-a-08-ts-contabo` | Tailscale на 🇩🇪 Brain Contabo (`…150`) | после a-05 | ✅ `aladdin-contabo` / `100.102.195.8` |
| `ps-a-09-dual-ssh` | Dual-path SSH: Tailscale имя + public IP break-glass | после a-06…08 | ✅ Host `*-ts` + IP Hosts сохранены |
| `ps-a-10-GO-close-public` | **GO последний:** сузить/закрыть public SSH (не продукт-порты) | **GO** | ⬜ |
| `ps-a-11-aperture-later` | Aperture / vault **только LLM keys** — отдельный GO, не bot/VPN | позже | ⬜ |

**Запрещено в этой фазе:** закрыть `:443` / VPN doors / `wg-bridge` (`ps-x-01`, `ps-x-02`).

---

## Фаза X — Конституция (не «фичи», а стоп-линии)

| ID | Задача | Статус |
|----|--------|--------|
| `ps-x-01-no-close-ports` | Не закрывать продукт-порты «как в статье» | ✅ политика в §0B + admin plan |
| `ps-x-02-no-aperture-vault` | Aperture ≠ vault BOT/LAVA/WG | ✅ политика |
| `ps-x-03-no-bonsai-ios` | Bonsai не в iPhone app без отдельного ТЗ | ✅ политика |
| `ps-x-04-no-graft-always` | trailhq Graft не constantly-on без ROI | ✅ политика |
| `ps-x-05-commit-docs` | Коммит docs/skills стека — только по просьбе владельца | ✅ 2026-09-22 |

---

## Связанный горизонт (другие id, не `ps-*`)

| ID | Трек | Статус |
|----|------|--------|
| `asm-r-06` | Asmadey B3 anti-slop | ⬜ |
| `asm-r-07` | Asmadey B4 hypothesis | ⬜ |
| Voice DEVICE | P0+P2 G6 владельцем | ⬜ вне Cursor TODO агента |

---

## Журнал

| Дата | Событие |
|------|---------|
| 2026-09-21 | Docs D0 ✅ · registry создан · Cursor TODO `ps-*` |
| 2026-09-21 | Старт работ: `ps-b-00` ✅ · `ps-b-01` ✅ (Intel 16GB!) · `ps-a-00` ✅ · Levels разбор отложен внедрять |
| 2026-09-21 | Phase 0 MAIN+Brain ✅ · Tailscale 1–5 + dual-path + smoke ✅ |
| 2026-09-21 | Orch vs Bonsai analysis ✅ `docs/PILOT_STACK_ORCH_VS_BONSAI_*.md` · Bonsai install **пауза** (рекомендация: Ollama mid-size сначала) |
| 2026-09-21 | Disk plan ✅ · TODO `ps-d-*` `ps-o-*` |
| 2026-09-21 | **Решение:** max quality = **Bonsai 2 27B only** · Ollama mid deferred · plan `PILOT_STACK_LOCAL_LLM_DISK_PLAN` обновлён |
| 2026-09-22 | Bonsai install ✅ · owner smoke ~0.5 tok/s · **Bonsai УДАЛЁН** с Disk (GO владельца) · wire не делать |
| 2026-09-22 | `ps-x-05` commit Pilot Stack docs (GO владельца) · Aperture = поздний · Graft = GO отдельно |
| | **Открыто:** `ps-c-02` Graft · `ps-a-10` SSH later · `ps-a-11` Aperture later · опц. qwen3:4b |

## Отложенный трек (после Pilot Stack)

| ID | Задача | Статус |
|----|--------|--------|
| `ps-levels-diy-scraper` | Levels DIY: разбор+решение ✅ · код worker — после `ps-*` + отдельный GO | 📋 `docs/PILOT_STACK_LEVELS_DIY_DEFERRED_2026-09-21.md` |

---

*Конец registry. Закрытие задач — merge:true только по id.*
