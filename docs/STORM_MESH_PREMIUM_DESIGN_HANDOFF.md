# ALADDIN iOS — Storm Mesh Premium Design System
## Handoff для ML-систем / агента Cursor

**Версия:** 1.2  
**Дата:** 2026-06-09 (обновлено: SCREEN-SAFE gate, Batch 9, продукт 5 столпов, Wellness split)  
**Репозиторий (единственный рабочий корень):**  
`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

**Проверка перед работой:**
```bash
git rev-parse --show-toplevel
git branch --show-current
git status --short
```

---

## 1. Executive Summary (что решили)

### 1.1 Цель
Привести **~20+ основных in-app экранов** к единому **premium** визуальному стилю «**Грозовое небо + золото**» (Storm + Gold), **не меняя**:
- тексты и localization keys;
- бизнес-логику, ViewModels, NavigationManager;
- accessibility identifiers (UITests);
- **экран онбординга `14_OnboardingScreen.swift`** — **полностью без изменений**.

### 1.2 Что меняем
| Меняем | Не меняем |
|--------|-----------|
| Фон экранов (mesh gradient) | Copy / localized strings |
| «Хром» карточек (glass + stroke + shadow) | Структура navigation |
| Accent strip 3pt на shield-экранах (статус) | Onboarding heroes + Figma OB_00–07 |
| Единые color tokens в `Colors.swift` | Subscription / family API logic |

### 1.3 Референсы (внешние ресурсы)
| Ресурс | Роль | Что берём | Что НЕ копируем |
|--------|------|-----------|-----------------|
| **Lazyweb** | UX in-app (250k+ экранов apps) | Паттерны фона, glass cards, иерархия hub/paywall/parental | Layout чужих apps 1:1 |
| **before.click** | App Store screenshot gallery | Палитра dark + gold, tone «доверие», ASO storyboard | Store-layout внутри app |

### 1.4 Продуктовый narrative
> «Гроза прошла — дом под золотым светом.»

ALADDIN — **не только security**. **Пять столпов продукта:**
- **Shield** — VPN, антивирус, устройства;
- **Family** — семья, чат, тарифы;
- **Grow** — родконтроль, воспитание;
- **Play** — игры, награды, геймификация детей;
- **Learn** — обучение, security education, young defender.

Mesh-variants отражают все пять (см. §4, §5 Batch 9).

---

## 1.5 ЧТО МЫ ДЕЛАЕМ (кратко — прочитать первым)

> **Онбординг (`14_OnboardingScreen.swift`) — НЕ ТРОГАЕМ.**  
> **Все тексты, localization keys, navigation, ViewModels — НЕ ТРОГАЕМ.**  
> Меняем только **визуальную оболочку**: фон + стекло на карточках.

### Список работ (по порядку)

| # | Что делаем | Файлы / Batch | Обязательно? |
|---|------------|---------------|--------------|
| 1 | Storm color tokens (`stormBase`, gold, teal…) | `Colors.swift` — **Batch 0** | ✅ Да |
| 2 | Компонент mesh-фона (11 variants) | `StormMeshBackground.swift` — **Batch 0** | ✅ Да |
| 3 | Компонент glass-карточек | `StormGlassCardStyle.swift` — **Batch 0** | ✅ Да |
| 4 | Подключить mesh на **20+ экранов** (см. §4) | **Batch 1–5** | ✅ Да |
| 5 | Glass + gold stroke на всех интерактивных карточках | **Batch 6** | ✅ **Да для 95% Premium** |
| 6 | Accent strip 3pt на shield-экранах (VPN, devices) | **Batch 6** | ✅ Да |
| 7 | QA: SE, Pro Max, onboarding→Main, контраст | **Batch 7** | ✅ Да |
| 8 | ASO 6 скринов в палитре `.hub` | **Batch 8** | ✅ Да для 100% бренда |
| 9 | Companion + Wellness + Games + Settings sub-screens + flows | **Batch 9** | ✅ **Да — иначе «швы» −10–15%** |
| — | Onboarding OB_00–07 | — | ❌ **Freeze** |

**Перед КАЖДЫМ экраном:** обязательный **SCREEN-SAFE Gate** — см. **§1.7** (ничего не сместилось, текст на месте, читаем).

**Формула Lazyweb + before.click → ALADDIN:** см. **§9.1–9.2** (обязательно для агента).

### Что НЕ входит в этот проект

- Смена текстов / copy / тарифных названий
- Редизайн layout (порядок блоков, новые кнопки)
- Emoji → SF Symbols (отдельная задача)
- Paywall logic (сколько планов показывать — отдельная задача)
- Изменения Figma онбординга

---

## 1.6 Будет ли Premium после 100% реализации?

### Короткий ответ

| Вопрос | Ответ |
|--------|--------|
| Будет ли premium после **всех** batch 0–9 + 8? | **Да** |
| Без Batch 9 (Companion/Wellness/Games)? | **Швы** — минус 10–15% целостности |
| Достаточно ли **только** mesh-фона (Batch 1–5 без Batch 6)? | **Нет** — будет «красивый фон», но не full premium (**~78%**) |
| Нужен ли Batch 6 (glass на карточках)? | **Да, обязателен** для **~95% premium** |
| Нужен ли Batch 8 (ASO)? | **Да** для ощущения «один бренд» Store ↔ app (**~100%**) |

### Шкала Premium — что видит пользователь

| Этап | Batches | Что сделано | Что видит пользователь | Premium |
|------|---------|-------------|------------------------|---------|
| **A** | Только **0** | Tokens + компоненты, экраны не тронуты | Без изменений | baseline |
| **B** | **1–5** | Mesh-фон на 20+ экранах; карточки **старые** (flat `white 10%`) | «Красивое небо, но карточки плоские» | **~78%** |
| **C** | **+ Batch 6** | Mesh + **glass** + gold stroke + shadow + accent strips | «Дорогое семейное приложение» (Revolut / Aura / Life360) | **~95%** |
| **D** | **+ Batch 7** | QA: контраст, blur, onboarding→Main | Стабильный premium на всех iPhone | **~95% verified** |
| **E** | **+ Batch 9** | Все «хвостовые» экраны (Companion, Wellness, Games…) | Нет старых gradient в углу app | **~95% full app** |
| **F** | **+ Batch 8** | ASO 6 скринов в storm+gold | Установка и app — **один бренд** | **~100% brand** |

### Визуальная формула Premium

```
Premium =
  Storm Mesh фон     (Batch 1–5)
