# Antifake Hub — финальный план UX (v2)

**Дата:** 2026-06-16 · **Статус:** к реализации  
**Предыдущая версия:** `ANTIFAKE_HUB_UX_SPEC_AND_PLAN.md` (v1)

---

## 1. Пересмотр: это лучший вариант?

### Что улучшено относительно v1

| v1 | v2 (финал) | Почему лучше |
|----|------------|--------------|
| Только перенос карточки на «Звонок» | **Две явные секции** с заголовками + разделитель | Пользователь видит два разных сценария, не один «звонковый» блок |
| Toggle post-call на Call Directory | **Toggle post-call в секции A** (запись) | Напоминание о загрузке записи ≠ метки на входящих |
| Карточка сверху на всех вкладках | **Контент вкладки первым** в ScrollView | Сразу видно «Проверить», а не «Как включить» |
| `status_unknown` = «неизвестно» | **«Расширение не найдено»** + отдельный баннер | Честнее при отсутствии extension в IPA |
| Кнопка «Как включить» | **«Инструкция: метки на входящих»** | Не путается с «включить проверку» |
| Один `antifake_call_hint` | **Раздельные hint** для записи и Call Directory | Тексты не смешивают два продукта |
| Hardcoded `ALADDIN` в setup sheet | Ключ `antifake_call_directory_extension_name` | Совпадает с «ALADDIN Call Filter» в Settings |

### Что сознательно НЕ делаем

- **Не** выносим Call Directory в 5-ю вкладку — звонок логически один экран, два сценария.
- **Не** deep link в Phone Settings (Apple не даёт) — только sheet + опционально «Открыть Настройки» (общие).
- **Не** дублируем баннер «настройки не нужны» на каждой вкладке (шум) — только в hub subtitle и FAQ.
- **Не** меняем API и sync-логику — только UI/копирайт.

---

## 2. Целевая структура экрана Hub

### Общий layout (premium)

```
┌─ Header: «Проверить подлинность» + subtitle ─────────────────┐
│  [i] → AntifakeAppleLimitsSheet                                 │
├─ Tab picker: Текст | Голос | Видео | Звонок ───────────────────┤
│  ScrollView:                                                    │
│    ① tabContent          ← ПЕРВЫМ (было: Call Directory сверху)│
│    ② AntifakeFamilyReportsSection (свёрнуто по умолчанию — P2) │
│    ③ AntifakeCheckHistorySection                                │
└─────────────────────────────────────────────────────────────────┘
```

### Вкладки Текст / Голос / Видео — без изменений логики

Только **убрать** глобальную карточку Call Directory. Контент как сейчас.

### Вкладка «Звонок» — новый wrapper `AntifakeCallTabView`

