# Review & Recommendations — Voice Safety Log Variant C

**Date:** 2026-09-18  
**For:** next ML system (implementer)  
**Base plan (SSOT product decision):** `docs/ML_SYSTEM_HANDOFF_VOICE_SAFETY_LOG_VARIANT_C_2026-09-18.md`  
**Repo root:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Status:** Plan review only · **no code until owner GO on P0**

---

## 0. Вердикт (коротко)

**Согласен с Variant C.** Это правильный путь для ALADDIN: защита семьи голосом + «проверить скопированное», лёгкий дневник сверху, без клона menu bar и без истории буфера.

Уверенность плана (~90% направление / ~85% P0) — честная. После сверки с кодом: **направление подтверждаю**, но в handoff есть **дыры, которые стоит закрыть до/во время P0**, иначе glue сломается на реальном UX (особенно sheet VoiceNotes → Antifake).

**Не переписывать базовый handoff.** Этот файл — дополнение: риски, варианты, acceptance, порядок работ.

---

## 1. С чем согласен (оставить как есть)

| Решение | Почему ок |
|---------|-----------|
| Variant C, не A/B/full VibeBar | Бренд family safety + reuse + ниже App Review risk |
| Glue, не новый движок STT | Уже есть `SpeechRecognizerFactory` + VoiceNotes |
| Clipboard Safety, не history ×15 | Правильный privacy story |
| Нет background `UIPasteboard` | Обязательный guard |
| Нет child spy / silent logging | Non-negotiable |
| Deterministic prefix router в P0 | Быстро, тестируемо, без сервера |
| TDD: router → clipboard → wire | Правильный порядок |
| P0 маленький, P1/P2 после usage | Не раздувать до доказанной ценности |
| `merge: true` на `vsl-c-*` | Не трогать другие TODO-треки |

---

## 2. Что проверить в коде (уже сверено)

Подтверждено в репо:

- `VoiceNotesViewModel` — `localOnlyModeEnabled` default **true**; после STT пишется только `transcriptPreview` (тегов/навигации от префикса **ещё нет** — место для router).
- `AntifakeTextCheckViewModel.pasteFromClipboard()` — читает pasteboard и сразу `applyPastedContent` (**без** sanitize/secret gate — место для ClipboardSafety).
- Навигация в Antifake уже есть: `NavigationManager.navigateToAntifakeShareCheck` / `navigateToAntifakeHub`.
- VoiceNotes открывается как **sheet** (`SettingsScreen`, `SimpleHomeScreen`) — **не** как обычный `ALADDINScreen`. Это критично для P0 wire.
- Share Extension / deep link путь в Antifake уже живой — sanitize должен быть **в одном choke point**, не только в кнопке Paste.
- В summary уже есть keyword-теги (`family`, `call`, …) — не путать с intent-тегами router.

---

## 3. Главные дополнения к плану (must / should / nice)

### MUST перед или в P0 (иначе баги)

#### M1. Навигация из sheet VoiceNotes → Antifake
**Проблема:** VoiceNotes часто modal sheet. `navigateTo(.antifakeHub)` «под» sheet = пользователь не увидит результат или застрянет.

**Рекомендация:** явный glue-контракт:
1. Router вернул `antifake_url` / `security_check` с payload  
2. Закрыть VoiceNotes sheet (или отложить dismiss)  
3. Затем `navigateToAntifakeShareCheck(payload:)`  
4. Toast: «Открываю проверку…»

Добавить acceptance **A9** (см. §6).

#### M2. Единый choke point для ClipboardSafety
Не только `pasteFromClipboard`. Прогонять sanitize/secret через:
- `pasteFromClipboard`
- `applyPastedContent` (если вызывается из Share / deep link с сырым текстом)
- любой новый «Проверить скопированное»

Иначе Share Extension обойдёт защиту.

#### M3. Порядок слоёв тегов (не дублировать смысл)
```
transcript OK
  → VoiceIntentRouter.parse  (intent tags: incident / idea / remind / …)
  → persist note (body policy — см. S2)
  → optional navigate Antifake
  → позже / отдельно: Summary + StructureService (semantic tags)
```
Router **не заменяет** StructureService. Structure **не должен** перетирать intent-теги.

#### M4. localOnly vs Antifake network
`localOnlyMode` = заметка/аудио локально. Переход в Antifake **осознанно** может бить в сеть.

**UX:** короткий copy: «Заметка остаётся на устройстве. Проверка ссылки идёт через защиту ALADDIN.»  
Не ломать `localOnlyMode` для самой VoiceNote.

---

### SHOULD (сильно повышает шанс, что фича живёт)

