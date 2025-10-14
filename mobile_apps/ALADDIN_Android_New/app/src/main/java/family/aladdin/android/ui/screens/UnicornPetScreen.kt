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
import androidx.compose.ui.unit.sp
import family.aladdin.android.ui.theme.*

@Composable
fun UnicornPetScreen() {
    var love by remember { mutableStateOf(0.75f) }
    var hunger by remember { mutableStateOf(0.6f) }
    var energy by remember { mutableStateOf(0.8f) }
    var mood by remember { mutableStateOf(0.7f) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column(
            modifier = Modifier
                .verticalScroll(rememberScrollState())
                .padding(Spacing.L),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(Spacing.L)
        ) {
            Text("🦄 МОЙ ПИТОМЕЦ", style = MaterialTheme.typography.displayLarge, color = TextPrimary)
            
            // Питомец
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(CornerRadius.XLarge),
                color = BackgroundMedium.copy(alpha = 0.5f)
            ) {
                Column(
                    modifier = Modifier.padding(Spacing.L),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("🦄", style = MaterialTheme.typography.displayLarge.copy(fontSize = 100.sp))
                    Text("Уровень 2", style = MaterialTheme.typography.displayMedium, color = PrimaryBlue)
                    Text("Стадия: Teen", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                }
            }
            
            // Индикаторы
            Column(verticalArrangement = Arrangement.spacedBy(Spacing.S), modifier = Modifier.fillMaxWidth()) {
                IndicatorRow("❤️", "Любовь", love, DangerRed)
                IndicatorRow("🍎", "Сытость", hunger, SuccessGreen)
                IndicatorRow("⭐", "Энергия", energy, WarningOrange)
                IndicatorRow("😊", "Настроение", mood, PrimaryBlue)
            }
            
            // Действия
            Row(horizontalArrangement = Arrangement.spacedBy(Spacing.M), modifier = Modifier.fillMaxWidth()) {
                ActionButton("🍎", "Покормить", "10 🦄", Modifier.weight(1f)) { hunger = (hunger + 0.2f).coerceAtMost(1f) }
                ActionButton("🎮", "Поиграть", "5 🦄", Modifier.weight(1f)) { energy = (energy + 0.15f).coerceAtMost(1f) }
                ActionButton("💕", "Погладить", "FREE", Modifier.weight(1f)) { love = (love + 0.1f).coerceAtMost(1f) }
            }
        }
    }
}

@Composable
private fun IndicatorRow(icon: String, label: String, value: Float, color: androidx.compose.ui.graphics.Color) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(Spacing.M),
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier.fillMaxWidth()
    ) {
        Text(icon, style = MaterialTheme.typography.titleLarge)
        Text(label, style = MaterialTheme.typography.titleMedium, color = TextPrimary, modifier = Modifier.width(100.dp))
        
        Box(
            modifier = Modifier
                .weight(1f)
                .height(10.dp)
                .background(BackgroundMedium.copy(alpha = 0.5f), RoundedCornerShape(5.dp))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(value)
                    .background(color, RoundedCornerShape(5.dp))
            )
        }
        
        Text("${(value * 100).toInt()}%", style = MaterialTheme.typography.bodySmall, color = TextSecondary, modifier = Modifier.width(40.dp))
    }
}

@Composable
private fun ActionButton(icon: String, title: String, cost: String, modifier: Modifier, onClick: () -> Unit) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.5f),
        onClick = onClick
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(icon, style = MaterialTheme.typography.displaySmall)
            Text(title, style = MaterialTheme.typography.bodySmall, color = TextPrimary)
            Text(cost, style = MaterialTheme.typography.labelSmall, color = SuccessGreen)
        }
    }
}



