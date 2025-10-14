package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.cards.FamilyMemberCard
import family.aladdin.android.ui.components.cards.FamilyRole
import family.aladdin.android.ui.components.cards.ProtectionStatus
import family.aladdin.android.ui.components.navigation.ALADDINTopBar
import family.aladdin.android.ui.components.navigation.TopBarAction
import family.aladdin.android.ui.theme.*

/**
 * 👨‍👩‍👧‍👦 Family Screen
 * Экран семьи
 * Источник: iOS FamilyScreen.swift и 03_family_screen.html
 */

@Composable
fun FamilyScreen(
    navController: NavHostController
) {
    var showRewardsQuickModal by remember { mutableStateOf(false) }
    var unicornBalance by remember { mutableStateOf(245) }
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
                title = "СЕМЬЯ",
                subtitle = "4 члена под защитой",
                onBackClick = { navController.popBackStack() },
                actions = {
                    TopBarAction(
                        icon = Icons.Default.Add,
                        onClick = { 
                            // TODO: Navigate to add member screen
                        }
                    )
                }
            )
            
            // Контент
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.M)
            ) {
                // Обзор семьи
                FamilyOverview()
                
                // Заголовок
                Text(
                    text = "ЧЛЕНЫ СЕМЬИ",
                    style = MaterialTheme.typography.displaySmall,
                    color = TextPrimary,
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding)
                )
                
                // Список членов
                Column(
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
                    verticalArrangement = Arrangement.spacedBy(Spacing.M)
                ) {
                    FamilyMemberCard(
                        name = "Сергей",
                        role = FamilyRole.PARENT,
                        avatar = "👨",
                        status = ProtectionStatus.PROTECTED,
                        threatsBlocked = 47
                    )
                    
                    FamilyMemberCard(
                        name = "Мария",
                        role = FamilyRole.PARENT,
                        avatar = "👩",
                        status = ProtectionStatus.PROTECTED,
                        threatsBlocked = 32,
                        lastActive = "5 мин назад"
                    )
                    
                    FamilyMemberCard(
                        name = "Маша",
                        role = FamilyRole.CHILD,
                        avatar = "👧",
                        status = ProtectionStatus.WARNING,
                        threatsBlocked = 23,
                        lastActive = "10 мин назад"
                    )
                    
                    FamilyMemberCard(
                        name = "Бабушка",
                        role = FamilyRole.ELDERLY,
                        avatar = "👵",
                        status = ProtectionStatus.OFFLINE,
                        threatsBlocked = 12,
                        lastActive = "2 часа назад"
                    )
                }
                
                // НОВОЕ: Карточка вознаграждений 🦄
                RewardsQuickCard(
                    unicornBalance = unicornBalance,
                    weeklyRewarded = 128,
                    onClick = { showRewardsQuickModal = true }
                )
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
        
        // Модальное окно вознаграждений
        if (showRewardsQuickModal) {
            RewardsQuickModalDialog(
                unicornBalance = unicornBalance,
                onReward = { unicornBalance += 10 },
                onPunish = { unicornBalance -= 10 },
                onDismiss = { showRewardsQuickModal = false }
            )
        }
    }
}

@Composable
private fun FamilyOverview() {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.CardPadding),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Text(text = "👨‍👩‍👧‍👦", style = MaterialTheme.typography.displayLarge)
            
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = "Ваша семья",
                    style = MaterialTheme.typography.displayMedium,
                    color = TextPrimary
                )
                Text(
                    text = "4 члена • Все под защитой",
                    style = MaterialTheme.typography.bodyLarge,
                    color = TextSecondary
                )
            }
            
            // Статистика
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem("🛡️", "47", "Угроз")
                Divider(modifier = Modifier.width(1.dp).height(40.dp), color = Color.White.copy(alpha = 0.2f))
                StatItem("⏰", "24/7", "Защита")
                Divider(modifier = Modifier.width(1.dp).height(40.dp), color = Color.White.copy(alpha = 0.2f))
                StatItem("📱", "8", "Устройств")
            }
        }
    }
}

