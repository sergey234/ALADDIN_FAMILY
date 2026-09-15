# План локализации A/B/C/G/I — без дублей (2026-09-15)

Правило: **один уникальный русский текст = один ключ = один пункт плана**.
Несколько файлов/строк с тем же текстом → один ключ, много call-sites.

| Зона | Уникальных фраз | NO_KEY | WIRE |
|------|----------------:|-------:|-----:|
| A | 25 | 22 | 3 |
| B | 86 | 85 | 1 |
| C | 78 | 57 | 21 |
| G | 26 | 25 | 1 |
| I | 12 | 8 | 4 |

## Зона A — 25 уникальных фраз

- [ ] **A-001** `WIRE` «Аладдин (13+)»
  - Ключ: `companion_hero_aladdin`
  - Действие: подключить localized
  - Места (1): `Screens/CompanionParentConsentSection.swift:67`
- [ ] **A-002** `WIRE` «Герой настороже»
  - Ключ: `companion_a11y_hero_alert`
  - Действие: подключить localized
  - Места (1): `UI/Companion/CompanionHeroAvatarView.swift:208`
- [ ] **A-003** `WIRE` «Единорог»
  - Ключ: `companion_hero_unicorn`
  - Действие: подключить localized
  - Места (1): `Screens/CompanionParentConsentSection.swift:66`
- [ ] **A-004** `NO_KEY` «AI-компаньон для детей»
  - Ключ: `TBD_A_004`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionParentConsentSection.swift:22`
- [ ] **A-005** `NO_KEY` «Как Grok Custom Instructions: родитель задаёт стиль общения для всей семьи. Без телефонов, адресов и паролей.»
  - Ключ: `TBD_A_005`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionPersonalitySection.swift:24`
- [ ] **A-006** `NO_KEY` «Краткие безопасные заметки для персонализации (экспорт и удаление ниже)»
  - Ключ: `TBD_A_006`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionParentConsentSection.swift:43`
- [ ] **A-007** `NO_KEY` «Краткие заметки без PII после разговоров. Родитель может выгрузить или удалить всё (152-ФЗ).»
  - Ключ: `TBD_A_007`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionMemoryManagementSection.swift:25`
- [ ] **A-008** `NO_KEY` «Память выключена. Включите переключатель «Память компаньона» выше и сохраните настройки.»
  - Ключ: `TBD_A_008`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionMemoryManagementSection.swift:33`
- [ ] **A-009** `NO_KEY` «Память компаньона»
  - Ключ: `TBD_A_009`
  - Действие: создать RU+EN ключ + localized
  - Места (2): `Screens/CompanionParentConsentSection.swift:42`; `Screens/CompanionMemoryManagementSection.swift:20`
- [ ] **A-010** `NO_KEY` «Пока нет сохранённых заметок. Они появятся после диалогов ребёнка с героем.»
  - Ключ: `TBD_A_010`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionMemoryManagementSection.swift:38`
- [ ] **A-011** `NO_KEY` «Разрешить «Разговор с героем»»
  - Ключ: `TBD_A_011`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionParentConsentSection.swift:36`
- [ ] **A-012** `NO_KEY` «Разрешённые герои»
  - Ключ: `TBD_A_012`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionParentConsentSection.swift:63`
- [ ] **A-013** `NO_KEY` «Ребёнок видит кнопку в Играх и может писать герою»
  - Ключ: `TBD_A_013`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionParentConsentSection.swift:37`
- [ ] **A-014** `NO_KEY` «Режим «эксперт безопасности» по умолчанию»
  - Ключ: `TBD_A_014`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionPersonalitySection.swift:45`
- [ ] **A-015** `NO_KEY` «Родитель решает, может ли ребёнок общаться с героями и сохранять ли память разговоров (152-ФЗ / COPPA).»
  - Ключ: `TBD_A_015`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionParentConsentSection.swift:27`
- [ ] **A-016** `NO_KEY` «Свои инструкции (до 500 символов)»
  - Ключ: `TBD_A_016`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionPersonalitySection.swift:50`
- [ ] **A-017** `NO_KEY` «Сохранить настройки компаньона»
  - Ключ: `TBD_A_017`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionParentConsentSection.swift:77`
- [ ] **A-018** `NO_KEY` «Сохранить тон и инструкции»
  - Ключ: `TBD_A_018`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionPersonalitySection.swift:72`
