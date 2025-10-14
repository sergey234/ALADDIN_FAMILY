package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.buttons.SecondaryButton
import family.aladdin.android.ui.components.inputs.ALADDINToggle
import family.aladdin.android.ui.components.navigation.ALADDINTopAppBar
import family.aladdin.android.ui.theme.*

/**
 * 📱 Device Detail Screen
 * Детали конкретного устройства
 * 15_device_detail_screen из HTML
 * ПОЛНАЯ КАЧЕСТВЕННАЯ ВЕРСИЯ!
 */

@Composable
fun DeviceDetailScreen(
    navController: NavHostController,
    deviceId: String = "1"
) {
    
    // Mock данные устройства
    val device = remember {
        Device(
            id = deviceId,
            name = "iPhone 14 Pro",
            owner = "Сергей",
            type = DeviceType.IPHONE,
            status = DeviceStatus.PROTECTED,
            lastActive = "Сейчас"
        )
    }
    
    var selectedTab by remember { mutableStateOf(0) }
    var isProtectionOn by remember { mutableStateOf(true) }
    var isScanningEnabled by remember { mutableStateOf(true) }
    
    val tabs = listOf("Инфо", "Статистика", "Угрозы", "Настройки")
    
    Box(modifier = Modifier.fillMaxSize().backgroundGradient()) {
        Column(modifier = Modifier.fillMaxSize()) {
            
            // Top App Bar
            ALADDINTopAppBar(
                title = device.name,
                subtitle = "${device.owner} • ${device.type.displayName}",
                onBackClick = { navController.popBackStack() }
            )
            
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(ScreenPadding)
            ) {
                
                // Device Status Card
                item {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .cardBackground()
                            .padding(CardPadding),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(device.type.icon, style = MaterialTheme.typography.headlineLarge.copy(fontSize = 80.sp))
                        
                        Spacer(modifier = Modifier.height(SpacingM))
                        
                        Text(device.name, style = MaterialTheme.typography.headlineMedium, color = TextPrimary)
                        
                        Spacer(modifier = Modifier.height(SpacingS))
                        
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(StatusIndicatorLarge)
                                    .background(device.status.color, shape = androidx.compose.foundation.shape.CircleShape)
                            )
                            Spacer(modifier = Modifier.width(SpacingXS))
                            Text(device.status.text, style = MaterialTheme.typography.labelMedium, color = device.status.color)
                        }
                        
                        Spacer(modifier = Modifier.height(SpacingXS))
                        
                        Text(
                            "Последняя активность: ${device.lastActive}",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(SpacingL))
                }
                
                // Tab Row
                item {
                    TabRow(
                        selectedTabIndex = selectedTab,
                        containerColor = SurfaceDark,
                        contentColor = TextPrimary
                    ) {
                        tabs.forEachIndexed { index, title ->
                            Tab(
                                selected = selectedTab == index,
                                onClick = { selectedTab = index },
                                text = {
                                    Text(
                                        title,
                                        style = MaterialTheme.typography.labelMedium,
                                        color = if (selectedTab == index) SecondaryGold else TextSecondary
                                    )
                                }
                            )
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(SpacingL))
                }
                
                // Tab Content
                when (selectedTab) {
                    0 -> {
                        // Info Tab
                        item {
                            Column(modifier = Modifier.fillMaxWidth()) {
                                DeviceInfoRow(label = "Владелец", value = device.owner)
                                Spacer(modifier = Modifier.height(SpacingM))
                                DeviceInfoRow(label = "Тип", value = device.type.displayName)
                                Spacer(modifier = Modifier.height(SpacingM))
                                DeviceInfoRow(label = "Модель", value = device.name)
                                Spacer(modifier = Modifier.height(SpacingM))
                                DeviceInfoRow(label = "Система", value = "iOS 17.1")
                                Spacer(modifier = Modifier.height(SpacingM))
                                DeviceInfoRow(label = "IP адрес", value = "192.168.1.147")
                                Spacer(modifier = Modifier.height(SpacingM))
                                DeviceInfoRow(label = "MAC адрес", value = "AA:BB:CC:DD:EE:FF")
                            }
                        }
                    }
                    1 -> {
                        // Stats Tab
                        item {
                            Column(modifier = Modifier.fillMaxWidth()) {
                                DeviceStatCard(icon = "🛡️", title = "Угрозы заблокированы", value = "47", color = DangerRed)
                                Spacer(modifier = Modifier.height(SpacingM))
                                DeviceStatCard(icon = "⬇️", title = "Трафик загружено", value = "2.4 GB", color = InfoBlue)
                                Spacer(modifier = Modifier.height(SpacingM))
                                DeviceStatCard(icon = "⬆️", title = "Трафик отправлено", value = "1.2 GB", color = InfoBlue)
                                Spacer(modifier = Modifier.height(SpacingM))
                                DeviceStatCard(icon = "⏱️", title = "Время использования", value = "4:37:21", color = SuccessGreen)
                            }
                        }
                    }
                    2 -> {
                        // Threats Tab
                        val threats = listOf(
                            ThreatItem("Вредоносный сайт", "5 мин назад", ThreatSeverity.HIGH),
                            ThreatItem("Трекер заблокирован", "15 мин назад", ThreatSeverity.MEDIUM),
                            ThreatItem("Фишинг попытка", "1 час назад", ThreatSeverity.HIGH),
                            ThreatItem("Реклама заблокирована", "2 часа назад", ThreatSeverity.LOW)
                        )
                        items(threats) { threat ->
                            DeviceThreatRow(threat = threat)
                            Spacer(modifier = Modifier.height(SpacingM))
                        }
                    }
                    3 -> {
                        // Settings Tab
                        item {
                            Column(modifier = Modifier.fillMaxWidth()) {
                                ALADDINToggle(
                                    title = "Защита устройства",
                                    isChecked = isProtectionOn,
                                    onCheckedChange = { isProtectionOn = it },
                                    icon = "🛡️"
                                )
                                Spacer(modifier = Modifier.height(SpacingM))
                                ALADDINToggle(
                                    title = "Автоматическое сканирование",
                                    isChecked = isScanningEnabled,
                                    onCheckedChange = { isScanningEnabled = it },
                                    icon = "🔍"
                                )
                            }
                        }
                    }
                }
                
                // Action Buttons
                item {
                    Spacer(modifier = Modifier.height(SpacingXL))
                    
                    Text("ДЕЙСТВИЯ", style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
                    
                    Spacer(modifier = Modifier.height(SpacingM))
                    
                    SecondaryButton(
                        text = "Заблокировать устройство",
                        onClick = { 
                            // TODO: Implement device blocking
                        }
                    )
                    
                    Spacer(modifier = Modifier.height(SpacingM))
                    
                    SecondaryButton(
                        text = "Удалить устройство",
                        onClick = { 
                            // TODO: Implement device removal
                        }
                    )
                }
            }
        }
    }
}

// MARK: - Helper Composables

@Composable
fun DeviceInfoRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .cardBackground()
            .padding(SpacingM),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
        Text(value, style = MaterialTheme.typography.labelMedium, color = TextPrimary)
    }
}

@Composable
fun DeviceStatCard(icon: String, title: String, value: String, color: androidx.compose.ui.graphics.Color) {
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
            Text(title, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            Text(value, style = MaterialTheme.typography.headlineSmall, color = color)
        }
    }
}

data class ThreatItem(
    val name: String,
    val time: String,
    val severity: ThreatSeverity
)

enum class ThreatSeverity(val icon: String, val color: androidx.compose.ui.graphics.Color) {
    LOW("🟢", SuccessGreen),
    MEDIUM("⚠️", WarningOrange),
    HIGH("🔴", DangerRed)
}

@Composable
fun DeviceThreatRow(threat: ThreatItem) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .cardBackground()
            .padding(SpacingM),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(threat.severity.icon, style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.width(SpacingM))
        Column(modifier = Modifier.weight(1f)) {
            Text(threat.name, style = MaterialTheme.typography.bodyMedium, color = TextPrimary)
            Text(threat.time, style = MaterialTheme.typography.bodySmall, color = TextTertiary)
        }
    }
}



