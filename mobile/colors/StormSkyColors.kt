package com.aladdin.mobile.colors

import android.graphics.Color
import androidx.compose.ui.graphics.Color as ComposeColor

/**
 * Unified Color Scheme - "Грозовое небо с золотыми акцентами"
 * Для Android приложения ALADDIN
 *
 * Created: 2025-01-27
 * Version: 2.0.0
 */
object StormSkyColors {
    
    // MARK: - Storm Sky Colors (Грозовое небо)
    
    /**
     * Темно-синий глубокий - верх и низ неба
     */
    val stormSkyDark = Color.parseColor("#0a1128")
    val stormSkyDarkCompose = ComposeColor(0x0a1128)
    
    /**
     * Синий грозового неба - основной цвет
     */
    val stormSkyMain = Color.parseColor("#1e3a5f")
    val stormSkyMainCompose = ComposeColor(0x1e3a5f)
    
    /**
     * Средний синий - центр неба
     */
    val stormSkyMid = Color.parseColor("#2e5090")
    val stormSkyMidCompose = ComposeColor(0x2e5090)
    
    // MARK: - Gold Accents (Золотые акценты)
    
    /**
     * Золотой основной - заголовки, кнопки, акценты
     */
    val goldMain = Color.parseColor("#F59E0B")
    val goldMainCompose = ComposeColor(0xF59E0B)
    
    /**
     * Золотой светлый - hover эффекты
     */
    val goldLight = Color.parseColor("#FCD34D")
    val goldLightCompose = ComposeColor(0xFCD34D)
    
    /**
     * Золотой темный - тени, градиенты
     */
    val goldDark = Color.parseColor("#D97706")
    val goldDarkCompose = ComposeColor(0xD97706)
    
    // MARK: - Status Colors (Цвета статусов)
    
    /**
     * Изумрудный успех - статус "Подключено"
     */
    val successGreen = Color.parseColor("#10B981")
    val successGreenCompose = ComposeColor(0x10B981)
    
    /**
     * Рубиновый ошибка - статус "Отключено"
     */
    val errorRed = Color.parseColor("#EF4444")
    val errorRedCompose = ComposeColor(0xEF4444)
    
    /**
     * Голубой молнии - эффекты, анимации
     */
    val lightningBlue = Color.parseColor("#60A5FA")
    val lightningBlueCompose = ComposeColor(0x60A5FA)
    
    // MARK: - Text Colors (Цвета текста)
    
    /**
     * Белый чистый - основной текст
     */
    val white = Color.WHITE
    val whiteCompose = ComposeColor.White
    
    /**
     * Белый полупрозрачный - вторичный текст
     */
    val whiteSecondary = Color.argb(204, 255, 255, 255) // 80% opacity
    val whiteSecondaryCompose = ComposeColor.White.copy(alpha = 0.8f)
    
    /**
     * Темно-серый - текст на светлом фоне
     */
    val darkGray = Color.parseColor("#1F2937")
    val darkGrayCompose = ComposeColor(0x1F2937)
    
    // MARK: - Background Colors (Цвета фона)
    
    /**
     * Основной фон - грозовое небо
     */
    val backgroundPrimary = stormSkyMain
    val backgroundPrimaryCompose = stormSkyMainCompose
    
    /**
     * Карточки - белый с прозрачностью
     */
    val cardBackground = Color.argb(242, 255, 255, 255) // 95% opacity
    val cardBackgroundCompose = ComposeColor.White.copy(alpha = 0.95f)
    
    /**
     * Вторичный фон
     */
    val backgroundSecondary = stormSkyDark
    val backgroundSecondaryCompose = stormSkyDarkCompose
    
    // MARK: - Gradient Colors (Цвета градиентов)
    
    /**
     * Цвета для градиента грозового неба
     */
    val stormSkyGradientColors = listOf(
        stormSkyDarkCompose,
        stormSkyMainCompose,
        stormSkyMidCompose,
        stormSkyMainCompose,
        stormSkyDarkCompose
    )
    
    /**
     * Цвета для золотого градиента
     */
    val goldGradientColors = listOf(
        goldMainCompose,
        goldLightCompose,
        goldDarkCompose
    )
    
    /**
     * Цвета для градиента успеха
     */
    val successGradientColors = listOf(
        successGreenCompose,
        ComposeColor(0x059669)
    )
    
