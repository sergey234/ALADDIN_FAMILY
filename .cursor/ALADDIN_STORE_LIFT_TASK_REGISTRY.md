# ALADDIN store lift — единый TODO (`fsl-*` + `gai-*`)

**План:** [`docs/PLAN_ALADDIN_STORE_LIFT_MASTER_2026-10-06.md`](../docs/PLAN_ALADDIN_STORE_LIFT_MASTER_2026-10-06.md)  
**Аудит 14+50 + промпт второй ИИ:** [`docs/AUDIT_STORE_TOPS_AND_GENAI50_FOR_SECOND_AI_2026-10-06.md`](../docs/AUDIT_STORE_TOPS_AND_GENAI50_FOR_SECOND_AI_2026-10-06.md)  
**Rule:** `.cursor/rules/aladdin-store-lift-todo-ssot.mdc`

## TodoWrite

Только **`merge: true`**. Не затирать `af-*`, `eld-*`, `ep*`, `ori-*`, `ps-*`, `ux-co-*`, `fws-*`.

Код после **GO LIFT BUILD**.

## Порядок

```text
lift-00 / fsl-00 / gai-00 / lift-01 / lift-02 планы ✅
→ GO LIFT BUILD
A  fsl-01 fsl-02 ✅
B  fsl-03 fsl-04 ✅
C  fsl-05 fsl-13 fsl-15 ✅ 2026-10-07
D  fsl-06 … fsl-12  fsl-14 fsl-16 ✅ 2026-10-07
E  gai-05 gai-06 gai-01 gai-03 gai-04 gai-02 gai-07 ✅ 2026-10-07
→ fsl-qa-device
```

| ID | Волна | Зачем | Статус |
|----|-------|--------|--------|
| `lift-00-master` | 0 | Один канон вместо двух планов | ✅ 2026-10-06 |
| `lift-01-audit-doc` | 0 | Один документ 14+50 + промпт второй ИИ | ✅ 2026-10-06 |
| `lift-02-gap-add` | 0 | GAP второй ИИ: fsl-14…16 + gai-07 | ✅ 2026-10-06 |
| `fsl-00-plan` | 0 | Разбор 14 ссылок ST | ✅ |
| `gai-00-plan` | 0 | Разбор топ 50 Gen AI | ✅ |
| `fsl-01-doc-hub` | A | Документ в Hub | ✅ 2026-10-06 |
| `fsl-02-share-image` | A | Share фото/PDF | ✅ 2026-10-06 |
| `fsl-03-home-map` | B | Карта дома | ✅ 2026-10-06 |
| `fsl-04-pause` | B | Пауза без роутера | ✅ 2026-10-06 |
| `fsl-05-geofence-live` | C | Живая школа | ✅ 2026-10-07 |
| `fsl-13-im-ok` | C | Кнопка «Я в порядке» | ✅ 2026-10-07 |
| `fsl-15-soft-presence` | C | Заряд + «был в сети / я ок» | ✅ 2026-10-07 |
| `fsl-06-verdict-speak` | D | Прослушать вердикт | ✅ 2026-10-07 |
| `fsl-07-day-strip` | D | Полоска дня | ✅ 2026-10-07 |
| `fsl-08-call-plain` | D | Простой текст звонка | ✅ 2026-10-07 |
| `fsl-09-focus-flag` | D | Фокус подростка | ✅ 2026-10-07 |
| `fsl-10-habits-surface` | D | Привычки на виду | ✅ 2026-10-07 |
| `fsl-11-share-onboard` | D | Научиться Share | ✅ 2026-10-07 |
| `fsl-12-iot-push` | D | Пуш IoT | ✅ 2026-10-07 |
| `fsl-14-week-digest` | D | Недельный дайджест щита | ✅ 2026-10-07 |
| `fsl-16-check-widget` | D | Виджет «Проверить ссылку» | ✅ 2026-10-07 |
| `gai-01-sources` | E | Sources API + empty (не второй UI; fws-04) | ✅ 2026-10-07 |
| `gai-02-grounded` | E | Герой по PDF семьи | ✅ 2026-10-07 |
| `gai-03-cam-ask` | E | Камера «что это?» | ✅ 2026-10-07 |
| `gai-04-translate` | E | Переведи и проверь | ✅ 2026-10-07 |
| `gai-05-chat-check` | E | Проверка в семейном чате | ✅ 2026-10-07 |
| `gai-06-siri-check` | E | Siri/ярлык «проверь ссылку» | ✅ 2026-10-07 |
| `gai-07-deepfake-lesson` | E | Урок Академии: лицо могут подделать | ✅ 2026-10-07 |
| `fsl-qa-device` | QA | Телефон владельца | ⬜ конец |

### Волна F — после Aura×Life360 (события мест / crash QA / browse) · 2026-10-07

**Канон экрана:** Cursor canvas `lift-next-plan-live-map-crash-safebrowse.canvas.tsx`  
**Принцип 152-ФЗ:** только события мест + явное согласие; не live GPS 24/7; не GPS-трек; Tile/dispatch/страховка — SKIP.

