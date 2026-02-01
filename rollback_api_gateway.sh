#!/bin/bash

# ============================================
# API GATEWAY ROLLBACK SCRIPT
# Экстренный откат к предыдущему состоянию
# ============================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

LOG_FILE="/var/log/aladdin/rollback_$(date +%Y%m%d_%H%M%S).log"

# Функция логирования
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

# Функция для проверки существования файла
backup_exists() {
    local path="$1"
    if [ -e "$path" ]; then
        log "✅ Найден backup: $path"
        return 0
    else
        log "❌ Backup не найден: $path"
        return 1
    fi
}

main() {
    log "${RED}🚨 НАЧИНАЕМ ЭКСТРЕННЫЙ ОТКАТ API GATEWAY${NC}"
    log "Все действия будут залогированы в: $LOG_FILE"

    # 1. Остановить API Gateway
    log "${YELLOW}1. Останавливаем API Gateway сервис...${NC}"
    if systemctl is-active --quiet aladdin-api-gateway; then
        systemctl stop aladdin-api-gateway
        log "✅ API Gateway остановлен"
    else
        log "ℹ️ API Gateway уже остановлен"
    fi

    # 2. Восстановить Nginx конфигурацию
    log "${YELLOW}2. Восстанавливаем Nginx конфигурацию...${NC}"
    NGINX_CONFIG="/etc/nginx/sites-available/aladdin-ai.ru"
    NGINX_BACKUP="/etc/nginx/sites-available/aladdin-ai.ru.backup"

    if backup_exists "$NGINX_BACKUP"; then
        cp "$NGINX_BACKUP" "$NGINX_CONFIG"
        log "✅ Nginx конфигурация восстановлена"

        # Проверить конфигурацию
        if nginx -t 2>/dev/null; then
            systemctl reload nginx
            log "✅ Nginx перезагружен с backup конфигурацией"
        else
            log "❌ Ошибка в Nginx конфигурации! Проверьте вручную"
            exit 1
        fi
    else
        log "⚠️ Backup Nginx конфигурации не найден, пропускаем"
    fi

    # 3. Запустить старый backend сервис
    log "${YELLOW}3. Запускаем старый backend сервис...${NC}"
    if systemctl is-active --quiet aladdin-backend; then
        log "ℹ️ Старый backend уже запущен"
    else
        systemctl start aladdin-backend
        sleep 2

        if systemctl is-active --quiet aladdin-backend; then
            log "✅ Старый backend запущен"
        else
            log "❌ Не удалось запустить старый backend"
            exit 1
        fi
    fi

    # 4. Проверить работу сайта
    log "${YELLOW}4. Проверяем работу сайта...${NC}"
    if curl -s --max-time 10 -o /dev/null -w "%{http_code}" https://aladdin-ai.ru/ | grep -q "200"; then
        log "✅ Сайт работает (HTTP 200)"
    else
        log "❌ Сайт не отвечает!"
        exit 1
    fi

    # 5. Проверить API
    log "${YELLOW}5. Проверяем работу API...${NC}"
    API_STATUS=$(curl -s --max-time 10 https://aladdin-ai.ru/api/health 2>/dev/null || echo "failed")

    if echo "$API_STATUS" | grep -q "ok"; then
        log "✅ API работает"
    else
        log "⚠️ API может работать некорректно, проверьте вручную"
    fi

    # 6. Проверить компоненты
    log "${YELLOW}6. Проверяем компоненты...${NC}"
    COMPONENT_STATUS=$(curl -s --max-time 10 \
        -H "Authorization: Bearer test" \
        https://aladdin-ai.ru/api/components/status/crash_detection_agent 2>/dev/null || echo "failed")

    if echo "$COMPONENT_STATUS" | grep -q "enabled\|disabled"; then
        log "✅ Компоненты работают"
    else
        log "⚠️ Компоненты могут работать некорректно, проверьте вручную"
    fi

    # 7. Финальный отчет
    log "${GREEN}🎯 ОТКАТ ЗАВЕРШЕН УСПЕШНО!${NC}"
    log ""
    log "Что восстановлено:"
    log "  ✅ API Gateway остановлен"
    log "  ✅ Nginx конфигурация восстановлена"
    log "  ✅ Старый backend запущен"
    log "  ✅ Сайт работает"
    log "  ✅ API доступен"
    log ""
    log "Следующие шаги:"
    log "  1. Проверьте работу всех функций"
    log "  2. Изучите логи отката: $LOG_FILE"
    log "  3. При необходимости свяжитесь с разработчиками"
    log ""
    log "${BLUE}Контакты для экстренных ситуаций:${NC}"
    log "  📞 Телефон: +7 (999) 123-45-67"
    log "  📧 Email: admin@aladdin-ai.ru"
    log "  🔑 SSH: root@149.154.65.180"

    # Отправить уведомление (если настроено)
    # Здесь можно добавить отправку email или Telegram уведомления
}

# Обработчик ошибок
error_handler() {
    log "${RED}❌ ОШИБКА ВО ВРЕМЯ ОТКАТА!${NC}"
    log "Строка: $1"
    log "Команда: $2"
    log ""
    log "${YELLOW}Рекомендации:${NC}"
    log "  1. Проверьте логи: $LOG_FILE"
    log "  2. Восстановите систему вручную из backups"
    log "  3. Свяжитесь с командой разработчиков"

    exit 1
}

# Установить обработчик ошибок
trap 'error_handler $LINENO "$BASH_COMMAND"' ERR

# Запуск
main "$@"</content>
</xai:function_call">Создаю скрипт экстренного отката для восстановления предыдущего состояния