+ Glass карточки     (Batch 6)     ← БЕЗ ЭТОГО НЕ PREMIUM, только «красивый фон» (~78%)
+ Единые цвета       (Batch 0–6)
+ QA                 (Batch 7)
+ Все хвостовые экраны (Batch 9)  ← без швов Companion/Wellness/Games
+ ASO = те же цвета  (Batch 8)     ← мост App Store ↔ приложение (~100% brand)
+ Onboarding freeze                  ← wow-вход сохранён (9/10)
+ SCREEN-SAFE Gate на каждом экране ← тексты/карточки не сдвинулись (§1.7)
```

### Definition: «100% реализация»

Проект **завершён на 100%**, когда:

- [x] Batch 0 — foundation  
- [x] Batch 1–5 — mesh на каждом экране из §4  
- [x] **Batch 6 — glass на карточках (НЕ ПРОПУСКАТЬ)**  
- [x] **Batch 9 — все экраны из §4.1 (Companion, Wellness, Games, Settings sub)**  
- [x] Batch 7 — QA pass (включая iPad, Reduce Motion, grep всех Screens/)  
- [x] Batch 8 — ASO assets  
- [x] Каждый экран прошёл **SCREEN-SAFE Gate** (§1.7)  
- [x] `14_OnboardingScreen.swift` — **zero diff**

**Итог для пользователя:** premium семейное приложение (**защита + семья + воспитание + игры + обучение**), не «security app с ярким gradient».

---

## 1.7 SCREEN-SAFE Gate — ОБЯЗАТЕЛЬНО перед / после каждого экрана

> **Меняем ТОЛЬКО дизайн (фон + glass chrome).** AI-агент **не закрывает** batch по экрану, пока не пройден gate.

### 1.7.0 Baseline backup (создан 2026-06-09)

**Директория бэкапа всех рабочих файлов (79 шт.):**

```
/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/backups/STORM_MESH_PREMIUM_BASELINE_20260609/
```

- `MANIFEST.txt` — полный список
- `README.md` — как восстановить один файл или всё сразу
- Onboarding **не** в бэкапе (freeze)

### 1.7.1 Перед изменениями (PRE)

```bash
# 0. При сомнении — копия из baseline backup (см. §1.7.0)
# cp -p backups/STORM_MESH_PREMIUM_BASELINE_20260609/Screens/<File>.swift Screens/<File>.swift

# 1. Зафиксировать файл в git (сохранность)
git status --short -- Screens/<File>.swift
git diff -- Screens/<File>.swift   # должен быть пуст до начала

# 2. Baseline: что должно остаться (записать в отчёт batch)
# - количество Button / NavigationLink / accessibilityIdentifier
# - список localization keys (grep localized\()
# - порядок major VStack/HStack блоков (не менять порядок child views)
```

**Чеклист PRE (все ✅):**
- [ ] Файл существует, путь верный
- [ ] `git diff` на файл пуст перед правкой
- [ ] Прочитан `body` / `homeContent` — отмечены блоки: header, cards, lists, buttons
- [ ] Выписаны все `accessibilityIdentifier` — **нельзя удалять/менять**

### 1.7.2 Что разрешено менять (ALLOWLIST)

| Можно | Нельзя |
|-------|--------|
| Слой `StormMeshBackground(variant:)` вместо `LinearGradient` / flat color | `Text(...)`, strings, localization keys |
| `.modifier(StormGlassCardStyle())` на существующих card containers | `.font()`, `.padding()`, frame sizes, spacing |
| Замена `.fill(Color.white.opacity(0.1))` на glass modifier | Порядок карточек / секций в VStack |
| `accentStrip` 3pt на shield status | Navigation actions, ViewModel calls |
| `.accessibilityHidden(true)` только на decorative background | Удаление кнопок, карточек, полей |

### 1.7.3 После изменений (POST) — визуальная и кодовая проверка

**Код (обязательно):**
```bash
# Количество accessibilityIdentifier не уменьшилось
grep -c 'accessibilityIdentifier' Screens/<File>.swift  # сравнить с PRE

# Localization keys не удалены
grep -o 'localized("[^"]*"' Screens/<File>.swift | sort -u  # сравнить с PRE

