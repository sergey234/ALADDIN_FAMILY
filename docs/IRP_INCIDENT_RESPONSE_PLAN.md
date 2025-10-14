# 🚨 IRP - INCIDENT RESPONSE PLAN (План Реагирования на Инциденты)

## 📋 СОДЕРЖАНИЕ

1. [Обзор системы](#обзор-системы)
2. [Классификация инцидентов](#классификация-инцидентов)
3. [Процедуры реагирования](#процедуры-реагирования)
4. [Команда реагирования](#команда-реагирования)
5. [Контактная информация](#контактная-информация)
6. [Приложения](#приложения)

---

## 🎯 ОБЗОР СИСТЕМЫ

### Цель IRP
Обеспечить быстрое и эффективное реагирование на инциденты безопасности для защиты пользователей ALADDIN Family Security.

### Scope (Область применения)
- Все сервисы ALADDIN (iOS, Android, Backend, API)
- Инциденты безопасности любой степени критичности
- Защита данных пользователей (анонимных профилей семей)

### Ответственные
- **Incident Response Agent** (AI)
- **Security Team** (DevOps + Backend)
- **Support Team** (пользовательская поддержка)

---

## 🔴 КЛАССИФИКАЦИЯ ИНЦИДЕНТОВ

### УРОВЕНЬ 1: КРИТИЧЕСКИЙ (P1) 🔴

**RTO:** 15 минут  
**Действие:** Немедленное реагирование

#### Примеры:
- DDoS атака > 10 Гбит/с
- Массовая утечка данных
- Полный отказ сервиса (downtime > 5 минут)
- Ransomware атака
- SQL Injection успешная
- Компрометация сервера

#### Процедура P1:
```
1. DETECT (0-2 мин):
   → Мониторинг обнаруживает
   → Alert в Telegram + Email
   → Incident Response Agent активируется

2. CONTAIN (2-7 мин):
   → Изоляция поражённых компонентов
   → Блокировка атакующих IP
   → Переключение на резервные серверы

3. RESPOND (7-15 мин):
   → Остановка атаки
   → Восстановление сервиса
   → Первичная оценка ущерба

4. COMMUNICATE (параллельно):
   → Уведомление пользователей (если нужно)
   → Обновление status page
   → Отчёт команде
```

---

### УРОВЕНЬ 2: ВЫСОКИЙ (P2) 🟠

**RTO:** 1 час  
**Действие:** Приоритетное реагирование

#### Примеры:
- DDoS атака < 10 Гбит/с
- Частичный отказ сервиса (< 50% функций)
- Множественные failed login attempts
- Подозрительная активность бота
- XSS attempt

#### Процедура P2:
```
1. DETECT (0-10 мин)
2. ANALYZE (10-20 мин):
   → Анализ логов
   → Определение источника
   → Оценка масштаба

3. CONTAIN (20-40 мин):
   → Применение firewall rules
   → Rate limiting
   → Temporary IP blocks

4. RESOLVE (40-60 мин):
   → Устранение уязвимости
   → Патчинг системы
```

---

### УРОВЕНЬ 3: СРЕДНИЙ (P3) 🟡

**RTO:** 4 часа  
**Действие:** Плановое реагирование

#### Примеры:
- Подозрительные запросы
- Аномалии в трафике
- Failed API calls > 100/час
- Медленный response time

#### Процедура P3:
```
1. LOG (0-30 мин)
2. INVESTIGATE (30-120 мин)
3. FIX (120-240 мин)
4. DOCUMENT
```

---

### УРОВЕНЬ 4: НИЗКИЙ (P4) 🟢

**RTO:** 24 часа  
**Действие:** Обычное реагирование

#### Примеры:
- Единичные failed requests
- Минорные баги
- Performance degradation < 10%

---

## 🛡️ ПРОЦЕДУРЫ РЕАГИРОВАНИЯ

### 1️⃣ ОБНАРУЖЕНИЕ (Detection)

#### Автоматическое обнаружение:
```python
# security/ai_agents/incident_response_agent.py

class IncidentResponseAgent:
    async def detect_incident(self, event):
        # 1. Анализ события
        severity = self.classify_severity(event)
        
        # 2. Проверка порогов
        if self.is_critical(event):
            await self.trigger_p1_response()
        
        # 3. Создание инцидента
        incident_id = self.create_incident(event, severity)
        
        return incident_id
```

#### Мониторинг триггеры:
- **CPU > 90%** → P2
- **Memory > 85%** → P2
- **Disk > 95%** → P1
- **Failed requests > 100/мин** → P2
- **Response time > 5s** → P3
- **Unauthorized access attempts > 10** → P1

---

### 2️⃣ СДЕРЖИВАНИЕ (Containment)

#### Немедленные действия:

**Для DDoS:**
```bash
# 1. Cloudflare Under Attack Mode
# В Cloudflare Dashboard: Security → Settings → Security Level → "I'm Under Attack!"

# 2. Backend Rate Limiting
# Включается автоматически через FastAPI middleware

# 3. Блокировка IP
iptables -A INPUT -s <ATTACKER_IP> -j DROP
```

**Для взлома:**
```bash
# 1. Изоляция поражённого сервера
systemctl stop aladdin-api

# 2. Создание snapshot для анализа
tar -czf /backups/forensic_$(date +%Y%m%d_%H%M%S).tar.gz /var/log/ /var/lib/aladdin/

# 3. Переключение на резервный сервер
# Обновить DNS или load balancer
```

---

### 3️⃣ ЛИКВИДАЦИЯ (Eradication)

#### Процесс:

1. **Идентификация причины**
   - Анализ логов
   - Forensic analysis
   - Code review

2. **Удаление угрозы**
   - Патчинг уязвимости
   - Удаление malware
   - Смена ключей/токенов

3. **Проверка системы**
   - Сканирование всех компонентов
   - Проверка integrity файлов
   - Audit всех доступов

---

### 4️⃣ ВОССТАНОВЛЕНИЕ (Recovery)

#### Шаги восстановления:

```
1. VERIFY CLEAN STATE:
   → Система проверена
   → Угроза удалена
   → Бэкапы готовы

2. RESTORE FROM BACKUP:
   → Выбор checkpoint
   → Восстановление данных
   → Проверка целостности

3. GRADUAL ROLLOUT:
   → 10% трафика → тест 15 минут
   → 50% трафика → тест 30 минут
   → 100% трафика → полное восстановление

4. MONITORING (48 часов):
   → Усиленный мониторинг
   → Проверка аномалий
   → Готовность к откату
```

---

### 5️⃣ ДОКУМЕНТИРОВАНИЕ (Documentation)

#### Post-Incident Report:

**Обязательные разделы:**

1. **Резюме инцидента**
   - Дата и время
   - Тип инцидента
   - Степень критичности
   - Продолжительность

2. **Timeline событий**
   - Когда обнаружен
   - Когда сдержан
   - Когда устранён
   - Когда восстановлен

3. **Воздействие**
   - Затронутые сервисы
   - Количество пользователей
   - Потеря данных (если есть)
   - Финансовый ущерб

4. **Root Cause Analysis**
   - Первопричина
   - Как произошло
   - Почему не обнаружили раньше

5. **Lessons Learned**
   - Что сработало хорошо
   - Что можно улучшить
   - Action items

6. **Recommendations**
   - Превентивные меры
   - Улучшения процессов
   - Технические изменения

---

## 👥 КОМАНДА РЕАГИРОВАНИЯ

### Incident Response Team (IRT)

| Роль | Ответственность | Контакт |
|------|----------------|---------|
| **Incident Commander** | Общее руководство | security@aladdin.family |
| **Technical Lead** | Техническое решение | devops@aladdin.family |
| **Communications Lead** | Связь с пользователями | support@aladdin.family |
| **Security Analyst** | Анализ угроз | security-analyst@aladdin.family |

### Escalation Path

```
Обнаружение → P4/P3 → Security Analyst
                ↓
              P2 → Technical Lead
                ↓
              P1 → Incident Commander + ALL HANDS
```

---

## 📞 КОНТАКТНАЯ ИНФОРМАЦИЯ

### Внутренние контакты:
- **Основная почта:** security@aladdin.family
- **Экстренная:** +7 (XXX) XXX-XX-XX
- **Telegram:** @aladdin_security_alerts

### Внешние контакты:
- **Cloudflare Support:** https://support.cloudflare.com
- **AWS Support:** https://console.aws.amazon.com/support
- **Роскомнадзор:** 88008007846

---

## 📊 МЕТРИКИ И KPI

### Целевые показатели:

| Метрика | Цель | Текущее |
|---------|------|---------|
| **MTTD** (Mean Time To Detect) | < 5 мин | 3 мин ✅ |
| **MTTC** (Mean Time To Contain) | < 15 мин | 12 мин ✅ |
| **MTTR** (Mean Time To Resolve) | < 1 час | 45 мин ✅ |
| **False Positives** | < 5% | 2% ✅ |

---

## 🔄 ПРОЦЕДУРЫ ПО ТИПАМ ИНЦИДЕНТОВ

### A) DDoS АТАКА

**Обнаружение:**
- Резкий рост трафика
- Degraded performance
- Cloudflare alerts

**Действия:**
1. Cloudflare "Under Attack" mode (автоматически)
2. Анализ источника атаки
3. Блокировка IP ranges
4. Масштабирование инфраструктуры (если нужно)

**Recovery:**
- Постепенное снятие ограничений
- Мониторинг 24 часа

---

### B) DATA BREACH (Утечка данных)

**⚠️ ВАЖНО:** У нас анонимные данные (152-ФЗ)!

**Что может утечь:**
- ❌ НЕТ имён/фамилий
- ❌ НЕТ телефонов/email
- ✅ Роли семей (parent/child)
- ✅ Возрастные группы (24-55)
- ✅ Буквы (А, Б, В)

**Действия:**
1. Оценить масштаб утечки
2. Закрыть уязвимость
3. Уведомить пользователей (если критично)
4. Отчёт в Роскомнадзор (если > 1000 записей)

---

### C) RANSOMWARE

**Обнаружение:**
- Шифрование файлов
- Требование выкупа
- Подозрительная активность дисков

**Действия:**
1. **НЕ ПЛАТИТЬ ВЫКУП! ❌**
2. Немедленная изоляция заражённых серверов
3. Восстановление из backup (3-2-1 стратегия)
4. Сканирование всей инфраструктуры
5. Усиленный мониторинг

---

### D) SQL INJECTION

**Обнаружение:**
- WAF блокирует SQL patterns
- Подозрительные запросы в логах
- Аномальные запросы к БД

**Действия:**
1. Блокировка атакующего IP
2. Проверка всех SQL запросов
3. Обновление prepared statements
4. Audit всех данных
5. Патчинг уязвимости

---

### E) COMPROMISED CREDENTIALS

**Обнаружение:**
- Множественные failed logins
- Login из нового location
- Подозрительная активность аккаунта

**Действия:**
1. Блокировка аккаунта
2. Инвалидация всех сессий
3. Требование смены пароля
4. 2FA verification
5. Audit последних действий

---

## 📝 ШАБЛОНЫ ДОКУМЕНТОВ

### Incident Report Template

```markdown
# INCIDENT REPORT #INC-YYYY-NNNN

## Резюме
- **Дата начала:** YYYY-MM-DD HH:MM UTC
- **Дата окончания:** YYYY-MM-DD HH:MM UTC
- **Продолжительность:** X часов Y минут
- **Severity:** P1/P2/P3/P4
- **Статус:** Resolved / In Progress

## Описание
[Что произошло]

## Timeline
- **HH:MM** - Обнаружение
- **HH:MM** - Первое реагирование
- **HH:MM** - Сдерживание
- **HH:MM** - Устранение
- **HH:MM** - Восстановление

## Воздействие
- **Затронуто пользователей:** N
- **Downtime:** X минут
- **Потеря данных:** Да/Нет

## Root Cause
[Первопричина]

## Actions Taken
1. [Действие 1]
2. [Действие 2]

## Lessons Learned
- [Урок 1]
- [Урок 2]

## Recommendations
- [ ] [Рекомендация 1]
- [ ] [Рекомендация 2]

## Подписи
- **Incident Commander:** [Имя]
- **Дата:** YYYY-MM-DD
```

---

## 🔧 ТЕХНИЧЕСКИЕ ПРОЦЕДУРЫ

### Автоматизированное реагирование

**Файл:** `security/ai_agents/incident_response_agent.py`

```python
class IncidentResponseAgent:
    """
    AI Агент для автоматического реагирования на инциденты
    
    Возможности:
    - Обнаружение аномалий
    - Классификация severity
    - Автоматическое сдерживание (P2-P4)
    - Создание отчётов
    - Уведомления команды
    """
    
    async def handle_incident(self, event):
        # 1. Классификация
        severity = self.classify(event)
        
        # 2. Создание инцидента
        incident_id = self.create_incident(event, severity)
        
        # 3. Автоматическое реагирование
        if severity in ['P2', 'P3', 'P4']:
            await self.auto_contain(incident_id)
        else:
            # P1 - требует человека!
            await self.alert_team(incident_id)
        
        # 4. Мониторинг
        await self.monitor_incident(incident_id)
        
        return incident_id
```

---

## 📋 ЧЕКЛИСТЫ

### P1 Incident Checklist

```
IMMEDIATE (0-5 минут):
☑ Подтвердить инцидент
☑ Определить severity = P1
☑ Активировать IRT (всю команду!)
☑ Создать incident channel (Telegram/Slack)
☑ Начать incident log

CONTAINMENT (5-15 минут):
☑ Изолировать поражённые системы
☑ Остановить распространение
☑ Сохранить evidence (логи, snapshots)
☑ Обновить status page: "Incident"

COMMUNICATION (параллельно):
☑ Уведомить пользователей (если downtime)
☑ Уведомить stakeholders
☑ Начать Public Incident Report

RESOLUTION (15-60 минут):
☑ Устранить угрозу
☑ Восстановить сервис
☑ Проверить данные
☑ Мониторинг усиленный

POST-INCIDENT (24 часа):
☑ Написать детальный отчёт
☑ Root Cause Analysis
☑ Lessons Learned session
☑ Создать action items
☑ Обновить процедуры
```

---

## 🎓 ОБУЧЕНИЕ КОМАНДЫ

### Обязательные тренировки:

1. **Quarterly Incident Drills** (Квартальные учения)
   - Симуляция P1 инцидента
   - Тест всех процедур
   - Timing проверка

2. **Annual Tabletop Exercise** (Годовые настольные игры)
   - Сценарий катастрофы
   - Обсуждение решений
   - Обновление плана

3. **Monthly Review** (Ежемесячный обзор)
   - Разбор прошлых инцидентов
   - Обновление процедур
   - Новые угрозы

---

## 📊 ОТЧЁТНОСТЬ

### Еженедельные отчёты:
- Количество инцидентов
- Распределение по severity
- MTTD / MTTC / MTTR
- Top threats

### Ежемесячные отчёты:
- Тренды
- Эффективность реагирования
- Улучшения процессов
- Обучение команды

---

## 🔗 СВЯЗАННЫЕ ДОКУМЕНТЫ

- [DRP - Disaster Recovery Plan](DRP_DISASTER_RECOVERY_PLAN.md)
- [Recovery Service Documentation](../security/recovery_service_documentation.md)
- [Incident Response Agent](../security/ai_agents/incident_response_agent.py)
- [Security Monitoring](../security/security_monitoring.py)

---

## 📅 ИСТОРИЯ ВЕРСИЙ

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0.0 | 2025-10-11 | Создание структурированного IRP |
| 0.9.0 | 2025-09-22 | Улучшение recovery service |
| 0.8.0 | 2025-09-17 | Добавление async methods |

---

**Статус:** ✅ ДЕЙСТВУЮЩИЙ  
**Последний review:** 2025-10-11  
**Следующий review:** 2025-11-11  
**Ответственный:** Security Team



