package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.buttons.PrimaryButton
import family.aladdin.android.ui.components.navigation.ALADDINTopBar
import family.aladdin.android.ui.components.navigation.TopBarAction
import family.aladdin.android.ui.theme.*

/**
 * 🛡️ VPN Screen
 * Экран VPN защиты
 * Источник: iOS VPNScreen.swift и 02_protection_screen.html
 */

@Composable
fun VPNScreen(
    navController: NavHostController
) {
    var isVPNEnabled by remember { mutableStateOf(true) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        GradientStart,
                        GradientMiddle,
                        GradientEnd
                    )
                )
            )
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Навигация
            ALADDINTopBar(
                title = "VPN ЗАЩИТА",
                subtitle = if (isVPNEnabled) "Подключено" else "Отключено",
                onBackClick = { navController.popBackStack() },
                actions = {
                    TopBarAction(
                        icon = Icons.Default.Settings,
                        onClick = { 
                            // TODO: Navigate to VPN settings
                        }
                    )
                }
            )
            
            // Контент
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.L),
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                // VPN Status Card
                VPNStatusCard(isEnabled = isVPNEnabled)
                
                // Кнопка управления
                PrimaryButton(
                    text = if (isVPNEnabled) "Отключить VPN" else "Включить VPN",
                    onClick = { isVPNEnabled = !isVPNEnabled },
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding)
                )
                
                // Выбор сервера
                ServerSelection()
                
                // Статистика
                StatisticsSection()
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
    }
}

@Composable
private fun VPNStatusCard(isEnabled: Boolean) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = BackgroundMedium.copy(alpha = 0.3f)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.CardPadding),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(Spacing.L)
        ) {
            // Иконка
            Box(
                modifier = Modifier
                    .size(120.dp)
                    .background(
                        color = if (isEnabled)
                            SuccessGreen.copy(alpha = 0.2f)
                        else
                            TextSecondary.copy(alpha = 0.2f),
                        shape = CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = if (isEnabled) "🛡️" else "🔒",
                    style = MaterialTheme.typography.displayLarge.copy(fontSize = MaterialTheme.typography.displayLarge.fontSize * 1.5f)
                )
            }
            
            // Статус
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = if (isEnabled) "ЗАЩИЩЕНО" else "НЕ ЗАЩИЩЕНО",
                    style = MaterialTheme.typography.displayLarge,
                    color = if (isEnabled) SuccessGreen else DangerRed
                )
                Text(
                    text = if (isEnabled)
                        "Ваше соединение зашифровано"
                    else
                        "Включите VPN для защиты",
                    style = MaterialTheme.typography.bodyLarge,
                    color = TextSecondary
                )
            }
            
            // IP адрес
            if (isEnabled) {
                Surface(
                    shape = RoundedCornerShape(CornerRadius.Medium),
                    color = BackgroundMedium.copy(alpha = 0.5f),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(Spacing.M),
                        horizontalArrangement = Arrangement.spacedBy(Spacing.S)
                    ) {
                        Text(text = "🌐", style = MaterialTheme.typography.bodyLarge)
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Ваш IP адрес",
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary
                            )
                            Text(
                                text = "192.168.1.147",
                                style = MaterialTheme.typography.bodyMedium,
                                color = PrimaryBlue
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ServerSelection() {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.S)
    ) {
        Text(
            text = "СЕРВЕР",
            style = MaterialTheme.typography.displaySmall,
            color = TextPrimary
        )
        
        Surface(
            onClick = { 
                // TODO: Show server selection dialog
            },
            shape = RoundedCornerShape(CornerRadius.Large),
            color = BackgroundMedium.copy(alpha = 0.5f)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(Spacing.CardPadding),
                horizontalArrangement = Arrangement.spacedBy(Spacing.M),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = "🇷🇺", style = MaterialTheme.typography.displayLarge)
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Россия • Москва",
                        style = MaterialTheme.typography.bodyLarge,
                        color = TextPrimary
                    )
                    Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XS)) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .background(SuccessGreen, CircleShape)
                        )
                        Text(
                            text = "Ping: 12 ms",
                            style = MaterialTheme.typography.bodySmall,
                            color = SuccessGreen
                        )
                    }
                }
                
                Text(text = "›", style = MaterialTheme.typography.displaySmall, color = TextSecondary)
            }
        }
    }
}

@Composable
private fun StatisticsSection() {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.S)
    ) {
        Text(
            text = "СТАТИСТИКА",
            style = MaterialTheme.typography.displaySmall,
            color = TextPrimary
        )
        
        Column(verticalArrangement = Arrangement.spacedBy(Spacing.S)) {
            StatCard("⬇️", "Загружено", "2.4 GB", "За сегодня")
            StatCard("⬆️", "Отправлено", "1.2 GB", "За сегодня")
            StatCard("⏱️", "Время сессии", "4:37:21", "Активная сессия")
            StatCard("🛡️", "Заблокировано", "47", "Угроз за неделю")
        }
    }
}

@Composable
private fun StatCard(icon: String, title: String, value: String, subtitle: String) {
    Surface(
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.3f)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Text(text = icon, style = MaterialTheme.typography.displayMedium)
            
            Column {
                Text(text = title, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                Text(text = value, style = MaterialTheme.typography.displaySmall, color = TextPrimary)
                Text(text = subtitle, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            }
        }
    }
}



