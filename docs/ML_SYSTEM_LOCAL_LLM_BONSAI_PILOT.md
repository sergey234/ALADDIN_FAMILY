# Bonsai 2 / локальный LLM — пилот (гибрид C, слой Compute)

**Статус:** план + GO-чеклист · сравнение с Orch → [`PILOT_STACK_ORCH_VS_BONSAI_2026-09-21.md`](PILOT_STACK_ORCH_VS_BONSAI_2026-09-21.md) · **install на паузе** до выбора §6 там  
**Дата:** 2026-09-21  
**Вход:** [`docs/ML_SYSTEM_START_HERE.md`](ML_SYSTEM_START_HERE.md) §0B  
**Skill:** `@aladdin-local-llm`  
**Budget:** [`coding_orchestrator/docs/BUDGET_POLICY.md`](../coding_orchestrator/docs/BUDGET_POLICY.md)  
**Orch (диспетчер, не модель):** [`coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md`](../coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md)  
**Трекинг:** [`.cursor/PILOT_STACK_2026_TASK_REGISTRY.md`](../.cursor/PILOT_STACK_2026_TASK_REGISTRY.md) · Cursor TODO `ps-b-*`

---

## 0. Простыми словами

**Сейчас:** черновики агента часто идут в платные/облачные модели (Claude, Codex, API).  
**После пилота (если GO и ROI ок):** «подумай / набросай / посмотри код ночью» может делать **локальная** модель Bonsai 2 (~6 ГБ на диске) на Mac.  
**Не меняется:** ревью, parental, security, merge Approve — по-прежнему сильные модели + человек (Mech Pilot).

Это **не** замена Cursor и **не** модель внутри iPhone-приложения ALADDIN.

---

## 1. Что было → что будет

| Слой | Было (сегодня) | Будет после успешного пилота |
|------|----------------|------------------------------|
| Draft / explore / night cheap | Ollama (если стоит) или сразу дорогая модель | **Bonsai 2** (или совместимый local) в том же слоте budget |
| Implement | Claude / Codex | без изменений |
| Review / security / merge | strongest + human Approve | **запрещено** слать на Bonsai |
| iOS app product LLM | нет Bonsai в приложении | **не добавляем** без отдельного ТЗ |
| VPN / bot / порты | не трогаем | не трогаем |

---

## 2. Плюсы и минусы пилота

### Плюсы
- Дешевле ночные/черновые прогоны orch (меньше $ и токенов API).  
- Работает offline / без утечки черновика в облако (если не слать секреты в промпт — конституция всё равно).  
- Маленький вес (~5.9 ГБ) vs полный 27B (~54 ГБ) — реально на «обычном» Mac.  
- Сохраняет маршрутизацию Mech Pilot: пилот решает, когда local ок.

### Минусы / риски
- Нужен **их** runtime (fork llama.cpp / MLX) — обычный Ollama может не съесть веса корректно.  
- Качество ≠ Claude на сложных parental/security задачах → **только draft**.  
- Время на установку, бенч, сравнение с baseline (1–2 недели ROI).  
- Риск «агент сам решил всё на Bonsai» — закрываем skill + budget policy.  
- Не путать с продуктом: родители в app не должны зависеть от Bonsai.

---

## 3. Границы (конституция)

| Делать | Не делать |
|--------|-----------|
| Draft, explore, cheap night, offline brainstorm | Review / merge / parental / antifake API decisions |
| Сравнивать $/tokens vs baseline 1–2 недели | Constantly-on без ROI-вердикта |
| Писать вердикт keep/drop в journal | Тянуть Bonsai в iPhone app без ТЗ |
| Спросить GO перед install runtime / весов | «Закрыть порты» / Aperture / prod SSH «заодно» |

---

## 4. GATES пилота (до слова «готово»)

| # | Gate | Доказательство |
|---|------|----------------|
| G1 | Runtime умеет грузить Bonsai 2 27B (HF PrismML) | лог успешного `load` + один smoke prompt |
| G2 | Orch/budget: draft → local; review → premium | фрагмент config / BUDGET_POLICY + 1 smoke spawn |
| G3 | Нет секретов в промптах local | checklist: `.env` / VPN§32 не в контексте |
| G4 | Baseline 7 дней: tokens/$ и «переделки» vs без Bonsai | таблица в journal |
| G5 | Вердикт владельца: **keep** / **drop** / **narrow** | запись в `.cursor/ASMADY_PILOT_JOURNAL.md` или orch journal |

---

## 5. GO-чеклист владельца (по шагам)

**Фаза 0 — только документы (уже можно без GO железа)**  
- [x] Этот файл создан  
- [x] START_HERE §0B + skill `@aladdin-local-llm`  
- [x] BUDGET_POLICY: Bonsai = draft only  

**Фаза 1 — GO получен 2026-09-21: max quality = Bonsai narrow на Disk**  
- [ ] `sudo` каталог `/Volumes/Disk/ALADDIN_LOCAL_LLM/bonsai2/{bin,weights}`  
- [ ] PrismML llama.cpp → `bin/` (Intel CPU, `-ngl 0`)  
- [ ] Веса **PTQ1_0** (~5.95 ГБ) → `weights/`  
- [ ] Smoke + journal (tok/s, RSS)  
- [ ] Mini-verdict → только потом Фаза 2  

**Фаза 2 — нужен отдельный GO: «GO Bonsai orch wire»**  
- [ ] Подключить как endpoint в orch budget route `draft/explore`  
- [ ] Запрет маршрута `review` → local (тест: попытка должна reject)  
- [ ] Kill switch budget по-прежнему работает  

**Фаза 3 — ROI 1–2 недели**  
- [ ] Считать: API $ · число tool-calls · число follow-up правок пилота  
- [ ] Вердикт keep/drop  
- [ ] Если drop — выключить route, веса можно оставить offline  

**Не в этом пилоте**  
- [ ] trailhq Graft constantly-on  
- [ ] Tailscale / закрытие портов (отдельный план admin mesh)  
- [ ] Aperture как vault BOT/VPN  

---

## 6. Связанные слои гибрида C (не путать)

| Слой | Канон | Статус |
|------|-------|--------|
| **Context** (карта кода) | Repowise SSOT · опц. пилот trailhq Graft | Repowise ✅ · Graft внешний — только с GO ROI |
| **Compute** (эта страница) | Bonsai draft | план |
| **Admin mesh** | [`ADMIN_MESH_TAILSCALE_HYBRID_PLAN_2026-07-27.md`](ADMIN_MESH_TAILSCALE_HYBRID_PLAN_2026-07-27.md) | план, не внедрён |

Имена **Graft**:
- **orch `GraftQueue`** = очередь merge в Coding Orchestrator (**не** граф кода).  
- **trailhq/Graft** = npm-надстройка графа для агента (опц. пилот).  
- **Repowise** = наш граф/wiki для Cursor MCP.

---

## 7. Источники (внешние)

- HF collection: https://huggingface.co/collections/prism-ml/bonsai-2  
- Не коммитить веса в git. Не пушить в iOS release.

---

## 8. Фраза владельца (копипаст)

```text
Прочитай docs/ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md + @aladdin-local-llm.
GO Bonsai runtime (только Mac, draft only). Не трогай VPN/bot/порты. Коммит docs только если попросил.
```

Или только документы без железа:

```text
Без install: обнови journal/GATES по Bonsai пилоту. Железо не ставить.
```

---

*Конец. Внедрение железа — только после явного GO владельца.*
