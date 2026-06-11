# COPY-POST-L3 — полный аудит маркетинговых и юридических текстов

**Дата:** 2026-06-11 · **Статус:** согласовано (с оговорками ниже) · **Batch ID:** `COPY-POST-L3` / `R-19`  
**Связь:** `EXTENDED_138_CHECKLIST.md` (100 угроз + 32 PC + 6 EX) · `ПОЛНЫЙ_АНАЛИЗ_42_КОМПОНЕНТОВ_И_138_ФУНКЦИЙ.md`  
**Исполнение:** `COPY_POST_L3_TODO.md` · трекер: `.cursor/IMPLEMENTATION_BATCHES_TODO.md` § R-19

---

## Согласованные решения (PO)

| # | Решение | Статус |
|---|---------|--------|
| 1 | OB_01: «основных киберугроз» | ✅ делаем |
| 2 | Тарифы/каталог: «комплексная защита по тарифу» | ✅ делаем |
| 3 | OB_02: «Военные технологии шифрования» | ✅ **оставляем** |
| 4 | OB_04: предсказывает/предотвращает → анализирует/предупреждает | ✅ делаем |
| 5 | OB_06: распознаёт → проверяет | ✅ делаем |
| 6 | `faq_unsafe_wifi_answer` — усиление про AES-256 | ❌ **не делаем** (текст без изменений) |
| 7 | Смягчить абсолюты: 100%, невозможно взломать, полная анонимность, блокирует SMS/звонки | ✅ делаем |
| 8 | Privacy/Terms/landing — синхрон с app + RU/EN | ✅ делаем |
| 9 | FAQ: +3 новых + включить скрытые + gap по 138 | ✅ делаем (см. §6) |

### Оговорки

- **50+ серверов** в Privacy — заменить на «серверы в РФ и за рубежом» до аудита реального пула VPS.
- **faq_protect_elderly** — убрать строку про голосовое управление (eld-03 deferred).
- **faq_critical_infrastructure**, **faq_domestic_violence** — не в публичный FAQ.
- **faq_emotional_problems** — только с wellness-disclaimer или отложить.
- Онбординг Figma frames — после правок строк прогнать `verify_onboarding_sync_01_03.py`.

---

## §1 Онбординг (OB_01…07)

**Файлы:** `Screens/14_OnboardingScreen.swift` (fallback RU/EN), `Core/Localization/LocalizationManager.swift`, `scripts/verify_onboarding_sync_01_03.py`, `LocalizedVersions/English/14_OnboardingScreen_Localized.swift`, `docs/kb/kb_v1/documents/onboarding_page_onboarding_{ru,en}.json`

| Key | RU было | RU стало | len | EN было | EN стало |
|-----|---------|----------|-----|---------|----------|
| `onboarding_page1_desc` | Комплексная система защиты от более 100 видов киберугроз | Комплексная система защиты от основных киберугроз | 51 (−4) | A complete protection system against cyber threats | Comprehensive protection against major cyber threats |
| `onboarding_page2_desc` | …Военные технологии шифрования | **без изменений** | 97 | AI protects your family 24/7 | AI protects your family 24/7 + Multi-layer protection ⭐⭐⭐⭐⭐! Military-grade encryption |
| `onboarding_page4_desc` | …предсказывает, обнаруживает и предотвращает… | Система ALADDIN AI анализирует, обнаруживает и предупреждает о киберугрозах. Постоянно обучается и улучшается. | 108 (+3) | …predicts, detects and prevents… | ALADDIN AI analyzes, detects and warns about cyber threats. It constantly learns and improves. |
| `onboarding_page6_desc` | AI распознает фейковые… | AI проверяет фейковые звонки, новости, сообщения и видео. Защита от поддельных голосов и номеров. | 97 (−1) | Detect fraud calls… | AI checks fake calls, news, messages and video. Protection from spoofed voices and numbers. |

**Не менять:** OB_03, OB_05, OB_07, OB_02 RU (военные технологии).