#### S1. Discoverability — мини-подсказка префиксов
Без подсказки родители не скажут «ссылка …».  
**P0.5 (1–2 часа UI):** один tip в VoiceNotes:  
«Скажите в начале: ссылка / проверка / тревога / идея / не забыть».  
Один раз, dismiss forever. Иначе P0 технически зелёный, продуктово мёртвый.

#### S2. Политика тела заметки
Зафиксировать в коде + тестах:
- **Хранить полный transcript** (как сказал пользователь)  
- **Intent** = prefix  
- **Body for Antifake / title** = remainder после prefix  
Не молча вырезать префикс из сохранённого текста без решения владельца (default выше — keep full).

#### S3. Устойчивость к ошибкам STT (RU)
On-device ru-RU часто коверкает начало фразы.

Минимум aliases в router (тесты обязательны):
| Слышит | Считать как |
|--------|-------------|
| ссылка / сылка / link / url | antifake_url |
| проверка / проверь / провери / check | security_check |
| тревога / срочно / alert | incident |
| не забыть / напомни / remind | remind |

Правило: **только leading tokens**, longest match first.  
Середина фразы («…проверка дома…») → **не** intent.

#### S4. Secret heuristics — конкретный список тестов
Не «password-like» в абстракции. Минимум unit cases:
- OTP: 4–8 цифр **и** контекст/короткий буфер (осторожно с телефонами)
- seed-like: 12/24 слова bip39-ish
- `sk-` / `Bearer ` / длинный base64 token
- банковская карта (Luhn) — warn, не persist  
Phone в Antifake contact mode — **не** считать OTP.

#### S5. Shortcut важнее Widget
В P1: **Siri Shortcut / App Intent «ALADDIN log»** раньше, чем Widget.  
Widget = App Groups, entitlements, дизайн — дороже при меньшей пользе на старте.  
**Рекомендация:** widget → optional P2, не P1 blocker.

#### S6. EventKit — явно OUT
В confidence table упомянут EventKit, в фазах — нет.  
**Зафиксировать:** EventKit **не в C** до отдельного GO. Иначе следующая система «додумает» календарь.

---

### NICE (после P0 green)

| ID | Идея | Зачем |
|----|------|-------|
| N1 | Privacy-safe intent counters (без audio/text) | Учить словарь 1–2 недели |
| N2 | Confirm chip «Открыть Antifake?» на сомнительный parse | Меньше ложных переходов |
| N3 | Elderly / SimpleHome entry point | ALADDIN — не только Settings sheet |
| N4 | Kill-switch UserDefaults `voiceIntentRouterEnabled` | Откат без релиза, если путает |
| N5 | Weekly digest — только security bullets сначала | Diary counts позже |
| N6 | «тревога» → optional Family Chat draft | Только после ответа владельца (§12 base) |
| N7 | App Review one-liner | Готовый текст для Guideline 2.1 про mic/clipboard |

---

## 4. Все разумные варианты продукта (карта развилок)

Использовать, если после P0 usage нужно pivot’нуть — **не** начинать с них.

| Код | Суть | Когда выбирать | Риск |
|-----|------|----------------|------|
| **C** (approved) | 80% security + 20% light diary | Default ALADDIN | Низкий |
| **C0** | Только router + tags, **без** Antifake navigate в P0 | Если sheet-nav сложный / нет времени | UX слабее |
| **C1** | C0 + ClipboardSafety + Antifake navigate | Нормальный полный P0 | То, что надо |
| **C-lite diary** | Security intents only; `idea`/`remind` отложить | Если бренд «размывается» | Ближе к A |
| **C+ coach** | C1 + tip префиксов + Shortcut | Лучший product P0.5 | Чуть больше UI |
| **A** | Security only | Owner хочет жёсткий shield | Теряем «мысль не потерялась» |
| **B** | Diary/productivity only | Почти никогда в ALADDIN | Wrong identity |
| **VibeBar port** | Menu bar + clipboard history | Никогда в iOS ALADDIN | Review + scope |
| **Pivot diary-first** | Если P0: родители не говорят security-префиксы | После 1–2 недель данных | Менять UI акцент, не архитектуру glue |

**Правило pivot:** менять **акцент UI и словарь**, не выкидывать router/clipboard services.

---

## 5. Уточнённый P0 (рекомендуемый порядок)

```
1. VoiceIntentRouter + tests (aliases, longest match, mid-sentence negative)
2. ClipboardSafetyService + tests (secrets, utm strip, phone≠OTP)
3. Wire choke point → applyPastedContent / paste / share payload
4. Wire VoiceNotes after successful transcript → tags + body policy
5. Sheet dismiss → Antifake navigate (M1)
6. One-shot coach tip (S1) — если owner согласен в том же GO
7. Acceptance A1–A12
8. Simulator/device build — только в конце фазы
```

