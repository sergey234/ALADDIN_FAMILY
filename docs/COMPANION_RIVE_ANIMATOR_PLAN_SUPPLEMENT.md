# HERO-3-07 — дополнение к плану для аниматора

**Версия:** 1.0 · **2026-05-28**  
**Краткая страница:** [COMPANION_RIVE_ANIMATOR_BRIEF.md](./COMPANION_RIVE_ANIMATOR_BRIEF.md)  
**6 шляп (аудит):** [COMPANION_RIVE_ANIMATOR_6_HATS_AUDIT.md](./COMPANION_RIVE_ANIMATOR_6_HATS_AUDIT.md)  
**Export чеклист:** [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md)

---

## 1. Цель (одна строка)

Собрать **3 production `.riv`** (360×480), чтобы iOS **только подменил файлы** в `Resources/Companion/` — без правок Swift.

---

## 2. Три файла × master (PO lock ✅)

| Export | `character_id` | Production master | PNG (репо) | Figma Companion |
|--------|----------------|-------------------|------------|-----------------|
| **`unicorn.riv`** | `unicorn` | **v2 cinematic** | `docs/assets/unicorn_master_crop_360x480.png` | `01_Unicorn` · [25:2](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes?node-id=25-2) |
| **`aladdin.riv`** | `aladdin` | **OB_01** human | `docs/assets/aladdin_master_OB01_crop_360x480.png` | `02_Aladdin_Human` · 12× `aladdin/emotion/*` |
| **`genie.riv`** | `genie` | **OB_03 headfix** | `docs/assets/onboarding_OB03_APP_360x480_FILL_headfix_v1.png` | `03_Genie` · [122:2](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes?node-id=122-2) |

**Figma file:** `vwKcGPUUEZjgayEHNn0BJM` · **Onboarding (read-only):** `KvkUdyb5Ll31Z9FSzCbpNl`

**genie mood (не master):** OB_04/06/07 — палитра, свечение; [CANON §3](./COMPANION_HERO_ART_CANON.md).

---

## 3. Технический контракт с iOS (обязательно)

Источник: `UI/Companion/CompanionHeroAvatarView.swift` → `CompanionHeroRiveMapping.riveStateName`

### 3.1 State Machine

| Input | Тип | Значения |
|-------|-----|----------|
| **`emotion`** | **Trigger** (13 шт.) | см. таблицу ниже |
| **`mouth_open`** | **Number** | **0.0 … 1.0** (TTS / speaking) |

### 3.2 Триггеры `emotion` (все 13 — иначе iOS молчит)

| Trigger | Фаза / контент | В Figma-постере 02? |
|---------|----------------|---------------------|
| `idle` | Hub + ожидание | ✅ |
| `listening` | Mic on | ✅ |
| `thinking` | Ждёт ответ | ✅ |
| **`speaking`** | **Говорит + рот** | ❌ (только Rive) |
| `happy` | контент | ✅ |
| `playful` | контент | ✅ |
| `sad` | контент | ✅ |
| `comfort` | контент | ✅ |
| `celebrate` | контент | ✅ |
| `curious` | контент | ✅ |
| `nostalgic` | контент | ✅ |
| `excited` | контент | ✅ |
| `alert` | контент | ✅ |

> **12 постеров** в Figma = имена без отдельного кадра `speaking`; в Rive state **`speaking` обязателен**.

### 3.3 `mouth_open`

- В state **`speaking`**: рот открывается пропорционально значению.
- Во всех остальных state: держать **0** (или не анимировать рот).
- iOS шлёт синус 0.35…0.6 при TTS (~12 Hz) — рот должен **визуально** реагировать.

### 3.4 Размер и fit

| Параметр | Значение |
|----------|----------|
| Artboard | **360 × 480** |
| Fit в app | `contain`, center |
| Conversation | rect **~56%** высоты экрана |
| Hub preview | круг **88×88** (лицо должно читаться) |
| Safe zone лица | короткая сторона лица **≥ 96 pt** на device |

---

## 4. Motion × герой (как рисовать движение)

Из [плана §2.2](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) — кратко:

| State | Единорог | Аладдин | Джин |
|-------|----------|---------|------|
| **idle** | мягкий bob 2.4 Hz | почти статичен | дым idle loop |
| **listening** | уши/рог вперёд | лёгкий кивок | дым к «ушам» |
| **thinking** | взгляд вверх | рука у подбородка (если есть) | искра над головой |
| **speaking** | bob + **mouth_open** | спокойный рот | **дым пульс** + рот |
| **playful** | мини-прыжок PG | улыбка, **без** прыжка | искры PG |
| **sad / comfort** | плечи ниже, **без** звёзд | тепло, без дыма | **без** дыма/искр |
| **alert** | уши настороже | серьёзный взгляд | дым слегка краснее, **не страшно** |

