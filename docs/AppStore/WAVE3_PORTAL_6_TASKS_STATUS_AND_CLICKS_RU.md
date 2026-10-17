# WAVE3 — 6 задач портала: что уже сделали + куда жать

**Проверка по репо / журналам:** 2026-10-17  
**Важно:** агент **не видит** живой Developer / ASC. Ниже — факты из документов и registry.  
Если в портале что-то уже сделали руками и не записали Request ID — откройте список и сверьте.

---

## Итог: делали или нет?

| # | Задача | В коде / docs | В портале Apple | Вердикт |
|---|--------|---------------|-----------------|--------|
| **1** | App ID `ai.aladdin.ShieldAction` + заявка FC | Код расширения ✅ | App ID ✅ · FC **`7KCSST4S7T`** · письмо **Assigned** FC Distribution 2026-10-17 | **Assigned** → включить на Shield Action + profile |
| **1b** | FC на main / Monitor | — | Main `952MH6KQWS` · Monitor `L2B4G3Y82L` (2026-10-16) | **Уже подавали** (другое, не Shield Action) |
| **1c** | App ID Monitor / Report / Shield**Configuration** | — | Инструкция была; Report/ShieldConfig ID в таблице **пусты** | **Проверить в Identifiers** — могли создать без записи |
| **2** | ASC Privacy Location (WAVE3: не Tracking) | Pack L15 ✅ | Precise/Coarse + User ID + Other Content · Func · Linked Yes · Tracking No · Publish 2026-10-17 | **Сделано** |
| **2b** | App Privacy вообще (старое, 2025) | Старые чеклисты «готово» | Могли заполнять год назад | **Не считать WAVE3 закрытым** |
| **3** | Review Notes WAVE3 | Pack H2 ✅ | Владелец: Save **отложил** до сборки / Submit | **Отложено** (осознанно) |
| **4** | Critical Alerts форма | Draft ✅ | Request ID **`VX53USXWCJ`** (2026-10-17) | **Сделано** (ждём Apple) |
| **5** | Communication Notifications | Draft ✅ | Галочка Enabled на `ai.aladdin` (форма не нужна) | **Сделано** |
| **6** | NE Content Filter (не VPN) | Explainer + draft ✅ | Network Extensions On · Personal VPN Off · подтипы UI нет | **Сделано** |

**Коротко (после сессии владельца 2026-10-17):** портал 1·2·4·5·6 ✅ · Notes (3) отложены до сборки/Submit · ждём Apple Assigned на FC Shield Action + Critical Alerts.

---

# Как проверить за 2 минуты (перед работой)

### A. Identifiers
Откройте: https://developer.apple.com/account/resources/identifiers/list  
Team **B3WGHSWL79**. Есть ли строки:

- [ ] `ai.aladdin`
- [ ] `ai.aladdin.DeviceActivityMonitor`
- [ ] `ai.aladdin.DeviceActivityReport`
- [ ] `ai.aladdin.ShieldConfiguration`
- [ ] `ai.aladdin.ShieldAction` ← **задача 1**

Если Shield Action **уже есть** — пропускайте создание App ID, сразу заявка FC (если ещё не подана).

### B. Capability Requests / Family Controls
https://developer.apple.com/account → Certificates, Identifiers & Profiles → Capability Requests  
или форма истории FC. Есть ли заявка именно на **`ai.aladdin.ShieldAction`**?

### C. ASC Privacy
https://appstoreconnect.apple.com → Apps → ALADDIN → App Privacy → Location:  
Tracking = **No**? App Functionality?

### D. Review Notes
Версия 1.0.1 → App Review Information → Notes: есть блок «WAVE3» / «FAMILY PLACES»?

---

# ЗАДАЧА 1 · Shield Action App ID + заявка FC

## Зачем
Кнопки «Спросить родителя» на щите Screen Time. Без App ID и FC Apple не подпишет расширение в Store.

## Было / будет
- **Было:** код есть; в CI без профиля расширение skip; FC заявки были на **main** и **Monitor**, не на Shield Action.  
- **Будет:** после Assigned + profile + финальной сборки — кнопки в IPA.

## Куда зайти и что нажать

### Шаг 1.1 — создать App ID (если ещё нет)

1. Откройте: https://developer.apple.com/account/resources/identifiers/list  
2. Войдите → команда **B3WGHSWL79**.  
3. Нажмите **`+`**.  
4. Выберите **App IDs** → **Continue**.  
5. Тип **App** → **Continue**.  
6. Впишите:
   - Description: `ALADDIN Shield Action`
   - Bundle ID: **Explicit**
   - Поле: `ai.aladdin.ShieldAction`
7. Capabilities пока не трогайте → **Continue** → **Register** → **Done**.  
8. Если «already exists» → App ID есть → сразу Шаг 1.2.

### Шаг 1.2 — заявка Family Controls

1. Откройте: https://developer.apple.com/contact/request/family-controls-distribution  
2. Bundle ID: **`ai.aladdin.ShieldAction`** (не `ai.aladdin`).  
3. Имя приложения: `ALADDIN`.  
4. App Store Connect Apple ID — как для main.  
5. Вставьте EN-текст из  
   `WAVE3_OWNER_PORTAL_SESSION_C1C3_L15_SHIELD_RU.md` §1B  
   (блок про Shield Action Ask Parent / Close).  
6. **Submit**.  
7. Запишите Request ID: _______________

### Не делать
- Не подавать ещё раз FC на `ai.aladdin` (main уже `952MH6KQWS`).  
- Не путать с `ai.aladdin.ShieldConfiguration`.

---

# ЗАДАЧА 2 · ASC Privacy → Location

## Зачем
Честно сказать стору: геолокация для мест семьи / SOS, **не** рекламный Tracking.

