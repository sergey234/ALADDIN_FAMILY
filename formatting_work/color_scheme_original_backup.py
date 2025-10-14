#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Цветовая схема Matrix AI Security System
========================================

Цветовая палитра для веб-интерфейса, мобильного приложения и всех UI компонентов
системы безопасности ALADDIN.

Автор: AI Security System
Версия: 1.0.0
Дата: 2024
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ColorTheme(Enum):
    """Темы цветовой схемы"""
    MATRIX_AI = "matrix_ai"
    DARK_MATRIX = "dark_matrix"
    LIGHT_MATRIX = "light_matrix"
    ELDERLY_FRIENDLY = "elderly_friendly"
    CHILD_FRIENDLY = "child_friendly"


@dataclass
class ColorPalette:
    """Палитра цветов"""
    name: str
    primary: str
    secondary: str
    accent: str
    text: str
    background: str
    success: str
    warning: str
    error: str
    info: str


class MatrixAIColorScheme:
    """Цветовая схема Matrix AI Security System"""
    
    def __init__(self):
        self.themes = self._initialize_themes()
        self.current_theme = ColorTheme.MATRIX_AI
    
    def _initialize_themes(self) -> Dict[ColorTheme, ColorPalette]:
        """Инициализация цветовых тем"""
        return {
            ColorTheme.MATRIX_AI: ColorPalette(
                name="Matrix AI",
                primary="#1E3A8A",      # Синий грозовой
                secondary="#0F172A",    # Темно-синий
                accent="#F59E0B",       # Золотой
                text="#FFFFFF",         # Белый
                background="#1E3A8A",   # Синий грозовой
                success="#00FF41",      # Зеленый матричный
                warning="#F59E0B",      # Золотой
                error="#EF4444",        # Красный
                info="#66FF99"          # Светло-зеленый
            ),
            
            ColorTheme.DARK_MATRIX: ColorPalette(
                name="Dark Matrix",
                primary="#0F172A",      # Темно-синий
                secondary="#1E293B",    # Сланцевый
                accent="#00FF41",       # Зеленый матричный
                text="#F8FAFC",         # Светло-белый
                background="#0F172A",   # Темно-синий
                success="#00CC33",      # Темно-зеленый
                warning="#F59E0B",      # Золотой
                error="#DC2626",        # Темно-красный
                info="#60A5FA"          # Светло-синий
            ),
            
            ColorTheme.LIGHT_MATRIX: ColorPalette(
                name="Light Matrix",
                primary="#3B82F6",      # Светло-синий
                secondary="#E0E7FF",    # Очень светло-синий
                accent="#F59E0B",       # Золотой
                text="#1F2937",         # Темно-серый
                background="#FFFFFF",   # Белый
                success="#10B981",      # Зеленый
                warning="#F59E0B",      # Золотой
                error="#EF4444",        # Красный
                info="#06B6D4"          # Голубой
            ),
            
            ColorTheme.ELDERLY_FRIENDLY: ColorPalette(
                name="Elderly Friendly",
                primary="#1E40AF",      # Контрастный синий
                secondary="#F3F4F6",    # Светло-серый
                accent="#F59E0B",       # Золотой
                text="#000000",         # Черный
                background="#FFFFFF",   # Белый
                success="#059669",      # Темно-зеленый
                warning="#D97706",      # Оранжевый
                error="#DC2626",        # Красный
                info="#0284C7"          # Синий
            ),
            
            ColorTheme.CHILD_FRIENDLY: ColorPalette(
                name="Child Friendly",
                primary="#3B82F6",      # Ярко-синий
                secondary="#FEF3C7",    # Светло-желтый
                accent="#F59E0B",       # Золотой
                text="#1F2937",         # Темно-серый
                background="#F0F9FF",   # Очень светло-синий
                success="#10B981",      # Зеленый
                warning="#F59E0B",      # Золотой
                error="#EF4444",        # Красный
                info="#8B5CF6"          # Фиолетовый
            )
        }
    
    def get_theme(self, theme: ColorTheme) -> ColorPalette:
        """Получение цветовой темы"""
        return self.themes.get(theme, self.themes[ColorTheme.MATRIX_AI])
    
    def set_theme(self, theme: ColorTheme) -> None:
        """Установка текущей темы"""
        self.current_theme = theme
    
    def get_current_theme(self) -> ColorPalette:
        """Получение текущей темы"""
        return self.get_theme(self.current_theme)
    
    def get_css_variables(self, theme: ColorTheme = None) -> Dict[str, str]:
        """Получение CSS переменных для темы"""
        if theme is None:
            theme = self.current_theme
        
        palette = self.get_theme(theme)
        
        return {
            "--color-primary": palette.primary,
            "--color-secondary": palette.secondary,
            "--color-accent": palette.accent,
            "--color-text": palette.text,
            "--color-background": palette.background,
            "--color-success": palette.success,
            "--color-warning": palette.warning,
            "--color-error": palette.error,
            "--color-info": palette.info,
            "--color-primary-rgb": self._hex_to_rgb(palette.primary),
            "--color-secondary-rgb": self._hex_to_rgb(palette.secondary),
            "--color-accent-rgb": self._hex_to_rgb(palette.accent),
            "--color-text-rgb": self._hex_to_rgb(palette.text),
            "--color-background-rgb": self._hex_to_rgb(palette.background),
            "--color-success-rgb": self._hex_to_rgb(palette.success),
            "--color-warning-rgb": self._hex_to_rgb(palette.warning),
            "--color-error-rgb": self._hex_to_rgb(palette.error),
            "--color-info-rgb": self._hex_to_rgb(palette.info)
        }
    
    def get_tailwind_colors(self, theme: ColorTheme = None) -> Dict[str, str]:
        """Получение цветов для Tailwind CSS"""
        if theme is None:
            theme = self.current_theme
        
        palette = self.get_theme(theme)
        
        return {
            "primary": palette.primary,
            "secondary": palette.secondary,
            "accent": palette.accent,
            "text": palette.text,
            "background": palette.background,
            "success": palette.success,
            "warning": palette.warning,
            "error": palette.error,
            "info": palette.info
        }
    
    def get_gradient_colors(self, theme: ColorTheme = None) -> List[Dict[str, str]]:
        """Получение градиентных цветов"""
        if theme is None:
            theme = self.current_theme
        
        palette = self.get_theme(theme)
        
        gradients = [
            {
                "name": "primary_gradient",
                "from": palette.primary,
                "to": palette.secondary,
                "direction": "to bottom right"
            },
            {
                "name": "matrix_gradient",
                "from": palette.success,
                "to": palette.info,
                "direction": "to right"
            },
            {
                "name": "accent_gradient",
                "from": palette.accent,
                "to": palette.warning,
                "direction": "to bottom"
            },
            {
                "name": "dark_gradient",
                "from": palette.primary,
                "to": "#000000",
                "direction": "to bottom"
            }
        ]
        
        return gradients
    
    def get_shadow_colors(self, theme: ColorTheme = None) -> Dict[str, str]:
        """Получение цветов для теней"""
        if theme is None:
            theme = self.current_theme
        
        palette = self.get_theme(theme)
        
        return {
            "shadow_light": f"{palette.primary}20",  # 20% opacity
            "shadow_medium": f"{palette.primary}40",  # 40% opacity
            "shadow_dark": f"{palette.primary}60",    # 60% opacity
            "shadow_accent": f"{palette.accent}30",   # 30% opacity
            "shadow_success": f"{palette.success}30", # 30% opacity
            "shadow_warning": f"{palette.warning}30", # 30% opacity
            "shadow_error": f"{palette.error}30"      # 30% opacity
        }
    
    def get_accessible_colors(self, theme: ColorTheme = None) -> Dict[str, str]:
        """Получение доступных цветов (WCAG AA)"""
        if theme is None:
            theme = self.current_theme
        
        palette = self.get_theme(theme)
        
        return {
            "text_on_primary": self._get_contrast_color(palette.primary),
            "text_on_secondary": self._get_contrast_color(palette.secondary),
            "text_on_accent": self._get_contrast_color(palette.accent),
            "text_on_success": self._get_contrast_color(palette.success),
            "text_on_warning": self._get_contrast_color(palette.warning),
            "text_on_error": self._get_contrast_color(palette.error),
            "text_on_info": self._get_contrast_color(palette.info)
        }
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Конвертация HEX в RGB"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Затемнение цвета"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Осветление цвета"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _get_contrast_color(self, hex_color: str) -> str:
        """Получение контрастного цвета"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Расчет яркости
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        # Возврат белого или черного в зависимости от яркости
        return "#FFFFFF" if brightness < 128 else "#000000"
    
    def generate_css_file(self, theme: ColorTheme = None, filename: str = None) -> str:
        """Генерация CSS файла с цветовой схемой"""
        if theme is None:
            theme = self.current_theme
        
        if filename is None:
            filename = f"security/static/css/matrix_ai_colors_{theme.value}.css"
        
        css_variables = self.get_css_variables(theme)
        gradients = self.get_gradient_colors(theme)
        shadows = self.get_shadow_colors(theme)
        accessible = self.get_accessible_colors(theme)
        
        css_content = f"""/* Matrix AI Security System - Color Scheme */
