package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.unit.dp
import family.aladdin.android.ui.components.navigation.ALADDINTopBar
import family.aladdin.android.ui.theme.*

/// 🎮 Games Parental Control Screen
/// Панель управления геймификацией
/// Источник дизайна: /mobile/wireframes/14c_games_parental_control.html
@Composable
fun GamesParentalControlScreen(
    navController: androidx.navigation.NavHostController,
    onBackClick: () -> Unit = {}
) {
    var isWheelEnabled by remember { mutableStateOf(true) }
    var isTournamentEnabled by remember { mutableStateOf(true) }
    var isUniverseEnabled by remember { mutableStateOf(true) }
    var wheelFrequency by remember { mutableStateOf(1f) }
    var prizeSector1 by remember { mutableStateOf(5f) }
    var prizeSector2 by remember { mutableStateOf(10f) }
    var prizeSector3 by remember { mutableStateOf(20f) }
    var prizeSector4 by remember { mutableStateOf(50f) }
    var prizeSector5 by remember { mutableStateOf(100f) }
    var prizeSector6 by remember { mutableStateOf(500f) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            ALADDINTopBar(
                title = "УПРАВЛЕНИЕ ИГРАМИ",
                subtitle = "Родительский контроль",
                onBackClick = { navController.popBackStack() }
            )
            
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                // Информация
                InfoCard()
                
                // Колесо удачи
                WheelGameCard(
                    isEnabled = isWheelEnabled,
                    onToggle = { isWheelEnabled = it },
                    frequency = wheelFrequency,
                    onFrequencyChange = { wheelFrequency = it },
                    prizes = listOf(prizeSector1, prizeSector2, prizeSector3, prizeSector4, prizeSector5, prizeSector6),
                    onPrizeChange = { index, value ->
                        when (index) {
                            0 -> prizeSector1 = value
                            1 -> prizeSector2 = value
                            2 -> prizeSector3 = value
                            3 -> prizeSector4 = value
                            4 -> prizeSector5 = value
                            5 -> prizeSector6 = value
                        }
                    }
                )
                
                // Семейный турнир
                GameCard(
                    icon = "🏆",
                    title = "Семейный турнир",
                    description = "Еженедельное соревнование всей семьи. 5 типов турниров. Призы: 🥇 +50 • 🥈 +30 • 🥉 +20 🦄",
                    isEnabled = isTournamentEnabled,
                    onToggle = { isTournamentEnabled = it }
                )
                
                // Единорог-питомец (всегда ВКЛ)
                PetGameCard()
                
                // Единорог-вселенная
                GameCard(
                    icon = "🌳",
                    title = "Единорог-вселенная",
                    description = "Сад единорогов, коллекция 10 видов, сторителлинг 5 глав.",
                    isEnabled = isUniverseEnabled,
                    onToggle = { isUniverseEnabled = it }
                )
                
                // Быстрые действия
                QuickActionsSection(
                    onDisableAll = {
                        isWheelEnabled = false
                        isTournamentEnabled = false
                        isUniverseEnabled = false
                    },
                    onEnableAll = {
                        isWheelEnabled = true
                        isTournamentEnabled = true
                        isUniverseEnabled = true
                    }
                )
                
                // Текущие настройки
                CurrentSettingsCard(
                    isWheelEnabled, wheelFrequency.toInt(),
                    listOf(prizeSector1.toInt(), prizeSector2.toInt(), prizeSector3.toInt(), prizeSector4.toInt(), prizeSector5.toInt(), prizeSector6.toInt()),
                    isTournamentEnabled, isUniverseEnabled
                )
                
                // Кнопка сохранить
                SaveButton(onBackClick)
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
    }
}

@Composable
private fun InfoCard() {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = PrimaryBlue.copy(alpha = 0.15f)
    ) {
        Row(
            modifier = Modifier.padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Text("💡", style = MaterialTheme.typography.titleLarge)
            Column {
                Text("Родительский контроль игр", style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                Text("Здесь вы можете включать/отключать игровые элементы. Единорог-питомец всегда активен! 🦄", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            }
        }
    }
}

@Composable
private fun WheelGameCard(
    isEnabled: Boolean,
    onToggle: (Boolean) -> Unit,
    frequency: Float,
    onFrequencyChange: (Float) -> Unit,
    prizes: List<Float>,
    onPrizeChange: (Int, Float) -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = BackgroundMedium.copy(alpha = if (isEnabled) 0.5f else 0.3f)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Row(horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XS)) {
                    Text("🎰", style = MaterialTheme.typography.titleLarge)
                    Text("Колесо удачи", style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                }
                
                Switch(checked = isEnabled, onCheckedChange = onToggle)
            }
            
            Text("Ребёнок крутит колесо и получает случайный приз от 5 до 500 🦄.", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            
            if (isEnabled) {
                Column(verticalArrangement = Arrangement.spacedBy(Spacing.S)) {
                    Text("Частота вращений в день:", style = MaterialTheme.typography.bodySmall, color = TextPrimary)
                    
                    Slider(
                        value = frequency,
                        onValueChange = onFrequencyChange,
                        valueRange = 1f..7f,
                        steps = 5,
                        colors = SliderDefaults.colors(thumbColor = SuccessGreen, activeTrackColor = SuccessGreen)
                    )
                    
                    Row(horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("1 раз", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
                        Text("${frequency.toInt()} раз в день", style = MaterialTheme.typography.bodySmall.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.SemiBold), color = SuccessGreen)
                        Text("7 раз", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
                    }
                    
                    Text("⚙️ Настройка призов на барабане:", style = MaterialTheme.typography.bodySmall, color = TextPrimary)
                    
                    PrizeSlider(1, "40%", prizes[0], 1f..50f) { onPrizeChange(0, it) }
                    PrizeSlider(2, "30%", prizes[1], 5f..100f) { onPrizeChange(1, it) }
                    PrizeSlider(3, "15%", prizes[2], 10f..150f) { onPrizeChange(2, it) }
                    PrizeSlider(4, "10%", prizes[3], 20f..200f) { onPrizeChange(3, it) }
                    PrizeSlider(5, "4%", prizes[4], 50f..300f) { onPrizeChange(4, it) }
                    PrizeSlider(6, "1% ДЖЕКПОТ", prizes[5], 100f..1000f) { onPrizeChange(5, it) }
                }
            }
        }
    }
}

