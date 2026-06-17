# Handoff: оживить героев + убрать тормоза + пройти QA

**Для:** следующая ML-система / агент  
**Дата:** 2026-06-17  
**Репозиторий:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Ветка:** `master`  
**Текущий билд в проде (TestFlight):** **239**  
**Цель билда:** **240** (или следующий) с исправлениями

---

## 0. Задача одной фразой

Сделать так, чтобы на **реальном iPhone** (не iOS 15 simulator) все **3 героя** на экране **«Мир героев»** **заметно** двигались (мимика + idle), приложение **не тормозило** и **не падало** watchdog'ом. Проверить всё по чеклисту в конце файла.

---

## 1. Что сломано сейчас (факты, не догадки)

| Проблема | Доказательство |
|----------|----------------|
| Герои выглядят как статичный PNG | Скрин пользователя: белые полосы сверху/снизу = `scaledToFit` / Rive `contain` |
| Краши на device | `ALADDIN-2026-06-17-220058.ips`, `220433.ips` — **0x8BADF00D** watchdog, main thread в `NSDictionary(contentsOf:)` + `ScrollView.body` |
| Тормоза на всех экранах | `LocalizationManager.localized()` читал `.strings` с диска **на каждый ключ** |
| Только unicorn частично готов | `unicorn.riv` — Face ✅; `aladdin.riv` / `genie.riv` — **Face ❌** (старый PNG-patch 4 июн) |
| AI офлайн на скрине | Баннер «Умный помощник офлайн» → `heroEmotion` = `idle`, lip-sync = 0 |
| Ожидание Grok-3D нереалистично | ADR: **2D Rive**, тело = PNG, двигается **лицо**, не весь персонаж |

---

## 2. Карта файлов (куда лезть)

```
mobile_apps/ALADDIN_iOS/
├── Resources/Companion/
│   ├── unicorn.riv          ← golden (160 KB, Face ✅)
│   ├── aladdin.riv          ← старый patch, Face ❌
│   ├── genie.riv            ← старый patch, Face ❌
│   ├── unicorn_master.png
│   ├── aladdin_master.png
│   └── genie_master.png
├── UI/Companion/
│   ├── CompanionHeroAvatarView.swift    ← маршрут PNG / Rive / emoji
│   ├── CompanionHeroRiveHost.swift      ← загрузка .riv, inputs, fallback
│   ├── CompanionHeroRasterView.swift    ← PNG fallback + слабый bob
│   └── CompanionHeroAnimatedView.swift  ← emoji fallback
├── Core/Localization/LocalizationManager.swift  ← тормоза + watchdog
├── Screens/CompanionConversationScreen.swift    ← heroEmotion, lipSync
├── scripts/
│   ├── companion_07_verify_unicorn_riv.py
│   ├── companion_07_automated_pipeline.sh
│   └── verify_companion_rive_ios_bundle.sh
└── docs/
    ├── COMPANION_08B_DEVICE_CHECKLIST.md
    └── COMPANION_2D_VS_3D_ADR.md
```

**SPM:** `RiveRuntime` подключён в `ALADDIN.xcodeproj`  
**Бандл:** папка `Resources/Companion/` целиком в Copy Bundle Resources (`Companion in Resources`)

---

## 3. Как приложение выбирает PNG или Rive

Читай `CompanionHeroAvatarView.heroCore`:

```
if shouldUseRasterMaster → CompanionHeroRasterView (PNG)
else if shouldAttemptRiveRuntime → CompanionHeroRiveRuntimeView (Rive)
else → CompanionHeroAnimatedView (emoji)
```

**Rive включается только если:**
1. `unicorn.riv` (или aladdin/genie) **≥ 25 000 байт**
2. Не симулятор iOS 15.x
3. `makeRiveViewModel()` вернул не-nil (artboard `Hero360`, SM `HeroSM`)

**Если Rive VM = nil** → тихий fallback на PNG (выглядит как «ничего не двигается»).

---

## 4. План работ — 6 фаз

Выполнять **по порядку**. Не переходить к следующей фазе, пока не PASS критерии текущей.

---

### ФАЗА 1 — Производительность и краши (P0, блокер)

**Зачем:** без этого UI зависает, watchdog убивает приложение, `TimelineView` не тикает → герои «мертвые».

#### 1.1 Кэш локализации

**Файл:** `Core/Localization/LocalizationManager.swift`

**Было:** `localizedFromBundle` вызывал `NSDictionary(contentsOfFile:)` на каждый ключ.  
**Нужно:**
- `ensureBundleTableLoaded(for:)` — один раз читать весь `Localizable.strings` на язык
- `warmBundleTablesAtLaunch()` в `init()` — прогреть `currentLanguage`, `ru`, `en`

