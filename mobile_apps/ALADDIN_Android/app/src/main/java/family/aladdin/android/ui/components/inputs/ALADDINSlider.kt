package family.aladdin.android.ui.components.inputs

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import family.aladdin.android.ui.theme.*

/**
 * 🎚️ ALADDIN Slider
 * Кастомный ползунок
 * Источник: iOS ALADDINSlider.swift
 */

@Composable
fun ALADDINSlider(
    title: String,
    value: Float,
    onValueChange: (Float) -> Unit,
    valueRange: ClosedFloatingPointRange<Float> = 0f..100f,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    icon: String? = null,
    unit: String = "",
    showValue: Boolean = true
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.3f)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.M),
            verticalArrangement = Arrangement.spacedBy(Spacing.S)
        ) {
            // Заголовок
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.M),
                verticalAlignment = androidx.compose.ui.Alignment.CenterVertically
            ) {
                icon?.let {
                    Text(
                        text = it,
                        style = MaterialTheme.typography.displayMedium
                    )
                }
                
                Column(modifier = Modifier.weight(1f)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = title,
                            style = MaterialTheme.typography.bodyLarge,
                            color = TextPrimary
                        )
                        
                        if (showValue) {
                            Text(
                                text = "${value.toInt()}$unit",
                                style = MaterialTheme.typography.bodyMedium,
                                color = PrimaryBlue
                            )
                        }
                    }
                    
                    subtitle?.let {
                        Text(
                            text = it,
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary
                        )
                    }
                }
            }
            
            // Ползунок
            Slider(
                value = value,
                onValueChange = onValueChange,
                valueRange = valueRange,
                colors = SliderDefaults.colors(
                    thumbColor = Color.White,
                    activeTrackColor = PrimaryBlue,
                    inactiveTrackColor = BackgroundMedium
                )
            )
            
            // Метки диапазона
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "${valueRange.start.toInt()}$unit",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary
                )
                Text(
                    text = "${valueRange.endInclusive.toInt()}$unit",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary
                )
            }
        }
    }
}




