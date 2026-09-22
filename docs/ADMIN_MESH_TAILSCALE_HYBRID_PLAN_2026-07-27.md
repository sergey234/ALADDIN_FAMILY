# ALADDIN Admin Mesh — гибридный план (Tailscale + существующая система)

**Дата:** 2026-07-27  
**Статус:** план (не внедрён)  
**Цель:** админ-плоскость (SSH, агенты Cursor/Hermes, LLM-секреты) без поломки клиентского VPN, бота Stars/Premium и antifake 138+42.

---

## 0. Вердикт (подтверждение / опровержение)

| Утверждение из предыдущего разбора | Вердикт | Комментарий |
|------------------------------------|---------|-------------|
| «Tailscale — лучшее решение для админ-mesh у нас» | **Частично подтвердить** | Лучший *простой* mesh Mac↔2 VPS с identity. Не единственный и **не первый** шаг по риску. |
| «Сначала поставить Tailscale и сразу закрыть SSH с мира» | **Опровергнуть** | Слишком рано. Сначала dual-path + hardening; public SSH резать только после доказанного отката. |
| «Aperture = центральное хранилище всех API-ключей» | **Опровергнуть** | Aperture = **AI gateway** (alpha) для LLM через Tailscale identity. **Не** vault для BOT_TOKEN / LAVA / VPN WG. |
| «wg-bridge заменить Tailscale» | **Опровергнуть** | Разные плоскости. `wg-bridge` (10.10.0.1↔10.10.0.2) — data plane VPN/API. Оставить. |
| «Закрыть все порты кроме Tailscale» | **Опровергнуть** | Публичные `443/8443/51820/8445/8446` и HTTPS nginx — продукт. |
| «Гибрид возможен и лучше для нас» | **Подтвердить** | Hybrid = лучший путь: Phase 0 hardening → Tailscale dual SSH → позже vault LLM → Aperture только для Cursor/agents. |
| «Быстрый откат на текущую систему» | **Подтвердить** | Если public SSH не резать до Phase C; в `~/.ssh/config` держать IP-алиасы. |
| «Hermes на каждом VPS» | **Опровергнуть** | MAIN: Companion/Hermes; Contabo: ASA LLM relay — так и оставить. |
| «P0 = только Tailscale» | **Скорректировать** | **P0a = SSH hardening** (на MAIN сейчас `PasswordAuthentication yes`). **P0b = Tailscale dual-path**. |

### Лучшее решение для ALADDIN (итог)

**Гибрид (рекомендуется):**

1. Оставить **как есть:** публичный VPN/HTTPS, `wg-bridge`, Contabo UFW для `8090/8091` с MAIN, runbooks, Cursor skills.  
2. Добавить **Tailscale** только как admin mesh (Mac + MAIN + Contabo).  
3. **Не** внедрять Aperture в прод бота/backend на старте (alpha; другой scope).  
4. LLM: доделать **уже написанный** `hermes_key_rotator` + `hermes_keys.txt` / env.  
5. Платежи/бот: один SSOT на Contabo `shared/.env`; MAIN bot `.env` заморозить/архивировать.  
6. Закрытие public SSH — **последний** шаг Phase C, с break-glass.

Это лучше «чистого Tailscale как в статье» и лучше «ничего не менять».

---

## 1. Текущий baseline (факт на 2026-07-27)

| Узел | IP | Роль | Admin SSH |
|------|-----|------|-----------|
| MAIN | 149.154.65.180 | backend `:8002`, SFM `:8003`, antifake-worker, nginx | public `22`, password auth **включён** (риск) |
| Contabo | 185.225.233.150 | shop bot, partner `:8090`, vpn-api `:8091`, xray | public `22`, fail2ban **inactive** |
| Mac | local | Cursor agents, deploy | `Host aladdin-server` / `aladdin-contabo` → IP |
| Связь data | `wg-bridge` `:51821` | MAIN `10.10.0.1` ↔ Contabo `10.10.0.2` | ping OK |
| Tailscale | — | нигде | нет |

Секреты: MAIN backend ~79 keys; MAIN bot ~155 (service inactive); Contabo bot ~196; `hermes_keys.txt` отсутствует.

