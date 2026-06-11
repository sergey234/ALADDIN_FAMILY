# Extended‑138: приёмка функций (прод, по смыслу)

Автогенерация: `python3 tools/gen_extended138_checklist.py`

Источник таксономии: `ПОЛНЫЙ_АНАЛИЗ_42_КОМПОНЕНТОВ_И_138_ФУНКЦИЙ.md` (100 угроз + 32 родительских + 6 доп.).

**L3 criterion (B-QA-01):** `verify=ok` = L3 smoke по `docs/server/L3_SMOKE_CONTRACT.md`, **не** HTTP 200 alone. Детали: `docs/release/QA_01_EXTENDED138_L3_CRITERION.md`. iOS TestFlight L3 → `B-QA-02`.

Колонки: **api_hint** — типовые REST/SFM пути (заполнить при аудите); **verify** — `TBD` | `ok` (L3 only).

| № | Группа | Функция (продукт) | api_hint | verify |
|---|--------|-------------------|----------|--------|
| 1 | UG-CYBER | Вирусы и трояны | `POST /api/antivirus/scan` + `GET /api/malware/threats` (prod smoke) | ok |
| 2 | UG-CYBER | Шифровальщики (ransomware) | `POST /api/antivirus/scan` + malware threats smoke | ok |
| 3 | UG-CYBER | Шпионское ПО | `POST /api/antivirus/scan` + malware threats smoke | ok |
| 4 | UG-CYBER | Ботнеты | `GET /api/network-protection/status` + `network_security_agent` smoke | ok |
| 5 | UG-CYBER | DDoS-атаки | `GET /api/network-protection/status` + network protection smoke | ok |
| 6 | UG-CYBER | Фишинговые сайты | `GET /api/reports/identity-theft/stats` + `phishing_protection_agent` smoke | ok |
| 7 | UG-CYBER | Поддельные приложения | `POST /api/antivirus/scan` + malware/identity smoke | ok |
| 8 | UG-CYBER | Вредоносные ссылки | `GET /api/reports/identity-theft/stats` + phishing smoke | ok |
| 9 | UG-CYBER | Криптовалютные майнеры | `POST /api/antivirus/scan` + malware threats smoke | ok |
| 10 | UG-CYBER | Руткиты | `POST /api/antivirus/scan` + malware threats smoke | ok |
| 11 | UG-NET | Опасные сайты | `GET /api/network-protection/status` + parental block smoke | ok |
| 12 | UG-NET | Вредоносная реклама | `GET/POST /api/parental-control/settings*` + content filter smoke | ok |
| 13 | UG-NET | Подозрительные загрузки | `GET /api/network-protection/status` + malware/network smoke | ok |
| 14 | UG-NET | Небезопасные сети Wi‑Fi | `GET /api/network-protection/status` + network security smoke | ok |
| 15 | UG-NET | DNS-спуфинг | `GET /api/network-protection/status` + network security smoke | ok |
| 16 | UG-NET | Атаки «человек посередине» | `GET /api/network-protection/status` + network security smoke | ok |
| 17 | UG-FRAUD | Телефонное мошенничество | `GET/POST /api/parental-control/settings*` + parental communication smoke | ok |
| 18 | UG-FRAUD | Финансовое мошенничество | `GET /api/reports/identity-theft/stats` + identity smoke | ok |
| 19 | UG-FRAUD | Медицинские аферы | `GET/POST /api/parental-control/settings*` + family safety smoke | ok |
| 20 | UG-FRAUD | Социальная инженерия | `GET /api/reports/identity-theft/stats` + family safety smoke | ok |
| 21 | UG-FRAUD | Поддельные банки | `GET /api/reports/identity-theft/stats` + phishing/identity smoke | ok |
| 22 | UG-FRAUD | Фишинговые письма | `GET /api/reports/identity-theft/stats` + phishing smoke | ok |
| 23 | UG-FRAUD | Мошенничество с картами | `GET /api/reports/identity-theft/stats` + identity-theft smoke | ok |
| 24 | UG-FRAUD | Инвестиционные пирамиды | `GET/POST /api/parental-control/settings*` + family safety smoke | ok |
| 25 | UG-FRAUD | Лотерейные мошенничества | `GET/POST /api/parental-control/settings*` + child safety smoke | ok |
| 26 | UG-FRAUD | Романтические аферы | `GET /api/reports/identity-theft/stats` + communication safety smoke | ok |
| 27 | UG-FRAUD | Vishing | `GET/POST /api/parental-control/settings*` + parental communication smoke | ok |
| 28 | UG-FRAUD | Smishing | `GET/POST /api/parental-control/settings*` + parental communication smoke | ok |
| 29 | UG-LEAK | Кража паролей | `GET /api/components/status` + `password_security_agent` smoke | ok |
| 30 | UG-LEAK | Компрометация аккаунтов | `GET /api/reports/identity-theft/stats` (contract/smoke) | ok |
| 31 | UG-LEAK | Утечки персональных данных | `GET/PATCH /api/user/profile/privacy*` + privacy/compliance smoke | ok |
| 32 | UG-LEAK | Нарушение приватности | `GET/PATCH /api/user/profile/privacy*` + privacy settings smoke | ok |
| 33 | UG-LEAK | Слежка за семьёй | `GET /api/family/members` + family notification/privacy smoke | ok |
| 34 | UG-LEAK | Утечки в тёмной сети | `GET /api/reports/dark-web/stats` (contract/smoke) | ok |
| 35 | UG-LEAK | Утечки метаданных | `GET /api/reports/privacy/cleanup/stats` + privacy cleanup smoke | ok |
| 36 | UG-LEAK | Кейлоггеры | `POST /api/antivirus/scan` + malware/spyware smoke | ok |
| 37 | UG-LEAK | Перехват сессий | `GET /api/network-protection/status` + network session protection smoke | ok |
| 38 | UG-LEAK | Отслеживающие cookie | `GET/PATCH /api/user/profile/privacy*` + privacy controls smoke | ok |
| 39 | UG-LEAK | Отслеживание геолокации | `GET /api/reports/privacy/location/stats` (contract/smoke) | ok |
| 40 | UG-LEAK | Утечки данных EXIF | `GET /api/reports/privacy/cleanup/stats` + media privacy cleanup smoke | ok |
| 41 | UG-MOB | Вредоносные приложения | `GET /api/malware/threats` + `POST /api/antivirus/scan` (prod smoke) | ok |
| 42 | UG-MOB | SMS-мошенничество | `GET/POST /api/parental-control/settings*` + device smoke parental/messaging flow | ok |
| 43 | UG-MOB | Поддельные уведомления | `GET /api/notifications*` + `smart_notification_manager` device smoke | ok |
| 44 | UG-MOB | Кража данных с телефона | `GET /api/reports/identity-theft/stats` + `POST /api/malware/quarantine/action` | ok |
| 45 | UG-MOB | Геолокационные угрозы | `GET /api/reports/privacy/location/stats` + `location_bubble_agent` device smoke | ok |
| 46 | UG-MOB | Bluetooth-атаки | `GET /api/network-protection/status` + `network_security_agent` device smoke | ok |
| 47 | UG-MOB | Перехват SIM (SIM-swapping) | `GET /api/reports/identity-theft/stats` + parental protection smoke | ok |
| 48 | UG-MOB | Поддельные приложения банков | `GET /api/reports/identity-theft/stats` + `phishing_protection_agent` device smoke | ok |
| 49 | UG-MOB | Мобильные шифровальщики | `POST /api/antivirus/scan` + `GET /api/malware/threats` (prod smoke) | ok |
| 50 | UG-MOB | Скрытая запись экрана | `GET /api/components/status` + `mobile_security_agent` settings smoke | ok |
| 51 | UG-CHILD | Неподходящий контент | `GET/POST /api/parental-control/settings*` + `parental_control_bot` device smoke | ok |
| 52 | UG-CHILD | Кибербуллинг | `GET/POST /api/parental-control/settings*` + `psychological_support_agent` device smoke | ok |
| 53 | UG-CHILD | Опасные знакомства | `GET/POST /api/parental-control/settings*` + `online_predators_agent` device smoke | ok |
| 54 | UG-CHILD | Игровая зависимость | `GET/POST /api/parental-control/time-limits*` + `gaming_security_bot` device smoke | ok |
| 55 | UG-CHILD | Случайные покупки | `GET/POST /api/parental-control/app-blocks*` + device smoke parental flow | ok |
| 56 | UG-CHILD | Взрослые сайты | `GET/POST /api/parental-control/settings*` + `parental_control_bot` device smoke | ok |
| 57 | UG-CHILD | Насилие в играх | `GET/POST /api/parental-control/settings*` + `gaming_security_bot` device smoke | ok |
| 58 | UG-CHILD | Наркотики и алкоголь | `GET/POST /api/parental-control/settings*` + child safety device smoke | ok |
| 59 | UG-CHILD | Азартные игры | `GET/POST /api/parental-control/settings*` + child safety device smoke | ok |
| 60 | UG-CHILD | Экстремистский контент | `GET/POST /api/parental-control/settings*` + child safety device smoke | ok |
| 61 | UG-CHILD | Контент с призывами к саморазрушению | `GET/POST /api/parental-control/settings*` + `self_harm_detection_agent` smoke | ok |
| 62 | UG-CHILD | Неподходящая реклама | `GET/POST /api/parental-control/settings*` + parental flow smoke | ok |
| 63 | UG-CHILD | Онлайн-хищники | `GET/POST /api/parental-control/settings*` + `online_predators_agent` smoke | ok |
| 64 | UG-CHILD | Груминг-атаки | `GET/POST /api/parental-control/settings*` + `grooming_detection_agent` smoke | ok |
| 65 | UG-CHILD | Кэтфишинг | `GET/POST /api/parental-control/settings*` + `online_predators_agent` smoke | ok |
| 66 | UG-CHILD | Токсичные игровые сообщества | `GET/POST /api/parental-control/settings*` + `gaming_security_bot` smoke | ok |
| 67 | UG-CHILD | Зависимость от онлайн-азартных игр | `GET/POST /api/parental-control/time-limits*` + `gaming_security_bot` smoke | ok |
| 68 | UG-FAM | Домашнее насилие в сети | `GET/POST /api/parental-control/settings*` + family safety device smoke | ok |
| 69 | UG-FAM | Семейные конфликты | `GET /api/family/members` + `family_notification_manager` smoke | ok |
| 70 | UG-FAM | Изоляция от семьи | `GET /api/family/members` + `family_notification_manager` smoke | ok |
| 71 | UG-FAM | Эмоциональные проблемы | `GET/POST /api/parental-control/settings*` + `psychological_support_agent` smoke | ok |
| 72 | UG-FAM | Психологическое давление | `GET/POST /api/parental-control/settings*` + `psychological_support_agent` smoke | ok |
| 73 | UG-FAM | Киберсталкинг | `GET/POST /api/parental-control/settings*` + parental/messaging smoke | ok |
| 74 | UG-FAM | Цифровое преследование | `GET/POST /api/parental-control/settings*` + parental/messaging smoke | ok |
| 75 | UG-FAM | Онлайн-конфликты | `GET /api/family/members` + family notifications smoke | ok |
| 76 | UG-FAM | Подмена члена семьи | `GET /api/family/members` + family integrity smoke | ok |
| 77 | UG-FAM | Цифровая изоляция | `GET /api/family/members` + family notification flow smoke | ok |
| 78 | UG-FAM | Онлайн-триггеры депрессии | `GET/POST /api/parental-control/settings*` + `psychological_support_agent` smoke | ok |
| 79 | UG-FAM | Манипуляции в интернете | `GET/POST /api/parental-control/settings*` + family safety smoke | ok |
| 80 | UG-FAM | Газлайтинг в сети | `GET/POST /api/parental-control/settings*` + family safety smoke | ok |
| 81 | UG-FAM | Нарушение семейной приватности | `GET/PATCH /api/user/profile/privacy*` + compliance smoke | ok |
| 82 | UG-FAM | Несанкционированный доступ родственников | `GET /api/family/members` + `family_notification_manager` smoke | ok |
| 83 | UG-IOT | Взлом умных устройств | `GET /api/network-protection/status` + `network_security_agent` smoke | ok |
| 84 | UG-IOT | Взлом умного дома | `GET /api/network-protection/status` + `network_security_agent` smoke | ok |
| 85 | UG-IOT | Компрометация камер | `GET /api/network-protection/status` + `incident_response_agent` smoke | ok |
| 86 | UG-IOT | Подслушивание через умную колонку | `GET /api/network-protection/status` + `voice_control_manager` smoke | ok |
| 87 | UG-IOT | Взлом домашней сети | `GET /api/network-protection/status` + `network_security_agent` smoke | ok |
| 88 | UG-IOT | Утечка данных умных устройств | `GET /api/reports/privacy/cleanup/stats` + privacy smoke | ok |
| 89 | UG-IOT | Манипуляция голосовыми командами | `GET/POST /api/components/configuration/voice_control_manager` + voice smoke | ok |
| 90 | UG-IOT | Слабые пароли устройств | `GET /api/components/status` + `password_security_agent` smoke | ok |
| 91 | UG-IOT | Пароли по умолчанию | `GET /api/components/status` + `password_security_agent` smoke | ok |
| 92 | UG-IOT | Кража умного устройства | `GET /api/family/members` + emergency/incident smoke | ok |
| 93 | UG-DEEP | Deepfake-видео | `GET /api/reports/ai-categories/stats` + AI categories smoke | ok |
| 94 | UG-DEEP | Поддельные голоса | `GET /api/reports/ai-categories/stats` + AI categories smoke | ok |
| 95 | UG-DEEP | Спуфинг номеров | `GET /api/reports/identity-theft/stats` + identity smoke | ok |
| 96 | UG-DEEP | Поддельные сайты | `GET /api/reports/identity-theft/stats` + phishing smoke | ok |
| 97 | UG-DEEP | Фейковые новости | `GET /api/reports/ai-categories/stats` + AI categories smoke | ok |
| 98 | UG-DEEP | Поддельные документы | `GET /api/reports/ai-categories/stats` + AI categories smoke | ok |
| 99 | UG-DEEP | Фейковые профили знакомств | `GET /api/reports/identity-theft/stats` + identity/threat smoke | ok |
| 100 | UG-DEEP | Спуфинг писем (email spoofing) | `GET /api/reports/identity-theft/stats` + phishing/identity smoke | ok |
| 101 | PC-BLOCK | Блокировка сайтов (4 категории) | `GET/POST /api/parental-control/settings*` + device smoke parental flow | ok |
| 102 | PC-BLOCK | Блокировка приложений (база) | `GET/POST /api/parental-control/app-blocks*` + device smoke parental flow | ok |
| 103 | PC-BLOCK | SafeSearch / ключевые слова | `GET/POST /api/parental-control/settings*` + device smoke parental flow | ok |
| 104 | PC-BLOCK | Белые/чёрные списки | `GET/POST /api/parental-control/settings*` + device smoke parental flow | ok |
| 105 | PC-BLOCK | Автоблокировка новых приложений | `GET/POST /api/parental-control/app-blocks*` + parental app-block smoke | ok |
| 106 | PC-TIME | Экранный лимит (общий) | `GET/POST /api/parental-control/time-limits*` + device smoke parental flow | ok |
| 107 | PC-TIME | Время сна (1 интервал) | `GET/POST /api/parental-control/time-limits*` + device smoke parental flow | ok |
| 108 | PC-TIME | Расписания «Учёба/Отдых» | `GET/POST /api/parental-control/schedules*` + device smoke parental flow | ok |
| 109 | PC-TIME | Лимиты по типам приложений | `GET/POST /api/parental-control/time-limits*` + device smoke parental flow | ok |
| 110 | PC-MON | История браузера (24 часа) | `GET /api/reports/*` + device smoke `browser_security_bot` | ok |
| 111 | PC-MON | История приложений (24 часа) | `GET /api/reports/*` + device smoke parental/apps flow | ok |
| 112 | PC-MON | История браузера (7 дней) | `GET /api/reports/*` + browser monitoring smoke | ok |
| 113 | PC-MON | История приложений (7 дней) | `GET /api/reports/*` + app monitoring smoke | ok |
| 114 | PC-MON | Контроль новых контактов | `GET/POST /api/v1/parental-control/access-requests*` + parental communication smoke | ok |
| 115 | PC-GEO | Местоположение в реальном времени | `GET /api/reports/privacy/location/stats` + device smoke `location_bubble_agent` | ok |
| 116 | PC-GEO | Геозоны (дом, школа, секция) | `GET/POST /api/parental-control/geofences*` + device smoke parental flow | ok |
| 117 | PC-GEO | История перемещений (24ч) | `GET /api/reports/privacy/location/stats` + location history smoke | ok |
| 118 | PC-GEO | SOS-кнопка | `GET/POST /api/parental-control/*` + device smoke emergency/parental flow | ok |
| 119 | PC-GEO | История перемещений (7 дней + экспорт) | `GET /api/reports/privacy/location/stats` + location history/export smoke | ok |
| 120 | PC-REP | Еженедельный отчёт | `GET /api/reports/driving/stats?period=week` (smoke) | ok |
| 121 | PC-REP | Расширенный отчёт (топ-5, пиковые часы) | `GET /api/reports/driving/stats?period=week` + reports modal smoke | ok |
| 122 | PC-REP | Ежемесячный отчёт + экспорт | `GET /api/reports/driving/stats?period=week` + reports export smoke | ok |
| 123 | PC-EXT | Запросы на доступ | `GET/POST /api/v1/parental-control/access-requests*` + device smoke parental flow | ok |
| 124 | PC-EXT | Режим «Домашнее задание» | `GET/POST /api/parental-control/schedules*` + device smoke parental flow | ok |
| 125 | PC-EXT | YouTube Safe Mode | `GET/POST /api/parental-control/settings*` + parental content-filter smoke | ok |
| 126 | PC-EXT | AI-аналитика поведения | `GET /api/reports/ai-categories/stats` (smoke) | ok |
| 127 | PC-BYPASS | Обнаружение инкогнито/приватных окон | `GET/POST /api/parental-control/settings*` + device smoke parental/advanced flow | ok |
| 128 | PC-BYPASS | Обнаружение VPN/Tor/Proxy | `GET /api/network-protection/status` + device smoke `network_security_agent` | ok |
| 129 | PC-BYPASS | Мгновенная блокировка обхода | `POST /api/components/disable` + parental rules + device smoke | ok |
| 130 | PC-REW | Базовые единороги (ручные награды/штрафы) | `GET /api/gamification/balance` + rewards flow smoke | ok |
| 131 | PC-REW | Автонаграды за достижения | `GET /api/gamification/achievements*` + rewards flow smoke | ok |
| 132 | PC-REW | Премиум награды + аналитика | `GET /api/gamification/rewards*` + premium rewards smoke | ok |
| 133 | EX-VPN | VPN защита (уровни FREE / Personal-Family / Premium AES-256) | `GET /api/network-protection/status` + network protection smoke | ok |
| 134 | EX-AI | AI помощник — Personal+ | `GET /api/reports/ai-categories/stats` + AI assistant/category smoke | ok |
| 135 | EX-ELD | Защита пожилых — Family+ | `GET/POST /api/elderly/medications*` + `appointments*` + device smoke | ok |
| 136 | EX-VOICE | Голосовое управление — Family+ | `GET /api/components/configuration/voice_control_manager` (prod API) | ok |
| 137 | EX-GAME | Полная геймификация — Family+ | `GET /api/gamification/balance` + device smoke `child_interface_manager`/`gaming_security_bot` | ok |
| 138 | EX-ANON | Анонимные профили — Premium | `GET/PATCH /api/user/profile/privacy*` + compliance/profile smoke | ok |

**Итого строк:** 138 (ожидается 138)
