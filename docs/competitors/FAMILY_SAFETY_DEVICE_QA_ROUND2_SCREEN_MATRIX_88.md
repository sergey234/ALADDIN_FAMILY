## 13. OWNER GO тексты (2026-11-09)

| Тема | Выбор |
|------|-------|
| A пуш срочный | **A1** (текущий RU/EN) |
| B история 30 дней | **B1** «История мест за 30 дней» / «30-day location history» |
| C places «В » | **C1** убрать «В » у улиц + **C2** «Возле:» на sheet |
| R10 + R5.5 | **GO на код** · сборка только после 100% + отдельный GO |

### Push routing (зафиксировано в плане)

| Тип | Куда |
|-----|------|
| Срочный сигнал / Нужна помощь | Карта + member SOS sheet |
| Я ок | Карта / presence member |
| Батарея | Карта / member |
| Geofence / no-show | Карта + место |
| Привычки | Семья → habits |
| Лимиты / shield | Семья → limits |
| Угроза / bypass / AV | Network Protection / Antifake |
| Тарифы | Tariffs |
| Post-call / companion / focus | Свои экраны |
| Без type | Fallback **карта семьи**, не Удобный режим |

---

## 14. Матрица 88 скринов — было → будет → текст

**Счётчик:** 88 экранных задач · ~116 экранных подзадач (база+extras S19/notif) · +10 push-route · +7 атомов R10-1…7 ≈ **133 атомарных** до device evidence.

