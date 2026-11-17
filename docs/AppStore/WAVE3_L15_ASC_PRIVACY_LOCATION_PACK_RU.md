# WAVE3 · L15 — ASC Privacy Nutrition + Review Notes (location)

**ID:** `cap-L15` · **Дата:** 2026-10-17  
**Supersede 2026-11-09 (канон B):** семейная карта + алерты мест + доступ к месту при закрытом приложении для свежей точки; маршрут при движении (Start не обязателен); **тихая зона** не шлёт точку семье; нет следа всего дня дома. В UI/копирайте не пишем слово Always. Полный liability уже в Terms.  
**Supersede 2026-11-17 (build 35, решение владельца):** добавлен `UIBackgroundModes location` **только на время поездки на машине** (Life360-style: км, время, макс. скорость, резкие торможения). Вне поездки — эконом-режим (SLC + геозоны). Review Notes §3 и чеклист §4 обновлены — **вставить заново в ASC перед отправкой build 35**.  
**Цель:** в App Store Connect честно описать геолокацию.  
**Кто закрывает в портале:** владелец (Account Holder / App Manager). Агент готовит текст; галочки в ASC — руками.

---

## 1. Что делает приложение (канон продукта B)

| Есть | Нет |
|------|-----|
| Region monitoring (геозоны дом/школа/секция/друзья/работа) | Круглосуточный след всех точек дня без поездки |
| Enter/exit → local UN + (после L4) APNs родителю | Продажа/реклама по локации |
| Always после opt-in: свежая точка + алерты мест | Скрытый GPS «для аналитики» |
| Актуальное / недавнее место на карте семьи | Тайное включение мимо разрешений iPhone |
| Маршрут (много точек) только Start trip → Stop | |
| Тихая зона: точку семье не отправляем | |
| SOS / «поделиться сейчас» | Soft presence «я в порядке» без GPS |

Purpose strings (уже в билде): `Info.plist` + `ru.lproj` / `en.lproj` `InfoPlist.strings`.

---

## 2. App Privacy (Nutrition Labels) — что поставить

**App Store Connect → App → App Privacy → Edit**

### Location

| Поле | Значение |
|------|----------|
| **Data type** | Precise Location **и/или** Coarse Location |
| **Used for** | **App Functionality** (семейные алерты о местах, SOS) |
| **Linked to user** | **Yes** (привязано к аккаунту / члену семьи) |
| **Used for tracking** | **No** (не Advertising / не Third-Party Advertising / не Tracking) |
| **Collected from** | только после согласия пользователя (системный диалог + in-app opt-in мест) |

Не отмечать Location для: Advertising, Analytics (если нет отдельного продукта на это), Product Personalization через GPS.

### Related (не путать с Location)

| Data | Purpose | Tracking? |
|------|---------|-----------|
| Device ID / User ID | App Functionality (JWT, семья) | No |
| Product Interaction (лимиты, Screen Time parental) | App Functionality | No |
| Other User Content (чат семьи, Im OK) | App Functionality | No |

---

## 3. Review Notes — вставить в ASC (EN, для ревьюера)

```text
LOCATION / FAMILY PLACES / DRIVING TRIPS (build 35)

ALADDIN uses location only for:
1) Family place alerts — region enter/exit (home, school, club, friends, work) after explicit opt-in.
2) Always authorization — only when the user enables family places; explained in-app before the system prompt.
3) SOS / share-location-now — When In Use + temporary Precise Location.
4) Driving trips (family safety) — UIBackgroundModes "location" is used ONLY while a car trip
   is in progress: the trip starts when driving speed is detected (or when the device leaves
   a ~150 m parking geofence) and stops when the car is parked. During the trip we record
   the route, distance, duration, top speed and harsh braking/acceleration, then show a
   "Trip completed" summary. Outside of trips the app returns to battery mode
   (significant-change + region monitoring only); background GPS is switched off.

We do NOT:
- Keep an all-day location trail while the user is not driving
- Collect location for advertising or analytics
- Enable geofence monitoring without parent/adult opt-in and (for adults) “My places for the family”
- Send the point to the family inside a user-defined quiet zone

How to test: grant location "Always", drive (or simulate a drive) above ~20 km/h for 1–2 minutes,
park for a minute — a "Trip completed" notification opens the trip card with map and stats.

Child under 18: places are managed by the parent; no separate child legal signature for geofence alerts.
Soft presence (“I’m OK”) does not use GPS.
```

### RU (для себя / Notes если нужны)

```text
Геолокация — алерты о местах семьи (вход/выход) после явного согласия, SOS «поделиться сейчас»
и поездки на машине. Фоновый GPS (UIBackgroundModes location) включается ТОЛЬКО на время поездки
(старт по скорости или выезду из зоны стоянки ~150 м, стоп при парковке) и выключается после неё.
Нет следа за весь день вне поездок, нет рекламы по локации. Soft presence «я в порядке» без GPS.
```

---

## 4. Чеклист владельца в ASC

- [ ] App Privacy → Location = App Functionality · Linked Yes · Tracking **No**
- [ ] Review Notes → блок LOCATION / DRIVING TRIPS (build 35) выше вставлен **заново**
- [ ] App Privacy → Location: Precise Location отмечен (поездки пишут точный GPS)
- [ ] Privacy Policy на сайте/в приложении не обещает «live track»
- [ ] Сверить с purpose strings в билде (EN plist + RU/EN InfoPlist.strings)

---

## 5. DoD `cap-L15`

| Критерий | Статус |
|----------|--------|
| Текст pack в репо | ✅ этот файл |
| Purpose strings RU/EN | ✅ Info.plist + InfoPlist.strings |
| Галочки в ASC портале | ⏳ владелец |
| Review Notes вставлены в версию | ✅ прод · What’s New build 12: `REVIEW_NOTES_CURRENT.md` (2026-10-19) |

После галочек в ASC — отметить `cap-L15` ✅ в registry.