Продукт: 138/138 + 42/42; antifake live; бот Stars/Premium/VPN на Contabo.

---

## 2. Альтернативы и гибрид

| Вариант | Плюсы | Минусы | Для нас |
|---------|-------|--------|---------|
| **A. Только hardening SSH** (keys-only, fail2ban, disable password) | Быстро, без новых зависимостей, мгновенный откат | Нет MagicDNS/identity revoke как у TS; Mac всё ещё по IP | **Обязательный Phase 0** |
| **B. WireGuard admin peer Mac→MAIN** | Уже есть WG экспертиза | На Mac нет `wg`; ручные ключи; нет SSO revoke | Возможен позже, сложнее TS |
| **C. Tailscale admin mesh** | Имена, ACL, revoke устройства, free для 3 узлов | Зависимость от control plane TS; новый софт | **Phase A–B** |
| **D. Cloudflare Tunnel / Zero Trust** | Хорош для HTTP admin | Хуже для произвольного SSH/агентов; другая модель | Не приоритет |
| **E. Aperture** | Централизация LLM для coding agents | Alpha; не для BOT/VPN; нужен Tailscale | **Phase D optional**, только Cursor/Hermes-dev |
| **F. Doppler/1Password/Vault** | Нормальный secrets SSOT | Отдельный продукт/оплата | Альтернатива Aperture для *всех* секретов позже |
| **Гибрид A+C (+E later)** | Максимум пользы / минимум риска | Дисциплина dual-path | **Выбор** |

### Гибридная схема целевая

```
[Mac + Cursor] --Tailscale admin--> [MAIN] --wg-bridge data--> [Contabo]
       |                                  |                         |
   SSH via TS                        public HTTPS              public VPN
   (primary)                         antifake API              bot/xray
       |
   SSH via IP (break-glass, Phase A–B only)
```

---

## 3. Разбор по каждому предложенному пункту

### Пункт 1 — Ops-агент по именам / плейбуки

| | |
|--|--|
| **Суть** | Cursor skills ходят на `aladdin-main` / `aladdin-contabo`, не на сырые IP |
| **+** | Меньше ошибок хоста; единый язык с AGENTS.md |
| **−** | ~critical docs содержат IP (гайд 60+, rules/skills по несколько); нужна dual Host |
| **Риски** | Агент обновит только TS Host → при падении TS деплой ломается |
| **Митигация** | В ssh config: `Host aladdin-server` = TS **или** IP fallback alias `aladdin-server-ip`; skills сначала alias, не hardcode TS-only |
| **Откат** | Вернуть `HostName` на IP в config (1 минута) |
| **Статус** | Делать в Phase B после Tailscale up |

### Пункт 2 — Централизация ключей (бывший «Aperture для всего»)

| | |
|--|--|
| **Суть уточнённая** | (2a) LLM → hermes rotator + keys file; (2b) платежи → Contabo SSOT; (2c) VPN vault → encrypted offline; (2d) Aperture — только later для agents |
| **+** | Убирает дрейф 155 vs 196; второй OpenRouter ключ закрывает известный TODO |
| **−** | Полный vault = проект; Aperture alpha не для prod bot |
| **Риски** | Перенос BOT_TOKEN в чужой SaaS; утечка при sync |
| **Митигация** | Платежи **не** в Aperture; LLM keys только в `/opt/.../secrets` mode 600; never-push VPN handoff сохранить |
| **Откат** | Оставить чтение из существующих `.env` (systemd уже так работает) |
| **Статус** | Phase B: hermes_keys; Phase B: archive MAIN bot env; Phase D: optional Aperture/Doppler |

### Пункт 3 — Закрыть public SSH / доступ только Tailscale

| | |
|--|--|
| **Суть** | UFW: 22 только с `tailscale0` |
| **+** | Главный выигрыш безопасности статьи |
| **−** | Lockout если TS down + нет console |
| **Риски** | **Критический lockout** MAIN/Contabo; ISP/VNC не у всех готов |
| **Митигация** | Phase C только после ≥7 дней dual-path; break-glass: hosting console + временное `ufw allow 22`; держать IP Host в config |
| **Откат** | `ufw allow 22` + `ufw reload` через console / existing session |
| **Статус** | **Не** Phase A; только Phase C |

