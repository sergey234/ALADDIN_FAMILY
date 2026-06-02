# Apple HealthKit — capability (p2-36)

> **Обновлено:** 2026-06-02  
> **Активный план PO:** 📋 **отложен** — сначала [WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md) (вариант B, без Portal).  
> **Вариант A** (этот файл, §2–4) — когда решите вернуть автозаполнение сна из Health.

---

## Контекст

| Дата | Событие |
|------|---------|
| Дек 2025 | HealthKit **удалён** по App Review |
| Июн 2026 | Wellness p2-36: **только read sleep** для prefill check-in |
| Build 221 `95439b21` | Entitlement снова в репо |
| CI `logs_71945656834` | Archive **FAILED**: profile без HealthKit |
| **Сейчас** | Код с HealthKit в `master`; **исполнение отката — позже** |

HealthKit в ALADDIN = **одна функция**: подставить **часы сна** в Wellness check-in. Без HealthKit check-in **полностью работает** (ползунок вручную).

---

## Вариант B — откат (рекомендован для ближайшего CI)

**Полный пошаговый план:** [WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md)

Кратко:

1. Убрать `com.apple.developer.healthkit` из `ALADDIN.entitlements`
2. Убрать `NSHealthShareUsageDescription` из `Info.plist`
3. Убрать import UI из `WellnessCheckinScreen.swift`
4. Clean Build → Build в Xcode → commit → push (правила релиза в плане §6)
5. Bump build (**222** рекомендуется после 221 с HealthKit)

**Не требует:** Apple Developer Portal, обновление GitHub Secrets.

---

## Вариант A — включить HealthKit (когда будете готовы)

### 1. Что в репозитории (после отката B нужно будет вернуть)

| Файл | Назначение |
|------|------------|
| `ALADDIN.entitlements` | `com.apple.developer.healthkit` = true |
| `Info.plist` | `NSHealthShareUsageDescription` |
| `Core/Services/WellnessHealthSleepReader.swift` | чтение сна за ~24 ч |
| `Screens/WellnessCheckinScreen.swift` | кнопка «Из Health» + prefill |

**Нет** `NSHealthUpdateUsageDescription` — приложение **не пишет** в Health.

### 2. Apple Developer Portal (PO)

1. [developer.apple.com](https://developer.apple.com) → **Certificates, Identifiers & Profiles**
2. **Identifiers** → App ID (`family.aladdin.ios` / ваш bundle id)
3. **Capabilities** → **HealthKit** → Save
4. **Profiles** → **App Store** (не Development / Ad Hoc):
   - App: HealthKit + App Groups (`group.com.aladdin.family`)
   - Extension `…ALADDINContentBlocker`: App Groups
5. Связать с **Apple Distribution: SERGEY KHLYSTOV**
6. Обновить GitHub Secrets: `PROVISIONING_PROFILE_APP`, `PROVISIONING_PROFILE_EXTENSION`

### Профили App Store (отдельно от HealthKit)

CI также предупреждал: secrets могут содержать **Development/Ad Hoc** профили (есть `ProvisionedDevices`). Для TestFlight нужны **App Store Distribution** профили **без** списка устройств — пересоздать при варианте A.

### 3. App Store Connect / Review

При отправке билда **с HealthKit** обновить ответ Review (раньше писали «HealthKit удалён»):

**RU:**  
«Опционально: пользователь может подставить часы сна из Apple Health в check-in эмоциональной поддержки. Не для диагноза. Только по разрешению пользователя.»

**EN:**  
«Optional HealthKit read (sleep duration) prefills a self-help mood check-in. Not medical diagnosis. User-initiated only.»

### 4. Проверка на устройстве

1. Реальный iPhone
2. Wellness → Check-in → «Из Health»
3. Allow → ползунок заполнился

Ошибка profile: *Provisioning profile doesn't include HealthKit entitlement*.

---

## Статус задач

| ID | Статус | Комментарий |
|----|--------|-------------|
| p2-36 (код) | ✅ в репо | Sleep reader + UI (до отката B) |
| po-healthkit (Portal A) | ⏸ отложено | См. rollback plan B |
| po-healthkit-rollback-ci | 📋 запланировано | [WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md) |

---

*Связано: [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md) · [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md)*
