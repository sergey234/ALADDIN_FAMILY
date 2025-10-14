package family.aladdin.android.ui.components.cards

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import family.aladdin.android.ui.theme.*

/**
 * 📇 Status Card
 * Карточка со статусом
 * Источник: iOS StatusCard.swift
 */

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StatusCard(
    title: String,
    subtitle: String,
    icon: String,
    statusColor: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit = {}
) {
    Card(
        onClick = onClick,
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Large),
        colors = CardDefaults.cardColors(
            containerColor = Color.Transparent
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 4.dp
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    brush = Brush.linearGradient(
                        colors = listOf(
                            GradientMiddle.copy(alpha = 0.7f),
                            GradientEnd.copy(alpha = 0.7f)
                        )
                    )
                )
                .padding(Spacing.CardPadding)
        ) {
            Column(
                verticalArrangement = Arrangement.spacedBy(Spacing.S)
            ) {
                // Иконка и заголовок
                Row(
                    horizontalArrangement = Arrangement.spacedBy(Spacing.S),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = icon,
                        style = MaterialTheme.typography.displayMedium
                    )
                    Text(
                        text = title,
                        style = MaterialTheme.typography.displaySmall,
                        color = TextPrimary
                    )
                }
                
                // Подзаголовок
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
                
                // Индикатор статуса
                Box(
                    modifier = Modifier
                        .size(Size.StatusIndicator)
                        .background(statusColor, CircleShape)
                )
            }
        }
    }
}



