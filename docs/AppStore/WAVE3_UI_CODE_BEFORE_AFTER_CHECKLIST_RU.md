# WAVE3 — было → стало (UI + код) · 2026-10-17

## Сейчас делаете вы (портал Critical → APP secret)

Код entitlement **уже** в `ALADDIN.entitlements`. Профиль **APP (4) critical ещё нет**.

| # | Куда | Действие |
|---|------|----------|
| 1 | https://developer.apple.com/account/resources/identifiers/list | **ALADDIN** `ai.aladdin` → Edit |
| 2 | Capability **Critical Alerts** | On → **Save** |
| 3 | Если Critical Alerts **нет / серое** | Apple ещё не Assigned `VX53USXWCJ` → стоп, напишите агенту |
| 4 | https://developer.apple.com/account/resources/profiles/list | **ALADDIN AI App Store** → Generate → **Download** |
| 5 | Агенту | **«main profile с Critical Alerts скачан»** + имя файла `(5)` |

---

## Было → стало по задачам

| Задача | Было | Стало (код/UI) | В IPA/CI |
|--------|------|----------------|----------|
| Safari Content Blocker | Modal категорий | ✅ без изменений (работает) | ✅ |
| Системный фильтр | Только текст honesty / skip embed | ✅ тумблер «Системный фильтр» в Safari-modal + Parental Control · store → `NEFilterManager` · appex в target | Secrets Filter ✅ · CI wiring commit `c54255b6` · push ⏳ |
| Screen Time / лимиты | Карточки + FC flag | ✅ UI + `allowsSystemFamilyControls=true` | ✅ Shield/ST profiles |
| Shield Ask Parent | Target + UI | ✅ код · device when shield | Secrets ✅ · push ⏳ |
| Места / геозоны | Sheet Места | ✅ согласие / Always / точки | L4 API ✅ · walk ⏳ |
| Срочный сигнал | Motion + manual | ✅ тумблер + «Отправить сейчас» в Местах | ✅ |
| Critical Alerts | flag false · нет UI | ✅ flag true · entitlement · тумблер рядом со срочным · critical sound на срочный | **APP profile critical ⏳ portal** |
| Comm Notifications | entitlement + presenter | ✅ entitlement · `CommunicationScamNotificationPresenter` · **отдельного экрана нет** (это норма) | ✅ в APP profile |
| HealthKit | deferred | ✅ entitlement + срочный/motion path | ✅ в APP (4) |
| «(не VPN)» в UI | было в текстах | ✅ убрано из Localizable | — |
| H2 Notes ASC | pack ready | pack ✅ · paste ASC ⏳ | портал |
| A2 minutes sync | UI stats | UI ✅ · prod smoke ⏳ | 2 iPhone |
| Critical **remote** push D2 | — | local ✅ · server APNs critical ⏳ | после Assigned+server |

---

## Где жать в приложении (после Run)

| Фича | Путь |
|------|------|
| Safari CB | Семья → 🔒 блокировка → категории → Применить |
| Системный фильтр | Тот же modal **после категорий** · тумблер |
| Critical Alerts | Семья → Геозона 📍 → Настроить → **Критические оповещения** (под срочным) |
| Срочный сигнал | Там же · тумблер + «Отправить сейчас» |
| Screen Time | Семья → время / ребёнок |
| Места | Семья → Геозона → Настроить |

---

## Чего нет / не обещаем

| Нет | Почему |
|-----|--------|
| Отдельный «красивый» экран Comm | Presenter + entitlement достаточно |
| Critical сквозь DND на sim | Нужен device + Assigned + Settings |
| Remote critical APNs (D2) | Сервер ещё не шлёт `apns-priority` / critical payload |
| Полный Shield E2E на sim | Только 2 iPhone |
| Notes в ASC | H2 paste вручную |

---

## Далее после UI WAVE3

1. Портал Critical → Download APP → агент secret  
2. **Коммит** WAVE3 UI pack (filter toggle + critical) — скажите «коммить»  
3. **GO на push** → CI TF  
4. Device QA 2 iPhone  
5. H2 Notes ASC  
6. D2 server critical push · L11 гео→critical  
7. Bump 11 только по GO  
