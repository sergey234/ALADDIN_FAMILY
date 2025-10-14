package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Notifications
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
import family.aladdin.android.ui.components.cards.FunctionCard
import family.aladdin.android.ui.components.cards.StatusType
import family.aladdin.android.ui.components.navigation.ALADDINTopBar
import family.aladdin.android.ui.components.navigation.TopBarAction
import family.aladdin.android.ui.theme.*

/**
 * 🏠 Main Screen
 * Главный экран ALADDIN
 * Источник: iOS MainScreen.swift и 01_main_screen.html
 */

@Composable
fun MainScreen(navController: NavHostController) {
    var isVPNEnabled by remember { mutableStateOf(true) }
    var selectedTab by remember { mutableStateOf(0) }
    
    // TODO: Use navController for navigation
    // TODO: Use selectedTab for tab switching
    
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
            // Навигационная панель
            ALADDINTopBar(
                title = "ALADDIN",
                subtitle = "AI Защита Семьи",
                actions = {
                    TopBarAction(
                        icon = Icons.Default.Notifications,
                        onClick = { 
                            // TODO: Navigate to notifications
                        }
                    )
                    TopBarAction(
                        icon = Icons.Default.Settings,
                        onClick = { 
                            // TODO: Navigate to settings
                        }
                    )
                }
            )
            
            // Основной контент
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.M)
            ) {
                // VPN статус карточка
                VPNStatusCard(
                    isEnabled = isVPNEnabled,
                    onToggle = { isVPNEnabled = !isVPNEnabled }
                )
                
                // Заголовок секции
                Text(
                    text = "ОСНОВНЫЕ ФУНКЦИИ",
                    style = MaterialTheme.typography.displaySmall,
                    color = TextPrimary,
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding)
                )
                
                // Сетка функций 2x2
                FunctionsGrid()
                
                // Быстрые действия
                QuickActionsSection()
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
    }
}

@Composable
private fun VPNStatusCard(
    isEnabled: Boolean,
    onToggle: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = if (isEnabled) SecondaryGold else BackgroundMedium
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.CardPadding),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Иконка
            Text(
                text = "🛡️",
                style = MaterialTheme.typography.displayLarge
            )
            
            // Информация
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(Spacing.XXS)
            ) {
                Text(
                    text = "VPN ЗАЩИТА",
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (isEnabled) BackgroundDark else TextPrimary
                )
                Text(
                    text = if (isEnabled) "Подключено • Безопасно" else "Отключено",
                    style = MaterialTheme.typography.bodySmall,
                    color = if (isEnabled) SuccessGreen else TextSecondary
                )
            }
            
            // Toggle
            IconButton(onClick = onToggle) {
                Surface(
                    shape = CircleShape,
                    color = if (isEnabled) SuccessGreen else TextSecondary,
                    modifier = Modifier.size(20.dp)
                ) {
                    Text(
                        text = if (isEnabled) "✓" else "✗",
                        color = Color.White,
                        modifier = Modifier.wrapContentSize(Alignment.Center)
                    )
                }
            }
        }
    }
}

@Composable
private fun FunctionsGrid() {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.M)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            FunctionCard(
                icon = "👨‍👩‍👧‍👦",
                title = "СЕМЬЯ",
                subtitle = "4 члена • Всё в порядке",
                status = StatusType.ACTIVE,
                modifier = Modifier.weight(1f),
                onClick = { 
                    // TODO: Navigate to screen
                }
            )
            
            FunctionCard(
                icon = "🌐",
                title = "VPN",
                subtitle = "Подключено",
                status = StatusType.ACTIVE,
                modifier = Modifier.weight(1f),
                onClick = { 
                    // TODO: Navigate to screen
                }
            )
        }
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            FunctionCard(
                icon = "📊",
                title = "АНАЛИТИКА",
                subtitle = "47 угроз заблокировано",
                status = StatusType.WARNING,
                modifier = Modifier.weight(1f),
                onClick = { 
                    // TODO: Navigate to screen
                }
            )
            
            FunctionCard(
                icon = "🤖",
                title = "AI",
                subtitle = "Всегда готов помочь",
                status = StatusType.NEUTRAL,
                modifier = Modifier.weight(1f),
                onClick = { 
                    // TODO: Navigate to screen
                }
            )
        }
    }
}

@Composable
private fun QuickActionsSection() {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.S)
    ) {
        Text(
            text = "БЫСТРЫЕ ДЕЙСТВИЯ",
            style = MaterialTheme.typography.displaySmall,
            color = TextPrimary
        )
        
        QuickActionButton(
            icon = "🚨",
            title = "Экстренная помощь",
            subtitle = "Быстрый вызов службы безопасности"
        )
        
        QuickActionButton(
            icon = "👶",
            title = "Детский контроль",
            subtitle = "Управление доступом детей"
        )
        
        QuickActionButton(
            icon = "📱",
            title = "Безопасность устройств",
            subtitle = "Статус защиты всех устройств"
        )
    }
}

@Composable
private fun QuickActionButton(
    icon: String,
    title: String,
    subtitle: String
) {
    Surface(
        onClick = { 
            // TODO: Navigate to screen
        },
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = icon,
                style = MaterialTheme.typography.displayMedium
            )
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyLarge,
                    color = TextPrimary
                )
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
            }
            
            Text(
                text = "›",
                style = MaterialTheme.typography.displaySmall,
                color = TextSecondary
            )
        }
    }
}



