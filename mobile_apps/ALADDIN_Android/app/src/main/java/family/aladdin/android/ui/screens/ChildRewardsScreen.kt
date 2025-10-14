package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import family.aladdin.android.ui.theme.*

/// 🦄 Child Rewards Screen
/// Экран наград для детского интерфейса
/// Источник дизайна: /mobile/wireframes/14b_child_rewards_screen.html
@Composable
fun ChildRewardsScreen(onBackClick: () -> Unit = {}) {
    var selectedTab by remember { mutableStateOf(RewardTab.SHOP) }
    var unicornBalance by remember { mutableStateOf(245) }
    var weeklyEarned by remember { mutableStateOf(128) }
    var weeklyPunished by remember { mutableStateOf(45) }
    var showRequestModal by remember { mutableStateOf(false) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            // Заголовок
            ChildRewardsHeader(onBackClick = onBackClick)
            
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                // Баланс единорогов
                BalanceCard(unicornBalance, weeklyEarned, weeklyPunished)
                
                // Прогресс к цели
                GoalProgressCard(unicornBalance, 800, "Новая игра PS5")
                
                // Кнопка "Сообщить родителям"
                RequestButton(onClick = { showRequestModal = true })
                
                // Табы
                TabSelector(selectedTab, onTabSelected = { selectedTab = it })
                
                // Контент вкладок
                when (selectedTab) {
                    RewardTab.SHOP -> RewardsShop(unicornBalance) { price, _ ->
                        unicornBalance -= price
                    }
                    RewardTab.HISTORY -> RewardsHistory()
                    RewardTab.ACHIEVEMENTS -> AchievementsTab()
                }
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
        
        // Модальное окно запросов
        if (showRequestModal) {
            AchievementRequestModal(
                onSendRequest = { achievement ->
                    println("📣 Отправлен запрос: $achievement")
                    showRequestModal = false
                },
                onDismiss = { showRequestModal = false }
            )
        }
    }
}

enum class RewardTab {
    SHOP, HISTORY, ACHIEVEMENTS;
    
    fun getTitle(): String = when (this) {
        SHOP -> "🏪 Магазин"
        HISTORY -> "📊 История"
        ACHIEVEMENTS -> "🏆 Успехи"
    }
}

@Composable
private fun ChildRewardsHeader(onBackClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding, vertical = Spacing.M),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(horizontalArrangement = Arrangement.spacedBy(Spacing.M), verticalAlignment = Alignment.CenterVertically) {
            Surface(
                shape = CircleShape,
                color = BackgroundMedium.copy(alpha = 0.5f),
                onClick = onBackClick
            ) {
                Text("←", style = MaterialTheme.typography.titleLarge, modifier = Modifier.padding(10.dp))
            }
            
            Text("Мои единороги", style = MaterialTheme.typography.displayMedium, color = UnicornPurple)
        }
        
        Surface(
            shape = RoundedCornerShape(20.dp),
            color = PrimaryBlue.copy(alpha = 0.3f)
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                horizontalArrangement = Arrangement.spacedBy(Spacing.XS)
            ) {
                Text("💎", style = MaterialTheme.typography.bodyMedium)
                Text("Уровень 2", style = MaterialTheme.typography.bodySmall, color = TextPrimary)
            }
        }
    }
}

@Composable
private fun BalanceCard(balance: Int, weeklyEarned: Int, weeklyPunished: Int) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = UnicornPurple.copy(alpha = 0.15f),
        border = androidx.compose.foundation.BorderStroke(2.dp, UnicornPurple.copy(alpha = 0.4f))
    ) {
        Column(
            modifier = Modifier.padding(Spacing.L),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Text("🦄", style = MaterialTheme.typography.displayLarge.copy(fontSize = 60.sp))
            
            Text("$balance", style = MaterialTheme.typography.displayLarge.copy(fontSize = 48.sp), color = UnicornPurple)
            
            Text("Единорогов на счету", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
            
            Divider(color = TextSecondary.copy(alpha = 0.2f), modifier = Modifier.padding(vertical = Spacing.S))
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.XXL),
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("+$weeklyEarned", style = MaterialTheme.typography.displayMedium, color = SuccessGreen)
                    Text("Заработано\nза неделю", style = MaterialTheme.typography.labelSmall, color = TextSecondary, textAlign = TextAlign.Center)
                }
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("-$weeklyPunished", style = MaterialTheme.typography.displayMedium, color = DangerRed)
                    Text("Наказано\nза неделю", style = MaterialTheme.typography.labelSmall, color = TextSecondary, textAlign = TextAlign.Center)
                }
            }
        }
    }
}