---

## §2 Тарифы и каталог защиты

**Файл:** `Core/Localization/LocalizationManager.swift`

| Key | RU было | RU стало | EN стало |
|-----|---------|----------|----------|
| `tariffs_ai_protection` | 🤖 AI защита от 100 видов угроз | 🤖 AI защита — набор угроз по тарифу | 🤖 AI protection — threat set by plan |
| `tariffs_ai_protection_desc` | Комплексная защита семьи от всех 100 угроз | Комплексная защита семьи по вашему тарифу | Comprehensive family protection for your plan |
| `protection_catalog_title` | 🤖 AI защита от 100 видов угроз | 🤖 AI защита — набор угроз по тарифу | 🤖 AI protection — threat set by plan |
| `protection_catalog_subtitle` | Комплексная защита семьи от всех 100 угроз | Комплексная защита семьи по вашему тарифу | Comprehensive family protection for your plan |
| `protection_scenarios_subtitle` | Защита от более чем 100 видов кибер угроз | Комплексная защита по тарифу | Protection scope depends on your plan |
| `tariff_protection_title` | Защита от 100 видов угроз | Защита по тарифу | Protection by plan |
| `tariffs_recommendation_premium_text` | …защита от deepfake и всех угроз | Военное шифрование, анонимность, antifake и максимальный набор угроз | Military-grade encryption, privacy, antifake and maximum threat coverage |

**Оставить:** `tariffs_comparison_aes256`, `tariff_additional_*_aes256`, `terms_section_*_content_5` (военное шифрование).

**Опционально (низкий приоритет):** `protection_benefit_fraud` «Предотвращает» → «Помогает предотвратить» (комментарий в Swift, не user-facing catalog title).

---

## §3 FAQ — смягчение существующих (32 в каталоге)

**Файлы:** `LocalizationManager.swift`, `Screens/13_SupportScreen.swift`, `docs/kb/kb_v1/documents/faq_*_{ru,en}.json`

| Key | Действие | RU ответ (новый фрагмент / полный) | EN answer (sync) |
|-----|----------|-----------------------------------|------------------|
| `faq_what_protects_answer` | смягчить | ALADDIN помогает защититься от основных опасностей в интернете. Набор функций зависит от тарифа. Это как охранник для телефона — предупреждает о вирусах, мошенниках и опасных сайтах.\n\nСистема работает 24/7 и отслеживает активность на устройстве. | ALADDIN helps protect against major online risks. Features depend on your plan. Like a guard for your phone — warns about viruses, scammers and dangerous sites.\n\nThe system works 24/7 and monitors activity on your device. |
| `faq_data_safe_answer` | смягчить анонимность | Да, ваши данные надёжно защищены! 🔒\n\nМы используем:\n• Военное шифрование (как в банках и армии)\n• Обработка в соответствии с законами РФ\n• Соблюдаем требования о защите данных\n• В Premium — расширенные настройки приватности профиля | Yes, your data is reliably protected! 🔒\n\nWe use:\n• Military-grade encryption (like banks and the military)\n• Processing in line with applicable laws\n• Strong data protection practices\n• Premium — extended profile privacy settings |
| `faq_viruses_trojans_answer` | хвост | …✅ ALADDIN обнаруживает угрозы и предупреждает до того, как они нанесут вред. | …✅ ALADDIN detects threats and warns you before harm is done. |
| `faq_spyware_answer` | хвост | …✅ ALADDIN обнаруживает шпионское ПО и предупреждает. | …✅ ALADDIN detects spyware and warns you. |
| `faq_phone_scam_answer` | хвост | …✅ ALADDIN предупреждает о подозрительных звонках и помогает проверить риск. | …✅ ALADDIN warns about suspicious calls and helps you assess the risk. |
| `faq_deepfake_answer` | +async | …✅ ALADDIN Premium проверяет подозрительное видео (анализ может занять время) и предупреждает. | …✅ ALADDIN Premium checks suspicious video (analysis may take time) and warns you. |
| `faq_fake_voices_answer` | +async | …✅ ALADDIN Premium анализирует голос (проверка может занять время) и предупреждает о подделке. | …✅ ALADDIN Premium analyzes voice (check may take time) and warns about spoofing. |
| `faq_fake_news_answer` | смягчить | …✅ ALADDIN оценивает достоверность и предупреждает о рисках дезинформации. | …✅ ALADDIN assesses credibility and warns about misinformation risks. |
| `faq_mitm_attacks_answer` | хвост | …✅ ALADDIN Premium с защитой сети затрудняет перехват данных. | …✅ ALADDIN Premium with network protection makes interception much harder. |
| `faq_aes256_answer` | смягчить | …Это как сейф с миллионом замков — ключ практически невозможно подобрать.\n\n✅ ALADDIN Premium применяет AES-256 для максимальной защиты. | …Like a safe with a million locks — the key is practically impossible to guess.\n\n✅ ALADDIN Premium uses AES-256 for maximum protection. |
| `faq_anonymity_answer` | смягчить | …✅ ALADDIN Premium с защитой сети повышает приватность; абсолютная анонимность в интернете недостижима. | …✅ ALADDIN Premium with network protection improves privacy; absolute anonymity online is not possible. |
| `faq_protect_elderly_answer` | убрать голос | …• Делаем простой интерфейс — всё понятно\n• Красная кнопка SOS — быстро вызвать помощь | …• Simple interface — easy to understand\n• Red SOS button — get help quickly |
| `faq_unsafe_wifi_answer` | **НЕ МЕНЯТЬ** | (текущий текст) | (current) |

