# PLAN ITEM Wave-1 (10 задач)

Источник: `docs/PLAN_ITEM_OPEN_TASKS.md`  
Размер волны: 10 (правило 5-10 соблюдено)

## Scope

1. Разные кисти (толстая, тонкая) | `child_interface_category_drawing` | `drawing.03` | PARTIAL  
2. Шаблоны для раскрашивания | `child_interface_category_drawing` | `drawing.05` | TODO  
3. Геометрические фигуры (рисование) | `child_interface_category_drawing` | `drawing.06` | PARTIAL  
4. Цветовые игры (узнай цвет) | `child_interface_category_toys` | `toys.03` | PARTIAL  
5. Геометрические фигуры (найди круг, квадрат) | `child_interface_category_toys` | `toys.04` | PARTIAL  
6. Детские песни с текстом | `child_interface_category_songs` | `songs.01` | PARTIAL  
7. Мелодии с аккомпанементом | `child_interface_category_songs` | `songs.03` | TODO  
8. Категории песен (колыбельные/игровые/обучающие) | `child_interface_category_songs` | `songs.05` | TODO  
9. Озвучка текста проф. актерами | `child_interface_category_stories` | `stories.02` | PARTIAL  
10. Вопросы после прочтения | `child_interface_category_stories` | `stories.05` | PARTIAL

## Ownership And Dates

- `1-6 Content Squad`: 1,2,3,4,5 — due `2026-05-18`
- `1-6 Audio Squad`: 6,7,8 — due `2026-05-18`
- `1-6 Narrative Squad`: 9,10 — due `2026-05-18`

## Implementation Sources (where to build)

- Content routing and host views: `Screens/ChildContentExperienceScreen.swift`
- Category/feed and progress cards: `Screens/ChildContentScreen.swift`
- Seed titles and item ids: `Core/Content/Seed/ContentSeedProvider.swift`
- Content contracts and validation: `Core/Content/Models/ContentModels.swift`, `Core/Content/Validation/ContentValidator.swift`
- RU/EN strings: `Resources/Localization/ru.lproj/Localizable.strings`, `Resources/Localization/en.lproj/Localizable.strings`

## Mandatory Gates (must PASS)

1. `python3 scripts/plan_item_traceability_smoke.py`
2. `python3 scripts/phase2_content_qa_matrix_smoke.py`
3. `python3 scripts/localization_lint.py`
4. `xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -configuration Debug -destination 'generic/platform=iOS Simulator' build`

Wave completion rule: все 10 пунктов переведены в `DONE` или обоснованно `PARTIAL->DONE` после PASS всех гейтов.
