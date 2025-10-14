package family.aladdin.android.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

/**
 * 🎨 ALADDIN Theme
 * Главная тема приложения
 */

private val ALADDINColorScheme = darkColorScheme(
    primary = PrimaryBlue,
    secondary = SecondaryBlue,
    tertiary = SecondaryGold,
    background = BackgroundDark,
    surface = SurfaceDark,
    error = DangerRed,
    onPrimary = Color.White,
    onSecondary = Color.White,
    onTertiary = BackgroundDark,
    onBackground = TextPrimary,
    onSurface = TextPrimary,
    onError = Color.White
)

@Composable
fun ALADDINTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    // TODO: Use darkTheme for theme switching
    MaterialTheme(
        colorScheme = ALADDINColorScheme,
        typography = ALADDINTypography,
        content = content
    )
}