---

## §4 FAQ — включить в каталог (были в LocalizationManager, не в UI)

Добавить в `UnifiedFAQCatalog` (`13_SupportScreen.swift`) + keys EN + kb JSON:

| ID | Зачем (138 / 42) |
|----|------------------|
| `faq_aes256` | EX-ANON / Premium encryption · военное шифрование PO |
| `faq_how_network_protection_works` | EX-VPN #133 · образование |
| `faq_malicious_apps` | UG-CYBER #7 |
| `faq_sms_scam` | UG-FRAUD Smishing #28 |
| `faq_location_threats` | PC-GEO #115–119 |

**Смягчить при включении:** `faq_sms_scam_answer` — «блокирует» → «проверяет ссылки и предупреждает»; `faq_malicious_apps` — без «перед установкой» (iOS sandbox) → «перед открытием/скачиванием».

---

## §5 FAQ — новые записи (3 + gap 138)

| ID | Вопрос RU | Ответ RU (кратко) | EN question | EN answer (кратко) | 138 |
|----|-----------|-------------------|-------------|-------------------|-----|
| `faq_crash_detection` | Что такое обнаружение аварии? | Датчики телефона могут заметить резкое столкновение при движении. ALADDIN покажет предупреждение и предложит вызвать помощь. Возможны ложные срабатывания — всегда проверяйте ситуацию. Не заменяет вызов 112. | What is crash detection? | Phone sensors may detect a sharp impact while moving. ALADDIN shows an alert and offers to call for help. False alarms are possible — always check. Not a substitute for emergency services. | B7 emergency |
| `faq_roadside_assistance` | Что такое помощь на дороге? | В разделе «Защита сети» можно отправить запрос о поломке: тип проблемы и место (с вашего согласия). Данные уходят на сервер ALADDIN для связи с экстренными контактами. Работает при включённой функции. | What is roadside assistance? | In Network Protection you can report a breakdown: issue type and location (with consent). Data goes to ALADDIN servers to reach emergency contacts. Requires the feature to be on. | B7 roadside |
| `faq_emergency_sos` | Как работает SOS для 60+? | Красная кнопка SOS в интерфейсе для пожилых отправляет сигнал близким и экстренным контактам семьи. Это не медицинская служба и не заменяет 112. | How does SOS for 60+ work? | The red SOS button in the elderly interface alerts family and emergency contacts. Not medical care and not a substitute for 112. | PC-GEO #118, EX-ELD |
| `faq_dark_web_leaks` | Что такое утечки в тёмной сети? | Мошенники продают украденные email и пароли в скрытых разделах интернета. ALADDIN в Privacy Hub проверяет, не светились ли ваши данные, и подсказывает, что сделать. | What are dark web leaks? | Stolen emails and passwords are sold in hidden parts of the internet. ALADDIN Privacy Hub checks exposure and suggests next steps. | UG-LEAK #34 |

