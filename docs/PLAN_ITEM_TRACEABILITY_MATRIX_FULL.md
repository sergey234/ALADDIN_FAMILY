# PLAN Item -> Implementation Traceability

Формат строки:
`PLAN_ITEM | category_id | item_id | status | owner | due | gates | wave`

Статусы: `DONE / PARTIAL / TODO`  
Базовые гейты для всех волн: `phase2_category_acceptance_smoke + localization_lint + xcodebuild`  
Для контентной глубины дополнительно: `phase2_content_qa_matrix_smoke`

---

## Для ML-системы: связка этого файла с полной инфраструктурой

Этот документ — **каноническая матрица 275** строк (`PLAN_ITEM | category_id | item_id | status | …`). Он описывает **каталог и план-факт по пунктам**, а не весь narrative реализации.

**Читать вместе с матрицей (полная картина «от начала до конца»):**

| Документ | Зачем |
| --- | --- |
| **`docs/CHILD_CONTENT_INTERFACE_ML_HANDBOOK.md`** | Единый handbook: как связаны планы **178 / 68 / 275**, карта кода, гейты, волны, индекс артефактов. |
| `docs/ML_SYSTEM_TRANSFER_PACKAGE_PHASE2.md` | Точка входа Phase 2 + порядок чтения (обновлён под матрицу 275). |
| `docs/PLAN_ITEM_OPEN_TASKS.md` | Только открытые строки матрицы (`PARTIAL` + `TODO`). |
| `docs/PLAN_ITEM_WAVE_1.md` | Первая волна из открытого списка (10 пунктов). |
| `docs/PHASE2_LIVE_TODO_TRACKER.md`, `docs/CURSOR_CHAT_PENDING_CHECKLIST.md` | Закрытие **68** задач Phase 2 (включая hard exit и SF). |
| `docs/TASK_56_DONE.md` … `docs/TASK_68_DONE.md` | Доказательства по пунктам 56–68. |
| `docs/PHASE2_FINAL_VERIFICATION_RUN.md` | Последний полный прогон гейтов + `xcodebuild`. |
| `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`, `docs/PLAN_174_ML_HANDOFF_FRONTEND.md` | Глобальный клиентский план **178** задач и handoff по закрытым 174. |
| `docs/CHILD_CONTENT_INTERFACE_PLAN_FACT.md` | Краткий план vs факт по детскому UI и контент-пайплайну. |
| `docs/CHILD_CONTENT_PROD_CHECK_AND_ROADMAP.md` | Проверка `/api/content/*` на prod, что обязательно в API, что добавить в план на 100% стыковки. |

**Скрипт проверки формата строк этой матрицы:** `scripts/plan_item_traceability_smoke.py`  
**Полный построчный аудит 275 (дубликаты, сводка по категориям, подсказка где реализовать):** `docs/PLAN_ITEM_275_AUDIT_REPORT.md` — генерировать командой `python3 scripts/plan_item_275_audit.py`  
**Чеклист по возрастам (читаемый Markdown, статусы как task-list):** `docs/PLAN_ITEM_275_BY_AGE_READABLE.md` — `python3 scripts/plan_item_275_age_checklist.py`

---

## 1-6 лет

### Игрушки (`child_interface_category_toys`)
- Интерактивные 3D-игрушки с анимацией | child_interface_category_toys | toys.01 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Звуковые эффекты при взаимодействии | child_interface_category_toys | toys.02 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Цветовые игры (узнай цвет) | child_interface_category_toys | toys.03 | PARTIAL | 1-6 Content Squad | 2026-05-11 | baseline+qa_matrix | W2
- Геометрические фигуры (найди круг, квадрат) | child_interface_category_toys | toys.04 | PARTIAL | 1-6 Content Squad | 2026-05-11 | baseline+qa_matrix | W2
- Животные с звуками | child_interface_category_toys | toys.05 | TODO | 1-6 Content Squad | 2026-05-18 | baseline+qa_matrix | W3
- Транспорт с движением | child_interface_category_toys | toys.06 | TODO | 1-6 Content Squad | 2026-05-18 | baseline+qa_matrix | W3
- Музыкальные инструменты | child_interface_category_toys | toys.07 | TODO | 1-6 Content Squad | 2026-05-25 | baseline+qa_matrix | W4
- Простые пазлы (2-4 элемента) | child_interface_category_toys | toys.08 | TODO | 1-6 Content Squad | 2026-05-25 | baseline+qa_matrix | W4
- Интерактивные книги | child_interface_category_toys | toys.09 | TODO | 1-6 Content Squad | 2026-06-01 | baseline+qa_matrix | W5
- Ролевые игры (кухня, магазин) | child_interface_category_toys | toys.10 | TODO | 1-6 Content Squad | 2026-06-01 | baseline+qa_matrix | W5
- Простые загадки | child_interface_category_toys | toys.11 | TODO | 1-6 Content Squad | 2026-06-08 | baseline+qa_matrix | W6
- Цифры и буквы | child_interface_category_toys | toys.12 | PARTIAL | 1-6 Content Squad | 2026-06-08 | baseline+qa_matrix | W6
- Эмоции и мимика | child_interface_category_toys | toys.13 | TODO | 1-6 Content Squad | 2026-06-15 | baseline+qa_matrix | W7
- Цвета и формы | child_interface_category_toys | toys.14 | PARTIAL | 1-6 Content Squad | 2026-06-15 | baseline+qa_matrix | W7
- Дни недели и времена года | child_interface_category_toys | toys.15 | TODO | 1-6 Content Squad | 2026-06-22 | baseline+qa_matrix | W8

