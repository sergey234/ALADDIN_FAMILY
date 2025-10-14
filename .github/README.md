# 🚀 ALADDIN GitHub Actions CI/CD

Полная система автоматизации для ALADDIN Security Dashboard с использованием GitHub Actions.

## 📋 **ДОСТУПНЫЕ WORKFLOW:**

### 🔄 **Основные Workflow:**

1. **🚀 CI/CD Pipeline** (`ci-cd.yml`)
   - **Триггеры:** Push, PR, Schedule, Manual
   - **Функции:** Code Quality, Unit Tests, Performance Tests, Security Tests, SFM Integration, Build & Deploy
   - **Частота:** При каждом push/PR + ежедневно в 2:00 UTC

2. **🔒 Security Audit** (`security-audit.yml`)
   - **Триггеры:** Schedule, Manual
   - **Функции:** Dependency Audit, Code Audit, Infrastructure Audit, Compliance Check
   - **Частота:** Каждый понедельник в 3:00 UTC

3. **📊 Performance Monitoring** (`performance-monitoring.yml`)
   - **Триггеры:** Schedule, Manual
   - **Функции:** Load Testing, Memory Monitoring, Response Time, SFM Performance, Cache Performance
   - **Частота:** Ежедневно в 4:00 UTC

4. **🚀 Deploy** (`deploy.yml`)
   - **Триггеры:** Push to main, Tags, Manual
   - **Функции:** Build Images, Pre-deployment Tests, Deploy to Staging/Production
   - **Частота:** При push в main или создании тега

5. **📊 Monitoring** (`monitoring.yml`)
   - **Триггеры:** Schedule, Manual
   - **Функции:** System Health, Dashboard Health, SFM Health, Performance, Security
   - **Частота:** Каждые 6 часов

6. **📢 Notifications** (`notifications.yml`)
   - **Триггеры:** Workflow Run, Manual
   - **Функции:** Slack, Telegram, Generic Webhook notifications
   - **Частота:** При завершении других workflow

---

## 🛠️ **НАСТРОЙКА СЕКРЕТОВ:**

### **Обязательные секреты:**
```bash
# Для уведомлений
SLACK_WEBHOOK=https://hooks.slack.com/services/...
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890
NOTIFICATION_WEBHOOK=https://your-webhook-url.com/notify

# Для деплоя (если используется)
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
KUBECONFIG=your-kubeconfig-content
```

### **Настройка секретов:**
1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте необходимые секреты
3. Workflow автоматически будут их использовать

---

## 🎯 **ТИПЫ ТЕСТИРОВАНИЯ:**

### **🧪 Unit & Integration Tests:**
- **Файлы:** `test_*.py`
- **Покрытие:** 100%
- **Время выполнения:** ~15 минут
- **Результаты:** JUnit XML + HTML отчеты

### **🚀 Performance Tests:**
- **Load Testing:** 100+ одновременных пользователей
- **Memory Testing:** Профилирование памяти, утечки
- **Response Time:** Время отклика < 500ms
- **Cache Testing:** HTTP кэширование, ETag, Last-Modified

### **🔒 Security Tests:**
- **Dependency Audit:** Safety, pip-audit
- **Code Audit:** Bandit, Semgrep
- **Infrastructure Audit:** Docker, GitHub Actions
- **Compliance:** GDPR, 152-ФЗ, PCI DSS

### **🔧 SFM Integration Tests:**
- **Advanced Integration:** Подключение, операции, конкурентность
- **Function Lifecycle:** Создание, управление, восстановление
- **Security Integration:** Аутентификация, валидация, rate limiting
- **Monitoring Integration:** Метрики, алерты, real-time
- **API Integration:** Endpoints, форматы, производительность

---

## 📊 **МОНИТОРИНГ И ОТЧЕТЫ:**

### **📈 Автоматические отчеты:**
- **Code Quality:** Flake8, Black, isort, mypy
- **Security:** Bandit, Safety, OWASP ZAP
- **Performance:** Load test results, memory usage
- **SFM Integration:** Function status, metrics
- **Deployment:** Build logs, health checks

