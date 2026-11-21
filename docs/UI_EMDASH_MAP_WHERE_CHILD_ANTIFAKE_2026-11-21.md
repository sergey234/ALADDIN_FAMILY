# Карта длинного тире «—»

Экраны сегодня: **Где семья** · **Ребёнок** · **Проверить** (+ связанные правки).

Ищем только **длинное тире** `—` (не `-`, не `–`).

**Первая очередь сделана:** на экранах сегодняшней работы длинное `—` → среднее `–` (аккуратно по ключам RU+EN + видимые UI-плейсхолдеры).  
Логи/комментарии разработчика не трогали.  
**Следующий шаг (отдельно):** поиск `—` **по всему приложению**.

## Схема (где смотреть)

```
Где семья
 ├─ Баннер / герой / Поделиться местом
 ├─ Питомцы · Вещи · Места · События
 ├─ Вождение
 └─ Безопасность · Подписка · Тихая зона
Ребёнок
 ├─ Дверь Home (пауза / ещё / минуты)
 └─ Родительский контроль / лимиты
Проверить
 └─ Хаб · история · семейная база
```

---

## Где семья · баннер / герой / шаринг

**С «—»:** 5

### 1. `map_share_expired`

- **RU:** Срок ссылки истёк **【—】** отправьте место снова
- **EN:** Location link expired **【—】** send your place again

### 2. `family_invite_soft_body`

- **RU:** Добавьте ещё одного человека в семью **【—】** увидите защиту и точку на карте.
- **EN:** Add one more person **【—】** see protection and their place on the map.

### 3. `family_invite_ttl_hint`

- **RU:** Коды приглашения действуют 3 дня. Если не успели **【—】** отправьте новый.
- **EN:** Invite codes work for 3 days. If it expired, send a new one.

### 4. `map_share_activity_hint`

- **RU:** Семья увидит одну точку **【—】** только на выбранное время.
- **EN:** Family sees one point **【—】** only for the time you choose.

### 5. `share_arrived_home_body`

- **RU:** Можно коротко сказать в WhatsApp или чате **【—】** без лишних звонков.
- **EN:** You can share a short note in WhatsApp or chat **【—】** no extra calls.

---

## Где семья · Питомцы / Вещи / Места / События

**С «—»:** 6

### 1. `location_events_empty_live`

- **RU:** Пока нет событий за сегодня. Когда ребёнок дойдёт до школы или другого места **【—】** здесь появятся время и уведомление.
- **EN:** No events today yet. When your child reaches school or another place, the time and a notification appear here.

### 2. `geofences_empty_list_hint`

- **RU:** Нет мест **【—】** добавьте Дом или Школу
- **EN:** No places **【—】** add Home or School

### 3. `geofences_empty_body`

- **RU:** Добавьте Дом или Школу **【—】** с реальным адресом.
- **EN:** Add Home or School with a real address.

### 4. `geofence_noshow_section_hint`

- **RU:** Если к сроку человека нет на месте **【—】** придёт уведомление.
- **EN:** If they’re not at the place by then, you’ll get a notification.

### 5. `geofence_noshow_roles_hint`

- **RU:** Родитель видит места ребёнка (если настроено). Супруги не следят друг за другом **【—】** каждый настраивает свой телефон.
- **EN:** A parent sees a child’s places when set up. Spouses do not track each other **【—】** each sets up their own phone.

### 6. `location_events_7d`

- **RU:** События мест за 7 дней
- **EN:** Place events **【—】** last 7 days

---

## Где семья · Вождение

**С «—»:** 11

### 1. `trip_no_map_track`

- **RU:** Маршрут на карте **【—】** после поездки с доступом к месту
- **EN:** Map route after a trip with location access

### 2. `asc_tip_driving_reports_body`

- **RU:** Пробег, макс. скорость и число поездок по каждому **【—】** после реальной поездки.
- **EN:** Mileage, max speed, and trips for each family member **【—】** after a real drive.

### 3. `driving_reports_why_motion`

- **RU:** 1. Разрешите «Движение и фитнес» для ALADDIN **【—】** так телефон понимает поездку.
- **EN:** 1. Allow Motion & Fitness for ALADDIN so the phone can detect driving.

