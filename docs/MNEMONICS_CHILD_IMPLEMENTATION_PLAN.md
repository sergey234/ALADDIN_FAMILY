# ALADDIN Mnemo Academy — мастер-план (v2.2)

Updated: 2026-06-06  
Версия: **v2.3** — брендинг «Академия памяти» + v2 MVP + v3 Course.  
**Синхронизация для ML:** `docs/MNEMO_PROJECT_SYNC.md` (111/119, Phase C: 8 задач)  
Scope: **100% мнемо-образование** в игровой форме, **без новых блоков** на главном экране.  
Цель v3: ребёнок растёт от 4 до 22 лет как «ученик памяти» — не разовый продукт, а **курс на 5–8 лет**.

---

## S) ПОЛИТИКА ПОЛНОЙ ЗАМЕНЫ (обязательно для всех ML-агентов)

> **Same ID, new soul** — `categoryId` и `item.id` не меняем; UX, тексты и игровая логика в мнемо-блоках **полностью заменяются**.

### S.1 Мнемо-категории — 100% замена

| Возраст | Категории | Что удаляем | Что вставляем |
|---------|-----------|-------------|---------------|
| 1–6 | `songs` | Старый greeting, «просто караоке» | 4 фазы + guided recall + SRS + мнемо-треки |
| 7–12 | `games`, `study`, `cartoons` | Daily journey, старые уроки 3стр, games.05 цифры | Mnemo Academy UI, 4 фазы study, palace drill |
| 13–17 | `music`, `video` | Старые drills без recall | rhythm-code / frame-peg + recall |
| 18–22 | `movies`, `education` | Старые milestones без мнемо | plot-link / SMART acronym + recall |

### S.2 В мнемо-каталоге заменяем полностью

- [x] Лейблы кнопок → `child_mnemo_label_*` (Batch 1)
- [x] Заголовок каталога + subtitle (Batch 1)
- [x] Greeting → `child_mnemo_catalog_greeting_*` (Batch 1)
- [x] Daily journey / school teen cards → `mnemoSkillLevelCard` + `mnemoAcademyBanner` (Batch 1)
- [x] Experience engines — Batch 3–6 ✅
- [x] Все `study.*` page_2 + тесты — Batch 4 ✅
- [x] Старые `child_game_greeting`, `child_study_welcome` в мнемо-потоке **не используются** ✅

### S.3 Не заменяем

toys, drawing, stories, safety, programming, social, creativity, career, internet — без изменений.

### S.4 Статус реализации (live)

| Batch | Статус |
|-------|--------|
| 0 Foundation | ✅ |
| 1 UI Labels | 🔄 IN PROGRESS (код залит, gate pending) |
| 2 MnemoCore | 🔄 IN PROGRESS (файлы есть, wiring/tests pending) |
| 3–8 v2 MVP | ⏳ |
| 9–14 v3 Course | ⏳ (план v2.2, см. §U–§Y) |

### S.5 Curriculum Spine Policy (v2.2 — обязательно для v3)

> **v2 = продукт первого года. v3 = курс на несколько лет.** Curriculum Spine — невидимый слой поверх Batch 1–8.

| Правило | Деталь |
|---------|--------|
| **Unlock семестра** | Семестр N+1 открывается при mastery ≥ **70%** техник семестра N |
| **Cross-age journey** | Остановки растут: **4** (kids) → **12** (school) → **20** (teen) → **40** (young adult) |
| **Комнатная модель** | `study.01` = stop 1, `study.02` = stop 2 … **не hash** — предмет = комната дворца |
| **3R (Россия)** | **R**hyme → **R**oad (дорожка) → **R**egister (таблица) — строгая последовательность |
| **5L (Longitudinal)** | Level 0 Pre (1–4) → 1 Found (5–7) → 2 Build (8–10) → 3 Apply (11–14) → 4 Master (15–17) → 5 Meta (18–22) |
| **Частота** | Целевая нагрузка: **20 мин × 4 раза/нед** (AMAkids); push «Сегодня повтори: N» |
| **Co-create** | Пиктограмму рисует ребёнок (Беззубикова) — сильнее готовых эмодзи ×1.5–2 |
| **Без leaderboard** | Только **личный рекорд** и personal best championship (ALADDIN safety) |

---

## A) Было ли v1 «лучшим»? — Нет. v2 — целевая модель.

