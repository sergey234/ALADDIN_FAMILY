# Аудит: 14 ссылок Sensor Tower + топ 50 Gen AI → ALADDIN

**Дата:** 2026-10-06  
**Роль файла:** один документ «что анализировали и как» + промпт для **второй** ИИ, чтобы перепроверить и предложить добавки в план  
**Канон реализации (не дублировать код-план):** [`PLAN_ALADDIN_STORE_LIFT_MASTER_2026-10-06.md`](PLAN_ALADDIN_STORE_LIFT_MASTER_2026-10-06.md)  
**Трекер задач:** [`.cursor/ALADDIN_STORE_LIFT_TASK_REGISTRY.md`](../.cursor/ALADDIN_STORE_LIFT_TASK_REGISTRY.md) · Cursor TODO `fsl-*` + `gai-*`  
**Корень репо:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

---

## 0. Зачем этот файл

Владелец попросил: вспомнить весь разбор 14 ссылок и топ‑50, собрать в один документ метод + выводы, и дать **промпт другой ИИ**, чтобы она могла найти пробелы в плане.  
Код по этому аудиту **не писать**, пока владелец не скажет **GO LIFT BUILD**.

---

## 1. Как анализировали (метод)

### 1.1. Шаги агента

1. Открыт канон ALADDIN: питч щита, Family Safety + Wellness, тарифы, App Store description, START_HERE.  
2. По коду: экраны `Screens/`, Hub antifake, Share extension, IoT, геозоны, привычки, Focus, TTS Companion, Voice Safety, ClipboardSafety, safe-word, Call Directory, App Intents.  
3. **14 URL** `app.sensortower.com/overview/{id}` + publisher: имена сверены через публичный **iTunes Lookup** (US), не через платный ST.  
4. **Топ 50 Gen AI** — со скринов a16z / Sensor Tower MAU (август 2026): по каждому take / adapt / have / skip.  
5. Два черновых плана склеены в один MASTER; второй проход кода добавил `fsl-13` и `gai-06`.

### 1.2. Критерии «берём в ALADDIN»

Брали только если усиливает:

- щит семьи (сеть / дом / устройства),  
- «правда или фейк» (ссылка, бумага, звонок, фото),  
- родительский контроль без шпионажа,  
- пожилые 60+ (крупно, голос, SOS),  
- герой с возрастной этикой,  
- **без** второго ChatGPT / CapCut / селфи / браузера / клавиатуры / трекинга 24/7.

### 1.3. Чего метод **не** покрыл (дыры для второй ИИ)

| Дыра | Почему важно |
|------|----------------|
| Платный Sensor Tower Top Charts 180 дней, Worldwide, iPhone-only | Мы не видели полный топ-100/200 по категориям |
| Топ family-safety конкуренты (Bark, Qustodio, Life360 официальный, Norton, Kaspersky) | В 14 ссылках их почти нет — туда попал Productivity |
| Google Play / Android | ALADDIN сейчас iOS |
| Выручка vs MAU | Топ 50 — по открытиям, не по деньгам |
| App Review свежие отказы конкурентов | Не парсили |
| Локальный рынок РФ (RuStore, локальные VPN/антифейк) | 14 ссылок = US storefront |

---

## 2. Что уже есть в ALADDIN (не дублировать в lift)

| Уже есть | Где / смысл |
|----------|-------------|
| Antifake Hub | текст / аудио / видео / звонок |
| Share URL/текст → Hub | `ALADDINAntifakeShare` |
| Сервер проверки документа + provenance | iOS-вкладки «Документ» ещё нет → `fsl-01` |
| IoT-экран, blockDevice, угрозы камер | нет одной «карты дома» и пуша → `fsl-03/12` |
| Devices / NetworkProtection | |
| Геозоны enter/exit в LocationManager | на UI демо «09:15» → `fsl-05` |
| Привычки семьи (секция + API + пуши) | только «на виду» → `fsl-10` |
| FocusSession 25/60, флаг выкл. | вход → `fsl-09` |
| CompanionSpeechOutput / AVSpeech | кнопка на вердикте → `fsl-06` |
| Voice Safety / call analyze | простой язык → `fsl-08` |
| ClipboardSafety | on-demand, без фона |
| Safe-word семьи | другой план fws |
| Экран после звонка 60+ | `eld-*`, не lift |
| 3 героя Companion + этика | не character.ai |
| `family_homework_mode` | не Photomath |
| App Intent на Voice Safety Log | нет Intent «проверь ссылку» → `gai-06` |

---

## 3. Четырнадцать ссылок Sensor Tower — полный вердикт