### Рисование (`child_interface_category_drawing`)
- Canvas с пальцевым рисованием | child_interface_category_drawing | drawing.01 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Выбор цветов (палитра) | child_interface_category_drawing | drawing.02 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Разные кисти (толстая, тонкая) | child_interface_category_drawing | drawing.03 | PARTIAL | 1-6 Content Squad | 2026-05-11 | baseline+qa_matrix | W2
- Сохранение рисунков в галерею | child_interface_category_drawing | drawing.04 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Шаблоны для раскрашивания | child_interface_category_drawing | drawing.05 | TODO | 1-6 Content Squad | 2026-05-18 | baseline+qa_matrix | W3
- Геометрические фигуры | child_interface_category_drawing | drawing.06 | PARTIAL | 1-6 Content Squad | 2026-05-18 | baseline+qa_matrix | W3
- Животные и растения | child_interface_category_drawing | drawing.07 | TODO | 1-6 Content Squad | 2026-05-25 | baseline+qa_matrix | W4
- Дом и семья | child_interface_category_drawing | drawing.08 | TODO | 1-6 Content Squad | 2026-06-01 | baseline+qa_matrix | W5
- Транспорт и техника | child_interface_category_drawing | drawing.09 | TODO | 1-6 Content Squad | 2026-06-08 | baseline+qa_matrix | W6
- Абстрактные узоры | child_interface_category_drawing | drawing.10 | TODO | 1-6 Content Squad | 2026-06-15 | baseline+qa_matrix | W7

### Песенки (`child_interface_category_songs`)
- Детские песни с текстом | child_interface_category_songs | songs.01 | PARTIAL | 1-6 Audio Squad | 2026-05-11 | baseline+qa_matrix | W2
- Караоке режим с подсветкой слов | child_interface_category_songs | songs.02 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Мелодии с аккомпанементом | child_interface_category_songs | songs.03 | TODO | 1-6 Audio Squad | 2026-05-18 | baseline+qa_matrix | W3
- Сохранение любимых песен | child_interface_category_songs | songs.04 | TODO | 1-6 Audio Squad | 2026-05-25 | baseline+qa_matrix | W4
- Категории (колыбельные, игровые, обучающие) | child_interface_category_songs | songs.05 | TODO | 1-6 Audio Squad | 2026-05-25 | baseline+qa_matrix | W4
- Песни про цифры | child_interface_category_songs | songs.06 | TODO | 1-6 Audio Squad | 2026-06-01 | baseline+qa_matrix | W5
- Песни про цвета | child_interface_category_songs | songs.07 | TODO | 1-6 Audio Squad | 2026-06-01 | baseline+qa_matrix | W5
- Песни про животных | child_interface_category_songs | songs.08 | TODO | 1-6 Audio Squad | 2026-06-08 | baseline+qa_matrix | W6
- Песни про времена года | child_interface_category_songs | songs.09 | TODO | 1-6 Audio Squad | 2026-06-08 | baseline+qa_matrix | W6
- Песни про дружбу | child_interface_category_songs | songs.10 | TODO | 1-6 Audio Squad | 2026-06-15 | baseline+qa_matrix | W7
- Песни про здоровье | child_interface_category_songs | songs.11 | TODO | 1-6 Audio Squad | 2026-06-15 | baseline+qa_matrix | W7
- Народные песенки | child_interface_category_songs | songs.12 | TODO | 1-6 Audio Squad | 2026-06-22 | baseline+qa_matrix | W8
- Современные детские песни | child_interface_category_songs | songs.13 | TODO | 1-6 Audio Squad | 2026-06-22 | baseline+qa_matrix | W8
- Песни разных стран | child_interface_category_songs | songs.14 | TODO | 1-6 Audio Squad | 2026-06-29 | baseline+qa_matrix | W9
- Ритмичные стишки | child_interface_category_songs | songs.15 | TODO | 1-6 Audio Squad | 2026-06-29 | baseline+qa_matrix | W9

### Сказки (`child_interface_category_stories`)
- Интерактивные сказки с картинками | child_interface_category_stories | stories.01 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Озвучка текста профессиональными актерами | child_interface_category_stories | stories.02 | PARTIAL | 1-6 Narrative Squad | 2026-05-18 | baseline+qa_matrix | W3
- Выбор темпа чтения | child_interface_category_stories | stories.03 | TODO | 1-6 Narrative Squad | 2026-05-25 | baseline+qa_matrix | W4
- Закладки на любимые места | child_interface_category_stories | stories.04 | TODO | 1-6 Narrative Squad | 2026-05-25 | baseline+qa_matrix | W4
- Вопросы после прочтения | child_interface_category_stories | stories.05 | PARTIAL | 1-6 Narrative Squad | 2026-06-01 | baseline+qa_matrix | W5
- Колобок и другие народные сказки | child_interface_category_stories | stories.06 | TODO | 1-6 Narrative Squad | 2026-06-08 | baseline+qa_matrix | W6
- Сказки про животных | child_interface_category_stories | stories.07 | TODO | 1-6 Narrative Squad | 2026-06-08 | baseline+qa_matrix | W6
- Волшебные истории | child_interface_category_stories | stories.08 | TODO | 1-6 Narrative Squad | 2026-06-15 | baseline+qa_matrix | W7
- Сказки разных народов | child_interface_category_stories | stories.09 | TODO | 1-6 Narrative Squad | 2026-06-22 | baseline+qa_matrix | W8
- Современные сказки | child_interface_category_stories | stories.10 | TODO | 1-6 Narrative Squad | 2026-06-22 | baseline+qa_matrix | W8

## 7-12 лет

