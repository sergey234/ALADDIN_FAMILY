# WAVE 3 — все задачи (полный список, ничего не забыто)

**Дата:** 2026-10-17 · **TF в облаке:** 1.0.1 / build **10** (последний OK Upload) · **NEXT bump:** **11** (только GO)  
**Канон push/CI:** [`docs/RELEASE_BUILD_PROMPT.md`](../RELEASE_BUILD_PROMPT.md) §0 · §0b · §7A  
**ASC handoff:** [`docs/ML_SYSTEM_HANDOFF_ASC_VERSION_BUILD_RU.md`](../ML_SYSTEM_HANDOFF_ASC_VERSION_BUILD_RU.md)  
**SSOT фич:** [`CAPABILITIES_WAVE3_BUILD11_MASTER_PLAN_2026-10-17_RU.md`](CAPABILITIES_WAVE3_BUILD11_MASTER_PLAN_2026-10-17_RU.md)  
**TODO:** `cap-*` · `.cursor/CAPABILITIES_WAVE3_TASK_REGISTRY.md`

---

## 📦 Что уже готово локально — commit / deploy?

### Сейчас (2026-10-17) — **GO на commit** (push отдельно)

| Пакет | Файлы (ядро) | Commit | Deploy / Push |
|-------|--------------|--------|---------------|
| **ExtensionKit Report** (ASC 409) | `ALADDINDeviceActivityReport/Info.plist` · `project.pbxproj` | ✅ в commit 10 | ⏳ push по «GO на push» |
| **Гео L1–L5, L10 + L4 client** | `Geofence*` · `LocationManager` · `NotificationManager` · `AppConfig` · `APIService` · `Info.plist` · `InfoPlist.strings` · `Localizable.strings` RU+EN | ✅ | ⏳ push |
| **L4 server APNs** | `app/services/geofence_family_notify.py` · `app/routers/family.py` | ✅ в том же commit | ⏳ только **«GO на деплой»** MAIN `:8002` |
| **Планы / канон** | `WAVE3_*` · `CAPABILITIES_WAVE3*` · `RELEASE_BUILD_PROMPT` · ASC · verify · registry | ✅ | ⏳ push |
| **Не в этот commit** | BACKUPS · `.DS_Store` · bot · `.env` · чужие M | ❌ никогда | — |

**Итого:** WAVE3-ядро → **один commit build 10** (без bump). Push / CI Upload / Xcode — по отдельному GO.  
Деплой `geofence-event` — только «GO на деплой».

### Staging checklist (этот commit)

```text
# MUST
ALADDINDeviceActivityReport/Info.plist
ALADDIN.xcodeproj/project.pbxproj
Core/Family/GeofenceEventStore.swift
Core/Family/GeofenceFamilyBridge.swift
Core/Family/GeofenceMonitoringBootstrap.swift
Core/Managers/LocationManager.swift
Core/Notifications/NotificationManager.swift
Core/Config/AppConfig.swift
Core/Network/APIService.swift
Info.plist
ru.lproj/InfoPlist.strings
en.lproj/InfoPlist.strings
Resources/Localization/ru.lproj/Localizable.strings
Resources/Localization/en.lproj/Localizable.strings
app/services/geofence_family_notify.py
app/routers/family.py
scripts/verify_capabilities_wave3_static.sh
docs/RELEASE_BUILD_PROMPT.md
docs/ML_SYSTEM_HANDOFF_ASC_VERSION_BUILD_RU.md
docs/AppStore/CAPABILITIES_WAVE3_BUILD11_MASTER_PLAN_2026-10-17_RU.md
docs/AppStore/WAVE3_TOMORROW_TASKS_2026-10-17_RU.md
.cursor/CAPABILITIES_WAVE3_TASK_REGISTRY.md
.cursor/rules/capabilities-wave3-todo-ssot.mdc
.cursor/SCREEN_TIME_WAVE2_TASK_REGISTRY.md   # опционально (ссылка st-F1)

# STOP
telegram_stars_shop_bot/**  .env  BACKUPS/**  .DS_Store  *.pbxproj.bak*
```

---

## ⚡ Утро — вспомнить за 2 минуты

