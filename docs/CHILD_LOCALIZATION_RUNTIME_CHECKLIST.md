# Child Localization Runtime Checklist (Manual QA)

Updated: 2026-04-29  
Purpose: detect and close defects where localization keys are shown instead of translated RU/EN text.

## How To Use

- Set app language to RU, run each row, fill `Факт RU`.
- Set app language to EN, rerun same rows, fill `Факт EN`.
- If UI shows raw key (e.g. `child_daily_journey_step_discover`) -> `Status = FAIL`.
- Pass criteria per row: both RU and EN are human-readable localized strings.

---

## 1-6 (Kids)

| Возраст | Карточка | Ключи | Ожидаемый RU | Ожидаемый EN | Факт RU | Факт EN | Статус |
|---|---|---|---|---|---|---|---|
| 1-6 | Header возраст | `child_interface_age_kids` | 1-6 лет | 1-6 years | OK (ключ в RU strings, рендер через `localized`) | OK (key in EN strings, rendered via `localized`) | PASS (precheck) |
| 1-6 | Header категория (Игрушки) | `child_interface_category_toys` | Игрушки | Toys | OK | OK | PASS (precheck) |
| 1-6 | Header категория (Рисование) | `child_interface_category_drawing` | Рисование | Drawing | OK | OK | PASS (precheck) |
| 1-6 | Header категория (Песенки) | `child_interface_category_songs` | Песенки | Songs | OK | OK | PASS (precheck) |
| 1-6 | Header категория (Сказки) | `child_interface_category_stories` | Сказки | Stories | OK | OK | PASS (precheck) |
| 1-6 | Greeting | `child_game_welcome` / `child_creativity_welcome` | Добро пожаловать в игры! / Давай творить! | Welcome to Games! / Let's create! | OK | OK | PASS (precheck) |
| 1-6 | Daily Journey title | `child_daily_journey_title` | Путь на сегодня | Today's Journey | OK | OK | PASS (precheck) |
| 1-6 | Daily Journey subtitle | `child_daily_journey_subtitle` | Пройди 3 шага: изучи -> потренируйся -> подведи итог. | Complete 3 steps: discover -> practice -> reflect. | OK | OK | PASS (precheck) |
| 1-6 | Daily Journey step 1 | `child_daily_journey_step_discover` | Изучить | Discover | OK | OK | PASS (precheck) |
| 1-6 | Daily Journey step 2 | `child_daily_journey_step_practice` | Тренировка | Practice | OK | OK | PASS (precheck) |
| 1-6 | Daily Journey step 3 | `child_daily_journey_step_reflect` | Итог | Reflect | OK | OK | PASS (precheck) |
| 1-6 | Daily tip | `child_daily_tip_kids` | (локализованный текст совета) | (localized tip text) | OK | OK | PASS (precheck) |

---

## 7-12 (School)

| Возраст | Карточка | Ключи | Ожидаемый RU | Ожидаемый EN | Факт RU | Факт EN | Статус |
|---|---|---|---|---|---|---|---|
| 7-12 | Header возраст | `child_interface_age_school` | 7-12 лет | 7-12 years | OK | OK | PASS (precheck) |
| 7-12 | Header категория (Игры) | `child_interface_category_games` | Игры | Games | OK | OK | PASS (precheck) |
| 7-12 | Header категория (Учёба) | `child_interface_category_study` | Учёба | Study | OK | OK | PASS (precheck) |
| 7-12 | Header категория (Мультики) | `child_interface_category_cartoons` | Мультфильмы | Cartoons | OK | OK | PASS (precheck) |
| 7-12 | Header категория (Творчество) | `child_interface_category_creativity` | Творчество | Creativity | OK | OK | PASS (precheck) |
| 7-12 | Safety tile label (main screen) | `family_category_safety` | БЕЗОПАСНОСТЬ | SAFETY | OK (через `LocalizationManager` словарь) | OK (через `LocalizationManager` словарь) | PASS (precheck) |
| 7-12 | Daily Journey title | `child_daily_journey_title` | Путь на сегодня | Today's Journey | OK | OK | PASS (precheck) |
| 7-12 | Daily Journey step discover/practice/reflect | `child_daily_journey_step_discover` / `...practice` / `...reflect` | Изучить / Тренировка / Итог | Discover / Practice / Reflect | OK | OK | PASS (precheck) |
| 7-12 | Journey v2 title | `child_daily_journey_v2_title` | Маршрут 7–12: темп и корректировка | Journey 7–12: Pacing & Correction | OK | OK | PASS (precheck) |
| 7-12 | Journey v2 pacing (fast) | `child_daily_journey_v2_pacing_fast` | Темп высокий... | Fast pace... | OK | OK | PASS (precheck) |
| 7-12 | Journey v2 pacing (steady) | `child_daily_journey_v2_pacing_steady` | Темп стабильный... | Steady pace... | OK | OK | PASS (precheck) |
| 7-12 | Journey v2 pacing (support) | `child_daily_journey_v2_pacing_support` | Темп просел... | Pace dropped... | OK | OK | PASS (precheck) |
| 7-12 | Journey v2 feedback keep/hint/retry | `child_daily_journey_v2_feedback_keep_going` / `...hint` / `...retry` | 3 локализованных фразы | 3 localized phrases | OK | OK | PASS (precheck) |
| 7-12 | Journey v2 action | `child_daily_journey_v2_corrective_action` | Применить корректирующий темп | Apply corrective pacing | OK | OK | PASS (precheck) |
| 7-12 | Daily tip | `child_daily_tip_school` | (локализованный текст совета) | (localized tip text) | OK | OK | PASS (precheck) |

