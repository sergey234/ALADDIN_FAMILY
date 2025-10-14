package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Divider
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import family.aladdin.android.ui.theme.*

/// 🦄 Rewards Modal View
/// Модальное окно управления вознаграждениями ребёнка
/// Источник дизайна: /mobile/wireframes/14_parental_control_screen.html (модальное окно)
@Composable
fun RewardsModalView(
    unicornBalance: Int,
    weeklyRewarded: Int,
    weeklyPunished: Int,
    onReward: () -> Unit,
    onPunish: () -> Unit,
    onDismiss: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            // Заголовок с кнопкой закрытия
            Surface(
                color = BackgroundMedium.copy(alpha = 0.3f),
                tonalElevation = 4.dp
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = Spacing.ScreenPadding, vertical = Spacing.M),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(Spacing.XS),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("🦄", style = MaterialTheme.typography.titleLarge)
                        Text("Вознаграждение ребёнка", style = MaterialTheme.typography.displaySmall, color = UnicornPurple)
                    }
                    
                    IconButton(onClick = onDismiss) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Закрыть",
                            tint = TextSecondary
                        )
                    }
                }
            }
            
            // Основной контент
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                // Баланс единорогов
                BalanceCard(unicornBalance, weeklyRewarded, weeklyPunished)
                
                // Быстрые действия
                QuickActions(onReward, onPunish)
                
                // Как заработать
                EarningWaysSection()
                
                // За что можно наказать
                PunishmentReasonsSection()
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
    }
}

@Composable
private fun BalanceCard(
    unicornBalance: Int,
    weeklyRewarded: Int,
    weeklyPunished: Int
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = UnicornPurple.copy(alpha = 0.12f),
        border = androidx.compose.foundation.BorderStroke(2.dp, UnicornPurple.copy(alpha = 0.4f))
    ) {
        Column(
            modifier = Modifier.padding(Spacing.L),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            // Иконка
            Text("🦄", style = MaterialTheme.typography.displayLarge.copy(fontSize = 56.sp))
            
            // Баланс
            Text(
                "$unicornBalance",
                style = MaterialTheme.typography.displayLarge.copy(fontSize = 36.sp),
                color = UnicornPurple
            )
            Text("Единорогов на счету", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
            
            // Разделитель
                    Divider(
                modifier = Modifier.padding(vertical = Spacing.S),
                color = TextSecondary.copy(alpha = 0.3f)
            )
            
            // Статистика за неделю
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.XXL),
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("+$weeklyRewarded", style = MaterialTheme.typography.displayMedium, color = SuccessGreen)
                    Text("Вознаграждено\nза неделю", style = MaterialTheme.typography.labelSmall, color = TextSecondary, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                }
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("-$weeklyPunished", style = MaterialTheme.typography.displayMedium, color = DangerRed)
                    Text("Наказано\nза неделю", style = MaterialTheme.typography.labelSmall, color = TextSecondary, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                }
            }
        }
    }
}

@Composable
private fun QuickActions(onReward: () -> Unit, onPunish: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        horizontalArrangement = Arrangement.spacedBy(Spacing.M)
    ) {
        // Кнопка "Вознаградить"
        Surface(
            modifier = Modifier.weight(1f),
            shape = RoundedCornerShape(CornerRadius.Medium),
            color = SuccessGreen.copy(alpha = 0.2f),
            border = androidx.compose.foundation.BorderStroke(2.dp, SuccessGreen),
            onClick = onReward
        ) {
            Column(
                modifier = Modifier.padding(Spacing.M),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(Spacing.XS)
            ) {
                Text("✅", style = MaterialTheme.typography.titleLarge)
                Text("Вознаградить", style = MaterialTheme.typography.bodySmall, color = SuccessGreen)
            }
        }
        
        // Кнопка "Наказать"
        Surface(
            modifier = Modifier.weight(1f),
            shape = RoundedCornerShape(CornerRadius.Medium),
            color = DangerRed.copy(alpha = 0.2f),
            border = androidx.compose.foundation.BorderStroke(2.dp, DangerRed),
            onClick = onPunish
        ) {
            Column(
                modifier = Modifier.padding(Spacing.M),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(Spacing.XS)
            ) {
                Text("❌", style = MaterialTheme.typography.titleLarge)
                Text("Наказать", style = MaterialTheme.typography.bodySmall, color = DangerRed)
            }
        }
    }
}

@Composable
private fun EarningWaysSection() {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = BackgroundMedium.copy(alpha = 0.3f)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.XS),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("✅", style = MaterialTheme.typography.titleMedium)
                Text("Как заработать:", style = MaterialTheme.typography.displaySmall, color = SuccessGreen)
            }
            
            Column(verticalArrangement = Arrangement.spacedBy(Spacing.S)) {
                EarningWayRow("📚", "Домашнее задание", "+10 единорогов за задание", "+10 🦄")
                EarningWayRow("🧹", "Домашние обязанности", "+5 единорогов за дело", "+5 🦄")
                EarningWayRow("😊", "Хорошее поведение", "+15 единорогов за день", "+15 🦄")
                EarningWayRow("📖", "Чтение книг", "+20 единорогов за книгу", "+20 🦄")
                EarningWayRow("🏆", "Достижения в учёбе", "+50 единорогов за 5", "+50 🦄")
            }
        }
    }
}

@Composable
private fun EarningWayRow(icon: String, title: String, subtitle: String, amount: String) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Row(
            modifier = Modifier.padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(icon, style = MaterialTheme.typography.titleLarge)
            
            Column(modifier = Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                Text(subtitle, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            }
            
            Text(amount, style = MaterialTheme.typography.titleMedium.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.Bold), color = SuccessGreen)
        }
    }
}

@Composable
private fun PunishmentReasonsSection() {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = DangerRed.copy(alpha = 0.08f),
        border = androidx.compose.foundation.BorderStroke(1.dp, DangerRed.copy(alpha = 0.3f))
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.XS),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("❌", style = MaterialTheme.typography.titleMedium)
                Text("За что можно наказать:", style = MaterialTheme.typography.displaySmall, color = DangerRed)
            }
            
            Column(verticalArrangement = Arrangement.spacedBy(Spacing.S)) {
                PunishmentReasonRow("📚", "Не сделал ДЗ", "Забыл или отказался делать", "-10 🦄")
                PunishmentReasonRow("😡", "Плохое поведение", "Грубость, ссоры, непослушание", "-15 🦄")
                PunishmentReasonRow("⏰", "Нарушение лимитов", "Превышение экранного времени", "-5 🦄")
                PunishmentReasonRow("🚫", "Обход блокировок", "Попытка обойти контроль", "-20 🦄")
                PunishmentReasonRow("😤", "Своя причина", "Родители указывают сами", "-1 до -50 🦄")
            }
        }
    }
}

@Composable
private fun PunishmentReasonRow(icon: String, title: String, subtitle: String, amount: String) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Row(
            modifier = Modifier.padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(icon, style = MaterialTheme.typography.titleLarge)
            
            Column(modifier = Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                Text(subtitle, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            }
            
            Text(amount, style = MaterialTheme.typography.titleMedium.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.Bold), color = DangerRed)
        }
    }
}



