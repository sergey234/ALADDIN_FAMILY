package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.inputs.ALADDINToggle
import family.aladdin.android.ui.components.inputs.ALADDINSlider
import family.aladdin.android.ui.components.navigation.ALADDINTopBar
import family.aladdin.android.ui.theme.*

@Composable
fun ParentalControlScreen(navController: NavHostController) {
    var isContentFilterEnabled by remember { mutableStateOf(true) }
    var screenTimeLimit by remember { mutableStateOf(3f) }
    
    // НОВОЕ: Вознаграждения с единорогами 🦄
    var showRewardsModal by remember { mutableStateOf(false) }
    var unicornBalance by remember { mutableStateOf(245) }
    var weeklyRewarded by remember { mutableStateOf(128) }
    var weeklyPunished by remember { mutableStateOf(45) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            ALADDINTopBar(
                title = "РОДИТЕЛЬСКИЙ КОНТРОЛЬ",
                subtitle = "Управление для детей",
                onBackClick = { navController.popBackStack() }
            )
            
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                // Выбор ребёнка
                ChildSelector()
                
                // Статистика
                ChildStats()
                
                // Фильтр контента
                Column(
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
                    verticalArrangement = Arrangement.spacedBy(Spacing.S)
                ) {
                    Text("🛡️ ФИЛЬТР КОНТЕНТА", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
                    
                    ALADDINToggle(
                        title = "Блокировка опасного контента",
                        isChecked = isContentFilterEnabled,
                        onCheckedChange = { isContentFilterEnabled = it },
                        subtitle = "Автоматическая блокировка",
                        icon = "🚫"
                    )
                }
                
                // Лимит времени
                Column(
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
                    verticalArrangement = Arrangement.spacedBy(Spacing.S)
                ) {
                    Text("⏰ ЛИМИТ ВРЕМЕНИ", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
                    
                    ALADDINSlider(
                        title = "Дневной лимит",
                        value = screenTimeLimit,
                        onValueChange = { screenTimeLimit = it },
                        valueRange = 1f..12f,
                        icon = "⏱️",
                        unit = " ч"
                    )
                }
                
                // НОВОЕ: Вознаграждение ребёнка 🦄
                RewardsSection(
                    unicornBalance = unicornBalance,
                    weeklyRewarded = weeklyRewarded,
                    weeklyPunished = weeklyPunished,
                    onClick = { showRewardsModal = true }
                )
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
        
        // Модальное окно вознаграждений
        if (showRewardsModal) {
            RewardsModalView(
                unicornBalance = unicornBalance,
                weeklyRewarded = weeklyRewarded,
                weeklyPunished = weeklyPunished,
                onReward = {
                    unicornBalance += 10
                    weeklyRewarded += 10
                },
                onPunish = {
                    unicornBalance -= 10
                    weeklyPunished += 10
                },
                onDismiss = {
                    showRewardsModal = false
                }
            )
        }
    }
}

@Composable
private fun ChildSelector() {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = BackgroundMedium.copy(alpha = 0.5f),
        onClick = {}
    ) {
        Row(
            modifier = Modifier.padding(Spacing.CardPadding),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(60.dp)
                    .background(PrimaryBlue.copy(alpha = 0.3f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text("👧", style = MaterialTheme.typography.displayLarge)
            }
            
            Column(modifier = Modifier.weight(1f)) {
                Text("Маша", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
                Text("Ребёнок • 10 лет", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            }
            
            Text("›", style = MaterialTheme.typography.displaySmall, color = TextSecondary)
        }
    }
}

@Composable
private fun ChildStats() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        horizontalArrangement = Arrangement.spacedBy(Spacing.M)
    ) {
        StatBox("⏰", "2:45", "Сегодня\nна экране", SuccessGreen, Modifier.weight(1f))
        StatBox("🚫", "12", "Заблокиров.\nсайтов", DangerRed, Modifier.weight(1f))
        StatBox("📱", "8", "Доступных\nприложений", PrimaryBlue, Modifier.weight(1f))
    }
}

@Composable
private fun StatBox(icon: String, value: String, label: String, color: androidx.compose.ui.graphics.Color, modifier: Modifier) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.3f)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(icon, style = MaterialTheme.typography.displayMedium)
            Text(value, style = MaterialTheme.typography.displayMedium, color = color)
            Text(label, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
        }
    }
}

// НОВОЕ: Раздел вознаграждений 🦄
@Composable
private fun RewardsSection(
    unicornBalance: Int,
    weeklyRewarded: Int,
    weeklyPunished: Int,
    onClick: () -> Unit
) {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.S)
    ) {
        Row(
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("🦄 ВОЗНАГРАЖДЕНИЕ РЕБЁНКА", style = MaterialTheme.typography.displaySmall, color = UnicornPurple)
            
            Surface(
                shape = RoundedCornerShape(20.dp),
                color = UnicornPurple.copy(alpha = 0.2f),
                border = androidx.compose.foundation.BorderStroke(1.dp, UnicornPurple)
            ) {
                Text(
                    "$unicornBalance 🦄",
                    style = MaterialTheme.typography.bodySmall,
                    color = UnicornPurple,
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp)
                )
            }
        }
        
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(CornerRadius.Large),
            color = BackgroundMedium.copy(alpha = 0.3f),
            onClick = onClick
        ) {
            Column(
                modifier = Modifier.padding(Spacing.CardPadding),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(Spacing.M)
            ) {
                Text("🦄", style = MaterialTheme.typography.displayLarge)
                
                Row(
                    horizontalArrangement = Arrangement.spacedBy(Spacing.XS),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("💰", style = MaterialTheme.typography.titleMedium)
                    Text("$unicornBalance единорогов", style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                }
                
                Row(
                    horizontalArrangement = Arrangement.spacedBy(Spacing.L),
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("+$weeklyRewarded", style = MaterialTheme.typography.displaySmall, color = SuccessGreen)
                        Text("Вознаграждено", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                    }
                    
                    Box(
                        modifier = Modifier
                            .width(1.dp)
                            .height(30.dp)
                            .background(TextSecondary.copy(alpha = 0.3f))
                    )
                    
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("-$weeklyPunished", style = MaterialTheme.typography.displaySmall, color = DangerRed)
                        Text("Наказано", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                    }
                }
            }
        }
    }
}

