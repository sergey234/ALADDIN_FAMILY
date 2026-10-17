# WAVE3 — сессия владельца в порталах (сейчас, без сборки)

**Дата:** 2026-10-17 · Team **B3WGHSWL79** · App **`ai.aladdin`**  
**Режим:** push/сборка **не** нужны. Параллельно с walk-test геозон (L4 уже на MAIN).

| Блок | ID | Время | Кто |
|------|-----|-------|-----|
| **1** Shield Action App ID + FC заявка | B1/B3 | ~15 мин | Account Holder |
| **2** ASC Privacy Location | L15 | ~10 мин | App Manager / AH |
| **3** Review Notes (черновик) | H2 | ~5 мин | App Manager |
| **4** Форма Critical Alerts | C1 | ~10 мин | Account Holder |
| **5** Форма Communication Notifications | C2 | ~10 мин | Account Holder |
| **6** Форма NE Content Filter (не VPN) | C3 | ~15 мин | Account Holder |

После Assigned → блок **7** (profiles + GitHub secrets) — можно в другой день.

Полные тексты:  
`WAVE3_L15_…` · `WAVE3_H2_…` · `WAVE3_C1_C2_…` · `WAVE3_C3_…` · FC click-by-click 2026-10-16.

---

## 1. Shield Action — App ID + заявка Family Controls

Уже есть (или были в процессе): Monitor / Report / Shield**Configuration**.  
Сейчас нужен ещё один: **Shield Action** (кнопки Ask Parent / Close).

### 1.1 Создать App ID

1. https://developer.apple.com/account/resources/identifiers/list  
2. Team **B3WGHSWL79**  
3. **`+`** → App IDs → Continue → App → Continue  
4. Заполнить:

| Поле | Значение |
|------|----------|
| Description | `ALADDIN Shield Action` |
| Bundle ID | **Explicit** → `ai.aladdin.ShieldAction` |

5. Capabilities пока можно не трогать (FC галочка после Assigned)  
6. Continue → Register → Done  

Если «already exists» — ID есть, идите в 1.2.

### 1.2 Заявка Family Controls Distribution на Shield Action

1. https://developer.apple.com/contact/request/family-controls-distribution  
2. Bundle ID: **`ai.aladdin.ShieldAction`** (не main)  
3. App Store Connect Apple ID приложения — тот же, что для main  
4. Вставьте текст:

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

This request is for the Shield Action extension
(bundle id: ai.aladdin.ShieldAction), which handles Ask Parent / Close
actions on the system shield UI.
```

5. Submit → запишите **Request ID** сюда:

| Bundle | Request ID | Дата |
|--------|------------|------|
| `ai.aladdin.ShieldAction` | _______________ | ____ |

### 1.3 Пока ждём Assigned

Код Shield Action уже в репо. CI без secret просто **skip embed** — это ок до шага 7.

---

## 2. ASC — App Privacy (Location) · L15

1. https://appstoreconnect.apple.com → **ALADDIN** / ALADDIN AI  
2. **App Privacy** → Edit  
3. **Location** (Precise и/или Coarse):

| Поле | Значение |
|------|----------|
| Used for | **App Functionality** |
| Linked to user | **Yes** |
| Used for Tracking | **No** |

4. Не ставить Location на Advertising / Analytics  
5. Save / Publish ответы Privacy  

Подробности: `WAVE3_L15_ASC_PRIVACY_LOCATION_PACK_RU.md`

Чеклист:
- [ ] Location = App Functionality · Linked Yes · Tracking No  
- [ ] Сохранено в ASC  

---

## 3. ASC — Review Notes (черновик, Submit позже)

1. ASC → версия **1.0.1** (или текущая) → **App Review Information** → Notes  
2. Вставьте блок LOCATION из L15 + общий блок из `WAVE3_H2_REVIEW_NOTES_ASC_PACK_RU.md`  
3. **Не** жмите Submit for Review сейчас — только сохранить Notes  

Чеклист:
- [ ] Notes вставлены  
- [ ] Submit for Review **не** нажимали  

---

## 4. Форма C1 — Critical Alerts

1. https://developer.apple.com/contact/request/notifications-critical-alerts-entitlement/  
   (если 404 — Developer → Account → Contact Us → Critical Alerts)  
2. Account Holder · Team B3WGHSWL79 · Bundle `ai.aladdin`  
3. Вставьте смысл (EN):

```text
ALADDIN is a family safety app. Critical Alerts are required so caregivers
receive time-sensitive notifications when an elderly member triggers SOS /
fall detection, or when a high-risk scam call is detected — including when
the phone is silenced. Not used for marketing, engagement, or news.