# Не добавлены новые navigation routes
grep 'navigateTo' Screens/<File>.swift  # те же destinations

git diff Screens/<File>.swift  # только background + card chrome
```

**Визуально (симулятор):**
- [ ] Все карточки на месте — **ничего не пропало**
- [ ] Тексты **не обрезаны**, **не налезают** друг на друга
- [ ] Текст **читаем** на фоне (белый/светлый на storm + scrim)
- [ ] Кнопки на тех же местах, **кликабельны**
- [ ] Scroll работает, нижний контент не под tab bar
- [ ] Dynamic Type Medium — без обрезания критичных label

**Если POST fail → откатить файл:**
```bash
git checkout -- Screens/<File>.swift
```

### 1.7.4 Отчёт агента после каждого экрана (шаблон)

```markdown
## SCREEN-SAFE: <FileName>
PRE:  accessibility IDs: N → POST: N ✅
PRE:  localized keys: M → POST: M ✅
Diff: только StormMeshBackground + StormGlassCardStyle ✅
Visual: все карточки/тексты на месте, читаемость OK ✅
```

### 1.7.5 Читаемость текста (минимальные контрасты)

| Элемент | На storm mesh |
|---------|---------------|
| Primary text | `.white` или `textPrimary` |
| Secondary | `textSecondary` `#94A3B8` |
| На glass card | существующие цвета карточки + scrim снизу экрана |
| Legal screens | `.legal` flat — без blur |
| Если текст бледный | усилить **bottom scrim**, не менять font size |

При `accessibilityReduceMotion == true`: **отключить blur** на blobs (flat stormBase + лёгкий gradient).

### Onboarding vs остальные экраны

| Зона | Стиль | Premium-роль |
|------|-------|--------------|
| Onboarding OB_00–07 | Cinematic heroes (**freeze**) | Wow-вход |
| Main + 20 экранов | Storm mesh + glass | Calm premium (~95%) |
| App Store | `.hub` palette + real UI | Обещание = реальность (~100% brand) |

Переход OB_07 → Main: `stormBase #070B14` = тёмный scrim онбординга → **без белой вспышки**.

---

## 2. Design System — техническая спецификация

### 2.1 Новые файлы (создать в Фазе 0)

```
Shared/Styles/Colors.swift                    — дополнить storm tokens
Shared/Components/StormMeshBackground.swift — enum + View
Shared/Components/StormGlassCardStyle.swift   — ViewModifier
```

### 2.2 Color tokens (добавить в `Colors.swift`)

| Token | HEX | Swift name | Назначение |
|-------|-----|------------|------------|
| Storm base | `#070B14` | `stormBase` | Ночное небо — база всех mesh |
| Storm deep | `#0F172A` | `stormDeep` | = `backgroundDark` (алиас ok) |
| Storm cloud | `#1E293B` | `stormCloud` | Blob «облако» |
| Storm indigo | `#312E81` | `stormIndigo` | Грозовой indigo |
| Storm violet | `#4C1D95` | `stormViolet` | Семья / воспитание |
| Storm teal | `#0D9488` | `stormTeal` | Обучение детей (Grow) |
| Storm lightning | `#6366F1` | `stormLightning` | AI, analytics |
| Gold primary | `#F59E0B` | `goldPrimary` | = `secondaryGold` |
| Gold soft | `#F59E0B` @ 18% | `goldSoft` | Blob под header |
| Gold warm | `#D97706` | `goldWarm` | Elderly 60+ |
| Scrim bottom | `#070B14` @ 55% | — | LinearGradient снизу |

**Правило золота:** один blob на экран, opacity **12–22%**. Исключение: `.premium` до **22%**.

### 2.3 StormMeshBackground — API

```swift
enum StormMeshVariant {
    case hub          // Main, Support
    case family       // Family, FamilyChat, JoinDevice
    case shield       // Network, Devices, DeviceDetail, EnergyStats
    case grow         // Parental Control
    case growWarm     // Child Interface
    case warm         // Elderly 60+
    case premium      // Tariffs, PaymentQR, Activation, Referral
    case ai           // AI Assistant
    case data         // Analytics, ProtectionStats
    case neutral      // Settings, Profile, Notifications
    case legal        // Privacy, Terms — flat only
}

struct StormMeshBackground: View {
    let variant: StormMeshVariant
    var body: some View { /* см. §2.4 */ }
}
```

### 2.4 Mesh implementation (performance-safe)

**Обязательно:**
- 2–3 `Circle()` + `.blur(radius: 80)`;
- **Без анимации**;
- `LinearGradient` scrim снизу (transparent → stormBase 55%);
- `.ignoresSafeArea()` на ZStack.

**Опционально (есолько lag на iPhone SE):**
- `drawingGroup()` на blob layer;
- `.legal` и `.neutral` — минимум blur.

**Псевдокод структуры:**
```swift
ZStack {
    Color.stormBase.ignoresSafeArea()
    // blob 1, 2, 3 — positions/colors по variant (§3)
    LinearGradient(
        colors: [.clear, Color.stormBase.opacity(0.55)],
        startPoint: .center,
        endPoint: .bottom
    ).ignoresSafeArea()
}
```

### 2.5 StormGlassCardStyle — ViewModifier

