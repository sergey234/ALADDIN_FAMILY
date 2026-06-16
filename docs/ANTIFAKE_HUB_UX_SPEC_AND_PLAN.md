# Antifake Hub — как должно работать (факт + цель + план)

**Версия:** 1.0 · **2026-06-16**  
**Контекст:** пользователь видит «Как включить» + «Синхронизировать» на всех вкладках; ALADDIN нет в Настройках → Телефон.

---

## 0. Факт из кода (аудит 2026-06-16)

### Что реально сейчас

| Элемент | Где в коде | Поведение |
|---------|------------|-----------|
| `AntifakeCallDirectorySettingsCard` | `AntifakeHubScreen` — **над** `tabContent`, в общем `ScrollView` | Показывается на **всех** вкладках при premium |
| Вкладка **Текст** | `AntifakeTextCheckView` | Текст/URL → `POST /api/antifake/check/text` или `/url` — **без** Call Directory |
| Вкладка **Голос** | `AntifakeQuickVoiceCaptureView` + `AntifakeMediaCheckView(.audio)` | 5 сек запись + файл → upload → job poll — **без** Call Directory |
| Вкладка **Видео** | `AntifakeVideoCheckPanel` | Видео/документ → upload — **без** Call Directory |
| Вкладка **Звонок** | `AntifakeMediaCheckView(.call)` | Запись после разговора + caller id — **без** Call Directory в панели |
| «Как включить» | Только в `AntifakeCallDirectorySettingsCard` | Sheet с шагами Settings → Phone (не deep link) |
| «Синхронизировать» | Только в `AntifakeCallDirectorySettingsCard` | `AntifakeCallDirectorySyncService` |

**Вывод:** логика **проверки контента** по вкладкам разная и правильная. **UX ошибка:** карточка Call Directory **глобальная** → создаётся ощущение «везде один алгоритм включения».

### Имя в iOS Settings

Расширение: `CFBundleDisplayName` = **«ALADDIN Call Filter»** (`ALADDINCallDirectory/Info.plist`), bundle id `family.aladdin.ios.ALADDINCallDirectory`.

---

## 1. Шесть шляп (6 Thinking Hats)

### 🤍 Белая — факты

- **Текст/URL:** синхронный API, verdict сразу или после короткого ответа.
- **Аудио/видео/звонок (файл):** upload → job 202 → poll → verdict (SFM/worker).
- **Call Directory:** список номеров PostgreSQL → `GET /api/antifake/call-directory` → App Group → `reloadExtension` → iOS показывает метку на **входящем** PSTN-звонке.
- **Синхронизировать** не проверяет текст/голос/видео — только **базу номеров** для меток.
- Apple **не даёт** слушать обычные звонки в фоне; post-call — push + загрузка записи пользователем.
- В списке «Блокировка…» только приложения с **вшитым** Call Directory extension в установленной сборке.

### ❤️ Красная — эмоции пользователя

- «Нажимаю включить — ALADDIN нет» → разочарование, недоверие к продукту.
- Одинаковая карточка на всех вкладках → «приложение не понимает, что я хочу».
- Инструкция говорит «ALADDIN», в списке может быть **«ALADDIN Call Filter»** или **ничего** (нет extension в сборке).

### 🖤 Чёрная — риски

- Путаница Call Directory ↔ проверка записи → ложные ожидания «приложение слушает звонки».
- FAQ (`faq_antifake_call_directory_answer`) смешивает весь Hub с Call Directory.
- Кнопка «Как включить» не открывает Settings (только sheet) — ожидание «нажал — включилось».
- Нет extension в IPA → бесконечный цикл «включите в настройках».

### 💛 Жёлтая — возможности

- Разделить UI: **«Проверка по запросу»** (4 вкладки) vs **«Метки на входящих»** (только Звонок или отдельный блок).
- Честный статус: «Расширение не установлено в этой сборке» / «Ищите ALADDIN Call Filter».
- После Sync — явно: «N номеров, метка: Возможный мошенник?».
- Звонок: два подблока — **A) входящие метки** / **B) проверка записи**.

### 💚 Зелёная — целевое поведение (лучший вариант)

См. раздел 2 ниже.

### 💙 Синяя — процесс внедрения

См. раздел 3 (TODO) — сначала UX/copy (низкий риск), затем conditional card placement, затем device QA D-batch.

---

## 2. Целевое отображение по разделам

### Общая структура Hub (premium)

```
[Заголовок] Antifake · подзаголовок «по вашему запросу»

[Вкладки] Текст | Голос | Видео | Звонок

── содержимое активной вкладки (без Call Directory на Текст/Голос/Видео) ──

[История проверок] (общая)
[Семейные отчёты] (опционально, свернуть)
```

**Call Directory — только на вкладке «Звонок»** (или collapsible «Входящие звонки» внутри неё).

---

### Вкладка «Текст»

| Блок | UI | Действие | API |
|------|-----|----------|-----|
| Режим | Текст / Ссылка | переключатель | — |
| Поле | TextEditor или URL | ввод | — |
| CTA | **Проверить** | отправка | `POST /api/antifake/check/text` или `/check/url` |
| Результат | `AntifakeVerdictCard` | verdict + reasons | sync response |
| Нет | «Как включить», «Синхронизировать» | — | — |

Подсказка: «Вставьте текст или ссылку. Проверка только когда вы нажмёте кнопку.»

