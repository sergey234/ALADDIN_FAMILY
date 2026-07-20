# HANDOFF: Wellness «тёплый проводник» (гибрид A+B, C gated)

**Дата:** 2026-07-20 (rev: As-built, merge Guide↔PSYCH, scope cleanup, 6 шляп; Cursor todos sync)  
**Для:** другая ML / агент  
**Канон iOS:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Связь:** отдельный трек от [HANDOFF_HYBRID_RARE_APPS_UNICORN_20260720.md](./HANDOFF_HYBRID_RARE_APPS_UNICORN_20260720.md) — **не блокировать** Unicorn P1.7+  
**Cursor todos:** те же id `psych-*` (§8); следующий Gap = `psych-01c`  
**Фундамент:** ADR-WELLNESS, Hub 4 столпа, `[WELLNESS v1]`, ethics L0–L3, Reflective / `reflective_modes_v1.json`, DigitalPsychologyLibrary, Companion LLM, `[PSYCH v1 internal]`, `wellness_guide_role.py`

---

## 0. Вердикт (не менять без продуктового решения)

| Решение | Правило |
|---------|---------|
| Роль | **Тёплый проводник самоисследования** — НЕ психотерапевт / психоаналитик |
| Гибрид | **A+B сейчас**, **C позже** (reflective + teen+ + clinical review) |
| Кто отвечает | **Companion LLM** под **фиксированным** system prompt + packs + ethics — не «живой психолог» |
| Промпт | **Версионируем мы** (`wellness_guide_role.py` + packs). Модель **не** генерирует новый «идеальный промпт» |
| Режимы A | Меняют **только session instruction** — **не** роль и **не** `primary_pillar` (см. §3.1) |
| Итог B | **Структурированный sheet** (понял / понаблюдать / шаг) — не свободный абзац |
| Челлендж | **Опциональный** CTA после шага — только если Family challenges доступны; XP только от Done |
| Награды | Unicorn **только** за шаг Done / дыхание / check-in — **не** за длину чата |
| Таймер | **Нет жёсткого cutoff 12 мин.** Опц. soft nudge «подведём итог?» (`psych-04b`) — или без таймера |
| Экраны | Sheet режимов + sheet итога; вход на Hub/Companion |
| i18n / nav | RU+EN; `goBackToPreviousScreen` / wellness `returnTo` |
| Scope этого MD | Только проводник A+B (+ C gated). Звук дыхания / медали серий воды — **другие треки** (см. §4) |

**Не делать:** генератор viral prompt; EMDR-сессии; детский IFS; клинические графики; диагнозы; медали за «терапию»; mode → auto pillar switch.

---

## 1. As-built (что уже в репо — не переписывать с нуля)

| Компонент | Путь / факт | Статус |
|-----------|-------------|--------|
| Guide role (фиксированный) | `security/services/ai_platform/wellness_guide_role.py` (`GUIDE_ROLE_VERSION`) | ✅ |
| PSYCH v1 internal | `companion_psychology.py` + `companion_knowledge/psychology/v1/internal.yaml` | ✅ |
| Сборка в router | `ai_companion_router.py`: `build_psych_internal_block` + `build_guide_role_block` (если flag ON) | ✅ оба; **merge-правило → §3.2** |
| Feature flag | `feature_flags.py`: `FEATURE_WELLNESS_GUIDE_MODES` default **True**; client `WellnessGuideSessionStore` | ✅ |
| Mode sheet A | `WellnessGuideModeSheet.swift` + ids как в `reflective_modes_v1.json` | ✅ |
| Mode store | `WellnessGuideSessionStore.swift` (default `structured_view`; child → `presence`) | ✅; **persist → доработать §3.3** |
| CTA «Поговорить бережно» | `WellnessHubScreen.swift` | ✅ |
| Session close B | `WellnessSessionCloseSheet.swift` (поля + CTA дыхание/check-in/челлендж) | ✅ UI; челлендж **не** feature-gated ещё |
| Presence nudge L1+ | Hub banner + `applyPresenceNudgeIfNeeded` | ✅ soft |
| Тесты роли | `Tests/test_wellness_guide_role.py` | ✅ |
| Soft 12-min nudge | — | ❌ нет (и **не** hard cutoff) |
| Mode ≠ pillar enforced | JSON modes ещё имеют поле `pillar` | ⚠️ контракт дописать в коде/тестах |
| SSOT modes JSON↔Swift | Swift `allModes` hardcoded + JSON | ⚠️ тест на совпадение id |

**Правило агента:** сначала читать As-built; новый код только в Gap / открытых тикетах.

---

## 2. Сверка с анализом 2-й ML