Заменяет паттерн `.fill(Color.white.opacity(0.1))` на premium chrome:

```swift
struct StormGlassCardStyle: ViewModifier {
    var cornerRadius: CGFloat = 10
    var accentStripColor: Color? = nil  // 3pt left strip для shield

    func body(content: Content) -> some View {
        content
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: cornerRadius))
            .overlay(RoundedRectangle(cornerRadius: cornerRadius)
                .stroke(Color.secondaryGold.opacity(0.25), lineWidth: 1))
            .shadow(color: .black.opacity(0.25), radius: 8, x: 0, y: 4)
            // accent strip if accentStripColor != nil
    }
}
```

**Исключение:** семейная tariff card на `01_MainScreen` — **сохранить** существующий `LinearGradient` по `currentTariffColor` (яркий акцент).

### 2.6 Интеграция в экран (шаблон)

**Было:**
```swift
ZStack {
    LinearGradient(colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)], ...)
        .ignoresSafeArea()
    // content
}
```

**Стало:**
```swift
ZStack {
    StormMeshBackground(variant: .hub)
    // content — без изменений текстов
}
```

---

## 3. Mesh variants — детальная спецификация blobs

### 3.1 `.hub` — MainScreen, SupportScreen
| Blob | Color | Opacity | Position (approx) |
|------|-------|---------|-------------------|
| 1 Indigo storm | stormIndigo | 35% | topLeading, 280×280 |
| 2 Gold ray | goldPrimary | 18% | topTrailing, 220×220 |
| 3 Violet haze | stormViolet | 25% | bottom, 320×320 |
| Scrim | stormBase | 55% bottom | full width |

**Lazyweb ref:** Aura home, Life360 hub  
**before.click ref:** Security/family ASO palette

### 3.2 `.family` — FamilyScreen, FamilyChatScreen, JoinDeviceScreen
| Blob | Color | Opacity | Position |
|------|-------|---------|----------|
| 1 Violet center | stormViolet | 30% | center |
| 2 Gold soft | goldPrimary | 12% | top |
| 3 Indigo edge | stormIndigo | 15% | leading |
| Scrim | stormBase | **60%** bottom | chat/lists readability |

### 3.3 `.shield` — NetworkProtection, Devices, DeviceDetail, EnergyStats
| Blob | Color | Opacity | Notes |
|------|-------|---------|-------|
| 1 Indigo | stormIndigo | 28% | **NO gold** |
| 2 Slate | stormCloud | 22% | |
| 3 Lightning hint | stormLightning | 20% | optional |
| Accent | statusProtected / dangerRed | 3pt strip | status cards only |

**Lazyweb ref:** Norton VPN, 1Password, Aura shield

### 3.4 `.grow` — ParentalControlScreen
| Blob | Color | Opacity |
|------|-------|---------|
| 1 Violet | stormViolet | 28% |
| 2 Teal | stormTeal | 22% |
| 3 Gold minimal | goldPrimary | 10% |

**Lazyweb ref:** Qustodio (trust tone, not surveillance)

### 3.5 `.growWarm` — ChildInterfaceScreen
| Blob | Color | Opacity | Notes |
|------|-------|---------|-------|
| Base | `#0C1220` | 100% | 8% lighter than stormBase |
| 1 Teal dominant | stormTeal | 30% | |
| 2 Violet soft | stormViolet | 15% | no indigo |

**Lazyweb ref:** Khan Kids warmth + structure

### 3.6 `.warm` — ElderlyInterfaceScreen
| Blob | Color | Opacity |
|------|-------|---------|
| 1 Gold warm | goldWarm | 20% |
| 2 Violet muted | stormViolet | 12% |

### 3.7 `.premium` — Tariffs, PaymentQR, ActivationCode, Referral
| Blob | Color | Opacity |
|------|-------|---------|
| 1 Gold | goldPrimary | **20–22%** |
| 2 Violet | stormViolet | 15% |

**Lazyweb ref:** Headspace, Calm paywall  
**before.click ref:** Premium conversion slides

### 3.8 `.ai` — AIAssistantScreen
| Blob | Color | Opacity |
|------|-------|---------|
| 1 Lightning | stormLightning | 25% |
| 2 Gold point | goldPrimary | 14% | behind header |

**Lazyweb ref:** ChatGPT iOS home

### 3.9 `.data` — AnalyticsScreen, ProtectionStatsScreen
| Blob | Color | Opacity |
|------|-------|---------|
| 1 Indigo | stormIndigo | 22% |
| 2 Lightning | stormLightning | 18% |
| 3 Gold hint | goldPrimary | 10% |

**Lazyweb ref:** Revolut/Monzo stats

### 3.10 `.neutral` — Settings, Profile, Notifications
| Blob | Color | Opacity |
|------|-------|---------|
| 1 Cloud only | stormCloud | 12% |
| Base flat | stormDeep | dominant |

**Lazyweb ref:** iOS Settings calm

### 3.11 `.legal` — PrivacyPolicy, TermsOfService
- **Flat** `Color.stormBase` only
- **Zero blobs**, zero blur
- Maximum long-text readability

---

## 4. Матрица экранов (полная)

