# План доработок Companion до 100% (без Rive и без 12 отложённых QA/gates)

**Обновлено:** 2026-05-29  
**Для кого:** команда, следующая ML-система  
**Главный handoff:** [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md)

---

## 1. Текущее состояние одной фразой

| Что | Статус |
|-----|--------|
| Код в репозитории (49 задач CODE v2) | ✅ локально (часть не в git) |
| GitHub `master` | ⏳ до коммита `771340a3` только спринты 1–3 |
| Сервер aladdin-ai.ru | ⏳ спринты 4–5 **не выкатаны** |
| TestFlight 214 | ⏳ без спринтов 4–5 и stream-fix |
| «100% без Rive» | ⏳ после этапов 1–3 ниже |

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

## 3. Этап 1 — Критично (1–2 дня) «чтобы фичи дошли до пользователя»

| # | Действие | Файлы | Критерий готово |
|---|----------|-------|-----------------|
| 1.1 | **Stream → сервер:** `chat_mode`, `workspace_id`, `attachments` | `CompanionStreamingService.swift`, `ai_companion_router.py` `CompanionStreamRequest` | pytest + ручной: режим «вдумчивый» влияет на ответ |
| 1.2 | **Commit + push** все Sprint 4–5 + stream + Child Rewards card | git | `git log` содержит один явный коммит |
| 1.3 | **Деплой VPS** | `scripts/deploy_companion_p0.sh` | `verify_companion_p0_prod.sh` PASS |
| 1.4 | **Проверка API на проде** | curl / health | `GET /api/ai/companion/domains` 200 |
| 1.5 | **iOS build 215** + TestFlight | bump `CFBundleVersion`, Archive | TF установлен на тестовый iPhone |
| 1.6 | **Smoke на устройстве** (короткий) | — | Друзья → чат → chips → режим → ответ |

**После этапа 1:** спринты 4–5 на сервере и в TF; stream не обрезает поля.

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

| Пункт | Цель 100% | Шаги |
|-------|-----------|------|
| Redis + хранилище | Stream cache на Redis в проде | `COMPANION_STREAM_CACHE_BACKEND=redis`, `REDIS_URL` на VPS |
| Оркестратор | Проверен на staging | `COMPANION_USE_ORCHESTRATOR=1`, smoke chat |
| Темы «О чём поговорим?» | Chips грузятся с прода | domains API + iOS `fetchLifeDomains` |
| Мост к людям | Баннер после 2+ lonely turns | E2E teen/senior фраза «мне одиноко» |
| Teen playbook | Подсказки в ответе | pytest + manual teen JWT |
| Trust за эмпатию | +4 за loneliness в UI trust | проверить `trust_delta` в stream meta |

**Postgres:** остаётся SQLite MVP до отдельного проекта; в доке зафиксировать «не блокер 100% без Rive».

---

## 6. Этап 4 — Спринт 5 (14 пунктов) до 100% MVP

| Пункт | MVP 100% | Не делаем сейчас |
|-------|----------|------------------|
| Поиск + ссылки | Флаг + честная дока «MVP citations» | Реальный Search API — опционально P2+ |
| Режимы Fast/Think | Stream + menu + видимая разница таймаута/ответа | — |
| Фото/PDF | `PhotosPicker` + лимит 400KB + BE validate | Vision model |
| Trust decay/streak | streak в UI из meta | — |
| Семья в промпте | Всегда в stream path | — |
| Tools list | `tools_used` в ответе | Полный OpenAI Responses |
| COGS | Строка в «Моё» для родителя | Биллинг-dashboard |
| 60+ с Main | Карточка + `senior` age band | — |
| Картинки/видео | Дока «stub, flag off» | Генерация в Family |
| Workspaces | UI: список + создать папку | Полный folders UX |
| Длинный контекст | Recap при >24 сообщениях | LLM summarization |
| Android / Adult | Доки актуальны | Отдельные репо |

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

1. Прочитать [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md)  
2. Этап 1 (stream уже в коде — проверить и закоммитить)  
3. Deploy + verify  
4. TF 215  
5. Этапы 2–4 по таблицам  
6. **Не начинать** Rive 07 / GATE-DIALOG без запроса PO

---

## 9. Определение «готово на 100% (без Rive)»

- [ ] Все 49 CODE задач в `master` и на VPS  
- [ ] TF build ≥215 с stream + спринты 4–5  
- [ ] Блок G проверен на device  
- [ ] Спринт 4: 6/6 MVP критериев  
- [ ] Спринт 5: 14/14 MVP критериев (stubs задокументированы)  
- [ ] pytest companion зелёный  
- [ ] verify_companion_p0_prod PASS  

*12 отложённых задач — отдельный трек после PO.*
