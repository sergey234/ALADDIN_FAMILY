# Wellness — откат HealthKit (вариант B) · план на будущее

> **Статус:** ✅ **выполнено** build **222** (2026-06-02)  
> **Цель:** CI/App Store archive без похода в Apple Developer Portal — только ручной ввод сна в check-in.  
> **Контекст CI:** GitHub Actions run `logs_71945656834` — archive упал на entitlement HealthKit; профиль `ALADDIN App Store Distribution new` без capability HealthKit.

---

## 1. Решение PO (отложено)

| | Вариант A (Portal + HealthKit) | **Вариант B (откат в коде)** ← выбран на потом |
|---|--------------------------------|------------------------------------------------|
| CI с текущими secrets | Нужен новый App Store profile | **Обычно достаточно** убрать entitlement |
| Check-in | Автозаполнение сна из Apple Health | **Только ползунок** 3–12 ч (руками) |
| Portal | HealthKit ON + secrets | **Не трогать** |
| App Review | Новый текст про optional HealthKit | Как декабрь 2025: «HealthKit не используем» |

**Сейчас в `master`:** build **221** (`95439b21`) **с** HealthKit — CI archive **не прошёл**.  
**Когда будете делать откат:** новый коммит + push по [§6](#6-релиз-commit--push-по-правилам).

---

## 2. Что HealthKit делал (и что останется)

| Было (p2-36) | После отката |
|--------------|--------------|
| Кнопка «Подставить сон из „Здоровье“» | Убрать из UI |
| Автоподстановка сна при открытии check-in | Убрать |
| Чтение `sleepAnalysis` из Health | Не вызывать |
| Ползунок «Как спал(а)?» + сохранение на сервер | **Без изменений** |
| Дневник снов, sleep stories API, mood/stress | **Без HealthKit** (как сейчас) |

**Единственный блокер CI из лога 71945656834 — HealthKit.** Других Health-типов (шаги, пульс) в коде нет.

**Отдельно (не HealthKit):** в secrets могут быть Development/Ad Hoc профили — CI на это **предупредил**, но упал именно на HealthKit. После отката B имеет смысл **позже** перевести secrets на App Store Distribution (см. [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md) § «Профили App Store»).

---

## 3. Плюсы и минусы варианта B

### Плюсы

- CI может собраться **без** обновления Portal и `PROVISIONING_PROFILE_*`.
- Проще App Review (история «HealthKit удалён» согласована).
- Check-in не ломается — пользователь сам указывает часы сна.
- Backend / API wellness **не меняется** (`sleep_hours` по-прежнему с клиента).

### Минусы

- Нет «Из Health» и автозаполнения для Apple Watch / Health.
- Код p2-36 остаётся в репо, но **отключён** (или за `#if false` / feature flag iOS).
- Позже для варианта A снова нужны Portal + secrets + текст Review.

---

## 4. Чеклист изменений в коде (когда выполнять)

Рабочий корень: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

### 4.1 Обязательно (подпись / CI)

| # | Файл | Действие |
|---|------|----------|
| 1 | `ALADDIN.entitlements` | Удалить блок `com.apple.developer.healthkit` |
| 2 | `Info.plist` | Удалить ключ `NSHealthShareUsageDescription` |
| 3 | `Screens/WellnessCheckinScreen.swift` | Убрать: `healthSleepHint`, кнопку import, `.task { tryAutoHealthSleep }`, функции `tryAutoHealthSleep` / `importSleepFromHealth` |
| 4 | Проверка | `grep -ri healthkit --include='*.swift' --include='*.entitlements' --include='Info.plist' .` — в **shipping** путях только `WellnessHealthSleepReader.swift` (см. ниже) |

### 4.2 Рекомендуется (чистота Review)

| # | Файл | Действие |
|---|------|----------|
| 5 | `Core/Services/WellnessHealthSleepReader.swift` | **Не удалять** — оставить для будущего A; добавить в шапку `@available` / комментарий «disabled until po-healthkit»; **не импортировать** из UI |
| 6 | `Core/Localization/LocalizationManager.swift` | Ключи `wellness_sleep_import_*` можно оставить (не мешают) или пометить deprecated |
| 7 | Xcode target | **Signing & Capabilities** → убедиться, что HealthKit capability **не** висит на target ALADDIN (если добавляли вручную в GUI) |

**Не трогать:** `telegram_stars_shop_bot/`, `.env` — отдельный проект ([no-telegram-bot-in-ios-release.mdc](../.cursor/rules/no-telegram-bot-in-ios-release.mdc)).

### 4.3 Номер сборки

Коммит `95439b21` уже на `origin/master` с build **221** и HealthKit.

| Стратегия | Когда |
|-----------|--------|
| **Bump 221 → 222** (рекомендуется) | Стандартный релизный коммит после отката |
| Оставить **221** в трёх файлах | Только если в App Store Connect **нет** загруженного билда 221 и PO хочет «исправленный 221» |

Три файла bump (как всегда):

- `Info.plist` → `CFBundleVersion`
- `ALADDIN.xcodeproj/project.pbxproj` → 8× `CURRENT_PROJECT_VERSION`
- `Core/Config/AppConfig.swift` → `buildNumber` + `minimumClientBuildForApiContract`

---

## 5. Проверка и тест (после правок, до commit)

### 5.1 Локально

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
git remote -v
git branch --show-current
git status --short
```

```bash
# Entitlement
grep -A1 healthkit ALADDIN.entitlements || echo "OK: no healthkit in entitlements"
grep NSHealthShare Info.plist || echo "OK: no NSHealthShare in Info.plist"
```

### 5.2 Xcode

1. **Product → Clean Build Folder** (⇧⌘K)
2. **Product → Build** (⌘B), scheme **ALADDIN**, Release или Debug
3. Ожидание: **нет** ошибки *Provisioning profile doesn't include HealthKit*
4. Симулятор: **Wellness → Check-in** — ползунок сна работает, **нет** кнопки «Из Health»

### 5.3 Опционально (устройство)

- Archive локально с тем же Distribution profile, что в CI (если есть) — smoke перед push.

### 5.4 CI

- Push в `master` → дождаться workflow **Build and Upload to App Store Connect**
- Успех: шаг **Build Archive with Fastlane** без HealthKit errors

---

## 6. Релиз: commit + push по правилам

Канон:

- Путь: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`
- Ветка: `master`
- Remote: `origin` = `git@github.com:sergey234/ALADDIN_FAMILY.git`

### Перед работой (показать вывод)

```bash
git remote -v
git branch --show-current
git log --oneline -n 3
```

### Перед push (sanity-check)

```bash
git merge-base HEAD origin/master
```

Если **нет hash** → **STOP**, не пушить.

### Staging (без telegram / .env)

```bash
git diff --cached --name-only | grep -E '^telegram_stars_shop_bot/|^\.env$' && echo STOP || echo OK
```

### Commit (пример сообщения)

```
fix(build 222): remove HealthKit entitlement for CI; manual sleep in check-in

Rollback variant B: Wellness check-in keeps sleep slider; no Apple Health import until Portal profile updated (po-healthkit deferred).
```

### Push

```bash
git push origin master
```

Показать hash коммита и строку успешного push.

**Запрещено:** rebase без разрешения, force-push в `master`, смена git config, работа из копий с другим `.git`.

**Если push не fast-forward:** STOP, спросить PO (не rebase, не force).

---

## 7. Документы обновить после выполнения отката

- [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md) — CI green, po-healthkit → deferred
- [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md) — отметить `po-healthkit-rollback-ci` done
- [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md) — статус «откат выполнен» / путь A на будущее

---

## 8. Возврат к варианту A (когда захотите Health снова)

1. Portal: HealthKit ON → App Store profiles с HealthKit + App Groups  
2. GitHub Secrets: `PROVISIONING_PROFILE_APP` (+ extension при необходимости)  
3. Код: вернуть entitlement, `NSHealthShareUsageDescription`, UI import в `WellnessCheckinScreen`  
4. App Review: текст из [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md) §3  
5. Bump build + push по §6  

---

*Связано: p2-36 · po-healthkit · CI logs_71945656834 · build 221 `95439b21`*