/* Theme: {theme.value} */
/* Generated automatically */

:root {{
    /* Primary Colors */
    --color-primary: {css_variables['--color-primary']};
    --color-secondary: {css_variables['--color-secondary']};
    --color-accent: {css_variables['--color-accent']};
    --color-text: {css_variables['--color-text']};
    --color-background: {css_variables['--color-background']};
    
    /* Status Colors */
    --color-success: {css_variables['--color-success']};
    --color-warning: {css_variables['--color-warning']};
    --color-error: {css_variables['--color-error']};
    --color-info: {css_variables['--color-info']};
    
    /* RGB Values */
    --color-primary-rgb: {css_variables['--color-primary-rgb']};
    --color-secondary-rgb: {css_variables['--color-secondary-rgb']};
    --color-accent-rgb: {css_variables['--color-accent-rgb']};
    --color-text-rgb: {css_variables['--color-text-rgb']};
    --color-background-rgb: {css_variables['--color-background-rgb']};
    --color-success-rgb: {css_variables['--color-success-rgb']};
    --color-warning-rgb: {css_variables['--color-warning-rgb']};
    --color-error-rgb: {css_variables['--color-error-rgb']};
    --color-info-rgb: {css_variables['--color-info-rgb']};
    
    /* Accessible Colors */
    --text-on-primary: {accessible['text_on_primary']};
    --text-on-secondary: {accessible['text_on_secondary']};
    --text-on-accent: {accessible['text_on_accent']};
    --text-on-success: {accessible['text_on_success']};
    --text-on-warning: {accessible['text_on_warning']};
    --text-on-error: {accessible['text_on_error']};
    --text-on-info: {accessible['text_on_info']};
    
    /* Shadow Colors */
    --shadow-light: {shadows['shadow_light']};
    --shadow-medium: {shadows['shadow_medium']};
    --shadow-dark: {shadows['shadow_dark']};
    --shadow-accent: {shadows['shadow_accent']};
    --shadow-success: {shadows['shadow_success']};
    --shadow-warning: {shadows['shadow_warning']};
    --shadow-error: {shadows['shadow_error']};
}}