### 4. `driving_reports_why_location`

- **RU:** 2. Включите геолокацию «Всегда» (и точное место) **【—】** иначе поездки в фоне не пишутся.
- **EN:** 2. Turn on Location Always (and Precise) so trips can record in the background.

### 5. `driving_reports_why_trip`

- **RU:** 3. Проедьте за рулём с открытым или в фоне ALADDIN **【—】** затем откройте «Вождение» снова.
- **EN:** 3. Take a drive with ALADDIN open or in the background, then open Driving again.

### 6. `drive_weekly_locked_title`

- **RU:** Риски за рулём **【—】** по Family/Premium
- **EN:** Driving risks **【—】** Family/Premium

### 7. `drive_weekly_locked_body`

- **RU:** Счётчики скорости и резких манёвров открываются на семейном тарифе. Поездки и км без выдуманных цифр.
- **EN:** Speed and harsh-maneuver counts unlock on a family plan. Trip and km stats stay honest **【—】** no invented numbers.

### 8. `drive_inc_explain_data_note`

- **RU:** Пока нет поездок с датчиками **【—】** счётчики 0. На вкладке «Вождение» нажмите «Разрешить движение и фитнес», затем совершите поездку.
- **EN:** No sensor trips yet **【—】** counters stay 0. On the Driving tab tap Allow Motion & Fitness, then take a drive.

### 9. `drive_pdf_disclaimer`

- **RU:** Оценка для семьи, не страховой отчёт.
- **EN:** Family estimate only **【—】** not an insurance report.

### 10. `driving_play_no_track`

- **RU:** Маршрут появится после поездки с доступом к месту. Пока **【—】** время, км и скорость
- **EN:** Route appears after a trip with location access. Showing time, km, and speed for now

### 11. `family_crash_tip_body`

- **RU:** Нужны: геолокация «Всегда», «Движение и фитнес» и уведомления **【—】** иначе защита в фоне не сработает.
- **EN:** Needs: Always location, Motion & Fitness, and notifications **【—】** or background protection won’t work.

---

## Где семья · Безопасность / Подписка / тихая зона

**С «—»:** 3

### 1. `map_hub_safety_sos_note`

- **RU:** Удержание SOS для семьи **【—】** на следующем шаге. Без «помощь уже едет».
- **EN:** Family SOS hold comes next. No “help is on the way” without a partner.

### 2. `family_invite_soft_body`

- **RU:** Добавьте ещё одного человека в семью **【—】** увидите защиту и точку на карте.
- **EN:** Add one more person **【—】** see protection and their place on the map.

### 3. `family_invite_ttl_hint`

- **RU:** Коды приглашения действуют 3 дня. Если не успели **【—】** отправьте новый.
- **EN:** Invite codes work for 3 days. If it expired, send a new one.

---

## Ребёнок · Home дверь + пауза / ещё

**С «—»:** 1

### 1. `child_overview_body`

- **RU:** Пауза, сайты, лимит и сон **【—】** ниже. Полные отчёты **【—】** в родительском разделе.
- **EN:** Pause, sites, limits and bedtime are below. Full reports are in Parental.

---

## Ребёнок · родительский контроль / лимиты

**С «—»:** 2

### 1. `parental_filter_safari_honesty`

- **RU:** Фильтр сайтов работает в Safari. В других приложениях **【—】** отдельно.
- **EN:** Site filter works in Safari. Other apps need a separate setting.

### 2. `screen_time_fc_need_auth`

- **RU:** Screen Time: нет авторизации на этом устройстве **【—】** настройте на iPhone ребёнка.
- **EN:** Screen Time: not authorized on this device **【—】** set up on the child’s iPhone.

---

## Проверить · хаб / текст / история / база

**С «—»:** 7

### 1. `antifake_hub_title`

- **RU:** 
- **EN:** Antifake **【—】** Проверить подлинность

### 2. `antifake_hub_subtitle`

- **RU:** 
- **EN:** Проверка текста, голоса и видео **【—】** по кнопке. На вкладке «Звонок» **【—】** запись и метки на входящих.

### 3. `share_onboard_body`

