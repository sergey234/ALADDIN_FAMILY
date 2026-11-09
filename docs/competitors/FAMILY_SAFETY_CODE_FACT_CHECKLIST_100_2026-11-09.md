# Family Safety — CODE-FACT чеклист 100% (S01–S80 + S19a–h)

**Дата:** 2026-11-09 · сверка **только по коду**, не по статусам в старых MD  
**Роль:** Principal iOS 15+ · Mech Pilot  
**Легенда:** ✅ сделано в коде · 🟡 частично · ❌ нет · ➖ N/A (не копируем / later) · ⏳ код есть, device QA нет  

## Промпт агента

```text
Principal iOS + Family Safety ALADDIN. SSOT этот файл + FULL_TZ.
Сверяй статус ТОЛЬКО grep/Read Swift/strings/plist. Docs = указатели, не proof.
No mock GPS/speed. RU+EN strings. Сборка/commit/push только после GO.
```

## Сводка (пересчёт 2026-11-09 вечер · live code)

| Корзина | Смысл | Примерно |
|--------|--------|----------|
| ✅ код мин./гибрид | ТЗ закрыто кодом (device ещё ⏳) | **~40+** из 88 (P0, play, quiet, X AI, 17 checks, voice 30s, chips, R10…) |
| 🟡 densitiy/polish | Есть каркас, не Life360 1:1 | **~25–30** (S16 таблица, S23 journal fullscreen, S52 mailbox art, S18 Snowball everywhere, S11 roster name, S42 ACL…) |
| ➖ N/A | Не делаем (согласовано) | S39 pet · S48 flights · S49–50 pets · scrape |
| ❌ долг | Нет артефакта | **FIG-L** |
| ⏳ | Evidence | **DEVICE-100** (сборка владельца) |

**Вердикт:** **нет**, не «все 88 на 100%». Обязательный код Round2 (P0 + согласованные волны + N/A) — **в основном влит**. Не закрыто: (1) densitiy-хвосты 🟡, (2) device evidence, (3) FIG-L, (4) commit/push.

---

## Чеклист по скринам (факт кода)

