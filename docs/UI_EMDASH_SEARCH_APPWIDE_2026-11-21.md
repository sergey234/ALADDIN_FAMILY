# Вторая очередь: поиск длинного тире «—» по всему приложению

**Был поиск; вторая очередь `.strings` уже применена (см. статус ниже).**


> **Статус 2026-11-21:** вторая очередь `.strings` (~140 ключей) выполнена: `—` → `–` по одному ключу; fails=0; verify LocManager OK. Замена логов Swift — отдельно.

Символ: длинное `—` (U+2014). Среднее `–` уже из первой очереди сюда не входит.

Область: продукт iOS — `*.swift` (без backup/bot/vpn-api) + `Localizable.strings` + `LocalizationManager`.

## Сводка

- Ключей локализации с «—» (RU и/или EN): **561**
- Вхождений «—» в этих ключах (RU+EN sum): **731**
- Swift, похоже на UI-строки: **1363** строк
- Swift логи/служебное: **96** строк (в UI-замену не берём без отдельного GO)

### По доменам (локализация)

| Домен | Ключей |
|-------|--------|
| Прочее | 147 |
| Wellness / companion | 111 |
| Семья / roster | 78 |
| Ребёнок / parental | 68 |
| Проверить / antifake | 60 |
| Где семья / карта | 53 |
| Настройки / профиль | 20 |
| Тарифы / подписка | 17 |
| Общие / common | 4 |
| Онбординг | 2 |
| VPN / сеть | 1 |

## Карта по доменам

### Прочее (147)

1. `ai_assistant_slow_hint`
   - EN: AI обрабатывает запрос 【—】 это может занять до 30 секунд…

2. `ai_consent_banner_title`
   - EN: Умный помощник офлайн 【—】 включите в Настройках

3. `ai_trust_disclaimer`
   - RU: AI может ошибаться. Это подсказка. Если сомневаетесь 【—】 перепроверьте или спросите взрослого.
   - EN: AI can be wrong. It’s a suggestion. If unsure 【—】 double-check or ask an adult.

4. `analytics_protection_level_no_events`
   - EN: За период не было зафиксированных угроз 【—】 доля «заблокировано от обнаруженных» не считается, поэтому здесь 0%. Это не значит, что защита выключена.

5. `antivirus_file_hub_hint`
   - EN: Проверка файла 【—】 отдельно от проверки утечек пароля. Утечки 【—】 в Privacy Hub.

6. `antivirus_scan_legal_disclaimer`
   - RU: Проверяется только выбранный вами файл. Полный обход хранилища телефона недоступен. Локальные эвристики; облачная проверка 【—】 только для файлов до %d МБ и при доступном сервере.

7. `antivirus_toast_large_file_local_only`
   - RU: Файл больше %d МБ 【—】 на сервер он не отправлялся; показан результат локальных проверок.

8. `app_limits_shield_parent_honesty`
   - RU: Лимиты минут сохраняются у родителя. Блокировка приложений (Shield) включается на iPhone ребёнка после настройки Screen Time 【—】 не на телефоне родителя.
   - EN: Minute limits are saved on the parent phone. App blocking (Shield) applies on the child’s iPhone after Screen Time setup 【—】 not on the parent device.

9. `appstore_redeem_help_card_body`
   - RU: Если код выдали из App Store Connect 【—】 активируйте его в App Store, не здесь. Здесь 【—】 только бонусные коды команды ALADDIN.
   - EN: If the code came from App Store Connect, redeem it in the App Store 【—】 not here. This screen is only for ALADDIN team bonus codes.

10. `appstore_redeem_help_step7`
   - RU: 7. Если откроется камера 【—】 нажмите «Ввести код вручную».

11. `battery_critical_chat_message`
   - RU: 🔋 У %@ батарея %d%% 【—】 почти села.
   - EN: 🔋 %@ battery is %d%% 【—】 almost empty.

12. `call_plain_line_fake`
   - EN: Похоже на обман 【—】 не переводите деньги и не называйте код.

13. `call_plain_line_family`
   - EN: Если сомневаетесь 【—】 нажмите «Я в порядке» или позвоните детям.

14. `call_plain_line_uncertain`
   - EN: Пока неясно 【—】 лучше перезвонить родственникам и уточнить.

15. `calls_disclaimer_full`
   - RU: Запись 【—】 только с микрофона при громкой связи и с вашего согласия. Линию оператора приложение не слышит. Предупредите собеседника.

16. `calls_disclaimer_short`
   - RU: Мы записываем только звук с микрофона при громкой связи 【—】 не саму линию звонка.
   - EN: We only record from the microphone on speaker 【—】 not the carrier line.

17. `calls_incoming_cta`
   - RU: Идёт входящий 【—】 записать с динамика
   - EN: Incoming call 【—】 record via speaker

18. `calls_paywall_title`
   - RU: Звонки 【—】 для Family и Premium
   - EN: Calls 【—】 Family and Premium

19. `calls_prep_mic_hint`
   - RU: После старта включите громкую связь и позвоните. Если запись оборвётся 【—】 после звонка сохраните суть.

20. `calls_safety_prompt_toggle_a11y_hint`
   - RU: После звонка Phone или FaceTime. WhatsApp и Telegram iOS не видит 【—】 откройте раздел Звонки вручную.
   - EN: After Phone or FaceTime. iOS cannot see WhatsApp or Telegram 【—】 open Calls manually.

21. `component.password_security_agent.desc`
   - EN: Придумать пароль и проверить утечку 【—】 не сейф

22. `connect_device_body_a`
   - RU: Добавьте телефон близкого 【—】 увидите защиту и точку на карте.
   - EN: Add a family phone 【—】 see protection and their place on the map.

23. `dark_web_explanation_recommendation_1`
   - EN: Для пароля всегда используйте безопасную проверку 【—】 пароль никуда не уходит

24. `dark_web_explanation_recommendation_3`
   - EN: Не вводите паспорт и страховой номер 【—】 мы их не собираем для этой проверки

25. `dark_web_explanation_secure_content`
   - EN: Пароль на телефоне превращается в защищённый код. На сервер уходит только этот код 【—】 не сам пароль. Мы сверяем его с известными утечками. Так проверять безопаснее всего.

26. `dark_web_no_leaks_cta`
   - RU: Запустите проверку 【—】 добавьте email или телефон
   - EN: Run a scan 【—】 add email or phone

27. `dark_web_scan_data_email_fast_explanation`
   - EN: Уходит на сервер только для проверки. Поиск по почте 【—】 когда эта проверка включена.

28. `dark_web_scan_method_fast_subtitle`
   - EN: Поиск по почте 【—】 когда эта проверка будет включена

29. `dark_web_scan_method_secure_subtitle`
   - EN: Пароль сверяется с известными утечками 【—】 сам пароль никуда не уходит

30. `delete_account_confirm_hint`
   - EN: Введите %@ 【—】 тогда кнопка станет активной

31. `delete_account_confirm_ready`
   - EN: Подтверждение принято 【—】 можно удалить

32. `device_hub_coverage_hint`
   - EN: Выберите угрозу 【—】 откроем нужную проверку.

33. `device_hub_eicar_detected`
   - EN: EICAR обнаружен 【—】 карантин доступен.

34. `dojim_sub_before_3_body`
   - EN: Продлите защиту семьи в тарифах. Пригласите друга: ему −20% на первый месяц, вам 【—】 дни защиты.

35. `duration_unknown`
   - RU: 【—】
   - EN: 【—】

36. `elderly_blood_pressure_no_reading`
   - EN: Нет измерений 【—】 добавьте первое

37. `elderly_fall_detection_description`
   - EN: Опционально через HealthKit. Мы не передаём медицинские данные 【—】 только пуш близким.

38. `elderly_scam_call_directory_cta_hint`
   - RU: Фильтр вызовов в настройках iPhone 【—】 метки мошенников
   - EN: Call filtering in iPhone Settings 【—】 scam number labels

39. `elderly_scam_call_hint`
   - EN: Просили деньги или карту 【—】 нажмите. Напишем семье.

40. `elderly_scam_call_push_body`
   - RU: Всё спокойно? Откройте 【—】 одна кнопка, если просили деньги или карту.
   - EN: All calm? Open the app 【—】 one tap if they asked for money or a card.

41. `elderly_scam_call_step2`
   - EN: 2. Спокойно 【—】 жмите «Всё спокойно»

42. `elderly_scam_call_step3`
   - EN: 3. Просили деньги или карту 【—】 красная кнопка

43. `elderly_seed_activity_body_3`
   - RU: Ложитесь в привычное время. Экраны 【—】 потише за час до сна.

44. `elderly_seed_health_body_1`
   - RU: Принимайте лекарства как назначил врач. Если сомневаетесь 【—】 спросите у семьи или врача, не у незнакомца по телефону.
   - EN: Take medicine as your doctor prescribed. If unsure 【—】 ask family or a doctor, not a stranger on the phone.

45. `elderly_seed_health_body_3`
   - RU: Список вопросов врачу и список лекарств 【—】 на бумаге или в заметках.
   - EN: Bring a list of questions and medicines 【—】 on paper or in notes.

46. `elderly_seed_memory_body_3`
   - RU: Запишите, как вы себя чувствуете сегодня 【—】 одной фразой.
   - EN: Write how you feel today 【—】 in one sentence.

47. `elderly_seed_safety_body_2`
   - RU: Если звонят «из банка» или «от родственника» и торопят 【—】 положите трубку. Нажмите «Хотят перевод или код», чтобы семья узнала.
   - EN: If someone claims to be a bank or a relative and rushes you 【—】 hang up. Tap “They want a transfer or code” so family knows.

48. `faq_aes256_answer`
   - EN: AES-256 【—】 это самый сильный способ защиты информации, который используют:
• Банки
• Военные
• Правительства
• Спецслужбы

Это как сейф с миллионом замков 【—】 ключ практически невозможно подобрать!

✅ ALADDIN Premium применяет AES-256 для максимальной защиты.

49. `faq_anonymity_answer`
   - EN: Анонимность означает, что вас сложнее отследить в сети:
• IP-адрес может быть скрыт при защите сети
• Меньше данных о ваших действиях
• Местоположение остаётся приватнее
• Сложнее шпионить за вами

Это как маскировка 【—】 активность есть, но вас труднее узнать!

✅ ALADDIN Premium с защитой сети повышает приватность; абсолютная анонимность в интернете недостижима.

50. `faq_apple_website_golden`
   - EN: Что iPhone не разрешает 【—】 и как помогает сайт?

51. `faq_apple_website_golden_answer`
   - EN: Золотая середина ALADDIN: в приложении 【—】 защита и Antifake по вашему действию (активный App Trial, Family или Premium); на сайте aladdin-ai.ru 【—】 то, что на iPhone неудобно или запрещено Apple.

❌ Нельзя нигде (честно):
• Слушать все звонки в фоне
• Автоматически класть трубку по AI
• Перехватывать FaceTime, Zoom, WhatsApp
• Читать SMS и мессенджеры без вашего действия
• Скрытую запись чужого экрана
• Полный антивирус всего iPhone как на ПК

✅ В приложении: Antifake по кнопке «Проверить» (Trial / Family / Premium), ALADDIN X AI, защита сети, семья.

🌐 На сайте: **14 дней бесплатно** на этом устройстве или Family/Premium по коду 【—】 aladdin-ai.ru/antifake: текст, голос, видео до 25 МБ; отчёты; инструкции ALADDIN X AI и ботов.

Подробнее: Поддержка → «Antifake на сайте» или Antifake → ℹ️.

52. `faq_dark_web_leaks_answer`
   - EN: После взломов сайтов пароли и почта иногда попадают в списки известных утечек.

Что может утечь:
• Пароли
• Адреса почты
• Номера телефонов

✅ ALADDIN помогает проверить, не попал ли ваш пароль в известные утечки. Сам пароль с телефона не уходит 【—】 сверяется только защищённый код.

53. `faq_data_safe_answer`
   - EN: Да, ваши данные надёжно защищены! 🔒

Мы используем:
• Военное шифрование (как в банках и армии)
• Обработку в соответствии с законами РФ
• Соблюдаем требования о защите данных
• В Premium 【—】 расширенные настройки приватности профиля

54. `faq_emergency_sos_answer`
   - EN: SOS для людей 60+ 【—】 это красная кнопка в простом интерфейсе.

Что происходит:
• Вы нажимаете SOS
• Близкие и экстренные контакты получают сигнал
• Можно быстро попросить о помощи

⚠️ Это не медицинская служба и не замена 112!

✅ ALADDIN помогает семье узнать, что вам нужна помощь.

55. `faq_geofencing_answer`
   - EN: Геозоны 【—】 это безопасные места на карте для членов семьи.

Как это работает:
1. Родитель создаёт зону (дом, школа, секция)
2. Указывает адрес и радиус
3. Получает уведомление, когда ребёнок входит или выходит из зоны

Это как виртуальный забор вокруг важных мест!

✅ ALADDIN помогает знать, что близкие в безопасной зоне 【—】 с вашего согласия.

56. `faq_protect_elderly_answer`
   - EN: Для бабушек и дедушек мы сделали специальную защиту:

• Предупреждаем о звонках от мошенников (они часто звонят людям 60+)
• Проверяем все сайты перед открытием
• Делаем простой интерфейс 【—】 всё понятно, даже если вы не дружите с телефоном
• Красная кнопка SOS 【—】 быстро вызвать помощь

57. `faq_roadside_assistance_answer`
   - EN: Помощь на дороге 【—】 это запрос о поломке из раздела «Защита сети».

Как это работает:
1. Вы описываете проблему (колесо, аккумулятор, ДТП)
2. С вашего согласия передаётся местоположение
3. Сигнал уходит близким и экстренным контактам семьи

Это как кнопка «мне нужна помощь на трассе» в кармане!

✅ ALADDIN отправляет запрос только когда вы сами нажимаете кнопку.

58. `faq_tg_support_ai_answer`
   - EN: В Telegram-боте @AladdinchatAI_bot можно спросить ИИ-помощника поддержки ALADDIN. Он отвечает по FAQ и гайдам приложения: антифейк, дети, тариф, семья, защита сети.

Важно:
• Это не Companion. Помощник отвечает только про приложение ALADDIN.
• В Telegram нет E2EE семейного чата ALADDIN 【—】 не вводите пароли, SMS-коды и данные карт.
• Факты тарифа/семьи берутся из вашей привязанной учётки; спорные случаи 【—】 живому оператору.
• Сначала «Подключить Telegram» (код /link), затем «Спросить помощника» или /help_ai в боте.

59. `faq_what_protects_answer`
   - EN: ALADDIN помогает защититься от основных опасностей в интернете. Набор функций зависит от вашего тарифа. Это как охранник для телефона 【—】 предупреждает о вирусах, мошенниках и опасных сайтах.

Система работает 24/7 и отслеживает активность на устройстве.

60. `games_pet_description`
   - EN: Тамагочи-питомец с индикаторами ❤️🍎⭐😊. Ребёнок кормит, играет, гладит. 4 стадии эволюции. Нельзя отключить 【—】 это основа мотивации!

61. `items_promo_body`
   - RU: Когда подключим метки 【—】 увидите ключи и сумку здесь. Сейчас раздел пустой специально.

62. `lists_empty_body`
   - RU: Свои и спам-номера появятся после синхронизации. Сейчас список пуст 【—】 без заглушек.
   - EN: Your own and spam numbers appear after sync. Empty for now 【—】 no fake rows.

63. `location_events_7d`
   - EN: Place events 【—】 last 7 days

64. `location_events_empty_live`
   - RU: Пока нет событий за сегодня. Когда ребёнок дойдёт до школы или другого места 【—】 здесь появятся время и уведомление.

65. `location_history_30d_subtitle`
   - RU: Полная история 【—】 в семейном тарифе

66. `main_exec_plan_inline_strike_hint`
   - EN: Нажмите круг слева, чтобы локально отметить сделанное (зачёркивание). Каноника 【—】 чекбоксы в дашборде и повторный запуск скрипта.

67. `need_help_confirm_body`
   - RU: Семья получит срочное сообщение. Если геолокация разрешена 【—】 один раз отправим примерное место (не трек).
   - EN: Семья получит срочное сообщение. Если геолокация разрешена 【—】 один раз отправим примерное место (не трек).

68. `need_help_push_body`
   - RU: %@: нужна помощь 【—】 срочно
   - EN: %@: need help 【—】 urgent

69. `need_help_sent_local`
   - RU: Сохранили на телефоне. Как только связь появится 【—】 отправим семье.
   - EN: Сохранили на телефоне. Как только связь появится 【—】 отправим семье.

70. `notif_s33_body`
   - RU: Пришёл или ушёл из места 【—】 пуш откроет карту.
   - EN: Arrived or left a place 【—】 opens the map.

71. `notif_s34_body`
   - RU: Когда заряд почти сел 【—】 пуш откроет карту.

72. `notif_s36_body`
   - RU: SOS и «нужна помощь» 【—】 сразу на карту.

73. `notif_s39_body`
   - RU: Не копируем Life360. Свой сценарий 【—】 позже.

74. `parent_dashboard_mnemo_mq_disclaimer`
   - EN: MQ 【—】 игровой ориентир, не IQ-тест

75. `parent_dashboard_mnemo_mq_subtitle`
   - EN: Квартальные тесты 【—】 только баллы, без слов и ответов

76. `parent_dashboard_mnemo_technique_subtitle`
   - EN: 10 техник · 4 ступени 【—】 без слов уроков и ответов

77. `parent_dashboard_s09_hint`
   - RU: Панель родителя 【—】 тот же тёмный стиль ALADDIN, без белых полей.
   - EN: Parent panel uses the same ALADDIN dark style 【—】 no white fields.

78. `parent_dashboard_trends_empty`
   - RU: Пока нет данных за выбранный период 【—】 откройте контент с устройства ребёнка, чтобы увидеть график.
   - EN: No data for this period yet 【—】 open content on the child device to populate the chart.

79. `parent_mnemo_guide_intro_4d_body`
   - EN: Двойной код (слово + образ), активное вспоминание, интервалы 1-3-7-14-30 и радость от игры 【—】 четыре опоры каждого урока.

80. `parent_mnemo_guide_intro_4d_title`
   - EN: 4D 【—】 как мозг закрепляет знания

81. `parent_mnemo_guide_intro_aim_association`
   - EN: Ассоциация 【—】 связываем новое с уже знакомым.

82. `parent_mnemo_guide_intro_aim_imagination`
   - EN: Воображение 【—】 яркий образ запоминается дольше слов.

83. `parent_mnemo_guide_intro_aim_location`
   - EN: Место 【—】 «комнаты» и остановки помогают держать порядок.

84. `parent_mnemo_guide_intro_aim_title`
   - EN: AIM 【—】 три опоры памяти

85. `parent_mnemo_guide_intro_lead`
   - EN: Ребёнок учится вспоминать через образы, якоря и интервальное повторение 【—】 не через зубрёжку.

86. `parent_mnemo_guide_mq_lead`
   - EN: MQ 0–100 показывает, как ребёнок вспоминает слова в коротком тесте 【—】 без оценок в школе.

87. `parent_mnemo_guide_mq_quarterly`
   - EN: Повторный тест 【—】 раз в квартал. Сравнивайте тренд, а не отдельный день.

88. `parent_mnemo_guide_mq_scale`
   - EN: 70+ 【—】 уверенное вспоминание; рост по кварталам важнее одной цифры.

89. `parent_mnemo_guide_srs_lead`
   - EN: Бейдж «Сегодня повторить: N» 【—】 это план, а не экзамен.

90. `parent_mnemo_guide_srs_tip_praise`
   - EN: Хвалите за попытку вспомнить 【—】 не только за идеальный ответ.

91. `parent_mnemo_guide_technique_acronym`
   - EN: Мнемофраза: проверьте 【—】 может ли ребёнок воспроизвести список по первым буквам?

92. `parent_mnemo_guide_technique_memoryPalace`
   - EN: Дворец памяти: попросите мысленно пройти по комнатам 【—】 без спешки и без подсказки ответа.

93. `parent_mnemo_guide_technique_rhymePeg`
   - EN: Рифма-якорь: если ребёнок любит песни 【—】 спросите, какой образ пришёл к рифме.

94. `parent_mnemo_guide_technique_rhythmCode`
   - EN: Ритм-код: похлопайте ритм вместе 【—】 тело помнит быстрее, чем кажется.

95. `parent_mnemo_guide_technique_spacedReview`
   - EN: Повтор 1-3-7-14: напоминание «сегодня N карточек» 【—】 норма, не повод для стресса.

96. `parent_mnemo_guide_technique_storyLink`
   - EN: Сюжет-связка: связывайте факты в мини-сюжет за ужином 【—】 5 минут без экрана.

97. `pet_routines_hero`
   - RU: Забота о питомце 【—】 дело всей семьи

98. `plan_275_sheet_done_title`
   - EN: Готово (DONE) 【—】 275

99. `plan_275_strike_hint`
   - EN: Круг слева 【—】 только локальная отметка «просмотрено»; каноника статуса в git-матрице.

100. `positioning_system_ios_note`
   - RU: На iPhone Apple всегда использует доступные спутники вместе (GPS + ГЛОНАСС + Galileo и др.). Выбор здесь 【—】 предпочтение для подсказок, а не принудительное отключение систем.
   - EN: On iPhone, Apple always uses available satellites together (GPS + GLONASS + Galileo, etc.). This choice is a preference for tips 【—】 it cannot force one system alone.

101. `protection_catalog_title`
   - EN: 🤖 AI защита 【—】 набор угроз по тарифу

102. `protection_feedback_messages_subtitle`
   - RU: Сохраняем настройку в семье. Push от iOS 【—】 только если разрешены уведомления.

103. `protection_feedback_safari_app_on_status`
   - RU: В приложении включено 【—】 осталось Safari
   - EN: On in the app 【—】 enable in Safari next

104. `psych_library_cbt_title`
   - EN: КПТ 【—】 разобрать мысль

105. `psych_library_disclaimer`
   - EN: Самопомощь и упражнения 【—】 не замена врача или психолога.

106. `psych_library_dream_subtitle`
   - EN: Запиши сон 【—】 без толкований

107. `psych_library_gestalt_title`
   - EN: Гештальт 【—】 здесь и сейчас

