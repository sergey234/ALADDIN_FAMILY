package family.aladdin.android.ui.components.cards

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import family.aladdin.android.ui.theme.*

/**
 * 📇 Function Card
 * Карточка функции для главного экрана
 * Источник: iOS FunctionCard.swift
 */

enum class StatusType(val indicator: String, val color: Color) {
    ACTIVE("🟢", SuccessGreen),
    WARNING("⚠️", WarningOrange),
    INACTIVE("🔴", DangerRed),
    NEUTRAL("✅", PrimaryBlue)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FunctionCard(
    icon: String,
    title: String,
    subtitle: String,
    status: StatusType = StatusType.NEUTRAL,
    modifier: Modifier = Modifier,
    onClick: () -> Unit = {}
) {
    Card(
        onClick = onClick,
        modifier = modifier
            .fillMaxWidth()
            .height(Size.FunctionCardHeight),
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
                .fillMaxSize()
                .background(
                    brush = Brush.linearGradient(
                        colors = listOf(
                            GradientMiddle.copy(alpha = 0.7f),
                            GradientEnd.copy(alpha = 0.7f)
                        )
                    )
                )
                .padding(Spacing.CardPadding),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(Spacing.M)
            ) {
                // Иконка
                Text(
                    text = icon,
                    style = MaterialTheme.typography.displayLarge
                )
                
                // Текст
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(Spacing.XXS)
                ) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.displaySmall,
                        color = TextPrimary,
                        textAlign = TextAlign.Center
                    )
                    
                    Text(
                        text = subtitle,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                        textAlign = TextAlign.Center
                    )
                }
                
                // Индикатор статуса
                Row(
                    horizontalArrangement = Arrangement.spacedBy(Spacing.XXS),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(Size.StatusIndicator)
                            .background(status.color, CircleShape)
                    )
                    
                    Text(
                        text = status.indicator,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }
    }
}



