package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.inputs.ALADDINToggle
import family.aladdin.android.ui.components.inputs.ALADDINSlider
import family.aladdin.android.ui.components.navigation.ALADDINTopBar
import family.aladdin.android.ui.theme.*

@Composable
fun SettingsScreen(navController: NavHostController) {
    var isVPNEnabled by remember { mutableStateOf(true) }
    var isNotificationsEnabled by remember { mutableStateOf(true) }
    var isBiometricEnabled by remember { mutableStateOf(true) }
    var protectionLevel by remember { mutableStateOf(75f) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            ALADDINTopBar(title = "НАСТРОЙКИ", subtitle = "Управление приложением", onBackClick = { navController.popBackStack() })
            
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                // Профиль
                ProfileSection()
                
                // Защита
                SecuritySection(
                    isVPNEnabled, { isVPNEnabled = it },
                    isBiometricEnabled, { isBiometricEnabled = it },
                    protectionLevel, { protectionLevel = it }
                )
                
                // Уведомления
                NotificationsSection(isNotificationsEnabled) { isNotificationsEnabled = it }
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
    }
}

@Composable
private fun ProfileSection() {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Row(
            modifier = Modifier.padding(Spacing.CardPadding),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Box(
                modifier = Modifier
                    .size(70.dp)
                    .background(Brush.linearGradient(listOf(PrimaryBlue, SecondaryBlue)), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text("👨", style = MaterialTheme.typography.displayLarge)
            }
            
            Column(modifier = Modifier.weight(1f)) {
                Text("Сергей Хлыстов", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
                Text("sergey@aladdin.family", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                Text("⭐ Premium до 31.12.2025", style = MaterialTheme.typography.bodySmall, color = SecondaryGold)
            }
        }
    }
}

@Composable
private fun SecuritySection(
    isVPNEnabled: Boolean,
    onVPNChange: (Boolean) -> Unit,
    isBiometricEnabled: Boolean,
    onBiometricChange: (Boolean) -> Unit,
    protectionLevel: Float,
    onProtectionChange: (Float) -> Unit
) {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.S)
    ) {
        Text("🛡️ ЗАЩИТА И БЕЗОПАСНОСТЬ", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
        
        ALADDINToggle(
            title = "VPN Защита",
            isChecked = isVPNEnabled,
            onCheckedChange = onVPNChange,
            subtitle = "Шифрование всего трафика",
            icon = "🌐"
        )
        
        ALADDINToggle(
            title = "Биометрия",
            isChecked = isBiometricEnabled,
            onCheckedChange = onBiometricChange,
            subtitle = "Вход по отпечатку",
            icon = "🔐"
        )
        
        ALADDINSlider(
            title = "Уровень защиты",
            value = protectionLevel,
            onValueChange = onProtectionChange,
            subtitle = "От базового до максимального",
            icon = "🛡️",
            unit = "%"
        )
    }
}

@Composable
private fun NotificationsSection(isEnabled: Boolean, onChange: (Boolean) -> Unit) {
    Column(
        modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
        verticalArrangement = Arrangement.spacedBy(Spacing.S)
    ) {
        Text("🔔 УВЕДОМЛЕНИЯ", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
        
        ALADDINToggle(
            title = "Уведомления об угрозах",
            isChecked = isEnabled,
            onCheckedChange = onChange,
            subtitle = "Сообщения о блокировках",
            icon = "⚠️"
        )
    }
}



