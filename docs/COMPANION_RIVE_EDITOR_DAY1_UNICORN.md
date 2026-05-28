# Rive Editor — День 1: `unicorn.riv` (пошагово)

**Кратко (5 шагов, все герои):** [COMPANION_RIVE_EDITOR_5_STEPS.md](./COMPANION_RIVE_EDITOR_5_STEPS.md)  
**Статус:** ⏳ в работе · **Следующий:** [DAY2 aladdin](./COMPANION_RIVE_ANIMATOR_PLAN_SUPPLEMENT.md)  
**Контракт iOS:** 360×480 · 13 triggers · `mouth_open` Number  
**PNG:** `docs/assets/unicorn_master_crop_360x480.png`

---

## Перед стартом (2 мин)

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/companion_07_sync_master_png_to_bundle.sh
./scripts/companion_07_prepare_rive_import.sh
./scripts/companion_07_open_in_rive.sh unicorn   # открыть placeholder в Rive
```

**Уже в приложении (iOS):** пока `.riv` &lt; 25 KB — показывается **`unicorn_master.png`** из бандла (`CompanionHeroRasterView`). После export production `.riv` — автоматически переключится на Rive.

---

## Шаг 1 — новый файл

1. Открыть **Rive** (Production, Mac).
2. **New file** → имя: `ALADDIN_unicorn_companion`.
3. Выбрать artboard / scene: размер **360 × 480** (Width × Height в pt).

---

## Шаг 2 — импорт art

1. **File → Import** (или перетащить PNG).
2. Файл:

   ```
   ALADDIN_iOS/docs/assets/unicorn_master_crop_360x480.png
   ```

3. Выровнять героя по центру safe zone (лицо в верхних ~45% кадра).
4. **Только герой** — без текста/UI.

---

## Шаг 3 — State Machine

1. Вкладка **Animate** → создать **State Machine** (имя например `HeroSM`).
2. Добавить **Inputs:**

| Имя | Тип | Заметка |
|-----|-----|---------|
| `mouth_open` | **Number** | 0 … 1 |
| `emotion` | через **13 transitions** как **Trigger** inputs | имена **точно** ниже |

3. **Trigger inputs** (создать 13 штук, имена **копировать**):

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

> iOS вызывает `triggerInput("happy")` и `setInput("mouth_open", value:)` — см. `CompanionHeroRiveHost.swift`.

---

## Шаг 4 — анимации (минимум для MVP)

Для каждого trigger — **одно состояние** (можно начать с копии idle + лёгкие отличия бровей/рта):

| Trigger | Минимум движения (unicorn) |
|---------|----------------------------|
| `idle` | дыхание 2 s loop |
| `listening` | уши/голова чуть вперёд |
| `thinking` | взгляд вверх |
| `speaking` | рот открывается от **`mouth_open`** |
| `happy` | улыбка |
| `sad` | линия рта вниз, **без** звёзд |
| `playful` | лёгкий bob |
| `comfort` | мягкая улыбка |
| остальные | отличимы от idle на скрине |

**Связать `mouth_open`:** в state `speaking` привязать открытие рта к input Number (0 = закрыт, 1 = открыт).

---

## Шаг 5 — Export

1. **Export** → **`.riv`** (For runtime).
2. Сохранить как:

   ```
   ALADDIN_iOS/Resources/Companion/unicorn.riv
   ```

   (заменить placeholder ~15 KB).

3. Проверка в терминале:

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion
./scripts/verify_companion_rive_ios_bundle.sh
```

4. Xcode → **реальный iPhone** → Мир героев → Главное → единорог: должен быть **новый** art (не круг-заглушка).

---

## Шаг 6 — отметить прогресс

| Когда | Действие |
|-------|----------|
| `unicorn.riv` gate OK | Написать в чат: **«unicorn.riv готов»** |
| Все 3 файла | **«07 готов»** → TRACKER `[x]` HERO-3-07 → **11c** |

---

## День 2 и 3

| День | Файл | PNG |
|------|------|-----|
| 2 | `aladdin.riv` | `aladdin_master_OB01_crop_360x480.png` |
| 3 | `genie.riv` | `onboarding_OB03_APP_360x480_FILL_headfix_v1.png` |

Можно **дублировать** файл unicorn → переименовать art → тот же SM (быстрее).

---

## Параллельно (не Rive)

**HERO-3-11b** на iPhone build **210+** — [COMPANION_HERO3_11B_DEVICE_SESSION.md](./COMPANION_HERO3_11B_DEVICE_SESSION.md) (placeholder `.riv` OK).
