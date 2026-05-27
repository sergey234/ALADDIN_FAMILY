# HERO-3-08b — проверка Rive на устройстве (5 мин)

**Цель:** на вкладке **Главное** (`CompanionHome`) видна **Rive-сцена** (placeholder `.riv` допустим), не краш и не emoji-заглушка.

**Не использовать для Rive-QA:** симулятор **iOS 15.2** (известный сбой Metal/Rive: `currentDrawable`, `missing sampler binding`).  
**Основной прогон:** **реальный iPhone** (записать модель и версию iOS в протокол ниже).

Figma / финальный арт (**HERO-3-07**) — параллельно, **не блокер** для 08b: достаточно placeholder `.riv` из бандла.

---

## Протокол прогона (заполнить после теста)

| Поле | Значение |
|------|----------|
| Дата | |
| Тестер | |
| Устройство (модель) | |
| iOS версия | |
| Build (CFBundleVersion) | |
| Результат | PASS / FAIL |
| Заметки | |

---

## Автопроверка до устройства

```bash
cd mobile_apps/ALADDIN_iOS
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN \
  -destination 'generic/platform=iOS' build
./scripts/verify_companion_rive_ios_bundle.sh
```

---

## Навигация на устройстве

1. Схема **ALADDIN** → **Run** на **вашем iPhone** (не iOS 15.2 Simulator).
2. Онбординг / вход в семейный режим.
3. **Aladdin Kids** → **награды / игры**.
4. Карточка **«Мир героев»** → `CompanionHomeScreen`.
5. Вкладки: **Главное** · **Герои** · **Моё**.
6. **Герои** → выбрать **Единорог** (или доступного героя) → переход на **Главное**.
7. На **Главное**:
   - верх ~**56%** — прямоугольная сцена;
   - низ — **субтитр** (не лента пузырей);
   - отправить **«Привет!»** — герой «думает», затем ответ, **поза/эмоция меняется**.

---

## PASS / FAIL (без emoji как критерий продукта)

| ✅ PASS | ❌ FAIL |
|--------|--------|
| В сцене **движущийся Rive** (арт из `.riv`, placeholder OK) | Только крупный emoji на градиенте |
| Нет краша при смене героя и вкладок | SIGABRT / чёрный экран |
| Субтитр + ввод работают | Навигация сломана |

**Не считать PASS:** только градиент без анимации (shell на симуляторе 15.x — для 08b нужен **device**).

---

## Умный выключатель Rive (для разработчиков)

| Условие | Поведение |
|---------|-----------|
| **Реальный iPhone** + `.riv` в бандле + экран active | **Rive всегда** |
| Симулятор **iOS 15.x** | Rive **выключен** (нет краша); сцена — фон без emoji; в Debug подпись «проверка на device» |
| Фон / нулевой размер сцены | Rive не рисует кадр (защита Metal) |

Код: `CompanionHeroRiveHost.shouldUseRiveRuntime`, `isSimulatorIOS15MetalUnstable`.

---

## После PASS

1. Отметить **HERO-3-08b** и пункт device в **GATE-P0** в [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md).
2. Следующий шаг: **[HERO-3-11](./COMPANION_HERO3_11_QA_CHECKLIST.md)** (11a auto ✅ → 11b device).
3. Параллельно: **HERO-3-07** — Figma → Rive Editor → export `.riv` → `Resources/Companion/`.

---

## Если FAIL на device

```bash
./scripts/reset_rive_spm_cache.sh
```

Xcode: **File → Packages → Resolve Package Versions** → Clean → Build → повторить прогон.
