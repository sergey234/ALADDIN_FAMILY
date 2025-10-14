package family.aladdin.android.ui.theme

import androidx.compose.foundation.background
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

/**
 * 🎨 ALADDIN Modifiers
 * Удобные модификаторы для стилизации UI
 */

// MARK: - Background Gradients

/**
 * Основной градиент фона приложения
 * Источник: iOS LinearGradient.backgroundGradient
 */
fun Modifier.backgroundGradient(): Modifier = this.background(
    brush = Brush.linearGradient(
        colors = listOf(
            GradientStart,
            GradientMiddle,
            GradientEnd
        )
    )
)

/**
 * Градиент для карточек
 * Источник: iOS LinearGradient.cardGradient
 */
fun Modifier.cardBackground(): Modifier = this
    .clip(RoundedCornerShape(CornerRadius.Large))
    .background(
        brush = Brush.linearGradient(
            colors = listOf(
                Color(0xFF1E3A5F),
                Color(0xFF2E5090)
            )
        )
    )

/**
 * Простой фон карточки (без градиента)
 */
fun Modifier.cardBackgroundSimple(): Modifier = this
    .clip(RoundedCornerShape(CornerRadius.Large))
    .background(SurfaceDark)

/**
 * Glassmorphism эффект для карточек
 */
fun Modifier.glassmorphismBackground(): Modifier = this
    .clip(RoundedCornerShape(CornerRadius.Large))
    .background(
        color = Color.White.copy(alpha = 0.1f)
    )

// MARK: - Gradient Helpers

/**
 * Градиент для кнопок
 */
fun Modifier.buttonGradient(): Modifier = this.background(
    brush = Brush.linearGradient(
        colors = listOf(
            PrimaryBlue,
            SecondaryBlue
        )
    )
)

/**
 * Градиент для Unicorn элементов
 */
fun Modifier.unicornGradient(): Modifier = this.background(
    brush = Brush.linearGradient(
        colors = listOf(
            UnicornPurple,
            UnicornPink
        )
    )
)

/**
 * Градиент успеха (зелёный)
 */
fun Modifier.successGradient(): Modifier = this.background(
    brush = Brush.linearGradient(
        colors = listOf(
            SuccessGreen,
            Color(0xFF059669)
        )
    )
)

/**
 * Градиент опасности (красный)
 */
fun Modifier.dangerGradient(): Modifier = this.background(
    brush = Brush.linearGradient(
        colors = listOf(
            DangerRed,
            Color(0xFFDC2626)
        )
    )
)

// MARK: - Shape Helpers

/**
 * Скругление карточки
 */
fun Modifier.cardShape(): Modifier = this.clip(RoundedCornerShape(CornerRadius.Large))

/**
 * Скругление кнопки
 */
fun Modifier.buttonShape(): Modifier = this.clip(RoundedCornerShape(CornerRadius.Medium))

/**
 * Полное скругление (pill shape)
 */
fun Modifier.pillShape(): Modifier = this.clip(RoundedCornerShape(CornerRadius.Full))



