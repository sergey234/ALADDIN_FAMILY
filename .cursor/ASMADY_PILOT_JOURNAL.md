# Asmadey pilots journal (волна A — `asm-r-01`…`03`)

**Дата:** 2026-09-19  
**Канон skills:** `aladdin-gates` · `aladdin-humanizer-ru` · `aladdin-ajtbd`  
**План:** [`ASMADY_SKILLS_REMAINING_PLAN.md`](ASMADY_SKILLS_REMAINING_PLAN.md)

---

## `asm-r-01` — GATES на Voice Safety Log (P2 / регресс)

**Задача:** закрытие критериев готовности Voice Safety Log P2 (не новый код — проверка доказательств).

### GATES

| # | Gate | Доказательство | Результат |
|---|------|----------------|-----------|
| G1 | Нет EventKit / EKEvent в Voice Safety / Widgets | `rg EventKit\|EKEvent` по `ALADDINWidgets/` + Voice paths — пусто | ✅ PASS |
| G2 | Нет фонового poll UIPasteboard / changeCount в Widgets | `rg UIPasteboard` в `ALADDINWidgets/` — пусто | ✅ PASS |
| G3 | Виджет читает App Group через SharedDataManager | `VoiceSafetyNowWidget` → `getVoiceSafetyWidgetData()` | ✅ PASS |
| G4 | Deep links weekly/log существуют | `CompanionDeepLinkRouter` `aladdin://voice/weekly` + `voice/log` | ✅ PASS |
| G5 | Теги идея/не забыть в коде | `intent_remind` / router в `Core/Voice`, `VoiceWeeklyDigestService` | ✅ PASS |
| G6 | Ручной QA на устройстве (виджет + неделя) | `docs/VOICE_SAFETY_LOG_P2_MANUAL_QA_RU.md` | ⬜ DEVICE (владелец) |

**Вердикт пилота:** skill полезен — без GATES легко «закрыть P2» без DEVICE.  
**Рекомендация:** `aladdin-gates` **on-demand** перед каждой фичей Voice/Antifake (не constantly в каждом чате).

---

## `asm-r-02` — Humanizer на App Review SHORT §2

**Файл:** `docs/AppStore/ALADDIN_AI_App_Review_Reply_SHORT_RU.txt`

### До

```
Семейная цифровая безопасность и воспитание: родители, дети, подростки, пожилые.
Проблема: мошенничество, риски в сети, нет семейных правил.
Ценность: Antifake, родительский контроль, закрытый семейный чат, обучение, AI-герои (Единорог, Аладдин, Джин), SaaS по подписке через Apple IAP.
```

### После (факты те же, тон живее)

```
ALADDIN AI — для семей: родители, дети, подростки и пожилые.
Родителям нужна защита от мошенничества и понятные правила в семье.
В приложении: Antifake, родительский контроль, закрытый семейный чат, обучение и AI-герои (Единорог, Аладдин, Джин); подписка только через Apple IAP.
```

**Вердикт:** полезен на App Review / Notes. **On-demand** при письмах Apple и OB-копирайте.

---

## `asm-r-03` — AJTBD: проверить ссылку / голос

1. **Работа:** когда ребёнок прислал сомнительную ссылку или родитель услышал подозрительный звонок, родитель хочет быстро понять риск, чтобы решить — блокировать / объяснить / игнорировать.  
2. **Триггер:** ссылка в чате / СМС / голос «проверь это».  
3. **Барьеры:** долго открывать Antifake; страх ложного срабатывания; непонятный вердикт.  
4. **Критерии найма:** за <2 минут: вставить/сказать → ясный риск + что делать дальше.  
5. **Acceptance:**  
   - [ ] Ввод: clipboard по тапу Check/Paste **или** голос → тот же Antifake pipeline  
   - [ ] Вердикт на языке родителя (не сырой JSON)  
   - [ ] Нет фоновой слежки за буфером / ребёнком  