108. `psych_library_humanistic_title`
   - EN: Роджерс 【—】 поддержка

109. `psych_library_jung_title`
   - EN: Юнг 【—】 образы

110. `psych_library_pavlov_title`
   - EN: Если 【—】 то

111. `referral_a_faq_a3`
   - EN: Нет. Только дни защиты и скидка 【—】 без вывода и без сетевого заработка.

112. `referral_a_ledger_empty`
   - EN: Пока нет начислений 【—】 пригласите семью

113. `referral_soft_stats_unavailable`
   - RU: Пока не удалось загрузить награды. Приглашать можно 【—】 цифры появятся чуть позже.
   - EN: Couldn’t load rewards yet. You can still invite 【—】 numbers will show up shortly.

114. `referral_step3_desc`
   - EN: После оплаты друга или 14 дней активной защиты: другу −20% на первый месяц, вам 【—】 дни семейной защиты по уровню.

115. `referral_text_template`
   - EN: 🎁 Присоединяйся к семейной защите ALADDIN! Друг получит −20% на первый месяц, вам 【—】 дни защиты. Без вывода денег.

Используй мой код: {CODE}

Скачай: https://aladdin-ai.ru/invite/{CODE}

С тобой на защите! 🛡️

116. `sos_alarm_choose_hint`
   - EN: Сначала можно сообщить семье крупным сигналом. Службы 【—】 ниже.

117. `sos_edu_mid_1_body`
   - RU: Короткого нажатия мало 【—】 так мы снижаем случайные сигналы. Отпустить можно в любой момент до отправки.
   - EN: A quick tap is not enough 【—】 that cuts accidental alerts. You can release anytime before it sends.

118. `sos_edu_mid_3_body`
   - EN: After you hold, the alert goes out quietly 【—】 you do not have to speak if it is unsafe nearby.

119. `sos_edu_mid_4_body`
   - RU: Отпустите до конца отсчёта 【—】 отправка отменится. Если сигнал уже ушёл, сразу напишите семье, что всё в порядке.

120. `system_filter_toggle_on_hint`
   - RU: Включено. Если iPhone спросил разрешение 【—】 нажмите «Разрешить».

121. `terms_section_liability_content_6`
   - RU: Запись звонков 【—】 только по вашей инициативе; вы отвечаете за согласие собеседника и законность
   - EN: Запись звонков 【—】 только по вашей инициативе; вы отвечаете за согласие собеседника и законность

122. `terms_section_liability_content_9`
   - RU: Раздел «Звонки» 【—】 вспомогательный инструмент, не юридическая или банковская консультация и не услуга оператора связи
   - EN: Раздел «Звонки» 【—】 вспомогательный инструмент, не юридическая или банковская консультация и не услуга оператора связи

123. `tg_link_expired`
   - EN: Код истёк 【—】 получите новый

124. `tg_link_mem_warning`
   - EN: Важно: код привязки 【—】 6 символов. Это не ID участника семьи (MEM_*). MEM_* для /link не подходит.

125. `threat_eicar_action`
   - RU: Можно оставить в карантине или удалить. Для обычных угроз 【—】 не открывайте файл.
   - EN: Keep in quarantine or delete. For real threats 【—】 do not open the file.

126. `threat_unknown_action`
   - RU: Оставьте в карантине или удалите. Если не уверены 【—】 спросите взрослого.
   - EN: Keep in quarantine or delete. If unsure 【—】 ask an adult.

127. `trust_teen_memo_body`
   - RU: Вы договорились в семье: родители видят место и «пришёл / ушёл», если геолокация разрешена. В тихой зоне точку не показывают. Полностью отключить 【—】 в Настройках iPhone → ALADDIN.

128. `vk_connect_body`
   - RU: Подключение VK 【—】 позже.
   - EN: VK connect 【—】 later.

129. `voice_day_recap_raw_fallback`
   - EN: Не удалось разобрать JSON 【—】 сырой ответ:

130. `voice_notes_local_only_disclaimer`
   - EN: Записи остаются на этом iPhone. Распознавание речи 【—】 средствами Apple на устройстве.

131. `voice_structure_raw_fallback`
   - EN: Не удалось разобрать JSON 【—】 сырой ответ:

132. `wind_down_push_body_15`
   - EN: 15 минут до сна 【—】 отложи экран 😴

133. `wind_down_push_body_30`
   - EN: Через 30 минут сон 【—】 начни спокойный ритуал 🌙

134. `wind_down_push_body_5`
   - EN: 5 минут 【—】 открой сказку для сна ✨

135. `young_defender_lesson_10_content_1`
   - EN: Утечка 【—】 когда чужие получили доступ к паролям или почте из старых взломов сайтов

136. `young_defender_lesson_10_content_3`
   - EN: Проверь пароль в ALADDIN: «проверка утечек» 【—】 и смени, если нашлось

137. `young_defender_lesson_10_content_4`
   - EN: Не плати «страховку личности» по холодным звонкам 【—】 это часто обман

138. `young_defender_lesson_10_desc`
   - EN: Что делать при большой утечке 【—】 без паники

139. `young_defender_lesson_10_quiz_2_a2`
   - EN: Нет 【—】 часто это обман

140. `young_defender_lesson_7_content_1`
   - EN: ИИ умеет менять лицо на фото и в видео 【—】 это называется deepfake

141. `young_defender_lesson_7_content_5`
   - EN: Если сомневаешься 【—】 покажи сообщение родителям в ALADDIN, не пересылай дальше

142. `young_defender_lesson_7_desc`
   - EN: Почему фото и видео лица 【—】 не доказательство

143. `young_defender_lesson_7_quiz_3_a2`
   - EN: Лицо легко изменить 【—】 нельзя верить только картинке

144. `young_defender_lesson_8_content_2`
   - EN: Это не значит, что ALADDIN «удалит вас из интернета» сам 【—】 нужны ваши шаги

145. `young_defender_lesson_8_content_5`
   - EN: Если нашли себя 【—】 сохраните ссылку и покажите родителям в ALADDIN

146. `young_defender_lesson_8_quiz_2_a2`
   - EN: Нет 【—】 нужны ваши шаги и помощь взрослых

147. `young_defender_lesson_9_content_3`
   - EN: Если бот просит фото или встречу 【—】 остановись и скажи взрослым

### Wellness / companion (111)

1. `companion_break_steps_water_blocked`
   - EN: Для привычки «вода» шаги без награды Единорога 【—】 отметьте Done в напоминании.

2. `companion_dialogue_empty`
   - EN: Скажи или напиши 【—】 я рядом.

3. `companion_error_load_timeout`
   - RU: Долго нет ответа 【—】 попробуем ещё раз
   - EN: Taking too long 【—】 trying again

4. `companion_error_usage_limit`
   - EN: Лимит сообщений на сегодня исчерпан. Завтра можно снова 【—】 или попроси родителя о Premium.

5. `companion_friends_hint`
   - EN: Поговорить с героями 【—】 Единорог, Аладдин и Джин

6. `companion_heroes_one_pager_aladdin`
   - EN: Аладдин 【—】 спокойный наставник: мудрость простыми словами, иногда сухой wit. Без религии в ответах.

7. `companion_heroes_one_pager_genie`
   - EN: Джин 【—】 больше юмора и игры слов, но не в каждом сообщении. При грусти 【—】 только поддержка.

8. `companion_heroes_one_pager_intro`
   - EN: Три AI-друга для разных настроений. Все ответы 【—】 ИИ, не живой человек. При тревоге 【—】 обратись к взрослому или на линию 112.

9. `companion_heroes_one_pager_unicorn`
   - EN: Единорог 【—】 тёплый друг для детей: сказка, школа, друзья, эмоции. Без сарказма.

10. `companion_humor_hint_genie`
   - EN: Джин 【—】 больше шуток и игры слов, но не в каждом ответе.

11. `companion_humor_hint_unicorn`
   - EN: Тёплые шутки иногда 【—】 в безопасном PG-стиле.

12. `companion_legal_offline_coppa_body`
   - EN: Обработка данных детей 【—】 с согласия законного представителя (152-ФЗ). Мы не используем данные ребёнка для рекламы. Память компаньона 【—】 опциональна, экспорт и удаление доступны в настройках.

13. `companion_legal_offline_voice_brief_body`
   - EN: • Основной путь: Apple (Siri cloud) на телефоне.
• Запасной путь: ALADDIN VPS 【—】 только если Apple не справилась.
• Аудио на сервере ALADDIN не копится «навсегда» 【—】 обработали и удалили.
• Текст диалога 【—】 по общим правилам компаньона (память, лимиты тарифа).

14. `companion_legal_offline_voice_fallback_body`
   - EN: Если на устройстве текст получить не удалось, приложение может один раз отправить короткую запись голоса (до 15 секунд) на сервер ALADDIN для преобразования в текст. Запись обрабатывается в памяти и не сохраняется после ответа (0 секунд хранения аудио). На сервер уходит только текст результата 【—】 как если бы вы напечатали сообщение. Запасной путь работает только при включённом «Облачном AI-помощнике» в настройках.

15. `companion_legal_offline_wellness_body`
   - EN: Раздел настроения 【—】 для самопомощи. Он не заменяет врача и экстренную помощь.

16. `companion_mic_coach_step3`
   - EN: 3. Отпусти 【—】 герой ответит

17. `companion_mine_cogs_alert`
   - EN: Порог $%.2f 【—】 проверьте использование

18. `companion_offline_cached_hint`
   - EN: Показана сохранённая история 【—】 без интернета.

19. `companion_social_bridge_body`
   - EN: Если хочешь 【—】 напиши маме, папе или другу. Герой всегда рядом, но живое общение тоже важно.

20. `companion_teen_humor_subtitle`
   - EN: Можно попросить героя шутить реже 【—】 поддержка и эмпатия останутся.

21. `faq_wellness_support_answer`
   - RU: Раздел «Настроение и поддержка» 【—】 это самопомощь: отметка настроения, упражнения и диалог с цифровым другом (ИИ).

⚠️ Это НЕ медицинская услуга, НЕ психотерапия и НЕ чат с живым врачом или психологом.

При признаках кризиса приложение подсказывает обратиться к взрослому, которому доверяете, или на линию 112 / 8-800-2000-122.

✅ ALADDIN помогает заметить настроение и сделать маленький шаг 【—】 без диагнозов и назначений.
   - EN: Mood and support is self-help: a mood check, exercises, and a chat with a digital friend (AI).

⚠️ This is NOT medical care, NOT therapy, and NOT a live chat with a doctor or counselor.

If there are signs of a crisis, the app suggests a trusted adult or public helplines (112 / 8-800-2000-122 in Russia).

✅ ALADDIN helps you notice your mood and take a small step 【—】 without diagnoses or prescriptions.

22. `wellness_age_band_mismatch_banner`
   - EN: Показаны дорожки для взрослых. Если это ошибка 【—】 выйдите и войдите снова.

23. `wellness_assessment_crisis_hint`
   - EN: Если тебе сейчас очень тяжело 【—】 позови взрослого или набери 112.

24. `wellness_assessment_crisis_hint_child`
   - EN: Если очень тяжело 【—】 позови взрослого или набери 112.

25. `wellness_assessment_crisis_hint_teen`
   - EN: Если тебе сейчас очень тяжело 【—】 позови взрослого или набери 112.

26. `wellness_assessment_gad7_subtitle`
   - EN: 7 вопросов 【—】 уровень тревоги

27. `wellness_assessment_mbi_subtitle`
   - EN: 5 вопросов 【—】 для взрослых, не диагноз

28. `wellness_assessment_phq9_subtitle`
   - EN: 9 вопросов 【—】 полный скрининг

29. `wellness_assessment_phq_lite_subtitle`
   - EN: 5 вопросов 【—】 быстрая проверка настроения

30. `wellness_assessment_result_mild`
   - EN: Лёгкие признаки 【—】 можно продолжить самопомощь

31. `wellness_breath_2min_done`
   - EN: Готово 【—】 можете вернуться.

32. `wellness_breath_2min_subtitle`
   - EN: Спокойный вдох и выдох 【—】 без медсоветов.

33. `wellness_checkin_subtitle_child`
   - EN: Быстро 【—】 нажми на смайлик

34. `wellness_checkin_subtitle_teen`
   - EN: Несколько секунд 【—】 без оценок

35. `wellness_companion_mode_banner`
   - EN: Режим: %@ 【—】 зажми микрофон и говори

36. `wellness_consent_body`
   - EN: ALADDIN 【—】 цифровой друг для самопомощи. Это не медицинский сервис и не заменяет психолога или врача. Опросники 【—】 скрининг, не диагноз.

37. `wellness_consent_body_child`
   - EN: ALADDIN 【—】 друг для самопомощи. Это не врач. Взрослый рядом 【—】 если тяжело.

38. `wellness_consent_body_teen`
   - EN: ALADDIN 【—】 цифровой друг для самопомощи. Не врач и не психолог. Опросы 【—】 не диагноз.

39. `wellness_consent_jung_note`
   - EN: «Понять себя» и сны 【—】 метафоры для размышления, не предсказания.

40. `wellness_consent_jung_note_child`
   - EN: Сны 【—】 просто картинки для размышления, не предсказания.

41. `wellness_consent_jung_note_teen`
   - EN: «Понять себя» и сны 【—】 метафоры, не предсказания.

42. `wellness_deep_explore_subtitle`
   - RU: Выберите, как герой ответит. Разговор тот же 【—】 меняется только стиль.
   - EN: Choose how the hero replies. Same chat 【—】 different style.

43. `wellness_detox_finished`
   - EN: Челлендж завершён 【—】 молодец!

44. `wellness_detox_subtitle`
   - EN: Отмечай дни, когда уложился в лимит 【—】 родители видят только счётчик.

45. `wellness_detox_weekly_progress`
   - EN: На этой неделе 【—】 продолжай отмечать дни под лимитом.

46. `wellness_dream_blocked_child`
   - EN: Дневник снов 【—】 с 13 лет

47. `wellness_dream_coachmark_body`
   - EN: Опишите сон своими словами 【—】 записи сохраняются ниже. Это не диагноз, а заметки для размышления.

48. `wellness_dream_disclaimer`
   - EN: Личный дневник снов 【—】 чтобы заметить образы и поразмышлять. Это не гадание и не медицинский совет.

49. `wellness_dream_disclaimer_sheet_2`
   - EN: Образы и символы 【—】 метафоры для размышления, не «приговор» и не диагноз.

50. `wellness_dream_disclaimer_sheet_3`
   - EN: Если тревожно или страшно 【—】 поговори со взрослым, которому доверяешь.

51. `wellness_dream_reflect_hint`
   - EN: Символы 【—】 только как метафоры, не «приговор»

52. `wellness_error_crisis_cooldown`
   - EN: Сначала важна поддержка живого человека 【—】 попробуйте позже

53. `wellness_error_generic`
   - EN: Не получилось 【—】 попробуй ещё раз

54. `wellness_error_offline_pillars`
   - EN: Нет сети 【—】 показаны дорожки для вашего возраста

55. `wellness_exam_one_thing_cta`
   - EN: Одно дело 【—】 5 мин

56. `wellness_exam_phase_day_before`
   - EN: Завтра важный день 【—】 отдохни сегодня

57. `wellness_exam_phase_final_5min`
   - EN: 5 минут до старта 【—】 дыши спокойно

58. `wellness_exam_started`
   - EN: Экзамен уже начался 【—】 ты справишься!

59. `wellness_guide_disclaimer`
   - EN: This is self-help and self-exploration 【—】 not a replacement for a psychologist or doctor.

60. `wellness_hero_intro_behavioral_child`
   - EN: Один маленький шаг сегодня 【—】 ты справишься!

61. `wellness_hero_intro_behavioral_senior`
   - EN: Небольшой шаг 【—】 в своём темпе.

62. `wellness_hero_intro_behavioral_teen`
   - EN: Один шаг сегодня 【—】 без больших планов.

63. `wellness_hero_intro_cognitive_child`
   - EN: Давай подумаем вместе 【—】 одной простой фразой.

64. `wellness_hero_intro_cognitive_parent`
   - EN: Одна мысль 【—】 разберём по шагам.

65. `wellness_hero_intro_cognitive_teen`
   - EN: Давай разложим мысль на части 【—】 как пазл.

66. `wellness_hero_intro_humanistic_parent`
   - EN: Минута тишины 【—】 выдохнуть можно.

67. `wellness_hero_intro_humanistic_senior`
   - EN: Никуда не спешим 【—】 я рядом.

68. `wellness_hero_intro_humanistic_teen`
   - EN: Я рядом 【—】 без советов, если не просишь.

69. `wellness_hero_intro_jung_child`
   - EN: Расскажи образ или сон 【—】 посмотрим, что он для тебя значит.

70. `wellness_hero_intro_jung_parent`
   - EN: Образы и сны 【—】 подсказки, не приговор.

71. `wellness_hero_intro_jung_senior`
   - EN: Образ или воспоминание 【—】 обсудим мягко.

72. `wellness_hero_intro_jung_teen`
   - EN: Сон или образ 【—】 что это может значить для тебя.

73. `wellness_hub_non_medical_banner`
   - EN: Это не медицина и не диагноз 【—】 только поддержка для самопомощи. В острой ситуации обратитесь за срочной помощью.

74. `wellness_if_then_title`
   - EN: Если 【—】 то

75. `wellness_mode_one_question_hint`
   - RU: Задам один важный вопрос 【—】 без лишнего
   - EN: One clear question 【—】 nothing extra

76. `wellness_nudge_idle_body`
   - EN: Давно не заходил(а) 【—】 всё ок? Хватит одной минуты check-in.

77. `wellness_one_thing_done`
   - EN: Готово! Маленький шаг 【—】 это победа.

78. `wellness_one_thing_hub_cta`
   - EN: 5 мин 【—】 одно дело

79. `wellness_one_thing_intro`
   - EN: Выбери одно маленькое дело на 5 минут 【—】 без отвлечений.

80. `wellness_outcome_pillar_switch`
   - EN: Попробуем дорожку «%@» 【—】 так иногда легче.

81. `wellness_outcome_subtitle`
   - EN: Один тап 【—】 это помогает подобрать поддержку

82. `wellness_outcome_subtitle_child`
   - EN: Нажми 【—】 так мы поймём, что помогает

83. `wellness_outcome_subtitle_teen`
   - EN: Один тап 【—】 подстроим поддержку

84. `wellness_outcome_thanks`
   - EN: Thanks 【—】 we’ll take that into account

85. `wellness_parent_playbook_subtitle`
   - EN: Готовые мягкие фразы 【—】 мы не читаем чат ребёнка, только подсказываем, как начать разговор

86. `wellness_pdf_title`
   - EN: Мой прогресс 【—】 ALADDIN

87. `wellness_pillar_cognitive_subtitle_b`
   - EN: Один шаг 【—】 отделить факт от тревоги

88. `wellness_pillar_humanistic_subtitle_b`
   - EN: Без советов 【—】 просто поддержка

89. `wellness_pillar_humanistic_subtitle_child`
   - EN: Просто побуть 【—】 без советов

90. `wellness_pillar_jung_subtitle`
   - EN: Сны и символы 【—】 без ярлыков

91. `wellness_pillar_jung_subtitle_teen`
   - EN: Сны и образы 【—】 без ярлыков

92. `wellness_reflective_info_body`
   - RU: Выберите, как герой ответит. Разговор тот же 【—】 меняется только стиль.
   - EN: Choose how the hero replies. Same chat 【—】 different style.

93. `wellness_reflective_subtitle`
   - EN: Выбери формат 【—】 откроется чат с другом

94. `wellness_senior_voice_intro`
   - EN: Нажмите и говорите 【—】 я рядом, без спешки.

95. `wellness_session_close_cta_if_then`
   - EN: В «Если 【—】 то»

96. `wellness_session_close_xp_note`
   - EN: Очки единорога 【—】 только за сделанный шаг, дыхание или check-in, не за сам разговор.

97. `wellness_session_soft_nudge_body`
   - EN: Можно подвести итог 【—】 или продолжить разговор.

98. `wellness_sleep_stories_offline_hint`
   - EN: Сказки на устройстве 【—】 без интернета.

99. `wellness_social_goal_call_grandparent`
   - EN: Позвони бабушке или дедушке 【—】 им будет приятно услышать тебя.

100. `wellness_social_goal_call_grandparent_step3`
   - EN: Можно просто помолчать вместе 【—】 это тоже ок

101. `wellness_social_goal_walk_friend`
   - EN: Погуляй или созвонись с другом 【—】 даже 10 минут помогают.

102. `wellness_talk_now_subtitle`
   - EN: Последний герой 【—】 1 тап

103. `wellness_teen_phq_parent_aggregate_hint`
   - EN: Родитель видит только сводку настроения, если включён переключатель выше 【—】 не переписку.

104. `wellness_timeline_empty`
   - EN: Пока нет записей 【—】 начни с отметки настроения

105. `wellness_together_offline_local`
   - EN: Без сети 【—】 локальный таймер дыхания 3 мин.

106. `wellness_trauma_specialist_note`
   - EN: Психолог или психотерапевт 【—】 очно или онлайн.

107. `wellness_trust_escalation_l0`
   - EN: Самопомощь 【—】 упражнения и чат

108. `wellness_trust_escalation_l1`
   - EN: Наблюдение 【—】 опросники и прогресс

109. `wellness_trust_escalation_l3`
   - EN: Кризис 【—】 112 и взрослый

110. `wellness_values_card_subtitle`
   - EN: Выберите 1–2 ценности 【—】 без оценок

111. `wellness_weekly_meaning_body`
   - EN: Раз в неделю 【—】 время для смысла

### Семья / roster (78)

1. `add_member_to_current_family_desc`
   - EN: Выберите роль и имя 【—】 участник появится в вашей семье без создания новой

2. `antifake_family_faq_3`
   - EN: В интерфейсе 60+ 【—】 одна кнопка «Проверить звонок» открывает Hub → Звонок.

3. `antifake_share_family_no_family`
   - EN: Семья не найдена 【—】 текст всё равно можно отправить через Share.

4. `child_mnemo_family_challenge_share_body`
   - EN: Семейный челлендж Академии памяти 🧠