- **RU:** 
- **EN:** В Safari или Telegram нажмите «Поделиться» и выберите ALADDIN **【—】** ссылка или фото попадут в проверку.

### 4. `antifake_premium_gate_no_demo`

- **RU:** 
- **EN:** Без Premium здесь нет фейковых примеров **【—】** только честное описание возможностей.

### 5. `antifake_translate_then_check_body`

- **RU:** 
- **EN:** Текст скопирован. Откройте системный Перевод (или Translate), вставьте сообщение, переведите на понятный язык, вернитесь сюда **【—】** Вставить и Проверить.

### 6. `antifake_family_cd_empty`

- **RU:** 
- **EN:** Нет данных **【—】** попросите участников синхронизировать базу в Hub.

### 7. `antifake_call_directory_status_disabled`

- **RU:** 
- **EN:** Расширение выключено **【—】** включите в настройках

---

## Итого

- Уникальных ключей: **33**
- Сумма «—» в RU+EN: **49**

## Варианты замены (обсуждение)

| Вариант | Пример |
|---------|--------|
| A. Точка / два предложения | `Разрешите геопозицию. Семья увидит аватар.` |
| B. Запятая | `Разрешите геопозицию, и семья увидит аватар.` |
| C. Двоеточие в заголовках | `Antifake: проверить подлинность` |
| D. Среднее тире `–` | визуально короче |
| E. Оставить «—» | ничего не менять |

Напишите: `все → B` или `только заголовки → C, остальное → A`.

---

## Приложение: полный список без фильтра чипов

Ключей с «—» во всех связанных файлах: **63**

1. `map_sheet_drag_hint`
   - RU: Тяните полоску вверх 【—】 список больше, карту меньше. Вниз 【—】 карта на весь экран.

2. `where_phone_setup_allow_body`
   - RU: Разрешите геопозицию 【—】 и семья увидит ваш аватар.

3. `where_phone_setup_denied_body`
   - RU: Включите её для ALADDIN в Настройках 【—】 это один переключатель.
   - EN: Turn it on for ALADDIN in Settings 【—】 it's one switch.

4. `where_phone_setup_precise_body`
   - RU: Включите точное место 【—】 аватар встанет туда, где вы.

5. `where_phone_setup_always_body`
   - RU: Разрешите «Всегда» 【—】 и место обновится, даже когда приложение закрыто.

6. `location_history_30d_subtitle`
   - RU: Полная история 【—】 в семейном тарифе

7. `family_cal_local_only`
   - RU: Пока видно на этом iPhone. Общий онлайн 【—】 позже.

8. `family_crash_tip_body`
   - RU: Нужны: геолокация «Всегда», «Движение и фитнес» и уведомления 【—】 иначе защита в фоне не сработает.
   - EN: Needs: Always location, Motion & Fitness, and notifications 【—】 or background protection won’t work.

9. `map_hub_safety_sos_note`
   - RU: Удержание SOS для семьи 【—】 на следующем шаге. Без «помощь уже едет».

10. `map_perm_precise_hint`
   - RU: В Настройках iPhone включите «Точные» для ALADDIN 【—】 точка будет точнее.

11. `map_bt_soon_body`
   - RU: Рядом / метки 【—】 в скором времени.
   - EN: Nearby / tags 【—】 coming soon.

12. `map_share_expired`
   - RU: Срок ссылки истёк 【—】 отправьте место снова
   - EN: Location link expired 【—】 send your place again

13. `trip_no_map_track`
   - RU: Маршрут на карте 【—】 после поездки с доступом к месту

14. `map_routes_on_family_map_hint`
   - RU: Маршрут на карте семьи. Навигатор 【—】 по кнопке рядом.
   - EN: Route on the family map. Navigator 【—】 tap the nearby button.

15. `family_invite_soft_body`
   - RU: Добавьте ещё одного человека в семью 【—】 увидите защиту и точку на карте.
   - EN: Add one more person 【—】 see protection and their place on the map.

16. `family_invite_ttl_hint`
   - RU: Коды приглашения действуют 3 дня. Если не успели 【—】 отправьте новый.

17. `premium_nudge_map_body`
   - RU: В Family 【—】 живая карта и больше мест для семьи.

