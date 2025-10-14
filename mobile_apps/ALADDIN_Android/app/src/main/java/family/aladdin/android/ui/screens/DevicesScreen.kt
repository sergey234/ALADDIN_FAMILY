package family.aladdin.android.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.buttons.PrimaryButton
import family.aladdin.android.ui.components.navigation.ALADDINTopAppBar
import family.aladdin.android.ui.theme.*
import family.aladdin.android.ui.theme.Size

/**
 * 📱 Devices Screen
 * Экран управления устройствами семьи
 * 12_devices_screen из HTML
 */

data class Device(
    val id: String,
    val name: String,
    val owner: String,
    val type: DeviceType,
    val status: DeviceStatus,
    val lastActive: String
)

enum class DeviceType(val icon: String, val displayName: String) {
    IPHONE("📱", "iPhone"),
    IPAD("📱", "iPad"),
    MAC("💻", "Mac"),
    ANDROID("📱", "Android"),
    WINDOWS("💻", "Windows")
}

enum class DeviceStatus(val icon: String, val color: androidx.compose.ui.graphics.Color, val text: String) {
    PROTECTED("🟢", SuccessGreen, "Защищено"),
    WARNING("⚠️", WarningOrange, "Внимание"),
    DANGER("🔴", DangerRed, "Опасность"),
    INACTIVE("⚫", TextTertiary, "Неактивно")
}

@Composable
fun DevicesScreen(navController: NavHostController) {
    
    val devices = remember {
        listOf(
            Device("1", "iPhone 14 Pro", "Сергей", DeviceType.IPHONE, DeviceStatus.PROTECTED, "Сейчас"),
            Device("2", "MacBook Pro", "Сергей", DeviceType.MAC, DeviceStatus.PROTECTED, "5 мин назад"),
            Device("3", "iPad Air", "Маша", DeviceType.IPAD, DeviceStatus.WARNING, "10 мин назад"),
            Device("4", "iPhone 12", "Мария", DeviceType.IPHONE, DeviceStatus.PROTECTED, "1 час назад"),
            Device("5", "Samsung Galaxy", "Бабушка", DeviceType.ANDROID, DeviceStatus.INACTIVE, "2 часа назад"),
            Device("6", "MacBook Air", "Маша", DeviceType.MAC, DeviceStatus.PROTECTED, "3 часа назад"),
            Device("7", "iPad Mini", "Петя", DeviceType.IPAD, DeviceStatus.DANGER, "5 часов назад"),
            Device("8", "iPhone SE", "Петя", DeviceType.IPHONE, DeviceStatus.WARNING, "1 день назад")
        )
    }
    
    Box(modifier = Modifier.fillMaxSize().backgroundGradient()) {
        Column(modifier = Modifier.fillMaxSize()) {
            
            ALADDINTopAppBar(
                title = "УСТРОЙСТВА",
                subtitle = "${devices.size} устройств под защитой",
                onBackClick = { navController.popBackStack() }
            )
            
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(ScreenPadding)
            ) {
                
                // Stats
                item {
                    Column(modifier = Modifier.padding(bottom = SpacingL)) {
                        Text(
                            text = "📊 СТАТИСТИКА",
                            style = MaterialTheme.typography.headlineSmall,
                            color = TextPrimary,
                            modifier = Modifier.padding(bottom = SpacingM)
                        )
                        
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .cardBackground()
                                .padding(CardPadding),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "🛡️ ${devices.count { it.status == DeviceStatus.PROTECTED }}",
                                    style = MaterialTheme.typography.headlineMedium,
                                    color = SuccessGreen
                                )
                                Text("Защищено", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                            }
                            
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "⚠️ ${devices.count { it.status == DeviceStatus.WARNING || it.status == DeviceStatus.DANGER }}",
                                    style = MaterialTheme.typography.headlineMedium,
                                    color = WarningOrange
                                )
                                Text("Требует внимания", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                            }
                            
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "📱 ${devices.size}",
                                    style = MaterialTheme.typography.headlineMedium,
                                    color = InfoBlue
                                )
                                Text("Всего", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                            }
                        }
                    }
                }
                
                // List Header
                item {
                    Text(
                        text = "СПИСОК УСТРОЙСТВ",
                        style = MaterialTheme.typography.headlineSmall,
                        color = TextPrimary,
                        modifier = Modifier.padding(bottom = SpacingM)
                    )
                }
                
                // Devices List
                items(devices) { device ->
                    DeviceRow(
                        device = device,
                        onClick = { 
                            // TODO: Navigate to device details
                        }
                    )
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                // Add Device Button
                item {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .cardBackground()
                            .padding(CardPadding)
                            .clickable { 
                                // TODO: Show add device dialog
                            }
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("➕", style = MaterialTheme.typography.headlineMedium)
                            Spacer(modifier = Modifier.width(SpacingM))
                            Column(modifier = Modifier.weight(1f)) {
                                Text("Добавить устройство", style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
                                Text("Подключите новое устройство к защите", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                            }
                            Text("›", style = MaterialTheme.typography.headlineMedium, color = TextSecondary)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun DeviceRow(device: Device, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .cardBackground()
            .padding(CardPadding)
            .clickable(onClick = onClick),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Device Icon
        Box(
            modifier = Modifier.size(Size.AvatarMedium),
            contentAlignment = Alignment.Center
        ) {
            Text(device.type.icon, style = MaterialTheme.typography.headlineMedium)
        }
        
        Spacer(modifier = Modifier.width(SpacingM))
        
        // Device Info
        Column(modifier = Modifier.weight(1f)) {
            Text(device.name, style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
            Row {
                Text("👤 ${device.owner}", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                Text(" • ", style = MaterialTheme.typography.bodySmall, color = TextTertiary)
                Text(device.type.displayName, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            }
            Text("⏰ ${device.lastActive}", style = MaterialTheme.typography.bodySmall, color = TextTertiary)
        }
        
        // Status
        Column(horizontalAlignment = Alignment.End) {
            Text(device.status.icon, style = MaterialTheme.typography.headlineMedium)
            Text(device.status.text, style = MaterialTheme.typography.bodySmall, color = device.status.color)
        }
    }
}