| ID | Экран | Волна | Было | Будет | Текст |
|----|-------|-------|------|-------|-------|
| S01 | onboarding_a | R0 | letterbox Fit | full-bleed Fill+zoom | (hero, без сырых ключей) |
| S02 | onboarding_b | R0 | letterbox Fit | full-bleed Fill+zoom | как S01 |
| S03 | map_mom_view | R5 | карта/пины | density + haptic | map_anti_spy_note короткий |
| S04 | map_adjacent | R5 | смежный map | тот же стек | — |
| S05 | antifake_disclaimer | R2 | длинный disclaimer | short banner | короткий баннер |
| S06 | antifake_verdict | R2 | пустой disclaimer | hide empty | вердикт без пустого текста |
| S07 | ios_call_blocking | R3 | имя ≠ app | ALADDIN X AI | ALADDIN X AI |
| S08 | simple_child | R1 | слабый контраст | gold title | золотой заголовок ребёнка |
| S09 | parental_panel | R1 | слабый контраст | contrast+copy | читаемая панель |
| S10 | speed_181_haptic | R5 | без gate | gate+SelectionHaptic | — |
| S11 | qr_invite | R7 | TTL | 72h ✅ W4 | QR 72 часа |
| S12 | always_allow_spy | R7 | spy-tone | честный anti-spy | короткая честная формулировка |
| S13 | tariffs_trial | R4 | ручной trial | auto trial | trial авто |
| S14 | tariffs_premium | R4 | bullets | antifake bullets | фичи antifake |
| S15 | call_filter_trunc | R3 | обрезка | короткие strings | короткие подписи |
| S16 | tariffs_table | R4 | таблица partial | polish | — |
| S17 | avatar_crop | R5 | нет crop | AvatarCropEditor | — |
| S18 | sections_color | R9 | цвета | polish iterative | — |
| S19 | life360_avatar_tap | R5.5 | слабый sheet | → S19a–h | см. S19a |
| S20 | quiet_zone | R6 | quiet zone | FAB тихая зона | Создать тихую зону |
| S21 | bg_refresh | R6 | BG refresh | гайд доступа | — |
| S22 | bt_motion | R6 | BT/motion | гайд доступов | — |
| S23 | journal_map | R6 | журнал | trip journal density | — |
| S24 | trip_car_chrono | R6 | хроно | trip car card | — |
| S25 | trip_passby | R6 | pass-by | passby card | — |
| S26 | trip_route | R6 | маршрут | route+map | — |
| S27 | hat_radius | R6 | радиус | slider | — |
| S28 | trip_details | R6 | детали | detail card | — |
| S29 | pin_shape | R5 | пин | pin parity | — |
| S30 | places_big | R5.5 | places | C1+C2 | Возле: / без «В » |
| S31 | event_create | R7 | событие | create event | — |
| S32 | event_who | R7 | кто | who picker | — |
| S33 | loc_notifs | R7+R10 | локальные пуши | deep-link карта+место | — |
| S34 | notif_battery | R10 | → Удобный режим | → карта/member | батарея близкого |
| S35 | notif_trips | R10 | → Удобный режим | → карта/trips | поездки |
| S36 | notif_safety | R10 | → Удобный режим | → карта/SOS | безопасность |
| S37 | notif_weather | R7 | weather | weather/map dest | — |
| S38 | notif_events | R7 | event notif | → event | — |
| S39 | notif_pet | R7 | pet Life360 | N/A не копируем | — |
| S40 | loc_access | R7 | доступ GPS | честный copy | — |
| S41 | circle_manage | R7 | круг | manage семьи | — |
| S42 | hats_access | R6 | доступ шапок | hat permissions | — |
| S43 | ui_compare_60 | R9 | compare | liked patterns | — |
| S44 | hat_settings | R6 | settings шапки | hat sheet | — |
| S45 | activity_share | R7 | share | activity share | — |
| S46 | leave_circle | R7 | leave | leave family | — |
| S47 | account_profile | R5 | профиль | profile+crop | — |
| S48 | flight_monitor | R7 | рейсы L360 | N/A later | — |
| S49 | lost_pets | R7 | pets | N/A | — |
| S50 | pet_alert | R7 | pet alert | N/A | — |
| S51 | ui_compare_liked | R9 | liked | перенос паттернов | — |
| S52 | inbox_mail | R7 | inbox | family inbox/chat | — |
| S53 | map_five_cards | R5 | 5 cards | map cards density | — |
| S54 | free_trial_ui | R4 | trial UI | auto trial | Попробовать / trial |
| S55 | create_circle | R7 | create | создать семью | — |
| S56 | circle_params_a | R7 | params A | params | — |
| S57 | circle_params_b | R7 | params B | params | — |
| S58 | trips_week | R6 | week trips | weekly card | Посмотрите поездки за эту неделю |
| S59 | gold_border | R1 | границы | contrast | — |
| S60 | add_wrap_pm | R1 | wrap | layout/contrast | — |
| S61 | trip_play_a | R6 | play A | play пин по нашему треку / fallback endpoints | — |
| S62 | trip_play_b | R6 | play B | scrubber + метрики · без чужого API | — |
| S63 | soft_reminders | R1 | простыни | hide soft prose | короткие напоминания |
| S64 | chip_nav | R8 | chips | monitoring chips | — |
| S65 | monitoring_17 | R8 | mismatch | pipeline copy | короткий мониторинг |
| S66 | family_day_trunc | R8 | truncate | no truncate | полный день |
| S67 | system_filter_a | R3 | filter A | короткие строки | — |
| S68 | system_filter_b | R3 | filter B | короткие строки | — |
| S69 | safari_extensions | R3 | Safari | гайд Safari | — |
| S70 | time_limits | R1 | контраст | UnifiedTimeLimits | лимиты времени |
| S71 | main_icons | R5 | иконки | icon polish | — |
| S72 | voice_5s | R2 | ~5s→10s | voice **30s** | RU: Быстрая проверка голоса (30 сек) · EN: Quick voice check (30 sec) |
| S73 | antifake_copy | R2 | длинный | short copy | короткий antifake |
| S74 | roadside_hide | R8 | видно roadside | hide accordion | скрыто |
| S75 | yandex_web | R9 | scrape risk | NO scrape | policy |
| S76 | call_filter_setup | R3 | setup | ALADDIN X AI | ALADDIN X AI |
| S77 | speed_online_max | R6 | speed max | gate+real | — |
| S78 | yandex_block_db | R9 | block DB | own lists | — |
| S79 | caller_id_features | R9 | caller id | polish | — |
| S80 | family_list_contrast | R1 | слабый список | contrast Family | — |
| S19a | member_sheet | R5.5 | частичный | полный sheet | Возле: · С HH:MM · Сохранить место · Создать шапку-невидимку |
| S19b | trip_sat | R5.5 | trip | map+route+км | дата · адрес → адрес · км |
| S19c | trip_sun | R5.5 | trip | длинный маршрут | как S19b |
| S19d | places_day | R5.5 | day places | unlock+stops | Разблокировать отчёт о поездках за эту неделю |
| S19e | history_upsell | R5.5 | Gold L360 | B1 ALADDIN | RU: История мест за 30 дней · EN: 30-day location history |
| S19f | trip_drive | R5.5 | drive | руль+скорость+риск | N рискованное событие |
| S19g | push_urgent | R10 | → Удобный режим | → карта+SOS | A1: Срочный сигнал семье / Нужна помощь близкого. Откройте ALADDIN и свяжитесь с ним. |
| S19h | places_list | R5.5 | «В улица» | C1+C2 | Львовская улица… · Возле: |

### Подзадачи (атомарно)

| Блок | Кол-во |
|------|--------|
| Экранные задачи S01–S80 + S19a–h | **88** |
| Экранные подзадачи (база + extras S19/notif) | **~116** |
| Push-типы маршрутизации | **10** |
| R10-1…R10-7 код | **7** |
| **Итого атомарных до device evidence** | **≈133** |
| Device evidence after (отдельный GO сборки) | +88 фото |

Код уже ✅ по волнам R0–R6,R8,R3…; R10 + R5.5.  
**Локализация:** политика G3 на все 88 (RU+EN strings, no raw keys). Колонка «Текст» с «—» ≈50 = нет отдельной фразы в матрице; ключи дописываются **по волне** (S30/Circles: FULL_TZ §2.7–2.8).  
**Next WAVE:** Circles B (S30 completer code ✅, device QA later). Сборка ⛔.