### Игры (`child_interface_category_games`)
- Математические игры | child_interface_category_games | games.01 | PARTIAL | 7-12 Learning Games Squad | 2026-05-11 | baseline+qa_matrix | W2
- Русский язык | child_interface_category_games | games.02 | PARTIAL | 7-12 Learning Games Squad | 2026-05-11 | baseline+qa_matrix | W2
- Головоломки и логические задачи | child_interface_category_games | games.03 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Викторины по предметам | child_interface_category_games | games.04 | TODO | 7-12 Learning Games Squad | 2026-05-18 | baseline+qa_matrix | W3
- Игры на развитие памяти | child_interface_category_games | games.05 | TODO | 7-12 Learning Games Squad | 2026-05-18 | baseline+qa_matrix | W3
- Скоростные игры | child_interface_category_games | games.06 | TODO | 7-12 Learning Games Squad | 2026-05-25 | baseline+qa_matrix | W4
- Командные игры | child_interface_category_games | games.07 | TODO | 7-12 Learning Games Squad | 2026-05-25 | baseline+qa_matrix | W4
- Стратегические игры | child_interface_category_games | games.08 | TODO | 7-12 Learning Games Squad | 2026-06-01 | baseline+qa_matrix | W5
- Приключенческие квесты | child_interface_category_games | games.09 | PARTIAL | 7-12 Learning Games Squad | 2026-06-01 | baseline+qa_matrix | W5
- Спортивные симуляторы | child_interface_category_games | games.10 | TODO | 7-12 Learning Games Squad | 2026-06-08 | baseline+qa_matrix | W6
- Настольные игры | child_interface_category_games | games.11 | TODO | 7-12 Learning Games Squad | 2026-06-08 | baseline+qa_matrix | W6
- Карточные игры | child_interface_category_games | games.12 | TODO | 7-12 Learning Games Squad | 2026-06-15 | baseline+qa_matrix | W7
- Аркадные игры | child_interface_category_games | games.13 | TODO | 7-12 Learning Games Squad | 2026-06-15 | baseline+qa_matrix | W7
- Платформеры | child_interface_category_games | games.14 | TODO | 7-12 Learning Games Squad | 2026-06-22 | baseline+qa_matrix | W8
- Гонки | child_interface_category_games | games.15 | TODO | 7-12 Learning Games Squad | 2026-06-22 | baseline+qa_matrix | W8
- Строительство и крафтинг | child_interface_category_games | games.16 | TODO | 7-12 Learning Games Squad | 2026-06-29 | baseline+qa_matrix | W9
- Ферма и животные | child_interface_category_games | games.17 | TODO | 7-12 Learning Games Squad | 2026-06-29 | baseline+qa_matrix | W9
- Космос и наука | child_interface_category_games | games.18 | TODO | 7-12 Learning Games Squad | 2026-07-06 | baseline+qa_matrix | W10
- История и география | child_interface_category_games | games.19 | TODO | 7-12 Learning Games Squad | 2026-07-06 | baseline+qa_matrix | W10
- Музыкальные игры | child_interface_category_games | games.20 | TODO | 7-12 Learning Games Squad | 2026-07-13 | baseline+qa_matrix | W11

### Учёба (`child_interface_category_study`)
- Русский язык: чтение, письмо, грамматика | child_interface_category_study | study.01 | PARTIAL | 7-12 Study Squad | 2026-05-18 | baseline+qa_matrix | W3
- Математика: арифметика, геометрия, задачи | child_interface_category_study | study.02 | PARTIAL | 7-12 Study Squad | 2026-05-18 | baseline+qa_matrix | W3
- Окружающий мир | child_interface_category_study | study.03 | PARTIAL | 7-12 Study Squad | 2026-05-25 | baseline+qa_matrix | W4
- История | child_interface_category_study | study.04 | TODO | 7-12 Study Squad | 2026-05-25 | baseline+qa_matrix | W4
- География | child_interface_category_study | study.05 | TODO | 7-12 Study Squad | 2026-06-01 | baseline+qa_matrix | W5
- Биология | child_interface_category_study | study.06 | TODO | 7-12 Study Squad | 2026-06-01 | baseline+qa_matrix | W5
- Физика | child_interface_category_study | study.07 | TODO | 7-12 Study Squad | 2026-06-08 | baseline+qa_matrix | W6
- Химия | child_interface_category_study | study.08 | TODO | 7-12 Study Squad | 2026-06-08 | baseline+qa_matrix | W6
- Литература | child_interface_category_study | study.09 | TODO | 7-12 Study Squad | 2026-06-15 | baseline+qa_matrix | W7
- Искусство | child_interface_category_study | study.10 | TODO | 7-12 Study Squad | 2026-06-15 | baseline+qa_matrix | W7
- Физкультура | child_interface_category_study | study.11 | TODO | 7-12 Study Squad | 2026-06-22 | baseline+qa_matrix | W8
- Труд | child_interface_category_study | study.12 | TODO | 7-12 Study Squad | 2026-06-22 | baseline+qa_matrix | W8
- Обществознание | child_interface_category_study | study.13 | TODO | 7-12 Study Squad | 2026-06-29 | baseline+qa_matrix | W9
- Экология | child_interface_category_study | study.14 | TODO | 7-12 Study Squad | 2026-06-29 | baseline+qa_matrix | W9
- Безопасность: ПДД | child_interface_category_study | study.15 | TODO | 7-12 Study Squad | 2026-07-06 | baseline+qa_matrix | W10
- Здоровье: гигиена, питание | child_interface_category_study | study.16 | TODO | 7-12 Study Squad | 2026-07-06 | baseline+qa_matrix | W10
- Финансовая грамотность | child_interface_category_study | study.17 | TODO | 7-12 Study Squad | 2026-07-13 | baseline+qa_matrix | W11
- Информатика | child_interface_category_study | study.18 | PARTIAL | 7-12 Study Squad | 2026-07-13 | baseline+qa_matrix | W11
- Иностранные языки | child_interface_category_study | study.19 | TODO | 7-12 Study Squad | 2026-07-20 | baseline+qa_matrix | W12
- Творчество | child_interface_category_study | study.20 | TODO | 7-12 Study Squad | 2026-07-20 | baseline+qa_matrix | W12
- Проектная деятельность | child_interface_category_study | study.21 | TODO | 7-12 Study Squad | 2026-07-27 | baseline+qa_matrix | W13
- Исследовательская работа | child_interface_category_study | study.22 | TODO | 7-12 Study Squad | 2026-07-27 | baseline+qa_matrix | W13
- Групповые задания | child_interface_category_study | study.23 | TODO | 7-12 Study Squad | 2026-08-03 | baseline+qa_matrix | W14
- Самостоятельные работы | child_interface_category_study | study.24 | TODO | 7-12 Study Squad | 2026-08-03 | baseline+qa_matrix | W14
- Контрольные работы | child_interface_category_study | study.25 | PARTIAL | 7-12 Study Squad | 2026-08-10 | baseline+qa_matrix | W15
- Тесты и викторины | child_interface_category_study | study.26 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Лабораторные работы | child_interface_category_study | study.27 | TODO | 7-12 Study Squad | 2026-08-10 | baseline+qa_matrix | W15
- Практические задания | child_interface_category_study | study.28 | PARTIAL | 7-12 Study Squad | 2026-08-17 | baseline+qa_matrix | W16
- Творческие проекты | child_interface_category_study | study.29 | TODO | 7-12 Study Squad | 2026-08-17 | baseline+qa_matrix | W16
- Портфолио достижений | child_interface_category_study | study.30 | TODO | 7-12 Study Squad | 2026-08-24 | baseline+qa_matrix | W17

