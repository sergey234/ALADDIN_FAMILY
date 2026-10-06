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

**Не новый id:** CTA «перед переводом» на главной — через **`fws-03`**, не `fsl-17`.

Указатели (не второй список): `FAMILY_SHIELD_UX_LIFT_TASK_REGISTRY.md` · `GENAI_TOP50_ALADDIN_TASK_REGISTRY.md`