| # | App Store ID | Приложение (US lookup) | Что это | В ALADDIN | Не берём |
|---|--------------|------------------------|---------|-----------|----------|
| 1 | `1499198946` | Structured | Таймлайн дня / ADHD planner | Полоска дня из уже заданных правил (`fsl-07`) | Календарь-планировщик |
| 2 | `1353634006` | Google Tasks | Списки дел Google | — | Tasks / Gmail sync |
| 3 | `1438388363` | Habit Tracker | Привычки, серии | Привычки уже есть — только заметность (`fsl-10`) | Фитнес / калории / чужой трекер |
| 4 | `608834326` | Calendars (Readdle) | Календарь Apple-стека | Правило как «событие» уже в лимитах — не отдельный CalDAV | Клиент календаря |
| 5 | `1209815023` | Speechify | Текст → голос | «Прослушать» вердикт/SOS (`fsl-06`) | Читалка книг |
| 6 | `1158877342` | Grammarly Keyboard | Клавиатура везде | Идея «проверить перед отправкой» → Share/чат (`fsl-02`, `gai-05`) | Системная клавиатура |
| 7 | `1258654743` | AT&T Smart Home Manager | Wi‑Fi оператора: устройства, пауза | Карта дома + пауза (`fsl-03`, `fsl-04`) | Логин AT&T / их роутер |
| 8 | `1497465230` | Opal | Самоконтроль экрана | Фокус «я сам» (`fsl-09`) | Лидерборды / замена Screen Time |
| 9 | `6741517781` | Cue | ИИ-конспект встреч | 2–3 фразы по звонку (`fsl-08`) | Скрытая запись переговоров |
| 10 | `883338188` | Evernote Scannable | Скан бумаги | Документ в Hub + Share фото (`fsl-01`, `fsl-02`) | Архив Evernote |
| 11 | `1232780281` | Notion | Wiki / задачи / ИИ | — | Notion |
| 12 | publisher `1541277944` → `1115101477` | SmartLife (Tuya) + B2B apps | Умный дом / монтаж | Пуш IoT (`fsl-12`), не хаб | Tuya / Construction / Light B2B |
| 13 | `1669041518` | Find Phone: Device Tracker | Карта, пришёл/ушёл | Живая школа + «Я в порядке» (`fsl-05`, `fsl-13`) | GPS 24/7 / шпионаж |
| 14 | `1023499075` | eero | Свой Wi‑Fi: профили, пауза | Тот же приём, что AT&T (`fsl-03`, `fsl-04`) | Купить eero |

---

## 4. Топ 50 Gen AI (MAU, авг 2026) — полный вердикт

Легенда: **have** = уже есть · **take** = приём в план · **adapt** = кусок · **skip** = не берём.

### Чат

| # | App | Вердикт | В ALADDIN / нет |
|---|-----|---------|-----------------|
| 1 | ChatGPT | have | Companion + Assistant уже |
| 3 | Gemini | adapt | Камера «что это?» (`gai-03`) |
| 6 | Copilot | skip | Office |
| 7 | Doubao | skip | Китайский чат |
| 9 | Dola | skip | Ещё один комбайн |
| 12 | Claude | adapt | Тон длинного файла → `gai-02` |
| 14 | DeepSeek | skip | Отдельный чат |
| 18 | Meta AI | take | Проверка в семейном чате (`gai-05`) |
| 19 | Grok | skip | Лента X |
| 44 | NOVA | skip | Переключатель моделей |
| 46 | Qwen | skip | Отдельный чат |

### Видео

| # | App | Вердикт | В ALADDIN / нет |
|---|-----|---------|-----------------|
| 2 | CapCut | skip | Монтаж; видео только antifake |
| 17 | Edits | skip | |
| 22 | VN | skip | |
| 29 | Wink | adapt | Читаемость фото бумаги **внутри** `fsl-01` |
| 33 | YouCut | skip | |

### Фото / дизайн / селфи

Все **skip** как продукты: Canva (4), AI Gallery (5), Picsart (8), Lightroom (20), Remini (23), Hypic (30), Adobe Express (31), Polish (34), FaceApp (43), Photoroom (45), Meitu (26), BeautyPlus (39), BeautyCam (40), SNOW (42), Faceu (48).  
FaceApp — разве что урок «лицо подделывают» в академии (не в lift-коде).

### Поиск / браузер

| # | App | Вердикт | В ALADDIN / нет |
|---|-----|---------|-----------------|
| 10 | Edge | adapt→gai-06 | Не браузер; Siri/ярлык «проверь ссылку» |
| 13 | Yandex | skip | Алиса ≠ герой |
| 15 | QQ Browser | skip | |
| 21 | Seekee | skip | Комбайн |
| 24 | Baidu AI Search | skip | |
| 25 | Perplexity | take | Источники в вердикте (`gai-01`) |
| 32 | Bing | skip | |