| Критерий | v1 (предыдущий план) | v2 (идеал) |
|----------|----------------------|------------|
| Научная база | Упоминание spaced repetition | **AIM + 4D** (см. ниже), Karpicke, Paivio, Putnam 2015 |
| Российская школа | Общие «образы» | **мнемодорожка, мнемоквадрат, мнемофразы** (Беззубикова, «Запоминай-ка») |
| Мировая школа | games.05 Simon | **Journey Method** (O'Brien, Junior Memory Championship) |
| Коммерческий опыт | — | **Memorika AMAkids** 3 уровня, 11 методов, 12 занятий |
| Интервалы | Текст «1-3-7» | **`MnemonicSRSStore`** Leitner 1-3-7-14-30 в коде |
| Урок | 3 страницы + тест | **4 фазы**: Образ → Якорь → Вспомни → Награда |
| Прогресс | Единороги | Уровни **Ученик → Мастер → Чемпион** + 🦄 |
| 1–6 лет | Только песни | Dual coding: **рифма + картинка + guided recall** (Karpicke: с подсказкой) |
| 100% покрытие | Частичное | **10 техник × 4 возраста** (матрица §F) |

---

## B) Метод 6 шляп — полный разбор

### 🤍 Белая шляпа — факты (исследования и практика 10+ лет)

**Нейронаука (обязательно в продукте):**
- **Retrieval practice** (Karpicke): активное вспоминание > перечитывание; у детей 7+ эффект устойчив; у 1–6 — **guided recall** с подсказкой-образом.
- **Dual coding** (Paivio): слово + картинка/звук одновременно → прочнее след в LTM.
- **Spaced repetition + мнемо** (Putnam 2015): связка даёт recall через 7+ дней; без SRS мнемо деградирует в «зубрёжку на тест».
- **Эпизодический контекст**: у 1–2 класса слабее — не требовать «вспомни контекст урока», только яркий образ.
- **Hippocampus + spatial**: Method of Loci работает у детей, т.к. мозг силён в пространстве (JMC, Hancock).

**Мир (10+ лет):**
| Источник | Стаж | Что взять в ALADDIN |
|----------|------|---------------------|
| **UK Schools Memory Championships** (O'Brien, Buzan, с 2008) | 17+ лет | Journey Method, «Game of Memory», экзаменные списки |
| **Junior Memory Championship** (Hancock) | 15+ лет | Memory journey, fantasy landscape, whole-brain |
| **Dominic O'Brien** (книги с 1994, школы) | 30+ лет | 3 ключа: Association, Imagination, Location |
| **HappyChild / Accelerated Learning** | 20+ лет | Number-rhyme peg, journey по дому |
| **Superhero Spelling (UK KS2)** | 10+ лет | Memory palace для орфографии → study.01 |

**Россия (10+ лет):**
| Источник | Что взять |
|----------|-----------|
| **КиберЛенинка / начальная школа** | Произвольная память, словарные слова через образ |
| **«Запоминай-ка» (2 класс, ФГОС)** | Рисунок, созвучие, группировка, стихи |
| **Беззубикова — мнемоквадрат, мнемодорожка, мнемотаблица** | Структура урока study + UI games |
| **Гимназия Минск (2014–2016, 2 года опыт)** | Мнемофразы, таблицы, тренажёры |
| **Полиглотики / Айтигенио / Викиум** | Дворец памяти, ассоциации, игровые тренажёры |
| **AMAkids Memorika** (сеть, Junior 7–10, Senior 11–16) | 11 методов, 12 уроков, 3 уровня, образное мышление |

### 🔴 Красная — эмоции ребёнка
- Хочет «суперсилу», не «ещё один урок».
- Цифры 1–2–3–4 в games.05 — скучно; **единорог на мнемодорожке** — да.
- Провал → стыд; нужен **guided hint**, не красный крест.
- 🦄 за «вспомнил образ» = гордость.

### ⚫ Чёрная — риски v1
- Текст «повтори через 3 дня» без напоминания = **иллюзия SRS**.
- 30 study без единого дворца = фрагментация.
- EN без kid-friendly tone = потеря 50% аудитории.
- Родитель не видит «освоил дворец» → не доверяет.

### 🟡 Жёлтая — возможности
- **Один невидимый дворец** «Мир единорога» через все возрасты (комнаты растут).
- Существующие движки покрывают 90% UI; не хватает **MnemoCore** (SRS + levels).
- Wikium-тренажёры → маппинг на games.05, games.12, study, songs.

### 🟢 Зелёная — идеальная модель **AIM + 4D**

```
AIM (O'Brien)          4D (нейропедагогика)
─────────────────      ─────────────────────
A — Association        D1 — Dual coding (слово+образ/звук)
I — Imagination        D2 — Drill retrieval (активное вспоминание)
M — Location (loci)    D3 — Distributed spacing (1-3-7-14-30)
                       D4 — Delight (игра + 🦄 + уровни)
```

**4 фазы урока (вместо «3 страницы + тест»):**
1. **ENCODE** — dual code (текст + эмодзи/кадр/нота)
2. **ANCHOR** — поставить на остановку мнемодорожки
3. **RECALL** — guided → самостоятельный (по возрасту)
4. **REWARD** — 🦄 + запись в SRS

### 🔵 Синяя — решение
Встроить **ALADDIN Mnemo Academy** как невидимый слой (`MnemoCore`) в существующие категории; переименовать только мнемо-блоки; единая мнемодорожка единорога; SRS в коде; 3 уровня навыка.

---

## C) Где мнемотехника 100% (ваши блоки)

| Возраст | Категории (100% мнемо) | Не трогаем |
|---------|------------------------|------------|
| **1–6** | `songs` | toys, drawing, stories |
| **7–12** | `games`, `study`, `cartoons` | safety, creativity |
| **13–17** | `music`, `video` | safety, programming, social |
| **18–22** | `movies`, `education` | safety, career, internet |

---

## D) Переименования (i18n ✅ добавлено в LocalizationManager)

| Ключ | RU | EN |
|------|----|----|
| `child_mnemo_label_songs_kids` | Песни-память | Memory Songs |
| `child_mnemo_label_games_school` | Игры памяти | Memory Games |
| `child_mnemo_label_study_school` | Учим с образами | Study with Images |
| `child_mnemo_label_cartoons_school` | Мульт-мнемо | Cartoon Memory |
| `child_mnemo_label_music_teen` | Ритм-память | Rhythm Memory |
| `child_mnemo_label_video_teen` | Видео-образы | Video Imagery |
| `child_mnemo_label_movies_young` | Кино-память | Movie Memory |
| `child_mnemo_label_education_young` | Учёба-образы | Learning Imagery |

Подзаголовки: `child_mnemo_subtitle_*` — в LocalizationManager ✅  
Фазы: `child_mnemo_phase_encode|anchor|recall|reward` ✅  
Техники: `child_mnemo_technique_*` (10 шт.) ✅  
Уровни: `child_mnemo_skill_novice|apprentice|champion` ✅

---

## E) Как это выглядит в UI (без новых блоков)

### Главный экран (`08_ChildInterfaceScreen`)
- Шапка: **только** `Привет!` ✅
- Кнопка «Песни-память» (1–6) вместо «Песни»
- Кнопки 7–12: Игры памяти / Учим с образами / Мульт-мнемо
- и т.д.

### Каталог (`ChildContentScreen`)
```
┌─────────────────────────────────────┐
│ 🎵 Песни-память                     │
│ Рифма и образ · Ученик памяти       │
│ [Образ] [Якорь] [Вспомни] [Награда] │  ← 4 фазы, progress dots
│ Сегодня повтори: 2                  │  ← SRS badge
└─────────────────────────────────────┘
```

### Урок study (`StudyLessonTestExperienceView` → 4 фазы)
```
Стр.1 ENCODE:  «Каждый охотник…» + 🌈 картинка
Стр.2 ANCHOR:   «Поставь на 3-ю остановку единорога»
Стр.3 RECALL:   guided quiz (подсказка-образ)
Тест:           3 вопроса, ≥1 про технику
Fail:           CTA → Игры памяти (child_mnemo_fail_cta_games)
```

### games.05 — «Мнемоквадрат + дорожка»
- Показ эмодзи 2 сек → скрыть → recall
- 4 остановки = мнемоквадрат 2×2
- 7+ остановок = мнемодорожка

### songs — «Викиум: Картина слов»
- Караоке → recall 3 слов → reverse order (7–12 опционально в games)

### cartoons / video / movies — «Кадр-якорь / Сюжет-связка»
- После просмотра: порядок сцен / кадр-образ / имя героя-образ

### ChildRewards
- +3/+5/+10 🦄 (ключи `child_mnemo_reward_*` ✅)
- Уровень: Novice → Apprentice (10 успешных recall) → Champion (дворец 20+ якорей)

---

## F) Матрица 10 техник × 4 возраста (100% покрытие)

| Техника | Ключ i18n | 1–6 | 7–12 | 13–17 | 18–22 | Движок |
|---------|-----------|:---:|:----:|:-----:|:-----:|--------|
| Рифма-якорь | `rhyme_peg` | ●●● | ● | — | — | songs |
| Цепочка | `link_chain` | ●● | ●●● | ●● | ●● | cartoons, movies |
| Дворец/дорожка | `memory_palace` | ● | ●●● | ●●● | ●●● | study, games.05 |
| Ключевое слово | `keyword` | — | ●●● | ●●● | ●● | study.19, games.12 |
| Мнемофраза | `acronym` | — | ●● | ●●● | ●●● | study.01,03, education |
| Группировка | `chunking` | ● | ●●● | ●●● | ●●● | study.02,18 |
| Ритм-код | `rhythm_code` | ●●● | ● | ●●● | ● | songs, music |
| Кадр-образ | `frame_peg` | — | ●● | ●●● | ●● | cartoons, video |
| Сюжет-связка | `story_link` | ●● | ●● | ●● | ●●● | movies, study.09 |
| SRS 1-3-7-14 | `spaced_review` | ● guided | ●● | ●●● | ●●● | MnemoCore |

●●● = основная техника возраста; ● = вводная; — = не акцент.

### F.2 Матрица техника × ступень мастерства (v3 Technique Mastery Matrix)

| Техника | Intro | Practice | Apply | Teach-back |
|---------|-------|----------|-------|------------|
| `rhyme_peg` | songs (1–6) | songs recall | study.02 chunk song | — |
| `link_chain` | songs 2-item | cartoons | study.12, 27 | — |
| `memory_palace` | games 4-stop | games 7-stop | study.05, 21 | study.25 exam palace |
| `keyword` | games.12 pairs | study.19 | study.13, 19 | — |
| `acronym` | study.03 КОЖЗФ | study.01 ИРД | study.07, 16 | education SMART |
| `chunking` | study.02 | study.17, 18 | study.24 SRS | — |
| `rhythm_code` | songs clap | music drills | study.11 | — |
| `frame_peg` | cartoons frame | video quiz | study.06, 08, 14, 15 | — |
| `story_link` | cartoons order | study.04 dates | study.09, 23 | movies plot-link |
| `spaced_review` | songs guided SRS | games SRS win | study.24, 25 | capstone retention |

**Ступени:** Intro → Practice → Apply → Teach-back. Прогресс пишет `MnemonicTechniqueMastery.swift` (Batch 9).

---

## G) Матрица 30 предметов study.* (техника + мнемофраза RU)

| ID | Предмет | Техника | Пример якоря (RU) |
|----|---------|---------|-------------------|
| study.01 | Русский | acronym + keyword | ИРД, образ слога |
| study.02 | Математика | chunking + rhyme | 7×8=56 «песня 5-6» |
| study.03 | Окружающий мир | acronym | КОЖЗФ (цвета) |
| study.04 | История | story_link | Цепочка дат-дворец |
| study.05 | География | memory_palace | Страны = комнаты |
| study.06 | Биология | frame_peg | Орган = яркий образ |
| study.07 | Физика | acronym | Формула = мнемофраза |
| study.08 | Химия | frame_peg | Элемент = цвет-образ |
| study.09 | Литература | story_link | Герой → событие |
| study.10 | ИЗО | dual code | Цвет = персонаж |
| study.11 | Спорт | rhythm_code | Такт = счёт |
| study.12 | Труд | link_chain | Шаги = остановки |
| study.13 | Обществознание | keyword | Термин = крючок |
| study.14 | Экология | frame_peg | Биом = место |
| study.15 | ПДД | frame_peg | Знак = сцена |
| study.16 | Здоровье | acronym | ВИТАМИН-правило |
| study.17 | Финансы | chunking | Суммы группами |
| study.18 | Информатика | chunking | Код блоками |
| study.19 | Язык | keyword + SRS | Образ слова + 1-3-7 |
| study.20 | Творчество | dual code | Метафора-образ |
| study.21 | Проект | memory_palace | Mind map = комнаты |
| study.22 | Исследование | acronym | Этапы НИР |
| study.23 | Групповая | story_link | Роли = персонажи |
| study.24 | Самостоятельная | spaced_review | Leitner-карточки |
| study.25 | Экзамены | palace + SRS | Дворец тем |
| study.26 | **Capstone** «Мой проект памяти» | all techniques | child picks topic → teach-back 3 min |
| study.27 | Лабораторная | link_chain | Шаги опыта |
| study.28 | Практика | drill recall | games.06 speed |
| study.29 | Творч. проект | dual code | Концепт-образ |
| study.30 | Портфолио | memory_palace | Папка = комната |

### Шаблон page_2 (все 30 предметов)

**RU:**  
`Техника: %@. Представь образ: … Поставь на остановку %d мнемодорожки. Повтор: сегодня, +1д, +3д, +7д.`

**EN:**  
`Technique: %@. Picture this: … Place it at stop %d on the memory path. Review: today, +1d, +3d, +7d.`

### G.2 Мнемотаблица — третья ступень российской школы (v3, Batch 13)

| Элемент | Спецификация |
|---------|--------------|
| **UI** | Grid 2×3 или 3×3; ячейка = пиктограмма + слово/фраза |
| **Когда** | После освоения квадрата (games.05) и дорожки (7+ stops) |
| **Контент** | study.09 (литература), тексты 5+ предложений |
| **Движок** | `MnemonicTableEngine` — variant games.05 или отдельный flow |
| **i18n** | `child_mnemo_table_*` (~15 ключей RU+EN) |
| **Recall** | Показ таблицы 3 сек → скрыть → восстановить порядок ячеек |

---

## H) MnemoCore — новый слой (единственный новый код, не UI-блок)

```
Core/Content/Mnemonics/
  MnemonicTechnique.swift           // enum 10 техник ✅
  MnemonicSRSStore.swift            // Leitner 1-3-7-14-30 ✅ (v3: +recordFailure, push)
  MnemonicSkillTracker.swift        // Novice/Apprentice/Champion ✅
  MnemonicRewardBridge.swift        // 🦄 ✅
  MnemonicJourneyPath.swift         // 20→40 остановок «Мир единорога» ✅
  MnemoCategoryChrome.swift         // 4 фазы UI ✅
  MnemonicStudyTechniqueMap.swift   // technique + journey stop ✅ (v3: semantic stops)
  // v3 (Batch 9–14):
  MnemonicCurriculumSpine.swift     // 8 семестров, unlock
  MnemonicTechniqueMastery.swift    // 10×4 ступени
  MnemonicBaselineAssessment.swift  // Memory Quotient
  MnemonicTableEngine.swift         // мнемотаблица 3×3
  MnemonicPictogramStore.swift      // co-created drawings local
  MnemonicHintLadder.swift          // 3 уровня подсказки
  MnemonicNotificationScheduler.swift // SRS push + deep link
```

Интеграция:
- `StudyLessonTestExperienceView` — 4 фазы
- `GamesChallengeEngineView` games.05 — palace drill
- `ContentRecommender` — boost due SRS items
- `ChildContentScreen` — subtitle + phase dots + SRS badge

---

## I) Локализация — статус и объём

### ✅ Уже в LocalizationManager (48 ключей)
- Labels + subtitles (8+8)
- Phases (4), AIM, skills (3), techniques (10)
- Journey, SRS, rewards, fail CTA

### ⏳ Осталось (~250 ключей)
| Пакет | Ключи | ID задачи |
|-------|-------|-----------|
| study page_2 × 30 | ~60 | MNEMO-P3-* |
| study test technique × 30 | ~90 | MNEMO-P3-* |
| songs tracks + recall | ~40 | MNEMO-P4-* |
| cartoons/video/movies | ~45 | MNEMO-P5-* |
| games.05/12 prompts | ~25 | MNEMO-P2-* |

**Правила EN:** короткие фразы, imperative («Picture…», «Place…»), без idioms.  
**Правила RU:** мнемофразы — культурно узнаваемые (КОЖЗФ, ИРД).  
**Gate:** `python3 scripts/child_localization_gate.py` после каждого пакета.

---

## J) Фазы реализации (обновлённые)

| Фаза | Содержание |
|------|------------|
| **P0** | Шапка «Привет!» ✅ |
| **P0b** | Базовые ключи child_mnemo_* ✅ |
| **P1** | Labels на кнопках + ChildContentScreen 4 фазы UI |
| **P1b** | **MnemoCore** scaffold (SRS + skill) |
| **P2** | games.05 palace + games.12 keyword pairs |
| **P3** | study 4-фазы + 30 page_2 (3 пакета) |
| **P4** | songs + cartoons |
| **P5** | music + video + movies + education |
| **P6** | Rewards + recommender + parent «mastery %» |
| **P7** | Gate + UITests + 4-age smoke |

---

## K) Cursor TODO — см. полный мастер-список §Q (**119 задач**)

> **v2.2:** все задачи v2 (Batch 0–8) и v3 (Batch 9–15) объединены в **§Q**.  
> Статус батчей — **§P**. Roadmap — **§Z**.

---

## L) Что НЕ меняем
- Количество кнопок на главном экране
- `ChildCategoryKey` / seed IDs
- toys, drawing, stories, safety, programming, social, creativity, career, internet
- Companion / Wellness

---

## M) Порядок в Cursor

### v2 MVP (Batch 0–8)
1. P1 (видимые лейблы) + P1b (MnemoCore) — параллельно  
2. P2 games.05 — первый working cycle  
3. P3 study content волнами  
4. P4–P5 по возрастам  
5. P6–P7  
6. P8 QA → F1–F10  

### v3 Course (Batch 9–15) — после/параллельно v2
1. **B10 параллельно B4+** — живой SRS (критично)  
2. B9 Curriculum Spine  
3. B12 Assessment + Capstone  
4. B13 Мнемотаблица + B11 Co-creation  
5. B14 Parent + Meta + Emotions  
6. B15 QA → F11–F15  

**Master:** `docs/MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md` (v2.2)

---

## N) ML HANDOFF — инструкция для любой ML-модели

### N.1 Рабочий корень (обязательно)

```
/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
```

Перед любой правкой:

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
git rev-parse --show-toplevel
git branch --show-current
git status --short
```

### N.2 Жёсткие ограничения (НЕ нарушать)

| Правило | Деталь |
|---------|--------|
| NO new home blocks | Не добавлять кнопки на `08_ChildInterfaceScreen` |
| NO categoryId change | `ChildCategoryKey` и seed IDs не менять |
| NO scope creep | toys, drawing, stories, safety, programming, social, creativity, career, internet — без мнемо |
| i18n parity | Каждый `child_mnemo_*` ключ — RU **и** EN в `LocalizationManager.swift` |
| Commit ID | `feat(mnemo): MNEMO-B{n}-T{m} краткое описание` |
| Gate | После каждого батча с i18n: `python3 scripts/child_localization_gate.py` |

### N.3 Педагогическая модель (вшить в код)

**AIM + 4D** — все уроки и игры следуют циклу:

```
ENCODE (dual code) → ANCHOR (journey stop) → RECALL (guided/active) → REWARD (🦄 + SRS)
```

Ключи фаз: `child_mnemo_phase_encode|anchor|recall|reward`

### N.4 Карта файлов (канон)

| Назначение | Файл |
|------------|------|
| Главный экран | `Screens/08_ChildInterfaceScreen.swift` |
| Каталог категории | `Screens/ChildContentScreen.swift` |
| Все движки | `Screens/ChildContentExperienceScreen.swift` |
| Категории (ID) | `Core/Content/Seed/ContentSeedProvider.swift` → `ChildCategoryKey` |
| Локализация | `Core/Localization/LocalizationManager.swift` |
| Награды | `Screens/ChildRewardsScreen.swift` |
| Персонализация | `Core/Content/Personalization/PersonalizationSystems.swift` |
| Родитель | `Screens/ParentDashboardView.swift` |
| **Новый слой** | `Core/Content/Mnemonics/*.swift` (создать в Batch 2) |
| План | `docs/MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md` |

### N.5 Финальный результат (Definition of Done — весь проект)

Проект **MNEMO 100%** считается завершённым, когда:

- [ ] **F1** — 8 мнемо-категорий показывают переименованные лейблы по возрасту
- [ ] **F2** — `MnemoCore` пишет SRS (1-3-7-14-30) и skill level (3 ступени)
- [ ] **F3** — `StudyLessonTestExperienceView` = 4 фазы + fail CTA → games
- [ ] **F4** — `games.05` = show→hide→emoji recall + journey
- [ ] **F5** — 30 `study.*` page_2 переписаны под мнемо (RU+EN)
- [ ] **F6** — songs + cartoons + music + video + movies + education = recall после контента
- [ ] **F7** — 🦄 начисляются через `MnemonicRewardBridge`
- [ ] **F8** — Parent dashboard: mnemo mastery % (без PII)
- [ ] **F9** — `child_localization_gate.py` PASS
- [ ] **F10** — Device smoke: 4 возраста × 8 мнемо-категорий
- [ ] **F11** — Curriculum Spine: 8 семестров, unlock ≥70% работает
- [ ] **F12** — Baseline + quarterly Memory Quotient в parent dashboard
- [ ] **F13** — Push «Сегодня повтори: N» + deep link в категорию
- [x] **F14** — Co-created pictogram сохраняется и показывается в recall (sign-off B15)
- [ ] **F15** — Мнемотаблица работает для study.09
- [x] **F16** — Brand «Академия памяти»: catalog + banner + parent Smart Memory

### N.5.1 F-flags — кто подписывает

| Flag | Sign-off owner | Когда |
|------|----------------|-------|
| F1–F9 | ML agent + `child_localization_gate.py` PASS | B8-T05 |
| F10 | Manual smoke (product/QA) | B8-T04/T05 |
| F11 | ML agent (UITest unlock) + manual 8×4 | B15-T03/T04/T05 |
| F12–F15 | ML agent (unit) + manual spot-check | B15-T05 |
| F13 | ML agent (unit B10-T08) + device push tap | B8/B10 tests |
| F16 | ✅ Product (brand) | B1C done |

**Tracker:** `docs/MNEMONICS_CURSOR_BATCH_TRACKER.md` · `python3 scripts/mnemo_batch_progress.py`

---

## O) БАТЧИ — подробный план + TODO для Cursor

> **Порядок:** Batch 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8.  
> Batch 1 и 2 можно параллелить. Batch 4 зависит от 2. Batch 7 зависит от 2–6.

---

### BATCH 0 — Foundation ✅ DONE

| ID | Задача | Файл | Статус |
|----|--------|------|--------|
| MNEMO-B0-T01 | Шапка только `Привет!` / `Hi!`, одна строка | `08_ChildInterfaceScreen.swift` | ✅ |
| MNEMO-B0-T02 | 48 ключей `child_mnemo_*` RU+EN | `LocalizationManager.swift` | ✅ |

**DoD Batch 0:** шапка без «Ты под защитой»; 48 ключей в обоих языках.

---

### BATCH 1 — UI Labels (главный экран + каталог)

**Цель:** пользователь видит мнемо-названия кнопок и каталог с 4 фазами.

**Prereq:** Batch 0 ✅

| ID | Задача | Что сделать | Файл |
|----|--------|-------------|------|
| MNEMO-B1-T01 | `mnemonicCategoryTitle(category:age:)` | Маппинг: songs→`child_mnemo_label_songs_kids` только при `.kids`; games/study/cartoons при `.school`; music/video при `.teen`; movies/education при `.youngAdult`; иначе `child_interface_category_*` | `08_ChildInterfaceScreen.swift` |
| MNEMO-B1-T02 | Подключить в `bigChildButton` | Заменить `localized(ChildCategoryKey.X)` на `mnemonicCategoryTitle` для 8 категорий | `08_ChildInterfaceScreen.swift` |
| MNEMO-B1-T03 | `MnemoCategoryChrome` helper | struct: `subtitleKey`, `isMnemoCategory`, `phaseKeys` | новый `Core/Content/Mnemonics/MnemoCategoryChrome.swift` |
| MNEMO-B1-T04 | Заголовок каталога | Если мнемо-категория → title + subtitle + 4 phase dots | `ChildContentScreen.swift` |
| MNEMO-B1-T05 | SRS badge placeholder | Текст `child_mnemo_srs_due_today` (пока 0, wiring в Batch 2) | `ChildContentScreen.swift` |
| MNEMO-B1-T06 | Gate | `python3 scripts/child_localization_gate.py` | — |

**DoD Batch 1:**
- [ ] 1–6: кнопка «Песни-память» (не «Songs»)
- [ ] 7–12: три мнемо-лейбла на games/study/cartoons
- [ ] Каталог мнемо-категории показывает subtitle + 4 точки фаз
- [ ] Gate PASS

**Verify:**
```bash
# Симулятор: Child Interface → каждый возраст → проверить тексты кнопок
python3 scripts/child_localization_gate.py
```

**Commit:** `feat(mnemo): MNEMO-B1 UI labels and catalog chrome`

---

### BATCH 1C — Brand «Академия памяти» (v2.3)

**Цель:** единый бренд + второстепенные слои (promise, superpower, smart memory).

**Prereq:** Batch 0 ✅

| ID | Задача | Файл | Статус |
|----|--------|------|--------|
| MNEMO-B1C-T01 | `MnemoBrandChrome` helper | `MnemoCategoryChrome.swift` | ✅ |
| MNEMO-B1C-T02 | i18n brand keys (§AA.2) RU+EN | `LocalizationManager.swift` | ✅ |
| MNEMO-B1C-T03 | Catalog header: brand title + tagline × age | `ChildContentScreen.swift` | ✅ |
| MNEMO-B1C-T04 | Academy banner: tagline + promise + superpower | `ChildContentScreen.swift` | ✅ |
| MNEMO-B1C-T05 | Parent: Smart Memory + scientific subtitle | `ParentDashboardView.swift` | ✅ |
| MNEMO-B1C-T06 | Level-up toast: superpower line | `ChildContentExperienceScreen.swift` | ✅ |
| MNEMO-B1C-T07 | Onboarding keys (wire OB_05 optional) | `14_OnboardingScreen.swift` | ⏳ |
| MNEMO-B1C-T08 | Gate brand keys | scripts | ⏳ |

**DoD Batch 1C:** F16 ✅; catalog показывает «Академия памяти» + tagline; parent «Умная память».

**Commit:** `feat(mnemo): MNEMO-B1C Memory Academy brand`

---

### BATCH 2 — MnemoCore (невидимый движок)

**Цель:** SRS, уровни навыка, мнемодорожка — единая память приложения.

**Prereq:** Batch 0 ✅ (Batch 1 желателен)

| ID | Задача | Что сделать | Файл |
|----|--------|-------------|------|
| MNEMO-B2-T01 | `MnemonicTechnique` enum | 10 cases = ключи `child_mnemo_technique_*` | `MnemonicTechnique.swift` |
| MNEMO-B2-T02 | `MnemonicSRSStore` | Leitner box 1–5; интервалы [1,3,7,14,30] дней; `scheduleReview(itemId:)` / `dueToday(childId:)` | `MnemonicSRSStore.swift` |
| MNEMO-B2-T03 | `MnemonicSkillTracker` | novice→apprentice (10 recall ok)→champion (20 anchors); UserDefaults per childId | `MnemonicSkillTracker.swift` |
| MNEMO-B2-T04 | `MnemonicJourneyPath` | 20 stops с ключами `child_mnemo_journey_stop_{1-20}` (добавить i18n) | `MnemonicJourneyPath.swift` |
| MNEMO-B2-T05 | i18n journey stops | 20×2=40 ключей RU+EN | `LocalizationManager.swift` |
| MNEMO-B2-T06 | Wire SRS badge | `ChildContentScreen` читает `MnemonicSRSStore.dueToday` | `ChildContentScreen.swift` |
| MNEMO-B2-T07 | Unit tests | SRS intervals, skill thresholds | `Tests/UnitTests/MnemonicSRSStoreTests.swift` |

**DoD Batch 2:**
- [ ] 5 файлов в `Core/Content/Mnemonics/`
- [ ] SRS записывает nextReviewDate после REWARD
- [ ] Badge «Сегодня повтори: N» работает
- [ ] Unit tests green

**Verify:**
```bash
xcodebuild test -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16' -only-testing:ALADDINTests/MnemonicSRSStoreTests 2>/dev/null | tail -5
```

**Commit:** `feat(mnemo): MNEMO-B2 MnemoCore SRS skill journey`

---

### BATCH 3 — Games памяти (7–12)

**Цель:** games.05 = полноценный palace drill; games.12 = keyword pairs.

**Prereq:** Batch 2 ✅

| ID | Задача | Что сделать | Файл |
|----|--------|-------------|------|
| MNEMO-B3-T01 | games.05 show→hide | Показ emoji 2 сек → скрыть → ввод; `@State showSequence` | `ChildContentExperienceScreen.swift` |
| MNEMO-B3-T02 | Emoji peg list | 🐱🌟🎈🚗🦄📚🎵⚽ вместо 1–4 | то же |
| MNEMO-B3-T03 | Мнемоквадрат 2×2 | rounds 1–2: 4 stops; round 3+: journey 7+ | то же |
| MNEMO-B3-T04 | SRS on win | `MnemonicSRSStore.recordSuccess(itemId: "games.05")` | то же |
| MNEMO-B3-T05 | games.12 pairs | 6 пар слово↔образ из i18n | то же |
| MNEMO-B3-T06 | i18n games | `child_mnemo_games_05_*`, `child_mnemo_games_12_pair_{1-6}_{word\|image}` RU+EN (~25 ключей) | `LocalizationManager.swift` |
| MNEMO-B3-T07 | Gate | child_localization_gate | — |

**DoD Batch 3:**
- [ ] games.05: sequence скрывается, recall работает, 3 раунда = complete
- [ ] games.12: 6 пар, match score
- [ ] SRS обновляется после games.05

**Commit:** `feat(mnemo): MNEMO-B3 games.05 palace and games.12 pairs`

---

### BATCH 4 — Study 4 фазы + 30 предметов (3 волны контента)

**Цель:** `StudyLessonTestExperienceView` = ENCODE→ANCHOR→RECALL→REWARD; контент study.01–30.

**Prereq:** Batch 2 ✅

#### Batch 4A — Рефакторинг движка

| ID | Задача | Файл |
|----|--------|------|
| MNEMO-B4A-T01 | Enum `StudyMnemoPhase`: encode, anchor, recall, reward | `ChildContentExperienceScreen.swift` |
| MNEMO-B4A-T02 | Заменить `lessonSection` на phase switch | то же |
| MNEMO-B4A-T03 | RECALL = guided (hint key `child_mnemo_recall_guided_hint`) | то же |
| MNEMO-B4A-T04 | REWARD → SRS + skill increment | то же |
| MNEMO-B4A-T05 | Fail test → CTA `child_mnemo_fail_cta_games` | то же |

#### Batch 4B — Контент волна 1 (study.01–10)

| ID | Предметы | Ключи (на каждый: page_1, page_2 мнемо, page_3, test×3) |
|----|----------|----------------------------------------------------------|
| MNEMO-B4B-T01 | study.01–05 | `child_study_{russian,math,world,history,geography}_page_2` + 1 test «техника» |
| MNEMO-B4B-T02 | study.06–10 | biology…art |

#### Batch 4C — Волна 2 (study.11–20)

| MNEMO-B4C-T01 | study.11–15 | sport…traffic |
| MNEMO-B4C-T02 | study.16–20 | health…creativity |

#### Batch 4D — Волна 3 (study.21–30)

| MNEMO-B4D-T01 | study.21–25 | project…exams |
| MNEMO-B4D-T02 | study.26–30 | skip 26 if empty…portfolio |

**Шаблон page_2 RU:**
```
Техника: {technique_localized}. Представь образ: {image}. Поставь на остановку {n} мнемодорожки. Повтор: сегодня, +1 день, +3 дня, +7 дней.
```

**DoD Batch 4:**
- [ ] 4 фазы в UI study
- [ ] 29 предметов с мнемо page_2 (study.26 резерв)
- [ ] ≥1 тестовый вопрос на технику в каждом предмете
- [ ] Gate PASS

**Commit (3 коммита):** `MNEMO-B4A engine`, `MNEMO-B4B-C content wave1-2`, `MNEMO-B4D content wave3`

---

### BATCH 5 — 1–6 Songs + 7–12 Cartoons

**Prereq:** Batch 2 ✅

| ID | Задача | Файл |
|----|--------|------|
| MNEMO-B5-T01 | 3 мнемо-трека в `KaraokeExperienceHostView` | `ChildContentExperienceScreen.swift` |
| MNEMO-B5-T02 | Guided recall после песни (3 слова/цифры) | то же |
| MNEMO-B5-T03 | Cartoons scene-order quiz после просмотра | `CartoonsActiveWatchExperienceView` |
| MNEMO-B5-T04 | i18n ~40 ключей `child_mnemo_song_*`, `child_mnemo_cartoon_*` | `LocalizationManager.swift` |
| MNEMO-B5-T05 | Gate | — |

**DoD Batch 5:**
- [ ] Песня → recall → можно завершить
- [ ] Мультфильм → «порядок сцен» квиз

**Commit:** `feat(mnemo): MNEMO-B5 songs and cartoons recall`

---

### BATCH 6 — 13–17 Music/Video + 18–22 Movies/Education

**Prereq:** Batch 2 ✅

| ID | Задача | Движок | Файл |
|----|--------|--------|------|
| MNEMO-B6-T01 | Rhythm-code drills | `MusicDrillsProgressionView` | `ChildContentExperienceScreen.swift` |
| MNEMO-B6-T02 | Frame-peg quiz | `VideoProductionExperienceView` | то же |
| MNEMO-B6-T03 | Plot-link + hero image | `MovieLiteracyExperienceView` | то же |
| MNEMO-B6-T04 | SMART/OKR acronym milestones | `EducationPathwaysMilestonesView` | то же |
| MNEMO-B6-T05 | i18n ~45 ключей teen/young | `LocalizationManager.swift` | |
| MNEMO-B6-T06 | Gate | — | |

**DoD Batch 6:** каждый движок имеет post-content recall step.

**Commit:** `feat(mnemo): MNEMO-B6 teen and young adult mnemo engines`

---

### BATCH 7 — Rewards + Personalization + Parent

**Prereq:** Batch 2–6 ✅

| ID | Задача | Файл |
|----|--------|------|
| MNEMO-B7-T01 | `MnemonicRewardBridge`: +3 song, +5 game/study, +10 streak | `MnemonicRewardBridge.swift` |
| MNEMO-B7-T02 | Skill level-up toast с `child_mnemo_skill_*` | `ChildContentExperienceScreen.swift` |
| MNEMO-B7-T03 | `ContentRecommender`: boost SRS due + failed study → games.05 | `PersonalizationSystems.swift` |
| MNEMO-B7-T04 | Parent dashboard: `mnemoMasteryPercent` (aggregated, no content text) | `ParentDashboardView.swift` |
| MNEMO-B7-T05 | metadata tag `mnemo` в seed items (опционально) | `ContentSeedProvider.swift` |

**DoD Batch 7:**
- [ ] 🦄 начисляются по правилам
- [ ] Level-up виден ребёнку
- [ ] Родитель видит % mastery

**Commit:** `feat(mnemo): MNEMO-B7 rewards recommender parent mastery`

---

### BATCH 8 — QA + Sign-off

**Prereq:** Batch 1–7 ✅

| ID | Задача | Команда / действие |
|----|--------|-------------------|
| MNEMO-B8-T01 | Full localization gate | `python3 scripts/child_localization_gate.py` |
| MNEMO-B8-T02 | Unit tests MnemoCore | xcodebuild test Mnemonic* |
| MNEMO-B8-T03 | UITest smoke | `Tests/UITests/MnemoAcademyUITests.swift` — 4-phase + SRS (`-UITestMnemoAcademy`) |
| MNEMO-B8-T04 | Manual matrix 4×8 | Симулятор: 4 age tabs × 8 mnemo categories → open → see 4 phases |
| MNEMO-B8-T05 | Обновить чеклист F1–F10 в этом файле | все [x] |

**DoD Batch 8:** F1–F10 все ✅.

**Commit:** `feat(mnemo): MNEMO-B8 QA sign-off mnemo academy 100%`

---

### BATCH 9 — Curriculum Spine (v3 многолетний курс)

**Цель:** longitudinal curriculum — ребёнок растёт 4→22 как «ученик памяти».

**Prereq:** Batch 2 ✅

| ID | Задача | Файл |
|----|--------|------|
| MNEMO-B9-T01 | `MnemonicCurriculumSpine.swift` — 8 семестров, недели, KPI | новый |
| MNEMO-B9-T02 | `MnemonicTechniqueMastery.swift` — 10 техник × 4 ступени | новый |
| MNEMO-B9-T03 | Unlock rules ≥70% → следующий семестр | `ChildContentScreen.swift` |
| MNEMO-B9-T04 | Journey expansion 20→40 stops + i18n stop 21–40 | `MnemonicJourneyPath.swift` |
| MNEMO-B9-T05 | Semantic journey stops: study.01→1 … study.30→30 | `MnemonicStudyTechniqueMap.swift` |
| MNEMO-B9-T06 | Semester progress UI в `mnemoAcademyBanner` | `ChildContentScreen.swift` |
| MNEMO-B9-T07 | i18n `child_mnemo_semester_{0-7}_*` RU+EN (~16 ключей) | `LocalizationManager.swift` |
| MNEMO-B9-T08 | Unit tests unlock + mastery thresholds | `Tests/UnitTests/` |

**DoD Batch 9:** F11 ✅; семестр 1→2 unlock при 70%; journey semantic stops.

**Commit:** `feat(mnemo): MNEMO-B9 curriculum spine and technique mastery`

---

### BATCH 10 — SRS v2 + Notifications (живой SRS)

**Цель:** без push SRS «умирает» через месяц; Leitner требует recordFailure.

**Prereq:** Batch 2 ✅ (можно параллельно Batch 3–4)

| ID | Задача | Файл |
|----|--------|------|
| MNEMO-B10-T01 | `recordFailure(itemId:)` → box 0, review +1 day | `MnemonicSRSStore.swift` |
| MNEMO-B10-T02 | `dueItems(childId:)` — список itemId на сегодня | `MnemonicSRSStore.swift` |
| MNEMO-B10-T03 | `MnemonicNotificationScheduler` — daily reminder | новый |
| MNEMO-B10-T04 | UNUserNotificationCenter permission + schedule | App delegate / manager |
| MNEMO-B10-T05 | Deep link: `aladdin://mnemo/review?category=games` | Navigation |
| MNEMO-B10-T06 | SRS badge tap → open first due item | `ChildContentScreen.swift` |
| MNEMO-B10-T07 | iCloud sync opt-in (NSUbiquitousKeyValueStore) | `MnemonicSRSStore.swift` |
| MNEMO-B10-T08 | Unit tests failure + dueItems + notification | `MnemonicSRSStoreTests.swift` |

**DoD Batch 10:** F13 ✅; провал → box 0; push «Сегодня повтори: 2» открывает категорию.

**Commit:** `feat(mnemo): MNEMO-B10 SRS v2 failure push deeplink`

---

### BATCH 11 — Co-creation (пиктограммы Беззубиковой)

**Цель:** ребёнок рисует свой образ — ENCODE phase; recall hint level 1.

**Prereq:** Batch 4A ✅; drawing engine (существующая категория `drawing`)

| ID | Задача | Файл |
|----|--------|------|
| MNEMO-B11-T01 | `MnemonicPictogramStore` — PNG per itemId, local, no PII | новый |
| MNEMO-B11-T02 | ENCODE CTA «Нарисуй свой образ» в study/songs | `ChildContentExperienceScreen.swift` |
| MNEMO-B11-T03 | Mini canvas или handoff → drawing category | experience flow |
| MNEMO-B11-T04 | RECALL hint level 1: показать saved pictogram | recall phase |
| MNEMO-B11-T05 | i18n `child_mnemo_pictogram_*` (~10 ключей) | `LocalizationManager.swift` |
| MNEMO-B11-T06 | Parent: «N pictograms created» (count only) | `ParentDashboardView.swift` |

**DoD Batch 11:** F14 ✅; pictogram сохраняется и показывается в recall.

**Commit:** `feat(mnemo): MNEMO-B11 co-created pictograms`

---

### BATCH 12 — Assessment + Capstone + Championship

**Цель:** Memory Quotient (AMAkids/JMC); study.26 capstone; personal best.

**Prereq:** Batch 4, 7 ✅

| ID | Задача | Файл |
|----|--------|------|
| MNEMO-B12-T01 | `MnemonicBaselineAssessment` — 5 слов / 2 мин | новый |
| MNEMO-B12-T02 | Memory Quotient score 0–100 | `MnemonicBaselineAssessment.swift` |
| MNEMO-B12-T03 | Quarterly re-test schedule (90 days) | spine integration |
| MNEMO-B12-T04 | Parent dashboard: MQ trend (no content text) | `ParentDashboardView.swift` |
| MNEMO-B12-T05 | study.26 Capstone flow — pick topic, teach-back 3 min | `ChildContentExperienceScreen.swift` |
| MNEMO-B12-T06 | Championship mode: 20 items / 5 min, personal best only | games.05 variant |
| MNEMO-B12-T07 | i18n assessment + capstone (~20 ключей) | `LocalizationManager.swift` |
| MNEMO-B12-T08 | Unit tests MQ calculation | tests |

**DoD Batch 12:** F12 ✅; baseline at semester 1 week 10; capstone unlocks Champion.

**Commit:** `feat(mnemo): MNEMO-B12 assessment capstone championship`

---

### BATCH 13 — Мнемотаблица (3R Register)

**Цель:** третья ступень российской школы — таблица для текстов 5+ предложений.

**Prereq:** Batch 3 ✅

| ID | Задача | Файл |
|----|--------|------|
| MNEMO-B13-T01 | `MnemonicTableEngine` — 3×3 grid show/hide/recall | новый |
| MNEMO-B13-T02 | study.09 literature integration | `ChildContentExperienceScreen.swift` |
| MNEMO-B13-T03 | Cell = emoji default + optional co-created pictogram | engine |
| MNEMO-B13-T04 | SRS on table recall success | `MnemonicSRSStore.swift` |
| MNEMO-B13-T05 | i18n `child_mnemo_table_*` (~15 ключей) | `LocalizationManager.swift` |
| MNEMO-B13-T06 | Gate table keys | scripts |

**DoD Batch 13:** F15 ✅; 6-cell table recall для study.09.

**Commit:** `feat(mnemo): MNEMO-B13 mnemotable engine`

---

### BATCH 14 — Parent Guide + Metacognition + Emotions

**Цель:** родительский ROI; REFLECT для 13+; 3-level hints; emotional design.

**Prereq:** Batch 7, 9 ✅

| ID | Задача | Файл |
|----|--------|------|
| MNEMO-B14-T01 | `parent_mnemo_guide_*` — 30 ключей RU+EN | `LocalizationManager.swift` |
| MNEMO-B14-T02 | Parent guide WebView «5 минут мнемо за ужином» | `ParentDashboardView.swift` |
| MNEMO-B14-T03 | Technique mastery breakdown parent UI | `ParentDashboardView.swift` |
| MNEMO-B14-T04 | `MnemonicHintLadder` — образ → буква → 3-choice | новый |
| MNEMO-B14-T05 | WARMUP phase (30 sec focus) для 7+ | `MnemoAcademyPhase` extend |
| MNEMO-B14-T06 | REFLECT phase «Какую технику выбрал?» для 13+ | study flow |
| MNEMO-B14-T07 | Technique picker before study lesson (13+) | `StudyLessonTestExperienceView` |
| MNEMO-B14-T08 | Memory Hero avatars (без имён реальных людей) | i18n + assets |
| MNEMO-B14-T09 | Micro-wins: 🦄 за попытку, не только 100% | `MnemonicRewardBridge.swift` |
| MNEMO-B14-T10 | Teen framing keys «хаки для экзаменов» | i18n teen packs |
| MNEMO-B14-T11 | Family Memory Challenge share sheet (5 words, no PII) | optional flow |
| MNEMO-B14-T12 | Companion voice: «2 карточки на сегодня» (opt-in) | Companion integration |
| MNEMO-B14-T13 | Stories optional recall hook (story_link, не менять stories) | content bridge |
| MNEMO-B14-T14 | Advanced track: number pegs opt-in (15+) | education sub-flow |
| MNEMO-B14-T15 | EN native review checklist | docs/process |
| MNEMO-B14-T16 | Parent widget: «до следующего семестра: N%» | `ParentDashboardView.swift` |

**DoD Batch 14:** parent видит techniques breakdown; 3 hint levels; REFLECT на 13+.

**Commit:** `feat(mnemo): MNEMO-B14 parent guide metacognition hints`

---

### BATCH 15 — v3 QA Sign-off

**Prereq:** Batch 9–14 ✅

| ID | Задача |
|----|--------|
| MNEMO-B15-T01 | Full gate all mnemo keys (~350+) |
| MNEMO-B15-T02 | Unit tests all MnemoCore v3 |
| MNEMO-B15-T03 | UITest: semester unlock + SRS push deeplink |
| MNEMO-B15-T04 | Manual: 8 semesters × 4 ages smoke |
| MNEMO-B15-T05 | F1–F15 all ✅ in this doc |

**Commit:** `feat(mnemo): MNEMO-B15 v3 course sign-off`

---

## P) Сводная таблица батчей (для трекинга)

| Batch | Название | Задач | Prereq | Статус |
|-------|----------|-------|--------|--------|
| **0** | Foundation | 2 | — | ✅ DONE |
| **1C** | Brand Academy | 8 | 0 | ✅ DONE |
| **1** | UI Labels | 6 | 0 | ✅ DONE |
| **2** | MnemoCore | 7 | 0 | ✅ DONE |
| **3** | Games 7–12 | 7 | 2 | ✅ DONE |
| **4** | Study 4ф + 30 | 11 | 2 | ✅ DONE |
| **5** | Songs + Cartoons | 5 | 2 | ✅ DONE |
| **6** | Teen + Young | 6 | 2 | ✅ DONE |
| **7** | Rewards + Parent | 5 | 2–6 | ✅ 5/5 |
| **8** | QA v2 Sign-off | 5 | 1–7 | ⏳ Phase C 1/5 |
| **9** | Curriculum Spine | 8 | 2 | ⏳ Phase C 7/8 |
| **10** | SRS v2 + Push | 8 | 2 | ⏳ Phase C 7/8 |
| **11** | Co-creation | 6 | 4A | ✅ 6/6 |
| **12** | Assessment + Capstone | 8 | 4,7 | ✅ 8/8 |
| **13** | Мнемотаблица | 6 | 3 | ✅ 6/6 |
| **14** | Parent + Meta + Emotions | 16 | 7,9 | ✅ 16/16 |
| **15** | QA v3 Sign-off | 5 | 9–14 | ⏳ Phase C 3/5 |
| | **ИТОГО v2** | **62** | | **58/62** |
| | **ИТОГО v3** | **57** | | **53/57** |
| | **ВСЕГО** | **119** | | **111/119 (93%)** — см. `MNEMO_PROJECT_SYNC.md` |

---

## U) v2 vs v3 — итоговая оценка и gap analysis

### U.1 Главный пробел v2

v2 описывает **что показать в каждой категории**, но не **longitudinal curriculum** — как ребёнок растёт 4→22 как «ученик памяти».

### U.2 Сравнение с лучшими программами мира

| Программа | Длительность | Структура | Чего не хватало в v2 | Batch закрытия |
|-----------|-------------|-----------|----------------------|----------------|
| **AMAkids Memorika** | 4 мес × 3 уровня | 12 занятий, 11 методов, MQ-тест, 20 мин×4/нед | Master level, baseline, частота | B12, B14 |
| **Junior Memory Championship** (Hancock) | Year 5–6 | Fantasy journey, whole-brain, teacher videos | Parent guide, championship | B9, B12, B14 |
| **UK Schools Memory Championships** (O'Brien) | Учебный год | Baseline → techniques → exam lists | Baseline, exam application | B12, B4 |
| **Беззубикова / «Запоминай-ka»** | 1–4 класс | Квадрат → дорожка → **таблица** | Мнемотаблица, co-create | B11, B13 |
| **Dominic O'Brien courses** | Многоуровневый | Intro → Tools → Application → Advanced | Advanced (numbers, spelling) | B14 |

### U.3 Оценка по критериям

| Критерий | v2 сейчас | v3 (Batch 9–15) |
|----------|-----------|-----------------|
| Научная база | 9/10 | **10/10** |
| Российская школа | 7/10 | **10/10** (таблица + co-create) |
| Мировая школа | 8/10 | **10/10** (baseline + championship) |
| Многолетность | 4/10 | **9/10** (Curriculum Spine) |
| iOS-реализация | 6/10 | **9/10** (после B10) |
| Родительский ROI | 5/10 | **9/10** (MQ + technique breakdown) |

### U.4 Три столпа v3 (не забыть)

1. **Curriculum Spine** — семестры, unlock, technique mastery matrix → **Batch 9**
2. **Живой SRS** — recordFailure + push + deep links → **Batch 10**
3. **Российская 3-я ступень** — мнемотаблица + co-created pictograms → **Batch 11 + 13**

---

## V) Метод 6 шляп — расширенный аудит + задачи

> Каждый пункт ниже имеет ID задачи в §Q.

### 🤍 V.1 Белая шляпа — факты и пробелы

| # | Факт / пробел | Задача |
|---|---------------|--------|
| W1 | Последовательность: рифма → квадрат → дорожка → таблица → дворец → meta | B9 Curriculum Spine |
| W2 | SRS без push = иллюзия | B10-T03–T06 |
| W3 | Co-created mnemonics ×1.5–2 vs emoji | B11 |
| W4 | Baseline + MQ (AMAkids, JMC) | B12-T01–T04 |
| W5 | Мнемотаблица — 3R Register | B13 |
| W6 | `recordFailure` в Leitner | B10-T01 |
| W7 | 3 skill levels мало → + technique mastery 4 stages | B9-T02 |
| W8 | Semantic palace stops (не hash) | B9-T05 |
| W9 | iCloud sync при смене устройства | B10-T07 |
| W10 | 20 мин × 4/нед — recommender cadence | B7-T03 + B14 |

### 🔴 V.2 Красная шляпа — эмоции ребёнка

| Возраст | Потребность | Задача |
|---------|-------------|--------|
| 1–6 | Микропобеды каждые 2 мин | B14-T09 micro-wins |
| 7–9 | «Хочу быть чемпионом» | B14-T08 Memory Hero |
| 10–12 | Личный рекорд, не leaderboard | B12-T06 personal best |
| 13–17 | «Хаки для экзаменов», не игрушки | B14-T10 teen framing |
| Все | 3 уровня подсказки, не красный крест | B14-T04 HintLadder |

### ⚫ V.3 Чёрная шляпа — риски

| Риск | Mitigation | Задача |
|------|------------|--------|
| Фрагментация дворца (hash stops) | study.N → stop N | B9-T05 |
| Разрыв 6→7 лет между songs/games | Journey 4→12→20→40 | B9-T04 |
| EN tone без native review | Checklist | B14-T15 |
| Parent % без контекста | Technique breakdown + MQ | B14-T03, B12-T04 |
| study.26 пустой | Capstone project | B12-T05 |
| UserDefaults only | iCloud opt-in | B10-T07 |

### 🟡 V.4 Жёлтая шляпа — возможности

| Возможность | Batch |
|-------------|-------|
| Curriculum Spine 8 семестров | B9 |
| Technique Mastery Matrix 10×4 | B9 |
| Draw pictogram (drawing category) | B11 |
| Family Memory Challenge | B14-T11 |
| Companion voice reminder | B14-T12 |
| Stories optional recall | B14-T13 |
| Championship personal best | B12-T06 |
| Advanced number pegs 15+ | B14-T14 |

### 🟢 V.5 Зелёная шляпа — модель AIM + 4D + 3R + 5L

```
AIM (O'Brien)     4D (нейро)       3R (Россия)        5L (курс)
─────────────     ────────────     ─────────────      ──────────────
Association       Dual coding      Rhyme (рифма)      L0 Pre (1–4)
Imagination       Drill retrieval  Road (дорожка)     L1 Found (5–7)
Location          Distributed      Register (таблица) L2 Build (8–10)
                  Delight                             L3 Apply (11–14)
                                                      L4 Master (15–17)
                                                      L5 Meta (18–22)
```

**Фазы урока v3:**
- **WARMUP** (0) — 30 сек focus, 7+ → B14-T05
- **ENCODE → ANCHOR → RECALL → REWARD** (1–4) — v2, сохранить
- **REFLECT** (5) — «какую технику?», 13+ → B14-T06

### 🔵 V.6 Синяя шляпа — приоритеты

| Приоритет | Когда | Batch |
|-----------|-------|-------|
| P0 | Сейчас | B1 gate → B2 full → B3 |
| P0 parallel | Критично | **B10** (SRS живой) |
| P1 | Следующий квартал | B4–B6 content |
| P2 | После MVP v2 | B9 Spine → B12 Assessment |
| P3 | Дифференциатор | B11 + B13 (co-create + таблица) |
| P4 | Полировка | B14 + B15 |

---

## W) Многолетний курс — 8 семестров (Curriculum Spine)

> Реализует `MnemonicCurriculumSpine.swift` (B9). Unlock: mastery ≥70% предыдущего семестра.

### W.0 Семестр 0 — «Пробуждение памяти» (1–4 года, `songs`)

| Нед | Техника | Контент | KPI | Unlock |
|-----|---------|---------|-----|--------|
| 1–4 | rhyme + dual code | 3 мнемо-песни, 3 слова recall | 3 guided recall OK | — |
| 5–8 | link_chain 2-item | «Кошка → звезда» | 2-item chain | — |
| 9–12 | rhythm_code | хлопки + цифры 1–3 | rhythm match | → Semester 1 |

### W.1 Семестр 1 — «Мнемоквадрат» (5–7 лет, `songs` + intro `games`)

| Нед | Техника | Контент | KPI |
|-----|---------|---------|-----|
| 1–3 | мнемоквадрат 2×2 | games.05 r1–2 | 4 emoji recall |
| 4–6 | rhyme_peg | songs track 1–3 | 3-word recall |
| 7–9 | journey stops 1–4 | anchor placement | 4 anchors |
| 10–12 | **Baseline #1** | 5 слов / 2 мин | Memory Quotient v1 |

### W.2 Семестр 2 — «Мнемодорожка» (7–9 лет, `games` + `cartoons`)

| Нед | Техника | Контент | KPI |
|-----|---------|---------|-----|
| 1–4 | memory_palace 7-stop | games.05 r3+ | 7-item journey |
| 5–8 | story_link | cartoons scene order | 4-scene order |
| 9–12 | keyword | games.12 pairs | 6 pairs |
| Capstone | «Мой первый дворец» | 7 stops filled | **Apprentice** |

### W.3 Семестр 3 — «Школа образов» (8–10 лет, `study` 01–10)

| Нед | Техника | Контент | KPI |
|-----|---------|---------|-----|
| 1–3 | acronym | study.01, 03 (ИРД, КОЖЗФ) | acronym recall |
| 4–6 | chunking | study.02 (7×8=56) | chunk song |
| 7–9 | palace per subject | study.05, 21 | 10 room anchors |
| 10–12 | **мнемотаблица** | study.09 lit | 6-cell recall |

### W.4 Семестр 4 — «Применение» (10–12 лет, `study` 11–20)

| Нед | Техника | Контент | KPI |
|-----|---------|---------|-----|
| 1–4 | frame_peg | study.06, 08, 14 | organ→image |
| 5–8 | story_link chains | study.04, 09 | date chain |
| 9–12 | spaced_review | study.19, 24 | 30-day retention |
| Capstone | **study.26** | child topic teach-back 3 min | project done |

### W.5 Семестр 5 — «Ритм и кадр» (11–14 лет, `music` + `video`)

| Нед | Техника | Контент | KPI |
|-----|---------|---------|-----|
| 1–4 | rhythm_code | music drills | beat+code |
| 5–8 | frame_peg adv | video quiz | frame→concept |
| 9–12 | cross-technique | meta-choice quiz | pick best technique |

### W.6 Семестр 6 — «Сюжеты и системы» (13–16 лет, `movies` + `education`)

| Нед | Техника | Контент | KPI |
|-----|---------|---------|-----|
| 1–4 | plot_link | movies recall | hero→event |
| 5–8 | acronym SMART/OKR | education | framework |
| 9–12 | exam palace | study.25 | 20-topic palace |
| Capstone | championship | 20 items / 5 min personal best | **Champion** |

### W.7–8 Семестр 7–8 — «Мастер и метакognition» (15–22, `education` + all)

| Блок | Содержание | KPI |
|------|------------|-----|
| Meta-choice | словарь vs формула vs даты | technique picker |
| Advanced opt-in | Dominic-style number pegs | 15+ track |
| Teach-back | voice record → local recall check (no upload) | 3 min |
| Portfolio | study.30 palace | 40-stop journey full |
| Quarterly MQ | re-test every 90 days | MQ trend up |

---

## X) Критические исправления кода (до/параллельно Batch 3)

### X.1 MnemonicSRSStore — recordFailure

```swift
func recordFailure(itemId: String, now: Date = Date()) {
    var entry = entries[itemId] ?? Entry(itemId: itemId, box: 0, lastReviewed: nil, nextReview: nil)
    entry.box = 0
    entry.lastReviewed = now
    entry.nextReview = Calendar.current.date(byAdding: .day, value: reviewIntervalsDays[0], to: now)
    entries[itemId] = entry
    persist()
}
```

### X.2 MnemonicStudyTechniqueMap — semantic stops

```swift
static func journeyStop(for itemId: String) -> Int {
    if itemId.hasPrefix("study."),
       let num = Int(itemId.replacingOccurrences(of: "study.", with: "")),
       (1...30).contains(num) {
        return min(num, MnemonicJourneyPath.stopCount)
    }
    // games/songs: progressive unlock from spine
    return MnemonicCurriculumSpine.shared.nextAvailableStop(for: itemId)
}
```

### X.3 MnemonicSkillTracker — расширенные уровни (v3)

Дополнить `MnemonicSkillLevel` или parallel enum `MnemoCourseLevel` (L0–L5) в B9 — не ломать Novice/Apprentice/Champion для v2 rewards.

---

## Y) Parent & Teacher Guide (§T)

| Пакет | Ключи | Batch |
|-------|-------|-------|
| `parent_mnemo_guide_intro_*` | что такое AIM+4D | B14-T01 |
| `parent_mnemo_guide_dinner_*` | 5 минут за ужином | B14-T02 |
| `parent_mnemo_guide_technique_*` | 10 техник простым языком | B14-T01 |
| `parent_mnemo_guide_srs_*` | как помочь с повторением | B14-T01 |
| `parent_mnemo_guide_mq_*` | как читать Memory Quotient | B12-T04 |

**Формат:** WebView в Parent Dashboard — **не новый блок** на child home.

---

## Q) Cursor TODO — МАСТЕР-СПИСОК (119 задач)

> **Правило:** после каждого batch — gate (если i18n), обновить статус в §P, commit `feat(mnemo): MNEMO-B{n}...`

### ✅ BATCH 0 — Foundation
- [x] MNEMO-B0-T01 — Шапка «Привет!»
- [x] MNEMO-B0-T02 — 48 ключей child_mnemo_*

### ✅ BATCH 1C — Brand Memory Academy (v2.3)
- [x] MNEMO-B1C-T01 — MnemoBrandChrome helper
- [x] MNEMO-B1C-T02 — i18n brand keys §AA.2 RU+EN
- [x] MNEMO-B1C-T03 — catalog header brand title + tagline
- [x] MNEMO-B1C-T04 — academy banner promise + superpower
- [x] MNEMO-B1C-T05 — parent Smart Memory + subtitle
- [x] MNEMO-B1C-T06 — level-up superpower toast
- [x] MNEMO-B1C-T07 — onboarding OB_05 wire (optional card)
- [x] MNEMO-B1C-T08 — gate brand keys

### ✅ BATCH 1 — UI Labels
- [x] MNEMO-B1-T01 — mnemonicCategoryTitle()
- [x] MNEMO-B1-T02 — bigChildButton labels (8 категорий)
- [x] MNEMO-B1-T03 — MnemoCategoryChrome.swift
- [x] MNEMO-B1-T04 — ChildContentScreen subtitle + 4 phases + greeting
- [x] MNEMO-B1-T05 — SRS badge + MnemonicSRSStore stub
- [x] MNEMO-B1-T06 — `python3 scripts/child_localization_gate.py` PASS

### ✅ BATCH 2 — MnemoCore
- [x] MNEMO-B2-T01 — MnemonicTechnique.swift
- [x] MNEMO-B2-T02 — MnemonicSRSStore.swift (Leitner stub)
- [x] MNEMO-B2-T03 — MnemonicSkillTracker.swift
- [x] MNEMO-B2-T04 — MnemonicJourneyPath.swift
- [x] MNEMO-B2-T05 — i18n journey stops ×20 RU+EN
- [x] MNEMO-B2-T06 — Wire SRS badge live (dueToday)
- [x] MNEMO-B2-T07 — Unit tests MnemonicSRSStore + SkillTracker

### ✅ BATCH 3 — Games 7–12
- [x] MNEMO-B3-T01 — games.05 show→hide→recall
- [x] MNEMO-B3-T02 — emoji peg list
- [x] MNEMO-B3-T03 — мнемоквадрат 2×2 + дорожка 7+
- [x] MNEMO-B3-T04 — SRS recordSuccess on win
- [x] MNEMO-B3-T05 — games.12 keyword pairs
- [x] MNEMO-B3-T06 — i18n games prompts (~25 ключей)
- [x] MNEMO-B3-T07 — localization gate

### ✅ BATCH 4 — Study 4 фазы + 30 предметов
- [x] MNEMO-B4A-T01 — StudyMnemoPhase / MnemoAcademyPhase wiring
- [x] MNEMO-B4A-T02 — phase switch UI (ENCODE→ANCHOR→RECALL→REWARD)
- [x] MNEMO-B4A-T03 — guided recall + HintLadder stub
- [x] MNEMO-B4A-T04 — REWARD → SRS + skill increment
- [x] MNEMO-B4A-T05 — fail test → CTA games + SRS recordFailure
- [x] MNEMO-B4B-T01 — study.01–05 content RU+EN
- [x] MNEMO-B4B-T02 — study.06–10 content RU+EN
- [x] MNEMO-B4C-T01 — study.11–15 content RU+EN
- [x] MNEMO-B4C-T02 — study.16–20 content RU+EN
- [x] MNEMO-B4D-T01 — study.21–25 content RU+EN
- [x] MNEMO-B4D-T02 — study.27–30 content (study.26 → B12 capstone)

### ✅ BATCH 5 — Songs + Cartoons
- [x] MNEMO-B5-T01 — 3 мнемо-трека
- [x] MNEMO-B5-T02 — song guided recall после караоке
- [x] MNEMO-B5-T03 — cartoon scene-order quiz
- [x] MNEMO-B5-T04 — i18n songs/cartoons (~40 ключей)
- [x] MNEMO-B5-T05 — gate

### ✅ BATCH 6 — Teen + Young Adult
- [x] MNEMO-B6-T01 — music rhythm-code drills + recall
- [x] MNEMO-B6-T02 — video frame-peg quiz
- [x] MNEMO-B6-T03 — movies plot-link + hero images
- [x] MNEMO-B6-T04 — education SMART/OKR acronyms
- [x] MNEMO-B6-T05 — i18n teen/young (~45 ключей)
- [x] MNEMO-B6-T06 — gate

### ✅ BATCH 7 — Rewards + Personalization + Parent v2
- [x] MNEMO-B7-T01 — MnemonicRewardBridge wiring (+3/+5/+10)
- [x] MNEMO-B7-T02 — skill level-up celebrations
- [x] MNEMO-B7-T03 — ContentRecommender SRS due + failed study → games.05
- [x] MNEMO-B7-T04 — parent mnemo mastery % (basic)
- [x] MNEMO-B7-T05 — seed metadata tag `mnemo` (optional)

### ⏳ BATCH 8 — QA v2 Sign-off
- [x] MNEMO-B8-T01 — full localization gate v2 keys
- [ ] MNEMO-B8-T02 — unit tests MnemoCore v2 (defer: `scripts/mnemo_run_tests.sh`)
- [ ] MNEMO-B8-T03 — UITest 4-phase lesson + SRS (defer: end of v2)
- [ ] MNEMO-B8-T04 — manual 4 ages × 8 mnemo categories
- [ ] MNEMO-B8-T05 — F1–F10 sign-off (after tests + manual)

### ⏳ BATCH 9 — Curriculum Spine (v3)
- [x] MNEMO-B9-T01 — MnemonicCurriculumSpine.swift (8 semesters)
- [x] MNEMO-B9-T02 — MnemonicTechniqueMastery.swift (10×4 stages)
- [x] MNEMO-B9-T03 — unlock rules ≥70% in ChildContentScreen (`MnemoSemesterLockView`, `SemesterGate`)
- [x] MNEMO-B9-T04 — journey 20→40 stops + i18n 21–40 (`stopCount=40`)
- [x] MNEMO-B9-T05 — semantic journey stops study.01→30
- [x] MNEMO-B9-T06 — semester progress in mnemoAcademyBanner
- [x] MNEMO-B9-T07 — i18n semester names RU+EN
- [ ] MNEMO-B9-T08 — unit tests unlock + mastery

### 🔄 BATCH 10 — SRS v2 + Notifications (**КРИТИЧНО**)
- [x] MNEMO-B10-T01 — recordFailure → box 0
- [x] MNEMO-B10-T02 — dueItems(childId:) list
- [x] MNEMO-B10-T03 — MnemonicNotificationScheduler
- [x] MNEMO-B10-T04 — UNUserNotificationCenter permission
- [x] MNEMO-B10-T05 — deep link aladdin://mnemo/review
- [x] MNEMO-B10-T06 — SRS badge tap → first due item
- [x] MNEMO-B10-T07 — iCloud sync opt-in
- [ ] MNEMO-B10-T08 — unit tests failure + notifications (defer: end of v2)

### ⏳ BATCH 11 — Co-creation (Беззубикова)
- [x] MNEMO-B11-T01 — MnemonicPictogramStore.swift (Application Support/MnemoPictograms)
- [x] MNEMO-B11-T02 — ENCODE «Нарисуй свой образ» CTA (`MnemoPictogramEncodeCTA`)
- [x] MNEMO-B11-T03 — handoff to drawing / mini canvas (`MnemoPictogramDrawingSheet`)
- [x] MNEMO-B11-T04 — RECALL hint level 1 pictogram (`MnemoPictogramRecallHint`)
- [x] MNEMO-B11-T05 — i18n pictogram keys (11 keys RU+EN; gate + literal scan)
- [x] MNEMO-B11-T06 — parent pictogram count (`parent_dashboard_mnemo_pictogram_count`)

### ⏳ BATCH 12 — Assessment + Capstone + Championship
- [x] MNEMO-B12-T01 — MnemonicBaselineAssessment.swift + `MnemoBaselineAssessmentView` (5 words / 2 min)
- [x] MNEMO-B12-T02 — Memory Quotient 0–100 (85% recall + 15% speed bonus)
- [x] MNEMO-B12-T03 — quarterly re-test (90 days + 1×/calendar quarter)
- [x] MNEMO-B12-T04 — parent MQ trend UI (`MnemoParentMQTrendView` sparkline)
- [x] MNEMO-B12-T05 — study.26 Capstone teach-back (`MnemoStudyCapstoneExperienceView`)
- [x] MNEMO-B12-T06 — championship personal best mode (`MnemonicChampionshipStore` + `MnemoChampionshipExperienceView` games.05)
- [x] MNEMO-B12-T07 — i18n assessment + capstone (21 baseline + 18 capstone + reward; gate expanded)
- [x] MNEMO-B12-T08 — unit tests MQ + quarterly schedule (`MnemonicBaselineAssessmentTests` 17 tests)

### ✅ BATCH 13 — Мнемотаблица (3R Register)
- [x] MNEMO-B13-T01 — MnemonicTableEngine 3×3 + `MnemoTableExperienceView` show/hide/recall
- [x] MNEMO-B13-T02 — study.09 → `MnemoTableExperienceView` (not `StudyLessonTestExperienceView`)
- [x] MNEMO-B13-T03 — cell emoji + optional pictogram (`study.09.table.N` + `MnemoTableCellVisual`)
- [x] MNEMO-B13-T04 — SRS on table success (`recordRecallSuccess` → `MnemonicSRSStore.recordSuccess`)
- [x] MNEMO-B13-T05 — i18n table keys (`child_mnemo_table_*` 14 keys RU+EN)
- [x] MNEMO-B13-T06 — gate (631 keys PASS; `--prefix child_mnemo_table_` micro-gate)

### ⏳ BATCH 14 — Parent Guide + Metacognition + Emotions
- [x] MNEMO-B14-T01 — parent_mnemo_guide_* 30 keys (`MnemoParentGuideContent.swift` + gate)
- [x] MNEMO-B14-T02 — parent guide WebView (`MnemoParentGuideSheet` + CTA in `ParentDashboardView`)
- [x] MNEMO-B14-T03 — technique mastery breakdown parent UI (`MnemoParentTechniqueMasteryView`)
- [x] MNEMO-B14-T04 — MnemonicHintLadder (образ→буква→3-choice; no red X)
- [x] MNEMO-B14-T05 — WARMUP phase 7+ (`MnemoWarmupPhaseView` 30s; banner 4 dots)
- [x] MNEMO-B14-T06 — REFLECT phase 13+ (`MnemoReflectPhaseView` after REWARD)
- [x] MNEMO-B14-T07 — technique picker before study (`MnemoTechniquePickerView` 13+)
- [x] MNEMO-B14-T08 — Memory Hero avatars (`MnemoMemoryHeroChrome` + flag)
- [x] MNEMO-B14-T09 — micro-wins 🦄 за попытку (`awardRecallAttempt` +1)
- [x] MNEMO-B14-T10 — teen exam-hacks framing i18n (`child_mnemo_exam_hacks_*` + flag)
- [x] MNEMO-B14-T11 — Family Memory Challenge share sheet (`MnemoFamilyMemoryChallengeCard`)
- [x] MNEMO-B14-T12 — Companion voice SRS reminder (`MnemoCompanionSRSReminderCard` + opt-in)
- [x] MNEMO-B14-T13 — stories optional recall hook (`MnemoStoriesRecallHookBanner`)
- [x] MNEMO-B14-T14 — advanced number pegs opt-in 15+ (`MnemoAdvancedNumberPegsCard`)
- [x] MNEMO-B14-T15 — EN native review checklist (`docs/MNEMO_EN_NATIVE_REVIEW_CHECKLIST.md`)
- [x] MNEMO-B14-T16 — parent semester unlock progress widget (`MnemoParentSemesterProgressView`)

### ⏳ BATCH 15 — QA v3 Sign-off
- [x] MNEMO-B15-T01 — full gate ~350+ keys (`--mnemo-full` ≥350 PASS)
- [x] MNEMO-B15-T02 — unit tests all MnemoCore v3 (`MnemoCoreV3Tests` + xctestplan; run Phase C)
- [x] MNEMO-B15-T03 — UITest semester unlock + deeplink (`MnemoAcademyUITests` B15; run Phase C)
- [ ] MNEMO-B15-T04 — manual 8 semesters × 4 ages
- [ ] MNEMO-B15-T05 — F1–F15 sign-off

---

## R) Промпт для следующей ML-сессии (copy-paste)

> **Полный handoff:** `docs/MNEMONICS_ML_HANDOFF.md` (§14–17: lock UI, P0–P3, 6 шляп, B14 split)

```
Рабочий корень: ALADDIN_iOS (см. N.1).
Прочитай docs/MNEMO_PROJECT_SYNC.md + MNEMONICS_ML_HANDOFF.md + §Q.
Прогресс: 111/119. КОД 100%. NEXT: Phase C (8 задач) — см. §Q.1.A.
  gate --mnemo-full → mnemo_run_tests.sh → manual B8-T04 + B15-T04 → §N.5 F1–F15
НЕ писать новый код без запроса. xcodebuild только в Phase C.
Обнови §Q + tracker + MNEMO_PROJECT_SYNC.md. Commit по запросу.
Не добавляй блоки на главный экран. Не меняй ChildCategoryKey.
```

---

## Q.1) Acceptance criteria

### Q.1.A — 8 pending задач (Phase C only)

| ID | Готово когда… |
|----|----------------|
| **B8-T02** | `scripts/mnemo_run_tests.sh` unit suites green |
| **B8-T03** | `MnemoAcademyUITests` B8 tests PASS (`-UITestMnemoAcademy`) |
| **B8-T04** | Manual matrix 4 ages × 8 mnemo categories = PASS |
| **B8-T05** | F1–F10 все `[x]` в §N.5 |
| **B9-T08** | Unit unlock/mastery green (`MnemoCoreV3Tests` + spine tests) |
| **B10-T08** | Unit failure + `MnemonicNotificationScheduler` green |
| **B15-T04** | Manual 8 semesters × 4 ages documented PASS |
| **B15-T05** | F1–F15 все `[x]` в §N.5 |

> **Полный реестр 119 задач:** `docs/MNEMO_PROJECT_SYNC.md` §4

### Q.1.B — Acceptance criteria (все задачи, справочник)

| ID | Готово когда… |
|----|----------------|
| **B8-T02** | `scripts/mnemo_run_tests.sh` или `-only-testing:MnemonicSRSStoreTests` green |
| **B8-T03** | `MnemoAcademyUITests` PASS: 4-phase lesson + SRS badge (`-UITestMnemoAcademy`) |
| **B8-T04** | `MNEMO_B8_MANUAL_SMOKE_4x8.md` matrix 4 ages × 8 categories = PASS |
| **B8-T05** | F1–F10 все `[x]` в §N.5 после tests + manual |
| **B9-T08** | Unit: `gate`, `itemGate`, `masteryFraction` bounds; study split 3/4/7; no false unlock |
| **B10-T08** | Unit: `recordFailure`, `dueItems`, `MnemonicNotificationScheduler` reschedule |
| **B11-T01** | `MnemonicPictogramStore`: PNG в Application Support/MnemoPictograms/{itemId}.png |
| **B11-T02** | ENCODE phase CTA «Нарисуй свой образ» виден в lesson flow |
| **B11-T03** | Tap CTA → system drawing sheet или mini canvas; PNG сохраняется |
| **B11-T04** | RECALL hint level 1 показывает saved pictogram |
| **B11-T05** | `child_mnemo_pictogram_*` keys RU+EN; gate PASS |
| **B11-T06** | Parent dashboard: pictogram count без PII |
| **B12-T01** | `MnemonicBaselineAssessment`: 5 words / 2 min; score persisted |
| **B12-T02** | Memory Quotient 0–100 formula + UserDefaults persist |
| **B12-T03** | Re-test prompt через 90 дней; не чаще 1×/квартал |
| **B12-T04** | Parent MQ trend chart/sparkline (без PII) |
| **B12-T05** | study.26 Capstone teach-back 3 min flow unlocks Champion |
| **B12-T06** | Championship personal best mode + local leaderboard |
| **B12-T07** | i18n assessment + capstone keys RU+EN; incremental gate PASS |
| **B12-T08** | Unit tests MQ calculation + quarterly schedule |
| **B13-T01** | `MnemonicTableEngine` 3×3 grid recall |
| **B13-T02** | study.09 opens table experience (not plain quiz) |
| **B13-T03** | Cell emoji + optional pictogram from B11 store |
| **B13-T04** | Table success → `MnemonicSRSStore.recordSuccess` |
| **B13-T05** | `child_mnemo_table_*` keys RU+EN |
| **B13-T06** | `child_localization_gate.py` PASS after table keys |
| **B14-T01** | ~30 `parent_mnemo_guide_*` keys RU+EN |
| **B14-T02** | Parent WebView «5 минут мнемо за ужином» loads local HTML/markdown |
| **B14-T03** | Parent UI: technique mastery breakdown per 10 techniques |
| **B14-T04** | `MnemonicHintLadder`: образ → буква → 3-choice; no red X |
| **B14-T05** | WARMUP 30s focus phase age 7+ in lesson; catalog banner still 4 dots |
| **B14-T06** | REFLECT «какую технику?» age 13+ after REWARD |
| **B14-T07** | Technique picker before study lesson (13+) |
| **B14-T08** | Memory Hero avatars i18n+assets; behind `MnemoFeatureFlags` (optional) |
| **B14-T09** | 🦄 micro-win за попытку recall (not only 100%) |
| **B14-T10** | Teen exam-hacks framing keys; behind feature flag (optional) |
| **B14-T11** | Family Memory Challenge share sheet 5 words no PII; flag optional |
| **B14-T12** | Companion voice «2 карточки сегодня»; flag optional + opt-in |
| **B14-T13** | Stories optional recall hook via story_link; flag optional |
| **B14-T14** | Advanced number pegs 15+ opt-in; flag optional |
| **B14-T15** | EN native review checklist doc completed |
| **B14-T16** | Parent widget: «до следующего семестра: N%» from `SemesterGate`; a11y id |
| **B15-T01** | Full gate ~350+ child+parent mnemo keys PASS |
| **B15-T02** | `MnemoCoreV3Tests` + 7 suites in `ALADDIN_MnemoCore.xctestplan`; green in Phase C |
| **B15-T03** | UITest semester unlock + deeplink (`-UITestMnemoSemesterLocked`) |
| **B15-T04** | Manual matrix 8 semesters × 4 ages documented PASS |
| **B15-T05** | F1–F15 all `[x]` в §N.5 |

---

## RISK) Risk register

| Risk | Impact | Mitigation |
|------|--------|------------|
| `masteryFraction` false unlock via `categoryBoost` | Семестр открывается рано | B9-T08 unit bounds; рассмотреть per-semester recall KPI |
| B11 pictogram canvas scope | Timeline slip | MVP: handoff to system drawing sheet; defer in-app canvas |
| B12 MQ validity | Parent trust | Baseline 5 words / 2 min; disclose «игровой индекс» в parent copy |
| B14-T12 Companion voice | External dep | `MnemoFeatureFlags.companionVoiceReminder` default off |
| ChildContentScreen size | Merge conflicts | `MnemoAcademyBannerView` extracted (B9-T03) |
| iCloud KVS 1 MB | SRS sync fail | §IOS-NOTES chunking; opt-in warning |
| 350+ i18n keys | Gate churn | **Incremental gate** после каждого i18n-batch (§R, handoff §18) |

---

## FLAGS) B14 optional feature flags

`Core/Content/Mnemonics/MnemoFeatureFlags.swift` — UserDefaults + **Prod preset 4–22 v1** (2026-06-06):

| Flag key | Task | Prod default |
|----------|------|--------------|
| `mnemo.memoryHeroAvatars` | B14-T08 | **on** |
| `mnemo.teenExamHacksCopy` | B14-T10 | **on** |
| `mnemo.storiesRecallHook` | B14-T13 | **on** |
| `mnemo.advancedNumberPegs` | B14-T14 | **on** |
| `mnemo.familyMemoryChallenge` | B14-T11 | off (после QA) |
| `mnemo.companionVoiceReminder` | B14-T12 | off (волна 2) |

**B14-core** (always): T01–T07, T09, **T16** (parent semester progress).  
**B14-optional** (flags, код ✅): T08, T10–T14. **B14-process:** T15 checklist doc ✅.

---

## IOS-NOTES) iOS-специфика

| Topic | Rule |
|-------|------|
| B11 pictogram PNG | `MnemonicPictogramStore` → `Application Support/MnemoPictograms/{childScope}/{itemId}.png` + `index.json` |
| B10 iCloud KVS | `NSUbiquitousKeyValueStore` ≤ **1 MB** total; SRS payload — compact JSON, chunk or trim history |
| B14 phases | Lesson: optional WARMUP(0) / REFLECT(5); catalog banner: `MnemoAcademyPhase.catalogPhases` (4 dots) |
| B9 lock UITest | `-UITestMnemoSemesterLocked` (DEBUG) |
| Micro-gate | `python3 scripts/child_localization_gate.py --prefix child_mnemo_` |

---

## AA) Брендинг «Академия памяти» — карта размещения и i18n

> **Главный бренд:** Академия памяти / Memory Academy  
> **Главный tagline (все возрасты):** Учимся запоминать с образами  
> **Второстепенные:** promise · superpower · smart memory (parent)

### AA.1 Где что показываем (UI map)

| Слой | RU | EN | Где в приложении | Ключ i18n |
|------|----|----|------------------|-----------|
| **Главный бренд** | Академия памяти | Memory Academy | Шапка каталога (eyebrow), onboarding | `child_mnemo_brand_title_{age}` |
| **Главный tagline** | Учимся запоминать с образами | Learning to remember with images | Шапка каталога, academy banner | `child_mnemo_brand_tagline_{age}` |
| **Promise** | Не зубрёжка — умение вспоминать | Not cramming — real recall skills | Academy banner, parent footer | `child_mnemo_brand_promise` |
| **Superpower title** | Суперсила памяти | Memory Superpower | Banner, rewards, level-up | `child_mnemo_brand_superpower_title` |
| **Superpower toast** | Твоя суперсила памяти растёт! | Your memory superpower is growing! | REWARD phase, level-up | `child_mnemo_brand_superpower_toast` |
| **Accent × age** | см. §AA.2 | см. §AA.2 | Banner, catalog greeting | `child_mnemo_brand_accent_{age}` |
| **Smart Memory** | Умная память | Smart Memory | Parent dashboard title | `parent_mnemo_brand_smart_title` |
| **Neuro-soft** | Тренировка памяти по научным методам | Memory training backed by science | Parent subtitle | `parent_mnemo_brand_smart_subtitle` |
| **Onboarding** | Академия памяти + desc | Memory Academy + desc | OB page 5 kids (optional) | `onboarding_mnemo_academy_*` |

**Не меняем:** кнопки категорий (`child_mnemo_label_*`) — «Песни-память», «Игры памяти» и т.д.

### AA.2 Точные строки LocalizationManager (title + tagline × 4 возраста)

#### RU

| Ключ | kids 1–6 | school 7–12 | teen 13–17 | young 18–22 |
|------|----------|-------------|------------|-------------|
| `child_mnemo_brand_title_*` | Академия памяти | Академия памяти | Академия памяти | Академия памяти |
| `child_mnemo_brand_tagline_*` | Учимся запоминать с образами | Учимся запоминать с образами | Учимся запоминать с образами | Учимся запоминать с образами |
| `child_mnemo_brand_accent_*` | Песни, рифмы и яркие образы | Тренируй суперсилу каждый день | Полезно для школы и экзаменов | Навык запоминания на всю жизнь |

**Общие RU:**
- `child_mnemo_brand_promise` → `Не зубрёжка — умение вспоминать`
- `child_mnemo_brand_superpower_title` → `Суперсила памяти`
- `child_mnemo_brand_superpower_toast` → `Твоя суперсила памяти растёт!`
- `parent_mnemo_brand_smart_title` → `Умная память`
- `parent_mnemo_brand_smart_subtitle` → `Тренировка памяти по научным методам`
- `onboarding_mnemo_academy_title` → `Академия памяти`
- `onboarding_mnemo_academy_desc` → `Учимся запоминать с образами. Не зубрёжка — умение вспоминать. Научные методы: образ, якорь, интервальное повторение.`

#### EN

| Key | kids | school | teen | young adult |
|-----|------|--------|------|-------------|
| `child_mnemo_brand_title_*` | Memory Academy | Memory Academy | Memory Academy | Memory Academy |
| `child_mnemo_brand_tagline_*` | Learning to remember with images | Learning to remember with images | Learning to remember with images | Learning to remember with images |
| `child_mnemo_brand_accent_*` | Songs, rhymes, and vivid images | Train your superpower every day | Helpful for school and exams | A lifelong memory skill |

**Shared EN:**
- `child_mnemo_brand_promise` → `Not cramming — real recall skills`
- `child_mnemo_brand_superpower_title` → `Memory Superpower`
- `child_mnemo_brand_superpower_toast` → `Your memory superpower is growing!`
- `parent_mnemo_brand_smart_title` → `Smart Memory`
- `parent_mnemo_brand_smart_subtitle` → `Memory training backed by science`
- `onboarding_mnemo_academy_title` → `Memory Academy`
- `onboarding_mnemo_academy_desc` → `Learn to remember with images. Not cramming — real recall. Science-backed steps: image, anchor, spaced review.`

### AA.3 Иерархия текста в шапке каталога (mnemo)

```
[возраст chip]
Академия памяти          ← brand title (eyebrow, yellow)
Песни-память             ← category label (bold)
Учимся запоминать с образами  ← brand tagline
Рифма и образ            ← technique subtitle (lighter)
```

### AA.4 Academy banner (внутри каталога)

```
Учимся запоминать с образами     ← tagline
Не зубрёжка — умение вспоминать  ← promise
{accent по возрасту}             ← superpower hint
Суперсила памяти                 ← superpower title
Ассоциация · Воображение · Место ← AIM
[● ● ● ●] фазы
Сегодня повтори: N               ← SRS
```

### AA.5 Parent dashboard

```
Умная память                              ← Smart Memory
Тренировка памяти по научным методам      ← neuro-soft
Прогресс: 42%
Чемпион памяти
Не зубрёжка — умение вспоминать           ← promise (trust)
```

### AA.6 Код — MnemoBrandChrome

Файл: `Core/Content/Mnemonics/MnemoCategoryChrome.swift` — enum `MnemoBrandChrome`.

---

## Z) Roadmap — календарный порядок (ничего не забыть)

```
Фаза 1 — v2 MVP (сейчас)
├── B1C brand (T07–T08 pending)
├── B1-T06 gate
├── B2-T06–T07 wire + tests
├── B3 games.05 palace drill
├── B4 study 4 phases + 30 subjects
├── B5–B6 recall engines all ages
├── B7 rewards + parent basic
└── B8 F1–F10 QA

Фаза 2 — v3 Critical (параллельно с B4+)
└── B10 SRS v2 + push + deeplink  ← без этого курс «умирает»

Фаза 3 — v3 Curriculum
├── B9 Curriculum Spine + semantic palace
├── B12 Baseline MQ + Capstone + Championship
├── B13 Мнемотаблица
└── B11 Co-created pictograms

Фаза 4 — v3 Polish
├── B14 Parent guide + meta + emotions + hints
└── B15 F1–F15 final QA
```

**Master doc:** `docs/MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md` (v2.3)