@Composable
private fun GoalProgressCard(balance: Int, goal: Int, goalTitle: String) {
    val progress = balance.toFloat() / goal.toFloat()
    
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.3f)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XS)) {
                Text("🎯", style = MaterialTheme.typography.titleMedium)
                Text("Моя цель: $goalTitle", style = MaterialTheme.typography.titleMedium, color = TextPrimary)
            }
            
            // Прогресс-бар
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(20.dp)
                    .background(BackgroundMedium.copy(alpha = 0.5f), RoundedCornerShape(10.dp))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(progress)
                        .background(
                            Brush.linearGradient(listOf(UnicornPurple, UnicornPink)),
                            RoundedCornerShape(10.dp)
                        )
                )
            }
            
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text("$balance 🦄 накоплено", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                Text("Нужно: $goal 🦄", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            }
            
            Text("✅ Осталось: ${goal - balance} 🦄 (примерно 35 дней)", style = MaterialTheme.typography.labelSmall, color = SuccessGreen)
        }
    }
}

@Composable
private fun RequestButton(onClick: () -> Unit) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = UnicornPurple.copy(alpha = 0.2f),
        border = androidx.compose.foundation.BorderStroke(2.dp, UnicornPurple.copy(alpha = 0.4f)),
        onClick = onClick
    ) {
        Row(
            modifier = Modifier.padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("📣", style = MaterialTheme.typography.titleLarge)
            Text("Сообщить родителям о достижении", style = MaterialTheme.typography.titleMedium, color = TextPrimary)
        }
    }
}

@Composable
private fun TabSelector(selectedTab: RewardTab, onTabSelected: (RewardTab) -> Unit) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Row(modifier = Modifier.padding(4.dp)) {
            RewardTab.values().forEach { tab ->
                Surface(
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(CornerRadius.Medium),
                    color = if (selectedTab == tab) PrimaryBlue.copy(alpha = 0.3f) else androidx.compose.ui.graphics.Color.Transparent,
                    onClick = { onTabSelected(tab) }
                ) {
                    Text(
                        tab.getTitle(),
                        style = if (selectedTab == tab) MaterialTheme.typography.titleMedium else MaterialTheme.typography.bodyMedium,
                        color = if (selectedTab == tab) TextPrimary else TextSecondary,
                        modifier = Modifier.padding(vertical = Spacing.M),
                        textAlign = TextAlign.Center
                    )
                }
            }
        }
    }
}

@Composable
private fun RewardsShop(balance: Int, onBuy: (Int, String) -> Unit) {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.M)
    ) {
        Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XS)) {
            Text("🏪", style = MaterialTheme.typography.titleMedium)
            Text("Доступные награды:", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
        }
        
        Column(verticalArrangement = Arrangement.spacedBy(Spacing.S)) {
            RewardItem("🎮", "+30 минут игр", "Дополнительное время", 50, balance >= 50) { onBuy(50, "Игры") }
            RewardItem("📱", "+1 час экранного времени", "На любой день", 80, balance >= 80) { onBuy(80, "Экран") }
            RewardItem("🌙", "+30 минут перед сном", "Сдвинуть время сна", 100, balance >= 100) { onBuy(100, "Сон") }
            RewardItem("🍕", "Заказ пиццы", "Твоя любимая!", 150, balance >= 150) { onBuy(150, "Пицца") }
            RewardItem("🎬", "Поход в кино", "С друзьями!", 200, balance >= 200) { onBuy(200, "Кино") }
            RewardItem("🎁", "Подарок по выбору", "До 1000₽", 500, balance >= 500) { onBuy(500, "Подарок") }
        }
    }
}

