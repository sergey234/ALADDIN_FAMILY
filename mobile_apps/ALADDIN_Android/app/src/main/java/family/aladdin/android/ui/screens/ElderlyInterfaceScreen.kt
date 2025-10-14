package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.theme.*

@Composable
fun ElderlyInterfaceScreen(navController: NavHostController) {
    // TODO: Use navController for navigation
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column(
            modifier = Modifier
                .verticalScroll(rememberScrollState())
                .padding(Spacing.L),
            verticalArrangement = Arrangement.spacedBy(Spacing.XL)
        ) {
            // Приветствие
            Surface(color = Color.White.copy(alpha = 0.15f), shape = RoundedCornerShape(CornerRadius.XLarge)) {
                Column(
                    modifier = Modifier.padding(Spacing.XL),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("✅", style = MaterialTheme.typography.displayLarge.copy(fontSize = 80.sp))
                    Text("ВСЁ ХОРОШО", style = MaterialTheme.typography.displayLarge.copy(fontSize = 32.sp), color = SuccessGreen)
                    Text("Угроз не обнаружено", style = MaterialTheme.typography.bodyLarge.copy(fontSize = 20.sp), color = Color.White.copy(alpha = 0.9f))
                }
            }
            
            // Большие кнопки
            BigElderlyButton("📞", "ПОЗВОНИТЬ РОДНЫМ", "Быстрый набор", SuccessGreen)
            BigElderlyButton("🛡️", "БЕЗОПАСНОСТЬ", "Статус защиты", PrimaryBlue)
            BigElderlyButton("📖", "ИНСТРУКЦИИ", "Помощь и советы", WarningOrange)
            
            // SOS кнопка
            Surface(
                onClick = {},
                shape = RoundedCornerShape(CornerRadius.XLarge),
                color = Color.Transparent
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Brush.linearGradient(listOf(DangerRed, Color(0xFFDC2626))))
                        .padding(Spacing.XL),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("🚨", style = MaterialTheme.typography.displayLarge.copy(fontSize = 64.sp))
                        Text("КНОПКА SOS", style = MaterialTheme.typography.displayLarge.copy(fontSize = 28.sp), color = Color.White)
                        Text("Экстренная помощь", style = MaterialTheme.typography.bodyLarge.copy(fontSize = 18.sp), color = Color.White.copy(alpha = 0.9f))
                    }
                }
            }
        }
    }
}

@Composable
private fun BigElderlyButton(icon: String, title: String, subtitle: String, color: Color) {
    Surface(
        onClick = {},
        shape = RoundedCornerShape(CornerRadius.Large),
        color = color.copy(alpha = 0.3f)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.L),
            horizontalArrangement = Arrangement.spacedBy(Spacing.L)
        ) {
            Text(icon, style = MaterialTheme.typography.displayLarge.copy(fontSize = 56.sp))
            
            Column {
                Text(title, style = MaterialTheme.typography.displaySmall.copy(fontSize = 22.sp), color = Color.White)
                Text(subtitle, style = MaterialTheme.typography.bodyLarge.copy(fontSize = 18.sp), color = Color.White.copy(alpha = 0.8f))
            }
        }
    }
}