### Пункт 4 — Установить Tailscale на 3 узла

| | |
|--|--|
| **Суть** | Mac + MAIN + Contabo в одном tailnet |
| **+** | Admin mesh без трогания VPN data plane |
| **−** | Зависимость от Tailscale coordination; ещё один агент на VPS |
| **Риски** | Конфликт маршрутов с `wg0`/`wg-bridge` (редко, но возможен) |
| **Митигация** | `--accept-routes=false` на старте; не advertise VPN subnet клиентам; тест ping TS IP до смены ssh config |
| **Откат** | `tailscale down` / uninstall; SSH по IP как сейчас |
| **Статус** | Phase A |

### Пункт 5 — 10–12 ops-агентов / playbooks

| | |
|--|--|
| **Суть** | deploy-backend, deploy-bot, antifake-ops, … |
| **+** | Уже есть skills — расширяем, не изобретаем |
| **−** | Документационный шум; ложное чувство «20 агентов» |
| **Риски** | Агент рестартит не тот unit; смешает iOS-commit и bot |
| **Митигация** | Жёсткие skills + rules (`no-telegram-bot-in-ios-release`); checklist health до/после |
| **Откат** | Ручной SSH runbook (уже канон) |
| **Статус** | Phase B–C, после стабильного SSH path |

### Пункт 6 — Aperture

| | |
|--|--|
| **Суть статьи** | Gateway LLM keys |
| **Вердикт** | **Не Phase 0–B для продакшена ALADDIN** |
| **+** | Полезно для Cursor/coding agents identity |
| **−** | Alpha; отдельная оплата; не покрывает bot/VPN/JWT |
| **Риски** | Сломать Companion/ASA если перевести прод LLM через alpha gateway |
| **Митигация** | Prod LLM остаётся OpenRouter direct + rotator; Aperture — песочница для Cursor later |
| **Откат** | Не подключать prod `AI_BACKEND` к Aperture до стабильности |
| **Статус** | Phase D optional |

### Пункт 7 — KPI скорость/безопасность/масштаб

| | |
|--|--|
| **Подтвердить KPI** | (1) MTTRинцидент SSH; (2) число живых копий секретов; (3) public SSH exposure |
| **Опровергнуть** | Маркетинговые 200–400% ROI из статьи — не использовать как цель |

### Пункт 8 — Чеклист «начать сейчас»

| Шаг статьи | Наша правка |
|------------|-------------|
| Сразу Tailscale | **Сначала** Phase 0 SSH hardening |
| Сразу закрыть порты | Только после dual-path недели |
| Aperture сразу | **Нет** — после hermes_keys |
| Остальное | Ок в Phase A–B |

### Применимость к 138 / 42 / antifake / bot

| Контур | Меняем? | Как |
|--------|---------|-----|
| iOS 138+42 | Нет функций | Только надёжнее deploy/sfm-truth |
| Antifake | Ops only | nightly drift через admin path; HIBP key optional |
| Bot VPN/Stars/Premium | Deploy path + secrets SSOT | Host Contabo; не трогать xray ports |
| wg-bridge | Не трогать | Data plane |

---

## 4. Риски (сводная) и как избежать

| # | Риск | Вероятность | Ущерб | Как избежать |
|---|------|-------------|-------|--------------|
| R1 | Lockout SSH после UFW | средняя | критический | Dual-path ≥7д; console break-glass; не резать 22 в Phase A–B |
| R2 | Tailscale ↔ wg-bridge route conflict | низкая | высокий (VPN) | `accept-routes=false`; не advertise 10.8.0.0/24 |
| R3 | Агент деплоит не на тот хост | средняя | средний | Dual Host names + smoke health |
| R4 | Утечка секретов в Aperture/SaaS | низкая при отказе | критический | Платежи/VPN не в Aperture |
| R5 | MAIN password SSH brute-force | **уже есть** | высокий | Phase 0: PasswordAuthentication no |
| R6 | Падение Tailscale control plane | низкая | средний | IP fallback Hosts до Phase C; после Phase C — console |
| R7 | Дрейф Contabo vs MAIN bot .env | уже есть | средний | Archive MAIN bot env; SSOT Contabo |
| R8 | Закрыть VPN порты по ошибке | средняя при «закрой всё» | критический | Чеклист «NEVER touch» портов |
| R9 | Hermes single key 429 | уже TODO | средний | hermes_keys 2+ в Phase B |
| R10 | Сломать iOS release ботом | процессный | средний | existing rule no-bot-in-ios-release |

