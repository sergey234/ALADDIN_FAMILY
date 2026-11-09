# Family Safety — МАСТЕР-ПЛАН доделки до 100% (88 экранов)

**Дата:** 2026-11-09 · **Build код:** **19** · marketing **1.0.2**  
**Правило закрытия:** **НЕ закрывать Round2 / не писать «готово 100%»**, пока по **всем 88** (S01–S80 + S19a–h) нет кода **и** device evidence (или явный ➖ N/A владельца).  
**Сверка статуса:** только **код** (`FAMILY_SAFETY_CODE_FACT_CHECKLIST_100_2026-11-09.md`), не старые ✅ в MD.  
**Эталон S19:** `qa_device_2026-11-09/S19_life360_member/` (7 jpg) ✅  

### Карта SSOT

| Документ | Роль |
|----------|------|
| **Этот файл** | Очередь доделки + волны + loc + рекомендации |
| `FAMILY_SAFETY_CODE_FACT_CHECKLIST_100_2026-11-09.md` | Факт ✅/🟡/❌ по коду |
| `FAMILY_SAFETY_DEVICE_QA_ROUND2_FULL_TZ_CHECKLIST_2026-11-09.md` | Полное ТЗ владельца |
| `FAMILY_SAFETY_DEVICE_QA_ROUND2_SCREEN_MATRIX_88.md` | Матрица was→will |
| `FAMILY_LOCATION_CANON_B_PLAN_2026-11-09.md` | Канон места B |
| `FAMILY_SAFETY_REMAINING_WORK_PLAN_2026-11-09.md` | Почему дыры |
| `FIGMA_FAMILY_SAFETY_ML_PROMPTS.md` | FIG-L долг (не OB_*) |
| `SNOWBALL_S18_COLOR_CANON_FOR_ML_2026-11-09.md` | **S18 цвет:** эталон jpg + HEX + куда вставлять + промпт для другой ML |
| `snowball_s18_ref/OWNER_SNOWBALL_COLOR_REF_2026-11-09.jpg` | Эталон цвета владельца (purple→magenta) |

---

## 0. Промпт агента (копировать в каждую волну)

```text
Роль: Principal iOS + Family Safety ALADDIN (15+ лет). Mech Pilot: пилот=владелец, меха=агент.
SSOT: docs/competitors/FAMILY_SAFETY_MASTER_FINISH_88_PLAN_2026-11-09.md
Факт: FAMILY_SAFETY_CODE_FACT_CHECKLIST_100_2026-11-09.md (только код).
Эталон S19: qa_device_2026-11-09/S19_life360_member/
Канон B: тихая зона; маршрут только в поездке; no mock GPS/speed; no Yandex scrape; no Directions API.
Локализация: сначала Resources/Localization/{ru,en}.lproj/Localizable.strings — без сырых ключей.
LocManager: только точечный StrReplace + ./scripts/verify_localization_manager_integrity.sh
Навигацию не ломать. Сборка / commit / push — только после явного GO.
FIG-L — отдельный GO; не трогать OB_* Figma onboarding file.
НЕ ставить «100% / закрыто» пока открыт любой ❌/🟡 обязательный или нет device evidence.
Гибрид: Life360 UX + ALADDIN copy/Snowball + наши реальные точки.
Snowball цвет S18: ТОЛЬКО канон SNOWBALL_S18_COLOR_CANON_FOR_ML_2026-11-09.md
  (jpg purple→magenta; текущий navy в AladdinSnowballPalette = WRONG until retoken).
```

---

## 1. Что уже РЕШИЛИ (продукт) — зафиксировано

| Решение | Канон |
|---------|--------|
| Место семьи | **B** — свежая точка + места; маршрут в поездке; **Тихая зона**; не 24/7 spy trail |
| Play S61–62 | Стек **1+2**: пин по нашему треку; fallback старт→финиш; без чужого API |
| Member S19 | **Одно scroll-окно** как L360 (7 фото); tap pin → sheet; tap avatar → crop |
| Quiet UI имя | **Тихая зона** (не «шапка-невидимка» в copy) |
| Call Directory | В Settings: **ALADDIN X AI** |
| История 30д | ALADDIN copy B1 (не Life360 Gold) |
| Pets / flights | **➖ N/A** сейчас (soon / prep only) |
| Yandex scrape | **Запрет** |
| FIG-L | Отдельный файл; не блокер кода P0 |
| **Snowball S18 цвет** | Эталон владельца jpg (`snowball_s18_ref/…`) = **purple→magenta glow**, не navy. Канон: `SNOWBALL_S18_COLOR_CANON_FOR_ML_2026-11-09.md` |
| Закрытие | Только после **100% по 88** + evidence |

