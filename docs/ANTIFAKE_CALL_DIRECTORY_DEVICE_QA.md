# Antifake Call Directory — device QA (D-batch + af-ux-10)

**Build:** 232+ (extension CFBundleVersion 235+) · **Tasks:** D-01…D-10, **af-ux-10**  
**Hub UX (2026-06):** Call Directory **только** на вкладке **«Звонок»** → блок **«Метки на входящих»**

---

## Цель

На **реальном iPhone** (не Simulator):

1. Extension **«ALADDIN Call Filter»** виден в настройках и включается  
2. Sync в app скачивает базу  
3. На **входящем** PSTN-звонке с QA-номера — метка **«Возможный мошенник?»** / **«Possible scam?»**

---

## Static gate (перед физическим тестом)

```bash
cd ALADDIN_iOS
bash scripts/verify_antifake_device_readiness.sh
bash scripts/verify_af_ux_hub_static.sh
```

---

## Предусловия

- [ ] TestFlight или Archive с встроенным `ALADDINCallDirectory.appex`  
- [ ] Premium (production: `bypassPremiumGate = false`)  
- [ ] Сервер: `GET /api/antifake/call-directory` → `identified[]` (не seed в коде)  
- [ ] QA-номера в БД (`source=qa`): `74951234567`, `78005553535`, `79001234567`

---

## af-ux-10 — пошаговый чеклист (основной)

| # | Шаг | Ожидание | Pass |
|---|-----|----------|------|
| 1 | Установить сборку с extension (TestFlight / Archive) | В IPA есть `ALADDINCallDirectory.appex` | ☐ |
| 2 | **Настройки → Телефон → Блокировка и опознавание вызовов** *(iOS 18+: Настройки → Приложения → Телефон → …)* | В списке есть **«ALADDIN Call Filter»** (не «ALADDIN») | ☐ |
| 3 | Включить переключатель **ALADDIN Call Filter** | ON | ☐ |
| 4 | App → **Проверить подлинность** → вкладка **«Звонок»** | Две секции: **«Проверка записи»** и **«Метки на входящих»** | ☐ |
| 5 | На вкладках **Текст / Голос / Видео** | **Нет** карточки «Метки на входящих» / «Синхронизировать» | ☐ |
| 6 | **Звонок** → **«Синхронизировать»** | «Синхронизировано N номеров · дата», статус «Расширение включено» | ☐ |
| 7 | С **другого телефона** позвонить на iPhone с `+7 495 123-45-67` (или другой QA) | **D-04:** метка на экране входящего | ☐ |
| 8 | Extension **выключен** в Settings, Sync в app | База скачивается, оранжевый баннер «метки не появятся» (**D-08**) | ☐ |
| 9 | Сборка **без** extension / симулятор | Баннер «Расширение не найдено — обновите приложение» | ☐ |
| 10 | iPhone language **EN** → повторить звонок | Метка **«Possible scam?»** (**D-10**) | ☐ |

### Если переключателя «ALADDIN Call Filter» нет

1. Убедиться, что сборка **не Simulator-only** и extension embedded  
2. Переустановить app из TestFlight  
3. Перезагрузить iPhone  
4. В app: **Звонок** → **Инструкция: метки на входящих** → **Открыть «Настройки»**  
5. Искать именно **ALADDIN Call Filter**

---

## Регрессия Hub UX (af-ux)

| ID | Проверка | Pass |
|----|----------|------|
| UX-01 | CD card только на tab Call | ☐ |
| UX-02 | Секции `recording` / `incoming` видны на Call | ☐ |
| UX-03 | Post-call toggle в секции «Проверка записи», не в CD card | ☐ |
| UX-04 | Family reports **свернуты** по умолчанию; раскрываются по тапу | ☐ |

---

## Подпись QA (R-02)

Заполнить `docs/release/device_qa/antifake/DEVICE_QA_RECORD.json`:

- **tester:** _______________  
- **build:** _______________  
- **device_ios:** _______________  
- **D-04 screenshot:** приложить путь к файлу  
- **sync_count:** _______________  
- **date:** _______________

---

## Связанные документы

- `docs/ANTIFAKE_HUB_UX_FINAL_PLAN.md` — продуктовый план UX  
- `docs/release/ANTIFAKE_DEVICE_BATCH_RUNBOOK.md` — archive / TestFlight  
- `docs/ANTIFAKE_POST_CALL_DEVICE_QA.md` — post-call запись (E-06)
