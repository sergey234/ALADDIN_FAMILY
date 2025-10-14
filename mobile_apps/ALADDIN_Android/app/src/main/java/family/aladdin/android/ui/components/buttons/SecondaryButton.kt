package family.aladdin.android.ui.components.buttons

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import family.aladdin.android.ui.theme.*

/**
 * 🔘 Secondary Button
 * Вторичная кнопка ALADDIN (обводка)
 * Источник: iOS SecondaryButton.swift
 */

@Composable
fun SecondaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: String? = null,
    enabled: Boolean = true
) {
    OutlinedButton(
        onClick = onClick,
        modifier = modifier
            .fillMaxWidth()
            .height(Size.ButtonHeight),
        enabled = enabled,
        colors = ButtonDefaults.outlinedButtonColors(
            contentColor = if (enabled) PrimaryBlue else TextSecondary,
            disabledContentColor = TextSecondary
        ),
        border = BorderStroke(
            width = 2.dp,
            color = if (enabled) PrimaryBlue else TextSecondary
        ),
        shape = RoundedCornerShape(CornerRadius.Medium)
    ) {
        Row(
            horizontalArrangement = Arrangement.Center,
            modifier = Modifier.fillMaxWidth()
        ) {
            icon?.let {
                Text(
                    text = it,
                    modifier = Modifier.padding(end = Spacing.XS)
                )
            }
            Text(
                text = text,
                style = MaterialTheme.typography.labelLarge
            )
        }
    }
}



