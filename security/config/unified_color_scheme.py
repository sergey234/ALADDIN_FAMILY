#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Color Scheme - "Грозовое небо с золотыми акцентами"
============================================================

Единая цветовая схема для всего приложения ALADDIN:
- Основное приложение
- VPN модуль
- Мобильное приложение (iOS + Android)
- Веб-интерфейс

Автор: ALADDIN Security Team
Версия: 2.0.0
Дата: 2025-01-27
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class ColorTheme(Enum):
    """Темы цветовой схемы"""
    STORM_SKY = "storm_sky"           # Грозовое небо (основная)
    STORM_SKY_DARK = "storm_sky_dark" # Темное грозовое небо
    STORM_SKY_LIGHT = "storm_sky_light" # Светлое грозовое небо
    ELDERLY_FRIENDLY = "elderly_friendly" # Для пожилых
    CHILD_FRIENDLY = "child_friendly" # Для детей


@dataclass
class ColorPalette:
    """Палитра цветов"""
    name: str
    primary: str
    secondary: str
    tertiary: str
    accent: str
    text: str
    background: str
    success: str
    warning: str
    error: str
    info: str


class UnifiedColorScheme:
    """Единая цветовая схема "Грозовое небо" для всего приложения ALADDIN"""

    def __init__(self):
        self.themes = self._initialize_themes()
        self.current_theme = ColorTheme.STORM_SKY

    def _initialize_themes(self) -> Dict[ColorTheme, ColorPalette]:
        """Инициализация цветовых тем"""
        return {
            ColorTheme.STORM_SKY: ColorPalette(
                name="Грозовое небо",
                primary="#1e3a5f",      # Синий грозового неба
                secondary="#0a1128",    # Темно-синий глубокий
                tertiary="#2e5090",     # Средний синий
                accent="#F59E0B",       # Золотой основной
                text="#FFFFFF",         # Белый
                background="#1e3a5f",   # Синий грозового неба
                success="#10B981",      # Изумрудный успех
                warning="#F59E0B",      # Золотой предупреждение
                error="#EF4444",        # Рубиновый ошибка
                info="#60A5FA",         # Голубой молнии
            ),
            ColorTheme.STORM_SKY_DARK: ColorPalette(
                name="Темное грозовое небо",
                primary="#0a1128",      # Темно-синий глубокий
                secondary="#1e3a5f",    # Синий грозового неба
                tertiary="#2e5090",     # Средний синий
                accent="#F59E0B",       # Золотой основной
                text="#FFFFFF",         # Белый
                background="#0a1128",   # Темно-синий глубокий
                success="#10B981",      # Изумрудный успех
                warning="#F59E0B",      # Золотой предупреждение
                error="#EF4444",        # Рубиновый ошибка
                info="#60A5FA",         # Голубой молнии
            ),
            ColorTheme.STORM_SKY_LIGHT: ColorPalette(
                name="Светлое грозовое небо",
                primary="#2e5090",      # Средний синий
                secondary="#1e3a5f",    # Синий грозового неба
                tertiary="#60A5FA",     # Голубой молнии
                accent="#F59E0B",       # Золотой основной
                text="#FFFFFF",         # Белый
                background="#2e5090",   # Средний синий
                success="#10B981",      # Изумрудный успех
                warning="#F59E0B",      # Золотой предупреждение
                error="#EF4444",        # Рубиновый ошибка
                info="#60A5FA",         # Голубой молнии
            ),
            ColorTheme.ELDERLY_FRIENDLY: ColorPalette(
                name="Грозовое небо для пожилых",
                primary="#1e3a5f",      # Синий грозового неба
                secondary="#F3F4F6",    # Светло-серый
                tertiary="#2e5090",     # Средний синий
                accent="#F59E0B",       # Золотой основной
                text="#000000",         # Черный (контрастный)
                background="#FFFFFF",   # Белый
                success="#059669",      # Темно-зеленый
                warning="#D97706",      # Оранжевый
                error="#DC2626",        # Темно-красный
                info="#0284C7",         # Синий
            ),
            ColorTheme.CHILD_FRIENDLY: ColorPalette(
                name="Грозовое небо для детей",
                primary="#2e5090",      # Средний синий
                secondary="#FEF3C7",    # Светло-желтый
                tertiary="#60A5FA",     # Голубой молнии
                accent="#F59E0B",       # Золотой основной
                text="#1F2937",         # Темно-серый
                background="#F0F9FF",   # Очень светло-синий
                success="#10B981",      # Зеленый
                warning="#F59E0B",      # Золотой
                error="#EF4444",        # Красный
                info="#8B5CF6",         # Фиолетовый
            ),
        }

    def get_theme(self, theme: ColorTheme) -> ColorPalette:
        """Получение цветовой темы"""
        return self.themes.get(theme, self.themes[ColorTheme.STORM_SKY])

    def set_theme(self, theme: ColorTheme) -> None:
        """Установка текущей темы"""
        self.current_theme = theme

    def get_current_theme(self) -> ColorPalette:
        """Получение текущей темы"""
        return self.get_theme(self.current_theme)

    def get_storm_sky_gradient(self, theme: ColorTheme = None) -> str:
        """Получение градиента грозового неба"""
        if theme is None:
            theme = self.current_theme

        palette = self.get_theme(theme)
        
        if theme == ColorTheme.STORM_SKY:
            return f"linear-gradient(to bottom, {palette.secondary} 0%, {palette.primary} 20%, {palette.tertiary} 40%, {palette.primary} 60%, {palette.secondary} 100%)"
        elif theme == ColorTheme.STORM_SKY_DARK:
            return f"linear-gradient(to bottom, {palette.primary} 0%, {palette.secondary} 50%, {palette.primary} 100%)"
        elif theme == ColorTheme.STORM_SKY_LIGHT:
            return f"linear-gradient(to bottom, {palette.primary} 0%, {palette.tertiary} 50%, {palette.primary} 100%)"
        else:
            return f"linear-gradient(135deg, {palette.primary}, {palette.tertiary})"

    def get_gold_gradient(self, theme: ColorTheme = None) -> str:
        """Получение золотого градиента"""
        if theme is None:
            theme = self.current_theme

        palette = self.get_theme(theme)
        return f"linear-gradient(135deg, {palette.accent} 0%, #FCD34D 50%, #D97706 100%)"

    def get_css_variables(self, theme: ColorTheme = None) -> Dict[str, str]:
        """Получение CSS переменных для темы"""
        if theme is None:
            theme = self.current_theme

        palette = self.get_theme(theme)

        return {
            "--color-primary": palette.primary,
            "--color-secondary": palette.secondary,
            "--color-tertiary": palette.tertiary,
            "--color-accent": palette.accent,
            "--color-text": palette.text,
            "--color-background": palette.background,
            "--color-success": palette.success,
            "--color-warning": palette.warning,
            "--color-error": palette.error,
            "--color-info": palette.info,
            "--storm-sky-gradient": self.get_storm_sky_gradient(theme),
            "--gold-gradient": self.get_gold_gradient(theme),
        }

    def get_ios_colors(self, theme: ColorTheme = None) -> Dict[str, str]:
        """Получение цветов для iOS (Swift)"""
        if theme is None:
            theme = self.current_theme

        palette = self.get_theme(theme)

        return {
            "stormSkyDark": palette.secondary,
            "stormSkyMain": palette.primary,
            "stormSkyMid": palette.tertiary,
            "goldMain": palette.accent,
            "goldLight": "#FCD34D",
            "goldDark": "#D97706",
            "white": palette.text,
            "lightningBlue": palette.info,
            "successGreen": palette.success,
            "errorRed": palette.error,
        }

    def get_android_colors(self, theme: ColorTheme = None) -> Dict[str, str]:
        """Получение цветов для Android (Kotlin)"""
        if theme is None:
            theme = self.current_theme

        palette = self.get_theme(theme)

        return {
            "stormSkyDark": palette.secondary,
            "stormSkyMain": palette.primary,
            "stormSkyMid": palette.tertiary,
            "goldMain": palette.accent,
            "goldLight": "#FCD34D",
            "goldDark": "#D97706",
            "white": palette.text,
            "lightningBlue": palette.info,
            "successGreen": palette.success,
            "errorRed": palette.error,
        }

    def generate_mobile_css(self, theme: ColorTheme = None) -> str:
        """Генерация CSS для мобильного приложения"""
        if theme is None:
            theme = self.current_theme

        palette = self.get_theme(theme)
        css_vars = self.get_css_variables(theme)

        return f"""
/* ALADDIN Mobile App - Storm Sky Theme */
:root {{
    /* Storm Sky Colors */
    --storm-sky-dark: {palette.secondary};
    --storm-sky-main: {palette.primary};
    --storm-sky-mid: {palette.tertiary};
    
    /* Gold Accents */
    --gold-main: {palette.accent};
    --gold-light: #FCD34D;
    --gold-dark: #D97706;
    
    /* Status Colors */
    --success-green: {palette.success};
    --error-red: {palette.error};
    --info-blue: {palette.info};
    
    /* Text Colors */
    --text-primary: {palette.text};
    --text-secondary: rgba(255, 255, 255, 0.8);
    
    /* Background */
    --bg-primary: {palette.background};
    --bg-gradient: {css_vars['--storm-sky-gradient']};
    --bg-card: rgba(255, 255, 255, 0.95);
    
    /* Shadows */
    --shadow-gold: 0 0 20px rgba(245, 158, 11, 0.3);
    --shadow-blue: 0 0 20px rgba(96, 165, 250, 0.3);
    --shadow-success: 0 0 20px rgba(16, 185, 129, 0.3);
    --shadow-error: 0 0 20px rgba(239, 68, 68, 0.3);
}}

/* Storm Sky Background */
.storm-sky-bg {{
    background: var(--bg-gradient);
    min-height: 100vh;
}}

/* Gold Accent Elements */
.gold-accent {{
    color: var(--gold-main);
    text-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
}}

.gold-button {{
    background: var(--gold-gradient);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 12px 24px;
    font-weight: bold;
    box-shadow: var(--shadow-gold);
    transition: all 0.3s ease;
}}

.gold-button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 0 30px rgba(245, 158, 11, 0.5);
}}

/* Cards */
.storm-card {{
    background: var(--bg-card);
    border: 2px solid rgba(245, 158, 11, 0.3);
    border-radius: 20px;
    padding: 20px;
    box-shadow: var(--shadow-gold);
    backdrop-filter: blur(10px);
}}

/* Status Indicators */
.status-connected {{
    background: radial-gradient(circle, var(--success-green) 0%, #059669 100%);
    box-shadow: var(--shadow-success);
}}

.status-disconnected {{
    background: radial-gradient(circle, var(--error-red) 0%, #DC2626 100%);
    box-shadow: var(--shadow-error);
}}

/* Lightning Effects */
.lightning-effect {{
    background: radial-gradient(ellipse at center,
        rgba(96, 165, 250, 0.2) 0%,
        rgba(59, 130, 246, 0.1) 30%,
        transparent 70%
    );
    animation: lightning 3s linear infinite;
}}

@keyframes lightning {{
    0%, 100% {{ opacity: 0.3; transform: translateY(0px); }}
    50% {{ opacity: 0.8; transform: translateY(-10px); }}
}}
"""


