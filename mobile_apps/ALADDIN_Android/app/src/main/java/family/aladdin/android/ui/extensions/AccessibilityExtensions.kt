package family.aladdin.android.ui.extensions

import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.material.ripple.rememberRipple
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.*
import androidx.compose.ui.state.ToggleableState
import androidx.compose.ui.unit.dp

/**
 * 🦯 Accessibility Extensions
 * Расширения для доступности Jetpack Compose
 * Упрощают добавление TalkBack и других функций
 */

// MARK: - Modifier Extensions

/**
 * Добавить TalkBack description для кнопки
 */
@Composable
fun Modifier.accessibilityButton(
    label: String,
    hint: String? = null,
    onClick: () -> Unit
): Modifier {
    return this
        .clickable(
            onClick = onClick,
            role = Role.Button,
            interactionSource = remember { MutableInteractionSource() },
            indication = rememberRipple()
        )
        .semantics {
            contentDescription = if (hint != null) "$label. $hint" else label
            role = Role.Button
        }
}

/**
 * Добавить content description (для TalkBack)
 */
fun Modifier.accessibilityDescription(description: String): Modifier {
    return this.semantics {
        contentDescription = description
    }
}

/**
 * Добавить accessibility для заголовка
 */
fun Modifier.accessibilityHeading(label: String): Modifier {
    return this.semantics {
        heading()
        contentDescription = label
    }
}

/**
 * Добавить accessibility для изображения
 */
fun Modifier.accessibilityImage(label: String, isDecorative: Boolean = false): Modifier {
    return if (isDecorative) {
        this.semantics { 
            // Декоративное изображение - скрываем от TalkBack
        }
    } else {
        this.semantics {
            contentDescription = label
            role = Role.Image
        }
    }
}

/**
 * Добавить accessibility для toggle/switch
 */
fun Modifier.accessibilityToggle(label: String, isOn: Boolean): Modifier {
    return this.semantics {
        contentDescription = "$label. ${if (isOn) "Включено" else "Выключено"}"
        role = Role.Switch
        toggleableState = ToggleableState(isOn)
    }
}

/**
 * Минимальный размер для касания (48dp)
 */
fun Modifier.minimumTouchTarget(): Modifier {
    return this.sizeIn(
        minWidth = 48.dp,
        minHeight = 48.dp
    )
}

/**
 * Скрыть от TalkBack (для декоративных элементов)
 */
fun Modifier.decorative(): Modifier {
    return this.semantics {
        // Скрываем элемент от accessibility сервисов
    }
}

// MARK: - Accessibility Labels Constants

object AccessibilityLabels {
    
    // Buttons
    const val BACK_BUTTON = "Назад"
    const val CLOSE_BUTTON = "Закрыть"
    const val SETTINGS_BUTTON = "Настройки"
    const val NOTIFICATIONS_BUTTON = "Уведомления"
    const val ADD_BUTTON = "Добавить"
    const val DELETE_BUTTON = "Удалить"
    const val SAVE_BUTTON = "Сохранить"
    const val CANCEL_BUTTON = "Отмена"
    
    // VPN
    const val VPN_TOGGLE = "VPN переключатель"
    const val VPN_STATUS_PROTECTED = "VPN подключён, соединение защищено"
    const val VPN_STATUS_NOT_PROTECTED = "VPN отключён, соединение не защищено"
    
    // Family
    const val FAMILY_MEMBER_CARD = "Карточка члена семьи"
    const val ADD_FAMILY_MEMBER = "Добавить члена семьи"
    
    // Threats
    const val THREAT_CARD = "Карточка угрозы"
    const val THREAT_BLOCKED = "Угроза заблокирована"
    
    // Devices
    const val DEVICE_CARD = "Карточка устройства"
    const val ADD_DEVICE = "Добавить устройство"
}



