# ALADDIN Hero Asset Production Pipeline (End-to-End Algorithm)

**Цель:** Полный воспроизводимый алгоритм создания hero-иллюстраций для онбординга (9 экранов) + Main.  
Данный документ позволяет любой ML-системе или команде точно повторить процесс, который был использован для первой страницы (OnboardingHero_00).

**Применение:**  
- Страницы 0–7 (онбординг)  
- Main (HeroMainScreenBackdrop)  
- Tier 1 / Tier 2 / Tier 3 (разная глубина проработки)

---

## 1. Общая структура процесса (одна страница)

Для каждой hero-иллюстрации выполняем 7 шагов:

1. **Story Definition** — описываем, какая часть истории рассказывается на этом экране.
2. **Prompt Engineering** — пишем максимально детальный промпт (на основе Character Bible + прогрессии).
3. **Image Generation** — генерируем 8–12 вариантов через AI.
4. **Asset Naming & Storage** — сохраняем под каноническим именем.
5. **Xcode Asset Catalog Integration** — добавляем в Images.xcassets с правильной структурой.
6. **Code Polish** — подключаем, усиливаем градиент читаемости, добавляем минимальную анимацию (если нужно).
7. **Visual QA** — запускаем симулятор, проверяем читаемость, композицию, перф.

---

## 2. Конкретный пример: Страница 0 (Выбор языка) — OnboardingHero_00

### Шаг 2.1. Story Definition

**Место в истории:**  
Самый первый экран. Пользователь только открыл приложение. Мы показываем **Лампу** как источник волшебства и лёгкий намёк на Единорога (золотое сияние рога в дыму). Это «приглашение в историю».

**Эмоция:** Любопытство, тепло, «меня ждут».  
**Tier:** 1 (лёгкий) — минимальная анимация, можно PNG + свечение в коде.  
**Композиция:** Hero-зона ~60% сверху (393×852). Низ должен «дышать» под текст.

### Шаг 2.2. Prompt Engineering

**Используемые источники:**
- `ALADDIN_Character_Bible.md` (персонажи, стиль, палитра)
- `ALADDIN_Onboarding_Prompts.md` (детальный промпт для слайда 0)
- Общий стиль: `highly detailed 3D render style, volumetric lighting, cinematic, soft realistic materials and textures...`

**Финальный промпт, который был использован:**

```
A magical night bedroom scene with a glowing golden oil lamp floating gently in soft volumetric smoke, subtle golden light hint of a small unicorn horn visible in the mist as a gentle first hint of the character, warm cozy bedside lamp lighting, soft god rays, highly detailed 3D render style, volumetric lighting, cinematic, soft realistic materials and textures, subsurface scattering, beautiful soft shadows and highlights, emotional storytelling, family-friendly, no text on image, indigo and golden color palette with warm pastel accents, beautiful bokeh, cozy and inviting atmosphere
```

### Шаг 2.3. Image Generation

**Инструмент:** Встроенный генератор изображений Cursor (на базе продвинутой модели).  
**Количество вариантов:** 8–12 (в данном случае взята первая удачная).  
**Результат (мастер в репозитории):**  
`ALADDIN_iOS/Resources/HeroAssets/OnboardingHero_00.png` (полный кадр; в каталог для рантайма — обрезка/масштаб 393×852 в `OnboardingHero_00.imageset/OnboardingHero_00.png`). См. также `Resources/HeroAssets/README.txt`.

### Шаг 2.4. Asset Naming & Storage

**Каноническое имя:** `OnboardingHero_00` (см. `HeroSlot.onboardingLanguage` и `HeroPresentation` в `HeroAmbientPresentation.swift`).

**Физическое расположение в репозитории:**
```
ALADDIN_iOS/
└── Resources/
    └── HeroAssets/
        └── OnboardingHero_00.png          ← исходный файл
```

### Шаг 2.5. Xcode Asset Catalog Integration

**Действия (выполнены автоматически):**

1. Создана папка:
   ```
   Assets.xcassets/OnboardingHero_00.imageset/
   ```

2. Скопирован файл:
   ```
   OnboardingHero_00.imageset/OnboardingHero_00.png  (корень `Assets.xcassets`, не вложенный `Images.xcassets`)
   ```

3. Создан `Contents.json`:
   ```json
   {
     "images": [
       {
         "filename": "OnboardingHero_00.png",
         "idiom": "universal",
         "scale": "3x"
       }
     ],
     "info": { "author": "xcode", "version": 1 }
   }
   ```

**Результат:** Код уже знает имя `OnboardingHero_00` — ничего править не нужно.

### Шаг 2.6. Code Polish (HeroAmbientPresentation + OnboardingScreen)

**Изменения:**

1. **Усиление градиента читаемости** (`HeroBottomReadableGradient`):
   - Добавлен параметр `strong: Bool`
   - На шаге языка (`currentPage == 0`) используется `strong: true` → opacity 0.62 вместо 0.48

2. **Лёгкая анимация «пульс лампы»** (Tier 1):
   - В `HeroAmbientLayerView` добавлено:
     ```swift
     .scaleEffect(slot == .onboardingLanguage ? (1.0 + sin(Date().timeIntervalSinceReferenceDate) * 0.008) : 1.0)
     .animation(.easeInOut(duration: 3.2).repeatForever(autoreverses: true), value: slot)
     ```
   - Очень лёгкая нагрузка, не влияет на старые iPhone.

**Файлы, которые были изменены:**
- `Shared/Components/HeroAmbientPresentation.swift`
- `Screens/14_OnboardingScreen.swift`

### Шаг 2.7. Visual QA

**Что проверяем в симуляторе:**
- Композиция: лампа и намёк на Единорога находятся в верхней hero-зоне.
- Читаемость: список языков и кнопка «Продолжить» хорошо видны благодаря усиленному градиенту.
- Анимация: лёгкий пульс лампы (не отвлекает).
- Перф: Tier 1 — должно работать даже на iPhone XR / SE 2020.
- RTL: при необходимости применяется flip.

---

## 3. Общий шаблон для остальных страниц (1–8 + Main)

Для каждой следующей hero-иллюстрации повторяем тот же цикл:

1. Взять промпт из `ALADDIN_Onboarding_Prompts.md`
2. Сгенерировать 8–12 вариантов
3. Сохранить под именем `OnboardingHero_0N.png` или `MainHero_ambient.png`
4. Добавить в Asset Catalog по тому же шаблону
5. При необходимости добавить лёгкую анимацию (только Tier 2–3)
6. Усилить градиент читаемости, если фон яркий
7. Проверить в симуляторе (0…N проход)

**Важно:**  
- Tier 1 (0, 1, 4) — можно PNG + свечение в коде  
- Tier 2 (2, 3, 6) — лёгкая Lottie (≤3 слоя)  
- Tier 3 (5, 7, Main) — полноценная Lottie, максимальная детализация

---

## 4. Источники правды (не менять без согласования)

- `docs/ALADDIN_Character_Bible.md` — внешность, цвета, стиль генерации
- `docs/ALADDIN_Onboarding_Prompts.md` — все 9 детальных промптов + описание истории
- `docs/ONBOARDING_MAIN_HERO_HANDOFF.md` — §5.B (прогрессивная история), §5.C (visual style), §1.8 (не ломать вёрстку)
- `docs/ALADDIN_Hero_Asset_Pipeline.md` — текущий документ (этот алгоритм)

---

*Этот документ — канон для всех hero-ассетов. Любая ML-система или разработчик должны следовать ему, чтобы получить консистентный результат на всех 9 экранах.*