/* Gradients */
"""
        
        for gradient in gradients:
            css_content += f"""
.{gradient['name']} {{
    background: linear-gradient({gradient['direction']}, {gradient['from']}, {gradient['to']});
}}
"""
        
        css_content += """
/* Utility Classes */
.text-primary { color: var(--color-primary); }
.text-secondary { color: var(--color-secondary); }
.text-accent { color: var(--color-accent); }
.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-error { color: var(--color-error); }
.text-info { color: var(--color-info); }

.bg-primary { background-color: var(--color-primary); }
.bg-secondary { background-color: var(--color-secondary); }
.bg-accent { background-color: var(--color-accent); }
.bg-success { background-color: var(--color-success); }
.bg-warning { background-color: var(--color-warning); }
.bg-error { background-color: var(--color-error); }
.bg-info { background-color: var(--color-info); }

.border-primary { border-color: var(--color-primary); }
.border-secondary { border-color: var(--color-secondary); }
.border-accent { border-color: var(--color-accent); }
.border-success { border-color: var(--color-success); }
.border-warning { border-color: var(--color-warning); }
.border-error { border-color: var(--color-error); }
.border-info { border-color: var(--color-info); }

/* Shadows */
.shadow-light { box-shadow: 0 2px 4px var(--shadow-light); }
.shadow-medium { box-shadow: 0 4px 8px var(--shadow-medium); }
.shadow-dark { box-shadow: 0 8px 16px var(--shadow-dark); }
.shadow-accent { box-shadow: 0 4px 8px var(--shadow-accent); }
.shadow-success { box-shadow: 0 4px 8px var(--shadow-success); }
.shadow-warning { box-shadow: 0 4px 8px var(--shadow-warning); }
.shadow-error { box-shadow: 0 4px 8px var(--shadow-error); }
"""
        
        return css_content
    
    def get_theme_recommendations(self, user_type: str) -> ColorTheme:
        """Получение рекомендации темы для типа пользователя"""
        recommendations = {
            "elderly": ColorTheme.ELDERLY_FRIENDLY,
            "child": ColorTheme.CHILD_FRIENDLY,
            "professional": ColorTheme.MATRIX_AI,
            "developer": ColorTheme.DARK_MATRIX,
            "general": ColorTheme.LIGHT_MATRIX
        }
        
        return recommendations.get(user_type, ColorTheme.MATRIX_AI)
    
    def validate_color_contrast(self, background: str, text: str) -> bool:
        """Проверка контрастности цветов (WCAG AA)"""
        # Упрощенная проверка контрастности
        bg_rgb = self._hex_to_rgb(background)
        text_rgb = self._hex_to_rgb(text)
        
        # Расчет контрастности (упрощенный)
        bg_brightness = sum([int(x) for x in bg_rgb.split(', ')]) / 3
        text_brightness = sum([int(x) for x in text_rgb.split(', ')]) / 3
        
        contrast_ratio = abs(bg_brightness - text_brightness) / 255
        
        return contrast_ratio >= 0.5  # Минимальный контраст для WCAG AA


# Глобальный экземпляр цветовой схемы
color_scheme = MatrixAIColorScheme()


def get_color_scheme() -> MatrixAIColorScheme:
    """Получение глобального экземпляра цветовой схемы"""
    return color_scheme


def generate_all_theme_files() -> List[str]:
    """Генерация CSS файлов для всех тем"""
    generated_files = []
    
    for theme in ColorTheme:
        filename = f"security/static/css/matrix_ai_colors_{theme.value}.css"
        css_content = color_scheme.generate_css_file(theme, filename)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        generated_files.append(filename)
    
    return generated_files


if __name__ == "__main__":
    # Тестирование цветовой схемы
    scheme = MatrixAIColorScheme()
    
    print("🎨 Matrix AI Color Scheme")
    print("=" * 50)
    
    # Показать все темы
    for theme in ColorTheme:
        palette = scheme.get_theme(theme)
        print(f"\n{theme.value.upper()}:")
        print(f"  Primary: {palette.primary}")
        print(f"  Secondary: {palette.secondary}")
        print(f"  Accent: {palette.accent}")
        print(f"  Text: {palette.text}")
        print(f"  Background: {palette.background}")
    
    # Генерация CSS файлов
    print("\n📁 Генерация CSS файлов...")
    generated_files = generate_all_theme_files()
    print(f"✅ Создано {len(generated_files)} CSS файлов")
    
    # Тестирование контрастности
    print("\n🔍 Тестирование контрастности...")
    test_combinations = [
        ("#1E3A8A", "#FFFFFF"),  # Синий + Белый
        ("#F59E0B", "#000000"),  # Золотой + Черный
        ("#00FF41", "#000000"),  # Зеленый + Черный
    ]
    
    for bg, text in test_combinations:
        contrast_ok = scheme.validate_color_contrast(bg, text)
        print(f"  {bg} + {text}: {'✅' if contrast_ok else '❌'}")
    
    print("\n🎉 Цветовая схема Matrix AI готова к использованию!")