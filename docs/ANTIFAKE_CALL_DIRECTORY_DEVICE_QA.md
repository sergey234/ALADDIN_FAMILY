# Antifake Call Directory — device QA (D-06)

**Build:** 232+ · **Tasks:** D-01…D-10 · **Cursor:** `af-D-*`

---

## Цель

Подтвердить на **real iPhone** (не Simulator): extension включён → Sync → входящий с QA-номера → метка на экране звонка.

---

## Static gate

```bash
bash scripts/verify_antifake_device_readiness.sh
```

## D-01 simulator compile

```bash
./scripts/archive_antifake_device_build.sh --simulator-only
```

## D-01 archive / D-02 TestFlight

See `docs/release/ANTIFAKE_DEVICE_BATCH_RUNBOOK.md`

---

## Предусловия

- [ ] TestFlight или Archive build 232+ с `ALADDINCallDirectory` extension
- [ ] **Premium** подписка (production: `bypassPremiumGate = false`; UITest: `-UITestAntifakeHubSmoke`)
- [ ] Сервер отдаёт `/api/antifake/call-directory` (не seed в коде)
- [ ] QA-номера в БД (`source=qa`): `74951234567`, `78005553535`, `79001234567`

---

## Шаги (D-03)

1. Установить сборку на iPhone
2. **Hub → Метки на звонках → «Как включить»** — включить ALADDIN в  
   **Настройки → Телефон → Блокировка и опознавание вызовов**  
   *(iOS 18+: Настройки → **Приложения** → Телефон → тот же раздел)*
3. Вернуться в app → **«Синхронизировать»**
4. Ожидание: «Синхронизировано N номеров · дата»
5. С **другого телефона** позвонить на iPhone с номера `+7 495 123-45-67` (или другой QA)
6. **D-04:** на экране входящего — метка **«Возможный мошенник?»** (RU) / **«Possible scam?»** (EN)

---

## Чеклист регрессии

| ID | Проверка | Pass |
|----|----------|------|
| D-04 | Скрин метки на входящем | ☐ |
| D-07 | `identified` — метка; `block=true` — блок (если включим) | ☐ |
| D-08 | Extension OFF → оранжевый статус в app | ☐ |
| D-09 | Airplane mode → sync снова OK | ☐ |
| D-10 | iPhone EN → метка на английском | ☐ |

---

## Подпись QA (R-02)

- Tester: _______________
- Build: _______________
- Скрин метки: приложить
- Sync count: _______________
- Дата: _______________