## Было / будет
- **Было:** общие App Privacy могли заполнять в 2025; WAVE3-формулировка «alerts not track» в ASC **не закрыта**.  
- **Будет:** Location = App Functionality · Linked Yes · Tracking **No**.

## Куда зайти и что нажать

1. https://appstoreconnect.apple.com → войдите.  
2. **Apps** → приложение **ALADDIN** (`ai.aladdin`).  
3. Слева **App Privacy**.  
4. **Edit** / Manage.  
5. Найдите **Location** (Precise и/или Coarse).  
6. Выставьте:
   - Purpose: **App Functionality**
   - Linked to User: **Yes**
   - Used for Tracking: **No**
7. Не ставьте Advertising / Analytics на Location.  
8. **Save** / **Publish**.

### Уже совпадает?
Если уже так — отметьте ✅ и напишите агенту «Privacy Location WAVE3 OK». Иначе поправьте.

---

# ЗАДАЧА 3 · Review Notes

## Зачем
Ревьюер читает Notes → меньше вопросов про Always Location / «это MDM?».

## Было / будет
- **Было:** pack текста готов в репо; вставка в ASC ⏳.  
- **Будет:** Notes сохранены; Submit **не** нажат.

## Куда зайти и что нажать

1. ASC → **Apps** → **ALADDIN**.  
2. **App Store** / Distribution → версия **1.0.1**.  
3. Прокрутите до **App Review Information**.  
4. Поле **Notes** → вставьте текст из  
   `WAVE3_OWNER_PORTAL_SESSION_C1C3_L15_SHIELD_RU.md` §3  
   (или `WAVE3_H2_REVIEW_NOTES_ASC_PACK_RU.md` + LOCATION из L15).  
5. Вверху **Save**.  
6. **Не** нажимайте Submit / Add for Review.

---

# ЗАДАЧА 4 · Critical Alerts (C1)

## Зачем
Право на «громкий» пуш при беззвучном / Focus для SOS / падение / срочный скам.  
Геозоны **уже** могут идти обычным пушем (L4) — Critical не обязателен для walk-test.

## Было / будет
- **Было:** только draft в репо; форма не отправлена.  
- **Будет:** заявка Submitted; в коде Critical всё ещё выключен до Assigned.

## Куда зайти и что нажать

### Вариант A
1. https://developer.apple.com/contact/request/notifications-critical-alerts-entitlement/  
2. Bundle `ai.aladdin` → текст из §4 файла OWNER_PORTAL → **Submit** → ID.

### Вариант B (если A 404)
1. https://developer.apple.com/account/resources/identifiers/list  
2. Клик **`ai.aladdin`**.  
3. Вкладка **Capability Requests**.  
4. **Critical Alerts** → **Request** → тот же текст → Submit.

---

# ЗАДАЧА 5 · Communication Notifications (C2)

## Зачем
UI уведомления «как входящий» для скам/спам + Call Directory. Не реклама.

## Было / будет
- **Было:** draft; submit не делали.  
- **Будет:** заявка Submitted; UI в приложении позже (E1).

## Куда зайти и что нажать

1. https://developer.apple.com/account/resources/identifiers/list  
2. Клик **`ai.aladdin`**.  
3. **Capability Requests**.  
4. **Communication Notifications** → **Request**.  
5. Текст из §5 OWNER_PORTAL → Submit → ID.

Справка: https://developer.apple.com/help/account/capabilities/capability-requests/

---

# ЗАДАЧА 6 · Content Filter / NE (не VPN)

## Зачем
Подготовить системный фильтр сайтов шире Safari. **VPN / Packet Tunnel не включать.**

## Было / будет
- **Было:** Safari Content Blocker работает; системный NE Filter не ship; портал не подтверждён.  
- **Будет:** capability Content Filter на App ID; код фильтра — позже (F2), не сегодня.

## Куда зайти и что нажать

1. https://developer.apple.com/account/resources/identifiers/list  
2. Клик **`ai.aladdin`** → Edit.  
3. Найдите **Network Extensions** → включите.  
4. Если спрашивают тип: только **Content Filter**.  
   - **Не** Packet Tunnel  
   - **Не** Personal VPN  
5. **Save**.  
6. Если есть **Capability Requests** → Content Filter / NE с кнопкой **Request** — нажмите, текст из §6B («NOT Packet Tunnel») → Submit.

Пояснение простыми словами: `WAVE3_CONTENT_FILTER_NE_EXPLAINED_RU.md`.

---

# Чеклист дня + отчёт

- [x] 1 ShieldAction App ID + FC request ID **`7KCSST4S7T`**  
- [x] 2 Privacy Location WAVE3 OK (Publish 2026-10-17)  
- [ ] 3 Notes Saved — **отложено** до сборки / Submit (owner 2026-10-17)  
- [x] 4 Critical Alerts Request ID **`VX53USXWCJ`**  
- [x] 5 Comm Notifications Enabled (no Request ID)  
- [x] 6 NE On · Personal VPN Off  

```text
PORTAL SESSION DONE (2026-10-17):
- ShieldAction App ID: created · FC ID: 7KCSST4S7T
- Privacy Location Tracking=No: yes (Published)
- Review Notes Saved: no (deferred until build/submit)
- C1 Critical ID: VX53USXWCJ
- C2 Comm: Enabled on ai.aladdin (no form)
- C3 NE without VPN: yes · Personal VPN off · subtypes N/A
```

Тексты для копипаста: [`WAVE3_OWNER_PORTAL_SESSION_C1C3_L15_SHIELD_RU.md`](WAVE3_OWNER_PORTAL_SESSION_C1C3_L15_SHIELD_RU.md)
