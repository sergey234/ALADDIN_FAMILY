# Порядок работ по матрице 275: сверка, волны, гейты, 100%

**Назначение:** чтобы команда **постоянно** сверялась с одним каноном и не теряла пункты из виду. Читать **вместе** с `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`.

**Редакция:** 2026-04-28

## Статус закрытия матрицы 275 (финал)

- `DONE: 275 / PARTIAL: 0 / TODO: 0` — завершено на **100%**.
- Финальные гейты прогнаны повторно и зафиксированы в отчётах:
  - `scripts/plan_item_traceability_smoke.py`
  - `scripts/plan_item_275_audit.py`
  - `scripts/localization_lint.py`
  - `scripts/child_localization_gate.py`
  - `scripts/phase2_content_qa_matrix_smoke.py`
  - `scripts/generate_plan_item_275_mirror.py`
  - `scripts/plan_item_275_age_checklist.py`

---

## 1) Канон и чек-листы в чате

- **Единственный источник правды по перечню и статусам:** `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` (строка = `PLAN_ITEM | category_id | item_id | status | …`).
- Любой «чек-лист в чате / таблица в Notion» — **копия**; при расхождении **правьте сначала матрицу в `docs/`**, потом остальное.
- **Смысл + `item_id`:** одна идея должна иметь **тот же** `item_id` (например `toys.03`). Если формулировка текста разошлась, **подтяните формулировку в матрице** под продукт — не плодите второй «канон».

---

## 2) Практичный ритм (не забывать)

1. **Сверка строки** — каждая рабочая тема **сопоставлена** со строкой матрицы (тот же `item_id` и смысл). Сомнения → открыть матрицу и найти `category_id` + `item_id`.
2. **Волны** — не «все 275 сразу», а **пачки** (например `docs/PLAN_ITEM_WAVE_1.md`: 10 открытых `PARTIAL`/`TODO`). Следующая волна — после закрытия или пересреза по договорённости.
3. **На каждую волну (Definition of Done):**
   - реализация в коде/контенте;
   - **обновление статуса** соответствующих строк в матрице (`DONE` / остаётся `PARTIAL` с обоснованием);
   - **RU + EN** для пользовательских строк по `LOCALIZATION_*` и `localization_lint` там, где требуется;
   - **гейты** из шапки матрицы / волны: как минимум `plan_item_traceability_smoke.py`, `localization_lint.py`, `xcodebuild`; для глубины контента — `phase2_content_qa_matrix_smoke.py` и др. по волне.
   - **обязательный child-i18n gate после каждого пакета 5/5:** `python3 scripts/child_localization_gate.py` (проверяет, что все `child_*` ключи, используемые в базовых экранах детского интерфейса, резолвятся в RU+EN через `LocalizationManager` и/или `Localizable.strings`).
4. **100% по этому плану контента** — только когда **все 275** строк = `DONE` (или осознанно `DEFER` вынесен **в тот же репо** с датой/причиной, если введёте такой статус; иначе «вечный TODO» = не 100%).

**После правок матрицы (массово):**  
`python3 scripts/plan_item_traceability_smoke.py`  
`python3 scripts/plan_item_275_audit.py` (и при необходимости `plan_item_275_age_checklist.py`)  
`python3 scripts/generate_plan_item_275_mirror.py` — если пользуетесь in-app **DEBUG**-зеркалом каталога.

**Быстрый набор гейтов после каждого пакета 5/5 (рекомендуемый минимум):**

`python3 scripts/plan_item_traceability_smoke.py`  
`python3 scripts/plan_item_275_audit.py`  
`python3 scripts/localization_lint.py`  
`python3 scripts/child_localization_gate.py`  
`python3 scripts/phase2_content_qa_matrix_smoke.py`  
`python3 scripts/generate_plan_item_275_mirror.py`  
`python3 scripts/plan_item_275_age_checklist.py`

---

## 3) Сверка «ваш чек-лист ↔ матрица» (по секциям, количество строк)