**Проверка:**
```bash
cd mobile_apps/ALADDIN_iOS
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN \
  -destination 'generic/platform=iOS' build
```
- Открыть любой экран со `ScrollView` (Настройки, Мир героев) — **нет** зависания 5+ сек
- Повторить краш-сценарий на device — **нет** нового `.ips` с `0x8BADF00D` + `parsePlistDictContent`

#### 1.2 Rive inputs (не спамить trigger)

**Файл:** `UI/Companion/CompanionHeroRiveHost.swift`

**Было (билд 239):** emotion trigger **каждый кадр** 30 fps.  
**Нужно:**
- `applyRiveEmotionTrigger` — только `onAppear` + `onChange(emotion)`
- `applyRiveMouthOnly` — на `mouthQuantized` (16 шагов)
- `TimelineView` — 20 fps, не 30
- Кэш `RiveViewModel` в `CompanionRiveViewModelHolder`

**Проверка:** Instruments / глазами — CPU на экране героя ниже, чем на 239.

---

### ФАЗА 2 — Диагностика RIVE vs PNG (P0)

**Зачем:** понять, почему на device «как PNG».

#### 2.1 DEBUG-бейдж (уже частично в коде)

**Файлы:** `CompanionHeroRiveHost.swift`, `CompanionHeroRasterView.swift`

- Зелёный: `RIVE unicorn` — Rive реально рисуется
- Оранжевый: `PNG fallback` / `PNG placeholder-riv` / `PNG iOS15-sim`

#### 2.2 Release-лог (добавить агенту)

**Добавить** одну строку `os_log` / `print` при старте сцены героя:
```
[CompanionHero] path=RIVE|PNG character=unicorn rivBytes=160543 vm=ok|nil
```

**Проверка на iPhone:**
- Debug-сборка → виден бейдж
- Release → в Console.app фильтр `CompanionHero`

**PASS:** на iPhone iOS 16+ с production `.riv` лог показывает `path=RIVE vm=ok`.

**FAIL:** `path=PNG vm=nil` → идти в Фазу 3 (починить загрузку VM).

---

### ФАЗА 3 — Ассеты Rive: unicorn эталон → aladdin + genie (P0)

**Зачем:** aladdin/genie сейчас **без Face** — даже при Rive это статичная картинка.

#### 3.0 Бэкап (обязательно)

```bash
cd mobile_apps/ALADDIN_iOS
mkdir -p backups/$(date +%Y-%m-%d)
cp Resources/Companion/*.riv Resources/Companion/*.rev backups/$(date +%Y-%m-%d)/ 2>/dev/null || true
```

#### 3.1 Эталон unicorn (уже есть)

```bash
python3 scripts/companion_07_verify_unicorn_riv.py unicorn
# Ожидание: PASS, ≥25000 bytes, HeroSM, mouth_open, 13 triggers, PNG внутри
```

Дополнительно проверить строки в файле:
```bash
python3 -c "
d=open('Resources/Companion/unicorn.riv','rb').read().decode('latin1')
for s in ['Face','brow','mouth','blush','Hero360','HeroSM','mouth_open']:
    print(s, s in d)
"
```

#### 3.2 Клонировать unicorn → aladdin

**В Rive Editor / RiveMCP:**
1. Открыть `unicorn_golden.rev` или `unicorn.riv` (source)
2. Duplicate → заменить PNG body на `aladdin_master.png` (360×480)
3. Сохранить Face-группу, HeroSM, 13 triggers, `mouth_open`
4. Подкрутить цвета blush/sparkle под Аладдина
5. Export → `Resources/Companion/aladdin.riv`

**Проверка:**
```bash
python3 scripts/companion_07_verify_unicorn_riv.py aladdin
# + Face must be True:
python3 -c "d=open('Resources/Companion/aladdin.riv','rb').read().decode('latin1'); print('Face', 'Face' in d)"
```

#### 3.3 Клонировать unicorn → genie

То же, body = `genie_master.png`.  
Искры/дым — только на `playful` / `speaking` (GATE-MIMIC-2).

```bash
python3 scripts/companion_07_verify_unicorn_riv.py genie
```

#### 3.4 Заморозить source

```bash
cp Resources/Companion/aladdin.riv Resources/Companion/aladdin_golden.rev
cp Resources/Companion/genie.riv Resources/Companion/genie_golden.rev
```

#### 3.5 Усилить видимость мимики (если «не видно»)

В Rive Editor для **всех 3 героев:**
- `idle` — loop: лёгкое движение глаз/бровей (амплитуда **≥ 8–12 px** на artboard 360×480)
- `speaking` — рот + `mouth_open` 0→1
- `happy` / `playful` — заметный сдвиг бровей и рта

**Не делать:** перерисовывать тело в 3D — только Face-слои.

---

### ФАЗА 4 — iOS код: заметное движение даже в fallback (P1)

**Зачем:** если Rive снова упадёт, пользователь всё равно видит жизнь.