| ID | Волна | Зачем | Статус |
|----|-------|--------|--------|
| `geo-01-home-arrive` | F-A | Пуш/событие «дошёл домой» как школа | ✅ код 2026-10-08 |
| `geo-02-noshow` | F-A | No Show: Place к времени без enter | ✅ код 2026-10-08 |
| `geo-03-history-7d` | F-A | История enter/exit 7 дней (не трек) | ✅ код 2026-10-08 |
| `geo-04-consent-152` | F-A | Согласие «уведомления о местах, не слежка» | ✅ код 2026-10-08 |
| `legal-01-consent-copy` | F-A | Сверка текстов согласий с Политикой/юристом | ⬜ юрист |
| `geo-05-temp-share` | F-A later | Временный «я в пути 30 мин» с выкл. | ⏸ после A |
| `crash-01-device-qa` | F-B | QA CrashDetection на iPhone (модуль уже есть) | ⬜ device |
| `crash-02-imok-link` | F-B | Crash → «я ок» / семья / 112 (без dispatch) | ✅ код 2026-10-08 |
| `browse-01-share-onboard` | F-C | Онбординг Share + виджет + Siri | ✅ код 2026-10-08 |
| `browse-02-safari-blocker` | F-C | Статус Safari Content Blocker + гайд | ✅ код 2026-10-08 |
| `browse-03-sources` | F-C | Sources + empty под вердиктом | ✅ (gai-01) |
| `pwd-01-rename-ux` | F-D | UX паролей: генератор/проверка | ✅ код 2026-10-08 |
| `pwd-02-darkweb-academy` | F-D | Dark Web HIBP статус + урок утечки | ✅ код 2026-10-08 |
| `av-01-file-hub-link` | F-D | AV файла: ясный итог + связь Hub | ✅ код 2026-10-08 |
| `call-01-elderly-steps` | F-E | Scam-звонок 60+: 2–3 шага | ✅ код 2026-10-08 |
| `ux-01-daystrip-digest` | F-E | Day strip + week digest на виду | ✅ код 2026-10-08 |
| `pay-01-tier-copy` | F-F | Paywall 3 уровня без страховки | ✅ код 2026-10-08 |
| `priv-01-broker-checklist` | F-G | Академия: чеклист «убери себя из витрин» (Aura data brokers — без авто-ops) | ✅ код 2026-10-08 |
| `gai-08-risky-ai-apps` | F-G | Академия: список «опасные AI-чаты» (не скан переписок) | ✅ код 2026-10-08 |
| `sos-01-large-alarm` | F-G | SOS: крупная тревога семье (без silent GPS / Tile) | ✅ код 2026-10-08 |
| `bat-01-critical-push` | F-G | Пуш «батарея критична» (добить fsl-15, без GPS) | ✅ код 2026-10-08 |
| `id-01-theft-academy` | F-G | Урок: что делать при краже личности/утечке (не страховка Aura/L360) | ✅ код 2026-10-08 |
| `consent-01-crash-on` | F-A+ | Короткое согласие при включении Crash (локация при срабатывании) | ✅ код 2026-10-08 |
| `foot-01-self-hub` | F-H | ~~Новый экран «Мой след»~~ → **CANCEL**: уже `PrivacyHubScreen` | ❌ не нужен |
| `foot-02-simple-map` | F-H | Блок «проверка→утечки→смени пароль» **внутри** `PrivacyHubDarkWebPanel` | ✅ код 2026-10-08 |
| `darkweb-01-no-pii-fields` | F-H | Убрать passport/SNILS из `DarkWebDataInputView` (не собираем ПДн-досье) | ✅ код 2026-10-08 |
| `foot-03-hibp-email` | F-H ops | Сервер: HIBP email когда ключ (после GO ops) | ⬜ после GO |
| `lift-impl-tests-plan` | F-QA | `scripts/verify_lift_wave_f.py` + план-факт до симулятора | ✅ 2026-10-08 |

**Flowsint:** https://github.com/reconurge/flowsint — **не вшивать**; ADAPT идея следа → `foot-*`. Канон: PLAN_MASTER §10.

**Итоговый экран владельца (6 шляп):** Cursor canvas `lift-final-checklist-6hats.canvas.tsx`  
**Блоки A–H:** A `call-01` · B `browse-01…03` · C `pwd-02`/`priv-01`/`gai-08`/`id-01` · D `ux-01` · E `geo-*`+`legal-01` · F `crash-*` · G `pwd-01`/`av-01` · H `sos-01`/`bat-01`/`pay-01` · QA `fsl-qa-device` · след `foot-*`.

**Уже закрыто волнами A–E (не дублировать в F):** fsl-05 школа · fsl-13 «я ок» · fsl-15 soft presence · fsl-04 пауза · fsl-07/14 day strip+digest · fsl-11/16 + gai-06 Share/виджет/Siri · gai-07 deepfake · fsl-03/12 IoT · parental ST/фокус.

**SKIP (не id):** live map 24/7 · GPS history-трек · Tile/Pet · Life360 dispatch/roadside/insurance · Aura local-VPN+Accessibility · Social Persona/Kidas · US credit/SSN · sex offender geo · Temporary Circle · flight/weather · driver telematics.

**Не новый id:** CTA «перед переводом» на главной — через **`fws-03`**, не `fsl-17`.

Указатели (не второй список): `FAMILY_SHIELD_UX_LIFT_TASK_REGISTRY.md` · `GENAI_TOP50_ALADDIN_TASK_REGISTRY.md`