Запомни слова: %@
Без имён и адресов 【—】 только тренировка!

5. `child_mnemo_family_challenge_subtitle`
   - EN: 5 слов без личных данных 【—】 поделись с семьёй

6. `family.incomplete_server_roster_hint`
   - RU: По тарифу можно больше участников, а с сервера пришёл один 【—】 данные семьи неполные. Обратитесь в поддержку или дождитесь исправления на сервере.
   - EN: Your plan allows more members, but the server only returned one 【—】 family data looks incomplete. Contact support or wait for a server-side fix.

7. `family_cal_local_only`
   - RU: Пока видно на этом iPhone. Общий онлайн 【—】 позже.

8. `family_cal_reminder_body`
   - RU: %@ · %@ 【—】 скоро
   - EN: %@ · %@ 【—】 soon

9. `family_cal_who_hint`
   - RU: Пока на этом iPhone. Общий список 【—】 позже.

10. `family_challenge_rewarded`
   - EN: Сделано 【—】 единорог получил заботу ✨

11. `family_challenge_section_hint`
   - EN: Семья пишет цель 【—】 каждый день «Сделано» → медали.

12. `family_chat_banner_no_family`
   - EN: Семья на сервере не найдена 【—】 отправка сообщений отключена.

13. `family_content_block_card_metric_hint`
   - RU: Детали 【—】 в Уведомлениях и Отчётах семьи

14. `family_groups_subtitle`
   - RU: Метки внутри одной семьи 【—】 без второго списка людей
   - EN: Labels inside one family 【—】 not a second member list

15. `family_growth_nudge_body_d3`
   - RU: Бесплатно 【—】 до 4 человек в семье. Отправьте приглашение за минуту.

16. `family_habit_custom_empty`
   - EN: Добавьте своё 【—】 например позвонить или зарядка

17. `family_habit_custom_limit_reached`
   - EN: Максимум 5 своих напоминаний 【—】 удалите одно

18. `family_habit_custom_mode_once_at_soon`
   - EN: Один раз (дата) 【—】 скоро

19. `family_habit_custom_once_at_past`
   - EN: Время уже прошло 【—】 выберите будущее

20. `family_habit_custom_server_outdated`
   - EN: Сервер пока не принимает свои напоминания. Локально всё работает 【—】 обновите сервер позже.

21. `family_habit_delivery_none`
   - EN: никому 【—】 включите «на этом телефоне» или детей

22. `family_habit_done_rewarded`
   - EN: Сделано 【—】 единорог получил заботу ✨

23. `family_habit_medicine_body`
   - RU: 💊 Лекарство 【—】 время принять.
   - EN: 💊 Medicine 【—】 time to take it.

24. `family_habit_medicine_custom_empty`
   - RU: Пока нет времени 【—】 добавьте ниже.
   - EN: No times yet 【—】 add one below.

25. `family_habit_medicine_disclaimer`
   - EN: ALADDIN не врач и не даёт медсоветов 【—】 только напоминание.

26. `family_habit_not_bedtime_hint`
   - EN: Gentle reminders only 【—】 not a screen lock.

27. `family_habit_section_subtitle`
   - EN: Вода, лекарство, телефон 【—】 на своём телефоне и/или у детей.

28. `family_habit_water_push_body_fmt`
   - RU: 💧 Вода 【—】 ещё стакан. Цель: %@
   - EN: 💧 Water 【—】 another glass. Goal: %@

29. `family_hub_chd_02_pipeline`
   - EN: Кибербуллинг 【—】 родительский контроль

30. `family_hub_chd_03_pipeline`
   - EN: Недельный отчёт 【—】 раздел «Отчёты»

31. `family_hub_chd_04_pipeline`
   - EN: Геозоны 【—】 раздел «Геолокация»

32. `family_hub_chd_05_pipeline`
   - EN: Игровая зависимость 【—】 лимиты времени

33. `family_hub_chd_06_pipeline`
   - EN: Случайные покупки 【—】 родительский контроль

34. `family_hub_chd_07_pipeline`
   - RU: Игры с насилием 【—】 топ приложений
   - EN: Violent games 【—】 top apps

35. `family_hub_chd_08_pipeline`
   - RU: Опасный контент 【—】 мониторинг
   - EN: Risky content 【—】 monitoring

36. `family_hub_chd_09_pipeline`
   - RU: Азарт 【—】 активность и лимиты
   - EN: Gambling 【—】 activity and limits

37. `family_hub_chd_10_pipeline`
   - RU: Экстремизм 【—】 подозрительная активность
   - EN: Extremism 【—】 suspicious activity

38. `family_hub_chd_11_pipeline`
   - RU: Риск самоповреждения 【—】 сигнал семье
   - EN: Self-harm risk 【—】 family alert

39. `family_hub_chd_12_pipeline`
   - RU: Реклама 【—】 защита сети
   - EN: Ads 【—】 network protection

40. `family_hub_chd_13_pipeline`
   - RU: Онлайн-знакомства 【—】 контакты
   - EN: Online strangers 【—】 contacts

41. `family_hub_chd_14_pipeline`
   - RU: Груминг 【—】 проверка сообщений
   - EN: Grooming 【—】 message checks

42. `family_hub_chd_15_pipeline`
   - RU: Кэтфишинг 【—】 проверка текста и ссылок
   - EN: Catfishing 【—】 text and link checks

43. `family_hub_chd_16_pipeline`
   - RU: Токсичные сообщества 【—】 отчёты
   - EN: Toxic communities 【—】 reports

44. `family_hub_chd_17_pipeline`
   - RU: Онлайн-азарт 【—】 отчёты и лимиты
   - EN: Online gambling 【—】 reports and limits

45. `family_hub_coverage_hint`
   - EN: Типы рисков для ребёнка 【—】 нажмите, чтобы открыть нужный раздел.

46. `family_identity_repair_section_body`
   - RU: Если участники есть, но раздел «Семья» ведёт себя странно 【—】 выровняйте привязку на этом устройстве.

47. `family_invite_soft_body`
   - RU: Добавьте ещё одного человека в семью 【—】 увидите защиту и точку на карте.
   - EN: Add one more person 【—】 see protection and their place on the map.

48. `family_invite_ttl_hint`
   - RU: Коды приглашения действуют 3 дня. Если не успели 【—】 отправьте новый.

49. `family_location_history_privacy_note`
   - RU: Историю видит только ваша семья. Старые точки удаляются автоматически, при удалении аккаунта 【—】 сразу.

50. `family_location_history_upsell`
   - RU: Хотите видеть дольше? Семейный 【—】 7 дней, Премиум 【—】 30 дней.
   - EN: Want to see further back? Family 【—】 7 days, Premium 【—】 30 days.

51. `family_moments_disclaimer`
   - EN: Только для семьи 【—】 не лента и не соцсеть.

52. `family_moments_empty`
   - EN: Пока нет моментов 【—】 добавьте первый.

53. `family_roster_manage_denied_banner_body`
   - RU: Приложение не видит вас как родителя или участника с ролью «Люди 60+» в этом списке. Выйдите из аккаунта и войдите снова, откройте раздел «Семья» повторно или дождитесь окончания синхронизации. Если проблема останется 【—】 обратитесь в поддержку.

54. `family_safe_word_no_family_step_2`
   - RU: Если вы начинаете 【—】 нажмите «Создать семью».
   - EN: If you’re starting 【—】 tap Create family.

55. `family_safe_word_no_family_step_3`
   - RU: Если вас пригласили 【—】 «Ввести код» или «Сканировать QR». Код вида FAM-XXXX… даёт родитель.
   - EN: If you were invited 【—】 Enter code or Scan QR. A parent shares a code like FAM-XXXX…

56. `family_safe_word_no_family_step_4`
   - RU: Когда семья появится 【—】 вернитесь сюда и сохраните фразу.
   - EN: Когда семья появится 【—】 вернитесь сюда и сохраните фразу.

57. `family_safe_word_setup_what`
   - RU: Кодовое слово 【—】 секретная фраза семьи (например: «серый волк»). Если звонят или пишут «от родных» и просят деньги / код / перевод 【—】 спросите эту фразу. Свой знает. Мошенник 【—】 нет.
   - EN: A family code word (for example: “grey wolf”). If someone calls or texts “from family” asking for money, a code, or a transfer 【—】 ask for this phrase. Your people know it. Scammers don’t.

58. `family_safe_word_subtitle`
   - RU: Если звонят «от родных» и просят деньги 【—】 спросите эту фразу. Чужой её не знает.
   - EN: If someone calls “from family” asking for money 【—】 ask this phrase. Strangers won’t know it.

59. `family_safe_word_verify_intro`
   - EN: Спросите у собеседника семейную фразу. Если не совпало 【—】 положите трубку.

60. `family_second_hand_step_2`
   - RU: Включите ALADDIN X AI 【—】 чтобы опасные номера подписывались.

61. `family_second_hand_teen_not_admin`
   - EN: Parents turn on critical settings 【—】 not you alone.

62. `family_second_hand_teen_subtitle`
   - RU: Вы свидетель и помощник 【—】 не единственный админ семьи.
   - EN: You are a witness and helper 【—】 not the only family admin.

63. `family_status_critical_message`
   - EN: Защита семьи недоступна (агенты или связь). Тариф может быть активен 【—】 проверьте экран «Тарифы».

64. `family_yesterday_push_body`
   - RU: Откройте историю мест 【—】 так спокойнее, когда близкие не рядом.
   - EN: Open place history 【—】 peace of mind when family is apart.

65. `invite_center_choose_flow_desc`
   - RU: Семья, новое устройство и приглашение друга 【—】 разные действия. Здесь они собраны рядом, чтобы не путать QR, 6-значный PIN и бонусную ссылку.

66. `main_family_network_layers_hint`
   - EN: Сеть защищает весь трафик; Safari 【—】 только браузер.

67. `main_family_network_protection_hint`
   - RU: Подробнее об отличиях счётчиков 【—】 в отчётах и уведомлениях.
   - EN: Подробнее об отличиях счётчиков 【—】 в отчётах и уведомлениях.

68. `main_family_start_trial_cta`
   - RU: Включить пробный на 14 дней 【—】 до 6 участников
   - EN: Start 14-day free trial 【—】 up to 6 members

69. `main_family_trial_ended_banner`
   - RU: Пробный закончился · Бесплатный тариф (семья до 4 человек). Антифрод 【—】 с Личного, вся семья 【—】 на Семейном.

70. `notification_smoke_family_habit_due`
   - EN: Привычка 【—】 due ping

71. `privacy_policy_section_family_location_content_6`
   - RU: История мест хранится на нашем сервере, чтобы семья могла посмотреть, где человек был. Срок зависит от тарифа: бесплатный и Личный 【—】 24 часа, пробный и Семейный 【—】 7 дней, Премиум 【—】 30 дней. Если у владельца семьи Семейный или Премиум, этот срок действует для всех её участников. Дольше 30 дней не храним никогда. Старые точки удаляются автоматически.
   - EN: Place history is stored on our server so your family can see where a person has been. How long depends on the plan: Free and Personal 【—】 24 hours, Trial and Family 【—】 7 days, Premium 【—】 30 days. If the family owner has Family or Premium, that period applies to every member. We never keep it longer than 30 days. Older points are deleted automatically.

72. `privacy_policy_section_family_location_content_7`
   - RU: Историю человека видят только участники его семьи: родители 【—】 всех, ребёнок 【—】 себя и родителей. При удалении аккаунта вся история мест и последняя точка удаляются с сервера. После выхода из семьи бывшая семья историю больше не видит.

73. `referral_invite_friends_desc`
   - EN: Друг получит −20% на первый месяц. Вам 【—】 дни семейной защиты после оплаты или 14 дней активной защиты.

74. `tariffs_family_features_5`
   - RU: Antifake по тарифу 【—】 только по вашему действию
   - EN: Antifake per plan 【—】 only when you tap Check

75. `tariffs_upgrade_personal_to_family_cta`
   - RU: Защитить всю семью 【—】 +%@ в месяц
   - EN: Protect your whole family 【—】 +%@/month

76. `tariffs_upgrade_personal_to_family_cta_plain`
   - RU: Защитить всю семью 【—】 перейти на Семейный
   - EN: Protect your whole family 【—】 switch to Family

77. `wellness_family_themes_empty`
   - EN: Пока нет заметных тем 【—】 это нормально.

78. `wellness_social_goal_family_chat`
   - EN: Напиши в семейный чат 【—】 родные рядом, даже если далеко.

### Ребёнок / parental (68)

1. `child_adaptive_loop_v2_confidence_message`
   - RU: Ты справишься. Ошибки 【—】 это часть обучения, не повод останавливаться.

2. `child_did_it_card_subtitle`
   - RU: Выбери дело или напиши своё 【—】 родители увидят
   - EN: Pick a task or write your own 【—】 parents will see it

3. `child_mnemo_baseline_offer_subtitle`
   - EN: 5 слов за 2 минуты 【—】 узнай свой стартовый уровень

4. `child_mnemo_baseline_recall_retry`
   - EN: Порядок не совпал 【—】 попробуй снова

5. `child_mnemo_baseline_retest_offer_subtitle`
   - EN: Прошло 90 дней 【—】 проверь, как выросла память (1 раз в квартал)

6. `child_mnemo_brand_promise`
   - EN: Не зубрёжка 【—】 умение вспоминать

7. `child_mnemo_capstone_prepare_hint`
   - EN: Вспомни образы и технику 【—】 потом объясни вслух

8. `child_mnemo_championship_recall_partial`
   - EN: Хорошая попытка 【—】 тренируй дальше

9. `child_mnemo_championship_subtitle`
   - EN: 20 образов за 5 минут 【—】 только твой личный рекорд

10. `child_mnemo_games_05_feedback_retry`
   - EN: Попробуй снова 【—】 вспомни образ

11. `child_mnemo_hint_ladder_recall_image_prompt`
   - EN: Сначала вспомни свой образ 【—】 без букв и вариантов

12. `child_mnemo_hint_ladder_try_again`
   - EN: Попробуй ещё 【—】 это тренировка, не ошибка

13. `child_mnemo_number_pegs_0`
   - EN: 0 【—】 кольцо

14. `child_mnemo_number_pegs_1`
   - EN: 1 【—】 свеча

15. `child_mnemo_number_pegs_2`
   - EN: 2 【—】 лебедь

16. `child_mnemo_number_pegs_3`
   - EN: 3 【—】 сердце

17. `child_mnemo_number_pegs_4`
   - EN: 4 【—】 стул

18. `child_mnemo_number_pegs_5`
   - EN: 5 【—】 крючок

19. `child_mnemo_number_pegs_6`
   - EN: 6 【—】 вишня

20. `child_mnemo_number_pegs_7`
   - EN: 7 【—】 коса

21. `child_mnemo_number_pegs_8`
   - EN: 8 【—】 снеговик

22. `child_mnemo_number_pegs_9`
   - EN: 9 【—】 воздушный шар

23. `child_mnemo_pictogram_draw_save_error`
   - EN: Не удалось сохранить 【—】 попробуй ещё раз

24. `child_mnemo_pictogram_draw_subtitle`
   - EN: Нарисуй яркий образ 【—】 он поможет вспомнить на повторении

25. `child_mnemo_pictogram_saved_badge`
   - EN: Твой образ сохранён 【—】 молодец!

26. `child_mnemo_reflect_feedback_hint`
   - EN: Почти 【—】 в этом уроке главная техника была другой:

27. `child_mnemo_reflect_subtitle`
   - EN: Короткая рефлексия 【—】 без оценки, только осознанность

28. `child_mnemo_semester_locked_subtitle`
   - EN: Сначала пройди «%@» 【—】 нужно набрать силу памяти

29. `child_mnemo_song_recall_retry`
   - EN: Попробуй снова 【—】 вспомни образ

30. `child_mnemo_song_track_1_line_1`
   - EN: Кот мурлычет 【—】 якорь номер раз

31. `child_mnemo_song_track_1_line_2`
   - EN: Звезда светит 【—】 рифма для нас

32. `child_mnemo_song_track_1_line_3`
   - EN: Шар летит 【—】 вспомни сейчас

33. `child_mnemo_song_track_2_line_1`
   - EN: Раз два три 【—】 образ в ряд

34. `child_mnemo_song_track_2_line_2`
   - EN: Четыре пять 【—】 не уступай

35. `child_mnemo_song_track_2_line_3`
   - EN: Шесть семь 【—】 запомни день

36. `child_mnemo_song_track_3_line_1`
   - EN: Красный круг 【—】 солнце в небе

37. `child_mnemo_song_track_3_line_2`
   - EN: Синий дом 【—】 мир в судьбе

38. `child_mnemo_song_track_3_line_3`
   - EN: Зелёный лист 【—】 свежий след

39. `child_mnemo_stories_recall_subtitle`
   - EN: Вспомни главный образ сюжета 【—】 без оценки

40. `child_mnemo_table_feedback_retry`
   - EN: Попробуй снова 【—】 вспомни порядок образов

41. `child_mnemo_table_subtitle`
   - EN: 6 образов сюжета 【—】 запомни таблицу для литературы

42. `child_mnemo_technique_picker_context_dates`
   - EN: Даты и факты 【—】 выбери технику для хронологии

43. `child_mnemo_technique_picker_context_formula`
   - EN: Формулы и шаги 【—】 выбери технику для правил

44. `child_mnemo_technique_picker_context_general`
   - EN: Общий материал 【—】 выбери свою технику

45. `child_mnemo_technique_picker_context_vocab`
   - EN: Словарь и термины 【—】 выбери технику для слов

46. `child_mnemo_technique_picker_subtitle`
   - EN: Мета-выбор 【—】 ты решаешь, как запоминать

47. `child_mnemo_warmup_focus_prompt`
   - EN: Закрой глаза на миг. Представь один яркий образ 【—】 потом откроем урок.

48. `child_mnemo_warmup_subtitle`
   - EN: Спокойно вспомни технику 【—】 без спешки

49. `child_overview_body`
   - RU: Пауза, сайты, лимит и сон 【—】 ниже. Полные отчёты 【—】 в родительском разделе.

50. `child_rewards_achievement_excellent_desc`
   - EN: 5 пятёрок подряд 【—】 отличная работа!

51. `child_safety_scenario_feedback_1c`
   - RU: Неверно: даже частичная геолокация 【—】 это персональные данные.

52. `child_safety_scenario_feedback_2b`
   - RU: Верно: сначала проверка у взрослого и источника 【—】 самый безопасный путь.

53. `child_study_creativity_page_3`
   - EN: Ошибки в творчестве 【—】 это шаг к новым открытиям.

54. `child_study_project_page_3`
   - EN: Итог проекта 【—】 продукт, презентация и выводы.

55. `child_toys_color_game_wrong`
   - EN: Not quite 【—】 try again.

56. `faq_parental_bypass_answer`
   - EN: Защита от обхода помогает родителям видеть, когда ребёнок пытается обойти правила семьи.

Что отслеживается:
• Режим инкогнито и приватные окна
• Tor и анонимные браузеры
• Прокси, туннели и обход защиты сети

Родители получают отчёт о попытках обхода 【—】 без mock-ответов в production.

✅ ALADDIN помогает держать правила честными, а не наказывать за каждый клик.

57. `focus_session_aborted`
   - EN: Ок, остановились. Без штрафа 【—】 можно начать снова.

58. `focus_session_completed`
   - EN: Отлично 【—】 сессия завершена.

59. `focus_session_name_option_1_desc`
   - RU: Таймер 25 или 60 минут. Помогает сосредоточиться 【—】 приложения не блокирует.
   - EN: A 25 or 60 minute timer. Helps you focus 【—】 does not block apps.

60. `focus_teen_entry_subtitle`
   - EN: Сам включи 25 минут тишины 【—】 без слежки.

61. `games_parental_info_description`
   - EN: Здесь вы можете включать и отключать игровые элементы. Единорог-питомец всегда активен 【—】 это основная мотивация.

62. `games_parental_pet_description`
   - EN: Тамагочи-питомец с индикаторами ❤️🍎⭐😊. Ребёнок кормит, играет, гладит. 4 стадии эволюции. Нельзя отключить 【—】 это основа мотивации.

63. `parental_custom_sites_empty`
   - RU: Пока нет своих сайтов 【—】 можно добавить.
   - EN: No custom sites yet 【—】 you can add some.

64. `parental_custom_sites_subtitle`
   - RU: Добавьте сайт 【—】 он перестанет открываться у ребёнка в Safari.
   - EN: Add a site 【—】 it will be blocked for the child in Safari.

65. `parental_filter_safari_honesty`
   - RU: Фильтр сайтов работает в Safari. В других приложениях 【—】 отдельно.

66. `referral_a_rewards_caption`
   - EN: Другу всегда −20%. Вам 【—】 дни семейной защиты по числу успешных семей (не растущий %).

67. `screen_time_fc_need_auth`
   - RU: Screen Time: нет авторизации на этом устройстве 【—】 настройте на iPhone ребёнка.
   - EN: Screen Time: not authorized on this device 【—】 set up on the child’s iPhone.

68. `unified_time_limits_server_bedtime_fmt`
   - RU: Окно сна: %@ 【—】 %@
   - EN: Bedtime window: %@ 【—】 %@

### Проверить / antifake (60)

1. `antifake_apple_limits_calls_body`
   - EN: Во время звонка ALADDIN не слушает разговор. После звонка загрузите запись на вкладке «Звонок» (блок «Проверка записи»), если она у вас есть. Метки на входящих 【—】 отдельный блок ниже на той же вкладке. Если звонят «из банка» 【—】 не называйте пароли; положите трубку и перезвоните по номеру с официального сайта.

2. `antifake_apple_limits_can_4`
   - EN: Показать метку «возможный мошенник» на входящем 【—】 вкладка «Звонок», блок меток (Call Directory)

3. `antifake_apple_limits_cannot_1`
   - EN: Не слушаем все телефонные звонки в фоне 【—】 iOS это запрещает

4. `antifake_apple_limits_cannot_5`
   - EN: Не обещаем 100% точность 【—】 бывает статус «неясно»

5. `antifake_apple_limits_disclaimer`
   - EN: Тумблеры «Защита от угроз» на этом экране 【—】 серверные агенты, не перехват сотовых звонков.