Не начинать P1 (NowStatusChip / widget / digest), пока A1–A12 не зелёные или owner не сказал иначе.

### Доп. Cursor TODO (merge: true)

| ID | Content |
|----|---------|
| `vsl-c-p0-08` | Sheet dismiss → Antifake navigate glue |
| `vsl-c-p0-09` | Coach tip prefixes (optional same GO) |
| `vsl-c-p0-10` | ClipboardSafety on Share/deep-link choke point |
| `vsl-c-p0-11` | STT alias tests RU |
| `vsl-c-p1-03` | Shortcut **before** widget; widget demote optional P2 |

---

## 6. Acceptance — добавить к A1–A8

| ID | Check |
|----|--------|
| A9 | Из VoiceNotes sheet: «ссылка …» закрывает sheet и открывает Antifake с URL |
| A10 | «Сегодня проверка дома прошла» → обычная note, **не** security_check |
| A11 | Share Extension / share payload проходит sanitize/secret gate |
| A12 | Intent-тег не затирается последующим summary/structure |

---

## 7. Security / App Store — дополнения одной строкой

- Mic/Speech — только по жесту (уже в base).  
- Pasteboard — только on-demand (уже в base).  
- **Не** добавлять `UIPasteboard.changed` observer даже «для удобства».  
- Privacy labels: clipboard по-прежнему user-initiated check; не описывать как clipboard history.  
- Готовый Review answer (черновик):  
  *«Voice Safety Log is an on-device parent helper: spoken security intents route into existing Antifake check; clipboard is read only when the parent taps Check / Paste. We do not keep clipboard history or monitor the pasteboard in background.»*

---

## 8. Открытые вопросы владельцу (расширение §12 base)

Не блокируют старт router+tests, но блокируют «полный» P0 wire UI:

1. **«статус»** → Network Protection / Main badge / AI speak? (default: Network / Main status)  
2. **«тревога»** → только local tag или ещё Family Chat draft? (default P0: local only)  
3. **Teen** → off until consent? (default: parent-only)  
4. **Coach tip** в том же GO что P0? (рекомендация: да)  
5. **Хранить полный transcript или strip prefix?** (рекомендация: полный)  
6. **Elderly / SimpleHome** — нужен вход в P0 или только Settings?  
7. **Widget в P1 или P2?** (рекомендация: P2)

---

## 9. Как работать следующей ML-системе (обновлённый чеклист)

1. Прочитать base handoff + **этот** review.  
2. `git rev-parse --show-toplevel` = iOS path; branch; `git status`.  
3. Подтвердить Variant C + **GO on P0** у владельца.  
4. TDD router (с aliases + negative mid-sentence) → ClipboardSafety → choke point → VoiceNotes wire → **sheet navigate**.  
5. Не трогать bot/VPN; не коммитить `.env`; `merge: true` на `vsl-c-*`.  
6. Не тащить EventKit / widget / child surfaces.  
7. Если блокер — shrink до **C0** (tags only), не изобретать второй voice stack.  
8. После A1–A12 — спросить owner про P1 (Shortcut first).

### Definition of Done — P0 (усиленный)

- [ ] Router + ClipboardSafety + unit tests green (включая aliases / secrets / A10)  
- [ ] Voice path: tags + Antifake path с корректным dismiss sheet  
- [ ] Paste + Share path через ClipboardSafety  
- [ ] A1–A12  
- [ ] Guards: no history, no background pasteboard, no child spy, no new STT  
- [ ] Нет drive-by refactors / bot в iOS commit  

---

## 10. Six Hats — короткая ревизия

| Hat | Дополнение к base |
|-----|-------------------|
| White | Sheet modal + Share choke point — факты из кода, не из ТЗ |
| Red | Без coach tip фича «не чувствуется» |
| Black | Ложный navigate + mid-sentence false positive + OTP≠phone |
| Yellow | C1 + coach + Shortcut = максимум ценности на glue |
| Green | Aliases + kill-switch + privacy counters |
| Blue | C1 P0 → Shortcut P1 → digest/widget P2 |

---

## 11. One-paragraph (для статуса)

**Base Variant C подтверждаю.** Делать glue на VoiceNotes + Antifake + DayRecap; не клонировать VibeBar и не делать clipboard history. Перед полным wire закрыть три дыры: (1) dismiss sheet → Antifake, (2) ClipboardSafety на Share/paste choke point, (3) STT aliases + leading-only parse. Добавить coach tip и Shortcut раньше widget. EventKit — out. Код — только после GO на P0; при нехватке времени — C0 tags-only, не новый экран.

---

*End of review. Implementer: start at base §10 + this §9.*