### Учёба

| # | App | Вердикт | В ALADDIN / нет |
|---|-----|---------|-----------------|
| 16 | Goodnotes | have/fsl-01 | Фото объявления → документ |
| 28 | Notion | skip | |
| 35 | Gemini Notebook | take | Герой только по PDF семьи (`gai-02`) |
| 37 | Gauth | skip | Не решаем домашку |
| 49 | Photomath | skip | Не решаем примеры |

### Прочее

| # | App | Вердикт | В ALADDIN / нет |
|---|-----|---------|-----------------|
| 11 | Meituan | skip | Еда |
| 27 | Facemoji | skip | Клавиатура |
| 36 | Papago | adapt | `gai-04` |
| 38 | Translate | adapt | `gai-04` |
| 41 | character.ai | have | 3 героя + этика |
| 47 | Suno | skip | Песни |
| 50 | Emochi | skip | Аниме RP |

---

## 5. Текущий единый план (задачи простым языком)

Порядок: **A бумага → B дом → C школа + «я в порядке» → D полировка → E ИИ → телефон**.

| ID | Волна | Что увидит человек |
|----|-------|-------------------|
| fsl-01 | A | Вкладка «Документ»: фото/PDF → правда или обман |
| fsl-02 | A | Поделиться фото/PDF → ALADDIN |
| fsl-03 | B | Одна карта: телефоны + умный дом |
| fsl-04 | B | Пауза интернета ребёнку / пауза камеры |
| fsl-05 | C | Пуш «дошёл до школы» по-настоящему |
| fsl-13 | C | Кнопка «Я в порядке» |
| fsl-06 | D | Прослушать вердикт / SOS |
| fsl-07 | D | Полоска дня: сон / учёба / экран |
| fsl-08 | D | 2–3 фразы после звонка для бабушки |
| fsl-09 | D | Подросток сам включает фокус 25 мин |
| fsl-10 | D | Привычки семьи не спрятаны |
| fsl-11 | D | Научили «Поделиться → ALADDIN» |
| fsl-12 | D | Пуш: камера торчит в интернет |
| gai-01 | E | В вердикте ссылки — почему и откуда |
| gai-02 | E | Герой отвечает только по файлу семьи |
| gai-03 | E | Камера «что это?» в том же Hub |
| gai-04 | E | Переведи SMS и сразу проверь |
| gai-05 | E | В семейном чате «это безопасно?» |
| gai-06 | E | Siri / Ярлык «проверь ссылку» |
| fsl-qa-device | QA | Владелец на живом iPhone |

Код: **GO LIFT BUILD**.

---

## 6. Промпт для второй ИИ (скопировать целиком)

