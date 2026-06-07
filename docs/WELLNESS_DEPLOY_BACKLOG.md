# Wellness + Companion — очередь деплоя (одним прогоном)

> **PO:** деплой **не сейчас** — после закрытия нужного по `WELLNESS_ROADMAP_100.md` и todo `r100-*`.  
> **Сервер:** `root@149.154.65.180`, `/opt/aladdin-backend`, ключ `~/.ssh/aladdin_server`  
> **Prod:** https://aladdin-ai.ru

---

## 1. Backend (VPS)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/deploy_wellness_batch4.sh root 149.154.65.180 ~/.ssh/aladdin_server
# при необходимости полный wellness P1:
# ./scripts/deploy_wellness_p1.sh root 149.154.65.180 ~/.ssh/aladdin_server
./scripts/deploy_companion_p0.sh root 149.154.65.180 ~/.ssh/aladdin_server
```

**Что уйдёт на prod (накоплено, батч 3–4):**

| Область | Файлы / папки |
|---------|----------------|
| Knowledge Pack | `wellness_knowledge/{cognitive,behavioral,humanistic,jung}/v1/pack.yaml` — flavor, exercise `instruction` |
| Wellness API | `wellness_router.py` — `pillar_fatigue` в `POST /outcomes` |
| Companion chat | `ai_companion_router.py` — drift log `wellness_pillar_drift`, taglines героев |
| Sprint 3 (если ещё не на VPS) | `wellness_age_policy.py`, `reflective_modes_v1.json` — `deploy_wellness_sprint3_age_i18n.sh` |

**После restart:**

```bash
./scripts/verify_wellness_prod.sh https://aladdin-ai.ru
./scripts/verify_wellness_reflective_prod.sh
```

**Не в этом деплое (батч 7):** OpenRouter / Hermes keys, Parent LLM `llm_used`, **Rive** (3× `.riv` только iOS bundle — [RIVE_MASTER_PLAN.md](./RIVE_MASTER_PLAN.md)), sleep CDN. Clinical ✅.

---

## 2. iOS (TestFlight / device)

Собрать билд с локальными изменениями:

| Фича | Экран / файл |
|------|----------------|
| Recap над чатом | `CompanionConversationScreen.swift` |
| Memory chips (consent) | то же |
| Outcome → смена дорожки / fatigue hint | `WellnessOutcomeSheet.swift` |
| Embedded wellness nav | `NavigationManager.finishWellnessFlow` + `WellnessHubScreen` + `CompanionHomeScreen` |
| Check-in → CTA герою | `WellnessCheckinScreen` + banner в чате |
| Голос reconnect | `CompanionVoiceSession` + `CompanionDialogueStrip` + `CompanionConversationScreen` |
| Embedded nav | `NavigationManager.finishWellnessFlow` |
| Герои taglines / стили | уже в репо (батч 3) |

**Ручной smoke (r100-0-05):** Companion → вкладка Wellness → упражнение → outcome → назад на Hub **внутри** «Мир героев» (не Main).

---

## 3. Чеклист «готово к деплою»

- [ ] Батч 4 закрыт в todo (`r100-4-*`)
- [ ] Батч 5 по решению PO (streaming/voice) или отложен
- [ ] `pytest` wellness green локально
- [ ] PO подтвердил: деплоим одним прогоном

---

*Обновлено: 2026-06-03. Связано: `WELLNESS_ROADMAP_100.md` §7в.*
