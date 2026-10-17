# WAVE3 — комит → деплой → тест · сборка только в конце

**Режим владельца (2026-10-17):**  
1) коммитим нужное · 2) деплоим только L4 · 3) тестим на телефонах ·  
4) **одна** финальная сборка / Upload — когда всё закрыто.

**Не делаем сейчас:** `xcodebuild` · bump 11 · Submit · Critical/NE код «в бою».

---

## Карта: что где лежит

| Слой | Уже в git (commits) | Ещё не в git (local) |
|------|---------------------|----------------------|
| ExtensionKit Report (фикс 409) | ✅ `e6d1cadc` | — |
| Гео L1–L5/L10 + L4 **client+server код** | ✅ `e6d1cadc` | — |
| Гео L6–L16 + Shield Action | ✅ `a4d868e9` | дожим L16 P1/A3, AdultSelfShare, loc mirror |
| D4 флаги · A3 honesty · F3 · H1 plist · packs L15/H2/C* | — | ✅ uncommitted |
| L4 **на сервере MAIN** | код в репо | **деплой ⏳** |

**Важно для теста без новой сборки:**  
на телефонах сейчас TF **1.0.1 / build 10** (старый Upload).  
- После **push** уже закоммиченного → CI положит в TF новый IPA build **10** (ExtensionKit + гео + Shield).  
- Дожим L16/D4/A3/F3/H1 попадёт в телефон только в **финальной** сборке (шаг 9).  
- **Деплой L4** чинит пуш родителю на **сервере** — его можно гонять уже с клиентом из TF после push (или с текущим, если L4 client уже был в прошлом IPA).

---

## Порядок работ (чеклист)

### Шаг 0 — до старта
- [ ] Ветка `master`
- [ ] Не трогаем: bot · `.env` · BACKUPS · VPN secrets
- [ ] Сборка Xcode **не** запускаем

---

### Шаг 1 — КОММИТ #1 (дожим WAVE3, без bump)
**Кто:** агент · **Фраза:** `коммить WAVE3 пакет`

В коммит (только это):
- [ ] `Core/` (Geofence*, AppConfig, NotificationManager, ScreenTimeAppLimitsBridge, LocManager точечно)
- [ ] `Screens/02_FamilyScreen.swift` · `07_ParentalControlScreen.swift`
- [ ] `Info.plist` · `ru/en.lproj/InfoPlist.strings`
- [ ] `Resources/Localization/{ru,en}.lproj/Localizable.strings`
- [ ] `scripts/verify_capabilities_wave3_static.sh`
- [ ] `docs/AppStore/WAVE3_*` · `CAPABILITIES_WAVE3_*` · registry
- [ ] `Core/Family/GeofenceAdultSelfShareStore.swift` (новый)

**Не в коммит:**
- [ ] `.DS_Store` · `*_BACKUP*` · `*_Old.swift` · чужие AppStore md/скриншоты IAP · bot

Перед коммитом агент: `./scripts/verify_capabilities_wave3_static.sh` → ALL OK.

---

### Шаг 2 — PUSH (CI Upload build 10, без bump)
**Кто:** агент · **Фраза:** `GO на push`

- [ ] `git push origin master`
- [ ] GitHub Actions → **Build and Upload** → Upload **зелёный**
- [ ] ASC → TestFlight → **1.0.1** → новый билд Processing → Ready
- [ ] Поставить этот билд на **2 iPhone** (родитель + ребёнок/второй)

*Пока Upload не Ready — walk-test геозон по новому коду не начинать.*

---

### Шаг 3 — ДЕПЛОЙ L4 (только APNs геозоны)
**Кто:** агент · **Фраза:** `GO на деплой L4`  
**Куда:** 🇷🇺 MAIN — FirstVDS / Аладдин · запас · Россия (`…180`) `:8002`

- [ ] Health снаружи: `curl …:8002/api/health` → ok
- [ ] Бэкап на сервере целевых файлов
- [ ] Выкат: `geofence_family_notify.py` + кусок `family.py` (geofence-event)
- [ ] `py_compile` · restart gunicorn/service по runbook
- [ ] Smoke: health + тестовый geofence-event (без секретов в чат)

**Не деплоим заодно:** бот Contabo · VPN xray · Brain.

---