### Безопасность (`child_interface_category_safety`) 7-12
- Правила дорожного движения | child_interface_category_safety | safety.01 | TODO | 7-12 Safety Squad | 2026-05-25 | baseline+qa_matrix | W4
- Безопасность в интернете | child_interface_category_safety | safety.02 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Пожарная безопасность | child_interface_category_safety | safety.03 | TODO | 7-12 Safety Squad | 2026-06-01 | baseline+qa_matrix | W5
- Безопасность на воде | child_interface_category_safety | safety.04 | TODO | 7-12 Safety Squad | 2026-06-01 | baseline+qa_matrix | W5
- Электробезопасность | child_interface_category_safety | safety.05 | TODO | 7-12 Safety Squad | 2026-06-08 | baseline+qa_matrix | W6
- Безопасность в природе | child_interface_category_safety | safety.06 | TODO | 7-12 Safety Squad | 2026-06-08 | baseline+qa_matrix | W6
- Безопасность в школе | child_interface_category_safety | safety.07 | TODO | 7-12 Safety Squad | 2026-06-15 | baseline+qa_matrix | W7
- Безопасность дома | child_interface_category_safety | safety.08 | TODO | 7-12 Safety Squad | 2026-06-15 | baseline+qa_matrix | W7
- Первая медицинская помощь | child_interface_category_safety | safety.09 | TODO | 7-12 Safety Squad | 2026-06-22 | baseline+qa_matrix | W8
- Защита от опасных веществ | child_interface_category_safety | safety.10 | TODO | 7-12 Safety Squad | 2026-06-22 | baseline+qa_matrix | W8
- Поведение в общественных местах | child_interface_category_safety | safety.11 | TODO | 7-12 Safety Squad | 2026-06-29 | baseline+qa_matrix | W9
- Защита от незнакомцев | child_interface_category_safety | safety.12 | PARTIAL | 7-12 Safety Squad | 2026-06-29 | baseline+qa_matrix | W9
- Экстренные службы | child_interface_category_safety | safety.13 | TODO | 7-12 Safety Squad | 2026-07-06 | baseline+qa_matrix | W10
- Правила использования гаджетов | child_interface_category_safety | safety.14 | TODO | 7-12 Safety Squad | 2026-07-06 | baseline+qa_matrix | W10
- Психологическая безопасность | child_interface_category_safety | safety.15 | PARTIAL | 7-12 Safety Squad | 2026-07-13 | baseline+qa_matrix | W11

### Мультфильмы (`child_interface_category_cartoons`)
- Образовательные мультфильмы | child_interface_category_cartoons | cartoons.01 | PARTIAL | 7-12 Media Squad | 2026-05-25 | baseline+qa_matrix | W4
- Мультфильмы про безопасность | child_interface_category_cartoons | cartoons.02 | TODO | 7-12 Media Squad | 2026-06-01 | baseline+qa_matrix | W5
- Мультфильмы про дружбу | child_interface_category_cartoons | cartoons.03 | TODO | 7-12 Media Squad | 2026-06-01 | baseline+qa_matrix | W5
- Мультфильмы про природу | child_interface_category_cartoons | cartoons.04 | TODO | 7-12 Media Squad | 2026-06-08 | baseline+qa_matrix | W6
- Мультфильмы про здоровье | child_interface_category_cartoons | cartoons.05 | TODO | 7-12 Media Squad | 2026-06-08 | baseline+qa_matrix | W6
- Мультфильмы про спорт | child_interface_category_cartoons | cartoons.06 | TODO | 7-12 Media Squad | 2026-06-15 | baseline+qa_matrix | W7
- Мультфильмы про искусство | child_interface_category_cartoons | cartoons.07 | TODO | 7-12 Media Squad | 2026-06-15 | baseline+qa_matrix | W7
- Мультфильмы про науку | child_interface_category_cartoons | cartoons.08 | TODO | 7-12 Media Squad | 2026-06-22 | baseline+qa_matrix | W8
- Мультфильмы про историю | child_interface_category_cartoons | cartoons.09 | TODO | 7-12 Media Squad | 2026-06-22 | baseline+qa_matrix | W8
- Мультфильмы про космос | child_interface_category_cartoons | cartoons.10 | TODO | 7-12 Media Squad | 2026-06-29 | baseline+qa_matrix | W9
- Мультфильмы про животных | child_interface_category_cartoons | cartoons.11 | TODO | 7-12 Media Squad | 2026-06-29 | baseline+qa_matrix | W9
- Мультфильмы про транспорт | child_interface_category_cartoons | cartoons.12 | TODO | 7-12 Media Squad | 2026-07-06 | baseline+qa_matrix | W10
- Мультфильмы про еду | child_interface_category_cartoons | cartoons.13 | TODO | 7-12 Media Squad | 2026-07-06 | baseline+qa_matrix | W10
- Мультфильмы про сон | child_interface_category_cartoons | cartoons.14 | TODO | 7-12 Media Squad | 2026-07-13 | baseline+qa_matrix | W11
- Мультфильмы про эмоции | child_interface_category_cartoons | cartoons.15 | TODO | 7-12 Media Squad | 2026-07-13 | baseline+qa_matrix | W11