### Порты NEVER TOUCH (без отдельного RFC)

`443/tcp`, `8443/tcp`, `8444/tcp`, `8445/tcp`, `8446/tcp`, `51820/udp`, `51821/udp` (bridge), `80/tcp` (ACME), публичный HTTPS nginx.

Admin-кандидаты на ограничение позже: `22/tcp`, опционально `9100`, прямой `8002` с мира (снаружи и так через nginx).

---

## 5. Быстрый откат на «как сейчас»

| Фаза внедрения | Откат |
|----------------|-------|
| Phase 0 hardening | Вернуть sshd drop-in из бэкапа `/etc/ssh/sshd_config.d/*.bak` |
| Phase A Tailscale installed | `tailscale down`; SSH по IP aliases |
| Phase B ssh config → MagicDNS | В `~/.ssh/config` вернуть `HostName` IP (или использовать `*-ip` Host) |
| Phase B hermes_keys | Убрать `HERMES_OPENROUTER_KEYS_FILE`; оставить `OPENROUTER_API_KEY` |
| Phase C UFW deny public 22 | Через hosting VNC/console: `ufw allow 22/tcp && ufw reload` |
| Docs/skills | IP в канонических гайдах **не удалять** до Phase C+; добавлять TS рядом |

**Критерий «можем быстро переключиться назад»:** пока Phase C не сделан — **да, <5 минут**. После Phase C — да, через console (заложить доступ к панели Contabo/FirstVDS заранее).

---

## 6. План реализации (фазы)

### Phase 0 — Hardening без Tailscale (1 вечер) — **СДЕЛАТЬ ПЕРВЫМ**

1. Бэкап sshd config на MAIN и Contabo.  
2. MAIN: `PasswordAuthentication no` (сейчас **yes** — подтверждено).  
3. Contabo: убедиться password off; включить fail2ban.  
4. Проверка: SSH ключом OK; паролем FAIL.  
5. Не менять UFW 22 Anywhere пока.

**DoD:** ключ-only SSH на обоих; fail2ban active на Contabo (+ MAIN если нужно).

### Phase A — Tailscale dual-path (1–2 часа + 7 дней наблюдения)

1. Аккаунт Tailscale (GitHub/Google).  
2. Mac: установить Tailscale, `tailscale up`.  
3. MAIN + Contabo: установить, имена `aladdin-main`, `aladdin-contabo`.  
4. ACL: только ваш user → `tag:server`.  
5. `~/.ssh/config` — **добавить**, не заменить:

```sshconfig
Host aladdin-server-ts
    HostName aladdin-main
    User root
    IdentityFile ~/.ssh/aladdin_server
    IdentitiesOnly yes

Host aladdin-contabo-ts
    HostName aladdin-contabo
    User root
    IdentityFile ~/.ssh/aladdin_server
    IdentitiesOnly yes

# существующие aladdin-server / aladdin-contabo ОСТАВИТЬ на IP (break-glass)
```

6. Смоук: `ssh aladdin-server-ts hostname`; health HTTPS; bot; один VPN `/ready` или docs smoke.  
7. Проверить отсутствие route conflict с `wg-bridge`.

**DoD:** TS ping/SSH OK; IP SSH OK; VPN/bot/antifake без регрессии ≥7 дней.

### Phase B — Секреты LLM + SSOT бота + soft docs (2–4 часа)

1. Создать `/opt/aladdin-backend/secrets/hermes_keys.txt` (2+ ключа, mode 600).  
2. Env: `HERMES_OPENROUTER_KEYS_FILE=...` (rotator уже в коде).  
3. Смоук Companion/ASA LLM.  
4. MAIN: пометить bot `shared/.env` как ARCHIVED / не использовать; SSOT = Contabo.  
5. Скрипт `scripts/admin_secrets_drift_names.sh` — diff **имён** ключей Contabo vs `env.example` (без печати значений).  
6. В `AGENTS.md` / skills: «предпочтительно `*-ts` Host; IP — fallback».  
7. Playbooks (минимальный набор): deploy-backend, deploy-bot, antifake-ops, vpn-health, payments-smoke.