@Composable
private fun RewardItem(icon: String, title: String, desc: String, price: Int, canAfford: Boolean, onClick: () -> Unit) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = canAfford) { onClick() },
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = if (canAfford) BackgroundMedium.copy(alpha = 0.5f) else BackgroundMedium.copy(alpha = 0.3f),
        border = androidx.compose.foundation.BorderStroke(
            if (canAfford) 2.dp else 1.dp,
            if (canAfford) UnicornPurple.copy(alpha = 0.4f) else TextSecondary.copy(alpha = 0.2f)
        )
    ) {
        Row(
            modifier = Modifier.padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(icon, style = MaterialTheme.typography.displaySmall)
            
            Column(modifier = Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                Text(desc, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text("$price 🦄", style = MaterialTheme.typography.titleMedium.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.Bold), color = UnicornPurple)
                
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = if (canAfford) SuccessGreen.copy(alpha = 0.2f) else DangerRed.copy(alpha = 0.2f)
                ) {
                    Text(
                        if (canAfford) "Купить!" else "Копи еще",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (canAfford) SuccessGreen else DangerRed,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun RewardsHistory() {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.M)
    ) {
        Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XS)) {
            Text("📊", style = MaterialTheme.typography.titleMedium)
            Text("История:", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
        }
        
        Column(verticalArrangement = Arrangement.spacedBy(Spacing.S)) {
            HistoryItem("🏆", "Получил '5' по математике", "+50", true, "Сегодня, 14:30")
            HistoryItem("📚", "Сделал домашнее задание", "+10", true, "Вчера, 18:00")
            HistoryItem("😡", "Плохое поведение", "-15", false, "2 дня назад, 16:00")
            HistoryItem("🧹", "Убрал в комнате", "+5", true, "3 дня назад, 10:00")
            HistoryItem("📖", "Прочитал книгу 'Гарри Поттер'", "+20", true, "4 дня назад, 20:00")
        }
    }
}

@Composable
private fun HistoryItem(icon: String, title: String, amount: String, isReward: Boolean, date: String) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = if (isReward) BackgroundMedium.copy(alpha = 0.5f) else DangerRed.copy(alpha = 0.08f),
        border = androidx.compose.foundation.BorderStroke(
            1.dp,
            if (isReward) TextSecondary.copy(alpha = 0.2f) else DangerRed.copy(alpha = 0.3f)
        )
    ) {
        Row(
            modifier = Modifier.padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(icon, style = MaterialTheme.typography.titleLarge)
            
            Column(modifier = Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                Text(date, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            }
            
            Text(amount, style = MaterialTheme.typography.titleMedium.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.Bold), color = if (isReward) SuccessGreen else DangerRed)
        }
    }
}

@Composable
private fun AchievementsTab() {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.M)
    ) {
        Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XS)) {
            Text("🏆", style = MaterialTheme.typography.titleMedium)
            Text("Мои успехи:", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
        }
        
        Column(verticalArrangement = Arrangement.spacedBy(Spacing.S)) {
            AchievementItem("📚", "Отличник", "10 заданий подряд", 0.7f)
            AchievementItem("🧹", "Помощник", "30 дней помощи", 0.5f)
            AchievementItem("📖", "Книжный червь", "Прочитай 5 книг", 0.4f)
        }
    }
}

@Composable
private fun AchievementItem(icon: String, title: String, desc: String, progress: Float) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            verticalArrangement = Arrangement.spacedBy(Spacing.S)
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.M),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(icon, style = MaterialTheme.typography.displaySmall)
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(title, style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                    Text(desc, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                }
                
                Text("${(progress * 100).toInt()}%", style = MaterialTheme.typography.bodySmall, color = SuccessGreen)
            }
            
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .background(BackgroundMedium.copy(alpha = 0.5f), RoundedCornerShape(5.dp))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(progress)
                        .background(SuccessGreen, RoundedCornerShape(5.dp))
                )
            }
        }
    }
}