6. `antifake_apple_limits_intro`
   - EN: ALADDIN проверяет подозрительный контент, который вы сами отправляете. Результат 【—】 оценка, не юридическое заключение.

7. `antifake_apple_limits_website_body`
   - EN: На aladdin-ai.ru/antifake 【—】 проверка текста, голоса и видео без установки; файлы больше 25 МБ; отчёты об утечках. То, что iPhone не даёт сделать автоматически 【—】 вы делаете сами: вставили или загрузили.

8. `antifake_audio_probe_footnote`
   - EN: Голос: распознавание речи → проверка на мошенничество; отдельно 【—】 признаки ИИ-голоса. При сомнении результат «неясно».

9. `antifake_call_directory_setup_step5_retry`
   - RU: Если переключателя нет 【—】 обновите приложение и перезагрузите iPhone
   - EN: If the switch is missing 【—】 update the app and restart iPhone

10. `antifake_call_directory_status_not_installed`
   - EN: Расширение не найдено 【—】 обновите приложение

11. `antifake_call_hint`
   - EN: Выберите файл записи (m4a, mp3 и др.). Номер и имя звонящего 【—】 по желанию.

12. `antifake_call_number_only_hint`
   - RU: Без записи проверим только номер. Чтобы проверить голос собеседника 【—】 прикрепите запись разговора.

13. `antifake_call_soon`
   - RU: Проверка звонка может занять больше времени. Если зависает 【—】 Отменить и повторить, или проверьте голос/текст.
   - EN: Call checks can take longer. If it hangs 【—】 Cancel and retry, or try voice/text.

14. `antifake_contact_hint`
   - EN: Укажите номер звонящего и имя из контактов 【—】 можно вставить из буфера.

15. `antifake_doc_check_hint`
   - RU: Сфотографируйте документ или выберите PDF 【—】 скажем, похоже на правду или на обман.
   - EN: Photograph a document or choose a PDF 【—】 we’ll say if it looks real or fake.

16. `antifake_document_hint`
   - EN: Сфотографируйте штраф, договор или счёт 【—】 или выберите фото/PDF. Скажем: похоже на правду или на обман.

17. `antifake_elderly_one_tap_opened`
   - EN: Открыта проверка звонка 【—】 загрузите запись, если есть.

18. `antifake_feedback_success`
   - EN: Спасибо 【—】 учтём в улучшении модели

19. `antifake_feedback_was_scam_hint`
   - EN: Мы не добавим слова в словарь автоматически 【—】 сначала ручная проверка.

20. `antifake_feedback_was_scam_queued`
   - EN: Спасибо 【—】 фразы поставлены в очередь на разбор словаря.

21. `antifake_feedback_was_scam_success`
   - EN: Спасибо 【—】 записали отзыв.

22. `antifake_post_call_banner_body`
   - EN: Если разговор показался подозрительным 【—】 выберите файл записи и нажмите «Проверить».

23. `antifake_premium_gate_bullet_1`
   - EN: Текст, ссылки, аудио и видео 【—】 по вашему запросу

24. `antifake_quick_voice_body`
   - RU: Запишите до 30 секунд речи. Без фоновой прослушки 【—】 только по вашей кнопке.
   - EN: Record up to 30 seconds of speech. No background listening 【—】 only when you tap.

25. `antifake_reason_urgency_manipulation`
   - EN: Давление срочностью 【—】 типичный приём мошенников

26. `antifake_reason_url_credential_trap`
   - EN: Символ @ в URL 【—】 возможная подмена домена

27. `antifake_spoof_hint_authority`
   - EN: «Банк» или «налоговая» с личного номера 【—】 частый приём мошенников.

28. `antifake_spoof_hint_directory`
   - EN: Номер есть в базе жалоб на мошенников 【—】 не называйте коды и не переводите деньги.

29. `antifake_spoof_hint_short_code`
   - EN: Короткий код (например 900) с названием банка на экране 【—】 перезвоните по номеру с карты.

30. `antifake_transfer_cta_title`
   - EN: Перед переводом 【—】 проверьте

31. `antifake_upload_max_hint`
   - EN: Максимальный размер файла 【—】 25 МБ

32. `antifake_url_sources_empty`
   - EN: Отдельных внешних источников для этой ссылки нет 【—】 опирайтесь на причины выше и официальный сайт.

33. `antifake_url_trust_copy_uncertain`
   - EN: Ссылка вызывает сомнения 【—】 проверьте через официальный сайт или приложение.

34. `antifake_verdict_insufficient_hint`
   - EN: Вставьте фрагмент новости, сообщения или письма 【—】 не формулу и не одно слово.

35. `antifake_verdict_next_steps_family`
   - EN: Если звучит как родственник 【—】 спросите семейное кодовое слово. Не совпало? Положите трубку и перезвоните на сохранённый номер.

36. `antifake_verdict_story_fake`
   - EN: Похоже на обман. Не переводите деньги и не диктуйте коды 【—】 сначала скажите взрослому.

37. `antifake_verdict_story_lead`
   - EN: Проверили → вот оценка. Дальше 【—】 коротко: почему так и что сделать.

38. `antifake_verdict_story_real`
   - EN: Похоже на обычное сообщение. Если сомнение осталось 【—】 всё равно лучше переспросить у близких.

39. `antifake_verdict_story_uncertain`
   - EN: Пока неясно. Не торопитесь с действиями 【—】 сверьте с взрослым или официальным каналом.

40. `antifake_video_hint`
   - EN: Выберите видео (лучше MP4 H.264). Сервер смотрит кадры; AV1 из Telegram часто не читается 【—】 тогда экспортируйте как MP4.

41. `antifake_video_probe_footnote`
   - EN: Видео: кадры + локальная модель. Если файл не открылся 【—】 «мало данных», не зелёный «всё ок».

42. `antifake_voice_fraud_threshold_body`
   - EN: Порог для меток CallKit и авто-добавления номера после проверки записи звонка. Настраивается на этом устройстве 【—】 не для всей семьи.

43. `antifake_voice_fraud_threshold_hint_mild`
   - EN: Больше предупреждений 【—】 возможны ложные срабатывания.

44. `antifake_voice_fraud_threshold_hint_strict`
   - EN: Только высокая уверенность 【—】 меньше ложных меток.

45. `faq_antifake_after_call_answer`
   - EN: После разговора ALADDIN может напомнить открыть вкладку «Звонок» (переключатель в блоке **«Проверка записи»**).

Загрузите запись, если она есть, и при желании укажите номер из «Недавних» в приложении «Телефон».

iOS не даёт приложению автоматически узнать номер 【—】 введите его вручную, если помните.

46. `faq_antifake_apple_limits`
   - EN: What can Antifake do on iPhone 【—】 and what can't it?

47. `faq_antifake_apple_limits_answer`
   - RU: ALADDIN проверяет текст, ссылки, аудио и видео только когда вы сами нажимаете «Проверить» или делитесь контентом через «Поделиться».

Мы не слушаем все телефонные звонки в фоне 【—】 iOS это запрещает. Не кладём трубку автоматически и не перехватываем FaceTime или мессенджеры.

Метки на звонках 【—】 только для номеров из проверенной базы (Call Directory), не для всех незнакомых.

На сайте aladdin-ai.ru/antifake 【—】 **14 дней бесплатно** или Family/Premium по коду; лимит файлов 25 МБ. В приложении 【—】 активный App Trial, Family или Premium.

Результат 【—】 оценка (похоже на подделку / неясно / похоже на подлинное), не юридическое заключение.
   - EN: ALADDIN checks text, links, audio, and video only when you tap Check or share content via the Share sheet.

We do not listen to all phone calls in the background 【—】 iOS forbids that. We do not hang up automatically or intercept FaceTime or messengers.

Call labels apply only to numbers in our verified database (Call Directory), not every unknown caller.

On aladdin-ai.ru/antifake 【—】 **14-day free trial** or Family/Premium with a code; 25 MB file limit. In the app 【—】 active App Trial, Family, or Premium.

Results are assessments (likely fake / uncertain / likely real), not legal verdicts.

48. `faq_antifake_call_directory_answer`
   - EN: Откройте «Проверить подлинность» → вкладка **«Звонок»** → блок «Метки на входящих» → инструкция и «Синхронизировать».

Номера только с сервера ALADDIN.

Метка на экране входящего, если номер в списке. iOS 18+: Настройки → Приложения → Телефон → Блокировка и опознавание → **ALADDIN X AI**.

Это не блокировка всех незнакомых 【—】 только подпись известных мошеннических номеров.

ALADDIN не слушает звонки в реальном времени (так устроен iOS). Запись, если она у вас есть, проверяйте во вкладке «Звонок» после разговора.

49. `faq_website_antifake_answer`
   - EN: Откройте aladdin-ai.ru/antifake на компьютере или в браузере телефона.

**14 дней бесплатно** на этом устройстве (кнопка «Начать пробный период») **или** Family/Premium 【—】 введите код активации.

1. Вкладка «Текст» 【—】 вставьте SMS, письмо или ссылку → «Проверить».
2. «Голос» 【—】 загрузите запись или голосовое (до 25 МБ).
3. «Видео» 【—】 ролик «из банка» или deepfake.
4. «Звонок» 【—】 запись после разговора + номер звонящего (если помните); метки на входящих 【—】 в app (ALADDIN X AI).

Результат: похоже на подделку / неясно / похоже на подлинное. Это оценка, не юридическое заключение.

В приложении: активный App Trial, Family или Premium 【—】 проверки, история и семейные алерты. Web-trial на сайте 【—】 отдельный контур.

50. `premium_nudge_antifake_body`
   - RU: В Family и Premium 【—】 расширенный Antifake для семьи.

51. `protection_antifake_accordion_subtitle`
   - EN: Проверка по запросу; метки на входящих 【—】 на вкладке «Звонок»

52. `protection_antifake_card_title`
   - EN: Antifake 【—】 Проверить подлинность

53. `support_antifake_qr_hint`
   - EN: Наведите камеру на код 【—】 откроется проверка на сайте

54. `support_antifake_share_note`
   - EN: Звонки проверяются отдельно 【—】 загрузите запись после разговора в Hub

55. `support_antifake_share_step3`
   - EN: Выберите «Проверить в ALADDIN». Если пункта нет 【—】 «Изменить действия…» и добавьте ALADDIN

56. `support_antifake_share_subtitle`
   - EN: Подозрительная страница или сообщение 【—】 через «Поделиться» в Safari или Telegram

57. `support_antifake_web_subtitle`
   - EN: 14 дней бесплатно на сайте 【—】 текст, голос и видео

58. `tariffs_antifake_action_only`
   - RU: Только по вашему действию 【—】 без фоновой записи
   - EN: Only when you tap 【—】 no background recording

59. `tariffs_antifake_paid`
   - RU: Antifake: без лимита 【—】 текст, документы, голос, видео, звонок
   - EN: Antifake: unlimited 【—】 text, docs, voice, video, call

60. `voice_safety_coach_tip`
   - RU: Скопируйте подозрительную ссылку, затем скажите «ссылка» или «проверка» 【—】 откроем проверку и подставим скопированное. Также: тревога / идея / не забыть.
   - EN: Copy a suspicious link, then say “link” or “check” 【—】 we’ll open the check and paste what you copied. Also: alert / idea / remind.

### Где семья / карта (53)

1. `crash_alert_call_services_question`
   - RU: Если молчать 【—】 семья получит сигнал. Можно отменить.

2. `crash_alert_false_positive_warning`
   - RU: Ложные срабатывания бывают 【—】 нажмите «Всё в порядке», если всё хорошо.
   - EN: False alerts happen 【—】 tap “I’m fine” if you’re OK.

3. `crash_checklist_location`
   - RU: • Геолокация 【—】 чтобы понять, где вы, если сработала защита
   - EN: • Location 【—】 so we know where you are if an alert fires

4. `crash_checklist_motion`
   - RU: • Датчик движения 【—】 на этом iPhone должен быть акселерометр
   - EN: • Motion sensor 【—】 this iPhone needs an accelerometer

5. `crash_checklist_notifications`
   - RU: • Уведомления 【—】 чтобы семья и вы увидели сигнал
   - EN: • Notifications 【—】 so you and family see the alert

6. `crash_confirm_offline`
   - RU: Нет сети 【—】 сохраним и отправим позже.
   - EN: You’re offline 【—】 we’ll save and send later.

7. `crash_logs_support_footer`
   - EN: Добровольно. Бот: @AladdinchatAI_bot. Не собираем пароли, карты, SMS, контакты и медиа для этого экрана 【—】 только то, что уже записано на устройстве для стабильности приложения. Перед отправкой можете стереть чувствительные строки вручную.

8. `crash_logs_support_telegram_alert_message`
   - EN: Откроется чат с официальным ботом в Telegram: @AladdinchatAI_bot (в списке чатов имя может отображаться как «AladdinAi_bot»).

Это добровольно. Мы не собираем через этот экран ваши пароли, данные банковских карт, SMS, контакты телефонной книги и фото/видео из галереи.

В отчёт могут попасть только уже записанные на устройстве технические сведения: модель устройства, версия iOS, версия и номер сборки приложения, служебные трассировки и сообщения об ошибках. Перед отправкой вы можете удалить из текста всё лишнее.

Полный файл: «Поделиться» → Telegram → @AladdinchatAI_bot.

После отправки сообщение обрабатывается платформой Telegram по её правилам. Подробнее 【—】 Политика конфиденциальности, раздел «Диагностика сбоев и поддержка в Telegram».

9. `drive_inc_accel_explain`
   - RU: Резкий разгон 【—】 резкое ускорение. Когда появятся данные с датчиков, здесь будет число за неделю.

10. `drive_inc_explain_data_note`
   - RU: Пока нет поездок с датчиками 【—】 счётчики 0. На вкладке «Вождение» нажмите «Разрешить движение и фитнес», затем совершите поездку.
   - EN: No sensor trips yet 【—】 counters stay 0. On the Driving tab tap Allow Motion & Fitness, then take a drive.

11. `drive_inc_speed_explain`
   - RU: Риск высокой скорости. Пока нет детальных поездок 【—】 показываем честный ноль, без выдуманных цифр.
   - EN: High-speed risk. Until detailed trips exist we show an honest zero 【—】 no invented numbers.

12. `drive_pdf_disclaimer`
   - EN: Family estimate only 【—】 not an insurance report.

13. `drive_weekly_locked_body`
   - EN: Speed and harsh-maneuver counts unlock on a family plan. Trip and km stats stay honest 【—】 no invented numbers.

14. `drive_weekly_locked_title`
   - RU: Риски за рулём 【—】 по Family/Premium
   - EN: Driving risks 【—】 Family/Premium

15. `driving_play_no_track`
   - RU: Маршрут появится после поездки с доступом к месту. Пока 【—】 время, км и скорость

16. `driving_reports_why_location`
   - RU: 2. Включите геолокацию «Всегда» (и точное место) 【—】 иначе поездки в фоне не пишутся.

17. `driving_reports_why_motion`
   - RU: 1. Разрешите «Движение и фитнес» для ALADDIN 【—】 так телефон понимает поездку.

18. `driving_reports_why_trip`
   - RU: 3. Проедьте за рулём с открытым или в фоне ALADDIN 【—】 затем откройте «Вождение» снова.

19. `faq_crash_detection_answer`
   - EN: Обнаружение аварии 【—】 это когда телефон замечает резкое столкновение во время движения.

Как это работает:
• Датчики устройства фиксируют сильный удар
• ALADDIN показывает предупреждение
• Вы сами решаете, вызывать ли помощь

⚠️ Возможны ложные срабатывания 【—】 всегда проверяйте ситуацию!

✅ ALADDIN помогает быстрее связаться с близкими, но не заменяет вызов 112.

20. `geofence_family_chat_arrived`
   - RU: %@: пришёл(а) 【—】 %@
   - EN: %@: arrived 【—】 %@

21. `geofence_family_chat_left`
   - RU: %@: ушёл(а) 【—】 %@
   - EN: %@: left 【—】 %@

22. `geofence_noshow_roles_hint`
   - RU: Родитель видит места ребёнка (если настроено). Супруги не следят друг за другом 【—】 каждый настраивает свой телефон.
   - EN: A parent sees a child’s places when set up. Spouses do not track each other 【—】 each sets up their own phone.

23. `geofence_noshow_section_hint`
   - RU: Если к сроку человека нет на месте 【—】 придёт мягкое уведомление.
   - EN: If they are not at the place by the time 【—】 you get a soft notification.

24. `geofences_empty_body`
   - RU: Добавьте Дом или Школу 【—】 с реальным адресом.

25. `geofences_empty_list_hint`
   - RU: Нет мест 【—】 добавьте Дом или Школу
   - EN: No places 【—】 add Home or School

26. `home_map_iot_resume_unavailable`
   - EN: Снять паузу сейчас нельзя 【—】 сервер обновляется. Попробуйте чуть позже.

27. `home_map_phones_empty`
   - EN: Пока нет привязанных телефонов 【—】 добавьте ниже.

28. `home_map_screen_time_link`
   - EN: Лимиты экранного времени 【—】 в разделе «Семья»

29. `map_anti_spy_note`
   - RU: Только последняя точка 【—】 по согласию семьи.
   - EN: Last known point 【—】 with family consent only.

30. `map_bt_soon_body`
   - RU: Рядом / метки 【—】 в скором времени.
   - EN: Nearby / tags 【—】 coming soon.

31. `map_hub_safety_sos_note`
   - RU: Удержание SOS для семьи 【—】 на следующем шаге. Без «помощь уже едет».

32. `map_hub_subscription_body`
   - RU: Семейный тариф ALADDIN 【—】 спокойствие для всех. Откройте планы без чужого бренда.
   - EN: ALADDIN Family plan 【—】 calm for everyone. Open plans without a third-party brand.

33. `map_invite_banner_title`
   - RU: Пригласите других 【—】 вместе спокойнее
   - EN: Invite others 【—】 safer together

34. `map_perm_precise_hint`
   - RU: В Настройках iPhone включите «Точные» для ALADDIN 【—】 точка будет точнее.

35. `map_pin_preview_body`
   - RU: Метка семьи с кольцом и зарядом. Цвета ALADDIN 【—】 без чужого бренда.
   - EN: Family pin with ring and battery. ALADDIN colors 【—】 no third-party brand.

36. `map_places_search_hint`
   - RU: Начните печатать 【—】 появятся подсказки

37. `map_routes_body`
   - RU: Откроем Apple Карты с выбранным способом. Точка 【—】 последняя известная.

38. `map_share_expired`
   - RU: Срок ссылки истёк 【—】 отправьте место снова
   - EN: Location link expired 【—】 send your place again

39. `map_sheet_drag_hint`
   - RU: Тяните полоску вверх 【—】 список больше, карту меньше. Вниз 【—】 карта на весь экран.

40. `map_soft_paywall_body`
   - RU: Карта семьи уже с вами. Family ALADDIN 【—】 спокойствие для всех устройств. Можно позже.
   - EN: Family map is already with you. ALADDIN Family 【—】 calm across devices. You can skip for now.

41. `map_soon_tile_body`
   - RU: В скором времени. Подключим метки честно 【—】 без фейковых точек.
   - EN: Coming soon. Tags will connect for real 【—】 no fake pins.

42. `motion_settings_hint_open_driving`
   - RU: Если в Настройках нет «Движение и фитнес» 【—】 откройте вкладку Вождение один раз, затем снова Настройки.

43. `notification_help_check_quiet`
   - EN: Тихие часы 【—】 выключены

44. `notification_help_check_quiet_mode`
   - EN: Тихий режим 【—】 выключен

45. `premium_nudge_map_body`
   - RU: В Family 【—】 живая карта и больше мест для семьи.

46. `privacy_policy_section_crash_diagnostics_content_1`
   - EN: Бот поддержки в Telegram: @AladdinchatAI_bot. В списке чатов отображаемое имя может быть «AladdinAi_bot» 【—】 это нормально для Telegram.

47. `privacy_policy_section_crash_diagnostics_content_4`
   - EN: В технический отчёт могут попасть только уже записанные на устройстве сведения для стабильности приложения: модель устройства, версия iOS, версия и номер сборки приложения, служебные трассировки, сообщения об ошибках сети и работы приложения. Там теоретически могут оказаться фрагменты URL или идентификаторов, если они попали в лог ошибки 【—】 перед отправкой вы можете удалить такие строки вручную.

48. `privacy_policy_section_crash_diagnostics_content_6`
   - EN: Цель такой передачи 【—】 только помощь в устранении сбоев и улучшение качества приложения; данные не используются для рекламы и не продаются.

49. `privacy_policy_section_crash_diagnostics_subtitle`
   - EN: Официальный бот @AladdinchatAI_bot 【—】 только по вашей инициативе

50. `safety_crash_body`
   - RU: Оповещение семье, если похоже на ДТП. Эвакуатор 【—】 когда будет партнёр.

51. `trip_no_map_track`
   - RU: Маршрут на карте 【—】 после поездки с доступом к месту

52. `where_phone_map_empty`
   - RU: Точки ещё нет. Отправьте место один раз 【—】 появится на карте.
   - EN: No point yet. Send place once 【—】 it appears on the map.

53. `where_phone_trail_empty`
   - RU: Пока пусто. След 【—】 только приходы и уходы из сохранённых мест за сегодня.

### Настройки / профиль (20)

1. `active_sessions_apple_privacy_note`
   - RU: Показываем устройства семейной защиты (имя, тип, последняя активность) 【—】 без точного GPS. «Выйти» снимает устройство с семьи после Parent Gate.
   - EN: We show family protection devices (name, type, last activity) 【—】 not precise GPS. Signing out removes a device from your family after Parent Gate.

2. `notification_help_check_important`
   - EN: Только важные 【—】 выключен

3. `notification_help_subtitle`
   - EN: Если тумблер включён, но пуш тихий 【—】 чаще всего Quiet / Только важные / DND или нет разрешения iOS.

4. `notification_help_test_body`
   - EN: Если видите это 【—】 цепочка уведомлений работает.

5. `notification_smoke_body_fmt`
   - EN: Smoke #%d type=%@ 【—】 локальная цепочка OK

6. `notification_smoke_referral_grant`
   - EN: Рефка 【—】 дни защиты