### Шаг 4 — ТЕСТ геозон (вы на 2 телефонах)
**Цель:** enter/exit → пуш у родителя.

Подготовка:
- [ ] Родитель: включены «Уведомления о местах семьи» (consent)
- [ ] На устройстве с геозоной: Always + Precise при setup
- [ ] Место с реальными coords (не демо-адрес)
- [ ] Взрослый (если тест на взрослом): «Мои места для семьи» ON
- [ ] Уведомления iOS ON · «Только важные» не режет geo (после L3 ок)

Сценарий:
- [ ] Добавить «Дом» / точку · выйти за радиус · подождать 1–3 мин
- [ ] Войти снова
- [ ] Локальный баннер на устройстве зоны?
- [ ] **Пуш у родителя** после L4? (главный PASS)

Результат в чат: PASS / FAIL + что видели.

---

### Шаг 5 — ТЕСТ Screen Time (Device QA A0) — без FC on
**На TF билде после шага 2.**

- [ ] Child: auth Family Controls → picker приложений
- [ ] Попользоваться 5–10 мин
- [ ] Parent: used/limit честно (не фейк 2:45)
- [ ] Shield / Ask Parent (если Shield Action в IPA)
- [ ] Записать PASS/FAIL → только потом A1

**A1 FC on в App Store path** — отдельная фраза после PASS: `GO на A1 FC on`  
(это правка флага + потом попадёт в финальную сборку).

---

### Шаг 6 — Параллельно тестам (вы в порталах, без сборки)
- [ ] ASC Privacy labels (L15 pack)
- [ ] Review Notes вставить (H2 pack) — можно черновик, Submit позже
- [ ] App ID `ai.aladdin.ShieldAction` + Distribution profile → GitHub secret
- [ ] Формы C1 / C2 / C3 отправить (Account Holder)

---

### Шаг 7 — Дожать код по FAIL тестам (агент, без сборки)
- [ ] Фиксы только по багам walk-test / ST QA
- [ ] Снова **коммит** (фраза `коммить фикс …`)
- [ ] Push **только если** нужен новый IPA до финала — иначе копить до шага 9

*Рекомендация режима «1 сборка в конце»:* после шага 2 push больше не делать до финала; фиксы копить локально + коммитить, Upload один раз на шаге 9.

---

### Шаг 8 — Перед финальной сборкой (ворота)
Всё ✅:
- [ ] Геозоны walk-test PASS (local + parent APNs)
- [ ] ST Device QA A0 PASS
- [ ] Решение по A1 (FC on) принято
- [ ] Shield Action profile/secret на месте (или честно skip в CI)
- [ ] L4 на MAIN живой
- [ ] `verify_capabilities_wave3_static.sh` ALL OK
- [ ] Нет сырых ключей loc (уже проверено)

---

### Шаг 9 — ОДНА финальная сборка
**Фразы по порядку:**
1. `GO на A1 FC on` — если включаем FC  
2. `GO на bump` — 10→11  
3. `коммить build 11`  
4. `GO на push` — CI Upload  
5. Device QA build 11  
6. Submit — отдельный GO

**Xcode локально** — только если скажете `GO на сборку` (обычно достаточно CI).

---

## Что говорить агенту (короткие команды)

| Когда | Фраза |
|-------|--------|
| Сохранить дожим | `коммить WAVE3 пакет` |
| Залить в TF build 10 | `GO на push` |
| APNs геозоны на MAIN | `GO на деплой L4` |
| Включить FC после QA | `GO на A1 FC on` |
| Финальный номер | `GO на bump` |
| Финальный Upload | `GO на push` |
| Локальный Xcode | `GO на сборку` (редко) |

---

## Запрещено в этом режиме

- Сборка «проверить» между шагами  
- Деплой Brain/бота/VPN «заодно»  
- Bump 11 до конца тестов  
- Push VPN secrets / bot в iOS-коммит  

---

## Мини-схема

```text
коммит дожима → GO push (TF 10) → поставить на 2 iPhone
       ↓
GO деплой L4 (MAIN)
       ↓
тест геозон + тест ST  →  фиксы/коммиты (без Upload)
       ↓
порталы Apple (формы, Privacy, Shield profile)
       ↓
GO bump + GO push  =  ОДНА финальная сборка 11
```