#### 4.1 PNG fallback — усилить idle

**Файл:** `CompanionHeroRasterView.swift`

- Увеличить `emotionBobOffset` для `.idle` на full-body (с 3 pt → **6–10 pt**)
- Добавить едва заметный «breathing» scale 1.0↔1.02 на idle
- Опционально: лёгкое мерцание глаз (overlay), если PNG-path

#### 4.2 Rive — idle loop без AI

**Файл:** `CompanionHeroRiveHost.swift`

- На `onAppear` всегда `applyRiveEmotionTrigger(.idle)` 
- Убедиться, что в `.riv` анимация `idle` — **loop** в state, не one-shot

#### 4.3 Release-диагностика пути

См. 2.2 — обязательно для TestFlight.

---

### ФАЗА 5 — Сборка, билд 240, TestFlight (P0)

#### 5.1 Bump версии

Обновить **везде одинаково** `239` → `240`:
- `Core/Config/AppConfig.swift` (`buildNumber`, `minimumClientBuildForApiContract`)
- `Info.plist`, `ALADDINCallDirectory/Info.plist`
- `ALADDIN.xcodeproj/project.pbxproj` (все `CURRENT_PROJECT_VERSION`)

#### 5.2 Автопроверки перед коммитом

```bash
cd mobile_apps/ALADDIN_iOS
./scripts/verify_companion_rive_ios_bundle.sh
python3 scripts/companion_07_verify_unicorn_riv.py unicorn
python3 scripts/companion_07_verify_unicorn_riv.py aladdin
python3 scripts/companion_07_verify_unicorn_riv.py genie
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN \
  -destination 'generic/platform=iOS' build
# Юнит-тесты по возможности:
xcodebuild test -project ALADDIN.xcodeproj -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -only-testing:ALADDINTests/CompanionStreamEmotionDebouncerTests 2>/dev/null || true
```

#### 5.3 Коммит (только по запросу пользователя)

```
feat(ios): build 240 — hero Rive mimic visible, l10n cache, perf fixes
```

**Не коммитить:** `.env`, ключи API, `telegram_stars_shop_bot/*`, `xcuserdata`.

#### 5.4 Push / TestFlight

По правилам репо — push `master` только если пользователь просит.

---

### ФАЗА 6 — QA на устройстве (обязательный финал)

Использовать `docs/COMPANION_08B_DEVICE_CHECKLIST.md` + таблицу ниже.

**Устройство:** реальный iPhone, **iOS 16+**, **не** Low Power Mode, устройство **не перегрето**.

| # | Шаг | Ожидание | PASS |
|---|-----|----------|------|
| Q1 | Открыть «Мир героев» → Единорог | Лог/бейдж `RIVE` | ☐ |
| Q2 | Смотреть 10 сек без чата | Заметное движение лица/idle loop | ☐ |
| Q3 | Написать «Привет!» (AI онлайн) | thinking → speaking → happy, рот шевелится | ☐ |
| Q4 | Переключить Аладдин, Джин | То же, у каждого Face-анимация | ☐ |
| Q5 | Прокрутить чат, сменить вкладки | Нет фриза 5+ сек, нет краша | ☐ |
| Q6 | 13 эмоций (MIMIC-Q) | Различимы минимум 8/13 на unicorn | ☐ |
| Q7 | Hub 96pt thumbnail | Круглая сцена, мимика видна | ☐ |
| Q8 | TTS / mouth_open ≥ 1 сек | Рот открыт при speaking | ☐ |

**MIMIC-Q (быстрый):** вручную или через debug-кнопки прогнать emotions:  
`idle, happy, sad, speaking, listening, thinking, playful, alert` — каждая **визуально отличается**.

**Протокол:** заполнить таблицу в `COMPANION_08B_DEVICE_CHECKLIST.md`.

---

## 5. TODO-лист для агента (копировать в трекер)

