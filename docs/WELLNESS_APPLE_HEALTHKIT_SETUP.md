# Apple HealthKit — включение capability (p2-36)

> **Контекст:** ранее HealthKit был **удалён** из сборки по требованию App Review (декабрь 2025).  
> С **Wellness p2-36** снова нужен **только read sleep** для prefill check-in — без PPG, без диагнозов.

---

## 1. Что уже в репозитории (код)

| Файл | Назначение |
|------|------------|
| `ALADDIN.entitlements` | `com.apple.developer.healthkit` = true |
| `Info.plist` | `NSHealthShareUsageDescription` (ru текст) |
| `Core/Services/WellnessHealthSleepReader.swift` | чтение сна за прошлую ночь |
| `Screens/WellnessCheckinScreen.swift` | кнопка «Из Health» + prefill `sleep_hours` |

**Нет** `NSHealthUpdateUsageDescription` — приложение **не пишет** в Health.

---

## 2. Apple Developer Portal (ручные шаги PO)

1. [developer.apple.com](https://developer.apple.com) → **Certificates, Identifiers & Profiles**
2. **Identifiers** → App ID `com.aladdin.family` (или ваш bundle id)
3. **Capabilities** → включить **HealthKit**
4. **Save** → пересоздать **Provisioning Profile** (Development + Distribution)
5. Xcode → **Signing & Capabilities** → выбрать новый profile
6. Убедиться, что capability **HealthKit** видна в target ALADDIN (не дублировать в extension без нужды)

**Статус репозитория (2026-06-01):** код + entitlements + `WellnessHealthSleepReader` ✅ · **осталось PO:** шаги 2–5 в Developer Portal.

---

## 3. App Store Connect / Review

При следующей отправке билда **обновить ответ Review** (ранее писали «HealthKit удалён»):

**RU (кратко):**  
«В версии X.Y добавлена опциональная интеграция HealthKit: пользователь может **по желанию** подставить часы сна из Apple Health в ежедневный check-in эмоциональной поддержки. Данные не используются для диагноза и не передаются третьим лицам вне защищённого API ALADDIN.»

**EN:**  
«Optional HealthKit read (sleep duration) prefills a self-help mood check-in. Not used for medical diagnosis. User-initiated permission only.»

Ссылка на политику: Privacy Policy + in-app disclaimer `wellness_*`.

---

## 4. Проверка на устройстве

1. Собрать на **реальном iPhone** (симулятор Health ограничен)
2. Wellness → Check-in → «Из Health» / import sleep
3. Системный диалог Health → Allow
4. Поле сна заполнилось (часы, 0.5 шаг)

Если capability не в profile — Xcode: *Provisioning profile doesn't include HealthKit entitlement*.

---

## 5. Откат (если Review снова отклонит)

1. Убрать entitlement из `ALADDIN.entitlements`
2. Обернуть UI import в `#if canImport(HealthKit)` + feature flag `FEATURE_WELLNESS_HEALTHKIT=0` на backend не нужен
3. Оставить ручной ввод сна в check-in

---

*Связано: p2-36 · [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md)*