| Утверждение | Вердикт |
|-------------|---------|
| Hub 4 столпа, ethics, library, child урезан | ✅ |
| Режимы в `reflective_modes_v1.json` — подключить UX, не плодить словарь | ✅ (UI есть; SSOT-тест — Gap) |
| Слить Guide + PSYCH без двух «личностей» | ✅ контракт §3.2 |
| A+B сейчас, C позже; не копировать viral как role | ✅ |
| XP не за чат | ✅ |
| Дыхание после сессии нужно | ✅ CTA в close sheet; **звук** — не этот MD |

---

## 3. Контракты (критично)

### 3.1 Mode overlay ≠ pillar switch

- Выбор режима (`presence` / `structured_view` / `deep_explore` / …) меняет **только** `session_instruction` / `guide_mode=…` в prefix.
- **Не** меняет `primary_pillar`, **не** ломает session pillar lock.
- Поле `pillar` в `reflective_modes_v1.json` = подсказка для deep-link «открыть столп» (если продукт явно зовёт), **не** auto-switch при выборе режима в Guide flow.
- Иначе «Разбери глубоко» тихо утащит в Jung ≈ преждевременный C.

### 3.2 Merge: Guide + PSYCH v1 (оба оставляем)

| Блок | Отвечает за |
|------|-------------|
| **`[WELLNESS GUIDE …]`** (`wellness_guide_role.py`) | Кто ты (проводник), принципы, forbidden claims, **режим сессии** |
| **`[PSYCH v1 internal]`** (`companion_psychology.py`) | Как слушать (лестница), max вопросов, distortion hints, depth_gear |
| **`[WELLNESS v1]`** (pillar pack) | Столп / упражнение / hero flavor |

**Приоритет при конфликте:**

1. **Ethics / escalation L2–L3** — оба guide и psych пустые / crisis path (уже так).  
2. **Guide role** побеждает по **идентичности** (не терапевт, не лечу, не EMDR, не диагноз).  
3. **PSYCH v1** дополняет **технику** (mirror → validate → один вопрос; hints), не переписывает роль.  
4. **Mode instruction** (из Guide) побеждает над общим «deepen» PSYCH, если режим = `presence` или `single_question`.  
5. Pillar pack не добавляет therapy claims.

**Итог личности:** один голос = проводник + хорошая техника слушания.  
PSYCH **не удаляем**.

Порядок в prompt assembler (рекомендация): ethics → Guide → PSYCH → WELLNESS pillar → user.

### 3.3 Persist режима

- **Новая** guide-сессия: default = `structured_view` (child = `presence`).
- Не стартовать автоматически с вчерашнего `deep_explore` / `blind_spots` из sticky UserDefaults.
- «Запомнить последний выбор» — опционально и только внутри активной сессии или явной настройки; не затягивать в тяжёлый режим по инерции.

### 3.4 Таймер ~12 мин

- **Убрать** жёсткий cutoff из архитектуры v1.
- Опционально `psych-04b`: soft nudge «уже около 12 мин — подведём итог?» → открыть close sheet. Чат **не** обрывать.

---

## 4. Настройки / флаги (только этот продукт)

| Что | Где | Default |
|-----|-----|---------|
| `FEATURE_WELLNESS_GUIDE_MODES` | `feature_flags.py` + client store | **ON** (как в коде); выключить `=0` без отката |
| Disclaimer «не замена специалисту» | вход сессии | всегда |
| Режим сессии | sheet; reset default на **новую** сессию | взгляд / child рядом |
| Child: только `presence` | ageBand | auto |
| CTA челлендж после шага | sheet B | **только если** Family challenges доступны |
| C части/тело | отдельный flag | OFF |

**Не в этом MD (другие треки — не тикеты `psych-*`):**

| Тема | Где живёт |
|------|-----------|
| CTA «дыхание» / check-in после сессии | ✅ этот трек (`psych-05`) |
| Звук/аудио дыхания | Wellness exercise track |
| Медали серий воды/лекарств | Family / Unicorn handoff |
| Unicorn P0 rare apps | отдельный handoff — **не блокировать** |

Отдельный «экран всех психо-настроек» в v1 **не обязателен**.

---

## 5. Гибрид A+B (C gated)

```
«Поговорить бережно»
  → A: режим (default = взгляд со стороны; child = рядом)
  → mode overlay ≠ pillar switch
  → ethics → Guide → PSYCH v1 → [WELLNESS v1]
  → B: «Завершить» → понял · понаблюдать · шаг
       (опц. soft nudge ~12 мин — без обрыва)
  → шаг → if-then / дыхание / check-in
  → опц. FamilyChallenge (feature-gated)
  → XP только с Done действия
  → C: flag + teen+ + review — отдельно
```

**Улучшения:** emotion/L1+ → nudge «рядом»; flag с `psych-00`; disclaimer на входе.

---

## 6. Шесть шляп (сжатый аудит продукта)