7. `privacy_policy_section_5_content`
   - RU: Данные хранятся только в течение срока, необходимого для соответствующей функции, безопасности, поддержки и законных обязательств; локальные данные удаляются вместе с приложением, а серверные 【—】 по правилам удаления аккаунта и конкретного сервиса. Функции безопасности и подсказки ALADDIN являются вспомогательными: они могут ошибаться и не заменяют родителя, экстренные службы, банк, врача, юриста или другого специалиста. Об изменениях политики сообщается в приложении; действует версия с указанной датой обновления.
   - EN: Данные хранятся только в течение срока, необходимого для соответствующей функции, безопасности, поддержки и законных обязательств; локальные данные удаляются вместе с приложением, а серверные 【—】 по правилам удаления аккаунта и конкретного сервиса. Функции безопасности и подсказки ALADDIN являются вспомогательными: они могут ошибаться и не заменяют родителя, экстренные службы, банк, врача, юриста или другого специалиста. Об изменениях политики сообщается в приложении; действует версия с указанной датой обновления.

8. `privacy_policy_section_auth_content_4`
   - EN: Face ID: Данные лица НЕ собираются 【—】 приложение использует только встроенную функцию iOS для локальной аутентификации

9. `privacy_policy_section_auth_content_5`
   - EN: Face ID: Данные лица НЕ передаются третьим лицам 【—】 вся обработка происходит локально на устройстве в Secure Enclave

10. `privacy_policy_section_auth_content_6`
   - EN: Face ID: Данные лица НЕ хранятся на наших серверах 【—】 они остаются только на устройстве пользователя и удаляются при удалении приложения

11. `privacy_policy_section_calls_memory_content_3`
   - RU: Аудио и выжимка по умолчанию хранятся на устройстве. На сервер 【—】 только если вы сами отправите (например, проверка antifake).
   - EN: Аудио и выжимка по умолчанию хранятся на устройстве. На сервер 【—】 только если вы сами отправите (например, проверка antifake).

12. `privacy_policy_section_calls_memory_content_6`
   - RU: Кнопки «спокойно» / «деньги» после звонка 【—】 ваш ручной сигнал семье, не автоматическое доказательство мошенничества.
   - EN: Кнопки «спокойно» / «деньги» после звонка 【—】 ваш ручной сигнал семье, не автоматическое доказательство мошенничества.

13. `privacy_policy_section_not_collected_content_2`
   - RU: Телефоны и email для рекламы не берём. Дом и школу 【—】 только если родитель сам сохранил в «Где семья»

14. `privacy_policy_section_principles_content_2`
   - EN: Принцип локальной обработки: чувствительные данные на устройстве; облачный AI, antifake и экстренные функции 【—】 на серверах ALADDIN по контракту

15. `privacy_policy_section_wellness_content_1`
   - RU: Раздел «Настроение и поддержка» 【—】 самопомощь: отметка настроения, упражнения, короткие опросники (не диагноз). Разговор ведёт цифровой друг (искусственный интеллект) в чате с героем. Нет живых консультантов, операторов и врачей в чате.
   - EN: Раздел «Настроение и поддержка» 【—】 самопомощь: отметка настроения, упражнения, короткие опросники (не диагноз). Разговор ведёт цифровой друг (искусственный интеллект) в чате с героем. Нет живых консультантов, операторов и врачей в чате.

16. `privacy_policy_section_wellness_content_3`
   - RU: «Понять себя» (сны и символы) 【—】 только метафоры для размышления, без предсказаний и магии.
   - EN: Understand yourself (dreams and symbols) uses metaphors for reflection only 【—】 no predictions or fortune-telling.

17. `privacy_policy_section_wellness_content_4`
   - RU: Могут сохраняться: настроение, ответы на короткие опросники, выбранный тип самопомощи. Для подростков 【—】 обезличенные итоги для семьи только с согласия. Текст чата ребёнка родителю дословно не показывается.
   - EN: Могут сохраняться: настроение, ответы на короткие опросники, выбранный тип самопомощи. Для подростков 【—】 обезличенные итоги для семьи только с согласия. Текст чата ребёнка родителю дословно не показывается.

18. `privacy_policy_section_wellness_content_6`
   - RU: При признаках кризиса 【—】 подсказка обратиться к взрослому, которому доверяете, и на линии помощи (112, 8-800-2000-122). ALADDIN не вызывает специалиста и не оказывает экстренную медпомощь.
   - EN: При признаках кризиса 【—】 подсказка обратиться к взрослому, которому доверяете, и на линии помощи (112, 8-800-2000-122). ALADDIN не вызывает специалиста и не оказывает экстренную медпомощь.

19. `privacy_policy_section_wellness_content_7`
   - RU: Удаление данных о настроении и самочувствии 【—】 по запросу через поддержку.
   - EN: Удаление данных о настроении и самочувствии 【—】 по запросу через поддержку.

20. `settings_notification_test_hint`
   - EN: Проверка прямо из Настроек 【—】 через 1 сек

### Тарифы / подписка (17)

1. `analytics_trial_mode_notice`
   - EN: Пробный период использует лимиты выбранного тарифа. Ниже 【—】 только статистика работы защиты за период.

2. `dojim_trial_before_3_body`
   - EN: Осталось 3 дня. Тарифы или рефка: другу −20% на первый месяц, вам 【—】 дни защиты.

3. `dojim_trial_before_7_title`
   - EN: Пробный период 【—】 ещё 7 дней

4. `notification_smoke_subscription_d1`
   - EN: Подписка 【—】 дожим D+1

5. `notification_smoke_subscription_d3`
   - EN: Подписка 【—】 дожим D+3

6. `pay_tiers_plain_body`
   - RU: После входа пробный период 14 дней включается сам. Здесь 【—】 переход на платный тариф.

7. `profile_subscription_free_no_expiry`
   - EN: Тариф Free 【—】 дата окончания не ограничена.

8. `tariffs_ai_protection`
   - EN: 🤖 AI защита 【—】 набор угроз по тарифу

9. `tariffs_billing_autorenew_note`
   - RU: Месяц и год 【—】 подписка с автопродлением. Отмена в Настройки → Apple ID → Подписки.

10. `tariffs_free_features_2`
   - RU: Ребёнок 【—】 пауза интернета, лимит, bedtime
   - EN: Child 【—】 internet pause, limit, bedtime

11. `tariffs_free_features_3`
   - RU: Карта 【—】 1 last-point (одна последняя точка, не трек)
   - EN: Map 【—】 1 last-point (single pin, not a track)

12. `tariffs_gates_free_note`
   - RU: Бесплатно: семья до 4, живая карта, SOS. Антифрод 【—】 с Личного.

13. `tariffs_personal_features_6`
   - RU: Только по вашему действию 【—】 без фоновой записи
   - EN: Only when you act 【—】 no background recording

14. `tariffs_personal_voice_video_limit`
   - RU: Проверка голоса и видео 【—】 %d в месяц
   - EN: Voice & video checks 【—】 %d per month

15. `tariffs_premium_features_5`
   - EN: Проверка текста и ссылок 【—】 по вашему запросу

16. `tariffs_premium_features_8`
   - RU: Только по вашему действию 【—】 без фоновой записи
   - EN: Only when you act 【—】 no background recording

17. `tariffs_price_unavailable`
   - EN: 【—】

### Общие / common (4)

1. `delete_account_error_gateway`
   - RU: Сервер вернул защитную оболочку без подтверждения удаления (mock-real-protection). Удаление не подтверждено 【—】 нужно исправить ответ DELETE /api/user/delete на бэкенде.
   - EN: The server returned a protection wrapper without confirming deletion (mock-real-protection). Deletion was not confirmed 【—】 the DELETE /api/user/delete response must be fixed on the backend.

2. `im_ok_no_gps_honesty`
   - RU: Без геолокации 【—】 только ваш сигнал семье.
   - EN: No location 【—】 just your OK signal to the family.

3. `im_ok_queue_delivered_body`
   - RU: Связь появилась 【—】 семья получила ваше сообщение.
   - EN: You’re back online 【—】 the family got your message.

4. `im_ok_sent_local`
   - RU: Сохранили на телефоне. Как только связь появится 【—】 отправим семье.
   - EN: Сохранили на телефоне. Как только связь появится 【—】 отправим семье.

### Онбординг (2)

1. `onboarding_mnemo_academy_desc`
   - EN: Учимся запоминать с образами. Не зубрёжка 【—】 умение вспоминать. Научные методы: образ, якорь, интервальное повторение.

2. `onboarding_page6_desc`
   - RU: Местоположение всей семьи 【—】 на карте в приложении. Сообщим, когда ребёнок пришёл домой, в школу или секцию.
   - EN: Местоположение всей семьи 【—】 на карте в приложении. Сообщим, когда ребёнок пришёл домой, в школу или секцию.

### VPN / сеть (1)

1. `vpn_help_proxy_answer`
   - EN: Прокси защищает только браузер, а защита сети 【—】 весь трафик устройства.

---

## Swift: возможные UI-строки с «—»

### `ARCHIVE_ONLY_DO_NOT_EDIT_2025-11-11/mobile_apps/ALADDIN_iOS/Core/Analytics/RemoteAnalyticsService.swift`

- L65: `vpnStats: fallback?.vpnStats ?? AnalyticsVPNStats(today: "—", week: "—", protection: "—")`

### `ARCHIVE_ONLY_DO_NOT_EDIT_2025-11-11/mobile_apps/ALADDIN_iOS/Screens/25_PaymentQRScreen.swift`

- L62: `guard let date else { return "—" }`

### `BACKUP_MOBILE_20251108_1800/Core/Localization/LocalizationManager.swift`

- L225: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L643: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1938: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2142: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2448: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_MOBILE_20251108_1800/Core/Localization/LocalizationManager_backup_20251107.swift`

- L173: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L351: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L1725: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2031: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_MOBILE_20251108_1800/Core/LocalizationManager.swift`

- L225: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L643: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1932: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2136: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2442: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_MOBILE_20251108_1800/Core/Navigation/NavigationManager.swift`

- L228: `appendLog("❗️ goBack: PaymentQR без тарифа и пустой стек — возвращаемся к Tariffs")`
- L287: `appendLog("⚠️ goBack: lastScreenBeforePaymentQR отсутствует — используем Tariffs")`
- L317: `appendLog("⚠️ Стек пуст при PaymentQR — fallback на Tariffs")`
- L321: `appendLog("⬅️ Стек пуст — возврат на .main")`

### `BACKUP_MOBILE_20251108_1800/Screens/09_ElderlyInterfaceScreen.swift`

- L321: `: "Следующий приём: \(medications.first?.time ?? "—") (\(medications.first?.name ?? "—"))",`
- L332: `: "Следующий: \(appointments.first?.date ?? "—") (\(appointments.first?.doctor ?? "—"))",`

### `BACKUP_MOBILE_20260211_120559/Core/Localization/LocalizationManager.swift`

- L380: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L437: `"games_pet_description": "Тамагочи-питомец с индикаторами ❤️🍎⭐😊. Ребёнок кормит, играет, гладит. 4 стадии эволюции. Нельзя отключить — это о`
- L1165: `"family_status_critical_message": "Защита отключена — включите тариф для семьи",`
- L1562: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а защита сети — весь трафик устройства.",`
- L1944: `"network_protection_energy_comparison_row": "%@ — %.1f%%",`
- L1986: `"network_protection_help_antivirus_answer": "Антивирус отвечает за проверки и обнаружение угроз, а защита сети — за безопасное соединение.",`
- L3112: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L3114: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L3179: `"privacy_policy_section_auth_content_4": "Face ID: Данные лица НЕ собираются — приложение использует только встроенную функцию iOS для локал`
- L3180: `"privacy_policy_section_auth_content_5": "Face ID: Данные лица НЕ передаются третьим лицам — вся обработка происходит локально на устройстве`
- L3181: `"privacy_policy_section_auth_content_6": "Face ID: Данные лица НЕ хранятся на наших серверах — они остаются только на устройстве пользовател`
- L3974: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L4604: `"network_protection_energy_comparison_row": "%@ — %.1f%%",`
- L4864: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L4921: `"games_pet_description": "Tamagotchi-style pet with ❤️🍎⭐😊 indicators. Kids feed, play, and pet it. 4 evolution stages. Can't be disabled — i`
- L5816: `"family_header_accessibility": "ALADDIN Family — Family Protection",`
- L7205: `"privacy_policy_section_auth_content_4": "Face ID: Face data is NOT collected — the app uses only the built-in iOS function for local authen`
- L7206: `"privacy_policy_section_auth_content_5": "Face ID: Face data is NOT shared with third parties — all processing occurs locally on the device `
- L7207: `"privacy_policy_section_auth_content_6": "Face ID: Face data is NOT stored on our servers — it remains only on the user's device and is dele`
- L8093: `"family_status_critical_message": "Protection disabled — enable family tariff",`

### `BACKUP_MOBILE_20260211_120559/Core/Localization/LocalizationManager_backup_20251107.swift`

- L173: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L351: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L1725: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2031: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_MOBILE_20260211_120559/Core/Localization/LocalizationManager_backup_20251109.swift`

- L227: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L664: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1991: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2197: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2511: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_MOBILE_20260211_120559/Core/Localization/LocalizationManager_backup_20251110_2015.swift`