@Composable
private fun StatItem(icon: String, value: String, label: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(Spacing.XS)
    ) {
        Text(text = icon, style = MaterialTheme.typography.displayMedium)
        Text(text = value, style = MaterialTheme.typography.displaySmall, color = PrimaryBlue)
        Text(text = label, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
    }
}

@Composable
private fun RewardsQuickCard(unicornBalance: Int, weeklyRewarded: Int, onClick: () -> Unit) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = UnicornPurple.copy(alpha = 0.12f),
        border = androidx.compose.foundation.BorderStroke(2.dp, UnicornPurple.copy(alpha = 0.4f)),
        onClick = onClick
    ) {
        Column(
            modifier = Modifier.padding(Spacing.CardPadding),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Text("🦄", style = MaterialTheme.typography.displayLarge)
            
            Text("Вознаграждение ребёнка", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold), color = UnicornPurple)
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.L),
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("$unicornBalance", style = MaterialTheme.typography.displayMedium, color = UnicornPurple)
                    Text("Баланс 🦄", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
                }
                
                Box(
                    modifier = Modifier
                        .width(1.dp)
                        .height(30.dp)
                        .background(TextSecondary.copy(alpha = 0.3f))
                )
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("+$weeklyRewarded", style = MaterialTheme.typography.displayMedium, color = SuccessGreen)
                    Text("За неделю", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
                }
            }
        }
    }
}

@Composable
private fun RewardsQuickModalDialog(
    unicornBalance: Int,
    onReward: () -> Unit,
    onPunish: () -> Unit,
    onDismiss: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            Surface(color = BackgroundMedium.copy(alpha = 0.3f), tonalElevation = 4.dp) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = Spacing.ScreenPadding, vertical = Spacing.M),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(horizontalArrangement = Arrangement.spacedBy(Spacing.XS)) {
                        Text("🦄", style = MaterialTheme.typography.titleLarge)
                        Text("Вознаграждение ребёнка", style = MaterialTheme.typography.displaySmall, color = UnicornPurple)
                    }
                    
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Default.Close, contentDescription = "Закрыть", tint = TextSecondary)
                    }
                }
            }
            
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(Spacing.L),
                verticalArrangement = Arrangement.spacedBy(Spacing.L),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Баланс
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(CornerRadius.Large),
                    color = UnicornPurple.copy(alpha = 0.15f)
                ) {
                    Column(
                        modifier = Modifier.padding(Spacing.L),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text("🦄", style = MaterialTheme.typography.displayLarge.copy(fontSize = 48.sp))
                        Text("$unicornBalance", style = MaterialTheme.typography.displayLarge.copy(fontSize = 36.sp), color = UnicornPurple)
                        Text("Единорогов на счету", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                    }
                }
                
                // Быстрые действия
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(Spacing.M)
                ) {
                    Surface(
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(CornerRadius.Medium),
                        color = SuccessGreen.copy(alpha = 0.2f),
                        border = androidx.compose.foundation.BorderStroke(2.dp, SuccessGreen),
                        onClick = { onReward(); onDismiss() }
                    ) {
                        Column(
                            modifier = Modifier.padding(Spacing.M),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("✅", style = MaterialTheme.typography.displaySmall)
                            Text("Вознаградить", style = MaterialTheme.typography.bodySmall, color = SuccessGreen)
                        }
                    }
                    
                    Surface(
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(CornerRadius.Medium),
                        color = DangerRed.copy(alpha = 0.2f),
                        border = androidx.compose.foundation.BorderStroke(2.dp, DangerRed),
                        onClick = { onPunish(); onDismiss() }
                    ) {
                        Column(
                            modifier = Modifier.padding(Spacing.M),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("❌", style = MaterialTheme.typography.displaySmall)
                            Text("Наказать", style = MaterialTheme.typography.bodySmall, color = DangerRed)
                        }
                    }
                }
            }
        }
    }
}