### Творчество (`child_interface_category_creativity`)
- Продвинутое рисование | child_interface_category_creativity | creativity.01 | PARTIAL | 7-12 Creativity Squad | 2026-06-01 | baseline+qa_matrix | W5
- Создание комиксов | child_interface_category_creativity | creativity.02 | TODO | 7-12 Creativity Squad | 2026-06-08 | baseline+qa_matrix | W6
- Дизайн и графика | child_interface_category_creativity | creativity.03 | TODO | 7-12 Creativity Squad | 2026-06-08 | baseline+qa_matrix | W6
- Фотография и обработка | child_interface_category_creativity | creativity.04 | TODO | 7-12 Creativity Squad | 2026-06-15 | baseline+qa_matrix | W7
- Видео монтаж | child_interface_category_creativity | creativity.05 | TODO | 7-12 Creativity Squad | 2026-06-15 | baseline+qa_matrix | W7
- Музыкальное творчество | child_interface_category_creativity | creativity.06 | TODO | 7-12 Creativity Squad | 2026-06-22 | baseline+qa_matrix | W8
- Литературное творчество | child_interface_category_creativity | creativity.07 | TODO | 7-12 Creativity Squad | 2026-06-22 | baseline+qa_matrix | W8
- Театр и импровизация | child_interface_category_creativity | creativity.08 | TODO | 7-12 Creativity Squad | 2026-06-29 | baseline+qa_matrix | W9
- Ручное творчество | child_interface_category_creativity | creativity.09 | TODO | 7-12 Creativity Squad | 2026-06-29 | baseline+qa_matrix | W9
- Цифровое искусство | child_interface_category_creativity | creativity.10 | TODO | 7-12 Creativity Squad | 2026-07-06 | baseline+qa_matrix | W10

## 13-17 лет

### Безопасность (`child_interface_category_safety`) teen-track
- Продвинутая кибербезопасность | child_interface_category_safety | teen_safety.01 | TODO | Teen Safety Squad | 2026-07-13 | baseline+qa_matrix | W11
- Защита персональных данных | child_interface_category_safety | teen_safety.02 | PARTIAL | Teen Safety Squad | 2026-07-13 | baseline+qa_matrix | W11
- Безопасность в соцсетях | child_interface_category_safety | teen_safety.03 | PARTIAL | Teen Safety Squad | 2026-07-20 | baseline+qa_matrix | W12
- Финансовая безопасность | child_interface_category_safety | teen_safety.04 | TODO | Teen Safety Squad | 2026-07-20 | baseline+qa_matrix | W12
- Безопасность в отношениях | child_interface_category_safety | teen_safety.05 | TODO | Teen Safety Squad | 2026-07-27 | baseline+qa_matrix | W13
- Защита от манипуляций | child_interface_category_safety | teen_safety.06 | TODO | Teen Safety Squad | 2026-07-27 | baseline+qa_matrix | W13
- Психологическая безопасность (13–17) | child_interface_category_safety | teen_safety.07 | PARTIAL | Teen Safety Squad | 2026-08-03 | baseline+qa_matrix | W14
- Физическая безопасность | child_interface_category_safety | teen_safety.08 | TODO | Teen Safety Squad | 2026-08-03 | baseline+qa_matrix | W14
- Безопасность в сети | child_interface_category_safety | teen_safety.09 | PARTIAL | Teen Safety Squad | 2026-08-10 | baseline+qa_matrix | W15
- Защита от вредного контента | child_interface_category_safety | teen_safety.10 | TODO | Teen Safety Squad | 2026-08-10 | baseline+qa_matrix | W15
- Безопасность при покупках онлайн | child_interface_category_safety | teen_safety.11 | TODO | Teen Safety Squad | 2026-08-17 | baseline+qa_matrix | W16
- Защита от мошенничества | child_interface_category_safety | teen_safety.12 | PARTIAL | Teen Safety Squad | 2026-08-17 | baseline+qa_matrix | W16
- Безопасность в путешествиях | child_interface_category_safety | teen_safety.13 | TODO | Teen Safety Squad | 2026-08-24 | baseline+qa_matrix | W17
- Экстренная подготовка | child_interface_category_safety | teen_safety.14 | TODO | Teen Safety Squad | 2026-08-24 | baseline+qa_matrix | W17
- Самозащита | child_interface_category_safety | teen_safety.15 | TODO | Teen Safety Squad | 2026-08-31 | baseline+qa_matrix | W18

