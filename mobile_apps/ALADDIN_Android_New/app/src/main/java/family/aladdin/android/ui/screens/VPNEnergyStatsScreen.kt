package family.aladdin.android.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.background
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material3.MaterialTheme
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.navigation.ALADDINTopAppBar
import family.aladdin.android.ui.theme.*

/**
 * 🔋 VPN Energy Stats Screen
 * Статистика энергопотребления VPN
 * 18_vpn_energy_stats из HTML
 * ПОЛНАЯ КАЧЕСТВЕННАЯ ВЕРСИЯ С ДЕТАЛЬНОЙ СТАТИСТИКОЙ!
 */

@Composable
fun VPNEnergyStatsScreen(navController: NavHostController) {
    
    var selectedPeriod by remember { mutableStateOf(0) }
    val periods = listOf("Сегодня", "Неделя", "Месяц")
    
    val batteryUsage by remember { mutableStateOf(12.5) } // %
    val dataUsage by remember { mutableStateOf("2.4 GB") }
    val sessionTime by remember { mutableStateOf("4:37:21") }
    val energyConsumed by remember { mutableStateOf(245) } // mAh
    val averageConsumption by remember { mutableStateOf(53) } // mAh/hour
    
    Box(modifier = Modifier.fillMaxSize().backgroundGradient()) {
        Column(modifier = Modifier.fillMaxSize()) {
            
            // Top App Bar
            ALADDINTopAppBar(
                title = "ЭНЕРГОПОТРЕБЛЕНИЕ VPN",
                subtitle = "Статистика использования",
                onBackClick = { navController.popBackStack() }
            )
            
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(ScreenPadding)
            ) {
                
                // Battery Impact Card
                item {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .cardBackground()
                            .padding(CardPadding),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text("🔋", style = MaterialTheme.typography.headlineLarge.copy(fontSize = 80.sp))
                        
                        Spacer(modifier = Modifier.height(SpacingM))
                        
                        Text(
                            "${String.format("%.1f", batteryUsage)}%",
                            style = MaterialTheme.typography.headlineLarge.copy(fontSize = 48.sp),
                            color = SecondaryGold
                        )
                        
                        Text(
                            "Расход батареи за сегодня",
                            style = MaterialTheme.typography.bodyMedium,
                            color = TextSecondary
                        )
                        
                        Spacer(modifier = Modifier.height(SpacingL))
                        
                        // Progress Bar
                        LinearProgressIndicator(
                            progress = (batteryUsage / 100).toFloat(),
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(8.dp),
                            color = SecondaryGold,
                            trackColor = BackgroundMedium,
                            strokeCap = StrokeCap.Round
                        )
                        
                        Spacer(modifier = Modifier.height(SpacingM))
                        
                        Text(
                            "Это ниже среднего! VPN работает эффективно ✅",
                            style = MaterialTheme.typography.bodySmall,
                            color = SuccessGreen,
                            textAlign = TextAlign.Center
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(SpacingL))
                }
                
                // Period Tabs
                item {
                    TabRow(
                        selectedTabIndex = selectedPeriod,
                        containerColor = SurfaceDark,
                        contentColor = TextPrimary
                    ) {
                        periods.forEachIndexed { index, period ->
                            Tab(
                                selected = selectedPeriod == index,
                                onClick = { selectedPeriod = index },
                                text = {
                                    Text(
                                        period,
                                        style = MaterialTheme.typography.labelMedium,
                                        color = if (selectedPeriod == index) SecondaryGold else TextSecondary
                                    )
                                }
                            )
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(SpacingL))
                }
                
                // Energy Statistics
                item {
                    Text("СТАТИСТИКА", style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                item {
                    EnergyStatCard(icon = "⚡", label = "Потреблено энергии", value = "$energyConsumed mAh", color = WarningOrange)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                item {
                    EnergyStatCard(icon = "⏱️", label = "Время работы VPN", value = sessionTime, color = InfoBlue)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                item {
                    EnergyStatCard(icon = "📊", label = "Средний расход", value = "$averageConsumption mAh/час", color = SuccessGreen)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                item {
                    EnergyStatCard(icon = "🌐", label = "Трафик обработан", value = dataUsage, color = InfoBlue)
                    Spacer(modifier = Modifier.height(SpacingXL))
                }
                
                // Comparison with other VPNs
                item {
                    Text("СРАВНЕНИЕ С ДРУГИМИ VPN", style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                item {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .cardBackground()
                            .padding(CardPadding)
                    ) {
                        VPNComparisonRow(name = "ALADDIN VPN", usage = 12.5, color = SuccessGreen)
                        Spacer(modifier = Modifier.height(SpacingS))
                        VPNComparisonRow(name = "NordVPN", usage = 18.3, color = WarningOrange)
                        Spacer(modifier = Modifier.height(SpacingS))
                        VPNComparisonRow(name = "ExpressVPN", usage = 22.1, color = DangerRed)
                        Spacer(modifier = Modifier.height(SpacingS))
                        VPNComparisonRow(name = "ProtonVPN", usage = 19.7, color = WarningOrange)
                    }
                    
                    Spacer(modifier = Modifier.height(SpacingXL))
                }
                
                // Energy Saving Tips
                item {
                    Text("💡 СОВЕТЫ ПО ЭКОНОМИИ", style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                val tips = listOf(
                    "Используйте Wi-Fi вместо сотовой сети для большей эффективности",
                    "Отключайте VPN когда не используете интернет активно",
                    "Выбирайте ближайший сервер для уменьшения задержки",
                    "Используйте режим 'Эко' в настройках VPN"
                )
                
                items(tips) { tip ->
                    EnergyTipCard(tip = tip)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                // Battery Impact Graph (placeholder)
                item {
                    Spacer(modifier = Modifier.height(SpacingL))
                    Text("ГРАФИК РАСХОДА ЗА ДЕНЬ", style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
                    Spacer(modifier = Modifier.height(SpacingM))
                    
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .cardBackground()
                            .padding(CardPadding),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            "📊 График энергопотребления",
                            style = MaterialTheme.typography.bodyMedium,
                            color = TextSecondary
                        )
                        Spacer(modifier = Modifier.height(SpacingM))
                        
                        // Simple bar chart representation
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.Bottom
                        ) {
                            BatteryBar(hour = "00-06", percentage = 5f)
                            BatteryBar(hour = "06-12", percentage = 45f)
                            BatteryBar(hour = "12-18", percentage = 35f)
                            BatteryBar(hour = "18-24", percentage = 15f)
                        }
                    }
                }
            }
        }
    }
}

// MARK: - Helper Composables

@Composable
fun EnergyStatCard(icon: String, label: String, value: String, color: androidx.compose.ui.graphics.Color) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .cardBackground()
            .padding(SpacingM),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(icon, style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.width(SpacingM))
        Column(modifier = Modifier.weight(1f)) {
            Text(label, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            Text(value, style = MaterialTheme.typography.headlineSmall, color = color)
        }
    }
}

@Composable
fun VPNComparisonRow(name: String, usage: Double, color: androidx.compose.ui.graphics.Color) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(name, style = MaterialTheme.typography.bodyMedium, color = TextPrimary)
            Text("${String.format("%.1f", usage)}%", style = MaterialTheme.typography.labelMedium, color = color)
        }
        
        Spacer(modifier = Modifier.height(SpacingXXS))
        
        // Progress bar
        LinearProgressIndicator(
            progress = (usage / 25.0).toFloat(),
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp),
            color = color,
            trackColor = BackgroundMedium,
            strokeCap = StrokeCap.Round
        )
    }
}

@Composable
fun EnergyTipCard(tip: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .cardBackground()
            .padding(SpacingM),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text("💡", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.width(SpacingM))
        Text(tip, style = MaterialTheme.typography.bodyMedium, color = TextPrimary)
    }
}

@Composable
fun BatteryBar(hour: String, percentage: Float) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.width(60.dp)
    ) {
        Box(
            modifier = Modifier
                .width(40.dp)
                .height((percentage * 1.5).dp)
                .background(SecondaryGold, shape = RoundedCornerShape(CornerRadiusSmall))
        )
        Spacer(modifier = Modifier.height(SpacingXS))
        Text(hour, style = MaterialTheme.typography.bodySmall, color = TextTertiary)
    }
}



