# План: Trial 14д · слоты тарифа · New York serif (Family)

**Дата:** 2026-11-10  
**Статус:** W-pre ✅ · W0+W1 ✅ · premium=15 на MAIN — после деплоя · дальше W2 по GO  

---

## 0. Канон Trial

| Вопрос | Ответ |
|--------|--------|
| Длительность | **14 дней** |
| Старт | Авто после онбординга |
| Пока trial | **ПРОБНЫЙ**, слоты **3** |
| После endDate | Авто → **БАЗОВЫЙ**, слоты **1** + баннер |
| Раньше срока | Confirm → `downgradeToFree` · или сервер one-shot |
| С 7.11 | Должны быть на ПРОБНОМ, пока trial жив |

---

## 1. Лимиты семьи (канон)

| Код | UI | Слоты |
|-----|-----|-------|
| free | БАЗОВЫЙ | **1** |
| trial | ПРОБНЫЙ | **3** |
| personal | ЛИЧНЫЙ | **2** |
| family | СЕМЕЙНЫЙ | **6** |
| premium | ПРЕМИУМ | **15** ← обновлено с 10 |

SSOT iOS: `familyMemberLimitStatic`. Репо: `app/services/family_roster_reconcile.py`.  
**Прод MAIN** (`/opt/aladdin-backend`) — отдельный **GO на деплой** лимита premium=15.

---

## 2. W-pre — статус реализации

| # | Задача | Статус |
|---|--------|--------|
| **W-pre-A** | `effectiveFamilyDisplay` + Main чип/подпись/слоты | ✅ код |
| **W-pre-B** | Баннер конца trial | ✅ код |
| **W-pre-C** | Confirm перед БАЗОВЫЙ во время trial | ✅ код |
| **W-pre-D** | CTA «Вернуть пробный» после раннего downgrade | ✅ код |
| **W-pre-E** | Evidence на Device QA (status/stats/логи) | ⏳ Device QA |
| premium **15** | iOS + reconcile в репо + тест | ✅ код · прод — GO deploy |

---

## 3. New York serif

Канон: Family Hub + двери — заголовки/описания через `AladdinFamilyType` (New York).  
Не трогать `Fonts.h1…bodyBold`. Онбординг body — отдельно. Без mass sed.  
D1.5: helper в `Shared/Styles/Fonts.swift` (enum в конце файла).

| Волна | Что | Риск | Статус |
|-------|-----|------|--------|
| **W0** | `AladdinFamilyType` + docs D1.5 | низкий | ✅ |
| **W1** | WhereIsPhoneScreen (заголовки / таббар / Safety / Subscription / sheets) | средний | ✅ |
| **W2** | DrivingReportsModal | средний | ⏳ |
| **W3** | FamilySafetyRemainderHub → ⏸ Device QA Hub | низкий |
| **W4** | SimpleHomeScreen двери | низкий |
| **W5** | Parental + Child + ParentDashboard | средний |
| **W6** | Antifake / Проверить | средний |
| **W7** | 02_FamilyScreen шапка/секции/Добавить | высокий |
| **финал** | grep; build/push только по GO | |

**Вне scope:** Main grid (кроме карточки W-pre), Settings redesign, онбординг body, bot/VPN, `.ttf`.

---

## 4. Порядок GO

1. ~~GO W-pre~~ → код сделан · нужен **Device QA** карточки семьи  
2. **GO на W0+W1** → serif  
3. После W3 → **GO Device QA Hub**  
4. W4–W7 по волнам  
5. Build / push / deploy premium=15 на MAIN — только отдельным GO  