**DoD:** rotator видит ≥2 ключа; drift script green; деплой через `*-ts` успешен один раз.

### Phase C — Ограничить public SSH (только после Phase A DoD)

1. Убедиться: доступ к console FirstVDS + Contabo panel.  
2. UFW: allow 22 с `tailscale0` (или TS CGNAT range по ACL); deny public 22.  
3. **Не** трогать VPN/HTTPS порты.  
4. Тест: TS SSH OK; с «чужой» сети 22 закрыт.  
5. Документировать break-glass в этом файле §5.

**DoD:** public 22 закрыт; break-glass проверен на бумаге; продукт жив.

### Phase D — Optional (не блокер)

1. Doppler/1Password для LLM+ops (не платежи в облако без отдельного решения).  
2. Aperture **только** для Cursor coding agents (не prod gunicorn Companion до стабильности alpha).  
3. Поджать MAIN: FTP/mail если не нужны (отдельный RFC).  
4. HIBP_API_KEY для antifake dark_web email (продукт, не mesh).  
5. Расширить до 10–12 playbooks.

---

## 7. Чеклист смоука после каждой фазы

```text
[ ] curl -sS -m 8 https://aladdin-ai.ru/api/health → {"status":"ok"}
[ ] https://aladdin-ai.ru/api/antifake/capabilities → model_version есть
[ ] Contabo: systemctl is-active aladdin-telegram-bot partner-api shop-vpn-api
[ ] MAIN: systemctl is-active aladdin-backend aladdin-antifake-worker
[ ] ping 10.10.0.1↔10.10.0.2 (wg-bridge)
[ ] SSH IP alias ещё работает (до Phase C)
[ ] SSH TS alias работает (с Phase A)
[ ] Бот: /start или admin health по runbook
[ ] VPN: не регрессировать выдачу профиля (короткий /ready или known smoke)
```

---

## 8. Post-plan verification — ничего не забыли?

| Тема | Покрыто? | Где |
|------|----------|-----|
| Лучшее ли решение / гибрид | ✅ | §0, §2 |
| +/− по каждому пункту 1–8 | ✅ | §3 |
| Риски + митигация | ✅ | §4 |
| Откат на текущую систему | ✅ | §5 |
| План фаз с DoD | ✅ | §6 |
| VPN порты never-touch | ✅ | §4 |
| wg-bridge сохранить | ✅ | §0, §2 |
| Aperture scope исправлен (не vault всего) | ✅ | §0, §3.6 |
| hermes_keys / rotator | ✅ | §6 Phase B |
| MAIN bot env drift | ✅ | §6 Phase B |
| Password SSH MAIN (важнее TS) | ✅ | §0, Phase 0 |
| fail2ban Contabo | ✅ | Phase 0 |
| Dual SSH Host rollback | ✅ | Phase A, §5 |
| 138/42 / antifake / bot impact | ✅ | §3 конец |
| Cursor skills IP coupling | ✅ | §3.1, Phase B |
| Lockout / console break-glass | ✅ | R1, Phase C |
| Route conflict TS vs WG | ✅ | R2, Phase A |
| Не смешивать 3 типа агентов | ✅ | введение цели |
| Не коммитить VPN §32 | ✅ | §3.2 |
| KPI без маркетинг-цифр | ✅ | §3.7 |
| HIBP / MAIN UFW mail — later | ✅ | Phase D |
| Конкретные install-скрипты | ⏳ | следующий артефакт по запросу |

**Итог проверки плана:** пункты Tailscale/Aperture разобраны; путь — **гибрид 0→S→A→B→C→D→R** (39 задач в Cursor). Быстрый откат до Phase C. Phase R и сводный счётчик — §14 (синхронизировать с Todo).

---

## 9. Следующий артефакт (по запросу)

- `scripts/admin_mesh/install_tailscale_node.sh`  
- `scripts/admin_mesh/ssh_config_dual_path.example`  
- `scripts/admin_mesh/ufw_ssh_tailscale_only.sh` (только Phase C)  
- `scripts/admin_secrets_drift_names.sh`  

