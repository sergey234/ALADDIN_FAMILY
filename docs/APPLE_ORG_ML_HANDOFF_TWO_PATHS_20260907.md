# ALADDIN iOS — Handoff для другой ML-системы  
## Миграция Apple: личный аккаунт → компания (2 пути) + что уже сделано

**Дата:** 2026-09-07  
**Репозиторий (единственный рабочий корень):**  
`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Ветка:** `master`  
**Приложение:** ALADDIN iOS · Bundle ID `family.aladdin.ios` · Marketing `1.0.0` · Build (на момент handoff) **247**

> Этот документ — полный понятный бриф. Читать сверху вниз. Не смешивать с `telegram_stars_shop_bot/` (бот не в iOS-релиз).

---

## 0) Зачем вообще два пути

Сейчас:

| Кто | Что есть |
|-----|----------|
| **Личный** Apple Developer | App `family.aladdin.ios` в App Store Connect, **только TestFlight** (в Store ещё не выходили) |
| **Компания** SAUDAPAYDI, TOO (Казахстан) | Отдельный Organization-аккаунт, Team ID **`B3WGHSWL79`**, email Holder **`aladdin.ai@tuta.io`** |

Цель владельца: в итоге **App Store от компании**.  
Проблема: Bundle ID `family.aladdin.ios` **уже занят личным** аккаунтом. Компания **не может** зарегистрировать тот же Bundle, пока ID «сидит» на личном.

Поэтому есть **только два рабочих варианта** (плюс временный шаг «сначала TestFlight с личного» — см. §5).

---

## 1) Что значит «Bundle занят»

- **Bundle ID** = уникальный адрес приложения у Apple (как номер паспорта).
- У ALADDIN сейчас: **`family.aladdin.ios`**.
- Его создал **личный** аккаунт → в мире Apple он принадлежит личному Team.
- Компания **не может** создать New App с тем же Bundle.
- Удаление TestFlight / «освободить ID» обычно **не работает** — ID почти не возвращают.

| Хотим | Как |
|-------|-----|
| Тот же Bundle у компании | Только **App Transfer** (путь A) после критерия Apple (обычно нужна версия в App Store) |
| Сразу кабинет компании без Transfer | **Новый** Bundle + новое приложение (путь B) |

---

## 2) Путь A — Transfer (рекомендованный для «одного приложения на годы»)

### Идея простыми словами

1. На **личном** аккаунте один раз выпустить ALADDIN в **App Store** (можно минимально).
2. Сделать **App Transfer** на компанию (`B3WGHSWL79` / `aladdin.ai@tuta.io`).
3. Дальше подписи, TestFlight, Store — **только компания**.
4. Bundle **тот же** `family.aladdin.ios`. Product ID подписок можно оставить текущие.

### Плюсы / минусы

| | |
|--|--|
| **Плюсы** | Один Bundle, одна история, меньше правок в коде, те же IAP ID |
| **Минусы** | Нужен Review на личном + ожидание Transfer; нельзя «мгновенно» грузить TF только в кабинет компании, пока Bundle на личном |

### Что делать другой ML-системе (чеклист A)

1. Проверить ASC **компании**: Agreements → **Paid Apps = Active** (+ Tax/Banking когда нужны выплаты).
2. На **личном** ASC: подготовить минимальный App Store релиз (скрины, Privacy, возрастной рейтинг, DSA trader уже заполняли).
3. Загрузить билд, подписанный **личным** Team → Submit for Review → Waiting for Review → Approved → Ready for Sale (или эквивалент, достаточный для Transfer).
4. Личный Account Holder → **Transfer App** → указать Team `B3WGHSWL79` и email `aladdin.ai@tuta.io`.
5. На компании: **Accept Transfer**.
6. После Accept: обновить Identifiers/Profiles под компанию, `DEVELOPMENT_TEAM = B3WGHSWL79`, Archive → TestFlight компании → IAP → релиз.

Канон в репо: `docs/APPLE_ORG_MIGRATION_RUNBOOK.md`, worksheet `docs/APPLE_ORG_MIGRATION_GATE0_WORKSHEET.md`.

---

## 3) Путь B — без Transfer, сразу новое приложение на компании

### Идея простыми словами

На компании создаём **другое** приложение с **новым** Bundle ID. Старый `family.aladdin.ios` остаётся на личном (или заброшен). Это **не** «переименование» — это вторая жизнь приложения.

### Какие правки в проекте (много, но делаемые)

| Что менять | Пример / зачем |
|------------|----------------|
| Bundle ID app | `family.aladdin.ios` → например `too.saudapaydi.aladdin` |
| Bundle ID 3 appex | Content Blocker, Antifake Share, Call Directory — новые ID |
| App Group | `group.com.aladdin.family` → новая группа под компанией (во всех entitlements) |
| Associated Domains | `applinks:aladdin-ai.ru` — перепривязать к новому App ID |
| IAP Product IDs в `StoreManager` | Старые ID привязаны к старому app → завести новые в ASC + в коде |
| StoreKit config | `ALADDIN/StoreKit/ALADDINSubscriptions.storekit` |
| Signing / profiles | Team `B3WGHSWL79`, новые Distribution profiles |
| ASC | **New App**, новый TestFlight, карточка Store с нуля |
| Deep links / Share (если завязаны на bundle) | проверить |

**Сможет ли агент сделать правки в коде?** Да — массовая замена Bundle/групп/Product ID + verify скрипты + сборка.  
**Что делает владелец в Apple:** Identifiers, New App, скрины, Review, соглашения.

### Плюсы / минусы

| | |
|--|--|
| **Плюсы** | Не ждать Transfer; сразу кабинет компании |
| **Минусы** | Другое приложение; старый TF не продолжается; два мира; выше риск ошибок ID/IAP |

---

## 4) Сравнение и рекомендация (уже согласовано с владельцем)

| Критерий | A Transfer | B Новое на компании |
|----------|------------|---------------------|
| Bundle | тот же | новый |
| Правки кода | мало | много |
| Непрерывность TF/Store | да | нет |
| Скорость «начать на компании» | медленнее | быстрее старт кабинета |
| На годы | **лучше** | хуже |

**Рекомендация владельцу:** путь **A (Transfer)** после минимального Store-релиза с личного.  
Путь B — только если нужен срочный кабинет компании ценой нового Bundle.

Выбранный ранее в worksheet: **путь C = A** (TF-only сейчас → минимальный Store на личном → Transfer → Store компании).

---

## 5) Отдельный срочный трек: TestFlight с **личного** аккаунта через GitHub

Это **не** замена пути A/B. Это «получить билд на телефон сейчас», пока миграция на компанию ещё не завершена.

### Критично

Пока Bundle на личном ASC, билд для **личного** TestFlight должен быть подписан **личным** Team:

| Team | ID |
|------|-----|
| Личный (для TF сейчас) | **`6CJVBBUGSN`** |
| Компания (после Transfer / для пути B) | **`B3WGHSWL79`** |

Если в `project.pbxproj` стоит компания, а грузите в личный ASC — подпись/upload сломаются или уйдут не туда.

CI: `.github/workflows/appstore.yml` (часто `workflow_dispatch`) + secrets  
`APP_STORE_CONNECT_API_KEY` / `APP_STORE_CONNECT_ISSUER_ID` / `APP_STORE_CONNECT_API_KEY_ID`  
(ключи должны быть от **того** ASC, куда грузите — сейчас личный).

Подробный операционный план: `docs/APPLE_ORG_PERSONAL_TESTFLIGHT_GITHUB_PLAN_20260907.md`.

---

## 6) Что уже сделали в этой сессии (факты для следующей ML)

### 6.1 Правка в коде / Xcode (главное)

**Файл:** `ALADDIN.xcodeproj/project.pbxproj`  

**Что:** все **12** вхождений `DEVELOPMENT_TEAM` изменены:

```text
было:  6CJVBBUGSN   (личный)
стало: B3WGHSWL79   (компания SAUDAPAYDI)
```

**Как:** скрипт  
`./scripts/ios_set_development_team.sh B3WGHSWL79`  

**Бэкап pbx:**  
`ALADDIN.xcodeproj/project.pbxproj.bak_team_20260907_131715`  
(в бэкапе ещё личный Team).

**Проверка:**  
`./scripts/ios_verify_signing_targets.sh` → один Team по проекту.

> ⚠️ На момент handoff эта правка **мешает** срочному личному TestFlight.  
> Перед GitHub → личный TF нужно вернуть Team на **`6CJVBBUGSN`**, а `B3WGHSWL79` поставить снова **после** Transfer (или для пути B).

**Не меняли в этой правке:** Bundle ID, App Group, Product ID подписок, Swift-логику экранов. Только `DEVELOPMENT_TEAM`.

### 6.2 Новые скрипты (untracked / добавить в git при коммите миграции)

| Файл | Назначение |
|------|------------|
| `scripts/ios_set_development_team.sh` | Массовая смена `DEVELOPMENT_TEAM` + бэкап pbx |
| `scripts/ios_verify_signing_targets.sh` | Проверка единого Team / targets |

### 6.3 Документы миграции (untracked)

| Файл | Назначение |
|------|------------|
| `docs/APPLE_ORG_MIGRATION_RUNBOOK.md` | Канон шагов миграции |
| `docs/APPLE_ORG_MIGRATION_GATE0_WORKSHEET.md` | Заполненные факты владельца |
| `docs/APPLE_ORG_MIGRATION_OWNER_CHECKLIST.md` | Чеклист владельца |
| `docs/APPLE_ORG_IAP_PRODUCT_IDS.md` | Product ID из кода |
| `docs/APPLE_ORG_RELEASE_NOTES_RELOGIN.md` | Заметки про re-login после смены аккаунта |
| `docs/APPLE_ORG_ML_HANDOFF_TWO_PATHS_20260907.md` | **этот файл** |
| `docs/APPLE_ORG_PERSONAL_TESTFLIGHT_GITHUB_PLAN_20260907.md` | План личного TF через GitHub |

### 6.4 StoreKit конфиг (untracked)

| Файл | Назначение |
|------|------------|
| `ALADDIN/StoreKit/ALADDINSubscriptions.storekit` | Локальный StoreKit для отладки подписок |

### 6.5 Product ID (канон из кода, см. `StoreManager`)

- `family.aladdin.ios.subscription.individual.v2`
- `family.aladdin.ios.subscription.family`
- `family.aladdin.ios.subscription.premium`

### 6.6 Факты Apple (владелец)

| Поле | Значение |
|------|----------|
| Компания | SAUDAPAYDI, TOO · DUNS `302078411` |
| Company Team | `B3WGHSWL79` |
| Holder | `aladdin.ai@tuta.io` (Account Holder + Admin) |
| Convert Individual→Org | **Нет** (два отдельных аккаунта) |
| Статус личного app | **Только TestFlight** |
| DSA trader | seller заявлен |
| Paid Apps / banking | добить Active + банк/налоги когда нужны выплаты |

### 6.7 Что НЕ делали

- App Transfer не запускали.
- New App на компании не создавали.
- Bundle / App Group / IAP ID в коде **не** переименовывали.
- В GitHub **не** пушили эту смену Team (на момент handoff — локальный diff).
- `telegram_stars_shop_bot/` в iOS-коммиты не класть.

### 6.8 Бэкапы продукта (параллельно, не Apple-signing)

- Чистый бэкап: `NEW_BACKUP_ALADDIN_20260907_113004` / ZIP `BACKUP_ALADDIN_CLEAN_20260907_1130.zip`
- Индекс секретов (без live values): в `~/ALADDIN_VPN_SAFE/` и Downloads kit  
- **Никогда** не коммитить `VPN_SPEED_DEGRADATION_HANDOFF_RU.md` §32

---

## 7) Identifiers / entitlements (не менялись, знать blast radius)

| Target | Bundle |
|--------|--------|
| ALADDIN | `family.aladdin.ios` |
| Content Blocker | `family.aladdin.ios.ALADDINContentBlocker` |
| Antifake Share | `family.aladdin.ios.ALADDINAntifakeShare` |
| Call Directory | `family.aladdin.ios.ALADDINCallDirectory` |

- App Group: `group.com.aladdin.family`
- Associated Domains: `applinks:aladdin-ai.ru`

---

## 8) Команды быстрой проверки

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
git rev-parse --show-toplevel   # должен быть этот путь
git branch --show-current
git status --short

# какой Team сейчас в проекте
./scripts/ios_verify_signing_targets.sh
grep -o 'DEVELOPMENT_TEAM = [^;]*' ALADDIN.xcodeproj/project.pbxproj | sort -u

# вернуть личный Team (для личного TestFlight)
./scripts/ios_set_development_team.sh 6CJVBBUGSN

# снова компания (только после Transfer или для пути B)
./scripts/ios_set_development_team.sh B3WGHSWL79
```

