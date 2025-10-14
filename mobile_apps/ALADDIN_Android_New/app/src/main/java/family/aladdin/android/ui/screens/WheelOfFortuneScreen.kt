package family.aladdin.android.ui.screens

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import kotlinx.coroutines.launch
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.unit.dp
import family.aladdin.android.ui.theme.*
import kotlin.random.Random

/// 🎰 Wheel of Fortune Screen
/// Колесо удачи с анимацией вращения
/// Источник дизайна: /mobile/wireframes/wheel_of_fortune_component.html
@Composable
fun WheelOfFortuneScreen() {
    var rotation by remember { mutableStateOf(0f) }
    var isSpinning by remember { mutableStateOf(false) }
    var wonPrize by remember { mutableStateOf(0) }
    var showPrizeDialog by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    var canSpin by remember { mutableStateOf(true) }
    var timeUntilNextSpin by remember { mutableStateOf(0) }
    var totalSpins by remember { mutableStateOf(0) }
    var totalWon by remember { mutableStateOf(0) }
    
    val prizes = listOf(5, 10, 20, 50, 100, 500)
    val probabilities = listOf(0.4, 0.3, 0.15, 0.1, 0.04, 0.01)
    
    val animatedRotation = remember { Animatable(0f) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(Spacing.L),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(Spacing.L)
        ) {
            // Заголовок
            Text("🎰 КОЛЕСО УДАЧИ", style = MaterialTheme.typography.displayLarge, color = TextPrimary)
            
            // Колесо
            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier.size(280.dp)
            ) {
                // Колесо
                Surface(
                    modifier = Modifier
                        .size(280.dp)
                        .rotate(animatedRotation.value),
                    shape = CircleShape,
                    color = UnicornPurple
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        // Упрощённое отображение секторов текстом
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            prizes.forEachIndexed { index, prize ->
                                Text("${index + 1}️⃣ $prize 🦄", style = MaterialTheme.typography.bodyMedium, color = androidx.compose.ui.graphics.Color.White)
                            }
                        }
                    }
                }
                
                // Центр
                Surface(
                    modifier = Modifier.size(60.dp),
                    shape = CircleShape,
                    color = GradientStart
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text("🦄", style = MaterialTheme.typography.displayMedium)
                    }
                }
                
                // Указатель
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(top = 20.dp),
                    contentAlignment = Alignment.TopCenter
                ) {
                    Text("🔻", style = MaterialTheme.typography.displaySmall, color = DangerRed)
                }
            }
            
            // Кнопка вращения
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(CornerRadius.XLarge),
                color = if (canSpin) SuccessGreen else TextSecondary,
                onClick = {
                    if (canSpin && !isSpinning) {
                        isSpinning = true
                        canSpin = false
                        
                        // Weighted random
                        val random = Random.nextDouble()
                        var cumulative = 0.0
                        var selectedIndex = 0
                        
                        probabilities.forEachIndexed { index, prob ->
                            cumulative += prob
                            if (random <= cumulative && selectedIndex == 0) {
                                selectedIndex = index
                            }
                        }
                        
                        wonPrize = prizes[selectedIndex]
                        
                        // Анимация
                        val targetRotation = rotation + (360 * 5) + (60 * selectedIndex)
                        
                        scope.launch {
                            animatedRotation.animateTo(
                                targetValue = targetRotation,
                                animationSpec = tween(durationMillis = 3000, easing = FastOutSlowInEasing)
                            )
                            
                            kotlinx.coroutines.delay(100)
                            isSpinning = false
                            totalSpins++
                            totalWon += wonPrize
                            showPrizeDialog = true
                            timeUntilNextSpin = 24
                        }
                    }
                }
            ) {
                Text(
                    if (canSpin) "🎰 КРУТИТЬ!" else "⏰ Подожди...",
                    style = MaterialTheme.typography.displayMedium.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.Bold),
                    color = TextPrimary,
                    modifier = Modifier.padding(Spacing.L)
                )
            }
            
            // Таймер
            if (!canSpin) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(CornerRadius.Medium),
                    color = BackgroundMedium.copy(alpha = 0.5f)
                ) {
                    Column(
                        modifier = Modifier.padding(Spacing.M),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text("⏰ Следующее вращение через:", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                        Text("$timeUntilNextSpin ч", style = MaterialTheme.typography.displayMedium, color = PrimaryBlue)
                    }
                }
            }
            
            // Статистика
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.XL),
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("$totalSpins", style = MaterialTheme.typography.displayMedium, color = PrimaryBlue)
                    Text("Вращений", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                }
                
                Box(modifier = Modifier.width(1.dp).height(40.dp).background(TextSecondary.copy(alpha = 0.3f)))
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("$totalWon 🦄", style = MaterialTheme.typography.displayMedium, color = SuccessGreen)
                    Text("Выиграно", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                }
            }
        }
        
        // Диалог приза
        if (showPrizeDialog) {
            AlertDialog(
                onDismissRequest = { showPrizeDialog = false },
                title = { Text("🎉 ПРИЗ!") },
                text = { Text("Ты выиграл $wonPrize 🦄!") },
                confirmButton = {
                    Button(onClick = { showPrizeDialog = false }) {
                        Text("OK")
                    }
                }
            )
        }
    }
}