- [ ] **A-019** `NO_KEY` «Сохраняем…»
  - Ключ: `TBD_A_019`
  - Действие: создать RU+EN ключ + localized
  - Места (2): `Screens/CompanionPersonalitySection.swift:72`; `Screens/CompanionParentConsentSection.swift:77`
- [ ] **A-020** `NO_KEY` «Стиль»
  - Ключ: `TBD_A_020`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionPersonalitySection.swift:33`
- [ ] **A-021** `NO_KEY` «Тон и инструкции героя»
  - Ключ: `TBD_A_021`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionPersonalitySection.swift:19`
- [ ] **A-022** `NO_KEY` «Удаление…»
  - Ключ: `TBD_A_022`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionMemoryManagementSection.swift:80`
- [ ] **A-023** `NO_KEY` «Удалить всё»
  - Ключ: `TBD_A_023`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionMemoryManagementSection.swift:80`
- [ ] **A-024** `NO_KEY` «Экспорт JSON»
  - Ключ: `TBD_A_024`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionMemoryManagementSection.swift:72`
- [ ] **A-025** `NO_KEY` «Экспорт…»
  - Ключ: `TBD_A_025`
  - Действие: создать RU+EN ключ + localized
  - Места (1): `Screens/CompanionMemoryManagementSection.swift:72`

## Зона B — 86 уникальных фраз

**Аудит 2026-09-15 (режим A):** каркас ключей оставлен; все 86 пунктов проверены вручную по чеклисту.

| Проверка | Результат |
|----------|-----------|
| Ключ RU+EN в `LocalizationManager` | ✅ 85 `child_loc_b_*` + WIRE `wellness_reflective_confirm_continue` |
| Call-site в Swift | ✅ все 86 подключены |
| Хардкод RU из списка B в Experience/Screen | ✅ 0 осталось |
| Отображение story title/choice через `localized` | ✅ |
| ChildContentScreen кнопки через `localized` | ✅ |
| Karaoke **названия** треков | ✅ |
| EN-тон (детский UI) | ✅ подправлены слабые формулировки (045, 055–056, 058, 060–061, 065, 070–071, 079, 081, 087, 104–105, 110) |

**Не входит в зону B (ещё RU на English UI):** тексты `page.narration` в сказках и **строки куплетов** karaoke — отдельный backlog, не эти 86 пунктов.

- [x] **B-026** `WIRE` «Продолжить» → `wellness_reflective_confirm_continue`
- [x] **B-027…B-111** `NO_KEY` → `child_loc_b_027`…`child_loc_b_111` (см. `scripts/_loc_b_keys.json` + словарь)

## Зона C — 78 уникальных фраз

**Пачка 1 (WIRE C-112…C-132) — ✅ 2026-09-15, вручную:**
- Подключены существующие ключи в MemberSettings / RewardsQuick / FamilyCreated / MemberStats / FamilyScreen.
- «Безопасность» → `profile_security_title` (EN: Security), не `nav_screen_security_education` (там «Security education»).
- Добавлены недостающие EN: `profile_edit_save` = Save, `profile_edit_ok` = Got it.

**Пачка 3 (NO_KEY C-138…C-147) — ✅ 2026-09-15, вручную:**
- [x] C-138 `member_settings_unicorn_choice` — Choose a unicorn
- [x] C-139 `member_settings_analytics_data` — Analytics data
- [x] C-140 `member_settings_children_actions` — Children’s activity
- [x] C-141 `member_settings_access_requests` — Access requests
- [x] C-142 `member_settings_notification_sounds` — Notification sounds
- [x] C-143 `member_settings_sound_alerts` — Sound alerts
- [x] C-144 `member_settings_game_settings` — Game settings
- [x] C-145 `member_settings_avatar_icon` — Avatar icon
- [x] C-146 `member_settings_interface` — Interface
- [x] C-147 `member_settings_browsing_history` — Browsing history

- [x] **C-112…C-132** WIRE (см. пачку 1)
- [x] **C-133…C-137** NO_KEY пачка 2
- [x] **C-138…C-147** NO_KEY пачка 3
- [x] **C-148…C-160** NO_KEY пачка 4
- [x] **C-161…C-189** NO_KEY пачка 5 — зона C закрыта ✅
- [x] **LOC-G** G-190…G-215 — зона G закрыта ✅
- [x] **LOC-I** I-216…I-227 — зона I закрыта ✅
- [x] **loc-verify** — `scripts/verify_loc_abcgi_user_visible.py` PASS (0 UI hardcode)

**Пачка 5 (NO_KEY C-161…C-189) — ✅ вручную:**
- FamilyScreen: Use server / Check fields / Roles & Profiles
- MemberSettings: simple auth, permissions, role/rights, 2FA on/off, children notifs, security threats, manage children/members, theme/level/parents see/bright buttons/critical only
- FamilyCreated: title + subtitle
- MemberStats section titles: activity variants, protection, rewards, my children/activity

<details><summary>Полный чеклист C (исторический)</summary>

- [x] **C-112…C-189** done (пачки 1–5) — зона C ✅

</details>

## Зона G — 26 уникальных фраз

**Пачка G-190…G-215 — ✅ 2026-09-15 вручную**

- [x] **G-190** `WIRE` `tariff_devices_unlimited` — TariffCardView
- [x] **G-191** `subscription_auth_expired_restoring`
- [x] **G-192…G-212** AppFeature name/desc keys + `displayName`/`fullDescription` → `localized`
- [x] **G-213** `tariff_plan_family_title` — PaymentQR preview (+ StoreManager.family reuse)
- [x] **G-214 / G-215** `feature_family_emergency_alerts_*`
- зона I + loc-verify — ✅

<details><summary>Исторический чеклист G</summary>

- [x] **G-190** `WIRE` «Неограниченно» → `tariff_devices_unlimited`
- [x] **G-191** `subscription_auth_expired_restoring`
- [x] **G-192** `feature_security_alerts_desc`
- [x] **G-193** `feature_family_medical_alerts_desc`
- [x] **G-194** `feature_family_community_alerts_desc`
- [x] **G-195** `feature_family_medical_alerts_name`
- [x] **G-196** `feature_suicide_prevention_alerts_desc`
- [x] **G-197** `feature_custom_security_alerts_desc`
- [x] **G-198** `subscription_auth_restore_failed`
- [x] **G-199** `feature_family_community_alerts_name`
- [x] **G-200** `feature_password_breach_alerts_desc`
- [x] **G-201** `feature_family_weather_alerts_desc`
- [x] **G-202** `feature_identity_theft_alerts_desc`
- [x] **G-203** `feature_fake_website_alerts_desc`
- [x] **G-204** `feature_cyberbullying_alerts_desc`
- [x] **G-205** `feature_family_weather_alerts_name`
- [x] **G-206** `feature_custom_security_alerts_name`
- [x] **G-207** `feature_security_alerts_name`
- [x] **G-208** `feature_password_breach_alerts_name`
- [x] **G-209** `feature_cyberbullying_alerts_name`
- [x] **G-210** `feature_identity_theft_alerts_name`
- [x] **G-211** `feature_suicide_prevention_alerts_name`
- [x] **G-212** `feature_fake_website_alerts_name`
- [x] **G-213** `tariff_plan_family_title`
- [x] **G-214** `feature_family_emergency_alerts_desc`
- [x] **G-215** `feature_family_emergency_alerts_name`

</details>

## Зона I — 12 уникальных фраз

**Пачка I-216…I-227 — ✅ 2026-09-15 вручную**

- WIRE: `nav_screen_analytics`, `elderly_appointments_time_label`, `family_protection_accessibility`, `nav_screen_network_protection`
- NO_KEY: `widget_label_*` (blocks/data/children_online/apps/sites/server/speed/threats)
- Runtime: `ALADDINWidgets/WidgetL10n.swift` (appex; mirrors LocalizationManager keys)

**Verify:** `python3 scripts/verify_loc_abcgi_user_visible.py` → **PASS** (2026-09-15)

<details><summary>Исторический чеклист I</summary>

- [x] **I-216** `WIRE` `nav_screen_analytics`
- [x] **I-217** `WIRE` `elderly_appointments_time_label`
- [x] **I-218** `WIRE` `family_protection_accessibility`
- [x] **I-219** `WIRE` `nav_screen_network_protection`
- [x] **I-220** `widget_label_blocks`
- [x] **I-221** `widget_label_data`
- [x] **I-222** `widget_label_children_online`
- [x] **I-223** `widget_label_apps`
- [x] **I-224** `widget_label_sites`
- [x] **I-225** `widget_label_server`
- [x] **I-226** `widget_label_speed`
- [x] **I-227** `widget_label_threats`

</details>