Не запускать Phase C скрипты без явного ок владельца.

---

## 13. Phase S — Чек-лист восстановления ВСЕХ секретов (отдельно от mesh)

**Канон шаблона:** `docs/ALADDIN_SECRETS_RECOVERY_CHECKLIST_PLAN_2026-07-27.md`

**Важно:** задачи mesh (0/A/B/C) **не** складывают все ключи в одно авто-хранилище. Phase S — ручное офлайн-заполнение карты секретов для 2 проектов (iOS/MAIN + bot/VPN Contabo). Единый Todo = **39** (0+S+A+B+C+D+R), см. §14.

| Правило | |
|---------|--|
| На серверах | Только чтение при инвентаризации; **не** удалять / не менять / не добавлять |
| В git | Только шаблон имён и «где лежит»; **без значений** |
| Заполнение | Офлайн: 1Password / Bitwarden / `~/ALADDIN_VPN_SAFE` |
| Без скриптов | Копирование значений — вручную владельцем |

### Порядок Phase S (параллельно Phase 0, до Phase C)

1. S1 Доступ (SSH, панели хостеров, позже Tailscale codes)  
2. S3 Бот Contabo SSOT (платежи Stars/Premium/VPN)  
3. S4 VPN API + WG/Xray + связка с `ALADDIN_VPN_SAFE`  
4. S2 MAIN backend / APNS / LLM / antifake  
5. S5 ASA relay  
6. S6–S7 БД и кабинеты  
7. S8 Бумажный тест «сможем восстановить?»  

**Блокер:** Phase C (закрыть SSH) нельзя без заполненного S1 (панели FirstVDS/Contabo).

---

## 14. Phase R — оператор агентов (из выпуска Ryan Carson) + сводный Todo

**Источник обсуждения:** Greg Isenberg + Ryan Carson — *Most Valuable Skill of 2026: Managing AI Agents* (YouTube `vJEy3nP2_C8`).

**Важно:** Devin / Ugmonk kit / 8 мониторов / 40 PR/день — **не** входят в обязательный Todo (сознательно). Cursor остаётся harness; R — привычки + автопроверки.

| ID | Задача | Когда |
|----|--------|--------|
| R.1 | Агентам нельзя постоянный prod-write (секреты из сейфа по запросу) | с Phase S |
| R.2 | Pin 1–2 задач дня + проверка ~25 мин (бумага/заметка = аналог Ugmonk Today) | каждый день |
| R.3 | Parent=план/ревью, children=дешёвые модели (router) | с Phase B |
| R.4 | E2E smoke раз в неделю: сайт/health + бот + VPN ready | после B.6 |
| R.5 | Утренний watchdog-отчёт (health, bot units, antifake, wg-bridge) | после A/B |
| R.6 | Алерты Telegram/Slack при падении smoke/watchdog | с R.4–R.5 |
| R.7 | Раз в неделю: сам пройти app + бот глазами | постоянно |
| R.8 | После деплоя: короткий phone-чеклист без полного SSH | после A |

### Сводный порядок (канон Cursor Todo = **39 задач**)

```
0 (4) → S (9) → A (7) → B (6) → C (3) → D (2 опц.) → R (8)
```

| Блок | Кол-во | Документ |
|------|--------|----------|
| Phase 0 | 4 | этот файл §6 |
| Phase S | 9 | `ALADDIN_SECRETS_RECOVERY_CHECKLIST_PLAN_2026-07-27.md` + §13 |
| Phase A–D | 7+6+3+2 | этот файл §6 |
| Phase R | 8 | этот §14 |
| **Итого** | **39** | Cursor Todo (единый список) |

**Синхронизация:** при изменении фаз обновлять **и** этот файл, **и** Cursor Todo.

---

## 10. Шесть шляп де Боно — стресс-тест плана

### 🤍 Белая (факты)