**Переходы:** cross-fade **200–300 ms** (idle ↔ content; listening ↔ thinking **150 ms**).

**Запрещено:** одновременно `speaking` + `sad` в одной композиции — iOS переключает по фазам.

---

## 5. Mimic × герой (12 контент-лиц)

Слои (все герои): `brow_*` · `eye_*` · `mouth_shape` · `cheek_blush` · `extras` (PG).

| Эмоция | Минимум отличия (MIMIC-Q1) |
|--------|----------------------------|
| happy vs sad | улыбка vs линия рта вниз |
| playful vs happy | подмигивание / шире рот |
| alert vs idle | прямая линия рта, серьёзные брови |
| thinking vs curious | взгляд вверх vs «о» рот |
| comfort vs sad | мягкая улыбка vs грусть |

**genie:** дым/искры **только** `playful` · `excited` · `speaking` — **не** на `sad`/`comfort`.

---

## 6. Пошаговый workflow (Rive Editor)

### Шаг 0 — подготовка

1. Скачать 3 PNG master из таблицы §2 (или экспорт из Figma Companion).
2. Открыть Figma `00_Spec` → `Motion_Spec` · `Mimic_Spec` (референс таймингов).
3. Создать artboard **360×480** × 3 файла.

### Шаг 1 — unicorn (эталон SM)

1. Import PNG → trace / redraw вектор (предпочтительно вектор для размера).
2. Разнести слои лица L1–L5.
3. Собрать **State Machine** с 13 triggers + `mouth_open`.
4. Прогнать в Rive preview: idle → listening → thinking → speaking (mouth 0→1) → happy.
5. Export `unicorn.riv`.

### Шаг 2 — aladdin

1. Import `aladdin_master_OB01_crop_360x480.png`.
2. **Скопировать структуру SM** с unicorn; заменить арт.
3. Убрать «магические» эффекты джина; сдержаннее амплитуда bob.
4. Export `aladdin.riv`.

### Шаг 3 — genie

1. Import **OB_03 headfix** (не полный экран OB_07 с UI).
2. Скопировать SM; добавить слой дыма (отдельный loop).
3. Проверить: sad/comfort — **дым выключен**.
4. Export `genie.riv`.

### Шаг 4 — сдача в репо

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
# положить файлы:
#   Resources/Companion/unicorn.riv
#   Resources/Companion/aladdin.riv
#   Resources/Companion/genie.riv

python3 scripts/companion_riv_size_gate.py --dir Resources/Companion
./scripts/verify_companion_rive_ios_bundle.sh
```

**Ожидание:** `OK` ×3, каждый **&lt; 512000** bytes.

### Шаг 5 — handoff QA

- Написать PO/Dev: «07 готово, прошу **11c** на build **210+**».
- Приложить **скриншот-сетку** 13 state × 3 героя (или 12+speaking).

---

## 7. DoD — чеклист перед сдачей

- [ ] 3 файла в `Resources/Companion/` с правильными именами
- [ ] Artboard 360×480
- [ ] 13 triggers `emotion` (имена **точно** как §3.2)
- [ ] Number input `mouth_open` 0…1
- [ ] `speaking` + `mouth_open` визуально связаны
- [ ] sad/comfort без playful-эффектов (genie: без дыма)
- [ ] size gate exit 0
- [ ] verify_companion_rive_ios_bundle.sh exit 0
- [ ] Скриншоты для MIMIC-Q1 (11c)

---

## 8. Чего не делать

| Не делать | Почему |
|-----------|--------|
| 12 отдельных `.riv` | Продукт = 1 файл на героя |
| Текст/UI на арте | Companion = только персонаж |
| Переименовать triggers | iOS hardcoded |
| genie из OB_02-only | Master = OB_03 |
| aladdin с 🧞-дымом | Другой персонаж |
| unicorn CONCEPT круги | Deprecated |
| Ждать 12 разных PNG v2 | v1.1 достаточно; лица в Rive |

---

## 9. Приёмка после сдачи

| Этап | Кто | ID |
|------|-----|-----|
| Автотесты | CI | 11a (уже ✅) |
| Device логика | PO | 11b (placeholder, параллельно) |
| Device лица | PO/QA | **11c** после ваших `.riv` |
| Продукт | PO | **GATE-EMO** |

Чеклист device: [COMPANION_HERO3_11_QA_CHECKLIST.md](./COMPANION_HERO3_11_QA_CHECKLIST.md)

---

## 10. Контакты в репо

| Вопрос | Документ |
|--------|----------|
| Галочки 102 | [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) |
| Полный план героев | [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) |
| iOS host | `UI/Companion/CompanionHeroRiveHost.swift` |

---

*Дополнение к плану утверждено по методу 6 шляп — см. [AUDIT](./COMPANION_RIVE_ANIMATOR_6_HATS_AUDIT.md).*