### Программирование (`child_interface_category_programming`)
- Основы Swift для iOS | child_interface_category_programming | programming.01 | PARTIAL | Teen Coding Squad | 2026-07-13 | baseline+qa_matrix | W11
- Визуальное программирование | child_interface_category_programming | programming.02 | PARTIAL | Teen Coding Squad | 2026-07-13 | baseline+qa_matrix | W11
- Создание простых приложений | child_interface_category_programming | programming.03 | TODO | Teen Coding Squad | 2026-07-20 | baseline+qa_matrix | W12
- Работа с данными | child_interface_category_programming | programming.04 | TODO | Teen Coding Squad | 2026-07-20 | baseline+qa_matrix | W12
- Интерфейсы и UX | child_interface_category_programming | programming.05 | TODO | Teen Coding Squad | 2026-07-27 | baseline+qa_matrix | W13
- Алгоритмы и логика | child_interface_category_programming | programming.06 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Отладка и тестирование | child_interface_category_programming | programming.07 | PARTIAL | Teen Coding Squad | 2026-07-27 | baseline+qa_matrix | W13
- Версии и развертывание | child_interface_category_programming | programming.08 | TODO | Teen Coding Squad | 2026-08-03 | baseline+qa_matrix | W14
- Командная разработка | child_interface_category_programming | programming.09 | TODO | Teen Coding Squad | 2026-08-03 | baseline+qa_matrix | W14
- Проектное управление | child_interface_category_programming | programming.10 | TODO | Teen Coding Squad | 2026-08-10 | baseline+qa_matrix | W15
- Этика программирования | child_interface_category_programming | programming.11 | TODO | Teen Coding Squad | 2026-08-10 | baseline+qa_matrix | W15
- Будущее технологий | child_interface_category_programming | programming.12 | TODO | Teen Coding Squad | 2026-08-17 | baseline+qa_matrix | W16
- Кибербезопасность в разработке | child_interface_category_programming | programming.13 | TODO | Teen Coding Squad | 2026-08-17 | baseline+qa_matrix | W16
- Мобильная разработка | child_interface_category_programming | programming.14 | PARTIAL | Teen Coding Squad | 2026-08-24 | baseline+qa_matrix | W17
- Веб-разработка | child_interface_category_programming | programming.15 | TODO | Teen Coding Squad | 2026-08-24 | baseline+qa_matrix | W17

### Социальные сети (`child_interface_category_social`)
- Безопасность в соцсетях | child_interface_category_social | social.01 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Управление приватностью | child_interface_category_social | social.02 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Цифровой след | child_interface_category_social | social.03 | PARTIAL | Teen Social Squad | 2026-07-20 | baseline+qa_matrix | W12
- Онлайн репутация | child_interface_category_social | social.04 | TODO | Teen Social Squad | 2026-07-20 | baseline+qa_matrix | W12
- Кибербуллинг и травля | child_interface_category_social | social.05 | PARTIAL | Teen Social Squad | 2026-07-27 | baseline+qa_matrix | W13
- Фейковые новости | child_interface_category_social | social.06 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Зависимость от соцсетей | child_interface_category_social | social.07 | TODO | Teen Social Squad | 2026-07-27 | baseline+qa_matrix | W13
- Баланс онлайн/оффлайн | child_interface_category_social | social.08 | PARTIAL | Teen Social Squad | 2026-08-03 | baseline+qa_matrix | W14
- Создание контента | child_interface_category_social | social.09 | TODO | Teen Social Squad | 2026-08-03 | baseline+qa_matrix | W14
- Влияние на самооценку | child_interface_category_social | social.10 | TODO | Teen Social Squad | 2026-08-10 | baseline+qa_matrix | W15
- Группы и сообщества | child_interface_category_social | social.11 | TODO | Teen Social Squad | 2026-08-10 | baseline+qa_matrix | W15
- Профессиональные сети | child_interface_category_social | social.12 | TODO | Teen Social Squad | 2026-08-17 | baseline+qa_matrix | W16
- Нетворкинг | child_interface_category_social | social.13 | TODO | Teen Social Squad | 2026-08-17 | baseline+qa_matrix | W16
- Брендинг в соцсетях | child_interface_category_social | social.14 | TODO | Teen Social Squad | 2026-08-24 | baseline+qa_matrix | W17
- Этика в цифровом мире | child_interface_category_social | social.15 | PARTIAL | Teen Social Squad | 2026-08-24 | baseline+qa_matrix | W17

### Музыка (`child_interface_category_music`)
- Теория музыки | child_interface_category_music | music.01 | PARTIAL | Teen Music Squad | 2026-07-20 | baseline+qa_matrix | W12
- Создание музыки | child_interface_category_music | music.02 | TODO | Teen Music Squad | 2026-07-20 | baseline+qa_matrix | W12
- Музыкальные инструменты | child_interface_category_music | music.03 | TODO | Teen Music Squad | 2026-07-27 | baseline+qa_matrix | W13
- Вокал и пение | child_interface_category_music | music.04 | PARTIAL | Teen Music Squad | 2026-07-27 | baseline+qa_matrix | W13
- Музыкальные жанры | child_interface_category_music | music.05 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- История музыки | child_interface_category_music | music.06 | TODO | Teen Music Squad | 2026-08-03 | baseline+qa_matrix | W14
- Музыкальная психология | child_interface_category_music | music.07 | TODO | Teen Music Squad | 2026-08-03 | baseline+qa_matrix | W14
- Музыка и эмоции | child_interface_category_music | music.08 | PARTIAL | Teen Music Squad | 2026-08-10 | baseline+qa_matrix | W15
- Музыка для концентрации | child_interface_category_music | music.09 | TODO | Teen Music Squad | 2026-08-10 | baseline+qa_matrix | W15
- Музыка для релаксации | child_interface_category_music | music.10 | TODO | Teen Music Squad | 2026-08-17 | baseline+qa_matrix | W16
- Саундтреки к фильмам | child_interface_category_music | music.11 | TODO | Teen Music Squad | 2026-08-17 | baseline+qa_matrix | W16
- Музыка разных культур | child_interface_category_music | music.12 | TODO | Teen Music Squad | 2026-08-24 | baseline+qa_matrix | W17
- Современная музыка | child_interface_category_music | music.13 | TODO | Teen Music Squad | 2026-08-24 | baseline+qa_matrix | W17
- Классическая музыка | child_interface_category_music | music.14 | TODO | Teen Music Squad | 2026-08-31 | baseline+qa_matrix | W18
- Экспериментальная музыка | child_interface_category_music | music.15 | TODO | Teen Music Squad | 2026-08-31 | baseline+qa_matrix | W18

