package family.aladdin.android.ui.components.cards

import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.ui.unit.dp
import family.aladdin.android.ui.theme.*

/**
 * 👤 Family Member Card
 * Карточка члена семьи
 * Источник: iOS FamilyMemberCard.swift
 */

enum class FamilyRole(val label: String, val icon: String) {
    PARENT("Родитель", "👨‍💼"),
    CHILD("Ребёнок", "👶"),
    TEENAGER("Подросток", "🧒"),
    ELDERLY("Пожилой", "👴")
}

enum class ProtectionStatus(val label: String, val color: Color, val indicator: String) {
    PROTECTED("Защищён", SuccessGreen, "🟢"),
    WARNING("Внимание", WarningOrange, "⚠️"),
    DANGER("Угроза", DangerRed, "🔴"),
    OFFLINE("Оффлайн", TextSecondary, "⚫")
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FamilyMemberCard(
    name: String,
    role: FamilyRole,
    avatar: String,
    status: ProtectionStatus,
    threatsBlocked: Int,
    lastActive: String = "Сейчас",
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
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.M),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Аватар с обводкой по статусу
                Box(
                    modifier = Modifier
                        .size(Size.AvatarSize)
                        .background(
                            brush = Brush.linearGradient(
                                colors = listOf(
                                    PrimaryBlue.copy(alpha = 0.3f),
                                    PrimaryBlue.copy(alpha = 0.1f)
                                )
                            ),
                            shape = CircleShape
                        )
                        .border(3.dp, status.color, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = avatar,
                        style = MaterialTheme.typography.displayMedium
                    )
                }
                
                // Информация
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(Spacing.XS)
                ) {
                    // Имя и роль
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(Spacing.XS)
                    ) {
                        Text(
                            text = name,
                            style = MaterialTheme.typography.displaySmall,
                            color = TextPrimary
                        )
                        Text(
                            text = role.icon,
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                    
                    // Роль
                    Text(
                        text = role.label,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                    
                    // Статистика
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(Spacing.M)
                    ) {
                        Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XXS)) {
                            Text(text = "🛡️", style = MaterialTheme.typography.bodySmall)
                            Text(
                                text = "$threatsBlocked",
                                style = MaterialTheme.typography.bodyMedium,
                                color = SuccessGreen
                            )
                        }
                        
                        Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XXS)) {
                            Text(text = "⏰", style = MaterialTheme.typography.bodySmall)
                            Text(
                                text = lastActive,
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary
                            )
                        }
                    }
                }
                
                // Статус
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(Spacing.XS)
                ) {
                    Text(
                        text = status.indicator,
                        style = MaterialTheme.typography.displayMedium
                    )
                    Text(
                        text = status.label,
                        style = MaterialTheme.typography.labelSmall,
                        color = status.color
                    )
                }
            }
        }
    }
}



