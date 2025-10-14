package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.navigation.ALADDINTopBar
import family.aladdin.android.ui.components.navigation.TopBarAction
import family.aladdin.android.ui.theme.*

@Composable
fun AnalyticsScreen(navController: NavHostController) {
    var selectedPeriod by remember { mutableStateOf("Неделя") }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            ALADDINTopBar(
                title = "АНАЛИТИКА",
                subtitle = "Статистика защиты",
                onBackClick = { navController.popBackStack() },
                actions = {
                    TopBarAction(icon = Icons.Default.FilterList, onClick = {})
                }
            )
            
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                // Период
                Row(
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
                    horizontalArrangement = Arrangement.spacedBy(Spacing.S)
                ) {
                    listOf("День", "Неделя", "Месяц").forEach { period ->
                        Button(
                            onClick = { selectedPeriod = period },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (selectedPeriod == period) PrimaryBlue else BackgroundMedium.copy(alpha = 0.3f)
                            )
                        ) {
                            Text(period)
                        }
                    }
                }
                
                // Статистика
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = Spacing.ScreenPadding),
                    shape = RoundedCornerShape(CornerRadius.Large),
                    color = BackgroundMedium.copy(alpha = 0.5f)
                ) {
                    Column(modifier = Modifier.padding(Spacing.CardPadding)) {
                        Text("ОБЩАЯ СТАТИСТИКА", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
                        
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            StatColumn("🛡️", "47", "Угроз\nобнаружено")
                            Divider(modifier = Modifier.width(1.dp).height(60.dp))
                            StatColumn("✅", "45", "Успешно\nзаблокировано")
                            Divider(modifier = Modifier.width(1.dp).height(60.dp))
                            StatColumn("📱", "5,234", "Проверено\nэлементов")
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
    }
}

@Composable
private fun StatColumn(icon: String, value: String, label: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(icon, style = MaterialTheme.typography.displayMedium)
        Text(value, style = MaterialTheme.typography.displayMedium, color = PrimaryBlue)
        Text(label, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
    }
}