---

## 2. Уже СДЕЛАНО в коде (не трогать без регресса)

| Тема | Статус |
|------|--------|
| Quiet zone + gate на send paths | ✅ |
| Auto-trip + DrivingTripTrackStore | ✅ |
| Play 1+2 (playhead + endpoints) | ✅ |
| R10 FamilyPushDeepLink | ✅ |
| Voice **30s** recorder | ✅ |
| S06 disclaimer вердикта пустой | ✅ |
| S12 anti-spy короткий | ✅ |
| S20/S27 slider тихой зоны | ✅ |
| S26 polyline наших точек | ✅ |
| S40 Info.plist plain language | ✅ |
| S45 share / S46 leave | ✅ |
| S53 5 chips | ✅ |
| S70 time limits contrast | ✅ |
| S75 no scrape policy | ✅ |
| Canon B legal site pack | ✅ publish был |
| Build bump **19** | ✅ (push нет) |
| 7 скринов S19 на диске | ✅ |

---

## 3. НЕ сделано / не до конца — очередь доделки

### WAVE FIX-P0 (обязательно первым после GO на код)

| ID | Что | Как наилучшим образом | Loc RU / EN (strings first) |
|----|-----|----------------------|------------------------------|
| P0-1 | OB_00…07 full-bleed как build 17 | ✅ код: `fillsViewport` + hero first + soft zoom; ⏳ device | без новых ключей (layout) |
| P0-2 | Sheet карты **90–95%** | ✅ код: snap full **1.0** → ~95%; any chip → full; ⏳ device | — |
| P0-3 | Pin tap → member | ✅ код: `didSelect` → `openMemberFromMapPin`; ⏳ device | — |
| P0-4 | Member = **одно** scroll окно | ✅ код: avatar→near→save→trips→stays→weekly→upsell→quiet; mini-map → S19-POLISH; ⏳ device | см. §5 |
| P0-5 | Tap аватар → crop/pan | ✅ код: ImagePicker → `AvatarCropEditor`; ⏳ device | `avatar_crop_*` |
| P0-6 | «Телефон потерян» CTA | ✅ код: Events scrollTo lost; ⏳ device | `where_phone_lost_*` |
| P0-7 | «Телефон потерян» sticky | **ОТКАТ** — снова только scroll P0-6 (как просил владелец) | — |

### WAVE S19-POLISH (после P0)

| ID | Экран | Доделать |
|----|-------|----------|
| S19b–f | Trip/stay cards inline | Реальные `DrivingReport` + track; C1 без «В » |
| S19g | Upsell 30d | ALADDIN B1; CTA trial/family |
| S19h | Risk row | Реальные events; без mock 181 |

### WAVE COPY-XAI-TARIFFS

| ID | Доделать |
|----|----------|
| S05/S73 | Добить короткие баннеры; убрать остатки простынь |
| S07/S15/S76 | ✅ код: EN/RU strings + LocManager + CallDirectory displayName → **ALADDIN X AI**; Settings URL уже в card; ⏳ device |
| S13–S16 | ✅ RU `tariffs_subscribe_agreement_text` → «Подписаться»; Trial A UX / таблица — ещё 🔓 |
| S08 | Gold title verify; centering «Вся семья» icons |
| S09 | Snowball без белых полей |
| S11 | 1× имя в QR/roster |
| S63 | Убрать soft-reminder простыни |

### WAVE HAPTIC-ROLL (по очереди, без mass rewrite)

По образцу WhereIsPhone scroll-spy → Child → Settings → Parental → 60+ → Menu → Tariffs → Rewards → Add. Helper `SelectionHaptic` уже есть.

### WAVE TRIPS-JOURNAL (S23–28, S58)

Плотность L360: хроно, pass-by, weekly art — **реальные** данные; иллюстрации машинки = asset/FIG-L later.

### WAVE FILTER-MONITOR (S64–69, S65)

Кликабельные проверки или честный empty; Safari/System filter — простой RU/EN; 3 варианта copy в FULL_TZ.

### WAVE VISUAL (S18, S71, S80, S59–60)

Snowball **цвет** → канон `SNOWBALL_S18_COLOR_CANON_FOR_ML_2026-11-09.md` (не navy).  
Main icons size; family list contrast; «Добавить» no wrap.

#### S18 — куда кладём цвет (кратко)