**Решение UX:** Voice Safety Log остаётся **on-device helper** → существующий Antifake; не отдельный «шпионский» продукт.  
**Вердикт skill:** оставлять **on-demand** на дизайн Voice/Antifake/Family.

---

## Итог волны A

| ID | Статус | constantly? |
|----|--------|-------------|
| `asm-r-01` | ✅ (G1–G5; G6 device) | on-demand |
| `asm-r-02` | ✅ текст в SHORT применён | on-demand |
| `asm-r-03` | ✅ JTBD записан | on-demand |

---

## `asm-r-04` — Dual-review Voice Safety / Antifake (волна B1)

**Дата:** 2026-09-21  
**Skill:** `@aladdin-dual-review`  
**Цель:** код Voice Safety Log + ClipboardSafety + Antifake paste choke (не весь репо)  
**Проход 1:** swift-reviewer subagent  
**Проход 2:** dual-review (API / mock / secrets / blast / privacy pasteboard)

### Findings (подтверждены чтением кода)

| Sev | ID | Где | Суть | Dual-review note |
|-----|-----|-----|------|------------------|
| Critical | C-1 | `AntifakeTextCheckViewModel.hasClipboardContent` | Читает `UIPasteboard.general.string` → баннер iOS 16 на re-render | **Keep:** gate через `.hasStrings` |
| Critical | C-2 | `ClipboardSafetyService.process` | `looksLikeURL` true + `extractURL` nil → в `normalizeURL` уходит raw `trimmed` | **Keep:** один `let extracted = extractURL…` |
| High | H-1 | `VoiceNotesScreen` `asyncAfter(0.4)` | Race dismiss→Antifake | Product risk на медленных устройствах |
| High | H-2 | `VoiceSafetyNowStore.save` | Нет `@MainActor`, трогает WidgetCenter / LM | Data-race при off-main |
| High | H-3 | kill-switch `voiceIntentRouterEnabled` | Нет теста disabled path | Integrity/tests |
| High | H-4 | `makeAntifakePayload` clipboard | Чтение буфера после STT (by design «ссылка») | Privacy banner; не spy, но не «только по тапу» |
| — | Mock | — | `sfm_mock` / mock_fallback в этом контуре | **Не найдено** ✅ |
| — | Secrets persist | ClipboardSafety | OTP/token/seed → `.blockedSecret`, не пишется в history | **OK** ✅ |

### ROI вердикт

| | |
|--|--|
| **Полезных findings** | ≥2 Critical + несколько High — skill **оправдан** |
| **Решение** | **Keep on-demand** (перед релизом Voice/Antifake / risky diff) |
| **Constantly?** | Нет |
| **Фикс в этом чате** | Нет — по плану B: фикс Critical только после **GO владельца** |

**Предложение владельцу:** GO на минимальный фикс **C-1 + C-2** (без расширения scope на H-*).

### Фикс Critical (GO 2026-09-21)

| ID | Изменение | Файл |
|----|-----------|------|
| C-1 | `hasClipboardContent` → `hasStrings \|\| hasURLs` (без чтения `.string`) | `AntifakeTextCheckViewModel` |
| C-2 | URL-путь только при успешном `extractURL`; prose с hostname → plain `.ok(trimmed)` | `ClipboardSafetyService` |
| Tests | `testLooksLikeURLWithoutSingleExtract…` · `testBareHostStillNormalized…` | `ClipboardSafetyServiceTests` |

H-1…H-4 **не** чинились (вне GO).

---

## Итог волны B (прогресс)

| ID | Статус | constantly? |
|----|--------|-------------|
| `asm-r-04` | ✅ dual-review done | on-demand |
| `asm-r-05` | ⬜ ui-stress | ждать фразу |
| `asm-r-06` | ⬜ anti-slop | ждать фразу |
| `asm-r-07` | ⬜ hypothesis | ждать фразу |

`asm-50` / `asm-51` — по-прежнему ⏸ без GO.  
Волны C / E — только по запросу.
