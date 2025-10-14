#!/bin/bash
# -*- coding: utf-8 -*-
# SFM Status Shell Script - Shell скрипт с автопоиском SFM

echo "🚀 SFM STATUS SHELL SCRIPT"
echo "=================================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для поиска SFM реестра
find_sfm_registry() {
    echo -e "${BLUE}🔍 Поиск SFM реестра...${NC}"
    
    # Возможные пути к реестру
    POSSIBLE_PATHS=(
        "data/sfm/function_registry.json"
        "../data/sfm/function_registry.json"
        "../../data/sfm/function_registry.json"
        "ALADDIN_NEW/data/sfm/function_registry.json"
        "/Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry.json"
    )
    
    SFM_REGISTRY=""
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -f "$path" ]; then
            SFM_REGISTRY="$path"
            echo -e "${GREEN}✅ SFM реестр найден: $path${NC}"
            break
        fi
    done
    
    if [ -z "$SFM_REGISTRY" ]; then
        echo -e "${RED}❌ SFM реестр не найден!${NC}"
        echo "Поиск в следующих местах:"
        for path in "${POSSIBLE_PATHS[@]}"; do
            echo "  - $path"
        done
        exit 1
    fi
}

# Функция для проверки JSON
check_json_validity() {
    echo -e "${BLUE}🔍 Проверка валидности JSON...${NC}"
    
    if python3 -c "import json; json.load(open('$SFM_REGISTRY'))" 2>/dev/null; then
        echo -e "${GREEN}✅ JSON файл корректен${NC}"
        return 0
    else
        echo -e "${RED}❌ JSON файл содержит ошибки${NC}"
        return 1
    fi
}

# Функция для получения базовой статистики
get_basic_stats() {
    echo -e "${BLUE}📊 Получение базовой статистики...${NC}"
    
    python3 -c "
import json
try:
    with open('$SFM_REGISTRY', 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    functions = registry.get('functions', {})
    total = len(functions)
    active = sum(1 for f in functions.values() if isinstance(f, dict) and f.get('status') == 'active')
    sleeping = sum(1 for f in functions.values() if isinstance(f, dict) and f.get('status') == 'sleeping')
    critical = sum(1 for f in functions.values() if isinstance(f, dict) and f.get('is_critical', False))
    
    print(f'Всего функций: {total}')
    print(f'Активные: {active}')
    print(f'Спящие: {sleeping}')
    print(f'Критические: {critical}')
    
    if total > 0:
        print(f'Активные: {active/total*100:.1f}%')
        print(f'Спящие: {sleeping/total*100:.1f}%')
        print(f'Критические: {critical/total*100:.1f}%')
    
except Exception as e:
    print(f'Ошибка: {e}')
    exit(1)
"
}

# Функция для проверки структуры
check_structure() {
    echo -e "${BLUE}🔍 Проверка структуры SFM...${NC}"
    
    if [ -f "scripts/sfm_structure_validator.py" ]; then
        python3 scripts/sfm_structure_validator.py
    else
        echo -e "${YELLOW}⚠️  Валидатор структуры не найден${NC}"
    fi
}

# Функция для запуска универсального анализа
run_universal_analysis() {
    echo -e "${BLUE}🔍 Запуск универсального анализа...${NC}"
    
    if [ -f "scripts/sfm_stats_universal.py" ]; then
        python3 scripts/sfm_stats_universal.py
    else
        echo -e "${YELLOW}⚠️  Универсальный анализатор не найден${NC}"
    fi
}

# Функция для показа справки
show_help() {
    echo "Использование: $0 [опции]"
    echo ""
    echo "Опции:"
    echo "  -h, --help     Показать эту справку"
    echo "  -s, --stats    Показать только статистику"
    echo "  -c, --check    Проверить только структуру"
    echo "  -a, --all      Полный анализ (по умолчанию)"
    echo "  -u, --universal Запустить универсальный анализатор"
    echo ""
    echo "Примеры:"
    echo "  $0              # Полный анализ"
    echo "  $0 --stats      # Только статистика"
    echo "  $0 --check      # Только проверка структуры"
    echo "  $0 --universal  # Универсальный анализатор"
}

# Главная функция
main() {
    # Обработка аргументов
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--stats)
            find_sfm_registry
            check_json_validity
            get_basic_stats
            ;;
        -c|--check)
            find_sfm_registry
            check_json_validity
            check_structure
            ;;
        -u|--universal)
            find_sfm_registry
            run_universal_analysis
            ;;
        -a|--all|"")
            find_sfm_registry
            check_json_validity
            get_basic_stats
            echo ""
            check_structure
            echo ""
            run_universal_analysis
            ;;
        *)
            echo -e "${RED}❌ Неизвестная опция: $1${NC}"
            show_help
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}🎉 Анализ завершен!${NC}"
}

# Запуск главной функции
main "$@"