| # | File | Mesh Variant | Glass | Lazyweb archetype | before.click use |
|---|------|--------------|-------|-------------------|------------------|
| 01 | `01_MainScreen.swift` | `.hub` | Yes (grid + chat) | Aura + Life360 hub | ASO slide 1 palette |
| 02 | `02_FamilyScreen.swift` | `.family` | Yes | Life360 roster | Family dashboard slide |
| 03 | `03_NetworkProtectionScreen.swift` | `.shield` | Yes + accent strip | Norton VPN | Security slide |
| 04 | `04_AnalyticsScreen.swift` | `.data` | Yes | Banking stats | — |
| 05 | `05_SettingsScreen.swift` | `.neutral` | List rows optional | iOS Settings | — |
| 06 | `06_AIAssistantScreen.swift` | `.ai` | Input bar | ChatGPT iOS | AI slide |
| 07 | `07_ParentalControlScreen.swift` | `.grow` | Yes | Qustodio | Parental trust slide |
| 08 | `08_ChildInterfaceScreen.swift` | `.growWarm` | Yes | Khan Kids | Learning slide |
| 09 | `09_ElderlyInterfaceScreen.swift` | `.warm` | Yes | Calm large-type | — |
| 10 | `10_TariffsScreen.swift` | `.premium` | Plan cards | Headspace paywall | Trial slide |
| 11 | `11_ProfileScreen.swift` | `.neutral` | Optional | Revolut profile | — |
| 12 | `12_NotificationsScreen.swift` | `.neutral` | List | iOS notifications | — |
| 13 | `13_SupportScreen.swift` | `.hub` | Yes | Intercom premium | Support trust |
| 14 | `14_OnboardingScreen.swift` | **SKIP** | **SKIP** | — | Heroes only in ASO |
| 18 | `18_PrivacyPolicyScreen.swift` | `.legal` | No | — | Trust slide |
| 19 | `19_TermsOfServiceScreen.swift` | `.legal` | No | — | — |
| 20 | `20_DevicesScreen.swift` | `.shield` | Yes | Find My | Devices slide |
| 21 | `21_ReferralScreen.swift` | `.premium` | Yes | Fintech referral | — |
| 22 | `22_DeviceDetailScreen.swift` | `.shield` | Yes | Device detail | — |
| 23 | `23_FamilyChatScreen.swift` | `.family` | Bubbles unchanged | iMessage dark | — |
| 24 | `24_NetworkProtectionEnergyStatsScreen.swift` | `.shield` | Yes | Usage cold UI | — |
| 25 | `25_PaymentQRScreen.swift` | `.premium` | Yes | Fintech pay | Payment slide |
| 26 | `26_ActivationCodeScreen.swift` | `.premium` | Yes | Redeem flow | — |
| 27 | `27_ProtectionStatsScreen.swift` | `.data` | Yes | Stats | — |
| 28 | `28_JoinDeviceScreen.swift` | `.family` | Yes | Invite warm | Join family |

**Правило для любого экрана не из таблицы (Batch 5c):** ближайший variant по домену — Shield→`.shield`, Family flow→`.family`, Child/Game/Learn→`.growWarm`, Pay→`.premium`, Legal→`.legal`, Care/60+→`.warm`, default→`.neutral`.

---

## 4.1 Batch 9 — «Хвост экранов» (обязательно, иначе швы −10–15%)

### Wellness — решение product (зафиксировано)

| Тип Wellness UI | Variant | Почему |
|-----------------|---------|--------|
| Hub, эмоции, together, dream, exercises | **`.warm`** | Забота, calm — рядом с Elderly/Companion |
| Длинные формы, PHQ, consent, legal, timeline data | **`.neutral`** | Читаемость важнее «атмосферы» |
| Paywall/referral sheets в Wellness | **`.premium`** | Конверсия |

**Итог:** Wellness **не один** variant — **split warm/neutral** (лучше, чем только warm или только neutral).

### Таблица Batch 9

| Группа | File(s) | Mesh | Glass | SCREEN-SAFE |
|--------|---------|------|-------|-------------|
| **Companion 60+** | `CompanionHomeScreen`, `CompanionHubScreen`, `CompanionConversationScreen`, `CompanionMineTabView`, sections | `.warm` | Yes | §1.7 |
| **Companion legal** | `CompanionLegalScreen` | `.legal` | No | §1.7 |
| **Дети / игры** | `ChildRewardsScreen`, `GamesParentalControlScreen`, `GamesParentalControlView`, `UnicornPetView`, `UnicornUniverseView`, `WheelOfFortuneView`, `FamilyTournamentView` | `.growWarm` | Yes | §1.7 |
| **Обучение** | `SecurityEducationScreen`, `YoungDefenderView`, `ChildContentScreen`, `ChildContentExperienceScreen` | `.growWarm` / `.grow` | Yes | §1.7 |
| **Wellness warm** | `WellnessHubScreen`, `WellnessCheckinScreen`, `WellnessTogetherModeScreen`, `WellnessDreamJournalScreen`, `WellnessExerciseScreen`, `WellnessReflectiveModeScreen`, `WellnessPillarEmotionView` | `.warm` | Yes | §1.7 |
| **Wellness neutral** | `WellnessPhqLiteScreen`, `WellnessConsentScreen`, `WellnessTimelineScreen`, `WellnessTrustCenterScreen`, `WellnessAssessmentFlowScreen`, sheets data-heavy | `.neutral` | Optional | §1.7 |
| **Wellness premium** | `WellnessPremiumPaywallSheet`, `WellnessReferralSheet` | `.premium` | Yes | §1.7 |
| **Shield settings** | `AdvancedProtectionSettingsScreen`, `ThreatProtectionScreen`, `ThreatProtectionSettingsScreen`, `MalwareDetectionSettingsScreen`, `MobileSecuritySettingsScreen`, `NetworkSecuritySettingsScreen`, `PhishingProtectionSettingsScreen`, `PasswordGeneratorSettingsScreen`, `IncidentResponseSettingsScreen`, `IoTSecurityScreen`, `UnifiedTimeLimitsScreen` | `.shield` | List rows | §1.7 |
| **Flows / modals** | `AddMemberOptionsScreen`, `MainScreenWithRegistration` | `.family` / `.hub` | Yes | §1.7 |
| **Family extras** | `FamilyProtectorView`, `ParentDashboardView` | `.family` / `.grow` | Yes | §1.7 |
| **Прочее** | `NotificationSettingsScreen`, `LanguageSettingsScreen`, `WidgetConfigurationScreen`, `VoiceNotesScreen` | `.neutral` | Optional | §1.7 |