@Composable
private fun PrizeSlider(sector: Int, chance: String, value: Float, range: ClosedFloatingPointRange<Float>, onValueChange: (Float) -> Unit) {
    Column {
        Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
            Text("${sector}️⃣ Сектор $sector ($chance):", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            Text("${value.toInt()} 🦄", style = MaterialTheme.typography.bodySmall.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.Bold), color = androidx.compose.ui.graphics.Color(0xFFFFD700))
        }
        Slider(value = value, onValueChange = onValueChange, valueRange = range, colors = SliderDefaults.colors(thumbColor = androidx.compose.ui.graphics.Color(0xFFFFD700), activeTrackColor = androidx.compose.ui.graphics.Color(0xFFFFD700)))
    }
}

@Composable
private fun GameCard(icon: String, title: String, description: String, isEnabled: Boolean, onToggle: (Boolean) -> Unit) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = BackgroundMedium.copy(alpha = if (isEnabled) 0.5f else 0.3f)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Row(horizontalArrangement = Arrangement.SpaceBetween) {
                Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XS)) {
                    Text(icon, style = MaterialTheme.typography.titleLarge)
                    Text(title, style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                }
                Switch(checked = isEnabled, onCheckedChange = onToggle)
            }
            Text(description, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
        }
    }
}

@Composable
private fun PetGameCard() {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = UnicornPurple.copy(alpha = 0.1f),
        border = androidx.compose.foundation.BorderStroke(1.dp, UnicornPurple)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Row(horizontalArrangement = Arrangement.SpaceBetween) {
                Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XS)) {
                    Text("🦄", style = MaterialTheme.typography.titleLarge)
                    Text("Единорог-питомец", style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                }
                
                Text("🔒 ВСЕГДА ВКЛ", style = MaterialTheme.typography.labelSmall, color = UnicornPurple, modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp).background(UnicornPurple.copy(alpha = 0.3f), RoundedCornerShape(20.dp)))
            }
            Text("Тамагочи с индикаторами ❤️🍎⭐😊. Нельзя отключить - основа мотивации!", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
        }
    }
}

@Composable
private fun QuickActionsSection(onDisableAll: () -> Unit, onEnableAll: () -> Unit) {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.S)
    ) {
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(CornerRadius.Medium),
            color = DangerRed.copy(alpha = 0.2f),
            border = androidx.compose.foundation.BorderStroke(2.dp, DangerRed),
            onClick = onDisableAll
        ) {
            Text("Отключить все (кроме 🦄)", style = MaterialTheme.typography.titleMedium.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.SemiBold), color = DangerRed, modifier = Modifier.padding(Spacing.M))
        }
        
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(CornerRadius.Medium),
            color = SuccessGreen.copy(alpha = 0.2f),
            border = androidx.compose.foundation.BorderStroke(2.dp, SuccessGreen),
            onClick = onEnableAll
        ) {
            Text("Включить все", style = MaterialTheme.typography.titleMedium.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.SemiBold), color = SuccessGreen, modifier = Modifier.padding(Spacing.M))
        }
    }
}

@Composable
private fun CurrentSettingsCard(
    isWheelEnabled: Boolean, wheelFrequency: Int, prizes: List<Int>,
    isTournamentEnabled: Boolean, isUniverseEnabled: Boolean
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Column(modifier = Modifier.padding(Spacing.M)) {
            Text("📊 Текущие настройки:", style = MaterialTheme.typography.titleMedium, color = TextPrimary)
            Spacer(modifier = Modifier.height(Spacing.S))
            
            if (isWheelEnabled) {
                Text("• Колесо удачи: ✅ Включено ($wheelFrequency раз в день)", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
                Text("  Призы: 1️⃣${prizes[0]} • 2️⃣${prizes[1]} • 3️⃣${prizes[2]} • 4️⃣${prizes[3]} • 5️⃣${prizes[4]} • 6️⃣${prizes[5]} 🦄", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            } else {
                Text("• Колесо удачи: ❌ Отключено", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            }
            
            Text(if (isTournamentEnabled) "• Семейный турнир: ✅ Включен" else "• Семейный турнир: ❌ Отключен", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            Text("• Единорог-питомец: 🔒 Всегда включен", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            Text(if (isUniverseEnabled) "• Единорог-вселенная: ✅ Включена" else "• Единорог-вселенная: ❌ Отключена", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
        }
    }
}

@Composable
private fun SaveButton(onSave: () -> Unit) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = SuccessGreen,
        onClick = onSave
    ) {
        Text("💾 Сохранить настройки", style = MaterialTheme.typography.titleMedium.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.SemiBold), color = TextPrimary, modifier = Modifier.padding(Spacing.M))
    }
}



