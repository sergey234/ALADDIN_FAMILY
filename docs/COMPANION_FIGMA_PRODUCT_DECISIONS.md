# Companion Figma — решения продукта (2026-05-26)

## Не трогаем

| Что | Файл | Страница |
|-----|------|----------|
| OB_00 … OB_07 | `KvkUdyb5Ll31Z9FSzCbpNl` | `OnboardingHero_00` |
| 2 макета Apple / логотип | тот же файл | `APP_AppStoreIcon_*` |

Только просмотр (скриншот, metadata). **Не удалять** ничего в этом файле.

## Companion HERO-3

| Решение | Значение |
|---------|----------|
| Где рисуем | **Новый отдельный** Figma-файл `Companion / Heroes` |
| Джин | Главный референс — **OB_02** (онбординг, read-only) |
| Сетка 02 | **12 фреймов** на героя = сценарии **CX.4** |
| 13 имён в коде | Rive input `emotion` + фазы; **speaking** в Motion Spec, не 13-й столбец в сетке |
| Sign-off 17 | Подписывает **вы** (владелец продукта) |
| **Conversation UI** | Grok Companions: **прямоугольная full-body сцена** ~56% высоты, **субтитр** снизу (`CompanionDialogueStrip`) |
| **Сцена** | `conversationFullBody` — **без круг-маски**; Hub — круг 96 pt |
| **Rive artboard** | **360×480 pt** (`CompanionHeroLayout.riveArtboardSize`) — bust/full-body |
| **Фон сцены** | `stageBackground` по герою (OB_01 / OB_02 / OB_05) + эмоция |
| **Диалог** | Крупный субтитр последнего ответа + «Вся история» (не лента пузырей) |

### Grok parity — статус (2026-05-26)

| Gap | Статус |
|-----|--------|
| Крупная сцена ~56% | ✅ `CompanionHeroLayout` |
| Прямоугольник full-body (не круг) | ✅ `conversationFullBody` |
| Фон/lighting по герою | ✅ `stageBackground` + floor glow |
| Субтитр вместо чата | ✅ `CompanionDialogueStrip` |
| 3D Rive вместо emoji | ⏳ **HERO-3-07** `.riv` ×3 |
| Финальный art OB_01/02/05 | ⏳ Figma/Rive после **07** |
| Lip-sync production | ⏳ **08** + TTS |
| QA MOTION/MIMIC | ⏳ **11** |

### 2D Rive vs настоящий 3D

**Полный ADR + таблицы + sign-off:** [COMPANION_2D_VS_3D_ADR.md](./COMPANION_2D_VS_3D_ADR.md)  
**Export HERO-3-07:** [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md)

<details><summary>Краткая выжимка (2026-05-26)</summary>

| | **Онбординг OB_00–07** | **Grok Ani** | **Companion HERO-3-07** |
|--|------------------------|--------------|-------------------------|
| Формат | **2D** PNG/Lottie, full-bleed иллюстрации | **3D** (pre-rendered motion) | **2D Rive** `.riv` (не SceneKit/USDZ) |
| Герои на экранах | 8 **сюжетных** кадров, не 3 ID | 1 companion | **3 ID:** unicorn, aladdin, genie |
| Референсы | OB_01 человек · OB_02/07 джин · OB_05 kids mood | — | Тот же **иллюстративный** стиль |

**Вывод:** **HERO-3-07 = 2D анимация в Rive** (bust/full-body 360×480), визуально в линии с онбордингом. Настоящий 3D — отдельный проект (IPA, пайплайн, детский бренд), не цель спринта.

</details>

---

## Простыми словами: 12 vs 13

**12 (для макетов Figma 02)** — это **12 разных «лиц» по ситуации в чате**, как в таблице CX.4:

- грустно → грустное лицо  
- шутка → весёлое  
- угроза → серьёзное  
- слушает микрофон → внимательное  
- думает → задумчивое  
- и т.д.

Дизайнер рисует **12 картинок на каждого героя** (единорог, человек, джин) = **36 фреймов**. Этого достаточно, чтобы продукт и QA понимали «герой меняется под настроение».

**13 (в коде и Rive)** — это **технический полный список** имён, которые приложение умеет переключать. Там же есть **`speaking`** — «сейчас говорит вслух» (рот открыт, lip-sync). В таблице CX.4 это описано как **фаза**, а не как «ещё одно настроение типа грусти/радости».

**Итог для нас:** в Figma сетке **02 рисуем 12**. Тринадцатое состояние **`speaking`** не добавляем 13-м столбцом — его правила (рот, `mouth_open`) живут в **Motion Spec (17)**. В Rive всё равно будет 13 inputs — дизайнер закладывает это в Motion, не в 13 отдельных постеров.

---

## Простыми словами: Sign-off 17 (HERO-3-17)

Это **не код и не TestFlight**. Это **ваше «ОК, можно рисовать 36 макетов»**.

Перед задачей **02** вы (как продукт/дизайн-владелец) проверяете в Figma страницу **`00_Spec`**:

1. Понятно ли, как герой **слушает / думает / говорит** (§2.2 Motion)?  
2. Понятно ли **брови, глаза, рот** для грусти, шутки, тревоги (§2.3 Mimic)?  
3. Согласны ли, что у **джина** стиль от **OB_02**, у human — OB_01, без 🧞 у человека?

Ставите галочки в [`COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md`](./COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md) (или в Sign-off фрейме в новом файле).

**Пока sign-off не стоит** — агент **не** рисует 3×12 (02), чтобы не переделывать 36 экранов.

**Кто подписывает:** **вы** (пользователь / владелец продукта).

---

## Figma-файл Companion (создан 2026-05-26)

| Поле | Значение |
|------|----------|
| **Имя** | Companion / Heroes |
| **URL** | https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM |
| **fileKey** | `vwKcGPUUEZjgayEHNn0BJM` |
| **Env** | [`FIGMA_COMPANION.env`](./FIGMA_COMPANION.env) |

**Страница `00_Spec`:** ADR · Motion wireframe · Mimic 12× · REF OB_01/02/05 · Sign-off · блок **02_LOCKED**.

Онбординг **не изменён:** `KvkUdyb5Ll31Z9FSzCbpNl`.

---

## Следующий шаг

1. ~~create_new_file + 00_Spec~~ ✅  
2. **Вы** — sign-off в Figma + [`COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md`](./COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md)  
3. После sign-off → **02** (3×12) в **этом** файле  
4. Export **07** + **22** + device QA