---

## 13-17 (Teen)

| Возраст | Карточка | Ключи | Ожидаемый RU | Ожидаемый EN | Факт RU | Факт EN | Статус |
|---|---|---|---|---|---|---|---|
| 13-17 | Header возраст | `child_interface_age_teen` | 13-17 лет | 13-17 years | OK | OK | PASS (precheck) |
| 13-17 | Header категория (Программирование) | `child_interface_category_programming` | Программирование | Programming | OK | OK | PASS (precheck) |
| 13-17 | Header категория (Соцсети) | `child_interface_category_social` | Социальные сети | Social Media | OK | OK | PASS (precheck) |
| 13-17 | Header категория (Музыка) | `child_interface_category_music` | Музыка | Music | OK | OK | PASS (precheck) |
| 13-17 | Header категория (Видео) | `child_interface_category_video` | Видео | Video | OK | OK | PASS (precheck) |
| 13-17 | Safety tile label (main screen) | `family_category_safety` | БЕЗОПАСНОСТЬ | SAFETY | OK | OK | PASS (precheck) |
| 13-17 | Daily Journey title | `child_daily_journey_title` | Путь на сегодня | Today's Journey | OK | OK | PASS (precheck) |
| 13-17 | Daily Journey step discover/practice/reflect | `child_daily_journey_step_discover` / `...practice` / `...reflect` | Изучить / Тренировка / Итог | Discover / Practice / Reflect | OK | OK | PASS (precheck) |
| 13-17 | Journey v3 title | `child_daily_journey_v3_title` | Маршрут 13–22: автономность и рефлексия | Journey 13–22: Autonomy And Reflection | OK | OK | PASS (precheck) |
| 13-17 | Journey v3 focus explore | `child_daily_journey_v3_focus_explore` | Фокус дня: выбери направление... | Daily focus: choose a direction... | OK | OK | PASS (precheck) |
| 13-17 | Journey v3 focus build | `child_daily_journey_v3_focus_build` | Фокус дня: закрепи навык... | Daily focus: strengthen a skill... | OK | OK | PASS (precheck) |
| 13-17 | Journey v3 focus lead | `child_daily_journey_v3_focus_lead` | Фокус дня: выбери приоритет... | Daily focus: set your priority... | OK | OK | PASS (precheck) |
| 13-17 | Journey v3 reflection prompt/action/done | `child_daily_journey_v3_reflection_prompt` / `...action` / `...done` | 3 локализованных фразы | 3 localized phrases | OK | OK | PASS (precheck) |
| 13-17 | Daily tip | `child_daily_tip_teen` | (локализованный текст совета) | (localized tip text) | OK | OK | PASS (precheck) |

---

## 18-22 (Young Adult)

| Возраст | Карточка | Ключи | Ожидаемый RU | Ожидаемый EN | Факт RU | Факт EN | Статус |
|---|---|---|---|---|---|---|---|
| 18-22 | Header возраст | `child_interface_age_young_adult` | 18-22 лет | 18-22 years | OK | OK | PASS (precheck) |
| 18-22 | Header категория (Образование) | `child_interface_category_education` | Образование | Education | OK | OK | PASS (precheck) |
| 18-22 | Header категория (Карьера) | `child_interface_category_career` | Карьера | Career | OK | OK | PASS (precheck) |
| 18-22 | Header категория (Интернет) | `child_interface_category_internet` | Безопасность в интернете | Internet Safety | OK | OK | PASS (precheck) |
| 18-22 | Header категория (Фильмы) | `child_interface_category_movies` | Фильмы | Movies | OK | OK | PASS (precheck) |
| 18-22 | Safety tile label (main screen) | `family_category_safety` | БЕЗОПАСНОСТЬ | SAFETY | OK | OK | PASS (precheck) |
| 18-22 | Daily Journey title | `child_daily_journey_title` | Путь на сегодня | Today's Journey | OK | OK | PASS (precheck) |
| 18-22 | Daily Journey step discover/practice/reflect | `child_daily_journey_step_discover` / `...practice` / `...reflect` | Изучить / Тренировка / Итог | Discover / Practice / Reflect | OK | OK | PASS (precheck) |
| 18-22 | Journey v3 title | `child_daily_journey_v3_title` | Маршрут 13–22: автономность и рефлексия | Journey 13–22: Autonomy And Reflection | OK | OK | PASS (precheck) |
| 18-22 | Journey v3 focus explore/build/lead | `child_daily_journey_v3_focus_explore` / `...build` / `...lead` | 3 локализованных фразы | 3 localized phrases | OK | OK | PASS (precheck) |
| 18-22 | Journey v3 reflection prompt/action/done | `child_daily_journey_v3_reflection_prompt` / `...action` / `...done` | 3 локализованных фразы | 3 localized phrases | OK | OK | PASS (precheck) |
| 18-22 | Daily tip | `child_daily_tip_young_adult` | (локализованный текст совета) | (localized tip text) | OK | OK | PASS (precheck) |

---

## Route Nuance (Mandatory QA Notes)

- 7-12 safety tile does not open standard category feed; it opens `ChildSafetyInstructionsModal`.
- 13-17 and 18-22 safety tile route goes to `.securityEducation`.
- Verify localization quality on those two paths separately from standard `navigateToContent`.

## Defect Recording Template

- Screen:
- Age:
- Card:
- Key shown instead of translation:
- App language:
- Expected:
- Actual:
- Repro steps:
- Screenshot:
