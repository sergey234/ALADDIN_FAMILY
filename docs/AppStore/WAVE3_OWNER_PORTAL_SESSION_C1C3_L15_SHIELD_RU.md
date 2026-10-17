# WAVE3 — порталы: клик за кликом (6 задач)

**Кто:** Account Holder / App Manager · Team **B3WGHSWL79** · Bundle main **`ai.aladdin`**  
**Сборка / push:** не нужны.  
**Порядок:** 1 → 2 → 3 → 4 → 5 → 6. Между задачами можно отдыхать.

Перед стартом войдите в Apple ID владельца команды.

| # | Задача | ~мин | Куда |
|---|--------|------|------|
| 1 | App ID Shield Action + заявка Family Controls | 15 | Developer |
| 2 | ASC Privacy → Location (не Tracking) | 10 | App Store Connect |
| 3 | Review Notes (Submit не жать) | 5 | App Store Connect |
| 4 | Форма Critical Alerts | 10 | Developer |
| 5 | Communication Notifications | 10 | Developer |
| 6 | Network Extensions Content Filter (**не VPN**) | 15 | Developer |

В конце — скопируйте блок «Отчёт агенту».

---

# ЗАДАЧА 1 · Shield Action App ID + заявка FC (~15 мин)

**Зачем:** расширение с кнопками «Спросить родителя» / «Закрыть» на щите Screen Time.  
**Bundle:** `ai.aladdin.ShieldAction`  
**Это не** Shield Configuration (`ai.aladdin.ShieldConfiguration`) — тот уже мог быть создан раньше.

## 1A. Создать App ID

### Ссылка
https://developer.apple.com/account/resources/identifiers/list

### Что нажимать

1. Откройте ссылку → войдите.
2. Сверху справа / в меню команды выберите Team с **`ai.aladdin`** / **B3WGHSWL79**.
3. Слева должно быть **Identifiers** (если нет — Certificates, Identifiers & Profiles → Identifiers).
4. Нажмите синюю кнопку **`+`** (слева вверху у списка).
5. Выберите **App IDs** → **Continue**.
6. Тип: **App** → **Continue**.
7. Заполните поля:

| Поле на экране | Что вписать |
|----------------|-------------|
| Description | `ALADDIN Shield Action` |
| Bundle ID | переключатель **Explicit** |
| Bundle ID (поле) | `ai.aladdin.ShieldAction` |

8. В длинном списке Capabilities **пока ничего не включайте** (Family Controls появится после Assigned).
9. **Continue** → проверьте Bundle ID → **Register**.
10. **Done**.

### Проверка
В списке Identifiers должна быть строка **`ai.aladdin.ShieldAction`**.

Если Apple пишет *Bundle ID is not available / already exists* — ID уже есть. **Не создавайте снова.** Переходите к **1B**.

---

## 1B. Заявка Family Controls Distribution на этот Bundle

### Ссылка
https://developer.apple.com/contact/request/family-controls-distribution

### Что нажимать

1. Откройте ссылку → войдите как **Account Holder**.
2. Выберите команду **B3WGHSWL79**.
3. Примите условия формы (родительский контроль / не реклама / не MDM) — как при прошлых заявках на Monitor/Report.
4. В полях формы укажите примерно так:

| Поле (названия могут чуть отличаться) | Значение |
|----------------------------------------|----------|
| App / product name | `ALADDIN` |
| Bundle ID | **`ai.aladdin.ShieldAction`** ← не `ai.aladdin` |
| App Store Connect Apple ID | тот же числовой ID приложения, что для main (ASC → App Information → Apple ID) |

5. В большое текстовое поле **вставьте целиком** (EN):

```text
ALADDIN is a family safety app. A parent uses ALADDIN to set age-appropriate
rules on a child’s device: allowed apps/categories, schedules, and limits.

We request the Family Controls distribution entitlement so ALADDIN can use
Apple Screen Time APIs (FamilyControls, ManagedSettings, DeviceActivity) to:
1) request Screen Time authorization on the child’s device;
2) apply app/category shields chosen by the parent;
3) enforce schedules/limits via Device Activity Monitor;
4) show usage via Device Activity Report for parental insights;
5) show a system shield screen via Shield Configuration;
6) handle Shield Action (Ask Parent / dismiss) when a child requests unlock.

Screen Time data is used only for parental controls and app functionality.
It is not used for advertising, cross-app tracking, or sale to third parties.
The parent initiates and can disable these controls.

This request is for the Shield Action extension
(bundle id: ai.aladdin.ShieldAction), which handles Ask Parent / Close
actions on the system shield UI.
```

6. Нажмите **Submit** / **Send**.
7. Запишите **Request ID** (как было `952MH6KQWS` у main):

| Поле | Ваша запись |
|------|-------------|
| Request ID | ________________ |
| Дата | ________________ |

### Где потом смотреть статус
https://developer.apple.com/account/resources/identifiers/list  
→ откройте `ai.aladdin.ShieldAction` → вкладка **Capability Requests** / раздел Family Controls  
или общий список Capability Requests в аккаунте.

Пока статус не **Assigned** — profiles/secrets (блок 7 внизу) **не** делаем.

### Чеклист задачи 1
- [ ] App ID `ai.aladdin.ShieldAction` есть в списке  
- [ ] Заявка FC отправлена  
- [ ] Request ID записан  

---

# ЗАДАЧА 2 · ASC Privacy → Location (~10 мин)

**Зачем:** в карточке App Store честно: геолокация = алерты о местах, **не** рекламный трекинг.  
**ID плана:** L15.

## Ссылки

1. Войти в ASC: https://appstoreconnect.apple.com  
2. Прямой вход в Privacy (после выбора приложения часто так):  
   https://appstoreconnect.apple.com/apps → выберите **ALADDIN** / ALADDIN AI → слева **App Privacy**

## Что нажимать

1. Откройте https://appstoreconnect.apple.com → войдите.
2. Нажмите **Apps** (Мои приложения).
3. Откройте приложение **ALADDIN** (bundle `ai.aladdin`, team B3WGHSWL79).
4. В левом меню нажмите **App Privacy** (Конфиденциальность приложения).
5. Нажмите **Edit** / **Get Started** / **Manage** (кнопка редактирования ответов).
6. Найдите тип данных **Location** / **Местоположение**:
   - **Precise Location** и/или **Coarse Location** — отметьте то, что реально используете (у нас есть Always/WhenInUse → обычно оба или Precise + Coarse по факту ASC).
7. Для Location ответьте:

| Вопрос ASC (смысл) | Ваш ответ |
|--------------------|-----------|
| Зачем собираете? | **App Functionality** / Функциональность приложения |
| Связано с личностью пользователя? | **Yes** / Да |
| Используется для Tracking (реклама cross-app)? | **No** / Нет |

8. **Не** отмечайте для Location цели: Advertising, Third-Party Advertising, Analytics (если ASC спрашивает отдельно — не ставьте).
9. Пройдите остальные экраны мастера до конца → **Save** / **Publish** ответы Privacy.

### Если Location уже был заполнен
Edit → откройте Location → поправьте цели на **App Functionality** · Linked **Yes** · Tracking **No** → Save.

### Чеклист задачи 2
- [ ] Location = App Functionality  
- [ ] Linked to user = Yes  
- [ ] Used for Tracking = **No**  
- [ ] Сохранено / опубликовано в ASC  

---

# ЗАДАЧА 3 · Review Notes вставить (~5 мин)

**Зачем:** ревьюер Apple читает Notes. Submit for Review **не** нажимать.  
**ID:** H2 + кусок L15.

## Ссылка
https://appstoreconnect.apple.com/apps  
→ ALADDIN → вкладка **Distribution** / **App Store** → версия **1.0.1** (или текущая) → прокрутите до **App Review Information**.

## Что нажимать

1. https://appstoreconnect.apple.com → **Apps** → **ALADDIN**.
2. Слева или сверху: **Distribution** / **App Store** (не TestFlight).
3. Откройте версию iOS **1.0.1** (клик по версии в списке).
4. Прокрутите вниз до блока **App Review Information** (Информация для App Review).
5. Найдите поле **Notes** (Примечания).
6. **Сотрите старое** только если уверены; лучше **добавьте в конец** новый блок.
7. Вставьте **целиком** текст ниже (EN).
8. Нажмите **Save** вверху справа у версии.
9. **Не** нажимайте:
   - **Add for Review**
   - **Submit to App Review**
   - **Submit for Review**

## Текст для вставки (скопировать)

```text
ALADDIN FAMILY — REVIEW NOTES (WAVE3 / build 10+)

WHAT THE APP IS
Family safety: parental Screen Time limits (FamilyControls), family place alerts (geofence enter/exit), soft presence (“I’m OK” without GPS), SOS share-location-now, anti-scam / elderly alerts (ordinary push). Optional AI companion with parental gate.

SCREEN TIME / FAMILY CONTROLS
Uses Apple FamilyControls + DeviceActivity + ManagedSettings + Shield.
Shield Action (ask parent / dismiss) uses the same Family Controls entitlement.
Usage minutes sync parent↔child for parental control only — not advertising, not third-party tracking.
System Family Controls may be gated in some builds until Device QA; UI shows honest empty / setup states (no fake minutes).

LOCATION / FAMILY PLACES
ALADDIN uses location only for:
1) Family place alerts — region enter/exit (home, school, club, friends, work) after explicit opt-in.
2) Always authorization — only when the user enables family places; explained in-app before the system prompt.
3) SOS / share-location-now — When In Use + temporary Precise Location; not continuous.
We do NOT use UIBackgroundModes "location", continuous GPS, route lines, or location for ads.
Adult members opt in via “My places for the family”. Soft presence (“I’m OK”) does not use GPS.

PUSH
Ordinary local + remote notifications for family alerts.
Critical Alerts / Communication Notifications — only after Apple entitlement Assigned. Until then we do not claim critical delivery.

NETWORK / FILTER
No in-app Packet Tunnel VPN. System Content Filter (if enabled later) is parental web filter only — not VPN.

WE DO NOT
- Call recording
- MDM / device supervision
- Silent GPS analytics
- Fake Screen Time statistics
```

### Чеклист задачи 3
- [ ] Notes вставлены и **Save**  
- [ ] Submit for Review **не** нажимали  

---

# ЗАДАЧА 4 · Critical Alerts (C1) (~10 мин)

**Зачем:** пуши, которые могут звучать при «беззвучном» / Focus — для SOS / падение / срочный скам.  
**Не блокер** обычных пушей геозон (L4 уже на сервере).  
До одобрения в коде флаг **выключен**.

## Способ A (прямая форма) — начните с него

### Ссылка
https://developer.apple.com/contact/request/notifications-critical-alerts-entitlement/

### Что нажимать

1. Откройте ссылку → войдите **Account Holder**.
2. Team **B3WGHSWL79**.
3. Заполните форму (поля могут называться по-разному):

| Смысл поля | Что писать |
|------------|------------|
| App name | `ALADDIN` |
| Bundle ID | `ai.aladdin` |
| Why / use case | вставьте текст ниже |

4. Текст:

```text
ALADDIN is a family safety app. Critical Alerts are required so caregivers
receive time-sensitive notifications when an elderly member triggers SOS /
fall detection, or when a high-risk scam call is detected — including when
the phone is silenced. Not used for marketing, engagement, or news.

We already ship ordinary push and local notifications. Critical is only for
predefined high-urgency family categories (SOS, fall, urgent scam).
The user can disable Critical Alerts in iOS Settings.
```

5. **Submit**.
6. Request ID / confirmation: _______________

## Способ B (если ссылка 404 / «нет доступа»)

1. https://developer.apple.com/account/resources/identifiers/list  
2. Откройте App ID **`ai.aladdin`** (клик по имени).  
3. Вкладка **Capability Requests** (Запросы возможностей).  
4. Найдите **Critical Alerts** → кнопка **Request**.  
5. Заполните форму тем же текстом → Submit.  

Справка Apple: https://developer.apple.com/help/account/capabilities/capability-requests/

### Чеклист задачи 4
- [ ] Форма Critical Alerts отправлена  
- [ ] ID / дата записаны  

---

# ЗАДАЧА 5 · Communication Notifications (C2) (~10 мин)

**Зачем:** уведомления «как входящий» для меток скам/спам (связка с Call Directory).  
**Не** маркетинг-чат.

Отдельной короткой public-URL формы часто нет — используйте Capability Requests на App ID.

## Ссылка (старт)
https://developer.apple.com/account/resources/identifiers/list

## Что нажимать

1. Откройте список Identifiers (ссылка выше).
2. Team **B3WGHSWL79**.
3. Кликните **`ai.aladdin`** (main app, не Shield Action).
4. Откройте вкладку **Capability Requests**.
5. Найдите **Communication Notifications**.
6. Нажмите **Request**.
7. В форме укажите Bundle `ai.aladdin` и вставьте:

```text
ALADDIN is a family safety app. We request Communication Notifications to
present clearer incoming-call style UI for numbers identified as scam/spam
via Call Directory, for family protection only.

Not used for advertising, marketing chat, or engagement campaigns.
```

8. **Submit**.
9. Request ID: _______________

### Если вкладки Capability Requests нет
1. https://developer.apple.com/contact/  
2. Contact Us / Account Holder forms → найдите Communication Notifications / Notifications.  
3. Тот же текст → Submit.

Справка: https://developer.apple.com/help/account/capabilities/capability-requests/  
Документация: https://developer.apple.com/documentation/usernotifications/implementing-communication-notifications

