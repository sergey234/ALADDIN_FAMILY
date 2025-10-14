package family.aladdin.android.accessibility

import android.content.Context
import android.view.accessibility.AccessibilityManager as SystemAccessibilityManager
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * 🦯 Accessibility Manager
 * Управление доступностью для людей с ограниченными возможностями
 * TalkBack, Scalable Text, Color Blind Mode, Touch Targets
 */

class AccessibilityManager(private val context: Context) {
    
    // MARK: - Properties
    
    private val systemAccessibilityManager = context.getSystemService(Context.ACCESSIBILITY_SERVICE) as SystemAccessibilityManager
    
    private val _isTalkBackEnabled = MutableStateFlow(false)
    val isTalkBackEnabled: StateFlow<Boolean> = _isTalkBackEnabled.asStateFlow()
    
    private val _colorBlindMode = MutableStateFlow(ColorBlindMode.NONE)
    val colorBlindMode: StateFlow<ColorBlindMode> = _colorBlindMode.asStateFlow()
    
    // MARK: - Color Blind Mode
    
    enum class ColorBlindMode(val displayName: String, val icon: String) {
        NONE("Обычный", "👁️"),
        PROTANOPIA("Протанопия (красный-зелёный)", "🔴"),
        DEUTERANOPIA("Дейтеранопия (красный-зелёный)", "🟢"),
        TRITANOPIA("Тританопия (сине-жёлтый)", "🔵"),
        MONOCHROMACY("Монохромазия (ч/б)", "⚫")
    }
    
    // MARK: - Init
    
    init {
        checkTalkBackStatus()
    }
    
    // MARK: - Check TalkBack
    
    /**
     * Проверить статус TalkBack
     */
    private fun checkTalkBackStatus() {
        _isTalkBackEnabled.value = systemAccessibilityManager.isEnabled &&
            systemAccessibilityManager.isTouchExplorationEnabled
        
        println("🦯 TalkBack: ${if (_isTalkBackEnabled.value) "ON" else "OFF"}")
    }
    
    /**
     * TalkBack включён?
     */
    fun isTalkBackRunning(): Boolean {
        return _isTalkBackEnabled.value
    }
    
    // MARK: - Color Blind Mode
    
    /**
     * Установить режим дальтонизма
     */
    fun setColorBlindMode(mode: ColorBlindMode) {
        _colorBlindMode.value = mode
        
        // Сохранить в SharedPreferences
        val prefs = context.getSharedPreferences("aladdin_prefs", Context.MODE_PRIVATE)
        prefs.edit().putString("colorBlindMode", mode.name).apply()
        
        println("👁️ Color Blind Mode: ${mode.displayName}")
    }
    
    /**
     * Получить сохранённый режим
     */
    fun getSavedColorBlindMode(): ColorBlindMode {
        val prefs = context.getSharedPreferences("aladdin_prefs", Context.MODE_PRIVATE)
        val modeName = prefs.getString("colorBlindMode", ColorBlindMode.NONE.name)
        return try {
            ColorBlindMode.valueOf(modeName ?: ColorBlindMode.NONE.name)
        } catch (e: Exception) {
            ColorBlindMode.NONE
        }
    }
    
    // MARK: - Touch Target Validation
    
    /**
     * Проверить что элемент достаточно большой для касания
     * Минимум 48dp согласно Material Design
     */
    fun isValidTouchTarget(sizeDp: Float): Boolean {
        return sizeDp >= 48f
    }
    
    /**
     * Рекомендуемый минимальный размер касания
     */
    companion object {
        const val MIN_TOUCH_TARGET_SIZE_DP = 48f
        const val RECOMMENDED_TOUCH_TARGET_SIZE_DP = 56f
    }
}

// MARK: - Composable Helpers

/**
 * Composable для получения AccessibilityManager
 */
@Composable
fun rememberAccessibilityManager(): AccessibilityManager {
    val context = LocalContext.current
    return remember { AccessibilityManager(context) }
}

/**
 * Modifier для добавления content description (для TalkBack)
 */
fun Modifier.accessibilityDescription(description: String): Modifier {
    return this.semantics {
        contentDescription = description
    }
}

/**
 * Modifier для минимального touch target
 */
fun Modifier.minimumTouchTarget(): Modifier {
    return this.sizeIn(
        minWidth = AccessibilityManager.MIN_TOUCH_TARGET_SIZE_DP.dp,
        minHeight = AccessibilityManager.MIN_TOUCH_TARGET_SIZE_DP.dp
    )
}



