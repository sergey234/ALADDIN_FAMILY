# Family API — автопочинка при поломке (план)

**Версия:** 1.0 · **2026-06-16**  
**Контекст:** smoke каждые 30 мин **ловит** поломку; сейчас **чинит** человек. Ниже — что можно автоматизировать безопасно.

---

## 1. Простыми словами: что можно и что нельзя

| Ситуация | Авто-починка? | Почему |
|----------|---------------|--------|
| Сервер «завис» / временный сбой БД | **Да** — перезапуск + повтор теста | Часто помогает без смены кода |
| После плохого деплоя сломался `family/create` | **Частично** — откат файлов на **последнюю зелёную** версию | Код возвращается к тому, что проходило smoke |
| Новый баг в логике (как вчера с INTEGER) | **Нет** — нужен новый фикс в коде | Робот не придумает патч сам |
| Поломка только на телефоне (баг iOS) | **Нет** — только серверный контур | Smoke не трогает приложение |

**Итог:** автопочинка = **«вернуть сервер к последнему рабочему состоянию»**, а не «заменить разработчика».

---

## 2. Целевое поведение (как для пользователя)

1. Smoke упал → система **сама** пробует починить (перезапуск → откат).
2. Если через N минут снова **зелёный** smoke → пользователи снова могут создавать семью **без** вашего участия.
3. Если не помогло → Telegram: **«нужен человек»** (как сейчас, но позже).

На iPhone по-прежнему **ничего не мигает** — меняется только то, работает ли API.

---

## 3. Три уровня автопочинки (по приоритету)

### Уровень A — «Пнуть сервер» (P0, простой)

**Когда:** periodic smoke упал впервые за час.

**Действия:**
1. `systemctl restart aladdin-backend`
2. Подождать 5 с
3. Снова `test_family_prod_smoke.py`

**Если прошло** → записать в лог `auto_remediate: restart_ok`, Telegram не слать (или короткое «само восстановилось»).

**Скрипт:** `scripts/family_auto_remediate.sh --phase restart`

---

### Уровень B — «Откат к последней зелёной версии» (P1, главный)

**Когда:** после A smoke всё ещё красный.

**Нужно заранее:**
- При **успешном** `deploy_family_backend.sh` или smoke писать файл:
  - `/var/lib/aladdin/family_last_good_backup.txt` → путь к `.deploy_backups/family_YYYYMMDD_HHMMSS`

**Действия:**
1. Прочитать путь к last-good backup
2. Восстановить `auth_router.py` + `family.py` из бэкапа
3. `py_compile` + `restart aladdin-backend`
4. Smoke снова

**Если прошло** → Telegram: «был откат на family_…, smoke OK».

**Если нет** → Telegram: «автооткат не помог, нужен разработчик».

**Скрипт:** `scripts/family_auto_remediate.sh --phase rollback`

---

### Уровень C — «Не выкатывать плохое» (уже почти есть → усилить P1)

**Когда:** **во время** деплоя smoke красный.

**Сейчас:** `deploy_family_backend.sh` падает с exit 1, но файлы **уже** на сервере.

**Улучшение:**
- Если post-deploy smoke FAIL → **сразу** вызвать rollback на backup **этого же** деплоя (создан до scp) + smoke
- Деплой считается failed, но прод возвращается к предыдущему рабочему коду

**Скрипт:** доработка `deploy_family_backend.sh` (блок `on_smoke_fail_rollback`).

---

### Уровень D — НЕ делаем в v1

- Автоматический `git pull` / правка кода агентом
- Автоматический BIGINT migration
- Авто-удаление семей пользователей

---

## 4. Как связать с тем, что уже есть

```
Каждые 30 мин:  aladdin-family-prod-smoke.timer
                      │
                      ▼ FAIL
              family_auto_remediate.sh
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
    restart      rollback      alert human
    (уровень A)  (уровень B)   (если B fail)

Каждые 15 мин:  family_ops_alerts.py
                      │
                      ▼ если stale / errors
              (опционально) запуск remediate
```

После деплоя: `deploy_family_backend.sh` → smoke OK → обновить `family_last_good_backup.txt`.

---

## 5. Риски (простым языком)

| Риск | Как смягчить |
|------|----------------|
| Откатим старый код, но баг был в БД | После отката всё равно alert человеку |
| Last-good backup устарел | Обновлять только после `pass: true` |
| Дважды откат подряд | Cooldown 1 ч на rollback |
| Ложный FAIL smoke (сеть) | Сначала только restart + 2 retry |

---

## 6. Cursor TODO (реализация)

| ID | Задача | Приоритет |
|----|--------|-----------|
| `fam-auto-01` | `family_auto_remediate.sh`: фаза restart + retry smoke (×2) | P0 |
| `fam-auto-02` | Писать `family_last_good_backup.txt` при успешном smoke/deploy | P0 |
| `fam-auto-03` | `family_auto_remediate.sh`: фаза rollback из last-good | P1 |
| `fam-auto-04` | Подключить remediate к timer: `OnFailure=` или wrapper в service | P1 |
| `fam-auto-05` | `deploy_family_backend.sh`: auto-rollback при FAIL post-deploy smoke | P1 |
| `fam-auto-06` | `family_ops_alerts.py`: при stale smoke вызывать remediate (cooldown) | P2 |
| `fam-auto-07` | Telegram тексты: recovered / rollback_ok / need_human | P2 |
| `fam-auto-08` | Runbook + § в server guide «автопочинка» | Doc |
| `fam-auto-09` | Dry-run режим `--dry-run` для теста на prod | Doc |

**Оценка:** уровни A+B+C ≈ **4–6 часов** работы + один тестовый прогон на VPS.

---

## 7. Definition of Done (автопочинка v1)

- [ ] Smoke падает → в течение ~2 мин выполняется restart + retry
- [ ] Всё ещё падает → откат на last-good + smoke
- [ ] Успех → timestamp smoke обновлён, пользовательский create снова работает
- [ ] Провал → Telegram «need human»
- [ ] Плохой деплой не оставляет прод в сломанном состоянии (rollback в deploy)

---

*Связано: `FAMILY_PROD_SMOKE_IMPLEMENTATION_PLAN.md`, `RUNBOOK_FAMILY_DEPLOY_ROLLBACK.md`*