We already ship ordinary push/local notifications. Critical is only for
predefined high-urgency family categories. The user can disable in Settings.
```

4. Submit → Request ID: _______________  

До Assigned: в коде `allowsCriticalAlerts = false` (уже).

---

## 5. Форма C2 — Communication Notifications

1. Developer Account → запрос **Communication Notifications** entitlement  
   (Capabilities / contact request — актуальный URL у AH)  
2. Текст:

```text
Used with Call Directory to present clearer incoming-call UI for numbers
identified as scam/spam for family protection. Not used for advertising
or marketing chat.
```

3. Submit → Request ID: _______________  

---

## 6. Форма C3 — NE Content Filter (**не VPN**)

1. Запрос Network Extension / Content Filter (Account Holder)  
2. Явно написать: **NOT Packet Tunnel / NOT VPN**  
3. Текст:

```text
ALADDIN is a family safety app. We request a Network Extension Content Filter
so parents can apply domain/app web rules beyond Safari (system-wide parental
filtering). We explicitly do not request Packet Tunnel VPN. VPN remains via
the user’s existing client. Filter rules come from parent settings only and
are not used for advertising or tracking.
```

4. Submit → Request ID: _______________  

Подробности: `WAVE3_C3_NE_CONTENT_FILTER_FORM_DRAFT_RU.md` · ADR `WAVE3_F1_…`

---

## 7. После Assigned (Shield Action / FC) — profiles + GitHub

Делать **когда** Capability Requests → Family Controls для `ai.aladdin.ShieldAction` = **Assigned**.

### 7.1 Identifier
1. Identifiers → `ai.aladdin.ShieldAction` → Edit  
2. Включить **Family Controls** + App Group **`group.ai.aladdin`** → Save  

### 7.2 Profile
1. Profiles → **`+`** → App Store → App ID `ai.aladdin.ShieldAction`  
2. Distribution cert → Generate → Download `.mobileprovision`  
3. Имя профиля например: `ALADDIN Shield Action AppStore`  

### 7.3 GitHub secrets (как у ST×3)

| Secret | Содержимое |
|--------|------------|
| `PROVISIONING_PROFILE_ST_SHIELD_ACTION` | base64 `.mobileprovision` (как другие ST) |
| decode → `PROVISIONING_PROFILE_ST_SHIELD_ACTION_UUID` | UUID профиля (как в CI для Monitor/Report/Shield) |

Точный decode-шаг — тот же workflow, что для `PROVISIONING_PROFILE_ST_SHIELD`.  
Fastfile уже умеет: нет UUID → skip embed; есть UUID → embed `ALADDINShieldAction`.

После секретов напишите агенту: **`Shield Action secret готов`** (push всё равно только в финале).

---

## Итоговый чеклист «сделал сегодня»

- [ ] 1 App ID `ai.aladdin.ShieldAction`  
- [ ] 1 заявка FC на Shield Action · Request ID записан  
- [ ] 2 ASC Privacy Location  
- [ ] 3 Review Notes вставлены (без Submit)  
- [ ] 4 C1 Critical · Request ID  
- [ ] 5 C2 Comm · Request ID  
- [ ] 6 C3 NE Filter · Request ID  
- [ ] (позже) 7 profiles + secrets после Assigned  

Параллельно на телефонах: **walk-test геозон** (L4 на MAIN уже).

---

## Что сказать агенту после сессии

Скопируйте и заполните:

```text
PORTAL SESSION DONE:
- ShieldAction App ID: yes/no · FC request: <ID>
- ASC Privacy Location: yes/no
- Review Notes pasted: yes/no
- C1 Critical: <ID or pending>
- C2 Comm: <ID or pending>
- C3 NE Filter: <ID or pending>
- Walk-test geo: PASS/FAIL — <кратко>
```