### Видео (`child_interface_category_video`)
- Основы видеосъемки | child_interface_category_video | video.01 | TODO | Teen Media Squad | 2026-07-27 | baseline+qa_matrix | W13
- Монтаж видео | child_interface_category_video | video.02 | TODO | Teen Media Squad | 2026-07-27 | baseline+qa_matrix | W13
- Создание контента | child_interface_category_video | video.03 | TODO | Teen Media Squad | 2026-08-03 | baseline+qa_matrix | W14
- Видео редактирование | child_interface_category_video | video.04 | TODO | Teen Media Squad | 2026-08-03 | baseline+qa_matrix | W14
- Спецэффекты | child_interface_category_video | video.05 | TODO | Teen Media Squad | 2026-08-10 | baseline+qa_matrix | W15
- Цветокоррекция | child_interface_category_video | video.06 | TODO | Teen Media Squad | 2026-08-10 | baseline+qa_matrix | W15
- Звук в видео | child_interface_category_video | video.07 | TODO | Teen Media Squad | 2026-08-17 | baseline+qa_matrix | W16
- Анимация в видео | child_interface_category_video | video.08 | TODO | Teen Media Squad | 2026-08-17 | baseline+qa_matrix | W16
- Видео для соцсетей | child_interface_category_video | video.09 | TODO | Teen Media Squad | 2026-08-24 | baseline+qa_matrix | W17
- Документальное видео | child_interface_category_video | video.10 | TODO | Teen Media Squad | 2026-08-24 | baseline+qa_matrix | W17
- Музыкальные клипы | child_interface_category_video | video.11 | TODO | Teen Media Squad | 2026-08-31 | baseline+qa_matrix | W18
- Рекламные видео | child_interface_category_video | video.12 | TODO | Teen Media Squad | 2026-08-31 | baseline+qa_matrix | W18
- Обучающие видео | child_interface_category_video | video.13 | PARTIAL | Teen Media Squad | 2026-09-07 | baseline+qa_matrix | W19
- Vlogging | child_interface_category_video | video.14 | TODO | Teen Media Squad | 2026-09-07 | baseline+qa_matrix | W19
- Стриминг | child_interface_category_video | video.15 | TODO | Teen Media Squad | 2026-09-14 | baseline+qa_matrix | W20

## 18-22 лет

### Образование (`child_interface_category_education`)
- Высшее образование | child_interface_category_education | education.01 | PARTIAL | Young Adult Education Squad | 2026-08-03 | baseline+qa_matrix | W14
- Выбор специальности | child_interface_category_education | education.02 | PARTIAL | Young Adult Education Squad | 2026-08-03 | baseline+qa_matrix | W14
- Онлайн обучение | child_interface_category_education | education.03 | TODO | Young Adult Education Squad | 2026-08-10 | baseline+qa_matrix | W15
- Самообразование | child_interface_category_education | education.04 | DONE | Child Core UX Squad | 2026-04-27 | baseline | W1
- Сертификаты и дипломы | child_interface_category_education | education.05 | TODO | Young Adult Education Squad | 2026-08-10 | baseline+qa_matrix | W15
- Международное образование | child_interface_category_education | education.06 | TODO | Young Adult Education Squad | 2026-08-17 | baseline+qa_matrix | W16
- Дистанционное обучение | child_interface_category_education | education.07 | TODO | Young Adult Education Squad | 2026-08-17 | baseline+qa_matrix | W16
- Профессиональная переподготовка | child_interface_category_education | education.08 | TODO | Young Adult Education Squad | 2026-08-24 | baseline+qa_matrix | W17
- Повышение квалификации | child_interface_category_education | education.09 | TODO | Young Adult Education Squad | 2026-08-24 | baseline+qa_matrix | W17
- Научная деятельность | child_interface_category_education | education.10 | TODO | Young Adult Education Squad | 2026-08-31 | baseline+qa_matrix | W18
- Исследовательская работа | child_interface_category_education | education.11 | TODO | Young Adult Education Squad | 2026-08-31 | baseline+qa_matrix | W18
- Академическое письмо | child_interface_category_education | education.12 | TODO | Young Adult Education Squad | 2026-09-07 | baseline+qa_matrix | W19
- Презентационные навыки | child_interface_category_education | education.13 | TODO | Young Adult Education Squad | 2026-09-07 | baseline+qa_matrix | W19
- Проектная деятельность | child_interface_category_education | education.14 | PARTIAL | Young Adult Education Squad | 2026-09-14 | baseline+qa_matrix | W20
- Международные программы | child_interface_category_education | education.15 | TODO | Young Adult Education Squad | 2026-09-14 | baseline+qa_matrix | W20

### Карьера (`child_interface_category_career`)
- Поиск работы | child_interface_category_career | career.01 | PARTIAL | Young Adult Career Squad | 2026-08-10 | baseline+qa_matrix | W15
- Составление резюме | child_interface_category_career | career.02 | TODO | Young Adult Career Squad | 2026-08-10 | baseline+qa_matrix | W15
- Собеседования | child_interface_category_career | career.03 | TODO | Young Adult Career Squad | 2026-08-17 | baseline+qa_matrix | W16
- Карьерный рост | child_interface_category_career | career.04 | PARTIAL | Young Adult Career Squad | 2026-08-17 | baseline+qa_matrix | W16
- Профессиональное развитие | child_interface_category_career | career.05 | TODO | Young Adult Career Squad | 2026-08-24 | baseline+qa_matrix | W17
- Нетворкинг | child_interface_category_career | career.06 | TODO | Young Adult Career Squad | 2026-08-24 | baseline+qa_matrix | W17
- Лидерские навыки | child_interface_category_career | career.07 | TODO | Young Adult Career Squad | 2026-08-31 | baseline+qa_matrix | W18
- Командная работа | child_interface_category_career | career.08 | TODO | Young Adult Career Squad | 2026-08-31 | baseline+qa_matrix | W18
- Управление временем | child_interface_category_career | career.09 | TODO | Young Adult Career Squad | 2026-09-07 | baseline+qa_matrix | W19
- Финансовая грамотность | child_interface_category_career | career.10 | PARTIAL | Young Adult Career Squad | 2026-09-07 | baseline+qa_matrix | W19
- Предпринимательство | child_interface_category_career | career.11 | TODO | Young Adult Career Squad | 2026-09-14 | baseline+qa_matrix | W20
- Фриланс | child_interface_category_career | career.12 | TODO | Young Adult Career Squad | 2026-09-14 | baseline+qa_matrix | W20
- Карьерные изменения | child_interface_category_career | career.13 | TODO | Young Adult Career Squad | 2026-09-21 | baseline+qa_matrix | W21
- Баланс работы и жизни | child_interface_category_career | career.14 | TODO | Young Adult Career Squad | 2026-09-21 | baseline+qa_matrix | W21
- Профессиональная этика | child_interface_category_career | career.15 | TODO | Young Adult Career Squad | 2026-09-28 | baseline+qa_matrix | W22

