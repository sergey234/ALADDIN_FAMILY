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

## A. Location — что подходит продукту

### Делать (лучшее под ALADDIN)

| # | Фича | Как | ID | Статус |
|---|------|-----|-----|--------|
| 1 | Геозоны дом/школа/работа → пуш родителю enter/exit | Always + region monitoring · local UN + APNs | L0–L5 · **L4 deploy** | код ✅ · деплой ⏳ |
| 2 | «Поделиться локацией сейчас» / SOS | When In Use + Precise коротко | **L7** | ⏳ |
| 3 | Soft presence «я в порядке» | **Без GPS** | **L8** | ⏳ усилить |
| 4 | Location Bubble / privacy-зоны | Opt-in · premium · честный copy | **L9** | ⏳ |
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
| Высокий | UX: When In Use → объяснение → Always только при местах | Нет | **L12** | ⏳ |
| Высокий | Sync геозон с `:8002`, убрать фейковые coords в UI | Нет | **L13** (+ L6) | ⏳ |
| Высокий | Parent APNs на enter/exit (не только chat) | Нет | **L4** | код ✅ · деплой ⏳ |
| Средний | ASC Privacy labels + Review Notes «alerts, not track» | Нет | **L15** · H2 | ⏳ |
| Средний | Precise только setup зоны / SOS | Нет | **L14** | ⏳ |
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
- [ ] **L4** деплой APNs  
- [ ] **L6** coords map/GPS  
- [ ] **L7** SOS share  
- [ ] **L8** Soft presence  
- [ ] **L9** Location Bubble  
- [ ] **L11** Critical на геозону  
- [ ] **L12** Progressive WhenInUse→Always  
- [ ] **L13** Sync :8002 + kill fake coords  
- [ ] **L14** Precise only setup/SOS  
- [ ] **L15** ASC Privacy labels location  
- [ ] **L16** Тумблер / no hidden GPS  

### A Screen Time · B Shield · C Forms · D Critical · E Comm · F NE · G HealthKit · H Hygiene · I Ship  
(как в MASTER §6 — ids `cap-A*` … `cap-I*`)

---

## H. Запрещено
- VPN / Packet Tunnel · continuous GPS · скрытый трекинг · MDM · запись звонков  
- Деплой / bump / сборка без **GO**

---

## Одна фраза на завтра

Walk-test геозон → результат → **GO деплой L4** и/или **GO сборка / Device QA ST** → Shield Action → заявки Critical / Comm / NE Filter.