18. `family_cal_who_hint`
   - RU: Пока на этом iPhone. Общий список 【—】 позже.

19. `family_cal_reminder_body`
   - RU: %@ · %@ 【—】 скоро
   - EN: %@ · %@ 【—】 soon

20. `map_anti_spy_note`
   - RU: Только последняя точка 【—】 по согласию семьи.
   - EN: Last known point 【—】 with family consent only.

21. `where_phone_map_empty`
   - RU: Точки ещё нет. Отправьте место один раз 【—】 появится на карте.
   - EN: No point yet. Send place once 【—】 it appears on the map.

22. `map_share_activity_hint`
   - RU: Семья увидит одну точку 【—】 только на выбранное время.
   - EN: Family sees one point 【—】 only for the time you choose.

23. `share_arrived_home_body`
   - RU: Можно коротко сказать в WhatsApp или чате 【—】 без лишних звонков.
   - EN: You can share a short note in WhatsApp or chat 【—】 no extra calls.

24. `map_routes_body`
   - RU: Сначала линия на карте семьи в ALADDIN. Здесь 【—】 Apple или Яндекс, если нужен навигатор. Точка 【—】 последняя известная.

25. `crash_detection_family_silence_hint`
   - RU: Если не ответите 【—】 напишем семье. «Всё в порядке» 【—】 отменяет.

26. `crash_confirm_offline`
   - RU: Нет сети 【—】 сохраним и отправим позже.
   - EN: You’re offline 【—】 we’ll save and send later.

27. `asc_tip_driving_reports_body`
   - RU: Пробег, макс. скорость и число поездок по каждому 【—】 после реальной поездки.
   - EN: Mileage, max speed, and trips for each family member 【—】 after a real drive.

28. `driving_reports_why_motion`
   - RU: 1. Разрешите «Движение и фитнес» для ALADDIN 【—】 так телефон понимает поездку.

29. `driving_reports_why_location`
   - RU: 2. Включите геолокацию «Всегда» (и точное место) 【—】 иначе поездки в фоне не пишутся.

30. `driving_reports_why_trip`
   - RU: 3. Проедьте за рулём с открытым или в фоне ALADDIN 【—】 затем откройте «Вождение» снова.

31. `drive_weekly_locked_title`
   - RU: Риски за рулём 【—】 по Family/Premium
   - EN: Driving risks 【—】 Family/Premium

32. `drive_weekly_locked_body`
   - RU: Счётчики скорости и резких манёвров открываются на семейном тарифе. Поездки и км без выдуманных цифр.
   - EN: Speed and harsh-maneuver counts unlock on a family plan. Trip and km stats stay honest 【—】 no invented numbers.

33. `drive_inc_explain_data_note`
   - RU: Пока нет поездок с датчиками 【—】 счётчики 0. На вкладке «Вождение» нажмите «Разрешить движение и фитнес», затем совершите поездку.
   - EN: No sensor trips yet 【—】 counters stay 0. On the Driving tab tap Allow Motion & Fitness, then take a drive.

34. `drive_pdf_disclaimer`
   - RU: Оценка для семьи, не страховой отчёт.
   - EN: Family estimate only 【—】 not an insurance report.

35. `driving_play_no_track`
   - RU: Маршрут появится после поездки с доступом к месту. Пока 【—】 время, км и скорость

36. `family.incomplete_server_roster_hint`
   - RU: По тарифу можно больше участников, а с сервера пришёл один 【—】 данные семьи неполные. Обратитесь в поддержку или дождитесь исправления на сервере.
   - EN: Your plan allows more members, but the server only returned one 【—】 family data looks incomplete. Contact support or wait for a server-side fix.

37. `family_roster_who_can_manage_body`
   - RU: 
   - EN: Добавлять и удалять участников могут только родители или участник с ролью «Люди 60+» в списке (не ребёнок и не подросток). До двух родительских аккаунтов 【—】 по правилам семьи.

38. `family_header_accessibility`
   - RU: 
   - EN: ALADDIN Family 【—】 защита семьи

39. `post_admin_add_device_offer_subtitle`
   - RU: 
   - EN: %@ добавлен в семью. Можно сразу зарегистрировать устройство 【—】 та же форма, что в разделе «Устройства».

