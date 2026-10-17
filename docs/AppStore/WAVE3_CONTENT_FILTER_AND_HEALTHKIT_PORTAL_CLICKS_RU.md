# WAVE3 — Content Filter App ID + (опц.) HealthKit: куда жать

**Дата:** 2026-10-17 · Team **B3WGHSWL79** · App `ai.aladdin`  
**Зачем:** вшить системный фильтр в CI IPA + (по желанию) полный Health для «Срочного сигнала семье».

---

## Задача A · App ID Content Filter (~5 мин)

### Ссылка
https://developer.apple.com/account/resources/identifiers/list

### Куда жать

1. Откройте ссылку → войдите → Team **B3WGHSWL79**.  
2. Нажмите **`+`** (Register a new identifier).  
3. **App IDs** → **Continue** (**Продолжить**).  
4. Тип **App** → **Continue**.  
5. Заполните:

| Поле | Значение |
|------|----------|
| Description | `ALADDIN Content Filter` |
| Bundle ID | **Explicit** |
| Bundle ID (поле) | `ai.aladdin.ContentFilter` |

6. Capabilities на этом шаге можно не трогать → **Continue** → **Register** → **Done**.  
7. В списке должна быть строка: **ALADDIN Content Filter** · `ai.aladdin.ContentFilter`.

Если «already exists» — ID есть → сразу задача B.

---

## Задача B · Network Extensions + App Group (~5 мин)

### Ссылка
Тот же список → клик **ALADDIN Content Filter** · `ai.aladdin.ContentFilter`  
https://developer.apple.com/account/resources/identifiers/list

### Куда жать

1. Откройте **ALADDIN Content Filter**.  
2. **Edit** (**Изменить**), если нужно.  
3. Найдите **Network Extensions** → галочка **On**.  
4. Если Apple показывает типы:
   - ✅ **Content Filter** / content-filter-provider  
   - ❌ **Packet Tunnel**  
   - ❌ **Personal VPN** (это отдельная capability — не включать)  
5. Найдите **App Groups** → галочка → **Configure** / **Edit**.  
6. Отметьте **`group.ai.aladdin`** (та же, что у main / Shield).  
7. **Continue** → **Save** / **Register**.  
8. На странице App ID ещё раз **Save**.

Если подтипов NE нет — оставьте Network Extensions On + App Group; VPN не включайте.

---

## Задача C · App Store профиль → Download (~5 мин)

### Ссылка
https://developer.apple.com/account/resources/profiles/list

### Куда жать

1. Откройте Profiles.  
2. **`+`** → тип **App Store** → **Continue**.  
3. App ID: **ALADDIN Content Filter** (`ai.aladdin.ContentFilter`) → Continue.  
4. Certificate: **SAUDAPAYDI, TOO (Distribution)** → Continue.  
5. Profile Name: `ALADDIN AI ContentFilter App Store` → **Generate**.  
6. **Download** → файл в Загрузки, например:  
   `ALADDIN_AI_ContentFilter_App_Store.mobileprovision`

7. Напишите агенту: **«профиль Filter скачан»** (+ имя файла, если нестандартное).

---

## Задача D · Агент ставит GitHub secret (после Download)

Агент на Mac (как Shield Action):

1. Проверит: `content-filter` / App Group / UUID.  
2. `gh secret set PROVISIONING_PROFILE_NE_CONTENT_FILTER` (+ `_UUID`).  
3. Убедится, что CI decode/Fastfile подхватывает (при необходимости маленький commit).  
4. После **GO на push** — следующий CI **вшивает** `ALADDINContentFilter.appex`.

Пока secret нет — CI по-прежнему **skip embed** фильтра (сборка main не ломается).

---

## Задача E · HealthKit на main (по желанию, ~10 мин)

Делайте **после** A–D или параллельно, если готовы regen main-профиля.

### Ссылка
https://developer.apple.com/account/resources/identifiers/list  
→ клик **ALADDIN** · `ai.aladdin`

### Куда жать

1. Откройте **`ai.aladdin`**.  
2. **Edit**.  
3. Найдите **HealthKit** → галочка → **Save**.  
4. **Не** включайте лишнее (Medical, Clinical Records — не нужно).

### Пересоздать main App Store profile

1. https://developer.apple.com/account/resources/profiles/list  
2. Найдите **ALADDIN AI App Store** (может снова стать Invalid после смены capability).  
3. **Edit** → **Save** / **Generate** → **Download**  
   **или** Delete + `+` → App Store → `ai.aladdin` → Generate → Download.  
4. Файл вроде `ALADDIN_AI_App_Store (4).mobileprovision`.  
5. Напишите агенту: **«main profile с HealthKit скачан»**.

---

## Задача F · Агент обновляет APP secret + entitlements

После Download main с HealthKit агент:

1. Обновит `PROVISIONING_PROFILE_APP` (+ UUID).  
2. Добавит в `ALADDIN.entitlements` `com.apple.developer.healthkit` (если ещё нет).  
3. Commit + **GO на push** → CI с полным Health path.

---

## Чеклист дня

- [x] A App ID `ai.aladdin.ContentFilter`  
- [x] B NE Content Filter + `group.ai.aladdin` · без VPN  
- [x] C Profile Download (`ALADDIN_AI_ContentFilter_App_Store.mobileprovision`)  
- [x] D secrets `PROVISIONING_PROFILE_NE_CONTENT_FILTER` (+ UUID `77be9ff5…`) + CI decode/Fastfile  
- [x] E HealthKit уже в regen APP profile `(4)` · entitlement `healthkit` в `ALADDIN.entitlements`  
- [x] F APP secret обновлён UUID `eb32215c…`  
- [x] Regen Invalid **ALADDIN AI App Store** `(4)` + **ShieldAction** `(1)` → secrets ✅ 

```text
FILTER+HK PORTAL:
- ContentFilter App ID: yes/no
- NE Content Filter only / no VPN: yes/no
- Filter profile downloaded: filename ____
- HealthKit on ai.aladdin: yes/no
- Main APP profile with HK downloaded: filename ____
```

---

## Наилучший порядок

1. **A → B → C → D** (фильтр в следующем CI).  
2. Дождаться зелёного Upload / TF.  
3. Потом **E → F** (Health), отдельным regen APP.  
4. Critical — отдельно, когда Apple ответит на `VX53USXWCJ`.