### Чеклист задачи 5
- [ ] Request отправлен  
- [ ] ID записан  

---

# ЗАДАЧА 6 · Content Filter / Network Extensions — **не VPN** (~15 мин)

**Зачем:** системный фильтр сайтов «вне Safari» (родительский).  
**Запрещено включать:** Packet Tunnel / VPN / Personal VPN.

> Важно: Content Filter на iOS часто **включается на App ID без отдельной «магической» формы** (self-serve Network Extensions).  
> Отдельная форма нужна не всегда. Наша цель сейчас: **правильно отметить capability и явно не трогать VPN**.  
> Код фильтра (F2) — **позже**, после Assigned FC и финальной сборки. Сейчас только портал.

## 6A. Включить Network Extensions на main (без tunnel)

### Ссылка
https://developer.apple.com/account/resources/identifiers/list

### Что нажимать

1. Откройте Identifiers.
2. Кликните **`ai.aladdin`**.
3. Нажмите **Edit** / карандаш (если нужно).
4. В списке Capabilities найдите **Network Extensions**.
5. Поставьте галочку **Network Extensions**.
6. В подпунктах / модалке (если Apple показывает типы) отметьте только то, что про **Content Filter** / content-filter-provider.  
   - **НЕ** отмечайте Packet Tunnel / VPN / Personal VPN.
7. Если отдельного чекбокса Content Filter нет — включите Network Extensions и **не** добавляйте VPN capability отдельно.
8. **Save** / **Continue** → подтвердите.

## 6B. Capability Request (если Apple просит Request)

1. На том же `ai.aladdin` → вкладка **Capability Requests**.  
2. Если есть **Network Extensions** / **Content Filter** / **URL Filter** с кнопкой **Request** — нажмите.  
3. В текст вставьте:

```text
ALADDIN is a family safety app. We request Network Extension Content Filter
so parents can apply domain/web rules beyond Safari (system-wide parental
filtering on the child’s device where Apple allows it with Screen Time /
family controls).

We explicitly do NOT request Packet Tunnel VPN.
VPN connectivity remains via the user’s existing client (outside this app).
Filter rules come from parent settings only. Not used for advertising or tracking.
```

4. Submit → ID: _______________

## 6C. Чего не делать

| Не нажимать / не включать | Почему |
|---------------------------|--------|
| Personal VPN | это VPN |
| Packet Tunnel | запрет WAVE3 |
| Hotspot Helper «заодно» | не нужно |

Справка NE: https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.networkextension  
TN3134 (content filter + Screen Time): https://developer.apple.com/documentation/technotes/tn3134-network-extension-provider-deployment

### Чеклист задачи 6
- [ ] Network Extensions на `ai.aladdin` рассмотрены / включены **без** Packet Tunnel  
- [ ] Если был Request — отправлен, ID записан  
- [ ] VPN **не** включали  

---

# ПОТОМ (не сегодня) · После Assigned Shield Action

Когда Family Controls для `ai.aladdin.ShieldAction` = **Assigned**:

1. Identifiers → `ai.aladdin.ShieldAction` → включить **Family Controls** + App Group **`group.ai.aladdin`** → Save.  
   Список: https://developer.apple.com/account/resources/identifiers/list  
2. Profiles → `+` → App Store → этот App ID → Generate → Download.  
   https://developer.apple.com/account/resources/profiles/list  
3. GitHub secret `PROVISIONING_PROFILE_ST_SHIELD_ACTION` (+ UUID) — как у Shield Configuration.  
4. Написать агенту: **`Shield Action secret готов`** (push всё равно в финале).

---

# Итоговый чеклист дня

- [ ] **1** App ID + FC заявка Shield Action  
- [ ] **2** ASC Privacy Location (не Tracking)  
- [ ] **3** Review Notes Saved (без Submit)  
- [ ] **4** Critical Alerts отправлено  
- [ ] **5** Communication Notifications отправлено  
- [ ] **6** NE Content Filter / без VPN  

Параллельно на телефонах: walk-test геозон (L4 на MAIN уже).

---

# Отчёт агенту (скопируйте и заполните)

```text
PORTAL SESSION DONE:
- 1 ShieldAction App ID: yes/no · FC request ID: ____
- 2 ASC Privacy Location (App Functionality, Tracking No): yes/no
- 3 Review Notes Saved (no Submit): yes/no
- 4 C1 Critical Alerts ID: ____
- 5 C2 Communication Notifications ID: ____
- 6 C3 NE Content Filter / NE enabled without VPN: yes/no · request ID: ____
- Walk-test geo: PASS/FAIL — ____
```
