# OPS Phase 2 Todo Tracker (короткий)

Назначение: единый короткий список задач по `docs/OPS_PHASE2_PLAN.md` для контроля выполнения и выката.

Как отмечать:
- `[ ]` не начато
- `[~]` в работе
- `[x]` готово
- В `PR/Issue` указывать ссылку на PR/задачу

## 0) Цели OPS-фазы (контроль достижения)

- [ ] Глобальные лимиты работают одинаково на нескольких инстансах
- [ ] Алерты доставляются в дежурный канал без просмотра логов
- [ ] Повторный инвойс контролируется через БД (межпроцессно)
- [ ] Сторно/споры обрабатываются по событиям провайдеров (идемпотентно)
- [ ] CI/CD выката воспроизводим и есть rollback
- [ ] Break-glass (`adm:paidbg`) под строгим аудитом

---

## 1) Распределённый rate limit (`memory|redis`)

- [x] Вынести `RateLimitStore` абстракцию
- [x] Реализовать `MemoryRateLimitStore`
- [x] Реализовать `RedisRateLimitStore`
- [x] Добавить конфиг: `PARTNER_API_RATE_LIMIT_BACKEND`, `REDIS_*`/`REDIS_URL`
- [x] Добавить fallback на in-memory при падении Redis + warning/alert
- [x] Тест: 2 воркера -> 1 общий лимит
- [x] Добавить edge rate-limit на Nginx для webhook/API
- [x] Обновить runbook (установка/мониторинг Redis)

PR/Issue: `...`  
Owner: `...`  
ETA: `...`

---

## 2) Алерты (Telegram/PagerDuty)

- [x] Сделать единый `send_alert(severity, title, body, dedupe_key)`
- [x] Добавить env-конфиг (`ALERTS_ENABLED`, Telegram/PagerDuty ключи)
- [x] Реализовать дедуп/кулдаун (`ALERT_COOLDOWN_SECONDS`)
- [x] Подключить алерты к webhook errors (HTTP>=400/исключения)
- [x] Подключить алерты к stuck paid monitor
- [ ] Опционально: алерт при Redis down
- [ ] Смоук на staging: 1 тестовый инцидент = 1 алерт

PR/Issue: `...`  
Owner: `...`  
ETA: `...`

---

## 3) Повторный инвойс через SQLite (транзакционно)

- [x] Добавить поле `invoice_last_requested_at` в `orders`
- [x] (Опционально) добавить `invoice_last_provider`, `invoice_last_external_id`
- [x] Проверка кулдауна в транзакции `BEGIN IMMEDIATE`
- [x] Вынести проверку в repo-функцию (`assert_invoice_request_allowed`)
- [x] Подключить в checkout (fiat + crypto)
- [x] Убрать/минимизировать зависимость от in-memory кулдауна
- [x] Тест параллельности: 2 попытки -> вторая отклоняется в окне кулдауна

PR/Issue: `...`  
Owner: `...`  
ETA: `...`

---

## 4) Сторно / dispute (L2/L3)

- [ ] Исследовать API LAVA/Crypto Pay/xRocket (refund/dispute/cancel hooks)
- [ ] Ввести таблицу/модель `payment_provider_events`
- [ ] Добавить обработку входящих provider events
- [ ] Гарантировать идемпотентность повторной доставки
- [ ] Составить матрицу `provider event -> order status`
- [ ] Для старта: безопасный путь `payment_disputed` + ручное подтверждение `refunded`

PR/Issue: `...`  
Owner: `...`  
ETA: `...`

---

## 5) CI/CD выката

- [x] PR workflow: автотесты (`pytest`)
- [x] Deploy workflow: `workflow_dispatch`/tag + SSH deploy
- [ ] Завести секреты (`SSH_KEY`, `HOST`, `ROOT`, env при необходимости)
- [~] Dry-run первого прод-запуска с человеком (workflow готов, нужен прогон в GitHub)
- [x] Документировать rollback (переключение симлинка на прошлый release)
- [ ] Проверка post-deploy health (`127.0.0.1:8090/health` + внешний check)

PR/Issue: `...`  
Owner: `...`  
ETA: `...`

---

## 5.5) Break-glass hardening (`adm:paidbg`)

- [x] Добавить чеклист доказательств в `docs/RUNBOOK.md`
- [x] Сделать обязательные audit-поля: `reason_code`, `provider`, `external_invoice_id`, `evidence_ref`
- [x] Ограничить ролью `SUPER_ADMIN_IDS`
- [x] Ввести правило «вторые глаза» для сумм выше порога
- [x] Отправлять алерт на каждое `adm:paidbg`
- [x] Ввести периодический отчёт по всем break-glass операциям

PR/Issue: `...`  
Owner: `...`  
ETA: `...`

---

## 6) Порядок внедрения (рекомендованный)

- [ ] Шаг 1: Алерты
- [ ] Шаг 2: Инвойс в БД
- [ ] Шаг 3: Break-glass hardening
- [ ] Шаг 4: Redis лимиты + edge лимиты
- [ ] Шаг 5: CI/CD
- [ ] Шаг 6: Сторно API

---

## 7) Риски, откат, оценка

- [ ] Для каждого блока заполнен риск
- [ ] Для каждого блока заполнен rollback
- [ ] Для каждого блока указан ETA
- [ ] Сверены ориентиры:
  - Break-glass: `0.5-2 дн`
  - Алерты: `1-3 дн`
  - Инвойс в БД: `2-5 дн`
  - Redis лимиты: `3-7 дн`
  - CI/CD: `2-5 дн`
  - Сторно API: `1+ нед`

---

## 8) Что делать прямо сейчас (операционный минимум)

- [ ] Идти по порядку: `2 -> 3 -> 5.5 -> 1 -> 5 -> 4`
- [ ] Вести отметки прогресса в PR (или синхронно в Notion/Jira)
- [ ] Перед прод-выкатом пройти `docs/ML_SYSTEM_HANDOFF_FINAL.md` чеклист
- [ ] Сделать внешний/внутренний health-check после релиза
- [ ] Обновить статус этого файла после каждого merge

---

## Статус спринта (1 строка)

Текущий фокус: `§5 CI/CD` | Следующий блок: `§4 Сторно/dispute` | Риск: `нужны GitHub secrets и первый dry-run` | Дата обновления: `2026-04-22`
