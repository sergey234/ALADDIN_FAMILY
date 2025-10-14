# Документация: check_vpn_sleep_mode.py

## Общая информация
- **Файл**: check_vpn_sleep_mode.py
- **Путь**: /Users/sergejhlystov/ALADDIN_NEW/security/vpn/
- **Размер**: 9.8KB
- **Строк**: 275
- **Назначение**: Проверка VPN систем в спящем режиме

## Описание функций
- `check_sleep_mode_status()` - Основная функция проверки статуса VPN в спящем режиме
- `check_vpn_ports()` - Проверка портов VPN
- `check_config_files()` - Проверка конфигурационных файлов
- `check_log_files()` - Проверка логов
- `check_vpn_services()` - Проверка VPN сервисов
- `check_security_components()` - Проверка компонентов безопасности
- `check_performance_metrics()` - Проверка метрик производительности
- `generate_sleep_report()` - Генерация отчета о спящем режиме

## Импорты
- json
- os
- time
- datetime
- typing (Dict, Any)

## Статус исправления
- **Дата начала**: $(date)
- **Этап**: 1 - ПОДГОТОВКА И АНАЛИЗ
- **Статус**: В процессе