# WAVE3 · L15 — ASC Privacy Nutrition + Review Notes (location)

**ID:** `cap-L15` · **Дата:** 2026-10-17  
**Цель:** в App Store Connect честно описать геолокацию как **алерты о местах семьи**, не continuous tracking.  
**Кто закрывает в портале:** владелец (Account Holder / App Manager). Агент готовит текст; галочки в ASC — руками.

---

## 1. Что делает приложение (канон продукта)

| Есть | Нет |
|------|-----|
| Region monitoring (геозоны дом/школа/секция/друзья/работа) | Live-трек 24/7 |
| Enter/exit → local UN + (после L4) APNs родителю | `UIBackgroundModes: location` |
| Always — только после opt-in мест + системный Always | Скрытый GPS «для аналитики» |
| SOS / «поделиться сейчас» — When In Use + Precise кратко | Продажа/реклама по локации |
| Soft presence «я в порядке» — **без GPS** | Трекинг без тумблера члена семьи |

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
LOCATION / FAMILY PLACES (WAVE3)

ALADDIN uses location only for:
1) Family place alerts — region enter/exit (home, school, club, friends, work) after explicit opt-in.
2) Always authorization — only when the user enables family places; explained in-app before the system prompt.
3) SOS / share-location-now — When In Use + temporary Precise Location; not continuous.

We do NOT:
- Use UIBackgroundModes "location"
- Continuously track or draw a route line
- Collect location for advertising or analytics
- Enable geofence monitoring without parent/adult opt-in and (for adults) “My places for the family”

Child under 18: places are managed by the parent; no separate child legal signature for geofence alerts.
Soft presence (“I’m OK”) does not use GPS.
```

### RU (для себя / Notes если нужны)

```text
Геолокация — только алерты о местах семьи (вход/выход) после явного согласия
и SOS «поделиться сейчас». Нет continuous GPS, нет UIBackgroundModes location,
нет рекламы по локации. Soft presence «я в порядке» без GPS.
```

---

## 4. Чеклист владельца в ASC

- [ ] App Privacy → Location = App Functionality · Linked Yes · Tracking **No**
- [ ] Review Notes → блок LOCATION выше вставлен
- [ ] Privacy Policy на сайте/в приложении не обещает «live track»
- [ ] Сверить с purpose strings в билде (EN plist + RU/EN InfoPlist.strings)

---

## 5. DoD `cap-L15`

| Критерий | Статус |
|----------|--------|
| Текст pack в репо | ✅ этот файл |
| Purpose strings RU/EN | ✅ Info.plist + InfoPlist.strings |
| Галочки в ASC портале | ⏳ владелец |
| Review Notes вставлены в версию | ⏳ владелец (до Submit) |

После галочек в ASC — отметить `cap-L15` ✅ в registry.