**Рекомендовано (фаза 2, не блокер R-19):** `faq_parental_bypass`, `faq_geofencing`, `faq_wellness_support` (wellness disclaimer), `faq_gamification_rewards` (PC-REW).

**Не добавлять:** `faq_critical_infrastructure`, `faq_domestic_violence`, `faq_emotional_problems` (без legal review).

---

## §6 Матрица FAQ ↔ 138+42

| Группа 138 | Строк | FAQ покрытие | Gap |
|------------|-------|--------------|-----|
| UG-CYBER (1–10) | 10 | viruses, ransomware, spyware, phishing, fake_apps, malicious_links | botnets, miners, rootkits — образование в Hub, FAQ опционально |
| UG-NET (11–16) | 6 | dangerous_sites, downloads, unsafe_wifi, mitm | DNS-spoofing — нет отдельного FAQ |
| UG-FRAUD (17–28) | 12 | phone, financial, social, banks, phishing_emails | +sms_scam (smishing); medical/pyramid/lottery/romance — в Identity Hub |
| UG-LEAK (29–38) | 10 | password, privacy | **+dark_web_leaks**; metadata/cookies — Privacy Hub |
| UG-CHILD (39–48) | 10 | children, content, bullying, contacts, gaming, purchases | OK |
| UG-DEEP (93–100) | 8 | deepfake, voices, fake_news | OK + async note |
| PC-* (101–132) | 32 | parental_control_setup, protect_children | bypass, geofences, reports — фаза 2 |
| EX-VPN (133) | 1 | unsafe_wifi, mitm + **how_network_protection** | OK после включения |
| EX-AI (134) | 1 | faq_ai_how_works | OK |
| EX-ELD (135) | 1 | protect_elderly + **emergency_sos** | OK после правки голоса |
| EX-VOICE (136) | 1 | — | UI deferred; не обещать в FAQ |
| EX-GAME (137) | 1 | — | фаза 2 optional |
| EX-ANON (138) | 1 | data_safe, anonymity, **aes256** | OK после смягчения |

**Итого FAQ после R-19:** 32 + 5 скрытых + 4 новых = **41 видимых** (+ 3 фаза 2 опционально).

---

## §7 Политика конфиденциальности

**Файлы:** `LocalizationManager.swift` (privacy_policy_*), `Screens/18_PrivacyPolicyScreen.swift`, `landing/privacy.html`, `docs/PRIVACY_POLICY_FULL_152FZ.md`

