# Финальный план: после Approved build 8 → push build 9 → Family Controls → реальная статистика

**Для другой ML-системы. Читать первым по Screen Time / FC после первой публикации.**

| Поле | Значение |
|------|----------|
| **Дата** | 2026-10-16 (обновлено: Assigned + Profiles 4/4 + PROD-100) |
| **Триггер** | Build 8 approved → push 9 → FC Assigned → WAVE 2 |
| **Сборка с фичами в git** | **9** на GitHub (без ST targets) |
| **Screen Time в бинаре 9** | **Нет** — правильно; FC уже **Assigned**, код ждёт GO |
| **Реальные цифры Screen Time** | **build 10** по SSOT WAVE 2 PROD-100 |

## Каноны (не дублировать — открывать)

| Документ | Зачем |
|----------|--------|
| **Этот файл** | Исполняемый порядок: push 9 → заявление FC → код после Assigned |
| [`SCREEN_TIME_NOW_VS_AFTER_FIRST_APPROVAL_2026-10-16_RU.md`](SCREEN_TIME_NOW_VS_AFTER_FIRST_APPROVAL_2026-10-16_RU.md) | Решение владельца: сначала публикация, потом заявление |
| [`SCREEN_TIME_STATS_COLLECTION_PLAN_2026-10-16_RU.md`](SCREEN_TIME_STATS_COLLECTION_PLAN_2026-10-16_RU.md) | Техплан Monitor/Report/App Group / фазы A–E |
| [`FAMILY_CONTROLS_DISTRIBUTION_IMPLEMENTATION_PLAN_2026-09-09_RU.md`](FAMILY_CONTROLS_DISTRIBUTION_IMPLEMENTATION_PLAN_2026-09-09_RU.md) | Тексты заявки §5 · кто подаёт · Bundle IDs |
| [`docs/RELEASE_BUILD_PROMPT.md`](../RELEASE_BUILD_PROMPT.md) | Номер сборки Path B · PREV/NEXT · push |

**Запрещено путать:** старые номера 247/248 и team `6CJVBBUGSN` — это другой app. Сейчас: `ai.aladdin`, team `B3WGHSWL79`, build **9** в коде.

---

## 0. Главный принцип (наилучший порядок)

```
Build 8 Approved ✅
    → WAVE 0: закоммиченный хвост + push origin master (build 9 в git)
    → WAVE 0b: Archive/TestFlight/Submit build 9 БЕЗ Family Controls
    → WAVE 1: Account Holder подаёт Family Controls Distribution (заявление)
    → ждать Assigned (дни–недели)
    → WAVE 2: код Monitor + Report (+ Shield) + реальные цифры
    → bump PREV=9 → NEXT=10 (или следующий свободный) → TF → Submit vNext
```

**Почему так:** без **Assigned** нельзя честно везти `com.apple.developer.family-controls` и targets DeviceActivity в App Store.  
**Build 9** = все готовые продуктовые коммиты + честный empty статистики.  
**Реальный Screen Time** = отдельная следующая сборка после Apple Assigned.

Агент **не** начинает WAVE 2 без явного GO владельца «Assigned получен».

---

## 1. WAVE 0 — Push build 9 (все предыдущие коммиты)

### Зачем
На GitHub и в CI/Archive должна быть **сборка 9** со всеми фичами после build 8, иначе TestFlight/команда работают со старым кодом.

### Коммиты, которые должны уйти на `origin/master` (на момент плана)

| Hash | Сообщение | Зачем |
|------|-----------|--------|
| `9f1a5133` | feat(build 9): Convenient QA + Hybrid C ProtectionFeedback + PROD QA tails | Bump 8→9 + основной объём |
| `f60e8515` | fix(ios): Convenient Mode parents-in-More, Calls close/phone, safe-word eye, habit switches | UX Convenient / Calls / safe-word |
| `85422a42` | fix(ios): honest time stats UI … + Screen Time plan | Честный empty + каноны Screen Time |
| `26a70568` | feat(backend): family safe-word store… | API safe-word (не Swift; едет в том же push) |
| `4a060658` | fix(ios): pbx FamilyScamCallFunnel, AV file-scope banner, unicorn PNG master | Archive-safe pbx + AV honesty + unicorn PNG |

### Задачи WAVE 0 (агент / ML)