---

### Вкладка «Голос»

| Блок | UI | Действие | API |
|------|-----|----------|-----|
| Быстрая запись | «Записать 5 сек» | AVAudioRecorder → upload | `/api/antifake/check/audio` |
| Файл | «Выбрать файл» | fileImporter | upload + job poll |
| CTA | **Проверить** | | |
| Результат | Verdict card | | |
| Нет | Call Directory | | |

Подсказка: «Запись только по кнопке. ALADDIN не слушает звонки в фоне.»

---

### Вкладка «Видео»

| Блок | UI | Действие | API |
|------|-----|----------|-----|
| Режим | Видео / Документ | | |
| Файл | picker | | `/api/antifake/check/video` или document |
| CTA | **Проверить** | | job poll |
| Результат | Verdict card | | |
| Нет | Call Directory | | |

---

### Вкладка «Звонок» (две зоны)

#### Зона A — «Проверить запись разговора» (как сейчас `AntifakeMediaCheckView.call`)

| UI | Действие |
|----|----------|
| Баннер post-call (если пришли из push) | подсказка загрузить запись |
| Поля номер / имя (опционально) | metadata |
| Выбор файла записи | m4a/mp3/… |
| **Проверить** | upload → `/api/antifake/call/analyze` (или media kind call) |

#### Зона B — «Метка на входящем звонке» (`AntifakeCallDirectorySettingsCard`)

| UI | Действие |
|----|----------|
| Статус | Включено / Выключено / Не установлено |
| **Как включить** | sheet: Settings path + **«ALADDIN Call Filter»** |
| **Синхронизировать** | см. раздел 3 |
| Toggle | Напоминание после звонка (post-call reminder) |

Разделитель + короткий текст: «Это не проверка записи. Метка появится на экране входящего, если номер в базе ALADDIN.»

---

## 3. «Синхронизировать» — логика по шагам

```
Пользователь нажимает «Синхронизировать»
        ↓
1. JWT → GET /api/antifake/call-directory
   (?since=last_sync для дельты)
        ↓
2. Ответ: identified[{phone, label}], blocked[], total_count, updated_at
   Источник: PostgreSQL antifake_scam_numbers (prod)
        ↓
3. Сохранение в App Group (UserDefaults)
   ключ snapshot + backup
        ↓
4. CXCallDirectoryManager.reloadExtension(
     family.aladdin.ios.ALADDINCallDirectory)
        ↓
5. Extension CallDirectoryHandler читает snapshot
   → addIdentificationEntry (метка)
   → addBlockingEntry (если blocked)
        ↓
6. UI: «Синхронизировано N номеров · дата»
   + статус extension (enabled/disabled)
```

**Если extension выключен в Settings:** sync всё равно качает базу, но метки **не появятся** до включения «ALADDIN Call Filter».

**Если extension нет в сборке:** reloadExtension fails → ошибка в UI.

---

## 4. Почему ALADDIN нет в Настройках (чеклист)

1. Искать **«ALADDIN Call Filter»**, не «ALADDIN».
2. iOS 18: **Настройки → Приложения → Телефон → …**
3. Сборка без `ALADDINCallDirectory` target / не TestFlight 232+.
4. Симулятор / переустановка без extension.
5. Статус в приложении: «Расширение выключено» vs «неизвестно» (часто = нет extension).

---

## 5. Cursor TODO (реализация лучшего UX)

| ID | Задача | Приоритет |
|----|--------|-----------|
| `af-ux-01` | Перенести `AntifakeCallDirectorySettingsCard` только на вкладку `.call` | P0 |
| `af-ux-02` | Copy: «ALADDIN Call Filter» в шагах setup + FAQ | P0 |
| `af-ux-03` | Статус extension `.unknown` → «Расширение не найдено — обновите приложение» | P0 |
| `af-ux-04` | Разделить вкладку Звонок: секции «Запись» / «Входящие метки» | P1 |
| `af-ux-05` | Убрать из `antifake_call_directory_body` упоминание настроек с карточки на Text/Audio (после переноса) | P1 |
| `af-ux-06` | Кнопка «Открыть Настройки» → `UIApplication.openSettingsURLString` (общие) + sheet | P2 |
| `af-ux-07` | FAQ: разделить «проверка контента» и «метки на звонках» | P1 |
| `af-ux-08` | Entry card «Проверить подлинность»: subtitle без Call Directory | P2 |
| `af-ux-09` | UITest: Call Directory card только на tab call | P1 |
| `af-ux-10` | Device QA: D-04 метка на входящем (Build 232 tracker) | P0 device |

---

## 6. Ответ на вопрос «ты уверен?»

| Утверждение | Верно? |
|-------------|--------|
| Текст/Голос/Видео не требуют Settings → Phone | **Да** (по коду) |
| Вкладка Звонок (файл) не требует Call Directory | **Да** |
| «Как включить» относится только к меткам на входящих | **Да по смыслу** |
| Пользователь видит это на всех вкладках | **Да** — из‑за **глобальной карточки** (UX баг) |
| «Синхронизировать» синхронизирует проверки текста | **Нет** — только номера для Call Directory |

**Итог:** продуктовая логика разделения **верная**, текущий **UI её ломает**. Исправление — перенос карточки + честные тексты + имя «ALADDIN Call Filter».