| Порядок | Куда | Файл |
|---------|------|------|
| 1 | Parent dashboard | `ParentDashboardView.swift` |
| 2 | Parental (убрать белые поля) | `07_ParentalControlScreen.swift` |
| 3 | WhereIsPhone sheets | `WhereIsPhoneScreen.swift` |
| 4 | Trips / play chrome | `DrivingReportsModal.swift` |
| 5 | Family remainder hub | `FamilySafetyRemainderHub.swift` |
| 6–8 | Groups / SecondHand shell / Filter hub фон | см. канон §4 |

**Не трогать:** OB_* · MapKit тайлы · snowball-иконку на каждый экран.  
**Код-шаг:** сначала retoken `AladdinSnowballPalette.swift` под HEX §2 канона → потом rollout 1–5.  
**100%?** Градиент UI ≥95% да; pixel-jpg bloom — только если GO «jpg фоном».

### WAVE N/A LOCK

S39 pet notif · S48 flights · S49–50 pets beacon — **не делать** до отдельного GO; soon sheets ok.

### WAVE FIG-L (отдельный GO)

L34 / L15 / L25 / L01 / L03 — новый Figma file.

### WAVE DEVICE-100

После кода: **GO на сборку** → evidence `*_after` по 88 → только тогда «Round2 100%».

---

## 4. Чеклист доделки (открыт до 100%)

| Волна | Статус | Закрыть когда |
|-------|--------|---------------|
| FIX-P0 | 🟡 код ✅ · device ⏳ | P0-1…6 влиты |
| S19-POLISH | 🟡 код ✅ · device ⏳ | one-scroll + stays C1 + mini-map live track |
| COPY-XAI-TARIFFS | 🟡 X AI + Subscribe RU ✅ · таблица 🟡 | Call Filter scrubbed |
| HAPTIC-ROLL | 🟡 Child+map+parental+tariffs | остальное по мере экранов |
| TRIPS-JOURNAL | 🔓 | densitiy без mock |
| FILTER-MONITOR | 🔓 | taps или honest empty |
| VISUAL | 🟡 код ✅ · device ⏳ | S18 retoken+rollout · Hero_08 hands recompose · icons/contrast уже были |
| N/A LOCK | ✅ | S39 pet · S48 flights · S49–50 pets = ➖ (не делать) |
| FIG-L | 🔓 после сборки владельцем · самый конец | отдельный GO |
| DEVICE-100 | 🔓 | 88 after + owner sign-off |

**Запрет:** `merge: completed` / «готово» на Round2 при любом обязательном 🟡/❌.

---

## 5. Локализация доделки (без сырых ключей)

Сначала `Localizable.strings` RU+EN. LocManager — только якорь StrReplace. После — `verify_localization_manager_integrity.sh`.

| Ключ (логика) | RU | EN | Где |
|---------------|----|----|-----|
| `map_member_save_place` | Сохранить место | Save place | S19 (уже есть — проверить) |
| `map_live_near_place` | Возле: %@ | Near: %@ | S19 |
| `map_member_since_fmt` | С %@ | Since %@ | S19 |
| `map_member_weekly_trips_title` | Посмотрите поездки за эту неделю | See trips for this week | S19 |
| `map_member_unlock_weekly` | Разблокировать отчёт о поездках за эту неделю | Unlock this week’s trip report | S19 |
| `location_history_30d_title` | История мест за 30 дней | 30-day location history | S19g B1 |
| `map_privacy_zone_title` / FAB | Создать тихую зону | Create quiet zone | S20 |
| `tariffs_subscribe_agreement_text` | Нажимая «Оформить подписку», вы соглашаетесь с | By tapping Subscribe, you agree to | S13 **FIX EN в RU** |
| `antifake_call_directory_extension_name` | ALADDIN X AI | ALADDIN X AI | S07 — EN dedupe Call Filter |
| `tariffs_purchase_button` | Оформить подписку | Subscribe | S14 — RU уже ок |
| `driving_play_*` | существующие | существующие | S61 |
| `family_invite_ttl_hint` | 3 дня | 3 days | S11 ok |

Новые ключи — только если нет существующих; **не** показывать raw key в UI.

---

## 6. Рекомендации Principal (как делать лучше)

1. **Сначала FIX-P0** — то, что владелец уже показал на скринах (OB, sheet, pin, member).  
2. **Один member ScrollView** — не плодить вторые модалки на каждый блок L360.  
3. **Crop один** (`AvatarCropEditor`) — профиль + member + pin preview.  
4. **Haptic** — только через helper, экран за экраном.  
5. **Тарифы** — один язык в agreement; trial не дублировать как «второй бесплатный» без решения A/B/C владельца (в FULL_TZ уже Trial A).  
6. **17 checks** — либо deep-link на реальный экран, либо «Скоро» — не мёртвые карточки.  
7. **Device evidence** — единственный способ закрыть ⏳; без GO на сборку 100% невозможно честно.  
8. **FIG-L** — после стабильного UX кода, иначе дважды переделывать.