- MAIN: `PasswordAuthentication yes`, `PermitRootLogin yes`; fail2ban **active**.
- Contabo: fail2ban **inactive**; password auth смешан (cloud-init `no` + другие конфиги — проверить effective).
- Tailscale / `wg` на Mac: **нет**.
- `wg-bridge` ping OK; продукт HTTPS/antifake/bot live.
- Aperture = AI gateway (alpha), не secrets vault для бота.
- В репо critical guides завязаны на IP (`ALADDIN_SERVER_CONNECTION_GUIDE` ~60 упоминаний).

**Вывод белой:** план опирается на проверяемые факты; «только улучшения без фактов» — нет.

### ❤️ Красная (ощущения / доверие)

- Страх lockout после закрытия 22 — **обоснован** → Phase C отложен.
- Доверие к статье «закрой всё» — **опасно** для VPN-продукта.
- Спокойствие даёт dual-path (IP + TS) и Phase 0 без новых вендоров.

### 🖤 Чёрная (риски — честно: это НЕ «только плюсы»)

| Что может ухудшиться | Как |
|----------------------|-----|
| Скорость ops | На старте **медленнее**: установка TS, dual Host, обучение агентов |
| Сложность | +1 control plane (Tailscale) + дисциплина фаз |
| Доступность admin | После Phase C зависимость от TS/console |
| Ошибка Phase 0 | Выключить password **до** проверки что ключ работает с вашей машины → lockout |
| hermes_keys | Неверный формат/права → Companion 401 до фикса |
| «Архив» MAIN bot .env | Если кто-то случайно включит MAIN bot со старым env → рассинхрон платежей |

**Вердикт чёрной:** путь правильный **при дисциплине фаз**; без Phase 0→A→B порядка — опаснее текущего.

### 💛 Жёлтая (выгоды — где реально лучше)

| Область | Улучшение |
|---------|-----------|
| Безопасность | Выключить password SSH = самый большой win сейчас |
| MTTR после привыкания | Имена хостов + playbooks < ручной IP-хаос |
| LLM устойчивость | 2+ ключа rotator |
| Секреты бота | Один SSOT Contabo |
| Масштаб до 5 VPS | Mesh заложен до роста |

Функциональность **продукта** (138/42, antifake, VPN, Stars) **не ускоряется сама по себе** — ускоряется **админка и надёжность ops**.

### 💚 Зелёная (альтернативы / креатив)

- Только Phase 0 (hardening) без Tailscale — валидный минимум, если не хотите вендора.
- WG admin peer Mac→MAIN вместо TS — возможна, но на Mac нет `wg`, дольше.
- Оставить public 22 навсегда + keys-only + fail2ban — компромисс «80% безопасности без Phase C».
- Aperture later только для Cursor; prod LLM — rotator.

### 💙 Синяя (управление процессом)

**Правильный порядок:** 0 → A (7 дней) → B → C (опционально) → D.  
**Запрещено:** прыгать к «закрой 22» или «Aperture в прод».  
**KPI:** (1) password SSH off, (2) dual SSH OK 7д, (3) число живых `.env` копий бота = 1, (4) hermes keys ≥2.  
**Не KPI:** маркетинговый ROI из статьи.

### Итог 6 шляп

| Вопрос | Ответ |
|--------|-------|
| Самый правильный путь для ALADDIN? | **Да — гибрид**, не «чистая статья» |
| Всё будет только быстрее и функциональнее? | **Нет.** Сначала кратко сложнее/медленнее; продукт не «ускоряется»; выигрыш — безопасность и ops |
| Риски предусмотрены? | Да в §4 + чёрная шляпа; критичные — lockout и route conflict |

---

## 11. Что УБИРАЕМ из статьи (отдельный список)

Ниже — пункты статьи / раннего предложения, которые **сознательно не делаем** (или откладываем). Не «забыли» — **отказались**.

### U1. «Закрой все порты, оставь только Tailscale»

| | |
|--|--|
| **Почему убираем** | Убьёт клиентский VPN/HTTPS (продукт) |
| **Риск отказа** | Admin-порты (`22`, лишний `8002`) останутся дольше публичными |
| **Как предотвратить риск отказа** | Phase 0 keys-only; Phase C — **только SSH/admin**, never-touch список портов VPN |
| **Можно вернуть частично?** | Да: закрыть только `22` (Phase C), не «все порты» |

### U2. Замена `wg-bridge` на Tailscale