@Composable
private fun AchievementRequestModal(
    onSendRequest: (String) -> Unit,
    onDismiss: () -> Unit
) {
    var selectedTemplate by remember { mutableStateOf<String?>(null) }
    var customMessage by remember { mutableStateOf("") }
    
    val templates = listOf(
        Triple("📚", "Сделал домашнее задание", "+10 🦄"),
        Triple("🧹", "Убрал в комнате", "+5 🦄"),
        Triple("📖", "Прочитал книгу", "+20 🦄"),
        Triple("🏆", "Получил '5' / закрыл четверть", "+50 🦄"),
        Triple("🏠", "Помог по дому", "+15 🦄")
    )
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            Surface(color = BackgroundMedium.copy(alpha = 0.3f), tonalElevation = 4.dp) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = Spacing.ScreenPadding, vertical = Spacing.M),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("📣 Сообщить родителям", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
                    
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Default.Close, contentDescription = "Закрыть", tint = TextSecondary)
                    }
                }
            }
            
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                Text(
                    "Выбери, о чём хочешь сообщить:",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary,
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding)
                )
                
                Column(
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
                    verticalArrangement = Arrangement.spacedBy(Spacing.S)
                ) {
                    templates.forEach { (icon, title, reward) ->
                        TemplateButton(icon, title, reward, selectedTemplate == title) {
                            selectedTemplate = title
                            customMessage = ""
                        }
                    }
                    
                    CustomMessageField(customMessage) {
                        customMessage = it
                        if (it.isNotEmpty()) selectedTemplate = null
                    }
                }
                
                if (selectedTemplate != null || customMessage.isNotEmpty()) {
                    SendButton {
                        val message = if (customMessage.isNotEmpty()) customMessage else (selectedTemplate ?: "")
                        onSendRequest(message)
                    }
                }
            }
        }
    }
}

@Composable
private fun TemplateButton(icon: String, title: String, reward: String, isSelected: Boolean, onClick: () -> Unit) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = if (isSelected) SuccessGreen.copy(alpha = 0.2f) else BackgroundMedium.copy(alpha = 0.5f),
        border = androidx.compose.foundation.BorderStroke(
            if (isSelected) 2.dp else 1.dp,
            if (isSelected) SuccessGreen else TextSecondary.copy(alpha = 0.2f)
        ),
        onClick = onClick
    ) {
        Row(
            modifier = Modifier.padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(icon, style = MaterialTheme.typography.titleLarge)
            
            Column(modifier = Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                Text(reward, style = MaterialTheme.typography.bodySmall, color = SuccessGreen)
            }
            
            if (isSelected) {
                Text("✅", style = MaterialTheme.typography.titleLarge, color = SuccessGreen)
            }
        }
    }
}

@Composable
private fun CustomMessageField(value: String, onValueChange: (String) -> Unit) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            verticalArrangement = Arrangement.spacedBy(Spacing.S)
        ) {
            Row(horizontalArrangement = Arrangement.spacedBy(Spacing.M)) {
                Text("✍️", style = MaterialTheme.typography.titleLarge)
                Text("Написать своё", style = MaterialTheme.typography.titleMedium, color = TextPrimary)
            }
            
            TextField(
                value = value,
                onValueChange = onValueChange,
                placeholder = { Text("Расскажи, что сделал...", color = TextSecondary) },
                colors = TextFieldDefaults.colors(
                    focusedContainerColor = BackgroundMedium.copy(alpha = 0.5f),
                    unfocusedContainerColor = BackgroundMedium.copy(alpha = 0.5f),
                    focusedTextColor = TextPrimary,
                    unfocusedTextColor = TextPrimary
                ),
                shape = RoundedCornerShape(CornerRadius.Small)
            )
        }
    }
}

@Composable
private fun SendButton(onClick: () -> Unit) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = SuccessGreen,
        onClick = onClick
    ) {
        Text(
            "📤 Отправить запрос",
            style = MaterialTheme.typography.titleMedium,
            color = TextPrimary,
            modifier = Modifier.padding(Spacing.M),
            textAlign = TextAlign.Center
        )
    }
}