### Гибрид (канон)

Life360 **поведение и плотность** + ALADDIN **шрифт/Storm/Snowball/Тихая зона** + данные **только реальные**.

---

## 7. Порядок исполнения (после GO)

```text
1) GO на код → WAVE FIX-P0
2) WAVE S19-POLISH
3) WAVE COPY-XAI-TARIFFS
4) WAVE HAPTIC-ROLL (порциями)
5) WAVE TRIPS-JOURNAL + FILTER-MONITOR + VISUAL
6) verify loc integrity + static
7) СТОП → спросить GO на сборку
8) DEVICE-100 evidence 88
9) (опц.) FIG-L GO
10) GO на commit → GO на push (build 19)
```

---

## 8. Cursor TODO ids (`fs88-*`) — полный список доделки

Не удалять ids. Закрывать только `merge: true`. **Не** ставить completed на Round2 meta, пока DEVICE-100 не PASS.

| id | Волна / экран |
|----|----------------|
| `fs88-meta` | SSOT / правило 100% |
| `fs88-forks` | S65 · Circles · Trial — ждать буквы владельца |
| `fs88-p0-1-ob` … `fs88-p0-6-lost` | FIX-P0 |
| `fs88-s19-trips` / `stays` / `upsell` | S19-POLISH |
| `fs88-s05-s73` `s07-xai` `s08` `s09` `s11` `s13-16` `s63` | COPY-XAI-TARIFFS |
| `fs88-haptic-queue` | HAPTIC-ROLL |
| `fs88-s30` `s31-32` `s33-39` `s41-44` `s45-47` `s52` `s54-57` `s58` `s59-60` | бывшие «сжатые» экраны — **по одному** |
| `fs88-s23-28` `s64-65` `s66` `s67-69` `s71` `s74` `s76-79` `s18-s80` `s10` `s21-22` `s29` | TRIPS/FILTER/VISUAL/depth |
| `fs88-na-lock` | S39/48–50 ➖ |
| `fs88-loc-gate` | strings RU+EN + verify |
| `fs88-fig-l` | FIG-L отдельный GO |
| `fs88-device-88` | evidence 88 |
| `fs88-commit-push` | GO commit/push |

### 8.1 Owner forks (открыто)

| # | Вопрос | Рекомендация | Статус |
|---|--------|--------------|--------|
| 1 | S65 17 проверок A/B/**C** | **C** hybrid | ✅ locked владельцем |
| 2 | Circles S55–57 **A**/B | **A** labels | ✅ locked |
| 3 | Trial S13 **A**/B/C | **A** hide card + auto | ✅ locked |

FIX-P0 код влит (после GO). Device smoke — после **GO на сборку**.

### 8.2 Атомарный чеклист «сжатых» экранов (теперь явно)

| ID | Доработка | Loc note |
|----|-----------|----------|
| S30 | Places big + completer | RU/EN place names keys |
| S31–32 | Event Name/Place/Today/Tomorrow/Who | `family_cal_*` |
| S33–39 | Notif copy battery/trips/safety/weather/events; pet ➖ | existing notif keys + wire |
| S41–44 | Circle manage / quiet ACL | по fork A |
| S45–47 | Share depth / leave / profile | existing |
| S52 | Inbox mailbox UI | new keys if needed |
| S54–57 | Trial 14d UI + circle templates | по fork A/B |
| S58 | Weekly art densitiy | real gates |
| S59–60 | Gold border / Добавить wrap / PM·PA | fix strings lineBreak |
| S64–66 | Monitoring chips / 17 / day strip | fork C |
| S67–69 | Filter + Safari plain RU/EN | 3 copy options → pick |
| S71–79 | Icons / roadside hide / call / speed / lists | no scrape |
| S18+S80 | Snowball + list contrast | tokens |

---

## 9. Журнал

| Дата | Событие |
|------|---------|
| 2026-11-09 | Мастер-план создан; правило «не закрывать до 100%/88» |
| 2026-11-09 | Code-fact + 7 S19 jpg + remaining |
| 2026-11-09 | Cursor TODO `fs88-*` полный · сжатые экраны развернуты в §8 |
| — | Ждём forks **C/A/A** (или свои) + **GO на код FIX-P0** |