    /**
     * Цвета для градиента ошибки
     */
    val errorGradientColors = listOf(
        errorRedCompose,
        ComposeColor(0xDC2626)
    )
    
    // MARK: - Shadow Colors (Цвета теней)
    
    /**
     * Золотая тень
     */
    val goldShadow = Color.argb(77, 0, 0, 0) // 30% opacity
    val goldShadowCompose = ComposeColor.Black.copy(alpha = 0.3f)
    
    /**
     * Синяя тень
     */
    val blueShadow = Color.argb(77, 96, 165, 250) // 30% opacity
    val blueShadowCompose = lightningBlueCompose.copy(alpha = 0.3f)
    
    /**
     * Зеленая тень
     */
    val greenShadow = Color.argb(77, 16, 185, 129) // 30% opacity
    val greenShadowCompose = successGreenCompose.copy(alpha = 0.3f)
    
    /**
     * Красная тень
     */
    val redShadow = Color.argb(77, 239, 68, 68) // 30% opacity
    val redShadowCompose = errorRedCompose.copy(alpha = 0.3f)
}

/**
 * Расширения для работы с цветами
 */
object ColorUtils {
    
    /**
     * Создание цвета из HEX строки
     */
    fun fromHex(hex: String): Color {
        return Color.parseColor(hex)
    }
    
    /**
     * Создание Compose цвета из HEX строки
     */
    fun fromHexCompose(hex: String): ComposeColor {
        val cleanHex = hex.replace("#", "")
        return ComposeColor(cleanHex.toLong(16))
    }
    
    /**
     * Получение контрастного цвета для текста
     */
    fun getContrastText(backgroundColor: Color): Color {
        val r = Color.red(backgroundColor)
        val g = Color.green(backgroundColor)
        val b = Color.blue(backgroundColor)
        
        // Расчет яркости
        val brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        return if (brightness < 128) Color.WHITE else Color.BLACK
    }
    
    /**
     * Получение контрастного Compose цвета для текста
     */
    fun getContrastTextCompose(backgroundColor: ComposeColor): ComposeColor {
        val r = backgroundColor.red
        val g = backgroundColor.green
        val b = backgroundColor.blue
        
        // Расчет яркости
        val brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        return if (brightness < 0.5f) ComposeColor.White else ComposeColor.Black
    }
}

/**
 * Константы для использования в XML ресурсах
 */
object StormSkyColorsRes {
    
    // Storm Sky Colors
    const val STORM_SKY_DARK = "#0a1128"
    const val STORM_SKY_MAIN = "#1e3a5f"
    const val STORM_SKY_MID = "#2e5090"
    
    // Gold Accents
    const val GOLD_MAIN = "#F59E0B"
    const val GOLD_LIGHT = "#FCD34D"
    const val GOLD_DARK = "#D97706"
    
    // Status Colors
    const val SUCCESS_GREEN = "#10B981"
    const val ERROR_RED = "#EF4444"
    const val LIGHTNING_BLUE = "#60A5FA"
    
    // Text Colors
    const val WHITE = "#FFFFFF"
    const val DARK_GRAY = "#1F2937"
    
    // Background Colors
    const val CARD_BACKGROUND = "#FFFFFF"
}

/**
 * Пример использования в Compose
 */
/*
@Composable
fun StormSkyExample() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(StormSkyColors.stormSkyGradientColors[0])
            .padding(16.dp)
    ) {
        // Заголовок с золотым акцентом
        Text(
            text = "ALADDIN Security",
            style = MaterialTheme.typography.h3,
            color = StormSkyColors.goldMainCompose,
            modifier = Modifier.shadow(4.dp, RoundedCornerShape(8.dp))
        )
        
        // Карточка в стиле грозового неба
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            backgroundColor = StormSkyColors.cardBackgroundCompose,
            elevation = 8.dp
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Статус безопасности",
                    style = MaterialTheme.typography.h6,
                    color = StormSkyColors.darkGrayCompose
                )
                
                Text(
                    text = "Защищено",
                    style = MaterialTheme.typography.body1,
                    color = StormSkyColors.successGreenCompose
                )
            }
        }
        
        // Золотая кнопка
        Button(
            onClick = { /* Action */ },
            colors = ButtonDefaults.buttonColors(
                containerColor = StormSkyColors.goldMainCompose
            ),
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp)
        ) {
            Text(
                text = "Подключить VPN",
                color = ComposeColor.White
            )
        }
    }
}
*/