**Исключения freeze (как onboarding):** test/debug screens (`SimpleTestScreen`, `SettingsTestSuiteView`, `CrashLogsView`, `*Workbench*`) — **не трогать**, если не в production navigation.

---

## 5. Фазы реализации (батчи)

> **Каждый пункт с экраном:** перед правкой → **§1.7 PRE**, после → **§1.7 POST + отчёт**.

### Batch 0 — Foundation
- [ ] Storm tokens в `Colors.swift`
- [ ] `StormMeshBackground.swift` — все 11 variants
- [ ] `StormGlassCardStyle.swift`
- [ ] Preview canvas с grid всех variants
- [ ] **Не трогать экраны**

### Batch 1 — Tier 1 (first impression)
- [ ] **SCREEN-SAFE PRE/POST** на каждый файл (§1.7)
- [ ] `01_MainScreen.swift` → `.hub` + glass grid cards
- [ ] `10_TariffsScreen.swift` → `.premium`
- [ ] `02_FamilyScreen.swift` → `.family`

### Batch 2 — Tier 2 (mission: Shield + Grow)
- [ ] `07_ParentalControlScreen.swift` → `.grow`
- [ ] `08_ChildInterfaceScreen.swift` → `.growWarm`
- [ ] `03_NetworkProtectionScreen.swift` → `.shield` + accent strips

### Batch 3 — Tier 3 (daily)
- [ ] `06_AIAssistantScreen.swift` → `.ai`
- [ ] `20_DevicesScreen.swift` + `22_DeviceDetailScreen.swift` → `.shield`
- [ ] `04_AnalyticsScreen.swift` + `27_ProtectionStatsScreen.swift` → `.data`
- [ ] `23_FamilyChatScreen.swift` → `.family`

### Batch 4 — Tier 4 (profile & service)
- [ ] `11_ProfileScreen.swift` + `05_SettingsScreen.swift` → `.neutral`
- [ ] `13_SupportScreen.swift` → `.hub`; `12_NotificationsScreen.swift` → `.neutral`
- [ ] `09_ElderlyInterfaceScreen.swift` → `.warm`
- [ ] `21_ReferralScreen.swift` → `.premium`

### Batch 5 — Tier 5 (transactional & legal)
- [ ] `24_NetworkProtectionEnergyStatsScreen.swift` → `.shield`
- [ ] `25_PaymentQRScreen.swift` → `.premium`
- [ ] `26_ActivationCodeScreen.swift` → `.premium`
- [ ] `28_JoinDeviceScreen.swift` → `.family`
- [ ] `18_PrivacyPolicyScreen.swift` + `19_TermsOfServiceScreen.swift` → `.legal`

### Batch 6 — Premium polish (**ОБЯЗАТЕЛЕН — без него только ~78% premium, см. §1.6**)
- [ ] Grep: удалить все `Color.blue.opacity` / старые LinearGradient фоны на listed screens
- [ ] Все interactive cards → `StormGlassCardStyle` (**это переводит 78% → 95% premium**)
- [ ] Shield screens → accent strip где status on/off
- [ ] Bottom tab bar area: subtle storm scrim (Main only, background layer)
- [ ] Family tariff card on Main — **keep** colored gradient

### Batch 9 — Хвост экранов (**ОБЯЗАТЕЛЕН — §4.1**)
- [ ] **SCREEN-SAFE PRE/POST** на каждый файл
- [ ] Companion 60+ → `.warm`
- [ ] Дети / игры → `.growWarm`
- [ ] Обучение → `.growWarm` / `.grow`
- [ ] Wellness hub/emotion → `.warm`; forms/data → `.neutral`; paywall → `.premium`
- [ ] Shield settings → `.shield`
- [ ] `AddMemberOptionsScreen` → `.family`; `MainScreenWithRegistration` → `.hub`
- [ ] Grep `Screens/*.swift` — нет `Color.blue.opacity(0.8)` / legacy hub gradient

