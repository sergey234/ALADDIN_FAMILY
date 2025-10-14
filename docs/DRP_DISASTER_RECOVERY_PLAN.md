# 🔄 DRP - DISASTER RECOVERY PLAN (План Восстановления после Катастроф)

## 📋 СОДЕРЖАНИЕ

1. [Обзор плана](#обзор-плана)
2. [Классификация катастроф](#классификация-катастроф)
3. [Стратегия восстановления](#стратегия-восстановления)
4. [Процедуры восстановления](#процедуры-восстановления)
5. [Тестирование плана](#тестирование-плана)
6. [Обновление плана](#обновление-плана)

---

## 🎯 ОБЗОР ПЛАНА

### Цель DRP
Обеспечить быстрое восстановление критических сервисов ALADDIN после катастрофических событий.

### Scope (Область применения)
- Полный отказ сервера
- Потеря датацентра
- Крупномасштабные катастрофы
- Ransomware на всю инфраструктуру
- Природные катастрофы

### Business Continuity Objectives

| Метрика | Цель | Описание |
|---------|------|----------|
| **RTO** (Recovery Time Objective) | < 4 часа | Максимальное время восстановления |
| **RPO** (Recovery Point Objective) | < 15 минут | Максимальная потеря данных |
| **MTPD** (Maximum Tolerable Period of Disruption) | < 24 часа | Критический порог |

---

## 🌪️ КЛАССИФИКАЦИЯ КАТАСТРОФ

### TIER 1: КРИТИЧЕСКАЯ КАТАСТРОФА 🔴

**RTO:** 2 часа  
**RPO:** 5 минут

#### Примеры:
- Полный отказ primary датацентра
- Ransomware на всех серверах
- Потеря всех баз данных
- Крупномасштабный взлом

#### Воздействие:
- 100% downtime
- Все пользователи затронуты
- Потеря бизнеса > $10K/час

---

### TIER 2: СЕРЬЁЗНАЯ КАТАСТРОФА 🟠

**RTO:** 4 часа  
**RPO:** 15 минут

#### Примеры:
- Отказ 50%+ серверов
- Потеря primary БД
- Критический bug в production
- DDoS > 50 Гбит/с

#### Воздействие:
- 50-80% функций недоступны
- Большинство пользователей затронуты
- Потеря бизнеса > $1K/час

---

### TIER 3: ЧАСТИЧНАЯ КАТАСТРОФА 🟡

**RTO:** 8 часов  
**RPO:** 30 минут

#### Примеры:
- Отказ вспомогательных сервисов
- Проблемы с single region
- Degraded performance

---

## 🛠️ СТРАТЕГИЯ ВОССТАНОВЛЕНИЯ

### 3-2-1 BACKUP СТРАТЕГИЯ

```
3 - ТРИ КОПИИ ДАННЫХ
    ├── Production Database (primary)
    ├── Hot Standby (реплика в реальном времени)
    └── Daily Backup (полная копия)

2 - ДВА РАЗНЫХ ТИПА ХРАНИЛИЩА
    ├── Local SSD (быстрое восстановление)
    └── Cloud Storage (долгосрочное хранение)

1 - ОДНА КОПИЯ OFFSITE
    └── AWS S3 Glacier (географически удалённое хранилище)
```

### BACKUP SCHEDULE

| Тип | Частота | Retention | Хранилище |
|-----|---------|-----------|-----------|
| **Full Backup** | Ежедневно 02:00 UTC | 30 дней | S3 + Local |
| **Incremental** | Каждые 6 часов | 7 дней | Local |
| **Transaction Log** | Каждые 15 минут | 24 часа | Local + S3 |
| **Config Backup** | При каждом изменении | 90 дней | Git + S3 |

---

## 🔄 ПРОЦЕДУРЫ ВОССТАНОВЛЕНИЯ

### ПРОЦЕДУРА 1: ВОССТАНОВЛЕНИЕ ИЗ BACKUP

#### Шаг 1: Оценка ситуации (0-15 минут)

```bash
# 1. Проверить статус primary системы
systemctl status aladdin-*

# 2. Проверить доступность backup
ls -lh /backups/daily/
aws s3 ls s3://aladdin-backups/

# 3. Определить последний чистый backup
# (до инцидента)
```

#### Шаг 2: Подготовка окружения (15-30 минут)

```bash
# 1. Запустить резервный сервер (если нужно)
terraform apply -var="use_backup_server=true"

# 2. Проверить сетевое подключение
ping backup-server.aladdin.family

# 3. Создать рабочий каталог
mkdir -p /recovery/$(date +%Y%m%d)
cd /recovery/$(date +%Y%m%d)
```

#### Шаг 3: Восстановление данных (30-90 минут)

```bash
# 1. Остановить все сервисы
systemctl stop aladdin-api aladdin-worker

# 2. Восстановить базу данных
# Из local backup (быстро!)
pg_restore -d aladdin_db /backups/daily/aladdin_$(date +%Y%m%d).dump

# Или из S3 (медленнее)
aws s3 cp s3://aladdin-backups/daily/aladdin_20251011.dump .
pg_restore -d aladdin_db aladdin_20251011.dump

# 3. Восстановить конфигурации
git checkout production
git pull origin production

# 4. Восстановить статические файлы
rsync -av /backups/static/ /var/www/aladdin/static/

# 5. Проверить целостность
python3 scripts/verify_data_integrity.py
```

#### Шаг 4: Проверка и тестирование (90-105 минут)

```bash
# 1. Запустить сервисы
systemctl start aladdin-api

# 2. Health check
curl https://aladdin.family/health

# 3. Smoke tests
python3 tests/smoke_tests.py

# 4. Проверить критические функции
- Регистрация семьи ✅
- Логин ✅
- API endpoints ✅
- Payment ✅
```

#### Шаг 5: Постепенное восстановление (105-120 минут)

```
1. 10% трафика → Тест 10 минут → OK? ✅
2. 25% трафика → Тест 10 минут → OK? ✅
3. 50% трафика → Тест 15 минут → OK? ✅
4. 100% трафика → FULL RECOVERY! 🎉
```

---

### ПРОЦЕДУРА 2: FAILOVER НА РЕЗЕРВНЫЙ СЕРВЕР

#### Когда использовать:
- Primary сервер недоступен
- Физический отказ hardware
- Проблемы с датацентром

#### Процесс (автоматический!):

```python
# monitoring/health_check.py

async def check_primary_health():
    try:
        response = await httpx.get("https://api.aladdin.family/health")
        if response.status_code != 200:
            # Primary down!
            await trigger_failover()
    except:
        # Primary unreachable!
        await trigger_failover()

async def trigger_failover():
    # 1. Activate standby server
    await activate_standby()
    
    # 2. Update DNS (Cloudflare API)
    await update_dns(
        record="api.aladdin.family",
        value="backup-api-ip"
    )
    
    # 3. Sync data from last backup
    await sync_from_backup()
    
    # 4. Start services
    await start_all_services()
    
    # 5. Alert team
    await send_alert("Failover to backup server completed!")
```

**Время failover:** 2-5 минут (автоматически!)

---

### ПРОЦЕДУРА 3: ВОССТАНОВЛЕНИЕ ПОСЛЕ RANSOMWARE

#### Критичность: МАКСИМАЛЬНАЯ 🔴

```
⚠️ НЕ ПЛАТИТЬ ВЫКУП! ❌

ДЕЙСТВИЯ:

1. ИЗОЛЯЦИЯ (0-15 мин):
   → Отключить все заражённые серверы
   → Изолировать сеть
   → Предотвратить распространение

2. ОЦЕНКА (15-30 мин):
   → Какие данные зашифрованы?
   → Когда началось шифрование?
   → Последний чистый backup?

3. ВОССТАНОВЛЕНИЕ (30-180 мин):
   → Развернуть чистые серверы
   → Восстановить из backup (до заражения)
   → Проверить на malware

4. УКРЕПЛЕНИЕ (180-240 мин):
   → Закрыть вектор атаки
   → Обновить все пароли
   → Усилить мониторинг

5. ПРОВЕРКА (240-300 мин):
   → Полное сканирование
   → Тест всех функций
   → Audit логов
```

---

### ПРОЦЕДУРА 4: ВОССТАНОВЛЕНИЕ БАЗЫ ДАННЫХ

#### Point-in-Time Recovery (PITR)

```bash
# Восстановление на конкретный момент времени

# 1. Определить целевое время
TARGET_TIME="2025-10-11 14:30:00 UTC"

# 2. Найти ближайший full backup
BACKUP_DATE="2025-10-11 02:00:00 UTC"

# 3. Восстановить full backup
pg_restore -d aladdin_db /backups/full/aladdin_20251011_0200.dump

# 4. Применить transaction logs до целевого времени
for log in /backups/wal/202510110200_*.wal; do
    if [[ $(stat -f %m "$log") -le $(date -j -f "%Y-%m-%d %H:%M:%S" "$TARGET_TIME" +%s) ]]; then
        pg_waldump "$log" | psql aladdin_db
    fi
done

# 5. Проверить состояние
psql -d aladdin_db -c "SELECT MAX(created_at) FROM families;"
```

**Точность восстановления:** до последних 15 минут!

---

## 🏗️ РЕЗЕРВНАЯ ИНФРАСТРУКТУРА

### Primary Infrastructure

```
Region: Europe (Frankfurt)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────┐
│  PRODUCTION SERVERS                         │
│                                             │
│  • api-1.aladdin.family (Load: 70%)        │
│  • api-2.aladdin.family (Load: 30%)        │
│  • db-primary (Hot Standby ready)          │
│  • redis-primary (Sentinel cluster)        │
└─────────────────────────────────────────────┘
```

### Backup Infrastructure

```
Region: Russia (Moscow) + Cloud (S3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────┐
│  BACKUP SERVERS (Cold Standby)              │
│                                             │
│  • backup-api.aladdin.family (OFF)         │
│  • db-backup (Standby, sync каждые 15 мин) │
│  • S3 Glacier (Long-term storage)          │
└─────────────────────────────────────────────┘

Время активации: 5-10 минут
```

---

## 📊 RECOVERY SCENARIOS

### Сценарий A: Полная потеря PRIMARY датацентра

**Причина:** Пожар / Наводнение / Отключение электричества

**RTO:** 4 часа  
**RPO:** 15 минут

```
ДЕЙСТВИЯ:

0:00 - ОБНАРУЖЕНИЕ
     → Мониторинг обнаруживает: Primary недоступен
     → Автоматический health check fails
     → Alert всей команде

0:05 - АКТИВАЦИЯ BACKUP
     → Запуск backup-api сервера (AWS EC2)
     → Восстановление БД из последнего backup
     → Проверка целостности данных

0:30 - ПЕРЕКЛЮЧЕНИЕ DNS
     → Cloudflare API: обновить A records
     → api.aladdin.family → backup-api-ip
     → TTL: 60 секунд (быстрое обновление)

0:35 - ПРОВЕРКА СЕРВИСОВ
     → Health checks
     → Smoke tests
     → Critical functions test

1:00 - ПОСТЕПЕННОЕ ВОССТАНОВЛЕНИЕ ТРАФИКА
     → 10% → тест 15 минут
     → 50% → тест 20 минут
     → 100% → полное восстановление

4:00 - ФИНАЛИЗАЦИЯ
     → Мониторинг усиленный (48 часов)
     → Post-mortem analysis
     → План восстановления primary
```

---

### Сценарий B: Потеря базы данных

**Причина:** Corruption / Ransomware / Hardware failure

**RTO:** 2 часа  
**RPO:** 15 минут

```
ДЕЙСТВИЯ:

1. STOP ALL WRITES (0-5 мин):
   systemctl stop aladdin-api
   systemctl stop aladdin-worker

2. ASSESS DAMAGE (5-15 мин):
   # Проверить что можно спасти
   pg_dump aladdin_db > /tmp/corrupted_db.dump
   
   # Анализ
   pg_restore --list /tmp/corrupted_db.dump

3. RESTORE FROM BACKUP (15-60 мин):
   # Последний daily backup
   pg_restore -d aladdin_db_new /backups/daily/latest.dump
   
   # Применить transaction logs
   for log in /backups/wal/*.wal; do
       pg_waldump "$log" | psql aladdin_db_new
   done

4. VERIFY DATA (60-90 мин):
   python3 scripts/verify_db_integrity.py
   
   # Проверить критические таблицы
   SELECT COUNT(*) FROM families;
   SELECT COUNT(*) FROM members;
   SELECT COUNT(*) FROM sessions;

5. SWITCH TO NEW DB (90-120 мин):
   # Update config
   DB_NAME=aladdin_db_new
   
   # Restart services
   systemctl start aladdin-api
   systemctl start aladdin-worker
```

---

### Сценарий C: Ransomware на всей инфраструктуре

**Причина:** Массовая атака шифровальщика

**RTO:** 6 часов  
**RPO:** 1 час (worst case)

```
КРИТИЧЕСКИЙ ПЛАН:

0:00 - ОБНАРУЖЕНИЕ
     → Файлы начинают шифроваться
     → Антивирус обнаруживает ransomware
     → НЕМЕДЛЕННЫЙ ALARM!

0:02 - ИЗОЛЯЦИЯ
     → systemctl stop ALL services
     → Отключить сеть: ifconfig eth0 down
     → Предотвратить распространение

0:10 - FORENSICS
     → Snapshot всех дисков (для анализа)
     → dd if=/dev/sda of=/forensic/disk_image.dd
     → Сохранить все логи

0:30 - ЧИСТАЯ УСТАНОВКА
     → Развернуть новые серверы (clean OS)
     → Установить ALADDIN из Git (проверенный commit)
     → БЕЗ восстановления исполняемых файлов!

1:00 - ВОССТАНОВЛЕНИЕ ДАННЫХ
     → Только данные (не код!)
     → Из backup до заражения
     → Проверка каждого файла

3:00 - ПРОВЕРКА НА MALWARE
     → Полное сканирование
     → Проверка integrity
     → Hash verification

4:00 - ТЕСТИРОВАНИЕ
     → Smoke tests
     → Security audit
     → Performance test

6:00 - ПОСТЕПЕННЫЙ ЗАПУСК
     → 10% → 50% → 100%
     → Усиленный мониторинг 72 часа
```

---

## 🗂️ BACKUP CATALOG

### Что бэкапится:

| Компонент | Метод | Частота | Retention |
|-----------|-------|---------|-----------|
| **PostgreSQL БД** | pg_dump + WAL | 15 минут | 30 дней |
| **Redis (sessions)** | RDB snapshot | 1 час | 7 дней |
| **Config файлы** | Git commit | Real-time | 90 дней |
| **Логи** | rsync | 6 часов | 30 дней |
| **Статика** | rsync | 1 день | 14 дней |
| **Code** | Git tags | Release | Бесконечно |

### Что НЕ бэкапится:

- ❌ Временные файлы (cache, tmp)
- ❌ Build artifacts
- ❌ node_modules
- ❌ Локальные тестовые данные

---

## 🧪 ТЕСТИРОВАНИЕ DRP

### Обязательные тесты:

#### 1. Quarterly Recovery Drill (Квартальные учения)

**Сценарий:**
1. Симуляция катастрофы (напр. потеря primary DB)
2. Команда восстанавливает систему по DRP
3. Засекается время (RTO)
4. Проверяется потеря данных (RPO)

**Цель:**
- Проверить процедуры
- Натренировать команду
- Найти узкие места

**Последнее:** 2025-09-15  
**Результат:** RTO 3h 20min, RPO 12 минут ✅  
**Следующее:** 2025-12-15

---

#### 2. Monthly Backup Verification (Ежемесячная проверка backup)

```bash
#!/bin/bash
# Тест восстановления из backup

# 1. Выбрать случайный backup
BACKUP=$(ls /backups/daily/ | shuf -n 1)

# 2. Восстановить в тестовую БД
pg_restore -d test_db /backups/daily/$BACKUP

# 3. Проверить данные
psql -d test_db -c "SELECT COUNT(*) FROM families;"

# 4. Если OK → backup валидный ✅
# 5. Если ошибка → ALARM! ❌
```

---

#### 3. Annual Disaster Simulation (Годовая симуляция катастрофы)

**Полномасштабное учение:**
- Симуляция Tier 1 катастрофы
- Вовлечение всей команды
- Реальное переключение на backup (в test environment)
- Полный цикл восстановления
- Детальный отчёт

**Последнее:** 2025-01-15  
**Следующее:** 2026-01-15

---

## 📞 КОНТАКТЫ И ESCALATION

### Emergency Contact List

| Роль | Контакт | Доступность |
|------|---------|-------------|
| **DR Commander** | +7 XXX XXX-XX-XX | 24/7 |
| **Lead DevOps** | +7 XXX XXX-XX-XX | 24/7 |
| **Database Admin** | +7 XXX XXX-XX-XX | On-call |
| **Security Lead** | security@aladdin.family | 24/7 |

### External Vendors

| Vendor | Service | Contact | SLA |
|--------|---------|---------|-----|
| **AWS** | Cloud Infrastructure | aws-support | 1 hour |
| **Cloudflare** | CDN + Security | cf-support | 2 hours |
| **Регистратор** | Domain | support@ | 4 hours |

---

## 🔐 БЕЗОПАСНОСТЬ BACKUP

### Защита backup от Ransomware:

```
1. AIR-GAPPED BACKUP:
   ✅ Offsite копия в S3 Glacier
   ✅ Immutable (нельзя удалить/изменить)
   ✅ Версионирование включено

2. ENCRYPTED BACKUPS:
   ✅ AES-256 шифрование
   ✅ Ключи в AWS KMS
   ✅ Separate credentials

3. ACCESS CONTROL:
   ✅ MFA required для доступа
   ✅ Audit log всех операций
   ✅ Только 2 человека имеют доступ
```

---

## 📈 CONTINUOUS IMPROVEMENT

### После каждого recovery:

1. **Post-Recovery Review** (в течение 24 часов)
   - Что сработало?
   - Что можно улучшить?
   - Сколько времени заняло?
   - RTO/RPO соблюдены?

2. **Update DRP** (в течение недели)
   - Обновить процедуры
   - Добавить новые сценарии
   - Улучшить автоматизацию

3. **Train Team** (в течение месяца)
   - Обучение на ошибках
   - Новые процедуры
   - Практические drill

---

## 📊 МЕТРИКИ RECOVERY

### Целевые показатели:

| Метрика | Tier 1 | Tier 2 | Tier 3 |
|---------|--------|--------|--------|
| **RTO** | < 2 часа | < 4 часа | < 8 часов |
| **RPO** | < 5 минут | < 15 минут | < 30 минут |
| **Data Loss** | < 0.01% | < 0.1% | < 1% |
| **Success Rate** | > 99% | > 98% | > 95% |

### Текущие результаты (2025 Q3):

| Метрика | Факт | Статус |
|---------|------|--------|
| **Avg RTO** | 3h 20min | ⚠️ Нужно улучшить до 2h |
| **Avg RPO** | 12 минут | ✅ Цель достигнута |
| **Recovery Success Rate** | 100% (3/3) | ✅ Отлично |
| **False Alarms** | 2% | ✅ Приемлемо |

---

## 🔗 INTEGRATION С СИСТЕМАМИ

### Автоматическое восстановление:

```python
# security/reactive/recovery_service.py

class RecoveryService:
    """
    Служба автоматического восстановления
    
    Возможности:
    - Автоматический failover
    - Self-healing для minor issues
    - Orchestration восстановления
    - Мониторинг recovery процесса
    """
    
    async def auto_recover(self, incident_id):
        # 1. Оценить возможность auto-recovery
        if self.can_auto_recover(incident_id):
            # 2. Запустить восстановление
            await self.execute_recovery(incident_id)
            
            # 3. Проверить результат
            if await self.verify_recovery():
                return RecoveryStatus.SUCCESS
        else:
            # Требуется ручное вмешательство
            await self.escalate_to_human()
```

---

## 📝 ЧЕКЛИСТЫ

### Pre-Disaster Checklist (Превентивная проверка)

```
ЕЖЕДНЕВНО:
☑ Backup успешно завершён
☑ Backup integrity проверен
☑ Disk space > 20% free
☑ Monitoring работает

ЕЖЕНЕДЕЛЬНО:
☑ Test restore (случайный backup)
☑ Review error logs
☑ Update recovery procedures
☑ Check failover готовность

ЕЖЕМЕСЯЧНО:
☑ Full DR drill
☑ Review contacts list
☑ Update documentation
☑ Train new team members

ЕЖЕКВАРТАЛЬНО:
☑ Disaster simulation
☑ Update RTO/RPO targets
☑ Review vendor SLAs
☑ Audit access controls
```

---

## 🚀 БЫСТРЫЙ СТАРТ (EMERGENCY)

### Если катастрофа СЕЙЧАС! 🔥

```
1. STOP! Не паникуйте! ⏸️

2. ASSESS (2 минуты):
   □ Что случилось?
   □ Tier 1/2/3?
   □ Сколько затронуто?

3. ACTIVATE TEAM (2 минуты):
   □ Telegram: @all "DISASTER! Type: X"
   □ Create war room
   □ Start incident log

4. FOLLOW PROCEDURE (зависит от Tier):
   □ Tier 1 → Сценарий A/B/C
   □ Tier 2 → Процедура 1/2
   □ Tier 3 → Процедура 4

5. DOCUMENT EVERYTHING:
   □ Screenshots
   □ Commands executed
   □ Timeline
   □ Decisions made
```

---

## 🔗 СВЯЗАННЫЕ ДОКУМЕНТЫ

- [IRP - Incident Response Plan](IRP_INCIDENT_RESPONSE_PLAN.md)
- [Recovery Service Documentation](../security/recovery_service_documentation.md)
- [Backup Procedures](../security/backups/BACKUP_PROCEDURES.md)
- [3-2-1 Backup Strategy](../security/backups/3-2-1_STRATEGY.md)

---

## 📅 ИСТОРИЯ ВЕРСИЙ

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0.0 | 2025-10-11 | Создание структурированного DRP |
| 0.9.0 | 2025-09-22 | Обновление recovery procedures |
| 0.8.0 | 2025-09-17 | Добавление 3-2-1 backup стратегии |

---

**Статус:** ✅ ДЕЙСТВУЮЩИЙ  
**Последний test:** 2025-09-15 (RTO 3h 20min, RPO 12min)  
**Следующий review:** 2025-11-11  
**Следующий drill:** 2025-12-15  
**Ответственный:** DevOps Team + Security Team



