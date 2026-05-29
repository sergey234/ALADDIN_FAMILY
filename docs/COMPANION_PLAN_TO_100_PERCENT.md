# План доработок Companion до 100% (без Rive и без 12 отложённых QA/gates)

**Обновлено:** 2026-05-29 (после deploy VPS)  
**Для кого:** команда, следующая ML-система  
**Главный handoff:** [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md)  
**Runbook Этап 2–3:** [COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md)

---

## 1. Текущее состояние одной фразой

| Что | Статус |
|-----|--------|
| Код в репозитории (49 задач CODE v2) | ✅ `master` **`351a9b03`**, build **215** |
| Сервер aladdin-ai.ru | ✅ Sprint 4–5 задеплоены 2026-05-29 |
| Verify прод | ✅ 17 шагов, 3 героя всем, `/domains` `/cogs` `/workspaces` |
| TestFlight 215 + smoke | ✅ (2026-05-29) |
| Sprint 4–5 MVP код+VPS | ✅ [cursor todo](./COMPANION_CURSOR_TODO_STAGE2_3.md) |
| TestFlight **216** | ⏳ COGS, workspaces, вложения |
| «100% без Rive» | ⏳ TF216 + [12 задач](./COMPANION_WHAT_REMAINS.md) (Rive/GATE) |

**12 задач не трогаем в этом плане:** production `.riv` ×3, device QA 11b/11c, UX-14b, Figma↔Rive (P2-09), A/B humor (P2-17), контрольные GATE-*.

---

## 2. Что уже сделано (~90 из 102) — см. handoff

Полный список блоков A–L (простым языком) — в [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md) §3.

Сводка цифр (источник правды — [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)):

| Блок | Готово | Всего |
|------|--------|-------|
| Базовый MVP | 19 | 19 |
| Функции чата | 11 | 11 |
| «Живой» компаньон | 6 | 6 |
| Операции | 4 | 4 |
| Три героя / Rive prep | 24 | 26 |
| Продакшен-улучшения | 11 | 12 |
| Расширение чата (фаза B) | 16 | 17 |
| Долгосрочные фичи (фаза C) | 6 | 6 |
| Adult backend (доки) | 3 | 3 |
| **Итого** | **90** | **102** |

---

## 3. Этап 1 — Критично «чтобы фичи дошли до пользователя»

| # | Действие | Критерий | Статус |
|---|----------|----------|--------|
| 1.1 | Stream: `chat_mode`, `workspace_id`, `attachments` | verify шаг **12b** | ✅ |
| 1.2 | Commit + push Sprint 4–5 | `351a9b03` | ✅ |
| 1.3 | Деплой VPS | `deploy_companion_p0.sh`, service active | ✅ 2026-05-29 |
| 1.4 | Verify прод | 17 шагов exit 0 | ✅ |
| 1.5 | iOS build **215** + TestFlight | Archive → App Store Connect | ✅ 2026-05-29 |
| 1.6 | Smoke device | Друзья → чат → chips → режим | ✅ 2026-05-29 |

**После этапа 1 полностью:** TF215 на тестовых iPhone.

---

## 4. Этап 2 — Блок G (UX «Мир героев») до 100%

| # | Задача | Сейчас | Доделать |
|---|--------|--------|----------|
| G.1 | Три героя везде | ✅ | — |
| G.2 | Карточка «Мир героев» на Rewards | ✅ код | Убедиться в **build 215** (видна родителю и ребёнку) |
| G.3 | Кнопка «Друзья» | ✅ | — |
| G.4 | Питомец → чат | ✅ | — |
| G.5 | Старые экраны → Home | ✅ | — |
| G.6 | Mic coach + hold для детей | ✅ | — |
| G.7 | Сообщение «закрой другого помощника» | ✅ | — |
| G.8 | Чистый overlay у ребёнка | ✅ | — |
| G.9 | RU/EN + VoiceOver | ✅ | — |

**Критерий 100% блока G:** все входы ведут в `companionHome`, карточка Rewards в TF215, mic coach на device OK.

---

## 5. Этап 3 — Спринт 4 (6 пунктов) до 100% MVP