### Batch 7 — QA (после Batch 6 и 9)
- [ ] iPhone SE 3 — readability, blur performance
- [ ] iPhone 15 Pro Max — blob clipping
- [ ] **iPad** (если target поддерживает) — blob не обрезаны
- [ ] **`accessibilityReduceMotion`** — blur off, flat storm
- [ ] VoiceOver — decorative background hidden
- [ ] Onboarding OB_07 → Main: no white flash (stormBase match)
- [ ] Screenshot compare Main vs ASO mockup palette
- [ ] **Grep всего `Screens/`** — zero legacy blue/purple full-screen gradients
- [ ] **Все экраны §4 + §4.1** прошли SCREEN-SAFE отчёт

### Batch 8 — ASO (**обязателен для 100% brand cohesion Store ↔ app, см. §1.6**)
6 App Store slides, palette `.hub`:
1. «Защита семьи 24/7» — Main
2. «Умный родконтроль» — Parental
3. «Обучение без страха» — Child
4. «AI для родителей» — AI
5. «Все устройства — одна панель» — Devices
6. «Попробуйте бесплатно» — Tariffs

Claim: **«Защита семьи. Умный родконтроль. Обучение без страха.»**

---

## 6. Правила для ML-агента (DO / DON'T)

### DO
- Работать только из iOS repo root (см. § header)
- **Перед каждым экраном:** §1.7 SCREEN-SAFE PRE → правка → POST → отчёт
- Менять **только** background ZStack layer и card chrome modifiers
- Сохранять файлы через git (не удалять экраны; при fail — `git checkout`)
- Сохранять все `accessibilityIdentifier`
- Сохранять все `localizationManager.localized(...)` keys
- Использовать существующий `Color.secondaryGold` / новые storm tokens
- Один batch = один PR / один commit (если пользователь просит commit)
- После каждого batch: build + visual check on simulator

### DON'T
- **Не изменять** `14_OnboardingScreen.swift`
- Не менять NavigationManager routes
- Не менять ViewModels / API calls
- Не менять тексты, fonts sizes, layout order (unless separate task)
- Не добавлять анимацию на mesh blobs
- Не копировать layout App Store screenshots into in-app UI
- Не коммитить `telegram_stars_shop_bot/`, `.env`

---

## 7. Промпт-шаблоны для Cursor

### Старт foundation
```
Выполни Batch 0 из docs/STORM_MESH_PREMIUM_DESIGN_HANDOFF.md:
создай StormMeshBackground.swift, StormGlassCardStyle.swift,
дополни Colors.swift storm tokens. Экраны не трогай.
```

### Старт экрана (с SCREEN-SAFE)
```
Выполни Batch 1a: 01_MainScreen.swift
1. §1.7 PRE: grep accessibilityIdentifier + localized keys (baseline)
2. StormMeshBackground(.hub) вместо LinearGradient
3. StormGlassCardStyle на grid cards и chat block
4. Family tariff card gradient НЕ менять
5. §1.7 POST: IDs/keys count unchanged, visual all cards/text in place, readable
6. Отчёт SCREEN-SAFE в ответе
Тексты, navigation, layout order — без изменений
См. docs/STORM_MESH_PREMIUM_DESIGN_HANDOFF.md §4 row 01, §1.7
```

### QA pass
```
Выполни Batch 7: grep старых gradient фонов на Screens/0*.swift,
проверь контраст текста на SE simulator, onboarding→main transition.
```

---

## 8. Критерии «Premium done» (Definition of Done)

> **Шкала этапов — см. §1.6.** Batch 6 (glass) и Batch 8 (ASO) **не optional**.

| # | Критерий | Batch | Premium stage | Проверка |
|---|----------|-------|---------------|----------|
| 1 | Storm tokens + components exist | 0 | A | files exist |
| 2 | Все экраны §4 + §4.1 имеют StormMeshBackground | 1–5, 9 | B/E | grep + visual |
| 2b | Каждый экран — SCREEN-SAFE отчёт | 1–9 | — | §1.7.4 |
| 3 | Onboarding untouched | — | — | git diff 14_OnboardingScreen empty |
| 4 | Нет legacy blue/purple full-screen gradient | 6 | C | grep |
| 5 | **Glass on all interactive cards** (except legal) | **6** | **C (~95%)** | code review |
| 6 | Shield accent strips on status UI | 6 | C | Network, Devices |
| 7 | Performance: no animated blur | 6–7 | D | code review |
| 8 | Main family card keeps tariff gradient | 6 | C | visual |
| 9 | QA SE + Pro Max + onboarding→Main | 7 | D (~95% verified) | simulator |
| 10 | **ASO palette matches `.hub`** | **8** | **E (~100% brand)** | side-by-side screenshot |

**Итоговый premium score после 100%:** in-app **~95%**, brand cohesion Store+app **~100%**, onboarding wow **9/10** (сохранён).

---

## 9. Связь Lazyweb ↔ before.click ↔ ALADDIN

> **Прочитать вместе с §1.5–1.6.** Два сайта — два слоя одного premium. Мы **не копируем** чужие экраны; склеиваем **UX-паттерны** (Lazyweb) и **бренд-палитру** (before.click).

### 9.1 Главная формула (склеивание ресурсов)

```
Lazyweb                    before.click              ALADDIN
────────                   ────────────              ───────
«Как сделать экран»   +    «Какими цветами»     =   Storm mesh + glass
«Glass cards»              «Dark + gold»             те же tokens (§2.2)
«Shield без gold»          «Trust tone»              .shield / .grow
«Paywall premium»          «Convert slide»           .premium + ASO (Batch 8)
```