| | |
|--|--|
| **Почему убираем** | Data plane уже работает; TS не для user VPN traffic |
| **Риск отказа** | Два туннеля жить рядом (сложность) |
| **Митигация** | `accept-routes=false`; не advertise VPN subnets в TS |
| **Вернуть?** | Нет — не цель |

### U3. Aperture как хранилище BOT_TOKEN / LAVA / VPN keys

| | |
|--|--|
| **Почему убираем** | Aperture = LLM gateway alpha; не платежный vault; compliance/риск утечки |
| **Риск отказа** | LLM-ключи всё ещё в `.env` до Phase B |
| **Митигация** | `hermes_keys.txt` + rotator (уже код); платежи SSOT Contabo; VPN → `ALADDIN_VPN_SAFE` |
| **Вернуть?** | Aperture **только** Phase D для Cursor agents, не для бота |

### U4. Немедленное закрытие public SSH (день 1)

| | |
|--|--|
| **Почему убираем из старта** | Lockout без доказанного dual-path и console |
| **Риск отказа** | Дольше окно brute-force на 22 |
| **Митигация** | Phase 0: password off + fail2ban Contabo; потом 7 дней TS |
| **Вернуть?** | Да, как Phase C |

### U5. Hermes / полный AI-стек на каждом VPS

| | |
|--|--|
| **Почему убираем** | Уже разделено: Companion/Hermes MAIN, ASA relay Contabo |
| **Риск отказа** | Нет «единого» Hermes everywhere как в статье |
| **Митигация** | Не нужен; мониторить оба сервиса playbooks |
| **Вернуть?** | Нет |

### U6. «20 агентов сразу»

| | |
|--|--|
| **Почему убираем** | Хаос документации; skills уже есть |
| **Риск отказа** | Медленнее автоматизация редких сценариев |
| **Митигация** | Старт: 5 playbooks; до 12 в Phase D |
| **Вернуть?** | Постепенно |

### U7. Полный перенос всех секретов в облачный vault в Phase 0–B

| | |
|--|--|
| **Почему убираем** | Объём, риск миграции платежей |
| **Риск отказа** | Остаётся ручной `.env` |
| **Митигация** | Drift script по именам; archive MAIN bot env |
| **Вернуть?** | Doppler/1Password в Phase D по желанию |

### U8. Слепая вера в ROI 200–400% / «85% процессов»

| | |
|--|--|
| **Почему убираем** | Маркетинг, не измеримо для ALADDIN |
| **Риск отказа** | Нет «красивой» метрики для C-level |
| **Митигация** | KPI: MTTR, password-off, 1× bot env, keys≥2 |

### Что ОСТАВЛЯЕМ из статьи (не убирать)

| Пункт статьи | Статус в плане |
|--------------|----------------|
| Частная сеть для admin | ✅ Tailscale Phase A |
| Доступ по имени | ✅ MagicDNS + ssh Host |
| Identity / revoke устройства | ✅ Tailscale ACL |
| Не держать ключи на 7 VPS как хаос | ✅ SSOT + hermes_keys (без Aperture) |
| Оркестрация с «главного» Mac | ✅ Cursor skills |
| Поэтапность | ✅ усилена (0→A→B→C) |

---

## 12. Ответ на «только улучшения / быстрее / функциональнее?»

| Утверждение | Вердикт |
|-------------|---------|
| Продукт (iOS/antifake/VPN/бот) станет быстрее для пользователей | **Нет** (и не цель) |
| Админ-работа станет быстрее с дня 1 | **Нет** — сначала медленнее на настройку |
| Админ-работа станет быстрее через 1–2 недели после Phase A–B | **Да**, при привыкании к Host/playbooks |
| Безопасность улучшится уже на Phase 0 | **Да** (password off) — главный быстрый win |
| Функциональность 138+42 вырастет от mesh | **Нет** — только надёжнее выкат/smoke |
| Это самый правильный путь vs «статья as-is» | **Да** |
| Это самый правильный путь vs «ничего не делать» | **Да** (из-за password SSH на MAIN) |
| Риски нулевые | **Нет** — см. чёрную шляпу и §4 |

**Формула:** правильный путь = **не максимум фич из статьи**, а **максимум пользы при контролируемом риске**.