```
ФАЗА 0 — Подготовка
[ ] 0.1  git pull, cwd = mobile_apps/ALADDIN_iOS
[ ] 0.2  Бэкап Resources/Companion/*.riv → backups/YYYY-MM-DD/
[ ] 0.3  Прочитать CompanionHeroAvatarView + CompanionHeroRiveHost

ФАЗА 1 — Perf / crashes (P0)
[ ] 1.1  LocalizationManager: кэш bundle tables + warm at launch
[ ] 1.2  CompanionHeroRiveHost: emotion trigger только onChange, mouth quantized
[ ] 1.3  xcodebuild PASS
[ ] 1.4  Smoke: ScrollView экраны не зависают

ФАЗА 2 — Диагностика
[ ] 2.1  DEBUG бейдж RIVE/PNG на device
[ ] 2.2  Release os_log [CompanionHero] path=...
[ ] 2.3  Зафиксировать в отчёте: RIVE или PNG на iPhone пользователя

ФАЗА 3 — Rive ассеты (P0)
[ ] 3.1  verify unicorn PASS + Face=True
[ ] 3.2  Клон unicorn → aladdin.riv + Face + 13 triggers
[ ] 3.3  Клон unicorn → genie.riv + Face + 13 triggers
[ ] 3.4  Усилить keyframes idle/speaking (амплитуда видна)
[ ] 3.5  verify aladdin + genie PASS
[ ] 3.6  Заморозить *_golden.rev

ФАЗА 4 — iOS polish (P1)
[ ] 4.1  Усилить idle bob на PNG fallback
[ ] 4.2  idle loop в Rive onAppear
[ ] 4.3  verify_companion_rive_ios_bundle.sh PASS

ФАЗА 5 — Релиз
[ ] 5.1  Bump 239 → 240 (AppConfig, plist, pbxproj)
[ ] 5.2  Полный build + verify scripts
[ ] 5.3  Коммит (если пользователь просит)
[ ] 5.4  TestFlight (если пользователь просит)

ФАЗА 6 — Device QA
[ ] 6.1  COMPANION_08B_DEVICE_CHECKLIST заполнен
[ ] 6.2  Q1–Q8 PASS на iPhone
[ ] 6.3  MIMIC-Q 8/13 emotions различимы × 3 героя
[ ] 6.4  Отчёт пользователю: что было / что сделано / скрины
```

---

## 6. Что НЕ делать

| ❌ | Почему |
|----|--------|
| Grok-3D / SceneKit / USDZ | Вне ADR, месяцы работы |
| QA Rive только на iOS 15.2 Simulator | Rive отключён намеренно |
| Перезаписывать `unicorn.riv` черновиком MCP без verify | Уже был сломанный бэкап |
| `load_riv` → re-export в одной MCP-сессии | Ломает контракт (история проекта) |
| Коммитить API-ключи, `.env` | Секреты |
| Упоминать удалённый `unicorn_broken_288kb.riv` | Пользователь просил забыть |

---

## 7. Контракт .riv (обязательные строки в файле)

| Поле | Значение |
|------|----------|
| Artboard | `Hero360` (360×480) |
| State Machine | `HeroSM` |
| Number input | `mouth_open` |
| Triggers (13) | idle, listening, thinking, speaking, happy, playful, sad, comfort, celebrate, curious, nostalgic, excited, alert |
| Face group | brow, mouth, blush, tear, sparkle (для production) |
| Min size | 25 000 bytes |
| Max size | 500 000 bytes (gate) |

**Verify:**
```bash
python3 scripts/companion_07_verify_unicorn_riv.py <unicorn|aladdin|genie>
```

---

## 8. Связь emotion в приложении и Rive

| App `CompanionHeroEmotion` | Rive trigger |
|----------------------------|--------------|
| idle | idle |
| happy | happy |
| listening | listening |
| speaking | speaking |
| … | см. `CompanionHeroRiveMapping.riveStateName` |

**Lip-sync:** `CompanionHeroLipSync.proceduralMouthOpen` → `mouth_open` 0…1  
Активен когда `emotion == .speaking` **или** `lipSyncPhase > 0`.

**Если AI офлайн:** emotion остаётся `idle` → рот не двигается. Для QA включить AI или добавить debug-кнопку «test speaking».

---

## 9. Локальные незакоммиченные правки (проверить агенту)

Возможно уже есть в рабочей копии (сессия 2026-06-17):
- `LocalizationManager.swift` — кэш bundle
- `CompanionHeroRiveHost.swift` — Rive inputs fix
- `CompanionHeroRasterView.swift` — DEBUG badge

**Действие:** `git status` → если есть — включить в билд 240, не дублировать.

---

## 10. Критерий «ГОТОВО» для пользователя

1. **Билд 240** на TestFlight  
2. На **iPhone SE2 / аналог** герои **видимо** двигаются в idle без чата  
3. При speaking — рот ≥ 1 сек  
4. Все 3 героя с Face-анимацией  
5. Нет watchdog-крашей при скролле  
6. Скрин + заполненный QA-протокол приложены к отчёту  

---

## 11. Шаблон отчёта агенту (заполнить в конце)

```markdown
## Отчёт HERO Animation Fix

- Билд: 240
- Устройство: iPhone ___, iOS ___
- Путь рендера: RIVE / PNG (почему)
- unicorn / aladdin / genie verify: PASS/FAIL
- Q1–Q8: ...
- MIMIC-Q: _/13 на unicorn, _/13 aladdin, _/13 genie
- Perf: ScrollView ок / не ок
- Краши: нет / приложить .ips
- Скрины: [idle] [speaking] [happy]
- Коммит: hash
```

---

*Конец handoff. Начинать с Фазы 1, не пропускать verify-скрипты.*