### 9.2 Таблица формулы (для ML-агента)

| Lazyweb (in-app UX) | before.click (бренд / Store) | Что получается в ALADDIN | Где в коде / batch |
|---------------------|------------------------------|--------------------------|-------------------|
| «Как сделать экран» — mesh hub, glass, иерархия | «Какими цветами» — dark navy + gold | **Storm mesh + glass** | `StormMeshBackground` + `StormGlassCardStyle` — Batch 0–6 |
| Glass cards — depth, blur surfaces | Dark + gold — premium ASO palette | **Те же tokens** — один `Colors.swift` | `stormBase`, `goldPrimary`, `stormTeal`… — §2.2 |
| Shield без gold — Norton, Aura VPN | Trust tone — не страх, а доверие | **`.shield`** (cold) / **`.grow`** (violet+teal) | 03, 20, 22 / 07 Parental |
| Paywall premium — Headspace, Calm | Convert slide — trial, value | **`.premium`** mesh + **Batch 8 ASO** | 10, 25, 26, 21 + Store assets |
| Life360 family hub | Family slide — «одна панель» | **`.hub`** / **`.family`** | 01, 02, 23, 28 |
| Khan Kids warmth | Play + learn slide | **`.growWarm`** | 08 Child |
| ChatGPT input home | AI slide | **`.ai`** | 06 AI |
| — | Store ≠ app (обман ожидания) | **Batch 8** — ASO = `.hub` colors | ~100% brand cohesion §1.6 |

### 9.3 Два ресурса — простыми словами

| Сайт | Что это | Что берём | Что НЕ берём |
|------|---------|-----------|--------------|
| **Lazyweb** | 250k+ экранов **внутри** apps | Фон (mesh), glass cards, разный mood по типу экрана (shield / family / paywall) | Чужой layout, тексты, кнопки 1:1 |
| **before.click** | Скриншоты **App Store** | Палитра dark+gold, tone «доверие», storyboard из 6 slides | Огромные Store-заголовки внутри app, fake iPhone frames в UI |

### 9.4 Проблема → решение (детальная таблица)

| Проблема | Lazyweb даёт | before.click даёт | Наше решение |
|----------|--------------|-------------------|--------------|
| Разрозненные фоны | Hub mesh pattern | Единая dark+gold палитра | 11 mesh variants, 1 token set |
| Плоские карточки | Glass + depth | Premium ASO look | `StormGlassCardStyle` — **Batch 6 (~95%)** |
| Security feels cold | Norton/Aura shield UI | Trust messaging | `.shield` — без gold |
| Parental feels surveillance | Qustodio trust UX | Family tone | `.grow` — violet + teal |
| Child feels disconnected | Khan warmth | Play+learn slide | `.growWarm` — teal dominant |
| Paywall noisy | Headspace 3-tier | Conversion slides | `.premium` — gold 20–22% |
| Store ≠ app | — | Screenshot consistency | Batch 8 ASO = `.hub` colors — **~100% brand** |

### 9.5 Narrative для команды (одна строка)

> **Lazyweb учит, как держать экран. before.click учит, как держать бренд. ALADDIN = storm+gold небо + glass-карточки; слова и онбординг — без изменений.**

---

## 10. Transition Onboarding → Main

**Проблема:** после cinematic onboarding резкий смен фона ломает premium feel.

**Решение (без изменения onboarding):**
- Main `stormBase` = `#070B14` — совпадает с тёмным низом OB scrim
- Первый кадр Main после OB_07 — тот же base color
- Optional (future): 0.3s fade on Main `onAppear` — **только если product approves**

---

## 11. Файлы для чтения агенту (контекст)

| File | Зачем |
|------|-------|
| `Shared/Styles/Colors.swift` | Existing tokens |
| `Screens/01_MainScreen.swift` | Primary integration example |
| `docs/ONBOARDING_MAIN_HERO_HANDOFF.md` | Onboarding do-not-touch policy |
| `.cursor/rules/onboarding-figma-ios-sync-mandatory.mdc` | Onboarding sync rules |

---

## 12. История решений

| Дата | Решение |
|------|---------|
| 2026-06-08 | Variant A (hero ambient on Main) — **отклонён** product |
| 2026-06-08 | Variant B Mesh — **принят** |
| 2026-06-08 | Onboarding — **freeze** |
| 2026-06-08 | Texts/cards content — **freeze**; chrome only |
| 2026-06-08 | 11 mesh variants для 20+ screens |
| 2026-06-08 | Glass cards — обязательная Batch 6 для ~95% premium (§1.6) |
| 2026-06-08 | §1.5–1.6: шкала 78% → 95% → 100% brand, «что делаем» |
| 2026-06-08 | §9.1–9.5: формула Lazyweb + before.click → ALADDIN |
| 2026-06-09 | §1.7 SCREEN-SAFE Gate (PRE/POST каждый экран) |
| 2026-06-09 | §4.1 + Batch 9: Companion, Wellness split warm/neutral, Games, Learn |
| 2026-06-09 | Продукт 5 столпов: Shield+Family+Grow+Play+Learn |
| 2026-06-09 | Batch 7: iPad, Reduce Motion, grep all Screens/ |

---

**Конец handoff.**  
Следующий шаг: `Batch 0` → затем `Batch 1a (01_MainScreen)`.