Пересчитано по `PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` (секции `## N-M лет` + `### Категория`). **Суммы совпадают** с детализацией 15+10+15+10 / 20+30+15+15+10 / 5×15 / 4×15.

| Возраст | Категория (логическое имя) | `category_id` (хвост) | Строк в матрице |
|--------|----------------------------|----------------------|-----------------|
| 1–6 | Игрушки | `…_toys` | 15 |
| 1–6 | Рисование | `…_drawing` | 10 |
| 1–6 | Песенки | `…_songs` | 15 |
| 1–6 | Сказки | `…_stories` | 10 |
| | **Итого 1–6** | | **50** |
| 7–12 | Игры | `…_games` | 20 |
| 7–12 | Учёба | `…_study` | 30 |
| 7–12 | Безопасность | `…_safety` | 15 |
| 7–12 | Мультфильмы | `…_cartoons` | 15 |
| 7–12 | Творчество | `…_creativity` | 10 |
| | **Итого 7–12** | | **90** |
| 13–17 | Безопасность | `…_safety` | 15 |
| 13–17 | Программирование | `…_programming` | 15 |
| 13–17 | Соцсети | `…_social` | 15 |
| 13–17 | Музыка | `…_music` | 15 |
| 13–17 | Видео | `…_video` | 15 |
| | **Итого 13–17** | | **75** |
| 18–22 | Образование | `…_education` | 15 |
| 18–22 | Карьера | `…_career` | 15 |
| 18–22 | Безопасность в интернете | `…_internet` | 15 |
| 18–22 | Фильмы | `…_movies` | 15 |
| | **Итого 18–22** | | **60** |
| | **Всего** | | **275** |

Полные `category_id` в матрице начинаются с `child_interface_category_` (например `child_interface_category_toys`).

---

## 4) Напоминание про локализацию (это **не** один «файл переводов»)

**Переводы в бандле:** `Resources/Localization/ru.lproj/Localizable.strings` и `en.lproj/Localizable.strings` (для `NSLocalizedString` и ключа, если **нигде** нет в `LocalizationManager`). **Без дублей:** одна и та же пара **ключ → тот же RU+EN** не ведётся **одновременно** и в `LocalizationManager.swift`, и в `Localizable.strings` — выбирается **один** канал истины для ключа, второй **не** копирует ту же формулировку (см. существующие ключи: иначе расходятся версии при правках).  
Для большого объёма `localized(_:)` **по умолчанию** — новые ключи 275-интерфейса в **`.russian` / `.english`** внутри `LocalizationManager` (и при чистовом `Localizable` — только по явному решению/миграции, а не дублированием).  

Отдельного «одного .md, куда пишем все 275» в репо **нет** и не нужен: в markdown матрица — **каталожный RU** как план, не runtime-ключи.

**Правила и соглашения (читать при любой волне с UI-строками):**

| Документ | Зачем |
| --- | --- |
| `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md` | RU+EN в одном изменении, без «голого» UI-текста в Swift; **§2a** — один канал на ключ: не дубли `LocalizationManager` + `Localizable.strings`. |
| `docs/LOCALIZATION_PR_CHECKLIST.md` | Проверка PR перед мержем (пары ключей, дубликаты, пропуски). |
| `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md` | Стабильные `child.*` / `common.*` / домены — как называть новые ключи. |

**Контент 275 (заголовки/описания карточек):** как только пункт перестаёт быть заглушкой, тексты идут либо через **ключи** по стандарту выше, либо через **манифест/API** (мультиязычные поля) — см. `docs/CHILD_CONTENT_PROD_CHECK_AND_ROADMAP.md` (раздел про i18n контент-потока; перекрёстно с `docs/PLAN_ITEM_275_AUDIT_REPORT.md` §1a).

---

## 5) Где ещё указана связка

- `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` — шапка и ссылка сюда.
- `docs/ML_SYSTEM_TRANSFER_PACKAGE_PHASE2.md` — порядок чтения.
- `docs/CHILD_CONTENT_INTERFACE_ML_HANDBOOK.md` — полный контекст 178 / 68 / 275.
