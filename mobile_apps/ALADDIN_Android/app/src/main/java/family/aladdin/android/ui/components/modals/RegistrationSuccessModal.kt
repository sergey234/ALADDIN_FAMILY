package family.aladdin.android.ui.components.modals

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import family.aladdin.android.models.FamilyMember
import family.aladdin.android.ui.components.buttons.PrimaryButton
import family.aladdin.android.ui.theme.*

/**
 * 🎉 Registration Success Modal
 * Модальное окно успешного присоединения/восстановления
 * Окно #8 - показывает список членов семьи
 * 
 * РАЗМЕРЫ (проверено):
 * - Modal width: 340dp
 * - Modal height: 360dp
 * - Celebration icon: 80sp с анимацией bounce
 */

@Composable
fun RegistrationSuccessModal(
    mode: SuccessMode,
    familyMembers: List<FamilyMember>,
    onContinue: () -> Unit,
    onDismiss: () -> Unit = { /* Modal cannot be dismissed */ }
) {
    // Bounce animation for celebration icon
    val infiniteTransition = rememberInfiniteTransition(label = "bounce")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(600, easing = EaseInOutCubic),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )
    
    Dialog(
        onDismissRequest = { /* Нельзя закрыть свайпом */ },
        properties = DialogProperties(
            dismissOnBackPress = false,
            dismissOnClickOutside = false
        )
    ) {
        Card(
            modifier = Modifier
                .width(340.dp)
                .wrapContentHeight(),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.Transparent
            )
        ) {
            Box(
                modifier = Modifier
                    .background(
                        Brush.linearGradient(
                            colors = listOf(
                                Color(0xFF0F172A),  // Космический тёмный
                                Color(0xFF1E3A8A),  // Глубокий синий
                                Color(0xFF3B82F6),  // Электрический синий
                                Color(0xFF1E40AF)   // Королевский синий
                            )
                        )
                    )
                    .padding(24.dp)
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(SpacingXL)
                ) {
                    // Celebration icon with animation
                    Text(
                        text = "🎉",
                        fontSize = 80.sp,
                        modifier = Modifier.scale(scale)
                    )
                    
                    // Title
                    Text(
                        text = mode.title,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = SuccessGreen
                    )
                    
                    // Family members list
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(SpacingS)
                    ) {
                        Text(
                            text = "👥 Ваша семья:",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = TextPrimary
                        )
                        
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(
                                    Color.White.copy(alpha = 0.05f),
                                    RoundedCornerShape(12.dp)
                                )
                                .padding(SpacingM),
                            verticalArrangement = Arrangement.spacedBy(SpacingS)
                        ) {
                            familyMembers.forEach { member ->
                                FamilyMemberRow(
                                    member = member,
                                    isCurrentUser = member.isYou
                                )
                            }
                        }
                    }
                    
                    // Continue button
                    PrimaryButton(
                        text = "НАЧАТЬ ИСПОЛЬЗОВАНИЕ 🚀",
                        onClick = onContinue
                    )
                }
            }
        }
    }
}

enum class SuccessMode(val title: String) {
    FAMILY_CREATED("СЕМЬЯ СОЗДАНА!"),
    JOINED("ВЫ ПРИСОЕДИНИЛИСЬ!"),
    RECOVERED("ДОСТУП ВОССТАНОВЛЕН!")
}

@Composable
fun FamilyMemberRow(
    member: FamilyMember,
    isCurrentUser: Boolean
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(36.dp),
        horizontalArrangement = Arrangement.spacedBy(SpacingM),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Icon
        Text(
            text = member.role.icon,
            fontSize = 24.sp
        )
        
        // Info
        Row(
            horizontalArrangement = Arrangement.spacedBy(SpacingXS),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = member.letter,
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFCD34D)  // Яркое золото из иконки!
            )
            
            Text("-", color = TextSecondary)
            
            Text(
                text = member.role.displayName,
                fontSize = 14.sp,
                color = TextPrimary
            )
            
            Text(
                text = "(${member.ageGroup.value})",
                fontSize = 12.sp,
                color = TextSecondary
            )
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        // Current user badge
        if (isCurrentUser) {
            Text(
                text = "⭐ Вы!",
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFCD34D),  // Золото!
                modifier = Modifier
                    .background(
                        Color(0xFFFCD34D).copy(alpha = 0.2f),
                        RoundedCornerShape(6.dp)
                    )
                    .padding(horizontal = SpacingS, vertical = 4.dp)
            )
        }
    }
}

// Extension для FamilyRole
val family.aladdin.android.models.FamilyRole.icon: String
    get() = when (this) {
        family.aladdin.android.models.FamilyRole.PARENT -> "👨‍👩‍👧‍👦"
        family.aladdin.android.models.FamilyRole.CHILD -> "👶"
        family.aladdin.android.models.FamilyRole.ELDERLY -> "👴"
        family.aladdin.android.models.FamilyRole.OTHER -> "👤"
    }

val family.aladdin.android.models.FamilyRole.displayName: String
    get() = when (this) {
        family.aladdin.android.models.FamilyRole.PARENT -> "Родитель"
        family.aladdin.android.models.FamilyRole.CHILD -> "Ребёнок"
        family.aladdin.android.models.FamilyRole.ELDERLY -> "Пожилой"
        family.aladdin.android.models.FamilyRole.OTHER -> "Другой"
    }