- L230: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L666: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1323: `"faq_what_protects_answer": "ALADDIN protects you from 100+ types of online dangers. Think of it as a guard for your phone—it keeps the bad `
- L1327: `"faq_protect_elderly_answer": "We built a special shield for grandparents:\n\n• We block scam calls (fraudsters target seniors first)\n• We `
- L1347: `"faq_social_engineering_answer": "Social engineering is when a fraudster tricks you with words instead of hacking.\n\nExamples:\n• \"I'm you`
- L1377: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1379: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L1383: `"faq_how_vpn_works_answer": "VPN acts like an underground tunnel. When you're online:\n• Normally: Your phone → Provider → Internet (everyon`
- L1387: `"faq_cancel_subscription_answer": "Easy! 😊\n\n1. Open \"Settings\"\n2. Find \"Manage subscription\"\n3. Tap \"Cancel subscription\"\n\nOr me`
- L1389: `"faq_phishing_emails_answer": "A phishing email is a deceptive message that pushes you to do something risky:\n• \"Your account is blocked, `
- L1981: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2179: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2485: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_MOBILE_20260211_120559/Core/Localization/LocalizationManager_backup_20251110_2145.swift`

- L230: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L682: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1366: `"faq_what_protects_answer": "ALADDIN защищает от 100+ видов опасностей в интернете. Это как сторож для твоего телефона — он не пускает плохи`
- L1370: `"faq_protect_elderly_answer": "Для бабушек и дедушек мы сделали специальную защиту:\n\n• Блокируем звонки от мошенников (они часто звонят по`
- L1372: `"faq_data_safe_answer": "Да, ваши данные полностью защищены! 🔒\n\nМы используем:\n• Военное шифрование (как в банках и армии)\n• Хранение да`
- L1374: `"faq_viruses_trojans_answer": "Вирус в телефоне — это как простуда для компьютера. Он может:\n• Удалить ваши фотографии\n• Украсть пароли\n•`
- L1378: `"faq_spyware_answer": "Шпион — невидимое приложение, которое следит за вами:\n• Видит пароли\n• Читает сообщения\n• Отслеживает местоположен`
- L1380: `"faq_phishing_sites_answer": "Фишинг — это поддельные сайты, похожие на настоящий банк или магазин.\n\nКак работает:\n1. Думаете, что зашли `
- L1382: `"faq_fake_apps_answer": "Поддельное приложение — как фальшивый телефон: выглядит как настоящее, но обманывает.\n\nМошенники создают:\n• Ложн`
- L1384: `"faq_malicious_links_answer": "Вредоносная ссылка — дверь в ловушку. Нажмёте — и попадёте в опасную зону!\n\nГде встречаются:\n• В сообщения`
- L1390: `"faq_social_engineering_answer": "Социальная инженерия — это когда вас обманывают словами, а не взломом.\n\nПримеры:\n• «Я ваш новый коллега`
- L1392: `"faq_fake_banks_answer": "Поддельный банк — это сайт-клон, который крадёт ваши данные.\n\nКак отличить:\n• Настоящий адрес: sberbank.ru\n• П`
- L1394: `"faq_inappropriate_content_answer": "Неподходящий контент — то, что дети не должны видеть:\n• Страшные видео\n• Взрослые сайты\n• Жестокие и`
- L1396: `"faq_cyberbullying_answer": "Кибербуллинг — когда детей травят в интернете:\n• Оскорбляют в чатах\n• Выкладывают обидные фото\n• Угрожают\n•`
- L1398: `"faq_dangerous_contacts_answer": "Опасные знакомства — когда взрослый пытается подружиться с ребёнком:\n• «Привет! Давай дружить»\n• «Ты так`
- L1400: `"faq_password_theft_answer": "Кража паролей — это когда мошенники узнают ваш пароль и входят в аккаунты:\n• Крадут деньги\n• Читают сообщени`
- L1402: `"faq_fake_voices_answer": "Поддельный голос — это когда компьютер копирует голос человека:\n• Мошенник звонит и говорит голосом вашего ребён`
- L1404: `"faq_fake_news_answer": "Фейковые новости — это ложная информация, выдаваемая за правду:\n• «Учёные нашли лекарство от всех болезней!»\n• «З`
- L1406: `"faq_unsafe_wifi_answer": "Небезопасный Wi‑Fi — публичная сеть-ловушка:\n• В кафе, аэропортах, метро\n• Мошенники могут перехватить ваши дан`
- L1408: `"faq_mitm_attacks_answer": "Man-in-the-middle — когда мошенник встаёт между вами и сервисом:\n1. Вы думаете, что общаетесь с банком\n2. На с`
- L1412: `"faq_sms_scam_answer": "SMS-мошенничество — это обманные сообщения:\n• «Вы выиграли! Переведите деньги для получения приза»\n• «Счёт заблоки`
- L1416: `"faq_domestic_violence_answer": "Цифровое домашнее насилие — когда близкий человек контролирует другого через интернет:\n• Читает все сообще`
- L1420: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1422: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L1424: `"faq_critical_infrastructure_answer": "Критическая инфраструктура — это важнейшие системы:\n• Больницы\n• Электростанции\n• Водоснабжение\n•`
- L1426: `"faq_how_vpn_works_answer": "VPN — это как подземный тоннель. Когда вы в интернете:\n• Обычно: телефон → провайдер → интернет (все видят, ку`
- L1430: `"faq_cancel_subscription_answer": "Легко! 😊\n\n1. Откройте «Настройки»\n2. Найдите «Управление подпиской»\n3. Нажмите «Отменить подписку»\n\`
- L1432: `"faq_phishing_emails_answer": "Фишинговое письмо — это обманное сообщение, заставляющее сделать что-то опасное:\n• «Ваш аккаунт заблокирован`
- L1436: `"faq_suspicious_downloads_answer": "Подозрительная загрузка — это файл, который может навредить:\n• Приложение с вирусом\n• Фото с вредоносн`
- L2032: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2230: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2552: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_MOBILE_20260211_120559/Core/Localization/LocalizationManager_backup_20251110_2152.swift`

- L230: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L682: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1366: `"faq_what_protects_answer": "ALADDIN защищает от 100+ видов опасностей в интернете. Это как сторож для твоего телефона — он не пускает плохи`
- L1370: `"faq_protect_elderly_answer": "Для бабушек и дедушек мы сделали специальную защиту:\n\n• Блокируем звонки от мошенников (они часто звонят по`
- L1372: `"faq_data_safe_answer": "Да, ваши данные полностью защищены! 🔒\n\nМы используем:\n• Военное шифрование (как в банках и армии)\n• Хранение да`
- L1374: `"faq_viruses_trojans_answer": "Вирус в телефоне — это как простуда для компьютера. Он может:\n• Удалить ваши фотографии\n• Украсть пароли\n•`
- L1378: `"faq_spyware_answer": "Шпион — невидимое приложение, которое следит за вами:\n• Видит пароли\n• Читает сообщения\n• Отслеживает местоположен`
- L1380: `"faq_phishing_sites_answer": "Фишинг — это поддельные сайты, похожие на настоящий банк или магазин.\n\nКак работает:\n1. Думаете, что зашли `
- L1382: `"faq_fake_apps_answer": "Поддельное приложение — как фальшивый телефон: выглядит как настоящее, но обманывает.\n\nМошенники создают:\n• Ложн`
- L1384: `"faq_malicious_links_answer": "Вредоносная ссылка — дверь в ловушку. Нажмёте — и попадёте в опасную зону!\n\nГде встречаются:\n• В сообщения`
- L1390: `"faq_social_engineering_answer": "Социальная инженерия — это когда вас обманывают словами, а не взломом.\n\nПримеры:\n• «Я ваш новый коллега`
- L1392: `"faq_fake_banks_answer": "Поддельный банк — это сайт-клон, который крадёт ваши данные.\n\nКак отличить:\n• Настоящий адрес: sberbank.ru\n• П`
- L1394: `"faq_inappropriate_content_answer": "Неподходящий контент — то, что дети не должны видеть:\n• Страшные видео\n• Взрослые сайты\n• Жестокие и`
- L1396: `"faq_cyberbullying_answer": "Кибербуллинг — когда детей травят в интернете:\n• Оскорбляют в чатах\n• Выкладывают обидные фото\n• Угрожают\n•`
- L1398: `"faq_dangerous_contacts_answer": "Опасные знакомства — когда взрослый пытается подружиться с ребёнком:\n• «Привет! Давай дружить»\n• «Ты так`
- L1400: `"faq_password_theft_answer": "Кража паролей — это когда мошенники узнают ваш пароль и входят в аккаунты:\n• Крадут деньги\n• Читают сообщени`
- L1402: `"faq_fake_voices_answer": "Поддельный голос — это когда компьютер копирует голос человека:\n• Мошенник звонит и говорит голосом вашего ребён`
- L1404: `"faq_fake_news_answer": "Фейковые новости — это ложная информация, выдаваемая за правду:\n• «Учёные нашли лекарство от всех болезней!»\n• «З`
- L1406: `"faq_unsafe_wifi_answer": "Небезопасный Wi‑Fi — публичная сеть-ловушка:\n• В кафе, аэропортах, метро\n• Мошенники могут перехватить ваши дан`
- L1408: `"faq_mitm_attacks_answer": "Man-in-the-middle — когда мошенник встаёт между вами и сервисом:\n1. Вы думаете, что общаетесь с банком\n2. На с`
- L1412: `"faq_sms_scam_answer": "SMS-мошенничество — это обманные сообщения:\n• «Вы выиграли! Переведите деньги для получения приза»\n• «Счёт заблоки`
- L1416: `"faq_domestic_violence_answer": "Цифровое домашнее насилие — когда близкий человек контролирует другого через интернет:\n• Читает все сообще`
- L1420: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1422: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L1424: `"faq_critical_infrastructure_answer": "Критическая инфраструктура — это важнейшие системы:\n• Больницы\n• Электростанции\n• Водоснабжение\n•`
- L1426: `"faq_how_vpn_works_answer": "VPN — это как подземный тоннель. Когда вы в интернете:\n• Обычно: телефон → провайдер → интернет (все видят, ку`
- L1430: `"faq_cancel_subscription_answer": "Легко! 😊\n\n1. Откройте «Настройки»\n2. Найдите «Управление подпиской»\n3. Нажмите «Отменить подписку»\n\`
- L1432: `"faq_phishing_emails_answer": "Фишинговое письмо — это обманное сообщение, заставляющее сделать что-то опасное:\n• «Ваш аккаунт заблокирован`
- L1436: `"faq_suspicious_downloads_answer": "Подозрительная загрузка — это файл, который может навредить:\n• Приложение с вирусом\n• Фото с вредоносн`
- L2032: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2230: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2552: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_MOBILE_20260211_120559/Core/Localization/LocalizationManager_backup_20251110_2215.swift`

- L230: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L687: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1395: `"faq_what_protects_answer": "ALADDIN защищает от 100+ видов опасностей в интернете. Это как сторож для твоего телефона — он не пускает плохи`
- L1399: `"faq_protect_elderly_answer": "Для бабушек и дедушек мы сделали специальную защиту:\n\n• Блокируем звонки от мошенников (они часто звонят по`
- L1401: `"faq_data_safe_answer": "Да, ваши данные полностью защищены! 🔒\n\nМы используем:\n• Военное шифрование (как в банках и армии)\n• Хранение да`
- L1403: `"faq_viruses_trojans_answer": "Вирус в телефоне — это как простуда для компьютера. Он может:\n• Удалить ваши фотографии\n• Украсть пароли\n•`
- L1407: `"faq_spyware_answer": "Шпион — невидимое приложение, которое следит за вами:\n• Видит пароли\n• Читает сообщения\n• Отслеживает местоположен`
- L1409: `"faq_phishing_sites_answer": "Фишинг — это поддельные сайты, похожие на настоящий банк или магазин.\n\nКак работает:\n1. Думаете, что зашли `
- L1411: `"faq_fake_apps_answer": "Поддельное приложение — как фальшивый телефон: выглядит как настоящее, но обманывает.\n\nМошенники создают:\n• Ложн`
- L1413: `"faq_malicious_links_answer": "Вредоносная ссылка — дверь в ловушку. Нажмёте — и попадёте в опасную зону!\n\nГде встречаются:\n• В сообщения`
- L1419: `"faq_social_engineering_answer": "Социальная инженерия — это когда вас обманывают словами, а не взломом.\n\nПримеры:\n• «Я ваш новый коллега`
- L1421: `"faq_fake_banks_answer": "Поддельный банк — это сайт-клон, который крадёт ваши данные.\n\nКак отличить:\n• Настоящий адрес: sberbank.ru\n• П`
- L1423: `"faq_inappropriate_content_answer": "Неподходящий контент — то, что дети не должны видеть:\n• Страшные видео\n• Взрослые сайты\n• Жестокие и`
- L1425: `"faq_cyberbullying_answer": "Кибербуллинг — когда детей травят в интернете:\n• Оскорбляют в чатах\n• Выкладывают обидные фото\n• Угрожают\n•`
- L1427: `"faq_dangerous_contacts_answer": "Опасные знакомства — когда взрослый пытается подружиться с ребёнком:\n• «Привет! Давай дружить»\n• «Ты так`
- L1429: `"faq_password_theft_answer": "Кража паролей — это когда мошенники узнают ваш пароль и входят в аккаунты:\n• Крадут деньги\n• Читают сообщени`
- L1431: `"faq_fake_voices_answer": "Поддельный голос — это когда компьютер копирует голос человека:\n• Мошенник звонит и говорит голосом вашего ребён`
- L1433: `"faq_fake_news_answer": "Фейковые новости — это ложная информация, выдаваемая за правду:\n• «Учёные нашли лекарство от всех болезней!»\n• «З`
- L1435: `"faq_unsafe_wifi_answer": "Небезопасный Wi‑Fi — публичная сеть-ловушка:\n• В кафе, аэропортах, метро\n• Мошенники могут перехватить ваши дан`
- L1437: `"faq_mitm_attacks_answer": "Man-in-the-middle — когда мошенник встаёт между вами и сервисом:\n1. Вы думаете, что общаетесь с банком\n2. На с`
- L1441: `"faq_sms_scam_answer": "SMS-мошенничество — это обманные сообщения:\n• «Вы выиграли! Переведите деньги для получения приза»\n• «Счёт заблоки`
- L1445: `"faq_domestic_violence_answer": "Цифровое домашнее насилие — когда близкий человек контролирует другого через интернет:\n• Читает все сообще`
- L1449: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1451: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L1453: `"faq_critical_infrastructure_answer": "Критическая инфраструктура — это важнейшие системы:\n• Больницы\n• Электростанции\n• Водоснабжение\n•`
- L1455: `"faq_how_vpn_works_answer": "VPN — это как подземный тоннель. Когда вы в интернете:\n• Обычно: телефон → провайдер → интернет (все видят, ку`
- L1459: `"faq_cancel_subscription_answer": "Легко! 😊\n\n1. Откройте «Настройки»\n2. Найдите «Управление подпиской»\n3. Нажмите «Отменить подписку»\n\`
- L1461: `"faq_phishing_emails_answer": "Фишинговое письмо — это обманное сообщение, заставляющее сделать что-то опасное:\n• «Ваш аккаунт заблокирован`
- L1465: `"faq_suspicious_downloads_answer": "Подозрительная загрузка — это файл, который может навредить:\n• Приложение с вирусом\n• Фото с вредоносн`
- L2061: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2259: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2586: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_MOBILE_20260211_120559/Core/Localization/LocalizationManager_backup_20251110_2250.swift`

- L230: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L694: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1433: `"faq_what_protects_answer": "ALADDIN защищает от 100+ видов опасностей в интернете. Это как сторож для твоего телефона — он не пускает плохи`
- L1437: `"faq_protect_elderly_answer": "Для бабушек и дедушек мы сделали специальную защиту:\n\n• Блокируем звонки от мошенников (они часто звонят по`
- L1439: `"faq_data_safe_answer": "Да, ваши данные полностью защищены! 🔒\n\nМы используем:\n• Военное шифрование (как в банках и армии)\n• Хранение да`
- L1441: `"faq_viruses_trojans_answer": "Вирус в телефоне — это как простуда для компьютера. Он может:\n• Удалить ваши фотографии\n• Украсть пароли\n•`
- L1445: `"faq_spyware_answer": "Шпион — невидимое приложение, которое следит за вами:\n• Видит пароли\n• Читает сообщения\n• Отслеживает местоположен`
- L1447: `"faq_phishing_sites_answer": "Фишинг — это поддельные сайты, похожие на настоящий банк или магазин.\n\nКак работает:\n1. Думаете, что зашли `
- L1449: `"faq_fake_apps_answer": "Поддельное приложение — как фальшивый телефон: выглядит как настоящее, но обманывает.\n\nМошенники создают:\n• Ложн`
- L1451: `"faq_malicious_links_answer": "Вредоносная ссылка — дверь в ловушку. Нажмёте — и попадёте в опасную зону!\n\nГде встречаются:\n• В сообщения`
- L1457: `"faq_social_engineering_answer": "Социальная инженерия — это когда вас обманывают словами, а не взломом.\n\nПримеры:\n• «Я ваш новый коллега`
- L1459: `"faq_fake_banks_answer": "Поддельный банк — это сайт-клон, который крадёт ваши данные.\n\nКак отличить:\n• Настоящий адрес: sberbank.ru\n• П`
- L1461: `"faq_inappropriate_content_answer": "Неподходящий контент — то, что дети не должны видеть:\n• Страшные видео\n• Взрослые сайты\n• Жестокие и`
- L1463: `"faq_cyberbullying_answer": "Кибербуллинг — когда детей травят в интернете:\n• Оскорбляют в чатах\n• Выкладывают обидные фото\n• Угрожают\n•`
- L1465: `"faq_dangerous_contacts_answer": "Опасные знакомства — когда взрослый пытается подружиться с ребёнком:\n• «Привет! Давай дружить»\n• «Ты так`
- L1467: `"faq_password_theft_answer": "Кража паролей — это когда мошенники узнают ваш пароль и входят в аккаунты:\n• Крадут деньги\n• Читают сообщени`
- L1469: `"faq_fake_voices_answer": "Поддельный голос — это когда компьютер копирует голос человека:\n• Мошенник звонит и говорит голосом вашего ребён`
- L1471: `"faq_fake_news_answer": "Фейковые новости — это ложная информация, выдаваемая за правду:\n• «Учёные нашли лекарство от всех болезней!»\n• «З`
- L1473: `"faq_unsafe_wifi_answer": "Небезопасный Wi‑Fi — публичная сеть-ловушка:\n• В кафе, аэропортах, метро\n• Мошенники могут перехватить ваши дан`
- L1475: `"faq_mitm_attacks_answer": "Man-in-the-middle — когда мошенник встаёт между вами и сервисом:\n1. Вы думаете, что общаетесь с банком\n2. На с`
- L1479: `"faq_sms_scam_answer": "SMS-мошенничество — это обманные сообщения:\n• «Вы выиграли! Переведите деньги для получения приза»\n• «Счёт заблоки`
- L1483: `"faq_domestic_violence_answer": "Цифровое домашнее насилие — когда близкий человек контролирует другого через интернет:\n• Читает все сообще`
- L1487: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1489: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L1491: `"faq_critical_infrastructure_answer": "Критическая инфраструктура — это важнейшие системы:\n• Больницы\n• Электростанции\n• Водоснабжение\n•`
- L1493: `"faq_how_vpn_works_answer": "VPN — это как подземный тоннель. Когда вы в интернете:\n• Обычно: телефон → провайдер → интернет (все видят, ку`
- L1497: `"faq_cancel_subscription_answer": "Легко! 😊\n\n1. Откройте «Настройки»\n2. Найдите «Управление подпиской»\n3. Нажмите «Отменить подписку»\n\`
- L1499: `"faq_phishing_emails_answer": "Фишинговое письмо — это обманное сообщение, заставляющее сделать что-то опасное:\n• «Ваш аккаунт заблокирован`
- L1503: `"faq_suspicious_downloads_answer": "Подозрительная загрузка — это файл, который может навредить:\n• Приложение с вирусом\n• Фото с вредоносн`
- L2099: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2297: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2631: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_MOBILE_20260211_120559/Core/Localization/LocalizationManager_backup_20251121.swift`

- L237: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L422: `"family_status_critical_message": "Защита отключена — включите тариф для семьи",`
- L748: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1115: `"tariffs_free_features_1": "VPN Базовый — с ограниченной скоростью и количеством мб трафика",`
- L1121: `"tariffs_personal_features_1": "VPN Pro — безлимитная скорость",`
- L1127: `"tariffs_family_features_1": "VPN Ultra — безлимитная скорость",`
- L1656: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1658: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L2268: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2465: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2837: `"family_header_accessibility": "ALADDIN Family — Family Protection",`
- L3419: `"tariffs_free_features_1": "Basic VPN — limited speed and data traffic",`
- L3425: `"tariffs_personal_features_1": "VPN Pro — unlimited speed",`
- L3431: `"tariffs_family_features_1": "VPN Ultra — unlimited speed",`
- L4378: `"family_status_critical_message": "Protection disabled — enable family tariff",`

### `BACKUP_MOBILE_20260211_120559/Core/Navigation/NavigationManager.swift`

- L242: `appendLog("❗️ goBack: PaymentQR без тарифа и пустой стек — возвращаемся к Tariffs")`
- L301: `appendLog("⚠️ goBack: lastScreenBeforePaymentQR отсутствует — используем Tariffs")`
- L331: `appendLog("⚠️ Стек пуст при PaymentQR — fallback на Tariffs")`
- L335: `appendLog("⬅️ Стек пуст — возврат на .main")`

### `BACKUP_MOBILE_20260211_120559/Screens/09_ElderlyInterfaceScreen.swift`

- L341: `: String(format: localizationManager.localized("elderly_medications_next_dose"), medications.first?.time ?? "—", medications.first?.name ?? `
- L352: `: String(format: localizationManager.localized("elderly_appointments_next"), appointments.first?.date ?? "—", appointments.first?.doctor ?? `

### `BACKUP_MOBILE_20260211_120559/Screens/18_PrivacyPolicyScreen.swift`

- L651: `"Face ID: Данные лица НЕ собираются — приложение использует только встроенную функцию iOS для локальной аутентификации",`
- L652: `"Face ID: Данные лица НЕ передаются третьим лицам — вся обработка происходит локально на устройстве в Secure Enclave",`
- L653: `"Face ID: Данные лица НЕ хранятся на наших серверах — они остаются только на устройстве пользователя и удаляются при удалении приложения"`

### `BACKUP_MOBILE_20260211_120559/Shared/Components/Modals/PrivacyReportsModal.swift`

- L309: `Text("—")`

### `BACKUP_SCREENS_20251104_141022/14_OnboardingScreen.swift`

- L67: `description: "Один клик — помощь рядом. Определение поддельных видео, поддельного голоса, фейковых звонков и номеров!",`
- L74: `description: "Спокойствие за близких — бесценно. Защита начинается сегодня!",`

### `BACKUP_SCREENS_20251106_132406/Screens/09_ElderlyInterfaceScreen.swift`

- L321: `: "Следующий приём: \(medications.first?.time ?? "—") (\(medications.first?.name ?? "—"))",`
- L332: `: "Следующий: \(appointments.first?.date ?? "—") (\(appointments.first?.doctor ?? "—"))",`

### `BACKUP_SCREENS_20251108_202630/Core/LocalizationManager.swift`

- L225: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L643: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1938: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2142: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2448: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `BACKUP_SCREENS_20251108_202630/Core/NavigationManager.swift`

- L228: `appendLog("❗️ goBack: PaymentQR без тарифа и пустой стек — возвращаемся к Tariffs")`
- L287: `appendLog("⚠️ goBack: lastScreenBeforePaymentQR отсутствует — используем Tariffs")`
- L317: `appendLog("⚠️ Стек пуст при PaymentQR — fallback на Tariffs")`
- L321: `appendLog("⬅️ Стек пуст — возврат на .main")`

### `Core/Audio/SpeechManager.swift`

- L140: `logger.warn("🎤 SpeechManager: Already recording — ignoring duplicate start")`
- L323: `logger.warn("🎤 SpeechManager: Empty cloud transcript after audio signal — retrying on-device path")`
- L332: `logger.warn("🎤 SpeechManager: Empty transcript after audio signal — retrying cloud path")`
- L429: `logger.business("🎤 SpeechManager: Using recognizer \(speechRecognizer.locale.identifier), mode=\(modeLabel) [Simulator — cloud only]")`
- L457: `logger.error("🎤 SpeechManager: Invalid input tap format — cannot start recording")`
- L461: `logger.warn("🎤 SpeechManager: Tap already installed — skipping duplicate install")`
- L536: `self.logger.warn("🎤 SpeechManager: Siri Retry — switching to cloud path")`
- L544: `self.logger.warn("🎤 SpeechManager: On-device model missing — retrying cloud path")`
- L555: `self.logger.warn("🎤 SpeechManager: Siri cloud unavailable (1107) — retrying on-device path")`
- L670: `self.logger.warn("🎤 SpeechManager: Max duration reached — auto stop")`
- L760: `logger.warn("🎤 SpeechManager: Audio session interrupted — stopping")`

### `Core/E2EE/FamilyE2EEManager.swift`

- L262: `"E2EE key not available yet — open Family Chat on another family device first"`

### `Core/Family/SystemContentFilterRulesStore.swift`

- L88: `"⚠️ SYSTEM_FILTER simulator — NEFilterManager not supported",`

### `Core/Localization/LocalizationManager.swift`

- L305: `"analytics_trial_mode_notice": "Пробный период использует лимиты выбранного тарифа. Ниже — только статистика работы защиты за период.",`
- L307: `"analytics_protection_level_no_events": "За период не было зафиксированных угроз — доля «заблокировано от обнаруженных» не считается, поэтом`
- L358: `"companion_friends_hint": "Поговорить с героями — Единорог, Аладдин и Джин",`
- L367: `"companion_mic_coach_step3": "3. Отпусти — герой ответит",`
- L378: `"companion_dialogue_empty": "Скажи или напиши — я рядом.",`
- L406: `"companion_mine_cogs_alert": "Порог $%.2f — проверьте использование",`
- L421: `"companion_humor_hint_unicorn": "Тёплые шутки иногда — в безопасном PG-стиле.",`
- L423: `"companion_humor_hint_genie": "Джин — больше шуток и игры слов, но не в каждом ответе.",`
- L463: `"companion_teen_humor_subtitle": "Можно попросить героя шутить реже — поддержка и эмпатия останутся.",`
- L467: `"companion_heroes_one_pager_intro": "Три AI-друга для разных настроений. Все ответы — ИИ, не живой человек. При тревоге — обратись к взросло`
- L468: `"companion_heroes_one_pager_unicorn": "Единорог — тёплый друг для детей: сказка, школа, друзья, эмоции. Без сарказма.",`
- L469: `"companion_heroes_one_pager_aladdin": "Аладдин — спокойный наставник: мудрость простыми словами, иногда сухой wit. Без религии в ответах.",`
- L470: `"companion_heroes_one_pager_genie": "Джин — больше юмора и игры слов, но не в каждом сообщении. При грусти — только поддержка.",`
- L489: `"companion_social_bridge_body": "Если хочешь — напиши маме, папе или другу. Герой всегда рядом, но живое общение тоже важно.",`
- L502: `"companion_break_steps_water_blocked": "Для привычки «вода» шаги без награды Единорога — отметьте Done в напоминании.",`
- L581: `"companion_legal_offline_coppa_body": "Обработка данных детей — с согласия законного представителя (152-ФЗ). Мы не используем данные ребёнка`
- L587: `"companion_legal_offline_voice_fallback_body": "Если на устройстве текст получить не удалось, приложение может один раз отправить короткую з`
- L589: `"companion_legal_offline_voice_brief_body": "• Основной путь: Apple (Siri cloud) на телефоне.\n• Запасной путь: ALADDIN VPS — только если Ap`
- L597: `"companion_legal_offline_wellness_body": "Раздел настроения — для самопомощи. Он не заменяет врача и экстренную помощь.",`
- L636: `"wellness_hub_non_medical_banner": "Это не медицина и не диагноз — только поддержка для самопомощи. В острой ситуации обратитесь за срочной `
- L645: `"wellness_pillar_jung_subtitle": "Сны и символы — без ярлыков",`
- L647: `"wellness_pillar_cognitive_subtitle_b": "Один шаг — отделить факт от тревоги",`
- L651: `"wellness_pillar_humanistic_subtitle_b": "Без советов — просто поддержка",`
- L660: `"wellness_family_themes_empty": "Пока нет заметных тем — это нормально.",`
- L673: `"wellness_consent_body": "ALADDIN — цифровой друг для самопомощи. Это не медицинский сервис и не заменяет психолога или врача. Опросники — с`
- L674: `"wellness_consent_jung_note": "«Понять себя» и сны — метафоры для размышления, не предсказания.",`
- L709: `"wellness_sleep_stories_offline_hint": "Сказки на устройстве — без интернета.",`
- L729: `"wellness_teen_phq_parent_aggregate_hint": "Родитель видит только сводку настроения, если включён переключатель выше — не переписку.",`
- L740: `"wellness_exam_started": "Экзамен уже начался — ты справишься!",`
- L742: `"wellness_exam_phase_day_before": "Завтра важный день — отдохни сегодня",`
- L743: `"wellness_exam_phase_final_5min": "5 минут до старта — дыши спокойно",`
- L747: `"wellness_exam_one_thing_cta": "Одно дело — 5 мин",`
- L752: `"wellness_one_thing_intro": "Выбери одно маленькое дело на 5 минут — без отвлечений.",`
- L756: `"wellness_one_thing_done": "Готово! Маленький шаг — это победа.",`
- L758: `"wellness_one_thing_hub_cta": "5 мин — одно дело",`
- L767: `"wellness_together_offline_local": "Без сети — локальный таймер дыхания 3 мин.",`
- L772: `"notification_help_subtitle": "Если тумблер включён, но пуш тихий — чаще всего Quiet / Только важные / DND или нет разрешения iOS.",`
- L775: `"notification_help_check_important": "Только важные — выключен",`
- L776: `"notification_help_check_quiet": "Тихие часы — выключены",`
- L777: `"notification_help_check_quiet_mode": "Тихий режим — выключен",`
- … ещё 742

### `Core/Localization/LocalizationManager_backup_20251107.swift`

- L173: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L351: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L1725: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2031: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `Core/Localization/LocalizationManager_backup_20251109.swift`

- L227: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L664: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1991: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2197: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2511: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `Core/Localization/LocalizationManager_backup_20251110_2015.swift`

- L230: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L666: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1323: `"faq_what_protects_answer": "ALADDIN protects you from 100+ types of online dangers. Think of it as a guard for your phone—it keeps the bad `
- L1327: `"faq_protect_elderly_answer": "We built a special shield for grandparents:\n\n• We block scam calls (fraudsters target seniors first)\n• We `
- L1347: `"faq_social_engineering_answer": "Social engineering is when a fraudster tricks you with words instead of hacking.\n\nExamples:\n• \"I'm you`
- L1377: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1379: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L1383: `"faq_how_vpn_works_answer": "VPN acts like an underground tunnel. When you're online:\n• Normally: Your phone → Provider → Internet (everyon`
- L1387: `"faq_cancel_subscription_answer": "Easy! 😊\n\n1. Open \"Settings\"\n2. Find \"Manage subscription\"\n3. Tap \"Cancel subscription\"\n\nOr me`
- L1389: `"faq_phishing_emails_answer": "A phishing email is a deceptive message that pushes you to do something risky:\n• \"Your account is blocked, `
- L1981: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2179: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2485: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `Core/Localization/LocalizationManager_backup_20251110_2145.swift`

- L230: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L682: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1366: `"faq_what_protects_answer": "ALADDIN защищает от 100+ видов опасностей в интернете. Это как сторож для твоего телефона — он не пускает плохи`
- L1370: `"faq_protect_elderly_answer": "Для бабушек и дедушек мы сделали специальную защиту:\n\n• Блокируем звонки от мошенников (они часто звонят по`
- L1372: `"faq_data_safe_answer": "Да, ваши данные полностью защищены! 🔒\n\nМы используем:\n• Военное шифрование (как в банках и армии)\n• Хранение да`
- L1374: `"faq_viruses_trojans_answer": "Вирус в телефоне — это как простуда для компьютера. Он может:\n• Удалить ваши фотографии\n• Украсть пароли\n•`
- L1378: `"faq_spyware_answer": "Шпион — невидимое приложение, которое следит за вами:\n• Видит пароли\n• Читает сообщения\n• Отслеживает местоположен`
- L1380: `"faq_phishing_sites_answer": "Фишинг — это поддельные сайты, похожие на настоящий банк или магазин.\n\nКак работает:\n1. Думаете, что зашли `
- L1382: `"faq_fake_apps_answer": "Поддельное приложение — как фальшивый телефон: выглядит как настоящее, но обманывает.\n\nМошенники создают:\n• Ложн`
- L1384: `"faq_malicious_links_answer": "Вредоносная ссылка — дверь в ловушку. Нажмёте — и попадёте в опасную зону!\n\nГде встречаются:\n• В сообщения`
- L1390: `"faq_social_engineering_answer": "Социальная инженерия — это когда вас обманывают словами, а не взломом.\n\nПримеры:\n• «Я ваш новый коллега`
- L1392: `"faq_fake_banks_answer": "Поддельный банк — это сайт-клон, который крадёт ваши данные.\n\nКак отличить:\n• Настоящий адрес: sberbank.ru\n• П`
- L1394: `"faq_inappropriate_content_answer": "Неподходящий контент — то, что дети не должны видеть:\n• Страшные видео\n• Взрослые сайты\n• Жестокие и`
- L1396: `"faq_cyberbullying_answer": "Кибербуллинг — когда детей травят в интернете:\n• Оскорбляют в чатах\n• Выкладывают обидные фото\n• Угрожают\n•`
- L1398: `"faq_dangerous_contacts_answer": "Опасные знакомства — когда взрослый пытается подружиться с ребёнком:\n• «Привет! Давай дружить»\n• «Ты так`
- L1400: `"faq_password_theft_answer": "Кража паролей — это когда мошенники узнают ваш пароль и входят в аккаунты:\n• Крадут деньги\n• Читают сообщени`
- L1402: `"faq_fake_voices_answer": "Поддельный голос — это когда компьютер копирует голос человека:\n• Мошенник звонит и говорит голосом вашего ребён`
- L1404: `"faq_fake_news_answer": "Фейковые новости — это ложная информация, выдаваемая за правду:\n• «Учёные нашли лекарство от всех болезней!»\n• «З`
- L1406: `"faq_unsafe_wifi_answer": "Небезопасный Wi‑Fi — публичная сеть-ловушка:\n• В кафе, аэропортах, метро\n• Мошенники могут перехватить ваши дан`
- L1408: `"faq_mitm_attacks_answer": "Man-in-the-middle — когда мошенник встаёт между вами и сервисом:\n1. Вы думаете, что общаетесь с банком\n2. На с`
- L1412: `"faq_sms_scam_answer": "SMS-мошенничество — это обманные сообщения:\n• «Вы выиграли! Переведите деньги для получения приза»\n• «Счёт заблоки`
- L1416: `"faq_domestic_violence_answer": "Цифровое домашнее насилие — когда близкий человек контролирует другого через интернет:\n• Читает все сообще`
- L1420: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1422: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L1424: `"faq_critical_infrastructure_answer": "Критическая инфраструктура — это важнейшие системы:\n• Больницы\n• Электростанции\n• Водоснабжение\n•`
- L1426: `"faq_how_vpn_works_answer": "VPN — это как подземный тоннель. Когда вы в интернете:\n• Обычно: телефон → провайдер → интернет (все видят, ку`
- L1430: `"faq_cancel_subscription_answer": "Легко! 😊\n\n1. Откройте «Настройки»\n2. Найдите «Управление подпиской»\n3. Нажмите «Отменить подписку»\n\`
- L1432: `"faq_phishing_emails_answer": "Фишинговое письмо — это обманное сообщение, заставляющее сделать что-то опасное:\n• «Ваш аккаунт заблокирован`
- L1436: `"faq_suspicious_downloads_answer": "Подозрительная загрузка — это файл, который может навредить:\n• Приложение с вирусом\n• Фото с вредоносн`
- L2032: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2230: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2552: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `Core/Localization/LocalizationManager_backup_20251110_2152.swift`

- L230: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L682: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1366: `"faq_what_protects_answer": "ALADDIN защищает от 100+ видов опасностей в интернете. Это как сторож для твоего телефона — он не пускает плохи`
- L1370: `"faq_protect_elderly_answer": "Для бабушек и дедушек мы сделали специальную защиту:\n\n• Блокируем звонки от мошенников (они часто звонят по`
- L1372: `"faq_data_safe_answer": "Да, ваши данные полностью защищены! 🔒\n\nМы используем:\n• Военное шифрование (как в банках и армии)\n• Хранение да`
- L1374: `"faq_viruses_trojans_answer": "Вирус в телефоне — это как простуда для компьютера. Он может:\n• Удалить ваши фотографии\n• Украсть пароли\n•`
- L1378: `"faq_spyware_answer": "Шпион — невидимое приложение, которое следит за вами:\n• Видит пароли\n• Читает сообщения\n• Отслеживает местоположен`
- L1380: `"faq_phishing_sites_answer": "Фишинг — это поддельные сайты, похожие на настоящий банк или магазин.\n\nКак работает:\n1. Думаете, что зашли `
- L1382: `"faq_fake_apps_answer": "Поддельное приложение — как фальшивый телефон: выглядит как настоящее, но обманывает.\n\nМошенники создают:\n• Ложн`
- L1384: `"faq_malicious_links_answer": "Вредоносная ссылка — дверь в ловушку. Нажмёте — и попадёте в опасную зону!\n\nГде встречаются:\n• В сообщения`
- L1390: `"faq_social_engineering_answer": "Социальная инженерия — это когда вас обманывают словами, а не взломом.\n\nПримеры:\n• «Я ваш новый коллега`
- L1392: `"faq_fake_banks_answer": "Поддельный банк — это сайт-клон, который крадёт ваши данные.\n\nКак отличить:\n• Настоящий адрес: sberbank.ru\n• П`
- L1394: `"faq_inappropriate_content_answer": "Неподходящий контент — то, что дети не должны видеть:\n• Страшные видео\n• Взрослые сайты\n• Жестокие и`
- L1396: `"faq_cyberbullying_answer": "Кибербуллинг — когда детей травят в интернете:\n• Оскорбляют в чатах\n• Выкладывают обидные фото\n• Угрожают\n•`
- L1398: `"faq_dangerous_contacts_answer": "Опасные знакомства — когда взрослый пытается подружиться с ребёнком:\n• «Привет! Давай дружить»\n• «Ты так`
- L1400: `"faq_password_theft_answer": "Кража паролей — это когда мошенники узнают ваш пароль и входят в аккаунты:\n• Крадут деньги\n• Читают сообщени`
- L1402: `"faq_fake_voices_answer": "Поддельный голос — это когда компьютер копирует голос человека:\n• Мошенник звонит и говорит голосом вашего ребён`
- L1404: `"faq_fake_news_answer": "Фейковые новости — это ложная информация, выдаваемая за правду:\n• «Учёные нашли лекарство от всех болезней!»\n• «З`
- L1406: `"faq_unsafe_wifi_answer": "Небезопасный Wi‑Fi — публичная сеть-ловушка:\n• В кафе, аэропортах, метро\n• Мошенники могут перехватить ваши дан`
- L1408: `"faq_mitm_attacks_answer": "Man-in-the-middle — когда мошенник встаёт между вами и сервисом:\n1. Вы думаете, что общаетесь с банком\n2. На с`
- L1412: `"faq_sms_scam_answer": "SMS-мошенничество — это обманные сообщения:\n• «Вы выиграли! Переведите деньги для получения приза»\n• «Счёт заблоки`
- L1416: `"faq_domestic_violence_answer": "Цифровое домашнее насилие — когда близкий человек контролирует другого через интернет:\n• Читает все сообще`
- L1420: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1422: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L1424: `"faq_critical_infrastructure_answer": "Критическая инфраструктура — это важнейшие системы:\n• Больницы\n• Электростанции\n• Водоснабжение\n•`
- L1426: `"faq_how_vpn_works_answer": "VPN — это как подземный тоннель. Когда вы в интернете:\n• Обычно: телефон → провайдер → интернет (все видят, ку`
- L1430: `"faq_cancel_subscription_answer": "Легко! 😊\n\n1. Откройте «Настройки»\n2. Найдите «Управление подпиской»\n3. Нажмите «Отменить подписку»\n\`
- L1432: `"faq_phishing_emails_answer": "Фишинговое письмо — это обманное сообщение, заставляющее сделать что-то опасное:\n• «Ваш аккаунт заблокирован`
- L1436: `"faq_suspicious_downloads_answer": "Подозрительная загрузка — это файл, который может навредить:\n• Приложение с вирусом\n• Фото с вредоносн`
- L2032: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2230: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2552: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `Core/Localization/LocalizationManager_backup_20251110_2215.swift`

- L230: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L687: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1395: `"faq_what_protects_answer": "ALADDIN защищает от 100+ видов опасностей в интернете. Это как сторож для твоего телефона — он не пускает плохи`
- L1399: `"faq_protect_elderly_answer": "Для бабушек и дедушек мы сделали специальную защиту:\n\n• Блокируем звонки от мошенников (они часто звонят по`
- L1401: `"faq_data_safe_answer": "Да, ваши данные полностью защищены! 🔒\n\nМы используем:\n• Военное шифрование (как в банках и армии)\n• Хранение да`
- L1403: `"faq_viruses_trojans_answer": "Вирус в телефоне — это как простуда для компьютера. Он может:\n• Удалить ваши фотографии\n• Украсть пароли\n•`
- L1407: `"faq_spyware_answer": "Шпион — невидимое приложение, которое следит за вами:\n• Видит пароли\n• Читает сообщения\n• Отслеживает местоположен`
- L1409: `"faq_phishing_sites_answer": "Фишинг — это поддельные сайты, похожие на настоящий банк или магазин.\n\nКак работает:\n1. Думаете, что зашли `
- L1411: `"faq_fake_apps_answer": "Поддельное приложение — как фальшивый телефон: выглядит как настоящее, но обманывает.\n\nМошенники создают:\n• Ложн`
- L1413: `"faq_malicious_links_answer": "Вредоносная ссылка — дверь в ловушку. Нажмёте — и попадёте в опасную зону!\n\nГде встречаются:\n• В сообщения`
- L1419: `"faq_social_engineering_answer": "Социальная инженерия — это когда вас обманывают словами, а не взломом.\n\nПримеры:\n• «Я ваш новый коллега`
- L1421: `"faq_fake_banks_answer": "Поддельный банк — это сайт-клон, который крадёт ваши данные.\n\nКак отличить:\n• Настоящий адрес: sberbank.ru\n• П`
- L1423: `"faq_inappropriate_content_answer": "Неподходящий контент — то, что дети не должны видеть:\n• Страшные видео\n• Взрослые сайты\n• Жестокие и`
- L1425: `"faq_cyberbullying_answer": "Кибербуллинг — когда детей травят в интернете:\n• Оскорбляют в чатах\n• Выкладывают обидные фото\n• Угрожают\n•`
- L1427: `"faq_dangerous_contacts_answer": "Опасные знакомства — когда взрослый пытается подружиться с ребёнком:\n• «Привет! Давай дружить»\n• «Ты так`
- L1429: `"faq_password_theft_answer": "Кража паролей — это когда мошенники узнают ваш пароль и входят в аккаунты:\n• Крадут деньги\n• Читают сообщени`
- L1431: `"faq_fake_voices_answer": "Поддельный голос — это когда компьютер копирует голос человека:\n• Мошенник звонит и говорит голосом вашего ребён`
- L1433: `"faq_fake_news_answer": "Фейковые новости — это ложная информация, выдаваемая за правду:\n• «Учёные нашли лекарство от всех болезней!»\n• «З`
- L1435: `"faq_unsafe_wifi_answer": "Небезопасный Wi‑Fi — публичная сеть-ловушка:\n• В кафе, аэропортах, метро\n• Мошенники могут перехватить ваши дан`
- L1437: `"faq_mitm_attacks_answer": "Man-in-the-middle — когда мошенник встаёт между вами и сервисом:\n1. Вы думаете, что общаетесь с банком\n2. На с`
- L1441: `"faq_sms_scam_answer": "SMS-мошенничество — это обманные сообщения:\n• «Вы выиграли! Переведите деньги для получения приза»\n• «Счёт заблоки`
- L1445: `"faq_domestic_violence_answer": "Цифровое домашнее насилие — когда близкий человек контролирует другого через интернет:\n• Читает все сообще`
- L1449: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1451: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L1453: `"faq_critical_infrastructure_answer": "Критическая инфраструктура — это важнейшие системы:\n• Больницы\n• Электростанции\n• Водоснабжение\n•`
- L1455: `"faq_how_vpn_works_answer": "VPN — это как подземный тоннель. Когда вы в интернете:\n• Обычно: телефон → провайдер → интернет (все видят, ку`
- L1459: `"faq_cancel_subscription_answer": "Легко! 😊\n\n1. Откройте «Настройки»\n2. Найдите «Управление подпиской»\n3. Нажмите «Отменить подписку»\n\`
- L1461: `"faq_phishing_emails_answer": "Фишинговое письмо — это обманное сообщение, заставляющее сделать что-то опасное:\n• «Ваш аккаунт заблокирован`
- L1465: `"faq_suspicious_downloads_answer": "Подозрительная загрузка — это файл, который может навредить:\n• Приложение с вирусом\n• Фото с вредоносн`
- L2061: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2259: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2586: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `Core/Localization/LocalizationManager_backup_20251110_2250.swift`

- L230: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L694: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1433: `"faq_what_protects_answer": "ALADDIN защищает от 100+ видов опасностей в интернете. Это как сторож для твоего телефона — он не пускает плохи`
- L1437: `"faq_protect_elderly_answer": "Для бабушек и дедушек мы сделали специальную защиту:\n\n• Блокируем звонки от мошенников (они часто звонят по`
- L1439: `"faq_data_safe_answer": "Да, ваши данные полностью защищены! 🔒\n\nМы используем:\n• Военное шифрование (как в банках и армии)\n• Хранение да`
- L1441: `"faq_viruses_trojans_answer": "Вирус в телефоне — это как простуда для компьютера. Он может:\n• Удалить ваши фотографии\n• Украсть пароли\n•`
- L1445: `"faq_spyware_answer": "Шпион — невидимое приложение, которое следит за вами:\n• Видит пароли\n• Читает сообщения\n• Отслеживает местоположен`
- L1447: `"faq_phishing_sites_answer": "Фишинг — это поддельные сайты, похожие на настоящий банк или магазин.\n\nКак работает:\n1. Думаете, что зашли `
- L1449: `"faq_fake_apps_answer": "Поддельное приложение — как фальшивый телефон: выглядит как настоящее, но обманывает.\n\nМошенники создают:\n• Ложн`
- L1451: `"faq_malicious_links_answer": "Вредоносная ссылка — дверь в ловушку. Нажмёте — и попадёте в опасную зону!\n\nГде встречаются:\n• В сообщения`
- L1457: `"faq_social_engineering_answer": "Социальная инженерия — это когда вас обманывают словами, а не взломом.\n\nПримеры:\n• «Я ваш новый коллега`
- L1459: `"faq_fake_banks_answer": "Поддельный банк — это сайт-клон, который крадёт ваши данные.\n\nКак отличить:\n• Настоящий адрес: sberbank.ru\n• П`
- L1461: `"faq_inappropriate_content_answer": "Неподходящий контент — то, что дети не должны видеть:\n• Страшные видео\n• Взрослые сайты\n• Жестокие и`
- L1463: `"faq_cyberbullying_answer": "Кибербуллинг — когда детей травят в интернете:\n• Оскорбляют в чатах\n• Выкладывают обидные фото\n• Угрожают\n•`
- L1465: `"faq_dangerous_contacts_answer": "Опасные знакомства — когда взрослый пытается подружиться с ребёнком:\n• «Привет! Давай дружить»\n• «Ты так`
- L1467: `"faq_password_theft_answer": "Кража паролей — это когда мошенники узнают ваш пароль и входят в аккаунты:\n• Крадут деньги\n• Читают сообщени`
- L1469: `"faq_fake_voices_answer": "Поддельный голос — это когда компьютер копирует голос человека:\n• Мошенник звонит и говорит голосом вашего ребён`
- L1471: `"faq_fake_news_answer": "Фейковые новости — это ложная информация, выдаваемая за правду:\n• «Учёные нашли лекарство от всех болезней!»\n• «З`
- L1473: `"faq_unsafe_wifi_answer": "Небезопасный Wi‑Fi — публичная сеть-ловушка:\n• В кафе, аэропортах, метро\n• Мошенники могут перехватить ваши дан`
- L1475: `"faq_mitm_attacks_answer": "Man-in-the-middle — когда мошенник встаёт между вами и сервисом:\n1. Вы думаете, что общаетесь с банком\n2. На с`
- L1479: `"faq_sms_scam_answer": "SMS-мошенничество — это обманные сообщения:\n• «Вы выиграли! Переведите деньги для получения приза»\n• «Счёт заблоки`
- L1483: `"faq_domestic_violence_answer": "Цифровое домашнее насилие — когда близкий человек контролирует другого через интернет:\n• Читает все сообще`
- L1487: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1489: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L1491: `"faq_critical_infrastructure_answer": "Критическая инфраструктура — это важнейшие системы:\n• Больницы\n• Электростанции\n• Водоснабжение\n•`
- L1493: `"faq_how_vpn_works_answer": "VPN — это как подземный тоннель. Когда вы в интернете:\n• Обычно: телефон → провайдер → интернет (все видят, ку`
- L1497: `"faq_cancel_subscription_answer": "Легко! 😊\n\n1. Откройте «Настройки»\n2. Найдите «Управление подпиской»\n3. Нажмите «Отменить подписку»\n\`
- L1499: `"faq_phishing_emails_answer": "Фишинговое письмо — это обманное сообщение, заставляющее сделать что-то опасное:\n• «Ваш аккаунт заблокирован`
- L1503: `"faq_suspicious_downloads_answer": "Подозрительная загрузка — это файл, который может навредить:\n• Приложение с вирусом\n• Фото с вредоносн`
- L2099: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2297: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2631: `"family_header_accessibility": "ALADDIN Family — Family Protection",`

### `Core/Localization/LocalizationManager_backup_20251121.swift`

- L237: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L422: `"family_status_critical_message": "Защита отключена — включите тариф для семьи",`
- L748: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а VPN — весь трафик устройства.",`
- L1115: `"tariffs_free_features_1": "VPN Базовый — с ограниченной скоростью и количеством мб трафика",`
- L1121: `"tariffs_personal_features_1": "VPN Pro — безлимитная скорость",`
- L1127: `"tariffs_family_features_1": "VPN Ultra — безлимитная скорость",`
- L1656: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L1658: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L2268: `"family_header_accessibility": "ALADDIN Family — защита семьи",`
- L2465: `"child_rewards_achievement_excellent_desc": "Five top grades in a row — great job!",`
- L2837: `"family_header_accessibility": "ALADDIN Family — Family Protection",`
- L3419: `"tariffs_free_features_1": "Basic VPN — limited speed and data traffic",`
- L3425: `"tariffs_personal_features_1": "VPN Pro — unlimited speed",`
- L3431: `"tariffs_family_features_1": "VPN Ultra — unlimited speed",`
- L4378: `"family_status_critical_message": "Protection disabled — enable family tariff",`

### `Core/Managers/FamilyLocalStore.swift`

- L273: `"🔄 FAMILY JWT user_id changed (\(previous) → \(extracted)) — clearing local family context",`
- L506: `"⚠️ FAMILY ID: your_member_id=\(current.prefix(8))… не в ростере; JWT отсутствует — требуется повторный вход или заголовок X-Current-Member-`
- L532: `"⚠️ FAMILY ID: your_member_id=\(current.prefix(8))… не в ростере; JWT не содержит подходящего MEM_* — проверьте токен на сервере",`

### `Core/Managers/SubscriptionManager.swift`

- L1037: `"⚠️ FAMILY STATS drift: JWT/local trial but server cap=\(cap) tier=\(tier.isEmpty ? "?" : tier) — keep server gate (no optimistic \(trialCap`
- L1042: `"⚠️ Hybrid-B: stale serverStats max=\(cap) while local trial active — NOT inflating add gate"`
- L2661: `logger.network("📡 Skipping sync — Support screen visible")`

### `Core/Navigation/NavigationManager.swift`

- L613: `appendLog("❗️ goBack: PaymentQR без тарифа и пустой стек — возвращаемся к Tariffs")`
- L672: `appendLog("⚠️ goBack: lastScreenBeforePaymentQR отсутствует — используем Tariffs")`
- L702: `appendLog("⚠️ Стек пуст при PaymentQR — fallback на Tariffs")`
- L708: `appendLog("⬅️ Стек пуст — возврат на \(fallback)")`
- L931: `appendLog("🛡️ navigateToAntifakeHub: уже на Hub — обновили tab=\(tab.rawValue)")`

### `Core/Network/APIService.swift`

- L808: `"🔄 FAMILY ADD(stale) 409 family_context_stale — clearing local family_id",`

### `Core/Network/NetworkManager.swift`

- L1600: `completion(.failure(NetworkError.decodingError(NSError(domain: "NetworkManager", code: -1, userInfo: [NSLocalizedDescriptionKey: "Mock/fallb`
- L1608: `logger.network("ℹ️ content_sync: ответ шлюза не по контракту \(reqPath) — используем локальный кэш")`
- L1631: `logger.network("ℹ️ content_sync: декод \(T.self) не удалился для \(reqPath) — используем кэш. \(decodingError.localizedDescription)")`

### `Core/Services/WellnessProgressPDFService.swift`

- L47: `let line = "• \(checkin.moodEmoji ?? "—") — \(checkin.day)"`

### `Core/Utilities/VisualLogger.swift`

- L125: `"Диагностика ALADDIN (iOS), exportKind=\(exportKind): открой в контейнере приложения папку Documents и файл «\(name)» (или по абсолютному пу`

### `Screens/02_FamilyScreen.swift`

- L662: `"🧹 FAMILY SYNC: server empty — dropped phantom local roster",`
- L807: `"🛡️ FAMILY SYNC: server returned fewer ids than local while family context matches — keeping merged roster (no server-only prune; GET may be`
- L1250: `"🛡️ REMOVE self-removal отказ сервера — откат optimistic, sync+reconcile your_member_id",`

### `Screens/09_ElderlyInterfaceScreen.swift`

- L462: `: String(format: localizationManager.localized("elderly_medications_next_dose"), medications.first?.time ?? "—", medications.first?.name ?? `
- L474: `: String(format: localizationManager.localized("elderly_appointments_next"), appointments.first?.date ?? "—", appointments.first?.doctor ?? `
- L3226: `return value.isEmpty ? "—" : value`

### `Screens/10_TariffsScreen.swift`

- L443: `Text(free ? "✓" : "—")`
- L447: `Text(family ? "✓" : "—")`
- L451: `Text(premium ? "✓" : "—")`
- L771: `return "—"`

### `Screens/11_ProfileScreen.swift`

- L396: `return "—"`

### `Screens/14_OnboardingScreen.swift`

- L814: `"onboarding_page6_desc": "Местоположение всей семьи — на карте в приложении. Сообщим, когда ребёнок пришёл домой, в школу или секцию.",`

### `Screens/14_OnboardingScreen_FULL_BACKUP.swift`

- L73: `description: "Один клик — помощь рядом. Определение поддельных видео, поддельного голоса, фейковых звонков и номеров!",`
- L80: `description: "Спокойствие за близких — бесценно. Защита начинается сегодня!",`

### `Screens/18_PrivacyPolicyScreen.swift`

- L746: `"Face ID: Данные лица НЕ собираются — приложение использует только встроенную функцию iOS для локальной аутентификации",`
- L747: `"Face ID: Данные лица НЕ передаются третьим лицам — вся обработка происходит локально на устройстве в Secure Enclave",`
- L748: `"Face ID: Данные лица НЕ хранятся на наших серверах — они остаются только на устройстве пользователя и удаляются при удалении приложения"`
- L755: `"В отчёте — технические данные, уже записанные на устройстве; лишнее можно стереть вручную.",`
- L757: `"Цель — исправление сбоев; не для рекламы и не продаём."`
- L762: `"Телефоны и email для рекламы не берём. Дом и школу — только если родитель сам сохранил в «Где семья»",`
- L778: `"Точка телефона ребёнка — только после разрешения на его телефоне",`
- L835: `"Раздел «Настроение и поддержка» — инструменты самопомощи, не медицинская услуга",`
- L838: `"При признаках кризиса — подсказки обратиться к взрослому или на линию помощи",`
- L844: `"Antifake — проверка подозрительных звонков и сообщений по вашей инициативе",`
- L846: `"Call Directory — локальная метка на экране входящего звонка после синхронизации",`
- L852: `"ALADDIN не записывает линию оператора. Запись — только с микрофона, если вы сами её включили (обычно громкая связь).",`
- L853: `"Запись не начинается сама — только ваши действия в разделе «Звонки» / Диктофон.",`
- L854: `"Аудио и выжимка по умолчанию на устройстве; на сервер — только если вы отправите сами.",`
- L857: `"Кнопки после звонка — ваш ручной сигнал семье, не автодоказательство мошенничества.",`

### `Screens/19_TermsOfServiceScreen.swift`

- L262: `"ALADDIN AI — система семейной безопасности",`
- L341: `"Запись звонков — только по вашей инициативе; вы отвечаете за согласие собеседника и законность",`
- L344: `"Раздел «Звонки» — вспомогательный инструмент, не юридическая или банковская консультация и не услуга оператора связи",`

### `Screens/22_DeviceDetailScreen.swift`

- L287: `guard !trimmed.isEmpty else { return "—" }`

### `Screens/23_FamilyChatScreen.swift`

- L795: `let u = underlying.map { "\(Swift.type(of: $0)): \($0.localizedDescription)" } ?? "—"`
- L796: `let s = silent.map { $0 ? "да" : "нет" } ?? "—"`

### `Screens/AdvancedProtectionSettingsScreen.swift`

- L37: `@State private var familyTotalTimeUsed: String = "—"`
- L38: `@State private var familyTotalTimeLimit: String = "—"`

### `Screens/ChildContentExperienceScreen.swift`

- L4961: `.init(startSec: 0, endSec: 4, text: "Bonjour, hola, hello — поём"),`

### `Screens/FamilyGroupsModal.swift`

- L246: `return "—"`

### `Screens/FamilySafetyRemainderHub.swift`

- L243: `"— pin NOT updated (RCA S13)"`

### `Screens/NotificationSettingsScreen.swift`

- L504: `Text("QA Smoke — user kinds (без VPN)")`
- L516: `Text("Сейчас фильтры ON — часть баннеров может не показаться. Для smoke выключите DND / Important / High priority.")`
- L602: `Text("soft_test (только диагностика) · VPN/network_protection — убраны · APNs remote — отдельный этап · biometric toggle — не семейное событ`

### `Screens/WellnessTimelineScreen.swift`

- L44: `Text(row.moodEmoji ?? "—")`

### `Shared/Components/Modals/PrivacyReportsModal.swift`

- L340: `Text("—")`

### `Shared/Components/StormMeshBackground.swift`

- L422: `.previewDisplayName("Storm Mesh — all variants")`
- L446: `case .devicesPanel: return "Все устройства — одна панель"`
- L524: `.previewDisplayName("Batch 8 — ASO 6 slides hub light")`

### `Shared/Components/VoiceNotes/VoiceDayRecapSheet.swift`

- L51: `Text("—")`

### `Shared/Components/VoiceNotes/VoiceNotesStructureSheet.swift`

- L80: `Text("—")`

### `Tests/UITests/CompanionSmokeUITests.swift`

- L28: `throw XCTSkip("Child interface not shown — check launch flags / navigation bootstrap")`

### `Tests/UITests/WellnessCompanionNavUITests.swift`

- L34: `throw XCTSkip("Exercise screen not reached — API/catalog may be offline")`

### `ViewModels/FamilyRegistrationViewModel.swift`

- L436: `logger.business("⚠️ ADMIN_ADD_MODE active but no family_id — resetting (avoid addMember 404 before family exists)")`
- L514: `logger.business("⚠️ ADMIN_ADD: stale family_id without roster identity — switching to createFamily()")`
- L516: `"🔄 Stale family_id on device (not your server family) — creating new family",`

### `ViewModels/NotificationsViewModel.swift`

- L777: `"Давно не заходил(а) — всё ок? Хватит одной минуты check-in.": "wellness_nudge_idle_body",`
- L778: `"Давно не заходил(а) — всё ок? Хватит одной минуты check-in": "wellness_nudge_idle_body",`
- L779: `"Haven't checked in — all OK? One minute is enough.": "wellness_nudge_idle_body",`
- L784: `"Ребёнок: нужна помощь — срочно": "need_help_confirm_sent_body",`
- L785: `"Child: need help — urgent": "need_help_confirm_sent_body",`

### `coding_orchestrator/ui/macos/Sources/OrchMac/ContentView.swift`

- L131: `Text(p.description.isEmpty ? p.name : "\(p.name) — \(p.description)")`
- L202: `Text("KILL SWITCH — spawn остановлен")`

### `coding_orchestrator/ui/macos/Sources/OrchMac/OrchModel.swift`

- L81: `return "Движок выключен — запустите scripts/orch_open.command"`
- L83: `return "Ждёт вас — разрешите или отклоните merge"`
- L85: `return "Работает — сессии или ночная очередь активны"`
- L87: `return "Свободен — можно поставить задачу"`

### `docs/backup/family-mobile-snapshot-20260505-020615/Core/Managers/FamilyLocalStore.swift`

- L255: `"⚠️ FAMILY ID: your_member_id=\(current.prefix(8))… не в ростере; JWT отсутствует — требуется повторный вход или заголовок X-Current-Member-`
- L281: `"⚠️ FAMILY ID: your_member_id=\(current.prefix(8))… не в ростере; JWT не содержит подходящего MEM_* — проверьте токен на сервере",`

### `docs/backup/family-mobile-snapshot-20260505-020615/Core/Network/NetworkManager.swift`

- L1492: `completion(.failure(NetworkError.decodingError(NSError(domain: "NetworkManager", code: -1, userInfo: [NSLocalizedDescriptionKey: "Mock/fallb`
- L1500: `logger.network("ℹ️ content_sync: ответ шлюза не по контракту \(reqPath) — используем локальный кэш")`
- L1523: `logger.network("ℹ️ content_sync: декод \(T.self) не удалился для \(reqPath) — используем кэш. \(decodingError.localizedDescription)")`

### `docs/backup/family-mobile-snapshot-20260505-020615/Screens/02_FamilyScreen.swift`

- L531: `"🛡️ FAMILY SYNC: server returned fewer ids than local while family context matches — keeping merged roster (no server-only prune; GET may be`
- L965: `"🛡️ REMOVE self-removal отказ сервера — откат optimistic, sync+reconcile your_member_id",`
- L971: `? "Сервер считает этого участника вашей учётной записью. Список обновлён — удаление другого профиля выполняйте с того устройства или обратит`
- L1489: `? "Добавлять и удалять участников могут только родители или пожилой в списке (не ребёнок и не подросток). До двух родительских аккаунтов — п`
- L1499: `? "Ваш ID: \(myId.isEmpty ? "—" : String(myId.prefix(14)))… · роль в списке: \(roleLabel) · родителей в списке: \(parents) · управление сост`
- L1500: `: "Your ID: \(myId.isEmpty ? "—" : String(myId.prefix(14)))… · role in list: \(roleLabel) · parents in list: \(parents) · can manage roster:`
- L3218: `@State private var topSite: String = "—"`
- L3220: `@State private var topApp: String = "—"`
- L3221: `@State private var topAppTime: String = "—"`
- L3419: `topSite = "—"`
- L3426: `topApp = "—"`
- L3427: `topAppTime = "—"`
- L6348: `private var emDash: String { "—" }`
- L6566: `Text(warning.time.isEmpty ? "—" : warning.time)`

### `docs/backup/family-mobile-snapshot-20260505-020615/ViewModels/FamilyRegistrationViewModel.swift`

- L318: `logger.business("⚠️ ADMIN_ADD_MODE active but no family_id — resetting (avoid addMember 404 before family exists)")`

### `docs/backup/onboarding_pages_0_plus_7_plus_main_20260511_221734/Core/Localization/LocalizationManager.swift`

- L304: `"analytics_trial_mode_notice": "Пробный период использует лимиты выбранного тарифа. Ниже — только статистика работы защиты за период.",`
- L306: `"analytics_protection_level_no_events": "За период не было зафиксированных угроз — доля «заблокировано от обнаруженных» не считается, поэтом`
- L395: `"crash_logs_support_telegram_alert_message": "Откроется чат с официальным ботом в Telegram: @AladdinchatAI_bot (в списке чатов имя может ото`
- L400: `"crash_logs_support_footer": "Добровольно. Бот: @AladdinchatAI_bot. Не собираем пароли, карты, SMS, контакты и медиа для этого экрана — толь`
- L426: `"family_roster_who_can_manage_body": "Добавлять и удалять участников могут только родители или участник с ролью «Люди 60+» в списке (не ребё`
- L574: `"child_rewards_achievement_excellent_desc": "5 пятёрок подряд — отличная работа!",`
- L633: `"games_pet_description": "Тамагочи-питомец с индикаторами ❤️🍎⭐😊. Ребёнок кормит, играет, гладит. 4 стадии эволюции. Нельзя отключить — это о`
- L1027: `"parent_dashboard_trends_empty": "No data for this period yet — open content on the child device to populate the chart.",`
- L1080: `"unified_time_limits_server_bedtime_fmt": "Bedtime window: %@ — %@",`
- L1393: `"add_member_to_current_family_desc": "Выберите роль и имя — участник появится в вашей семье без создания новой",`
- L1495: `"family_status_critical_message": "Защита семьи недоступна (агенты или связь). Тариф может быть активен — проверьте экран «Тарифы».",`
- L1776: `"bypass_smart_dns_reason_ipc_failed": "Системный модуль DNS (nehelper) не принял настройку: сбой IPC. Часто это временно — перезагрузите iPh`
- L1901: `"vpn_help_proxy_answer": "Прокси защищает только браузер, а защита сети — весь трафик устройства.",`
- L2674: `"post_admin_add_device_offer_subtitle": "%@ добавлен в семью. Можно сразу зарегистрировать устройство — та же форма, что в разделе «Устройст`
- L3224: `"child_study_chemistry_page_2": "Вода, соль, сахар и воздух — примеры веществ, которые мы встречаем каждый день.",`
- L3390: `"child_study_creativity_page_3": "Ошибки в творчестве — это шаг к новым открытиям.",`
- L3405: `"child_study_project_page_3": "Итог проекта — продукт, презентация и выводы.",`
- L4697: `"games_parental_info_description": "Здесь вы можете включать и отключать игровые элементы. Единорог-питомец всегда активен — это основная мо`
- L4711: `"games_parental_pet_description": "Тамагочи-питомец с индикаторами ❤️🍎⭐😊. Ребёнок кормит, играет, гладит. 4 стадии эволюции. Нельзя отключит`
- L5033: `"profile_subscription_free_no_expiry": "Тариф Free — дата окончания не ограничена.",`
- L5118: `"delete_account_error_gateway": "Сервер вернул защитную оболочку без подтверждения удаления (mock-real-protection). Удаление не подтверждено`
- L5119: `"family.incomplete_server_roster_hint": "По тарифу можно больше участников, а с сервера пришёл один — данные семьи неполные. Обратитесь в по`
- L5225: `"faq_protect_elderly_answer": "Для бабушек и дедушек мы сделали специальную защиту:\n\n• Блокируем звонки от мошенников (они часто звонят лю`
- L5287: `"faq_aes256_answer": "AES-256 — это самый сильный способ защиты информации, который используют:\n• Банки\n• Военные\n• Правительства\n• Спец`
- L5289: `"faq_anonymity_answer": "Анонимность означает, что никто не знает, кто вы:\n• Ваш IP-адрес скрыт\n• Ваши действия не могут быть отслежены\n•`
- L5354: `"privacy_policy_section_auth_content_4": "Face ID: Данные лица НЕ собираются — приложение использует только встроенную функцию iOS для локал`
- L5355: `"privacy_policy_section_auth_content_5": "Face ID: Данные лица НЕ передаются третьим лицам — вся обработка происходит локально на устройстве`
- L5356: `"privacy_policy_section_auth_content_6": "Face ID: Данные лица НЕ хранятся на наших серверах — они остаются только на устройстве пользовател`
- L5358: `"privacy_policy_section_crash_diagnostics_subtitle": "Официальный бот @AladdinchatAI_bot — только по вашей инициативе",`
- L5359: `"privacy_policy_section_crash_diagnostics_content_1": "Бот поддержки в Telegram: @AladdinchatAI_bot. В списке чатов отображаемое имя может б`
- L5362: `"privacy_policy_section_crash_diagnostics_content_4": "В технический отчёт могут попасть только уже записанные на устройстве сведения для ст`
- L5364: `"privacy_policy_section_crash_diagnostics_content_6": "Цель такой передачи — только помощь в устранении сбоев и улучшение качества приложени`
- L5751: `"family_chat_banner_no_family": "Семья на сервере не найдена — отправка сообщений отключена.",`
- L6199: `"main_exec_plan_inline_strike_hint": "Нажмите круг слева, чтобы локально отметить сделанное (зачёркивание). Каноника — чекбоксы в дашборде и`
- L6210: `"plan_275_strike_hint": "Круг слева — только локальная отметка «просмотрено»; каноника статуса в git-матрице.",`
- L6216: `"plan_275_sheet_done_title": "Готово (DONE) — 275",`
- L6222: `"main_family_network_protection_hint": "Подробнее об отличиях счётчиков — в отчётах и уведомлениях.",`
- L6227: `"main_family_network_layers_hint": "Отдельно от счётчика угроз выше: DNS — уровень сети; Safari CB — только браузер.",`
- L6230: `"family_modal_network_layers_scope": "Статус ниже — этот iPhone с приложением; карточки мониторинга выше — данные ребёнка с сервера.",`
- L6231: `"family_modal_network_layers_p2_note": "Продуктовая линия P2: статус Safari/DNS ребёнка на его телефоне через приложение не показываем — тол`
- … ещё 26

### `docs/backup/onboarding_pages_0_plus_7_plus_main_20260511_221734/Core/Navigation/NavigationManager.swift`

- L306: `appendLog("❗️ goBack: PaymentQR без тарифа и пустой стек — возвращаемся к Tariffs")`
- L365: `appendLog("⚠️ goBack: lastScreenBeforePaymentQR отсутствует — используем Tariffs")`
- L395: `appendLog("⚠️ Стек пуст при PaymentQR — fallback на Tariffs")`
- L399: `appendLog("⬅️ Стек пуст — возврат на .main")`

---

## Swift: логи / RCA (справочно, не первая замена)

Всего: 96. Примеры:

- `ALADDINApp.swift:951` print("🔄 MainScreenWithRegistration disappeared — registration flow completed")
- `ALADDINApp.swift:1499` print("⚠️ initializeNavigation: @AppStorage snapshot (\(passed)) ≠ UserDefaults (\(onboardingDone)) 
- `ALADDINApp.swift:1521` print("🟢 ONBOARDING: Пройден (UserDefaults) — переходим на вход")
- `ALADDINApp_new.swift:72` print("🌍 RESET_ONBOARDING активирован — ключ сброшен")
- `ViewModels/ChildRewardsViewModel.swift:67` VisualLogger.shared.log("ℹ️ load() cancelled — no user-facing error", level: .info, category: "CHILD
- `ViewModels/DrivingReportsViewModel.swift:101` print("⚠️ DrivingReportsViewModel: unauthorized — local ledger only")
- `ViewModels/MainViewModel.swift:167` print("ℹ️ MainViewModel.refreshDevicesCountFromAPI: пропуск — уже идёт loadDashboardData (будет dedu
- `ViewModels/MainViewModel.swift:281` print("⏳ MainViewModel: Сессия ещё не готова — ждём SubscriptionManager…")
- `ViewModels/MainViewModel.swift:293` print("ℹ️ MainViewModel: Нет API-сессии — пропускаем загрузку дашборда")
- `ViewModels/MainViewModel.swift:602` print("🔐 MainViewModel: Debug токены не работают с сервером — локальный режим")
- `ViewModels/MainViewModel.swift:674` print("⏳ SubscriptionManager ещё не инициализирован — откладываем загрузку на 800мс")
- `ViewModels/MainViewModel.swift:691` print("   - Данных нет — загружаем обязательно")
- `ViewModels/MainViewModel.swift:700` print("   - ✅ Принудительное обновление дашборда (изменился состав семьи — ждём /api/family/stats)")
- `ViewModels/NetworkProtectionViewModel.swift:311` print("⚠️ NetworkProtectionViewModel: Crash Detection на симуляторе — \(presentation.message)")
- `ViewModels/NotificationsViewModel.swift:9` Карта данных (экран Уведомления и связанные потоки) — int-1 / согласование с бэкендом:
- `ViewModels/NotificationsViewModel.swift:15` - Главный экран / семья: агрегаты угроз и семейной защиты — `GET /api/parental-control/stats` и связ
- `ViewModels/NotificationsViewModel.swift:16` подписи «угрозы» — про данные защиты устройств / CB, не про bypass и не сумма с Safari без пояснения
- `ViewModels/NotificationsViewModel.swift:19` - Обход (bypass): счётчики — `GET /api/parental/bypass/stats` + локальный журнал при офлайне;
- `ViewModels/NotificationsViewModel.swift:20` серверная запись событий — `POST /api/parental-control/monitoring/events` (kind/payload «bypass»)
- `ViewModels/NotificationsViewModel.swift:22` - Мониторинг/отчёты РК: `GET /api/parental-control/monitoring/detail`, отчёты — `/reports/daily` и т
- `ViewModels/NotificationsViewModel.swift:23` Safari Content Blocker — отдельный контур телеметрии, не смешивать с метрикой обхода.
- `ViewModels/FamilyRegistrationViewModel.swift:601` VisualLogger.shared.log("🚫 FAMILY_ADD tariff limit — no createFamily fallback", level: .warning, cat
- `ViewModels/FamilyRegistrationViewModel.swift:632` VisualLogger.shared.log("❌ FAMILY_ADD forbidden/stale — no createFamily wipe", level: .error, catego
- `BACKUP_SCREENS_20251106_132406/ALADDINApp.swift:18` print("🌍 RESET_ONBOARDING активирован — ключ сброшен")
- `Core/Config/AppConfig.swift:174` print("⚠️ AppConfig.authToken: Keychain fill on main — prefer warmAuthTokenCache() before UI body")

… и ещё 71.

---

## Следующий шаг (когда скажете GO)

Аккуратно `—` → `–` по доменам из этой карты (не логи), с verify локализации.