| ID | ТЗ владельца (суть) | Код-факт | Статус |
|----|---------------------|----------|--------|
| **S01–S02** | Full-bleed 8 стр. OB, без лишних отступов как build 17 | Hero_08 recomposed ~5% side margins (руки); zoom 01–07 без изменений; device «Где семья» ⏳ | ✅ код · ⏳ device |
| **S03** | Вид как L360 + время на пине + фото в фигуре с pan | Sheet **0.95** · pin time · pin photo из ProfileImage · pin tap | ✅ код · ⏳ device |
| **S05** | Короткий antifake disclaimer, не простыня | Вердикт-disclaimer `=""`; другие AI disclaimer-ключи ещё длинные | 🟡 |
| **S05b** | Timeout «слишком долго» Text/Doc/Voice/Video/Call | Retry/timeout пути есть; flaky prod = сервер/сеть, не только UI | 🟡 |
| **S06** | Убрать «вердикт неверный / не юр. / калькулятор» | `antifake_verdict_disclaimer` пустой; показ только если непусто | ✅ |
| **S07** | Имя в iOS = как в Settings; ссылка куда | Extension + strings **ALADDIN X AI**; Settings deep link в card | ✅ код · ⏳ device |
| **S08** | «Ребёнок» золотом; убрать простыню про карту; иконки семьи по центру | `secondaryGold` на child title; spy-простыня в child не найдена; centering иконок — не доказано | 🟡 |
| **S09** | Parent panel цвет без белых полей | Snowball purple→magenta + StormMesh veil 0.18; glass не full-bleed white | ✅ код · ⏳ device |
| **S10** | Только реальная скорость; haptic на scroll chips | Скорость из `CLLocation` (нет hardcode 181); scroll-spy haptic **на WhereIsPhone** есть; **не** раскатано на все разделы | 🟡 |
| **S11** | QR работает; TTL; «Родитель А» 1 раз | Invite TTL hint **3 дня (=72h)**; дубль имени — UI/roster, не закрыто grep-ом | 🟡 |
| **S12** | Убрать «без скрытого отслеживания» | Короткий `map_anti_spy_note` (последняя точка) | ✅ |
| **S13** | Auto-trial; убрать путаницу 2× бесплатно; «Бесплатно» без переноса | Trial A keys/UI; RU agreement **«Подписаться»**; polish таблицы/карточки — 🟡 | ✅ мин · 🟡 polish |
| **S14** | Antifake bullets по тарифам; убрать лишнее; Subscribe RU | `tariffs_antifake_*` в features; agreement EN; purchase RU «Оформить подписку» | 🟡 |
| **S15** | Текст не обрезать; Call Filter→понятно; Settings path | Truncation layout ⏳; имя X AI / Call Filter смешанно EN | 🟡 |
| **S16** | Таблица тарифов топ-уровня | Таблица есть; «устройства/бесплатно/семья» всё ещё сырой UX | 🟡 |
| **S17** | Crop/pan аватара везде | AvatarCrop в Profile + **member sheet**; pin показывает фото | ✅ код · ⏳ device |
| **S18** | Snowball цвета разделов | Retoken ✅ purple→magenta · rollout Parent/Parental/map sheets/trips/hub/modals ✅ · OB не трогали | ✅ код · ⏳ device |
| **S19** | Member sheet = L360 one scroll (7 jpg) | Pin tap · one-scroll · crop · stays · weekly/upsell/quiet · mini-map **если live track**; список поездок с API пока пуст (`applyFrom` → `reports=[]`) | ✅ каркас · 🟡 densitiy trips |
| **S19a–h** | Эталон 7 скринов | Файлы в `qa_device_…/S19_life360_member/` | ✅ эталон |
| **S20** | Тихая зона (шапка) | `FamilyMapQuietZoneStore` + FAB/sheet | ✅ |
| **S21** | Background App Refresh | `UIBackgroundModes` = **fetch** only; гайд UX | 🟡 |
| **S22** | BT + Motion как L360 | Motion для crash/auto-trip; **нет** L360-style BT+Fitness onboarding; канон B не требует Always-spy | ➖/🟡 |
| **S23** | Journal map full-screen | Driving/trip map preview есть; не full-screen journal L360 | 🟡 |
| **S24–S25** | Машинка / pass-by / хроно | Trip cards densitiy + chrono в DrivingReports | 🟡 |
| **S26** | Маршрут на карте | Polyline из **наших** точек / endpoints; не Directions API | ✅ гибрид |
| **S27** | Slider радиуса тихой зоны | Slider 50…500 в quiet sheet + member | ✅ |
| **S28** | Подробности поездки | Driving detail + play | 🟡 |
| **S29** | Пин-фигура + crop фото | Pin + фото из ProfileImage; crop через member sheet | ✅ код · ⏳ device |
| **S30** | Большой выбор мест + completer | Places/geofence + completer wave | 🟡 |
| **S31–S32** | Создать событие + кто увидит | Draft title/place/start/end/audience в WhereIsPhone calendar | 🟡 |
| **S33–S39** | Notif matrix + тексты | Keys + `FamilyPushDeepLink`; weather/pet L360 **N/A** | 🟡/➖ |
| **S40** | Доступ к месту — честный copy | Info.plist plain language (no Always jargon) | ✅ |
| **S41** | Круг/роли/название | `FamilyGroupsModal` = labels внутри семьи (не 2-й roster) | 🟡 |
| **S42** | Доступ к тихим зонам | Quiet store; отдельный L360 ACL экран — нет | 🟡 |
| **S43** | UI compare 60+ | Iterative; Snowball tokens | 🟡 |
| **S44** | Настройки шапки кому | Quiet global meters; per-member ACL L360 — нет | 🟡 |
| **S45** | Share activity | `map_share_activity_*` + duration picker | ✅ |
| **S46** | Leave circle | `FamilyLocalStore.leaveFamilyOnThisDevice` | ✅ |
| **S47** | Profile improve + crop | Profile + AvatarCropEditor | 🟡 |
| **S48** | Flights | Не продукт сейчас | ➖ |
| **S49–S50** | Pets lost | Нет маячков; soon sheets | ➖ |
| **S51** | Liked UI patterns | Partial Snowball | 🟡 |
| **S52** | Inbox mail UI | Family inbox/chat foundation; не L360 mailbox art | 🟡 |
| **S53** | 5 chips на карте | Family/Pets/Items/Places/Events chips | ✅ |
| **S54** | Free trial 14d UI | Trial strings/UI; auto+баннер — product fork | 🟡 |
| **S55–S57** | Create circle templates | Groups labels ≠ L360 multi-circle templates | 🟡 |
| **S58** | Weekly trips + locks | weekly strip densitiy + tariff gate + honest violations | ✅ код · ⏳ device |
| **S59** | Золотой ободок | SecondHand gold stroke + accent | ✅ код · ⏳ device |
| **S60** | «Добавить» wrap; PM/PA | AddMoreMember `lineLimit(1)` + scale | ✅ код · ⏳ device |
| **S61–S62** | Play по маршруту | Playhead + scrubber + наш трек/endpoints | ✅ |
| **S63** | Убрать soft reminder простыню | Часть soft-copy ещё в geofence/family | 🟡 |
| **S64** | Chip nav как на карте | Day strip chips + family hub cards | ✅ код · ⏳ device |
| **S65** | 17 проверок кликабельны | `FamilyChildThreatCoverageView` ×17 routes (fork C) | ✅ код · ⏳ device |
| **S66** | Family day truncate sync | Day strip 2-line / scale | ✅ код · ⏳ device |
| **S67–S68** | System filter text + enable | Content filter extension есть; UX copy / simulator limits | 🟡 |
| **S69** | Safari Aladdin просто RU | Safari guide screens; «content blocked» jargon — чистить | 🟡 |
| **S70** | Time limits светлый текст | `UnifiedTimeLimitsScreen` white/gold | ✅ |
| **S71** | Иконки main как L360 | Main grid icons 28pt / cards 100h | ✅ код · ⏳ device |
| **S72** | Voice 30s + единый стиль | `maxDuration = 30` | ✅ |
| **S73** | Короткий antifake copy | Частично | 🟡 |
| **S74** | Убрать roadside из блока | Hub: no roadside dispatch; component strings ещё живут | 🟡 |
| **S75** | Yandex web scrape? | Policy: **no scrape** | ✅ |
| **S76** | Call filter UI + Settings deep link | X AI + gold title contrast on card | ✅ код · ⏳ device |
| **S77** | Скорость online/max real | Live speed badge on map | ✅ код · ⏳ device |
| **S78** | Yandex block DB | Own lists; не чужой scrape | ➖/✅ |
| **S79** | Caller ID features | Extension X AI displayName | ✅ код · ⏳ device |
| **S80** | Family list contrast | Gold CTA ink + StormMesh family | ✅ код · ⏳ device |
| **R10** | Push → map/SOS не Удобный | `FamilyPushDeepLink.swift` | ✅ |
| **Canon B** | Quiet all paths + auto-trip | QuietZoneStore + AutoTripTracker + LocationManager gates | ✅ |
| **FIG-L** | Figma family file | Не создан | ❌ |
| **Device 88** | after evidence | Нет GO сборки | ⏳ |

---

## P0 / copy (после кода)

1–5 P0 — ✅ код · ⏳ device  
6. RU «Подписаться» — ✅ strings  
7. ALADDIN X AI — ✅ strings + CallDirectory displayName · ⏳ device Settings  


## Гибрид

Life360 **UX** (member scroll, chips, quiet, trip play) + ALADDIN copy/Snowball + **только наши GPS** (без Directions/Yandex scrape).