# Глобальный экземпляр цветовой схемы
unified_color_scheme = UnifiedColorScheme()


def get_unified_color_scheme() -> UnifiedColorScheme:
    """Получение глобального экземпляра цветовой схемы"""
    return unified_color_scheme


if __name__ == "__main__":
    # Тестирование цветовой схемы
    scheme = UnifiedColorScheme()

    print("🌌 ALADDIN Unified Color Scheme - 'Грозовое небо'")
    print("=" * 60)

    # Показать все темы
    for theme in ColorTheme:
        palette = scheme.get_theme(theme)
        print(f"\n{theme.value.upper()}:")
        print(f"  Primary: {palette.primary}")
        print(f"  Secondary: {palette.secondary}")
        print(f"  Tertiary: {palette.tertiary}")
        print(f"  Accent: {palette.accent}")
        print(f"  Text: {palette.text}")
        print(f"  Background: {palette.background}")

    # Генерация мобильного CSS
    print("\n📱 Генерация мобильного CSS...")
    mobile_css = scheme.generate_mobile_css()
    
    with open("ALADDIN_NEW/security/static/css/unified_mobile_theme.css", "w", encoding="utf-8") as f:
        f.write(mobile_css)
    
    print("✅ Создан unified_mobile_theme.css")

    print("\n🎉 Единая цветовая схема 'Грозовое небо' готова!")

