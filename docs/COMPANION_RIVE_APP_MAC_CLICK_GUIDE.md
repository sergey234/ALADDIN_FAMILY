# Rive.app на Mac — куда нажимать (PATH A, 12 мимик)

> **⚠️ Import PNG не работает на Mac app?** → главный путь: **[COMPANION_RIVE_COMFORT_PATH.md](./COMPANION_RIVE_COMFORT_PATH.md)** (веб **editor.rive.app** + Cadet).

> **Для:** `aladdin.riv` · `genie.riv` (и проверка `unicorn.riv`)  
> **Важно:** файлы могли открыться **сами** из терминала (`open -a Rive …`) — это делала ML, не вы.

---

## 0. Что у вас уже в файлах (честно)

| Файл | Кто собрал | Что внутри сейчас |
|------|------------|-------------------|
| `unicorn.riv` | Аниматор / прошлая сессия | Production SM + мимика |
| `aladdin.riv` | ML-скрипт + **ваша** доводка в Rive | PNG Аладдина + SM с эталона unicorn |
| `genie.riv` | То же | PNG Джина + SM с эталона |

**12 мимик «по плану 100%»** = вы в Rive **подстраиваете** брови/рот/веки **в каждом state** (§2.3). Без этого эмоции могут выглядеть похоже.

---

## 1. Карта окна Rive (Mac)

```text
┌─────────────────────────────────────────────────────────────────┐
│ Rive   File  Edit  View  …          [Design] [Animate]   ▶ Play │  ← верх
├──────────┬──────────────────────────────────────┬─────────────┤
│ СЛОИ     │                                      │ INSPECTOR   │
│ (слева)  │         ХОЛСТ 360×480                │ (справа)    │
│ Outliner │         герой                        │ X Y W H     │
│          │                                      │ Opacity …   │
├──────────┴──────────────────────────────────────┴─────────────┤
│ НИЗ: Timeline  ИЛИ  State Machine (граф состояний) + Inputs    │  ← главное
└─────────────────────────────────────────────────────────────────┘
```

| Зона | Зачем |
|------|--------|
| **Design** (вкладка вверху) | Рисунок, слои, PNG, кости |
| **Animate** (вкладка) | Таймлайны, **State Machine**, Preview |
| **Слева — Outliner** | Дерево: Artboard → слои (`mouth`, `brow_L`…) |
| **Центр** | Картинка героя |
| **Справа — Inspector** | Позиция, поворот, масштаб выбранного слоя |
| **▶ Play** | Запуск превью State Machine |
| **Низ** | Таймлайн кадров **или** граф SM + панель **Inputs** |