40. `family_content_block_card_metric_hint`
   - RU: Детали 【—】 в Уведомлениях и Отчётах семьи

41. `family_modal_network_layers_scope`
   - RU: 
   - EN: Ниже 【—】 статус этого iPhone; карточки выше 【—】 данные ребёнка.

42. `location_events_empty_live`
   - RU: Пока нет событий за сегодня. Когда ребёнок дойдёт до школы или другого места 【—】 здесь появятся время и уведомление.

43. `family_location_signal_weak_hint`
   - RU: 
   - EN: Сигнал GPS слабый 【—】 попробуйте на улице

44. `geofences_empty_list_hint`
   - RU: Нет мест 【—】 добавьте Дом или Школу
   - EN: No places 【—】 add Home or School

45. `remote_lock_desc`
   - RU: 
   - EN: Отправим жёсткие ограничения на профиль ребёнка. Полная блокировка экрана 【—】 когда у ребёнка открыт ALADDIN.

46. `remote_lock_battery_unknown`
   - RU: 
   - EN: 【—】

47. `app_limits_shield_parent_honesty`
   - RU: Лимиты минут сохраняются у родителя. Блокировка приложений (Shield) включается на iPhone ребёнка после настройки Screen Time 【—】 не на телефоне родителя.
   - EN: Minute limits are saved on the parent phone. App blocking (Shield) applies on the child’s iPhone after Screen Time setup 【—】 not on the parent device.

48. `geofences_empty_body`
   - RU: Добавьте Дом или Школу 【—】 с реальным адресом.

49. `geofence_noshow_section_hint`
   - RU: Если к сроку человека нет на месте 【—】 придёт уведомление.

50. `geofence_noshow_roles_hint`
   - RU: Родитель видит места ребёнка (если настроено). Супруги не следят друг за другом 【—】 каждый настраивает свой телефон.
   - EN: A parent sees a child’s places when set up. Spouses do not track each other 【—】 each sets up their own phone.

51. `location_events_7d`
   - RU: События мест за 7 дней
   - EN: Place events 【—】 last 7 days

52. `bypass_empty_hint`
   - RU: 
   - EN: Если фильтры попробуют обойти 【—】 мы покажем это здесь.

53. `youtube_safe_mode_desc`
   - RU: 
   - EN: Безопасный режим YouTube 【—】 сохраняется в настройках семьи.

54. `child_overview_body`
   - RU: Пауза, сайты, лимит и сон 【—】 ниже. Полные отчёты 【—】 в родительском разделе.

55. `parental_filter_safari_honesty`
   - RU: Фильтр сайтов работает в Safari. В других приложениях 【—】 отдельно.

56. `screen_time_fc_need_auth`
   - RU: Screen Time: нет авторизации на этом устройстве 【—】 настройте на iPhone ребёнка.
   - EN: Screen Time: not authorized on this device 【—】 set up on the child’s iPhone.

57. `antifake_hub_title`
   - RU: 
   - EN: Antifake 【—】 Проверить подлинность

58. `antifake_hub_subtitle`
   - RU: 
   - EN: Проверка текста, голоса и видео 【—】 по кнопке. На вкладке «Звонок» 【—】 запись и метки на входящих.

59. `share_onboard_body`
   - RU: 
   - EN: В Safari или Telegram нажмите «Поделиться» и выберите ALADDIN 【—】 ссылка или фото попадут в проверку.

60. `antifake_premium_gate_no_demo`
   - RU: 
   - EN: Без Premium здесь нет фейковых примеров 【—】 только честное описание возможностей.

61. `antifake_translate_then_check_body`
   - RU: 
   - EN: Текст скопирован. Откройте системный Перевод (или Translate), вставьте сообщение, переведите на понятный язык, вернитесь сюда 【—】 Вставить и Проверить.

62. `antifake_family_cd_empty`
   - RU: 
   - EN: Нет данных 【—】 попросите участников синхронизировать базу в Hub.

63. `antifake_call_directory_status_disabled`
   - RU: 
   - EN: Расширение выключено 【—】 включите в настройках