### Где мы
| | |
|--|--|
| App / Team | `ai.aladdin` · **B3WGHSWL79** |
| Version / Build в TF | **1.0.1 / 10** (успех #588; следующий Upload = снова **10** с ExtensionKit) |
| След. bump | **11** — только «GO на bump» |
| Ветка / remote | `master` → `git@github.com:sergey234/ALADDIN_FAMILY.git` |
| CI | `check-secrets.yml` = **Build and Upload to App Store** |
| Commit 10 WAVE3 | ExtensionKit + L1–L5/L10/L4 + loc RU/EN + планы — **commit локально** · origin после «GO на push» |

### Почему не было новой сборки в TF
`logs_105606115805`: Archive OK · **Upload FAILED 409** (Report = NSExtension).  
Artifact IPA в GitHub ≠ TestFlight. Фикс ExtensionKit в commit; Upload — после push.

### Политика (решение владельца 2026-10-17 утро)

```text
1) Commit пакета WAVE3 (build 10, без bump) — СЕЙЧАС.
2) Дальше код по плану (L6–L16 · Shield · …) · локализация RU+EN всегда.
3) Push / CI Upload — только «GO на push».
4) Сборка Xcode / симулятор — только в КОНЦЕ и только «GO на сборку».
5) Деплой L4 — только «GO на деплой». Bump 11 — только «GO на bump».
```

### Push + GitHub (когда скажете «GO на push»)

```text
1) cd …/ALADDIN_iOS · master · remote канон
2) ./scripts/verify_capabilities_wave3_static.sh → ALL OK
3) «GO на push» (без bump → build 10)
4) git push origin master
5) Actions → Build and Upload → Upload ЗЕЛЁНЫЙ
6) ASC → TestFlight → 1.0.1 → Builds → Processing → Ready
```

Зелёный релиз = **Archive + Export + Upload**.  
Куда смотреть: App Store Connect → ALADDIN AI → **TestFlight** → iOS → **1.0.1**.

### Порядок дел (после этого commit)

```text
ПОСЛЕ COMMIT (код, без Xcode пока):
  1. L12 progressive Always · L6/L13 coords · L7 SOS · L8/L9 honesty · L14–L16
  2. Shield Action B1–B4 (код)
  3. Walk-test геозон на TF 10 (локальный баннер) — владелец
  4. По GO: деплой L4 на MAIN :8002

В КОНЦЕ ПАКЕТА:
  5. «GO на push» → CI Upload → TF 1.0.1/10 ExtensionKit+L
     ИЛИ «GO на сборку» в Xcode (Device QA) — что скажет владелец
  6. Device QA ST (A0) → FC on (A1) по GO
  7. Bump 11 — только «GO на bump»
```
---

## Рекомендация одной фразой

Оставляем модель **Always для геозон + significant-change**, **без** `UIBackgroundModes location`.  
Усиливаем честные тексты, sync и согласие. Continuous GPS не трогаем.  
Громкие алерты = **Critical Alerts** (WAVE3), не новое location-entitlement.

**Отдельная заявка Apple на геолокацию не нужна.**

---

## L16 — названия (выбор владельца) · copy без «следить»

### Родитель включает функцию в семье (сейчас: «уведомления о местах»)

| # | Название кнопки/тумблера | Подзаголовок (зачем) | Рекомендация |
|---|--------------------------|----------------------|--------------|
| **P1** | **Уведомления о местах семьи** | Семья узнает: пришёл или ушёл из дома/школы. Без линии маршрута. | ✅ **рекомендуем** (уже близко к текущему) |
| **P2** | **Приход и уход из мест** | Только сигнал «на месте» / «ушёл». Не карта и не трек. | альтернатива короче |
| **P3** | **Безопасные места** | Дом, школа, работа — семья видит приход и уход. | мягче, «product» тон |

**Кто нажимает:** родитель / настраивающий семью (не «подпись ребёнка до 18»).  
**На телефоне ребёнка:** системный запрос iOS Location Always — отдельно.

### Взрослый член семьи (бабушка, супруг) — opt‑in себе (без слова «следить»)

| # | Название тумблера | Подзаголовок | Рекомендация |
|---|-------------------|--------------|--------------|
| **A1** | **Сообщать семье о моих местах** | Семья узнает, когда я прихожу или ухожу из выбранных мест. | ✅ **рекомендуем** |
| **A2** | **Делиться приходом и уходом** | Только сигналы по местам, которые я сам(а) выбрал(а). | нейтрально |
| **A3** | **Мои места для семьи** | Родные видят: я на месте или ушёл(а). Без маршрута. | короче |

**Выбор владельца 2026-10-17:** **P1 + A3** (+ teen Always copy) — **применено в коде**.

### Подросток — короткий текст на экране Always (без «подписи до 18»)

| Язык | Текст (черновик) |
|------|------------------|
| RU | Родители узнают только: ты пришёл(а) или ушёл(а) из места. Без линии маршрута по карте. |
| EN | Parents only see when you arrive or leave a place. No route line on the map. |

Задача: **L16-teen-copy** (карточка Always / consent).

---

## Пуш-уведомления — что уже «включено и разрешено Apple»

| Тип | У нас в коде | Нужна заявка Apple? | В TestFlight сейчас |
|-----|--------------|---------------------|---------------------|
| Обычные local + remote (alert/badge/sound) | ✅ `NotificationManager` · `remote-notification` в Background Modes | **Нет** — стандарт | ✅ работают, если пользователь разрешил |
| Provisional | ✅ в options | Нет | тихо, без полного баннера |
| Гео enter/exit → **локальный** баннер | ✅ L3 important types | Нет | на устройстве с зонами |
| Гео enter/exit → **APNs родителю** (L4) | ✅ код · **деплой ⏳** | Нет (обычный push) | после «GO на деплой» |
| Shield «спросить родителя» | ✅ local banner · APNs позже | Нет | после push IPA |
| **Critical Alerts** (громко сквозь DND) | ❌ флаг/форма WAVE3 C1→D* | **Да** (Account Holder) | нет |
| Communication Notifications | ❌ WAVE3 C2 | **Да** (portal) | нет |

**Итог:** обычные пуши Apple **разрешены и подключены**. Не подключены только **особые** entitlement (Critical / Comm) — это отдельные формы WAVE3.  
На устройстве всё равно нужно: Настройки → ALADDIN → Уведомления = Вкл (и не «только важные», если режете гео).

---

## A. Location — что подходит продукту

### Делать (лучшее под ALADDIN)

| # | Фича | Как | ID | Статус |
|---|------|-----|-----|--------|
| 1 | Геозоны дом/школа/работа → пуш родителю enter/exit | Always + region monitoring · local UN + APNs | L0–L5 · **L4 deploy** | код ✅ · деплой ⏳ |
| 2 | «Поделиться локацией сейчас» / SOS | When In Use + Precise коротко | **L7** | ✅ код |
| 3 | Soft presence «я в порядке» | **Без GPS** | **L8** | ✅ код |
| 4 | Location Bubble / privacy-зоны | Opt-in · premium · честный copy | **L9** | ✅ код |
| 5 | Battery-friendly | significant-change + точный GPS только у границы | уже в `LocationManager` · **L10** ✅ | не ломать |

### Не делать / не обещать

| Запрет | ID / где |
|--------|----------|
| Live-трек 24/7 + `UIBackgroundModes location` | OUT · **L10** ✅ verify |
| Скрытый GPS «для аналитики» | **L16** |
| Трекинг без явного тумблера у члена семьи | **L16** + consent мест |
| Packet Tunnel / in-app VPN | OUT всей WAVE3 |
| MDM / запись звонков | H2 |

### Что добавить в WAVE3 (location) — таблица приоритетов

| Приоритет | Действие | Заявка Apple? | ID | Статус |
|-----------|----------|---------------|-----|--------|
| Высокий | Purpose strings конкретно (геозоны, SOS) RU+EN | Нет | **L5** | ✅ |
| Высокий | UX: When In Use → объяснение → Always только при местах | Нет | **L12** | ✅ код |
| Высокий | Sync геозон с `:8002`, убрать фейковые coords в UI | Нет | **L13** (+ L6) | ✅ код |
| Высокий | Parent APNs на enter/exit (не только chat) | Нет | **L4** | код ✅ · деплой ⏳ |
| Средний | ASC Privacy labels + Review Notes «alerts, not track» | Нет | **L15** · H2 | ✅ pack · ⏳ ASC |
| Средний | Precise только setup зоны / SOS | Нет | **L14** | ✅ код |
| Низкий | Не добавлять background `location` | — | **L10** | ✅ |
| Связка | Critical Alerts на выход из зоны / SOS | **Да** (не location) | **L11** · D* · C1 | ⏳ форма |

---

## B. Apple capabilities (кроме VPN) — весь WAVE 3

| # | Что | Форма? | ID |
|---|-----|--------|-----|
| 1 | **Shield Action** (ask parent / close) | Нет — тот же FC | B1–B4 |
| 2 | **Critical Alerts** | Да | C1 → D1–D4 |
| 3 | **NE Content Filter / DNS Proxy** | Да | C3 → F1–F4 |
| 4 | ~~Packet Tunnel VPN~~ | — | **OUT** |
| 5 | **HealthKit** fall | Capability + Review | G1–G3 |
| 6 | **Communication Notifications** | Portal | C2 → E1–E2 |

### Без новой заявки (продукт)

| Что | ID |
|-----|-----|
| Device QA ST → `allowsSystemFamilyControls=true` | A0 → A1 |
| Shield + ManagedSettings honesty | B* · A3 |
| Sync минут parent↔child | A2 |
| Privacy plist hygiene (не врать HomeKit/BT) | H1 |
| Честные Review Notes (нет MDM / recording) | H2 |

---

## C. Практичный порядок работ

```text
0. BLOCKER CI: ExtensionKit — commit ✅ · push ⏳
1. Гео walk-test → GO деплой L4
2. GO на push → CI Upload (build 10)  ·  Xcode только в конце + GO
3. Device QA ST (A0) → FC on (A1)
4. Shield Action (B)
5. Заявки Apple: Critical · Comm · NE Filter
6. L12–L16 · H · bump 11 (GO)
```

### BLOCKER — почему TF пустой (run logs_105606115805)

| Шаг | Результат |
|-----|-----------|
| Archive + Export IPA | OK |
| Upload ASC | **FAILED 409** — Report как NSExtension в PlugIns |
| Artifact GitHub IPA | OK (это не TestFlight) |

**Фикс (в commit, Upload после push):** ExtensionKit  
- Info.plist → `EXAppExtensionAttributes`  
- productType → `extensionkit-extension`  
- Embed → `Extensions/` (`dstSubfolderSpec = 16`)  

Пока нет push + Upload SUCCESS — **новой сборки в TestFlight не будет**.
---

## D. Сегодня уже сделано (без телефона)

| ID | Что |
|----|-----|
| L0 | Диагноз no-push (15 причин) |
| L1 | Always gate |
| L2 | requestState |
| L3 | Important types (exit не глотается) |
| L5 | Purpose strings |
| L10 | Verify no background location |
| L4 | API + iOS client (деплой ждёт GO) |
| ST-Report | ExtensionKit (ASC 409 fix) — **без push** | ✅ локально |

```bash
./scripts/verify_capabilities_wave3_static.sh
```

---

## E. Вам завтра — геозоны (1 телефон)

- [ ] Гео = **Всегда**
- [ ] Уведомления ALADDIN = Вкл
- [ ] Места: согласие + «мониторинг»
- [ ] Семья Вкл · «Только важные» Выкл · тихие/DND/лимит Выкл
- [ ] Выйти за радиус → 1–3 мин → лента + баннер?

| Лента | Баннер | Дальше |
|-------|--------|--------|
| нет | нет | 3 скрина |
| есть | нет | скрин настроек уведомлений |
| есть | есть | тест родителя |

---

## F. Вам завтра — родитель (2-й телефон)

- [ ] Enter/exit на детском → пуш у родителя?

Нужен **«GO на деплой geofence-event»** на 🇷🇺 MAIN (`…180`) `:8002`.

---

## G. Полный чеклист (отмечать)

### Location L
- [x] L0–L3, L5, L10  
- [x] **L4** деплой APNs MAIN (`…180`) 2026-10-17 · walk-test ⏳  
- [x] **L6** coords map/GPS (geocode fail = alert; «моя точка»)  
- [x] **L7** SOS one-shot When In Use + precise  
- [x] **L8** Soft presence honesty (Im OK без GPS)  
- [x] **L9** Location Bubble honesty copy  
- [ ] **L11** Critical на геозону  
- [x] **L12** Progressive WhenInUse→Always (CTA only)  
- [x] **L13** Soft sync parental API + demo blocked (UI local SSOT)  
- [x] **L14** Precise only place-setup helper (+ SOS)  
- [x] **L15** pack ASC Privacy + Review Notes (`WAVE3_L15_ASC_PRIVACY_LOCATION_PACK_RU.md`) · галочки в портале — владелец  
- [x] **L16** Opt-in мест (родительский consent) · no silent GPS  
- [x] **L16-copy** **P1 + A3** применены RU/EN  
- [x] **L16-teen-copy** текст Always для подростка  
- [x] **L16-adult** тумблер «Мои места для семьи» (A3)  
- [x] **Loc audit** geofence/ImOK/NeedHelp/Shield — 100 ключей UI в RU+EN `Localizable.strings` (без сырых ключей)  

### Пуши / Apple
- [x] Обычные UN + remote-notification  
- [x] L4 APNs geo → родитель (деплой MAIN ✅) · walk-test ⏳  
- [x] Critical Alerts — draft формы C1 · submit ⏳ AH  
- [x] Communication Notifications — draft C2 · submit ⏳ AH  
- [x] H2 Review Notes pack · paste ASC ⏳  
- [x] **Сессия порталов (клик за кликом):** [`WAVE3_OWNER_PORTAL_SESSION_C1C3_L15_SHIELD_RU.md`](WAVE3_OWNER_PORTAL_SESSION_C1C3_L15_SHIELD_RU.md) — Shield App ID · L15 · C1–C3 

### A Screen Time · B Shield · C Forms · D Critical · E Comm · F NE · G HealthKit · H Hygiene · I Ship  
(как в MASTER §6 — ids `cap-A*` … `cap-I*`)  
**B1/B2 код ✅** · **B3** ждёт App ID `ai.aladdin.ShieldAction` + secret · **B4** local parent banner ✅ (APNs позже)

### Hygiene H / verify
- [x] **H1** Info.plist — убраны HomeKit/BT/Music/Siri/LocalNet/Reminders  
- [x] **H2** Review Notes pack  
- [x] **I1** `verify_capabilities_wave3_static.sh` ALL OK (+ H1/L16/D4)  
- [x] Loc RU+EN geofence/ImOK — 100 ключей, без сырых  

### Flags / forms / ST (код без деплоя)
- [x] **D4** `allowsCriticalAlerts` / Comm / ContentFilter = false · UN не просит critical  
- [x] **C3** draft NE Content Filter (не VPN)  
- [x] **F1** ADR Filter vs DNS Proxy  
- [x] **A3** ManagedSettings FC-gate + honesty в лимитах  
- [x] **F3** Parental: Safari CB vs system filter honesty  

### Ship (build 10 → TF)
- [x] Commit ExtensionKit + L + Shield (`e6d1cadc`, `a4d868e9`)  
- [ ] Commit uncommitted: L16 copy + loc mirror + H1/H2/L15/C1C2 packs (сказать **«коммить»**)  
- [ ] **GO на push** → CI Upload SUCCESS  
- [ ] Walk-test геозон  
- [ ] **GO на деплой** L4  
- [ ] Device QA ST (A0) → FC on (A1)  
- [ ] Xcode только в конце + **GO на сборку**

---

## H. Запрещено
- VPN / Packet Tunnel · continuous GPS · скрытый трекинг · MDM · запись звонков  
- Деплой / bump / сборка без **GO**

---

## Одна фраза на завтра

Walk-test геозон → результат → **GO деплой L4** и/или **GO сборка / Device QA ST** → Shield Action → заявки Critical / Comm / NE Filter.