---

## 9) Решение для следующей ML-системы (порядок работ)

1. **Сейчас (телефон / TF):** личный Team `6CJVBBUGSN` → коммит iOS-only → push/GitHub Actions → TestFlight на личный ASC → установка на iPhone.  
   План: `APPLE_ORG_PERSONAL_TESTFLIGHT_GITHUB_PLAN_20260907.md`.
2. **Потом (магазин компании):** минимальный Store с личного → Transfer → Team `B3WGHSWL79` → профили компании → TF/Store компании (путь A).
3. **Альтернатива:** путь B только по явному GO владельца + выбранный новый Bundle.

---

## 10) Связанные файлы

- `docs/APPLE_ORG_MIGRATION_RUNBOOK.md`
- `docs/APPLE_ORG_MIGRATION_GATE0_WORKSHEET.md`
- `docs/APPLE_ORG_MIGRATION_OWNER_CHECKLIST.md`
- `docs/APPLE_ORG_IAP_PRODUCT_IDS.md`
- `docs/APPLE_ORG_PERSONAL_TESTFLIGHT_GITHUB_PLAN_20260907.md`
- `AGENTS.md` (карта репо, запреты)

**Конец handoff.** Следующая система: не гадать Team — смотреть `ios_verify_signing_targets.sh` и цель (личный TF vs компания).
