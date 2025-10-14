package family.aladdin.android.ui.theme

import androidx.compose.ui.unit.dp

/**
 * 📐 ALADDIN Dimensions System
 * Все размеры взяты из iOS Spacing.swift
 */

object Spacing {
    // Standard Spacing
    val XXS = 4.dp
    val XS = 8.dp
    val S = 12.dp
    val M = 16.dp
    val L = 24.dp
    val XL = 32.dp
    val XXL = 48.dp
    
    // Specific Use Cases
    val CardSpacing = 16.dp
    val CardPadding = 20.dp
    val ScreenPadding = 20.dp
    val SectionSpacing = 32.dp
}

object CornerRadius {
    val Small = 8.dp
    val Medium = 12.dp
    val Large = 16.dp
    val XLarge = 24.dp
    val Full = 999.dp
}

object Size {
    // Icons
    val IconSmall = 16.dp
    val IconMedium = 24.dp
    val IconLarge = 48.dp
    val IconXLarge = 64.dp
    
    // Buttons
    val ButtonMinHeight = 44.dp
    val ButtonHeight = 48.dp
    val ButtonLargeHeight = 60.dp
    val SOSButtonSize = 120.dp
    
    // Cards
    val CardMinHeight = 100.dp
    val FunctionCardHeight = 140.dp
    
    // Avatar
    val AvatarSmall = 32.dp
    val AvatarMedium = 48.dp
    val AvatarSize = 48.dp
    val AvatarLarge = 80.dp
    
    // Status Indicator
    val StatusIndicator = 12.dp
    val StatusIndicatorLarge = 16.dp
    
    // Toggle Switch
    val ToggleWidth = 51.dp
    val ToggleHeight = 31.dp
    val ToggleKnob = 27.dp
    
    // Slider
    val SliderTrackHeight = 4.dp
    val SliderKnob = 28.dp
    
    // Navigation
    val NavButtonSize = 40.dp
}

// MARK: - Aliases for easier usage (camelCase style)
// Эти aliases упрощают использование в коде

// Spacing aliases
val SpacingXXS = Spacing.XXS
val SpacingXS = Spacing.XS
val SpacingS = Spacing.S
val SpacingM = Spacing.M
val SpacingL = Spacing.L
val SpacingXL = Spacing.XL
val SpacingXXL = Spacing.XXL

// Specific spacing aliases
val CardPadding = Spacing.CardPadding
val ScreenPadding = Spacing.ScreenPadding

// Corner radius aliases
val CornerRadiusSmall = CornerRadius.Small
val CornerRadiusMedium = CornerRadius.Medium
val CornerRadiusLarge = CornerRadius.Large

// Size aliases
val StatusIndicatorLarge = Size.StatusIndicatorLarge



