package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.buttons.PrimaryButton
import family.aladdin.android.ui.theme.*
import kotlinx.coroutines.launch

data class OnboardingPage(val icon: String, val title: String, val description: String)

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun OnboardingScreen(
    navController: NavHostController,
    onComplete: () -> Unit = {},
    onJoinFamily: () -> Unit = {},
    onRecovery: () -> Unit = {}
) {
    // TODO: Use navController for navigation
    val pages = listOf(
        OnboardingPage("🛡️", "ЗАЩИТА СЕМЬИ", "Комплексная защита для всей вашей семьи"),
        OnboardingPage("🤖", "AI ПОМОЩНИК", "Умный ассистент всегда готов помочь"),
        OnboardingPage("👶", "РОДИТЕЛЬСКИЙ КОНТРОЛЬ", "Полный контроль над устройствами детей"),
        OnboardingPage("📊", "АНАЛИТИКА", "Подробная статистика угроз")
    )
    
    val pagerState = rememberPagerState(pageCount = { pages.size })
    val scope = rememberCoroutineScope()
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Skip button
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(Spacing.M),
                horizontalArrangement = Arrangement.End
            ) {
                TextButton(onClick = onComplete) {
                    Text("Пропустить", color = TextSecondary)
                }
            }
            
            // Pages
            HorizontalPager(
                state = pagerState,
                modifier = Modifier.weight(1f)
            ) { page ->
                OnboardingPageContent(pages[page])
            }
            
            // Indicators
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = Spacing.L),
                horizontalArrangement = Arrangement.Center
            ) {
                repeat(pages.size) { index ->
                    Box(
                        modifier = Modifier
                            .size(if (pagerState.currentPage == index) 12.dp else 8.dp)
                            .background(
                                if (pagerState.currentPage == index) PrimaryBlue else TextSecondary.copy(alpha = 0.3f),
                                CircleShape
                            )
                    )
                    if (index < pages.size - 1) Spacer(modifier = Modifier.width(Spacing.S))
                }
            }
            
            // Buttons
            Column(
                modifier = Modifier.padding(Spacing.ScreenPadding).padding(bottom = Spacing.XL),
                verticalArrangement = Arrangement.spacedBy(SpacingM)
            ) {
                // Main button
                PrimaryButton(
                    text = if (pagerState.currentPage < pages.size - 1) "ПРОДОЛЖИТЬ" else "НАЧАТЬ",
                    onClick = {
                        if (pagerState.currentPage < pages.size - 1) {
                            scope.launch {
                                pagerState.animateScrollToPage(pagerState.currentPage + 1)
                            }
                        } else {
                            onComplete()
                        }
                    }
                )
                
                // Additional buttons on last slide
                if (pagerState.currentPage == pages.size - 1) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(SpacingM)
                    ) {
                        // Join family button
                        androidx.compose.material3.OutlinedButton(
                            onClick = onJoinFamily,
                            modifier = Modifier.weight(1f).height(44.dp),
                            colors = androidx.compose.material3.ButtonDefaults.outlinedButtonColors(
                                containerColor = Color(0xFFFCD34D).copy(alpha = 0.15f),  // Золото!
                                contentColor = Color(0xFFFCD34D)
                            ),
                            border = androidx.compose.foundation.BorderStroke(0.dp, Color.Transparent),
                            shape = RoundedCornerShape(CornerRadiusMedium)
                        ) {
                            Text(
                                "У МЕНЯ ЕСТЬ КОД",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        
                        // Recovery button
                        androidx.compose.material3.OutlinedButton(
                            onClick = onRecovery,
                            modifier = Modifier.weight(1f).height(44.dp),
                            colors = androidx.compose.material3.ButtonDefaults.outlinedButtonColors(
                                containerColor = Color(0xFF60A5FA).copy(alpha = 0.15f),  // Электрический синий!
                                contentColor = Color(0xFF60A5FA)
                            ),
                            border = androidx.compose.foundation.BorderStroke(0.dp, Color.Transparent),
                            shape = RoundedCornerShape(CornerRadiusMedium)
                        ) {
                            Text(
                                "ВОССТАНОВИТЬ",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun OnboardingPageContent(page: OnboardingPage) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(Spacing.XL),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(page.icon, style = MaterialTheme.typography.displayLarge.copy(fontSize = 80.sp))
        Spacer(modifier = Modifier.height(Spacing.XL))
        Text(page.title, style = MaterialTheme.typography.displayLarge.copy(fontSize = 32.sp), color = Color.White)
        Spacer(modifier = Modifier.height(Spacing.M))
        Text(page.description, style = MaterialTheme.typography.bodyLarge.copy(fontSize = 18.sp), color = TextSecondary)
    }
}