| ID | Задача | Зачем |
|----|--------|--------|
| **W0.1** | Проверить ветку `master`, remote `git@github.com:sergey234/ALADDIN_FAMILY.git` | Канон релиза |
| **W0.2** | Verify build **9** везде: Info.plist, pbx `CURRENT_PROJECT_VERSION`, AppConfig×2, CallDirectory, AppConfigTests | Иначе TF «не видит» / reject |
| **W0.3** | `./scripts/verify_parental_time_stats_honesty.sh` | Нет моков статистики |
| **W0.4** | Staging только релизные файлы; **не** `telegram_stars_shop_bot/**`, не `.env`, не BACKUPS, не Vault | Правило bot∉iOS |
| **W0.5** | После **GO на push** владельца: `git push origin master` | Все 5 коммитов на GitHub |
| **W0.6** | Показать hash + `master -> master` | Evidence |
| **W0.7** | После **GO на сборку**: Archive build **9** в Xcode (team `B3WGHSWL79`) → TestFlight | Доставить билд 9 в Apple |
| **W0.8** | Review Notes build 9: **не** обещать системный Screen Time | Guideline |

`AppStoreBuildPolicy.allowsSystemFamilyControls` остаётся **false** в build 9.

---

## 2. WAVE 1 — Заявление Apple (Family Controls Distribution)

### Когда
После того как build 8 Accepted / Ready for Sale (уже выполнено или выполняется).  
Можно **параллельно** с W0.7 (TF build 9), но **не** блокировать push из‑за заявки.

### Кто
Только **Account Holder** Apple Developer (агент/ML **не** может подать форму за владельца).

### Зачем
Без Distribution Assigned нельзя легально ставить Monitor/Report/Shield в прод.

### Задачи WAVE 1 (владелец + черновик агента)

| ID | Задача | Зачем |
|----|--------|--------|
| **W1.1** | Зафиксировать Bundle IDs: `ai.aladdin`, `ai.aladdin.DeviceActivityMonitor`, `ai.aladdin.DeviceActivityReport` (+ `…ShieldConfiguration` если берём блокировку) | Отдельный request на каждый ID |
| **W1.2** | Взять тексты из Distribution-плана **§5** (EN для Capability Request) | Единый смысл заявки |
| **W1.3** | Account Holder: developer.apple.com → Certificates, Identifiers & Profiles → **Capability Requests** → Family Controls | Официальный канал |
| **W1.4** | Подать запросы на **main + Monitor + Report** (Shield — рекомендуется для полного parental) | Stats = Monitor+Report; блок = Shield |
| **W1.5** | Сохранить дату / номер / скрин статуса заявки в `docs/AppStore/` (без секретов) | Память для ML |
| **W1.6** | Ждать статус **Assigned** | GATES G1 из stats-плана |
| **W1.7** | Только после Assigned — **GO на WAVE 2** агенту | Не писать FC-код «заранее в прод» |

Пока ждём Apple — можно делать только **черновики за флагом** (см. P2 в NOW_VS_AFTER), **без** merge entitlement в релиз.

---

## 3. WAVE 2 — После Assigned: код + реальные цифры (vNext)

### Зачем
Родитель видит **факт** минут по выбранным apps; лимиты начинают опираться на систему; (опционально) Shield блокирует.

### Номер сборки
По канону: сейчас PREV=**9**, NEXT=**10**.  
После GO на bump: везде **10** (не 248).  
Если build 9 ещё не уехал в ASC — всё равно **не** смешивать FC в уже описанный TF-9 без Assigned; после Assigned = новый bump.

### Задачи WAVE 2 (агент после GO)

| ID | Задача | Зачем |
|----|--------|--------|
| **W2.1** | App IDs + profiles: включить Family Controls на main/Monitor/Report/(Shield) | Подпись Archive |
| **W2.2** | Entitlement `com.apple.developer.family-controls` на нужных targets | Системный API |
| **W2.3** | Xcode targets DeviceActivityMonitor + DeviceActivityReport, embed | Сбор + UI-отчёт |
| **W2.4** | App Group + `ScreenTimeUsageStore` (схема из stats-плана) | Мост extension ↔ main |
| **W2.5** | Report: дневной агрегат выбранных apps → store | Источник цифр |
| **W2.6** | Monitor: schedule/thresholds → refresh | Лимиты/события |
| **W2.7** | `fetchRealScreenTimeStats()` читает store (не моки) | Честный UI |
| **W2.8** | UI Семья / Advanced: реальные минуты; убрать «навсегда empty» | Продукт |
| **W2.9** | (Рек.) Shield Configuration/Action | Реальная блокировка apps |
| **W2.10** | `allowsSystemFamilyControls = true` только в этой версии | Claims согласованы с кодом |
| **W2.11** | Device QA: 2 iPhone (parent + child) | Без этого не Submit |
| **W2.12** | Bump build по `RELEASE_BUILD_PROMPT.md`, commit, push (GO), Archive, TF, Submit | Доставка vNext |
| **W2.13** | Обновить Review Notes / ASO: только то, что реально работает | Guideline |