| Key / раздел | RU было | RU стало | EN |
|--------------|---------|----------|-----|
| `privacy_policy_section_responsibility_content_2` | Полная анонимность пользователей | Анонимная модель аккаунта (роль и возрастная группа) | Anonymous account model (role and age group) |
| `privacy_policy_*_encryption_content_3` | квантовая защита будущего | Усиленный режим ChaCha20 для максимальной стойкости | Enhanced ChaCha20 mode for maximum strength |
| `privacy_policy_*_encryption_content_4` | Все 3 вида: НЕВОЗМОЖНО взломать | Все 3 вида: стойкость военного уровня | All three: military-grade strength |
| `privacy_policy_*_servers_subtitle` | 50+ серверов по всему миру | Серверы защиты сети в РФ и за рубежом | Network protection servers in Russia and abroad |
| `privacy_policy_*_servers_content_1…4` | 🇷🇺 15 / 🇪🇺 20… | Удалить точные цифры; одна строка: «География узлов уточняется в настройках защиты сети» | Remove hard counts; single line on node geography |
| landing §16 | НЕВОЗМОЖНО взломать / 100% | практически неподбираемый ключ / высокий уровень защиты | practically unguessable key / high protection level |
| landing §13 | Полная анонимность | как responsibility_content_2 | same |
| **Добавить §** | — | Emergency/Crash/Roadside: геолокация при согласии, срок хранения, отключение | EN mirror |
| **Добавить §** | — | Antifake async: медиа на сервер для анализа, не хранится постоянно | EN mirror |
| principles | всё на устройстве | Уточнить: cloud AI, antifake, emergency — часть на сервере ALADDIN | EN mirror |
| version date | 11 мая / 1 июня рассинхрон | Единая дата при релизе COPY-POST-L3 | same |

**Оставить:** subtitle «3 вида военного шифрования», content_1 «военный уровень», wellness §18.

---

## §8 Условия использования

**Файл:** `LocalizationManager.swift` (terms_section_*)

| Key | RU было | RU стало | EN |
|-----|---------|----------|-----|
| `terms_section_description_content_2` | …антивирус… | …анализ угроз на устройстве… | …on-device threat analysis… |
| `terms_section_network_protection_content_5` | Используется военное шифрование | **без изменений** | Military-grade encryption is used |
| **Добавить** `terms_section_antifake_content_*` | — | Проверки аудио/видео — асинхронно, до нескольких минут | Async audio/video checks, up to a few minutes |
| **Добавить** `terms_section_emergency_content_*` | — | Обнаружение аварий — не замена 112; ложные срабатывания возможны | Crash detection not a substitute for 112; false positives possible |

**Оставить:** `terms_section_liability_content_2` «Не гарантируем 100% защиту».

---

## §9 Landing и KB

| Файл | Действие |
|------|----------|
| `landing/privacy.html` | §13, §16, §17 — как §7 |
| `landing/terms.html` | синхрон с Terms app |
| `landing/help-faq.html` | после FAQ keys — ручной или скрипт экспорт |
| `docs/kb/kb_v1/documents/faq_*_{ru,en}.json` | 32 существующих + новые 7 |
| `docs/kb/kb_v1/documents/onboarding_page_onboarding_{ru,en}.json` | OB_01,04,06 |
| `docs/release/COPY_01_ONBOARDING_L3_AUDIT.md` | пометка: OB_02 военное — keep |
| `scripts/verify_onboarding_sync_01_03.py` | EXPECTED strings OB_01,04,06 |

---

## §10 ML_SYSTEM_PACKAGE / дубли

Синхронизировать после основного merge:

- `ML_SYSTEM_PACKAGE/LocalizationManager.swift`
- `ML_SYSTEM_PACKAGE/LocalizedVersions/English/14_OnboardingScreen_Localized.swift`
- `LocalizedVersions/English/14_OnboardingScreen_Localized.swift`

---

## §11 Gate PASS для COPY-POST-L3

- [ ] Все keys из `COPY_POST_L3_TODO.md` — RU+EN в `LocalizationManager.swift`
- [ ] `UnifiedFAQCatalog` — 41 entry
- [ ] Onboarding fallback RU/EN + verify script PASS
- [ ] Privacy/Terms landing sync
- [ ] kb JSON обновлены
- [ ] `grep` старых фраз: `предсказывает`, `100\+ видов`, `НЕВОЗМОЖНО взломать`, `полная анонимность` — 0 в user-facing (кроме changelog)
- [ ] LOC regression spot-check `docs/release/QA_06_LOC_REGRESSION.md`
- [ ] `onboarding_frozen: false` в `security-l3-report.json` после merge

---

*COPY_POST_L3_FULL_AUDIT v1.0 · 2026-06-11 · SSOT для R-19*
