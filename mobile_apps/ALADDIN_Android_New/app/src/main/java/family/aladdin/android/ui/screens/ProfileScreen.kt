package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
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
fun ProfileScreen(navController: NavHostController) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            ALADDINTopBar(
                title = "ПРОФИЛЬ",
                subtitle = "Личная информация",
                onBackClick = { navController.popBackStack() },
                actions = {
                    TopBarAction(icon = Icons.Default.Edit, onClick = {})
                }
            )
            
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.L),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                // Аватар
                Box(
                    modifier = Modifier
                        .size(100.dp)
                        .background(Brush.linearGradient(listOf(PrimaryBlue, SecondaryBlue)), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text("👨", style = MaterialTheme.typography.displayLarge.copy(fontSize = MaterialTheme.typography.displayLarge.fontSize * 1.5f))
                }
                
                Text("Сергей Хлыстов", style = MaterialTheme.typography.displayMedium, color = Color.White)
                Text("sergey@aladdin.family", style = MaterialTheme.typography.bodyLarge, color = TextSecondary)
                
                Surface(
                    shape = RoundedCornerShape(CornerRadius.Full),
                    color = SecondaryGold.copy(alpha = 0.2f)
                ) {
                    Text(
                        "⭐ Premium до 31.12.2025",
                        modifier = Modifier.padding(horizontal = Spacing.L, vertical = Spacing.S),
                        color = SecondaryGold
                    )
                }
                
                // Статистика
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = Spacing.ScreenPadding),
                    horizontalArrangement = Arrangement.spacedBy(Spacing.M)
                ) {
                    ProfileStat("🛡️", "47", "Угроз", Modifier.weight(1f))
                    ProfileStat("👥", "4", "Членов", Modifier.weight(1f))
                    ProfileStat("📱", "8", "Устройств", Modifier.weight(1f))
                }
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
    }
}

@Composable
private fun ProfileStat(icon: String, value: String, label: String, modifier: Modifier) {
    Surface(modifier = modifier, shape = RoundedCornerShape(CornerRadius.Medium), color = BackgroundMedium.copy(alpha = 0.3f)) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(icon, style = MaterialTheme.typography.displayMedium)
            Text(value, style = MaterialTheme.typography.displayMedium, color = PrimaryBlue)
            Text(label, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
        }
    }
}



