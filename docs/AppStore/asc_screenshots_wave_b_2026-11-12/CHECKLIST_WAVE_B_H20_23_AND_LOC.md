# Wave B — чеклист статус (обновлено 2026-11-12 ~18:26)

Папка Finder: `~/Downloads/ALADDIN_ASC_WaveB_LOC_CHECK_2026-11-12/`  
Fitted: `07_FITTED_1290x2796/` · All: `~/Downloads/ALADDIN_ASC_WaveB_All/`  
Repo: `docs/AppStore/asc_screenshots_wave_b_2026-11-12/`  
Handoff: `docs/competitors/figma_preview_fig_l/PLAN_WAVE_B_CAPCUT_TODAY_HANDOFF_2026-11-12.md`

**Правило имён:** **Gary** оставляем везде (не переименовывать в Andrey).  
**Aladdin на кадре:** не писать (бренд = navy+gold).

---

## ✅ Сделано

### CapCut / in-app heroes
- [x] CapCut pack JOB01–23 + MAP_28
- [x] JOB01–12 wire in-app (pin, calendar, SUV, lock, pets, family, SOS…)
- [x] Loc keys SOS / pets / family / tip driving reports (strings)

### H20 Invite OG
- [x] CapCut JOB13 A/B/C · imagesets H20
- [x] In-app compose + share preview
- [x] Site OG + API `family_invite_og` deploy (MAIN …180)

### ASC 1290×2796 RU+EN
- [x] H01 MomHome
- [x] **H03** MariaSection — RU был; **EN CapCut вечером** fitted + headline
- [x] **H21** DrivingSpeed — RU был; **EN CapCut вечером** fitted + headline
- [x] H22–H24 Family map / sunset / driving path
- [x] H25–H26 Driving history (EN in-phone patched)
- [x] H27–H28 Driving reports (EN in-phone patched)
- [x] ASC_LOCALIZATION_SSOT + copy md

### Draft A–D (extras, не замена H20–H28 канона)
- [x] CapCut EN 6 кадров → fitted 1290×2796
- [x] CapCut RU Draft A–C (+ D twin) → fitted 1290×2796
- [x] DraftC: CapCut watermark scrub; EN stats **20–50 млн**; crash alert = Gary
- [x] Скопировано в repo · WaveB_All · `05_Full_ASC_RU_EN` · `07_FITTED`

| Draft | RU | EN | Смысл |
|-------|----|----|-------|
| A | ✅ | ✅ | Family Circle driving stats + Gary crash |
| B | ✅ | ✅ | Lock screen place alerts |
| C | ✅ | ✅ | WHO safety facts Mercedes |
| D | ✅ twin | ✅ | Two phones shield scan |

---

## ASC upload — простыми словами (не код)

Это **загрузка готовых PNG** на витрину App Store (руками в браузере). Не `git`, не сервер, не Xcode.