> В новых версиях Rive логика SM часто в **нижней** панели, не справа ([Rive Data Binding blog](https://rive.app/blog/getting-started-with-data-binding)).

---

## 2c. PNG «грузит» или «ничего не происходит»

> **Тест 64×64 прошёл** → Rive установлен OK. **Большой PNG 360×480 RGBA** (~157 KB) у Rive 0.8.x на Mac часто **зависает** — это баг/особенность редактора, не ваш файл.

### Почему тест OK, а единорог — нет

| | `test_64x64.png` | `unicorn_360x480.png` |
|--|------------------|------------------------|
| Размер | 64×64 | 360×480 |
| Альфа | нет (RGB) | **есть (RGBA)** |
| Вес | 132 B | 157 KB |
| В Rive | ✅ за секунды | ❌ спиннер / зависание |

### ✅ Официальный workflow Rive ([Rive 101 — Import Raster](https://www.youtube.com/watch?v=hPbgPGJNE78))

**Способ 1 — Paste (самый надёжный на Mac)**

1. Откройте картинку в **Preview** (Просмотр): двойной клик по файлу на Desktop.
2. **⌘A** → **⌘C** (скопировать).
3. В Rive: **File → New file** → клик по пустому Stage.
4. **⌘V** — Rive **сам** создаёт Artboard **360×480** и кладёт картинку внутрь.

**Способ 2 — Assets → Generate Artboard**

1. **File → New file**.
2. Откройте панель **Assets** (не Design-холст для первого шага).
3. Перетащите файл **в область Assets** (не на artboard).
4. Дождитесь появления превью в списке (если >30 сек — см. способ 3).
5. **Правый клик** по asset → **Generate Artboard** (artboard = размер картинки).

**Способ 3 — JPEG без альфы (если PNG висит)**

На Desktop уже лежит:

```text
/Users/sergejhlystov/Desktop/RIVE_IMPORT/unicorn_360x480_flat.jpg
```

(~27 KB, без прозрачности) — повторите способ 1 или 2 с **.jpg**.

**Способ 4 — проверка масштаба**

Сначала `unicorn_180x240_test.png` — если он в Assets появляется, проблема в **размере/альфе** большого PNG.

### Если снова «висит»

1. **⌘⌥Esc** → Rive → Принудительно завершить.
2. Файл только с **Desktop/RIVE_IMPORT/** (не `/Volumes/Disk/`).
3. В Assets после импорта: выберите asset → в Inspector **Apply** на compression → включите **Export to RIV**.
4. Войти в **rive.app** (Cadet) — без логина иногда зависает Export/Assets.

### ❌ Старая ошибка в инструкции

Раньше писали «не в Assets» — **это было неверно**. По документации Rive raster **сначала** идёт в **Assets**, потом на artboard или **Generate Artboard**.

**Признак успеха:** в Hierarchy виден **Artboard 360×480** + слой Image с единорогом.

---

## 2. ⚠️ Почему `unicorn.riv` / `aladdin.riv` / `genie.riv` **серые** в Rive

> **Главная причина:** эти три файла — **runtime export** (для iOS-приложения), **не** исходник редактора.  
> Rive Editor **не открывает** runtime `.riv` для редактирования — в диалоге **File → Open** они **закрашены серым**.  
> Это нормально, не баг macOS.

| Тип | Расширение | Кто использует | Открыть в Rive Editor? |
|-----|------------|----------------|------------------------|
| **Исходник / backup** | **`.rev`** | аниматор | ✅ **Да** |
| **Runtime export** | **`.riv`** | iOS / Android / Web | ❌ **Нет** (только проигрывание в runtime) |

Наши production-файлы начинаются с байтов `RIVE` (format v7) — это **готовый бинарник для приложения**.  
`aladdin.riv` и `genie.riv` дополнительно собраны **скриптом** (подмена PNG внутри unicorn) — это **не** проект Rive.

**Что открывать для работы:**

1. **File → New file** (новый проект 360×480) + **Import** PNG из `docs/assets/` — см. [COMPANION_RIVE_EDITOR_5_STEPS.md](./COMPANION_RIVE_EDITOR_5_STEPS.md), или  
2. Единственный `.rev` в репо (черновик MCP, не production):  
   `Resources/Companion/unicorn_mcp_draft.rev` (~2 KB), или  
3. Проект на **rive.app** (Cadet), если сохраняли в облако.

**Когда закончили мимики:** **File → Export → For runtime** → сохранить **поверх**  
`Resources/Companion/unicorn.riv` (или aladdin/genie).  
Параллельно: **File → Export → .rev for backup** — чтобы в следующий раз файл **не был серым**.

---

## 2b. Открыть `.rev` (если есть исходник)

1. Rive → **File → Open…** (`⌘O`).
2. **`⌘⇧G`** → папка `Resources/Companion`.
3. Внизу диалога: **«Показать: Все файлы»** / **All Files** — выберите **`*.rev`**, не серый `.riv`.
4. Или терминал: `./scripts/companion_07_open_in_rive.sh rev` (если скрипт поддерживает `.rev`).

**Не открывайте для редактирования:** `aladdin_work_in_progress.riv` — это тоже runtime-копия unicorn.

---

## 3. Проверка artboard (1 мин)

1. Вкладка **Design** (вверху).
2. Слева клик **Artboard** (часто `Hero360` или `360×480`).
3. Справа в Inspector: **W = 360**, **H = 480**.
4. Лицо героя — в **верхней половине** кадра (не внизу).

---

## 4. Preview всех эмоций (5 мин) — «куда жать»

### 4.1 Перейти в Animate

1. Вверху нажмите **Animate** (не Design).

### 4.2 Найти State Machine

1. **Слева** список анимаций (Animations / Timeline list).
2. Найдите **`HeroSM`** (или единственный **State Machine**).
3. **Клик** по `HeroSM` — внизу откроется **граф** (кружки-состояния: idle, happy, sad…).

### 4.3 Панель Inputs (ручной Preview)

1. Внизу или справа от графа — вкладка / секция **Inputs**.
2. Там список:
   - **Triggers:** `idle`, `listening`, `thinking`, `speaking`, `happy`, …
   - **Number:** `mouth_open` (ползунок 0…1)

### 4.4 Прогон по плану

1. Нажмите **▶ Play** (вверху).
2. В **Inputs** по очереди **кликайте** (fire) триггеры:
   - `idle` → `listening` → `thinking` → `speaking`
3. На **`speaking`**: двигайте ползунок **`mouth_open`** от **0** до **1** — рот должен открываться.
4. Дальше: `happy` → `sad` → `comfort` → `alert`.

**Запишите:** какие пары **выглядят одинаково** (например happy = idle) — их правите в §5.

> iOS шлёт те же имена — **не переименовывайте** `Happy` / `happy1` и т.д.

---

## 5. Доводка 12 мимик (основная работа, ~20–40 мин на героя)

### 5.1 Выбрать state

1. Режим **Animate**, открыт **`HeroSM`**.
2. В **графе SM** **двойной клик** по кружку **`sad`** (или `happy`, …).
3. Внизу откроется **Timeline** именно для этого state.

### 5.2 Выбрать слои лица

1. Слева в Outliner раскройте группу лица (часто `Face`, `head`, или слои с картинкой).
2. Выделите **`mouth`** (или слой рта).
3. Для **sad**: опустите уголки рта / смените форму (см. таблицу M6 в PATH_A).
4. Выделите **`brow_L`**, **`brow_R`** — опустите брови для sad.
5. При необходимости **`eye_L`**, **`eye_R`** — веки полуприкрыты.

### 5.3 Закрепить ключевой кадр

1. На таймлайне в **начале** клипа (ромб / keyframe).
2. После сдвига слоёв Rive запомнит позу для этого state.
3. Повторите для **каждого** из 12 states (не пропускайте `speaking`).

### 5.4 Таблица «что менять» (Аладдин)

| State | Рот | Брови | Запрет |
|-------|-----|-------|--------|
| idle | нейтраль | мягкие | улыбка |
| listening | лёгкая улыбка M1 | чуть вверх | — |
| thinking | M7 «hm» | одна выше | — |
| **speaking** | **M4** + ключи на `mouth_open` | нейтраль | — |
| happy | M2 улыбка | дуга вверх | — |
| playful | M3 | подмигивание | **без прыжка** |
| sad | M6 вниз | внутрь | звёзды, веселье |
| comfort | M1 мягко | тепло | — |
| celebrate | M3 | — | — |
| curious | M5 «о» | одна выше | — |
| nostalgic | M1 | мечтательный взгляд | — |
| excited | M3 | — | сдержанно |
| alert | M0 | серьёзно | — |

### 5.5 speaking + mouth_open (обязательно)

1. State **`speaking`** → timeline.
2. Слой **mouth** привязан к input **`mouth_open`** (если нет — в SM для speaking добавьте constraint / binding на открытие рта по Number).
3. Preview: Play + `speaking` + ползунок `mouth_open` 0→1.

---

## 6. Джин — после Аладдина

1. **File → Open** → `Resources/Companion/genie.riv`.
2. Повторите §4–§5.
3. **Дополнительно** слой дыма/искр (`extras`, `smoke`):
   - **Включить** opacity/анимацию на: `playful`, `excited`, `speaking`.
   - **Выключить** на: `idle`, `sad`, `comfort`, `listening`, `thinking`, `alert`.

---

## 7. Export в бандл (Cadet)

1. **File → Export** (или кнопка **Export** справа вверху).
2. Формат: **`.riv`** (Runtime / For runtime).
3. Сохранить **поверх**:
   - `…/Resources/Companion/aladdin.riv`
   - потом `…/Resources/Companion/genie.riv`
4. Не сохраняйте только на Desktop — иначе iOS не увидит.

### Проверка в Терминале

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion --min-kb 25
./scripts/verify_companion_rive_ios_bundle.sh
```

В чат: **`aladdin готов`** · **`genie готов`**.

---

## 8. Единорог — только проверка

Вы **не обязаны** переделывать unicorn, если не трогали файл.

1. Open `unicorn.riv`.
2. §4 Preview — все 13 triggers + `mouth_open`.
3. Если OK — эталон не трогаем.

---

## 9. Rive серая / не открывает файл (двойной клик и перетаскивание)

> **Почему так:** иконка в Dock **серая**, если приложение **не запущено** или **зависло**. Перетаскивание на серую иконку **не сработает**. На `.riv` иногда висит **карантин macOS** (скачано через Chrome) — Finder не отдаёт файл редактору.

### Способ A — надёжный (сначала Rive, потом файл)

1. **Полностью закройте Rive:** `⌘Q` в окне Rive. Если не реагирует: **⌘⌥Esc** → **Rive** → **Принудительно завершить**.
2. Откройте **Finder → Программы → Rive** (двойной клик). Дождитесь окна (логин Cadet / главный экран).
3. В Rive: **File → Open…** (`⌘O`).
4. В диалоге нажмите **`⌘⇧G`** (Переход к папке) и **вставьте целиком**:

```text
/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/Resources/Companion
```

5. Выберите **`unicorn.riv`** → **Open**.

### Способ B — Терминал (обходит Finder)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/companion_07_open_in_rive.sh unicorn
```

(для Аладдина: `… open_in_rive.sh aladdin`, для Джина: `… genie`)

### Способ C — «Открыть с помощью»

1. В Finder откройте папку `Resources/Companion`.
2. **Правый клик** по `unicorn.riv` → **Открыть с помощью** → **Rive**.
3. Если Rive нет в списке: **Другая…** → **Программы → Rive** → включите **«Всегда открывать»** (по желанию).

### Снять карантин macOS (один раз)

```bash
xattr -d com.apple.quarantine "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/Resources/Companion/unicorn.riv"
xattr -d com.apple.quarantine "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/Resources/Companion/aladdin.riv"
xattr -d com.apple.quarantine "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/Resources/Companion/genie.riv"
```

### Что **не** делать

| Не работает | Почему |
|-------------|--------|
| Перетащить на **серую** иконку Rive в Dock | Rive не запущен или завис |
| Двойной клик `.riv` без привязки к Rive | macOS не знает программу (тип `public.data`) |
| Открыть `aladdin_work_in_progress.riv` | это черновик, не бандл |

**Признак успеха:** под иконкой Rive в Dock **точка** (приложение запущено), в заголовке окна — `unicorn.riv` (или aladdin/genie).

---

## 10. Частые «не вижу кнопку»

| Проблема | Решение |
|----------|---------|
| Нет Inputs | Убедитесь: выбран **HeroSM**, нажат **Play** |
| Нет HeroSM | Слева в списке анимаций — ищите State Machine с 13 входами; не создавайте новый с другими именами |
| Все эмоции одинаковые | Нормально до §5 — нужно править **каждый state** отдельно |
| Вижу единорога на aladdin | Открыт не тот файл — нужен **aladdin.riv** после export с PNG Аладдина |
| Export серый | Cadet должен быть активен; File → Export |

---

## 11. Что вы **не** делали (и это OK)

| Действие | Кто |
|----------|-----|
| `open -a Rive aladdin.riv genie.riv` | ML из Cursor |
| Сборка `aladdin.riv` / `genie.riv` из unicorn + PNG | скрипт `companion_07_patch_riv_hero_image.py` |
| 12 мимик в Rive | **только вы** по этой инструкции |

---

*См. также [COMPANION_HERO_07_PATH_A_RIVE_ANIMATOR.md](./COMPANION_HERO_07_PATH_A_RIVE_ANIMATOR.md)*