### Безопасность в интернете (`child_interface_category_internet`)
- Продвинутая кибербезопасность | child_interface_category_internet | internet.01 | TODO | Young Adult Security Squad | 2026-08-17 | baseline+qa_matrix | W16
- Защита персональных данных | child_interface_category_internet | internet.02 | PARTIAL | Young Adult Security Squad | 2026-08-17 | baseline+qa_matrix | W16
- Безопасность платежей | child_interface_category_internet | internet.03 | TODO | Young Adult Security Squad | 2026-08-24 | baseline+qa_matrix | W17
- Защита от хакеров | child_interface_category_internet | internet.04 | TODO | Young Adult Security Squad | 2026-08-24 | baseline+qa_matrix | W17
- Безопасность в облаке | child_interface_category_internet | internet.05 | TODO | Young Adult Security Squad | 2026-08-31 | baseline+qa_matrix | W18
- Защита устройств | child_interface_category_internet | internet.06 | TODO | Young Adult Security Squad | 2026-08-31 | baseline+qa_matrix | W18
- Безопасность в соцсетях | child_interface_category_internet | internet.07 | PARTIAL | Young Adult Security Squad | 2026-09-07 | baseline+qa_matrix | W19
- Защита от фишинга | child_interface_category_internet | internet.08 | TODO | Young Adult Security Squad | 2026-09-07 | baseline+qa_matrix | W19
- Безопасность email | child_interface_category_internet | internet.09 | TODO | Young Adult Security Squad | 2026-09-14 | baseline+qa_matrix | W20
- Защита от вирусов | child_interface_category_internet | internet.10 | TODO | Young Adult Security Squad | 2026-09-14 | baseline+qa_matrix | W20
- Безопасность Wi-Fi | child_interface_category_internet | internet.11 | TODO | Young Adult Security Squad | 2026-09-21 | baseline+qa_matrix | W21
- Защита от мошенничества | child_interface_category_internet | internet.12 | PARTIAL | Young Adult Security Squad | 2026-09-21 | baseline+qa_matrix | W21
- Безопасность в путешествиях | child_interface_category_internet | internet.13 | TODO | Young Adult Security Squad | 2026-09-28 | baseline+qa_matrix | W22
- Корпоративная безопасность | child_interface_category_internet | internet.14 | TODO | Young Adult Security Squad | 2026-09-28 | baseline+qa_matrix | W22
- Правовые аспекты | child_interface_category_internet | internet.15 | TODO | Young Adult Security Squad | 2026-10-05 | baseline+qa_matrix | W23

### Фильмы (`child_interface_category_movies`)
- Классика кино | child_interface_category_movies | movies.01 | TODO | Young Adult Media Squad | 2026-08-24 | baseline+qa_matrix | W17
- Современное кино | child_interface_category_movies | movies.02 | TODO | Young Adult Media Squad | 2026-08-24 | baseline+qa_matrix | W17
- Фильмы по жанрам | child_interface_category_movies | movies.03 | TODO | Young Adult Media Squad | 2026-08-31 | baseline+qa_matrix | W18
- Киноискусство | child_interface_category_movies | movies.04 | TODO | Young Adult Media Squad | 2026-08-31 | baseline+qa_matrix | W18
- Фильмография режиссеров | child_interface_category_movies | movies.05 | TODO | Young Adult Media Squad | 2026-09-07 | baseline+qa_matrix | W19
- Актерское мастерство | child_interface_category_movies | movies.06 | TODO | Young Adult Media Squad | 2026-09-07 | baseline+qa_matrix | W19
- Кинематография | child_interface_category_movies | movies.07 | TODO | Young Adult Media Squad | 2026-09-14 | baseline+qa_matrix | W20
- Сценарное мастерство | child_interface_category_movies | movies.08 | TODO | Young Adult Media Squad | 2026-09-14 | baseline+qa_matrix | W20
- Продюсирование | child_interface_category_movies | movies.09 | TODO | Young Adult Media Squad | 2026-09-21 | baseline+qa_matrix | W21
- Кино критика | child_interface_category_movies | movies.10 | TODO | Young Adult Media Squad | 2026-09-21 | baseline+qa_matrix | W21
- Документальное кино | child_interface_category_movies | movies.11 | TODO | Young Adult Media Squad | 2026-09-28 | baseline+qa_matrix | W22
- Анимационное кино | child_interface_category_movies | movies.12 | TODO | Young Adult Media Squad | 2026-09-28 | baseline+qa_matrix | W22
- Короткометражки | child_interface_category_movies | movies.13 | TODO | Young Adult Media Squad | 2026-10-05 | baseline+qa_matrix | W23
- Кинофестивали | child_interface_category_movies | movies.14 | TODO | Young Adult Media Squad | 2026-10-05 | baseline+qa_matrix | W23
- Международное кино | child_interface_category_movies | movies.15 | TODO | Young Adult Media Squad | 2026-10-12 | baseline+qa_matrix | W24

## Notes
- `DONE`: подтверждено кодом модулей и/или seed-контентом.
- `PARTIAL`: есть движок/каркас, но не закрыт полный тематический/объемный контент.
- `TODO`: отсутствует реализованный item-level контент или нет подтвержденного UX flow.