### **📊 Артефакты:**
- **Test Results:** JUnit XML, HTML отчеты
- **Security Reports:** JSON отчеты безопасности
- **Performance Data:** CSV метрики, графики
- **Deployment Logs:** Docker build, deploy logs
- **Monitoring Data:** System metrics, health status

---

## 🚀 **ЗАПУСК WORKFLOW:**

### **Автоматический запуск:**
- **Push/PR:** Автоматически при изменениях кода
- **Schedule:** По расписанию (ежедневно, еженедельно)
- **Workflow Run:** При завершении других workflow

### **Ручной запуск:**
1. Перейдите в Actions → выберите workflow
2. Нажмите "Run workflow"
3. Выберите параметры (тип тестирования, окружение)
4. Нажмите "Run workflow"

### **Параметры ручного запуска:**
- **CI/CD Pipeline:** test_type (all, performance, security, integration, sfm)
- **Security Audit:** audit_type (full, dependencies, code, infrastructure)
- **Performance Monitoring:** monitoring_type (full, load, memory, response-time, sfm)
- **Deploy:** environment (staging, production), deploy_type (full, dashboard-only, sfm-only, config-only)

---

## 🔧 **КОНФИГУРАЦИЯ:**

### **Environment Variables:**
```yaml
env:
  PYTHON_VERSION: '3.9'
  NODE_VERSION: '18'
  DASHBOARD_PORT: 8080
  SFM_PORT: 8011
  REDIS_PORT: 6379
  POSTGRES_PORT: 5432
```

### **Docker Images:**
- **Dashboard:** `ghcr.io/username/aladdin-dashboard:latest`
- **SFM:** `ghcr.io/username/aladdin-sfm:latest`

### **Ports:**
- **Dashboard:** 8080
- **SFM:** 8011
- **Redis:** 6379
- **PostgreSQL:** 5432

---

## 📱 **УВЕДОМЛЕНИЯ:**

### **Поддерживаемые каналы:**
- **Slack:** Webhook notifications
- **Telegram:** Bot notifications
- **Generic Webhook:** Custom integrations

### **Типы уведомлений:**
- **Success:** ✅ Успешное выполнение
- **Failure:** ❌ Ошибка выполнения
- **Warning:** ⚠️ Предупреждения

### **Содержание уведомлений:**
- Статус workflow
- Commit SHA и сообщение
- Ссылка на детали
- Время выполнения

---

## 🎯 **BEST PRACTICES:**

### **Для разработчиков:**
1. **Всегда проверяйте результаты CI/CD** перед мержем
2. **Используйте feature branches** для новых функций
3. **Пишите тесты** для нового кода
4. **Следите за уведомлениями** о проблемах

### **Для DevOps:**
1. **Мониторьте производительность** workflow
2. **Обновляйте секреты** регулярно
3. **Анализируйте отчеты** безопасности
4. **Оптимизируйте время выполнения** тестов

### **Для мониторинга:**
1. **Настройте алерты** для критических ошибок
2. **Проверяйте метрики** производительности
3. **Анализируйте тренды** использования
4. **Планируйте масштабирование** на основе данных

---

## 🆘 **TROUBLESHOOTING:**

### **Частые проблемы:**
1. **Tests failing:** Проверьте логи, исправьте код
2. **Build errors:** Проверьте Dockerfile, зависимости
3. **Deploy failures:** Проверьте секреты, конфигурацию
4. **Notification issues:** Проверьте webhook URLs, токены

### **Полезные команды:**
```bash
# Локальный запуск тестов
pytest tests/ -v

# Проверка качества кода
flake8 .
black --check .
isort --check-only .

# Проверка безопасности
bandit -r .
safety check

# Запуск дашборда локально
python enhanced_api_docs.py
```

---

## 📞 **ПОДДЕРЖКА:**

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Documentation:** README файлы
- **Logs:** GitHub Actions logs

---

**🎉 Система готова к использованию! Все workflow настроены и готовы к автоматическому выполнению.**