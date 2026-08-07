# AI Помощник — бренд-голос v1.1 — TODO (простым языком)

**План:** `PLAN_AIMONKEY_ASSISTANT_BRAND_VOICE_V1_1_2026-07-15.md`  
**Префикс Cursor:** `as-bv-*`  
**Правило:** ids не удалять; статус через `merge: true`.  
**Запрет:** fine-tune/LoRA в этом треке (`as-bv-r9`).

---

## 0. Старт

- [ ] `as-bv-00-owner-align` — OWNER ок с лестницей: тон+эталоны сейчас, LoRA потом
- [ ] `as-bv-00-baseline` — Снять baseline 7 дней: CSAT, эскалации, топ тем (до деплоя голоса)

## 1. Tone guide

- [ ] `as-bv-1-tone-doc` — Написать `AIMONKEY_ASSISTANT_BRAND_VOICE.md` (тон, длина, запреты)
- [ ] `as-bv-1-tone-owner` — OWNER вычитал и подтвердил tone guide
- [ ] `as-bv-1-prompt` — Сжать tone rules в `SYSTEM_PROMPT` (не раздувать)

## 2. Золотые ответы (30–50)

- [ ] `as-bv-2-schema` — Формат эталона (id/topic/must_include/must_not)
- [ ] `as-bv-2-t1-happ-android` — Эталоны T1 Happ Android (каркас, без копии SSOT)
- [ ] `as-bv-2-t2-happ-ios` — Эталоны T2 Happ iOS
- [ ] `as-bv-2-t3-order-own` — Эталоны T3 свой заказ
- [ ] `as-bv-2-t4-order-miss` — Эталоны T4 заказ не найден
- [ ] `as-bv-2-t5-bonus` — Эталоны T5 Stars с бонуса — отказ
- [ ] `as-bv-2-t6-ref` — Эталоны T6 рефералка
- [ ] `as-bv-2-t7-captcha` — Эталоны T7 капча/checkout
- [ ] `as-bv-2-t8-vpn-down` — Эталоны T8 VPN не работает
- [ ] `as-bv-2-t9-refund` — Эталоны T9 возврат → человек
- [ ] `as-bv-2-t10-inject` — Эталоны T10 jailbreak/admin
- [ ] `as-bv-2-count-30` — Набрать ≥30 эталонов; цель 50
- [ ] `as-bv-2-pii-review` — Проверка: нет ПДн/реальных user id/токенов

## 3. Код

- [ ] `as-bv-3-module` — Модуль `brand_gold_answers` (данные эталонов)
- [ ] `as-bv-3-flag` — Env `ASSISTANT_BRAND_VOICE_ENABLED` + Settings
- [ ] `as-bv-3-fewshot` — Подмешивать ≤2 эталона в orchestrator по topic
- [ ] `as-bv-3-kb-brand` — Опционально chunk `kb.brand` в KB build
- [ ] `as-bv-3-token-budget` — Лимит размера few-shot (анти-402)

## 4. Тесты и регресс

- [ ] `as-bv-4-unit-gold` — Unit: must_include / must_not на эталонах
- [ ] `as-bv-4-unit-policy` — Регресс bonus/refund/injection/sub-mask
- [ ] `as-bv-4-integ-mock` — Mock LLM: ответ ближе к эталону по T5/T9

## 5. Риски (закрыть контролем)

- [ ] `as-bv-r1-no-dup-happ` — Эталоны не копируют шаги Happ SSOT
- [ ] `as-bv-r2-token-budget` — = см. `as-bv-3-token-budget` (контроль бюджета)
- [ ] `as-bv-r3-policy-lint` — Линт эталонов на запретные обещания
- [ ] `as-bv-r4-no-pii` — = `as-bv-2-pii-review`
- [ ] `as-bv-r5-clarity` — Ревью: ясность важнее «милоты»
- [ ] `as-bv-r6-regress` — = блок §4 тестов зелёный
- [ ] `as-bv-r7-baseline` — = `as-bv-00-baseline`
- [ ] `as-bv-r8-killswitch` — Проверка выключателя бренд-пакета на Contabo
- [ ] `as-bv-r9-no-lora-v11` — Подтвердить: LoRA вне scope v1.1
- [ ] `as-bv-r10-monthly-sync` — Календарь сверки эталонов с FAQ/Happ раз в месяц

## 6. Выкладка и месяц наблюдения

- [ ] `as-bv-5-deploy` — Contabo: код + flag ON
- [ ] `as-bv-5-smoke` — Smoke: T5/T9/T1 в живом боте под админом
- [ ] `as-bv-6-week1` — Неделя 1: выборка 20 диалогов, правки эталонов
- [ ] `as-bv-6-month` — День 30: отчёт CSAT/темы vs baseline
- [ ] `as-bv-6-gate-lora` — Go/No-go: остаёмся на v1.1 или копим пары к LoRA v2

## 7. Явно cancelled / не делать здесь

- `as-bv-x-lora-now` — cancelled: fine-tune не в v1.1  
- `as-bv-x-9router` — cancelled: localhost 9Router не prod  
- `as-bv-x-train-on-raw-logs` — cancelled: сырые логи с ПДн не в эталоны  

---

## Порядок исполнения

```
as-bv-00 → tone doc → 30 gold → code wire → tests → deploy → smoke
→ week1 polish → day30 report → lora gate (обычно NO)
```
