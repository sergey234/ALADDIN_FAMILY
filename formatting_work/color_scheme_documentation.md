# Документация файла color_scheme.py

## Общая информация
- **Файл**: `security/config/color_scheme.py`
- **Размер**: 19KB, 491 строка
- **Назначение**: Цветовая схема Matrix AI Security System
- **Версия**: 1.0.0
- **Автор**: AI Security System

## Структура файла

### Импорты
```python
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
```

### Классы
1. **ColorTheme** (Enum) - Темы цветовой схемы
2. **ColorPalette** (dataclass) - Палитра цветов
3. **MatrixAIColorScheme** - Основной класс цветовой схемы

### Методы MatrixAIColorScheme
- `__init__()` - Инициализация
- `_initialize_themes()` - Инициализация тем
- `get_theme()` - Получение темы
- `set_theme()` - Установка темы
- `get_current_theme()` - Получение текущей темы
- `get_css_variables()` - CSS переменные
- `get_tailwind_colors()` - Tailwind CSS цвета
- `get_gradient_colors()` - Градиентные цвета
- `get_shadow_colors()` - Цвета теней
- `get_accessible_colors()` - Доступные цвета
- `_hex_to_rgb()` - Конвертация HEX в RGB
- `_darken_color()` - Затемнение цвета
- `_lighten_color()` - Осветление цвета
- `_get_contrast_color()` - Контрастный цвет
- `generate_css_file()` - Генерация CSS файла
- `get_theme_recommendations()` - Рекомендации тем
- `validate_color_contrast()` - Проверка контрастности

### Глобальные функции
- `get_color_scheme()` - Получение глобального экземпляра
- `generate_all_theme_files()` - Генерация всех CSS файлов

### Темы
1. MATRIX_AI - Основная тема
2. DARK_MATRIX - Темная тема
3. LIGHT_MATRIX - Светлая тема
4. ELDERLY_FRIENDLY - Для пожилых
5. CHILD_FRIENDLY - Для детей

## Зависимости
- Стандартные библиотеки Python (typing, dataclasses, enum)
- Нет внешних зависимостей

## Использование
Файл используется в различных компонентах системы для:
- Генерации CSS переменных
- Создания цветовых схем для UI
- Обеспечения доступности цветов
- Поддержки различных тем

## Потенциальные проблемы
- Длинные строки (E501)
- Возможные проблемы с импортами
- Необходимость проверки качества кода