package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
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

data class AppNotification(
    val icon: String,
    val title: String,
    val message: String,
    val time: String,
    val isRead: Boolean
)

@Composable
fun NotificationsScreen(navController: NavHostController) {
    val notifications = remember {
        mutableStateListOf(
            AppNotification("🛡️", "Угроза заблокирована", "Заблокирован вредоносный сайт", "5 мин назад", false),
            AppNotification("✅", "VPN подключён", "Ваше соединение защищено", "1 час назад", true),
            AppNotification("⚠️", "Подозрительная активность", "Обнаружена попытка доступа", "2 часа назад", true)
        )
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            ALADDINTopBar(
                title = "УВЕДОМЛЕНИЯ",
                subtitle = "${notifications.count { !it.isRead }} непрочитанных",
                onBackClick = { navController.popBackStack() },
                actions = {
                    TopBarAction(icon = Icons.Default.CheckCircle, onClick = {})
                }
            )
            
            LazyColumn(
                modifier = Modifier.padding(top = Spacing.M),
                contentPadding = PaddingValues(horizontal = Spacing.ScreenPadding, vertical = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.M)
            ) {
                items(notifications) { notification ->
                    NotificationCard(notification)
                }
            }
        }
    }
}

@Composable
private fun NotificationCard(notification: AppNotification) {
    Surface(
        onClick = {},
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = if (notification.isRead) BackgroundMedium.copy(alpha = 0.3f) else BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Box(
                modifier = Modifier
                    .size(50.dp)
                    .background(PrimaryBlue.copy(alpha = 0.2f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(notification.icon, style = MaterialTheme.typography.displayMedium)
            }
            
            Column(modifier = Modifier.weight(1f)) {
                Text(notification.title, style = if (notification.isRead) MaterialTheme.typography.bodyLarge else MaterialTheme.typography.bodyMedium, color = TextPrimary)
                Text(notification.message, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                Text(notification.time, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            }
            
            if (!notification.isRead) {
                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .background(PrimaryBlue, CircleShape)
                )
            }
        }
    }
}



