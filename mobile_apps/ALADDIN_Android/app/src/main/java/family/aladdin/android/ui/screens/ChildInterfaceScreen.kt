package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.theme.*

@Composable
fun ChildInterfaceScreen(navController: NavHostController) {
    // TODO: Use navController for navigation
    var selectedAge by remember { mutableStateOf(AgeGroup.SCHOOL) }
    var showChildRewards by remember { mutableStateOf(false) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.linearGradient(
                    listOf(
                        Color(0xFF1e3a8a),
                        Color(0xFF3b82f6),
                        Color(0xFF60a5fa)
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier
                .verticalScroll(rememberScrollState())
                .padding(Spacing.L),
            verticalArrangement = Arrangement.spacedBy(Spacing.XL)
        ) {
            // Приветствие
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.fillMaxWidth()
            ) {
                // Аватар (НОВОЕ: клик открывает награды)
                Surface(
                    shape = androidx.compose.foundation.shape.CircleShape,
                    onClick = { showChildRewards = true }
                ) {
                    Text("👧", style = MaterialTheme.typography.displayLarge.copy(fontSize = MaterialTheme.typography.displayLarge.fontSize * 2f))
                }
                
                Text("Привет, Маша!", style = MaterialTheme.typography.displayLarge, color = Color.White)
                Text("Ты под защитой 🛡️", style = MaterialTheme.typography.bodyLarge, color = Color.White.copy(alpha = 0.8f))
            }
            
            // НОВОЕ: Возрастные табы
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("🎯 Выбери свой возраст", style = MaterialTheme.typography.displaySmall, color = Color.White)
                Spacer(modifier = Modifier.height(Spacing.M))
                
                Row(
                    horizontalArrangement = Arrangement.spacedBy(Spacing.S),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    listOf(AgeGroup.KIDS, AgeGroup.SCHOOL, AgeGroup.TEEN).forEach { age ->
                        Surface(
                            onClick = { selectedAge = age },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(CornerRadius.Medium),
                            color = if (selectedAge == age) PrimaryBlue else Color.White.copy(alpha = 0.1f)
                        ) {
                            Text(
                                age.getTitle(),
                                style = if (selectedAge == age) MaterialTheme.typography.bodyMedium.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.Bold) else MaterialTheme.typography.bodySmall,
                                color = if (selectedAge == age) Color.White else Color.White.copy(alpha = 0.7f),
                                modifier = Modifier.padding(horizontal = Spacing.M, vertical = Spacing.S),
                                textAlign = androidx.compose.ui.text.style.TextAlign.Center
                            )
                        }
                    }
                }
            }
            
            // Большие кнопки
            Column(verticalArrangement = Arrangement.spacedBy(Spacing.M)) {
                Row(horizontalArrangement = Arrangement.spacedBy(Spacing.M)) {
                    BigChildButton("🎮", "ИГРЫ", SuccessGreen, Modifier.weight(1f))
                    BigChildButton("📚", "УЧЁБА", PrimaryBlue, Modifier.weight(1f))
                }
                Row(horizontalArrangement = Arrangement.spacedBy(Spacing.M)) {
                    BigChildButton("🎨", "ТВОРЧЕСТВО", WarningOrange, Modifier.weight(1f))
                    BigChildButton("📺", "ВИДЕО", DangerRed, Modifier.weight(1f))
                }
            }
        }
        
        // Модальное окно наград
        if (showChildRewards) {
            ChildRewardsScreen(onBackClick = { showChildRewards = false })
        }
    }
}

enum class AgeGroup {
    KIDS, SCHOOL, TEEN;
    
    fun getTitle(): String = when (this) {
        KIDS -> "👶 1-6 лет"
        SCHOOL -> "🎒 7-12 лет"
        TEEN -> "🎓 13-17 лет"
    }
}

@Composable
private fun BigChildButton(icon: String, title: String, color: Color, modifier: Modifier) {
    Surface(
        onClick = {},
        modifier = modifier.height(140.dp),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = color.copy(alpha = 0.3f)
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .border(3.dp, color, RoundedCornerShape(CornerRadius.Large)),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(icon, style = MaterialTheme.typography.displayLarge.copy(fontSize = MaterialTheme.typography.displayLarge.fontSize * 1.5f))
                Text(title, style = MaterialTheme.typography.displaySmall, color = Color.White)
            }
        }
    }
}

