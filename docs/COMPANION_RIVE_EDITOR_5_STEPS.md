# Rive Editor — 5 шагов (без Node, без Lottie)

**Для кого:** вы в **Rive.app** на Mac · **HERO-3-07**  
**Контракт iOS:** artboard **360×480** · **13 triggers** · Number **`mouth_open`** 0…1  
**Подробнее:** [DAY1 unicorn](./COMPANION_RIVE_EDITOR_DAY1_UNICORN.md) · [Export checklist](./COMPANION_RIVE_EXPORT_CHECKLIST.md) · [Motion/Mimic](./COMPANION_RIVE_ANIMATOR_PLAN_SUPPLEMENT.md)

---

## Перед 5 шагами (2 минуты в Терминале)

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/companion_07_sync_master_png_to_bundle.sh
./scripts/companion_07_prepare_rive_import.sh
./scripts/companion_07_open_in_rive.sh unicorn   # или aladdin / genie
```

Пока `.riv` меньше ~25 KB — в приложении показывается **PNG** (`CompanionHeroRasterView`). После export production `.riv` — автоматически **живая** Rive-анимация.

| Герой | Файл export | PNG для импорта |
|-------|-------------|-----------------|
| unicorn | `Resources/Companion/unicorn.riv` | `docs/assets/unicorn_master_crop_360x480.png` |
| aladdin | `Resources/Companion/aladdin.riv` | `docs/assets/aladdin_master_OB01_crop_360x480.png` |
| genie | `Resources/Companion/genie.riv` | `docs/assets/onboarding_OB03_APP_360x480_FILL_headfix_v1.png` |

**Порядок:** сначала **unicorn** (эталон State Machine) → скопировать файл → заменить арт для aladdin и genie.

---

## Шаг 1 — Import PNG

**Цель:** положить мастер-картинку в сцену 360×480.

1. Открыть **Rive** → **New file** (или открыть placeholder через скрипт выше).
2. Artboard / scene: **Width 360** · **Height 480** (pt).
3. **Import** PNG из таблицы (перетащить или File → Import).
4. Выровнять героя по центру: **лицо в верхних ~45%** кадра (читается в круге 88×88 и в чате ~56% высоты).
5. **Только персонаж** — без текста, кнопок, подписей Figma.

**Не обязательно** сразу векторизовать весь герой. Для MVP можно оставить один слой PNG и анимировать **отдельные** элементы лица поверх; для меньшего веса файла позже — trace / redraw вектором.

---

## Шаг 2 — Слои (чтобы лицо могло двигаться)

**Цель:** разнести лицо так, чтобы брови, глаза и рот менялись между эмоциями.

Минимальный набор (имена в Rive — как удобно, **inputs iOS не трогаем**):

| Слой | Зачем |
|------|--------|
| `body` / `torso` | bob, наклон плеч (sad, comfort) |
| `head` | лёгкий поворот listening / thinking |
| `brow_L` · `brow_R` | happy, sad, alert, thinking |
| `eye_L` · `eye_R` | моргание в idle, curious |
| `mouth` | все эмоции + **speaking** |
| `cheek` (опц.) | playful, comfort |
| `extras` | unicorn: рог/уши; genie: **дым/искры** (только playful / excited / speaking) |

**Как сделать в Editor (типично):**

1. Дублировать или **обрезать** части из PNG (Crop / separate images) **или** нарисовать вектор поверх.
2. Сгруппировать: `Face` → дети mouth, eyes, brows.
3. Привязать **origin** рта к центру губ — для `mouth_open` масштаб/открытие шло от одной точки.

**Референс 12 лиц:** Figma Companion `vwKcGPUUEZjgayEHNn0BJM` — страницы `01_Unicorn` … `03_Genie` (сетка эмоций). В Rive нужен ещё state **`speaking`** — его нет отдельным постером в Figma.

---

## Шаг 3 — 13 эмоций (State Machine)

**Цель:** iOS по имени вызывает trigger — герой переключает «настроение».

1. Вкладка **Animate** → **State Machine** (имя например `HeroSM`).
2. Создать **13 Trigger inputs** — имена **скопировать один в один** (регистр важен):

```
idle
listening
thinking
speaking
happy
playful
sad
comfort
celebrate
curious
nostalgic
excited
alert
```

3. Для **каждого** trigger — **своё состояние** (State) в графе SM.
4. Связать переходы: trigger → соответствующий state (Rive: transition on input).
5. **Переходы между эмоциями:** cross-fade **200–300 ms**; listening ↔ thinking **~150 ms**.

**Минимум движения по состояниям (MVP):**

| State | Что видно на экране |
|-------|-------------------|
| `idle` | лёгкое «дыхание» 2 s loop |
| `listening` | голова/уши чуть вперёд |
| `thinking` | взгляд вверх, брови |
| `speaking` | см. шаг 4 |
| `happy` | улыбка |
| `sad` | рот вниз, **без** «праздничных» эффектов |
| `playful` | лёгкий bob / подмигивание |
| `comfort` | мягкая улыбка |
| `alert` | серьёзные брови, прямой рот |
| остальные | хотя бы **одно** отличие от idle (брови/рот/взгляд) |

**Preview в Rive:** прогнать цепочку  
`idle` → `listening` → `thinking` → `speaking` → `happy` → `sad` → `idle`.

**genie:** дым и искры **только** на `playful`, `excited`, `speaking` — **выключить** на `sad` и `comfort`.

---

## Шаг 4 — `mouth_open` (рот от TTS)

**Цель:** пока герой в режиме **speaking**, рот открывается от 0 до 1; iOS шлёт число ~12 раз в секунду.

1. В State Machine добавить input: **`mouth_open`** · тип **Number** · диапазон **0 … 1**.
2. В state **`speaking`**:
   - привязать высоту/масштаб рта (или blend shape) к **`mouth_open`**;
   - при **0** — рот закрыт, при **1** — максимально открыт.
3. В **остальных** states рот **закрыт** (не дублировать speaking-логику).
4. В Preview: выбрать state `speaking`, вручную двигать `mouth_open` 0 → 0.5 → 1 — рот должен **заметно** меняться.

iOS: `triggerInput("speaking")` + `setInput("mouth_open", value:)` — см. `CompanionHeroRiveHost.swift`.

---

## Шаг 5 — Export и проверка

**Цель:** положить production `.riv` в бандл и пройти gate.

1. **Export** → **`.riv`** (For runtime / iOS).
2. Сохранить **поверх** placeholder:

   ```
   ALADDIN_iOS/Resources/Companion/unicorn.riv
   ALADDIN_iOS/Resources/Companion/aladdin.riv
   ALADDIN_iOS/Resources/Companion/genie.riv
   ```

   Production файл обычно **> 25 KB** (placeholder ~15 KB).

3. Терминал:

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion
./scripts/verify_companion_rive_ios_bundle.sh
```

