package family.aladdin.android.ui.components.inputs

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import family.aladdin.android.ui.theme.*

/**
 * 🔘 ALADDIN Toggle
 * Кастомный переключатель
 * Источник: iOS ALADDINToggle.swift
 */

@Composable
fun ALADDINToggle(
    title: String,
    isChecked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    icon: String? = null,
    enabled: Boolean = true
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.3f)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Иконка
            icon?.let {
                Text(
                    text = it,
                    style = MaterialTheme.typography.displayMedium
                )
            }
            
            // Текст
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(Spacing.XXS)
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyLarge,
                    color = if (enabled) TextPrimary else TextSecondary
                )
                
                subtitle?.let {
                    Text(
                        text = it,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }
            }
            
            // Переключатель
            Switch(
                checked = isChecked,
                onCheckedChange = onCheckedChange,
                enabled = enabled,
                colors = SwitchDefaults.colors(
                    checkedThumbColor = Color.White,
                    checkedTrackColor = PrimaryBlue,
                    uncheckedThumbColor = Color.White,
                    uncheckedTrackColor = BackgroundMedium
                )
            )
        }
    }
}