Детали реализации: фазы **A–E** в `SCREEN_TIME_STATS_COLLECTION_PLAN_2026-10-16_RU.md`.

---

## 4. Что НЕ делать (красные флаги)

| Нельзя | Почему |
|--------|--------|
| Возвращать мок «18 min Instagram» | Обман + Review |
| Включать FC entitlement в build 9 до Assigned | Archive/подпись/reject |
| Обещать Screen Time в ASO build 8/9 | Claims без capability |
| Пушить BACKUPS / bot / `.env` / Vault | Правила репо |
| Bump на 247/248 или понижать build | Канон Path B |
| `xcodebuild` / Simulator без GO владельца | ask-before-ios-build |
| Push без фразы **GO на push** | ios-commit-on-master / RELEASE prompt |

---

## 5. Чеклист владельца (просто)

### Сегодня / ближайшие часы
- [ ] **GO на push** — уйти 5 коммитов build 9 на GitHub  
- [ ] **GO на сборку** — Archive/TF build **9** (без Screen Time)  
- [ ] Решить день подачи FC (сразу или +1–3 дня после Ready for Sale build 8)  

### Заявление Apple
- [ ] Account Holder подал main + Monitor + Report (+ Shield)  
- [ ] Записана дата заявки  
- [ ] Статус → Assigned  

### После Assigned
- [ ] **GO на WAVE 2** агенту  
- [ ] Device QA  
- [ ] **GO на bump** (9→10) + push + Submit vNext с реальной статистикой  

---

## 6. Одна фраза

> **Build 8 принят.** Сейчас пушим и везём **build 9** со всеми готовыми коммитами **без** Screen Time. Параллельно Account Holder подаёт Family Controls. Когда Apple даст **Assigned** — в **следующей** сборке ставим Monitor+Report(+Shield) и показываем **реальные** цифры.

## 7. Статус на 2026-10-16 (актуально)

| Поле | Значение |
|------|----------|
| Build 8 | Accepted / App approved |
| Build 9 в git / GitHub | **Да** (без Screen Time targets) |
| FC Distribution | **Assigned** · Profiles **4/4** на Mac |
| Код Monitor/Report/Shield | Ждёт фразу **«FC Assigned — GO на WAVE 2»** |
| SSOT WAVE 2 | `SCREEN_TIME_WAVE2_FULL_UI_MAP_AND_CHECKLIST_2026-10-16_RU.md` **PROD-100** |
| TODO | `.cursor/SCREEN_TIME_WAVE2_TASK_REGISTRY.md` (`st-*`) |
| Следующий номер после 9 | **10** (только с GO на bump) |

**Конец финального плана.**

---

## 8. Обновление после писем Apple (2026-10-16)

| Событие | Статус |
|---------|--------|
| App Review: ALADDIN AI approved for distribution | **YES** |
| Family Controls (Distribution) Assigned | **YES** |
| Следующий исполняемый SSOT | [`SCREEN_TIME_WAVE2_FULL_UI_MAP_AND_CHECKLIST_2026-10-16_RU.md`](SCREEN_TIME_WAVE2_FULL_UI_MAP_AND_CHECKLIST_2026-10-16_RU.md) |
| Код Screen Time | После GO «FC Assigned — GO на WAVE 2» → build **10** |

### Портал закрыт 2026-10-16

Profiles main+Monitor+Report+Shield установлены на Mac, в каждом `family-controls` + `group.ai.aladdin`.  
Код: SSOT `SCREEN_TIME_WAVE2_FULL_UI_MAP_AND_CHECKLIST_2026-10-16_RU.md` §9 — ждать **«FC Assigned — GO на WAVE 2»**.