| Шляпа | Вывод |
|-------|--------|
| **Белая** | Hub, packs, ethics, Guide role, PSYCH, sheets уже есть; Gap: merge-тест, mode≠pillar, session reset, challenge gate, soft nudge |
| **Красная** | Люди хотят тепло «как в промпте»; страх «бот лечит» снимаем ролью проводника |
| **Чёрная** | App Store «терапевт»; mode→Jung; sticky deep; фарм XP за чат; challenge как обязаловка |
| **Жёлтая** | A+B = вау на текущих экранах; прогресс через шаг/дыхание/check-in |
| **Зелёная** | Soft nudge вместо cutoff; challenge optional; Guide>PSYCH по роли |
| **Синяя** | Добить Gap-тикеты; C не мешать P0 Unicorn; не раздувать MD чужим scope |

---

## 7. Метод из промпта vs опасно

**Золото:** исследовать > чинить; режимы; 1–3 вопроса; факт/интерпретация; опора first; итог; осознание ≠ изменение; не романтизировать боль; контекст (сон, нагрузка).

**Опасно дословно:** психотерапевт 20+; EMDR проводим; полный IFS/травма-сессия; психоанализ; «лечу психику».

---

## 8. Тикеты Cursor (`psych-*`)

| Id | Статус | Работа | DoD |
|----|--------|--------|-----|
| `psych-00` | ✅ | Контракт: проводник; не терапевт; RU+EN; returnTo; flag; child; нет генератора промптов; **mode≠pillar**; **merge Guide↔PSYCH** | as-built в MD+коде |
| `psych-01` | ✅ | Фиксированный role+principles+forbidden в `wellness_guide_role.py` | LLM не «психотерапевт»; не генерится моделью |
| `psych-01b` | ✅ | Тест forbidden + «кто ты?» → проводник | `test_wellness_guide_role.py` |
| `psych-01c` | ✅ | Enforce merge: Guide identity > PSYCH; presence/one_q бьёт deepen; unit на конфликт | `merge_guide_over_psych` + tests |
| `psych-02` | ✅ UI / ⚠️ SSOT | Sheet режимов; ids = JSON; default взгляд; **instruction only** | UI + `guide_mode=`; тест id Swift↔JSON; **нет** pillar switch |
| `psych-03` | ✅ | CTA «Поговорить бережно» + disclaimer; child урезан | ≤2 тапа |
| `psych-04` | ✅ UI | «Завершить» → структурированный sheet | не essay |
| `psych-04b` | ❌ optional | Soft nudge ~12 мин → предложить итог; **без** hard cutoff (**в scope**) | баннер/sheet; чат жив |
| `psych-05` | ⚠️ partial | Шаг → if-then; CTA дыхание/check-in; XP только Done | нет XP за чат; if-then из close надёжно |
| `psych-05b` | ⚠️ UI always | CTA челлендж **optional / feature-gated**; **depends on Unicorn `p2-9h`** | скрыть если challenges нет; не до P1.7+1.8 |
| `psych-06` | ✅ soft | L1+ → nudge «рядом» | баннер / accept → presence |
| `psych-07` | ❌ P2 | C части/тело reflective+teen+ review; не child/EMDR | flag OFF |
| `psych-08` | ✅ | Flag `FEATURE_WELLNESS_GUIDE_MODES` (default ON; `=0` выкл) | выключается без отката |
| `psych-09` | ❌ Gap | Persist: reset default mode на **новую** сессию | не sticky deep |

**Порядок (остаток):** `00` контракт в PR → `01c` merge → `02` SSOT + no pillar switch → `09` session reset → `05` добить if-then → **`05b` только после `p2-9h`** → опц. `04b` → `07` позже.

**Не стартовать с нуля:** `01`, `01b`, `03`, `04` UI, `06`, `08`.

---

## 9. Связь с Единорог / челленджи

| Можно | Нельзя |
|-------|--------|
| После B: Done дыхание / check-in / шаг / (опц.) челлендж → Unicorn | XP за сообщения в чате |
| Челлендж как опциональный хвост | Обязать челлендж чтобы закрыть сессию |
| Параллелить с Unicorn P0 | Блокировать / переписывать Unicorn P0 этим треком |

---

## 10. Инструкции агенту

1. Не раздувать Unicorn P0 этим треком.  
2. Не копировать viral prompt дословно.  
3. Не добавлять runtime «prompt generator».  
4. **Оба** Guide и PSYCH — по §3.2; не плодить третий словарь ролей.  
5. Mode ≠ pillar switch (§3.1).  
6. Не тащить сюда ТЗ звука дыхания / медалей серий — CTA дыхания оставить.  
7. L3 + crisis CTA сохранить.  
8. PR: RU+EN + disclaimer + ageBand.  
9. Читать §1 As-built перед кодом.

**Конец handoff.**