4. Xcode → **реальный iPhone** → сцена с героем: должен играть **Rive**, не статичный PNG.
5. Проверить: `listening` / `thinking` / `speaking` **различимы**; при TTS ≥1 s виден **рот**.

**Когда готово:** все 3 файла → в чат **«07 готов»** → TRACKER **HERO-3-07** → **11c** (MIMIC на device).

---

## Частые ошибки

| Ошибка | Последствие |
|--------|-------------|
| Переименовать trigger (`Happy` вместо `happy`) | iOS не найдёт input — останется idle |
| Нет state `speaking` | TTS без «говорящего» лица |
| Нет Number `mouth_open` | рот не синхронизируется |
| Artboard не 360×480 | обрезка / неверный scale в чате |
| `.riv` &lt; 25 KB | приложение покажет **PNG bridge**, не вашу анимацию |

---

## День 2–3 (копия SM)

1. **File → Duplicate** проект unicorn.
2. Заменить арт на aladdin / genie PNG.
3. Подкрутить motion по [PLAN_SUPPLEMENT §4](./COMPANION_RIVE_ANIMATOR_PLAN_SUPPLEMENT.md) (аладдин сдержаннее, джин — дым только где разрешено).
4. Export в соответствующий `.riv`.

**Node / RiveMCP / Lottie на этом пути не нужны.**