1. Открыть [App Store Connect](https://appstoreconnect.apple.com) → приложение **ALADDIN** → нужная **версия** → блок **Скриншоты** (iPhone).  
2. Взять PNG из:
   - репо: `docs/AppStore/asc_screenshots_wave_b_2026-11-12/`
   - или Finder: `~/Downloads/ALADDIN_ASC_WaveB_All/`
3. **H\*** = основные кадры (карта, езда, отчёты…): `ALADDIN_ASC_H01_*` … `H28_*` (RU+EN где есть).  
4. **Draft A–D** = 4 бонусных: статистика+Gary · lock-алерты · ВОЗ/Mercedes · два телефона (`ALADDIN_ASC_DraftA_*` … `DraftD_*`).  
5. **Решение владельца 2026-11-12:** грузить **и H\*, и Draft** (не только H*).  
6. Размер кадров: **1290×2796**. Gary на кадрах где уже есть — **не убирать**.

Чеклист слотов / copy: этот файл · `README_ASC_INDEX.md` · `ASC_LOCALIZATION_SSOT.md`.  
Полная карта путей: `docs/competitors/figma_preview_fig_l/ARTIFACT_MAP_WAVE_ABC_NO_DUPES_2026-11-12.md`.

---

## Статус пакета: где мы · с чего начать · где конец

| Этап | Статус | Кто |
|------|--------|-----|
| Код tip + SOS mid + G1 + heroes + QA-11 | ✅ в `master` (`55fb5602` · `62ee8dc2`) | агент сделал · **закоммичено** |
| ASC PNG H\*+Draft в репо/Downloads | ✅ готовы | агент |
| **Сборка Xcode / устройство** | ⏳ **вы сами** | владелец · агент **не** собирает |
| Device QA по приложению | ⏳ после вашей сборки | владелец |
| ASC upload в Connect | ⏳ когда решите | владелец (руками, § выше) |
| **Конец Wave B-чата** | после вашей QA (+ опц. ASC upload) | — |
| **Старт Wave C** | другой чат · `ML_HANDOFF_WAVE_C_…` · «GO Wave C art Batch1» | другая ML |

**Инвариант:** проект собирает **владелец**. Агент не делает `xcodebuild` / Simulator / Archive без явной фразы «GO на сборку» (и по умолчанию вы собираете сами).

---

## ⏳ Осталось

### ASC / продукт (нужен ваш GO)
- [x] **Слоты ASC:** владелец 2026-11-12 — **H\* + Draft A–D** (грузим всё) ✅ сделали решение; файлы fitted готовы
- [ ] **Ручной upload** H\*+Draft в App Store Connect (шаги § выше) — когда скажете
- [ ] OB_01 wordmark выше головы — отдельный GO (Figma↔iOS SYNC)
- [x] Tip card **wire** Where → Езда → отчёты ✅
- [x] SOS mid-tips (4 слайда text+SF между intro/release) ✅ CapCut art опц. позже
- [ ] CapCut NICE polish H01/H25–H28 (низкий приоритет)
- [ ] DraftC RU 20–50 млн (если ещё 35–50 в RU) — опц.

### Wave C — Ребёнок + Проверить (следующая волна иконок)
- [x] Стиль **Вариант A LOCKED** («всё как Семья»)
- [x] План + ML handoff: `PLAN_WAVE_C_…` · `ML_HANDOFF_WAVE_C_VARIANT_A_…`
- [ ] GO Wave C art Batch1 (C04–C10) → Glyph+Black → AliveGlyph wire — **другой чат**
- [ ] Не смешивать с Draft ASC

### Владелец / релиз
- [x] Wave A+B tip/SOS/ASC/docs → commit `55fb5602` (без bot / `.env`)
- [x] QA-11 хвост после build 20 → commit `62ee8dc2` — **без** `*_BACKUP_*` / bot
- [ ] **Сборка проекта — владелец сам** (Xcode)
- [ ] Device QA Wave B — после вашей сборки (агент не запускает sim)
- [ ] OB-QA · DEV-88 · bump · push — только ваши GO

### Инварианты (всегда)
- [x] Не коммитить `telegram_stars_shop_bot/` · `.env` · VPN secrets · `*_BACKUP_*` экраны
- [x] Не трогать OB_* Figma
- [x] Агент **не** `xcodebuild` — сборку делает владелец

---

## QA-11 хвост (после build 20) — в плане

**Build 20:** `3604688c` · 2026-11-10 12:56.  
**Правки на диске:** 2026-11-11 ~13:22–18:28 → **после** build 20 → **комитим** (отдельный QA-коммит).

| Файл | Когда | Суть |
|------|-------|------|
| `12_NotificationsScreen` · `NotificationSettingsScreen` | ~13:22–13:24 | полный текст по тапу · quiet hours UI |
| `07_ParentalControlScreen` · `ParentDashboardView` | ~13:29–13:34 | тёмный sheet без белых полей |
| `11_ProfileScreen` · `20_DevicesScreen` | ~13:29–13:42 | тариф «проверяем…» · счётчик устройств |
| `14_OnboardingScreen` | ~18:28 | взрослый онбординг → роль `parent` |

**Не коммитить:** `01_MainScreen_BACKUP_*` · bot · `.env` · BACKUPS · `.DS_Store`.

---

## Канон H20–H23 (не путать с Draft)

| ID | Статус |
|----|--------|
| H20 Invite OG | ✅ DONE + deploy |
| H21 ASC | ✅ RU+EN (EN обновлён вечером) |
| H22 ASC | ✅ RU+EN |
| H23 ASC | ✅ RU+EN |

---

## Куда смотреть сейчас

1. **Вы:** собрать в Xcode → Device QA (tip + SOS 6 стр + иконки).  
2. ASC PNG: `docs/AppStore/asc_screenshots_wave_b_2026-11-12/` · Downloads `ALADDIN_ASC_WaveB_All/` · `07_FITTED_1290x2796/`.  
3. Upload Connect — когда решите (не блокирует сборку).  
4. Код Wave B/QA-11 уже закоммичен — **не** ждать ещё «Сохраняй» на этот пакет.  
5. Wave C — **новый чат**, не продолжать art Child здесь.
