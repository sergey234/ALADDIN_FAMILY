package family.aladdin.android.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.background
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.buttons.PrimaryButton
import family.aladdin.android.ui.components.buttons.SecondaryButton
import family.aladdin.android.ui.components.navigation.ALADDINTopAppBar
import family.aladdin.android.ui.theme.*

/**
 * 🎁 Referral Screen  
 * Реферальная программа
 * 13_referral_screen из HTML
 */

data class Referral(
    val name: String,
    val date: String,
    val bonus: Int,
    val status: ReferralStatus
)

enum class ReferralStatus(val text: String, val color: androidx.compose.ui.graphics.Color) {
    COMPLETED("Получено", SuccessGreen),
    PENDING("Ожидание", WarningOrange)
}

@Composable
fun ReferralScreen(navController: NavHostController) {
    
    val referralCode = "ALADDIN-SH2024"
    val referrals = remember {
        listOf(
            Referral("Александр К.", "15.10.2025", 500, ReferralStatus.COMPLETED),
            Referral("Мария С.", "12.10.2025", 500, ReferralStatus.COMPLETED),
            Referral("Иван П.", "10.10.2025", 500, ReferralStatus.PENDING)
        )
    }
    
    Box(modifier = Modifier.fillMaxSize().backgroundGradient()) {
        Column(modifier = Modifier.fillMaxSize()) {
            
            ALADDINTopAppBar(
                title = "РЕФЕРАЛЬНАЯ ПРОГРАММА",
                subtitle = "Приглашай друзей - получай бонусы",
                onBackClick = { navController.popBackStack() }
            )
            
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(ScreenPadding)
            ) {
                
                // Header
                item {
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text("🎁", style = MaterialTheme.typography.headlineLarge.copy(fontSize = 80.sp))
                        Spacer(modifier = Modifier.height(SpacingM))
                        Text("Пригласи друзей", style = MaterialTheme.typography.headlineMedium, color = TextPrimary)
                        Text("Получи 500₽ за каждого друга", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                        
                        Spacer(modifier = Modifier.height(SpacingL))
                        
                        // Stats
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .cardBackground()
                                .padding(CardPadding),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text("${referrals.size}", style = MaterialTheme.typography.headlineLarge, color = SecondaryGold)
                                Text("Приглашено", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                            }
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text("${referrals.sumOf { it.bonus }}₽", style = MaterialTheme.typography.headlineLarge, color = SuccessGreen)
                                Text("Заработано", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(SpacingL))
                    }
                }
                
                // Referral Code
                item {
                    Text("ВАШ КОД", style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
                    Spacer(modifier = Modifier.height(SpacingM))
                    
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .cardBackground()
                            .padding(CardPadding),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(referralCode, style = MaterialTheme.typography.headlineMedium, color = SecondaryGold)
                        Spacer(modifier = Modifier)
                        PrimaryButton(
                            text = "Копировать", 
                            onClick = { 
                                // TODO: Implement copy to clipboard
                            }, 
                            modifier = Modifier.width(120.dp)
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(SpacingL))
                }
                
                // Share Buttons
                item {
                    Text("ПОДЕЛИТЬСЯ", style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
                    Spacer(modifier = Modifier.height(SpacingM))
                    
                    PrimaryButton(text = "Поделиться с друзьями", onClick = {})
                    Spacer(modifier = Modifier.height(SpacingM))
                    SecondaryButton(text = "Отправить в WhatsApp", onClick = {})
                    Spacer(modifier = Modifier.height(SpacingM))
                    SecondaryButton(text = "Отправить в Telegram", onClick = {})
                    
                    Spacer(modifier = Modifier.height(SpacingL))
                }
                
                // How it Works
                item {
                    Text("КАК ЭТО РАБОТАЕТ", style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                items(3) { index ->
                    val steps = listOf(
                        "Поделитесь кодом" to "Отправьте ваш код друзьям",
                        "Друг регистрируется" to "Друг использует код при регистрации",
                        "Получите бонус" to "Вы получаете 500₽, друг скидку 20%"
                    )
                    StepCard(number = index + 1, title = steps[index].first, description = steps[index].second)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                // Referrals List
                item {
                    Text("ВАШИ ПРИГЛАШЕНИЯ", style = MaterialTheme.typography.headlineSmall, color = TextPrimary)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
                
                items(referrals) { referral ->
                    ReferralRow(referral = referral)
                    Spacer(modifier = Modifier.height(SpacingM))
                }
            }
        }
    }
}

@Composable
fun StepCard(number: Int, title: String, description: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .cardBackground()
            .padding(SpacingM),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text("$number", style = MaterialTheme.typography.headlineLarge, color = SecondaryGold, modifier = Modifier.size(50.dp).background(SurfaceDark).wrapContentSize())
        Spacer(modifier = Modifier.width(SpacingM))
        Column(modifier = Modifier.weight(1f)) {
            Text(title, style = MaterialTheme.typography.labelMedium, color = TextPrimary)
            Text(description, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
        }
    }
}

@Composable
fun ReferralRow(referral: Referral) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .cardBackground()
            .padding(SpacingM)
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(referral.name, style = MaterialTheme.typography.labelMedium, color = TextPrimary)
            Text(referral.date, style = MaterialTheme.typography.bodySmall, color = TextTertiary)
        }
        Column(horizontalAlignment = Alignment.End) {
            Text("+${referral.bonus}₽", style = MaterialTheme.typography.labelMedium, color = referral.status.color)
            Text(referral.status.text, style = MaterialTheme.typography.bodySmall, color = referral.status.color)
        }
    }
}