> **Полная таблица с командами VPS:** [COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md) § Sprint 4

| # | Пункт | Действие для 100% MVP | Проверка | Статус |
|---|--------|------------------------|----------|--------|
| 4.1 | Redis | `COMPANION_STREAM_CACHE_BACKEND=redis` + `REDIS_URL` в `/opt/aladdin-backend/.env`, restart | stream resume после обрыва | ⏳ |
| 4.2 | Orchestrator | `COMPANION_USE_ORCHESTRATOR=1` smoke, затем решение PO | 3 режима chat без 500 | ⏳ |
| 4.3 | Темы chips | API ✅ · iOS TF215 `fetchLifeDomains` | chips над полем ввода | ⏳ |
| 4.4 | Social bridge | E2E 2+ «одиноко» | `show_social_bridge: true` в meta | ⏳ |
| 4.5 | Teen playbook | `pytest Tests/test_companion_sprint4.py` | teen JWT manual | ⏳ |
| 4.6 | Trust эмпатия | lonely turn | `trust_delta` в stream `done` + UI | ⏳ |

**Postgres:** SQLite MVP — **не блокер** «100% без Rive».

---

## 6. Этап 4 — Спринт 5 (14 пунктов) до 100% MVP

> **Полная таблица:** [COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md) § Sprint 5

| # | Пункт | MVP 100% | Не сейчас | Статус |
|---|--------|----------|-----------|--------|
| 5.1 | Поиск + ссылки | флаг + дока «MVP citations» | реальный Search API | ⏳ |
| 5.2 | Режимы fast/think | stream + меню + видимая разница | — | ⏳ device |
| 5.3 | Фото/PDF | PhotosPicker + лимит + BE validate | vision model | ⏳ |
| 5.4 | Trust streak | UI из `trust_streak_days` в done meta | — | ⏳ |
| 5.5 | Семья в промпте | stream path = тот же core что `/chat` | — | ⏳ audit |
| 5.6 | Tools list | `tools_used` в ответе (опц. UI) | полный Responses API | ⏳ |
| 5.7 | COGS | строка в «Моё» родителя (`GET /cogs` ✅) | биллинг | ⏳ iOS |
| 5.8 | 60+ с Main | карточка Main + senior band | — | ⏳ TF |
| 5.9 | Картинки/видео | stub + flag off в доке | генерация | ⏳ doc |
| 5.10 | Workspaces | UI список/создать (`API` ✅) | полный folders UX | ⏳ iOS |
| 5.11 | Long context | recap при >24 сообщениях | LLM summary | ⏳ |
| 5.12 | Android | `docs/android/` актуален | отдельное репо | ✅ |
| 5.13 | Adult | `docs/adult/` актуален | отдельное app | ✅ |
| 5.14 | Adult policy | `test_adult_companion_policy.py` | — | ✅ |

---

## 7. Этап 5 — Автотесты и документы

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 -m pytest Tests/test_companion*.py Tests/test_adult_companion_policy.py -q
# цель: 80+ passed, 0 failed
```

Обновить после деплоя:

- `COMPANION_PROGRESS_TRACKER.md` — дата деплоя, build 215
- `COMPANION_CODE_TODO_TRACKER.md` — секция «В проде»
- Этот файл — отметить этапы `[x]`

---

## 8. Порядок работ для ML-системы (кратко)

1. [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md) §0  
2. **[COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md)** — главный чеклист  
3. TestFlight **215** (если не в сторе)  
4. Этап 3 (Sprint 4) → Этап 4 (Sprint 5) → Блок G на device  
5. **Не начинать** Rive 07 / GATE-DIALOG без PO  

**Рабочая папка:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

---

## 9. Определение «готово на 100% (без Rive)»

- [x] Все 49 CODE задач в `master` и на VPS  
- [x] verify_companion_p0_prod PASS (17 шагов)  
- [ ] TF build ≥215 на device  
- [ ] Блок G проверен на device  
- [ ] Спринт 4: 6/6 MVP критериев  
- [ ] Спринт 5: 14/14 MVP критериев (stubs задокументированы)  
- [ ] pytest companion зелёный  

*12 отложённых задач — отдельный трек после PO.*