```
┌─ Секция A: «Проверка записи» ──────────────────────────────────┐
│  Заголовок + subtitle                                           │
│  [post-call banner] (если push)                                 │
│  AntifakeMediaCheckView(.call) — без дублирующего title в panel │
│  Toggle: «Напоминать проверить запись после звонка»             │
├─ Divider + spacing ─────────────────────────────────────────────┤
┌─ Секция B: «Метки на входящих» ────────────────────────────────┐
│  Заголовок + subtitle + disclaimer                            │
│  AntifakeCallDirectorySettingsCard (без post-call toggle)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Что УБРАТЬ (код)

| # | Файл | Удалить / изменить |
|---|------|-------------------|
| R1 | `AntifakeHubScreen.swift` L35–38 | `AntifakeCallDirectorySettingsCard()` из общего ScrollView |
| R2 | `AntifakeHubScreen.swift` case `.call` | Прямой `AntifakeMediaCheckView` → заменить на `AntifakeCallTabView` |
| R3 | `AntifakeCallDirectorySettingsCard.swift` | Блок `postCallReminderToggle` (L98–109) |
| R4 | `AntifakeCallDirectorySetupSheet` | Hardcoded `"ALADDIN"` в demo Toggle (L247–252) |
| R5 | `antifake_call_directory_body` (локализация) | Текст «включите… затем синхронизируйте» в одном абзаце на всех вкладках |
| R6 | `antifake_call_hint` | Фраза про «ALADDIN не слушает» — перенести в subtitle секции A |
| R7 | `faq_antifake_after_call_answer` | Ссылка на «настройках карточки Call Directory» для toggle |
| R8 | UITests (если есть) | Ожидание `antifake_call_directory_card` на tab text/audio/video |

---

## 4. Что ВСТАВИТЬ (код)

| # | Файл | Добавить |
|---|------|----------|
| I1 | `Shared/Components/AntifakeCallTabView.swift` | **Новый** wrapper: секции A + B |
| I2 | `Shared/Components/AntifakeHubSectionHeader.swift` | **Новый** (опционально) title + subtitle для секций |
| I3 | `AntifakeCallTabView` | `AntifakePostCallReminderToggle` (вынести из CD card) |
| I4 | `AntifakeHubScreen` case `.call` | `AntifakeCallTabView(showPremiumPaywall:…, showPostCallUploadPrompt:…)` |
| I5 | `AntifakeCallDirectorySettingsCard` | Баннер `not_installed` при `.unknown` после проверки |
| I6 | `AntifakeCallDirectorySetupSheet` | Кнопка «Открыть Настройки» → `UIApplication.openSettingsURLString` |
| I7 | `AntifakeCallDirectoryConstants.swift` | `extensionDisplayNameKey = "antifake_call_directory_extension_name"` |
| I8 | `AntifakeMediaCheckView` | Параметр `showsPanelTitle: Bool = true` — на Call tab `false` (заголовок у секции) |

---

## 5. Поведение по разделам (финал)

### Текст
- **Показать:** Текст/Ссылка, поле, hint, **Проверить**, verdict, история.
- **Не показывать:** Call Directory, «Как включить», «Синхронизировать».
- **API:** `POST /api/antifake/check/text` | `/check/url`.

### Голос
- **Показать:** 5 сек запись, файл, **Проверить**, verdict.
- **Не показывать:** Call Directory.
- **API:** upload audio → job poll.

### Видео
- **Показать:** видео/документ, picker, **Проверить**, verdict.
- **Не показывать:** Call Directory.
- **API:** upload video/document → job poll.

### Звонок — секция A «Проверка записи»
- Загрузка m4a/mp3, номер/имя (опц.), **Проверить**, post-call banner, **toggle напоминания**.
- Настройки iPhone **не нужны**.
- **API:** upload call → analyze.

### Звонок — секция B «Метки на входящих»
- Статус: включено / выключено / **расширение не найдено**.
- **Инструкция: метки на входящих** → sheet с **ALADDIN Call Filter**.
- **Синхронизировать** → `GET /api/antifake/call-directory` → App Group → `reloadExtension`.
- Disclaimer: «Не проверяет запись. Метка на входящем, если номер в базе ALADDIN.»

### «Синхронизировать» (без изменений логики)
1. `GET /api/antifake/call-directory?since=…`
2. `identified[]` + `blocked[]` → `AntifakeCallDirectoryStore`
3. `CXCallDirectoryManager.reloadExtension(family.aladdin.ios.ALADDINCallDirectory)`
4. UI: «Синхронизировано N номеров · дата»
5. **Не** проверяет текст/голос/видео/запись.

---

## 6. Локализация — полная таблица (RU + EN)

### 6.1 Новые ключи

| Key | RU | EN |
|-----|----|----|
| `antifake_call_section_recording_title` | Проверка записи после звонка | Check a call recording |
| `antifake_call_section_recording_subtitle` | Загрузите файл записи и нажмите «Проверить». Настройки iPhone не нужны. | Upload a recording and tap Check. No iPhone Settings required. |
| `antifake_call_section_incoming_title` | Метки на входящих звонках | Labels on incoming calls |
| `antifake_call_section_incoming_subtitle` | Подпись на экране входящего, если номер есть в базе ALADDIN. Это не проверка записи. | A label on the incoming call screen when the number is in ALADDIN's database. This does not analyze recordings. |
| `antifake_call_directory_extension_name` | ALADDIN Call Filter | ALADDIN Call Filter |
| `antifake_call_directory_not_recording_note` | Отдельно от проверки записи выше. | Separate from checking a recording above. |
| `antifake_call_directory_status_not_installed` | Расширение не найдено — обновите приложение | Extension not found — update the app |
| `antifake_call_directory_not_installed_banner` | Переключателя «ALADDIN Call Filter» нет в настройках, если расширение не установлено в этой версии приложения. Установите последнюю сборку из TestFlight или App Store. | The «ALADDIN Call Filter» switch won't appear if this app build doesn't include the extension. Install the latest build from TestFlight or the App Store. |
| `antifake_call_directory_open_settings_app` | Открыть «Настройки» | Open Settings |
| `antifake_hub_tab_call_accessibility` | Звонок: запись и метки на входящих | Call: recording check and incoming labels |

### 6.2 Обновить существующие ключи

| Key | RU (новое) | EN (новое) |
|-----|------------|------------|
| `antifake_hub_subtitle` | Проверка текста, голоса и видео — по кнопке. На вкладке «Звонок» — запись и метки на входящих. | Check text, voice, and video on demand. On Call — recording check and incoming labels. |
| `antifake_call_directory_title` | Метки на входящих | Incoming call labels |
| `antifake_call_directory_body` | Скачайте базу номеров кнопкой «Синхронизировать». Чтобы метки показывались, включите «ALADDIN Call Filter» в настройках iPhone (см. инструкцию). | Tap Sync to download the number list. For labels to appear, enable «ALADDIN Call Filter» in iPhone Settings (see the guide). |
| `antifake_call_directory_open_settings` | Инструкция: метки на входящих | Guide: incoming call labels |
| `antifake_call_directory_setup_step4` | 4. Включите «ALADDIN Call Filter» | 4. Turn on «ALADDIN Call Filter» |
| `antifake_call_directory_setup_step4_ios18` | 4. Включите «ALADDIN Call Filter» | 4. Turn on «ALADDIN Call Filter» |
| `antifake_call_directory_setup_step5_retry` | 5. Включите переключатель «ALADDIN Call Filter» | 5. Turn on the «ALADDIN Call Filter» switch |
| `antifake_call_directory_setup_animation_accessibility` | Анимация: Настройки, Телефон, переключатель ALADDIN Call Filter | Animation: Settings, Phone, ALADDIN Call Filter toggle |
| `antifake_call_directory_setup_retry_body` | Если переключателя нет: обновите приложение до последней версии, перезагрузите iPhone, затем нажмите «Синхронизировать» здесь. Ищите имя «ALADDIN Call Filter», не «ALADDIN». | If the switch is missing: update to the latest app version, restart iPhone, then tap Sync here. Look for «ALADDIN Call Filter», not «ALADDIN». |
| `antifake_call_directory_disabled_banner` | Метки не появятся, пока «ALADDIN Call Filter» выключен в Настройки → Телефон → Блокировка и опознавание вызовов. | Labels won't appear until «ALADDIN Call Filter» is on in Settings → Phone → Call Blocking & Identification. |
| `antifake_call_directory_status_unknown` | Не удалось определить статус расширения | Could not determine extension status |
| `antifake_call_hint` | Выберите файл записи (m4a, mp3 и др.). Номер и имя звонящего — по желанию. | Choose a recording file (m4a, mp3, etc.). Caller number and name are optional. |
| `antifake_call_title` | *(не показывать в panel при секции — ключ оставить для accessibility)* | *(same)* |
| `protection_antifake_card_subtitle` | Текст · голос · видео · звонок (запись и метки) | Text · voice · video · call (recording & labels) |
| `protection_antifake_accordion_subtitle` | Проверка по запросу; метки на входящих — на вкладке «Звонок» | On-demand checks; incoming labels on the Call tab |
| `faq_antifake_call_directory_answer` | Откройте «Проверить подлинность» → вкладка **«Звонок»** → блок «Метки на входящих» → инструкция и «Синхронизировать».\n\nНомера только с сервера ALADDIN.\n\nМетка на экране входящего, если номер в списке. iOS 18+: Настройки → Приложения → Телефон → Блокировка и опознавание → **ALADDIN Call Filter**.\n\nЭто не блокировка всех незнакомых — только подпись известных мошеннических номеров. | Open Authenticity Check → **Call** tab → Incoming labels section → guide and Sync.\n\nNumbers come only from ALADDIN's server.\n\nA label appears on incoming calls when the number is listed. iOS 18+: Settings → Apps → Phone → Call Blocking & Identification → **ALADDIN Call Filter**.\n\nThis does not block every unknown caller — only labels known scam numbers. |
| `faq_antifake_after_call_answer` | После разговора ALADDIN может напомнить открыть вкладку «Звонок» (переключатель в блоке **«Проверка записи»**).\n\nЗагрузите запись, если она есть, и при желании укажите номер из «Недавних» в приложении «Телефон». | After a call, ALADDIN can remind you to open the Call tab (toggle in **Check a recording**).\n\nUpload your recording if you have one and optionally enter the number from Recents in the Phone app. |

### 6.3 Ключи без изменений (оставить)

`antifake_check_button`, `antifake_call_directory_sync`, `antifake_call_directory_sync_success_count`, verdict keys, post_call_banner keys, media hints for audio/video/text.

---

## 7. Фазы реализации и TODO

### Фаза 1 — P0 Структура (1 PR)

| ID | Задача | Файлы |
|----|--------|-------|
| **af-ux-01** | Убрать глобальную CD card; tabContent первым в ScrollView | `AntifakeHubScreen.swift` |
| **af-ux-04** | Создать `AntifakeCallTabView` с секциями A/B + divider | новый файл + Hub |
| **af-ux-11** | Перенести post-call toggle из CD card в секцию A | `AntifakeCallTabView`, `AntifakeCallDirectorySettingsCard` |
| **af-ux-12** | `showsPanelTitle: false` для call media panel | `AntifakeMediaCheckView` |

### Фаза 2 — P0 Локализация и copy (тот же PR или след.)

| ID | Задача | Файлы |
|----|--------|-------|
| **af-ux-02** | Все ключи §6.1–6.2 RU+EN | `LocalizationManager.swift` |
| **af-ux-03** | Баннер `not_installed` при `.unknown` | `AntifakeCallDirectorySettingsCard` |
| **af-ux-13** | Setup sheet: `extension_name` вместо hardcoded ALADDIN | `AntifakeCallDirectorySettingsCard.swift` |

### Фаза 3 — P1 Входы и FAQ

| ID | Задача | Файлы |
|----|--------|-------|
| **af-ux-05** | Карточки входа «Проверить подлинность» — subtitle §6.2 | `LocalizationManager`, `AntifakeQuickAccessCopy` |
| **af-ux-07** | FAQ §6.2 | `LocalizationManager` |
| **af-ux-14** | `AntifakeAppleLimitsSheet` — упомянуть вкладку «Звонок» для CD | sheet file |

### Фаза 4 — P1 Тесты

| ID | Задача |
|----|--------|
| **af-ux-09** | UITest: `antifake_call_directory_card` только на tab `call` |
| **af-ux-15** | UITest: секции `antifake_call_section_recording` / `incoming` accessibility ids |

### Фаза 5 — P2 Полировка

| ID | Задача |
|----|--------|
| **af-ux-06** | «Открыть Настройки» в setup sheet |
| **af-ux-16** | Family reports — свернуть по умолчанию (если ещё не) |

### Фаза 6 — P0 Device (вне кода)

| ID | Задача |
|----|--------|
| **af-ux-10** | D-04: метка на входящем, extension в IPA, имя «ALADDIN Call Filter» в Settings |

---

## 8. Критерии приёмки (Definition of Done)

- [ ] На вкладках Текст/Голос/Видео **нет** `antifake_call_directory_card`.
- [ ] На «Звонок» видны **две** секции с разными заголовками.
- [ ] Toggle post-call **только** в секции A.
- [ ] В setup и FAQ везде **«ALADDIN Call Filter»**.
- [ ] При `.unknown` показывается баннер «обновите приложение».
- [ ] Sync по-прежнему работает; UITests зелёные.
- [ ] RU и EN ключи §6 синхронизированы.

---

## 9. Шесть шляп — финальный синтез

| Шляпа | Решение v2 |
|-------|------------|
| Белая | Два продукта на одной вкладке «Звонок» — нормально, если визуально разделены |
| Красная | Убрать «Как включить» с текстовой вкладки — снимает главную боль |
| Чёрная | Toggle на CD card вводил в заблуждение — перенос в секцию A |
| Жёлтая | Счётчик N номеров после sync уже есть — оставить |
| Зелёная | Секции A/B + честное имя extension — целевой UX |
| Синяя | Фазы 1→2→3→4→5→6, один PR на фазы 1–2 |