```text
Ты — независимый product/security auditor для семейного iOS-приложения ALADDIN (щит семьи: antifake, родительский контроль, VPN/сеть, пожилые, герои Companion). Твоя задача — ПЕРЕПРОВЕРИТЬ разбор конкурентов и план lift. Код не писать. Не предлагать mock parental, шпионский GPS, скрытую запись звонков, клавиатуру, клон ChatGPT/CapCut/Canva.

РАБОЧИЙ КОРЕНЬ:
/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

ОБЯЗАТЕЛЬНО ПРОЧИТАЙ СНАЧАЛА:
1) docs/AUDIT_STORE_TOPS_AND_GENAI50_FOR_SECOND_AI_2026-10-06.md  (этот аудит)
2) docs/PLAN_ALADDIN_STORE_LIFT_MASTER_2026-10-06.md  (канон плана)
3) .cursor/ALADDIN_STORE_LIFT_TASK_REGISTRY.md  (TODO fsl-* + gai-*)
4) docs/PITCH_ALADDIN_FAMILY_SHIELD.md
5) docs/FAMILY_SAFETY_WELLNESS_MASTER_PLAN.md  (§ «уже есть»)
6) docs/ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md (если есть) / docs/ANTIFAKE_CALLS_PRODUCT_SCOPE.md
7) Быстрый grep/read: AntifakeHubScreen, ALADDINAntifakeShare, IoTSecurityScreen, LocationManager, FamilyHabitRemindersSection, FocusSessionScreen, CompanionSpeechOutput, ClipboardSafetyService, OpenVoiceSafetyLogIntent

ИСТОЧНИКИ РАЗБОРА (уже сделаны первой ИИ — не повторяй с нуля, ИЩИ ПРОБЕЛЫ):
A) 14 Sensor Tower / App Store ID (см. §3 аудита): Structured, Google Tasks, Habit Tracker, Calendars Readdle, Speechify, Grammarly Keyboard, AT&T Smart Home, Opal, Cue, Scannable, Notion, SmartLife/Tuya publisher, Find Phone tracker, eero.
B) Топ 50 Gen AI mobile по MAU авг 2026 (см. §4): все 50 имён со скрина Sensor Tower / a16z.

КРИТЕРИИ ПРОВЕРКИ (пройди ВСЕ пункты и отметь PASS / GAP / CONFLICT):

1. Покрытие конкурентов
   - Для каждого из 14: вердикт take/skip логичен? Что упущено из публичного App Store description?
   - Для каждого из 50: вердикт have/take/adapt/skip логичен? Есть ли фича, полезная семье, которую первая ИИ пометила skip слишком рано?

2. Дубли с уже существующим ALADDIN
   - Не предлагает ли план второй Share URL, второй Focus, второй Habit Tracker, второй чат, второй IoT-хаб, второй safe-word, второй clipboard monitor, второй eld-экран звонка?

3. Пробелы относительно семейной безопасности (даже если не было в 14/50)
   - Сравни с типичными family-safety apps (Bark, Qustodio, Life360, Google Family Link, Apple Screen Time+Family Sharing, Norton Family): какие 3–7 приёмов UX могли бы усилить ALADDIN БЕЗ шпионажа и БЕЗ смены продукта?
   - Только то, чего нет в fsl-* / gai-* / eld-* / af-* / fws-*.

4. Apple / закон / доверие
   - Любая предложенная фича: согласие, прозрачность, App Review, нет скрытого микрофона/локации, нет клавиатуры с паролями.

5. Гибрид (лучший способ)
   - Для каждой новой кандидатуры: что делает iOS система / что уже есть в ALADDIN UI / что на сервере. Один экран, минимальный diff.

6. Приоритет
   - Если находишь добавки: максимум 5 новых id вида fsl-14+ или gai-07+, каждая с: «что увидит родитель», «откуда приём», «почему не дубль», «волна A–E или новая F», «DoD одной строкой».
   - Если добавок нет — явно напиши: «план достаточен; дыр нет внутри заявленных источников».

7. Честность про лимиты данных
   - Напомни, что не было платного ST Worldwide Top 200 и что 14 ссылок — не топ family-safety.

ФОРМАТ ОТВЕТА (строго):
## Вердикт (1 абзац)
## PASS — что согласен
## GAP — что добавить в план (таблица: id | волна | что увидит человек | почему)
## CONFLICT — где первая ИИ ошиблась (skip→take или наоборот)
## НЕ ДОБАВЛЯТЬ — список соблазнов с причиной
## Риски App Review / privacy
## Нужен ли GO владельца на правку реестра (да/нет)

Язык ответа: простой русский, без воды. Не коммить. Не деплой. Не трогай telegram_stars_shop_bot в iOS-релизе.
```

---

## 7. Связь с Cursor TODO

Единый трекер: `.cursor/ALADDIN_STORE_LIFT_TASK_REGISTRY.md`.  
Правило: `.cursor/rules/aladdin-store-lift-todo-ssot.mdc`.  
Только `merge: true`. Не затирать `af-*` / `eld-*` / `fws-*`.

Если вторая ИИ предложит GAP — владелец говорит **GO LIFT ADD**, тогда ids добавляют в реестр и Cursor TODO.

---

## 8. Финальное заключение первой ИИ (для сверки)

ALADDIN не должен стать ChatGPT, eero или Habit Tracker.  
Нужно дожать щит: бумага/камера, дом/пауза, школа + «я в порядке», голос 60+, источники ссылки, проверка в чате, Siri «проверь ссылку».  
По заявленным источникам план **достаточен**; главные дыры метода — платный ST и отсутствие отдельного бенчмарка Bark/Qustodio (вторая ИИ как раз должна это закрыть рекомендациями, не клонами).

---

## 9. Ответ второй ИИ → GO LIFT ADD (2026-10-06)

Вторая ИИ подтвердила план и предложила GAP. Владелец: **GO LIFT ADD** + **начинаем реализацию**.

Принято в реестр:

| id | что |
|----|-----|
| fsl-14 | Недельный дайджест |
| fsl-15 | Мягкий статус (заряд / я ок) |
| fsl-16 | Виджет «Проверить ссылку» |
| gai-07 | Урок Академии про подделку лица |

Уточнения без нового id: `gai-01` = API sources + empty (UI есть); `fws-03` CTA «перед переводом» на главной — Wellness.  
Код: волна A (`fsl-01`, `fsl-02`) первой.
