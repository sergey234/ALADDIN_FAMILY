package family.aladdin.android.ui.components.modals

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import family.aladdin.android.models.AgeGroup
import family.aladdin.android.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * 🎂 Age Group Selection Modal
 * Модальное окно выбора возрастной группы
 * Окно #2 в процессе регистрации
 * 
 * РАЗМЕРЫ (проверено на переполнение):
 * - Modal width: 340dp (safe для 360dp экранов)
 * - Modal height: 420dp (safe для 640dp экранов)
 * - Padding: 24dp (внутренний отступ)
 * - Each option height: 40dp
 * - Gap between options: 12dp
 * - Total content: ~400dp (безопасно!)
 */

@Composable
fun AgeGroupSelectionModal(
    onAgeGroupSelected: (AgeGroup) -> Unit,
    onDismiss: () -> Unit = { /* Modal cannot be dismissed */ }
) {
    var selectedAgeGroup by remember { mutableStateOf<AgeGroup?>(null) }
    val scope = rememberCoroutineScope()
    
    Dialog(
        onDismissRequest = { /* НЕЛЬЗЯ ЗАКРЫТЬ! */ },
        properties = DialogProperties(
            dismissOnBackPress = false,
            dismissOnClickOutside = false
        )
    ) {
        Card(
            modifier = Modifier
                .width(340.dp)  // Безопасно для всех экранов (min 360dp)
                .wrapContentHeight()
                .heightIn(max = 420.dp),  // Максимальная высота
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
                    .padding(24.dp)  // Внутренний отступ
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(SpacingXL)
                ) {
                    // Header
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(SpacingM)
                    ) {
                        Text(
                            text = "🎂",
                            fontSize = 40.sp
                        )
                        
                        Text(
                            text = "Ваша возрастная группа?",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFFFCD34D)  // Яркое золото из иконки!
                        )
                        
                        Text(
                            text = "(Для подбора защиты)",
                            fontSize = 14.sp,
                            color = TextSecondary
                        )
                    }
                    
                    // Age options
                    Column(
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        AgeGroup.values().forEach { ageGroup ->
                            AgeOption(
                                ageGroup = ageGroup,
                                isSelected = selectedAgeGroup == ageGroup,
                                onClick = {
                                    selectedAgeGroup = ageGroup
                                    scope.launch {
                                        delay(300)
                                        onAgeGroupSelected(ageGroup)
                                    }
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun AgeOption(
    ageGroup: AgeGroup,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()  // Заполняет ширину родителя (340dp - 48dp padding = 292dp)
            .height(40.dp)  // Фиксированная высота
        .background(
            if (isSelected)
                Color(0xFF60A5FA).copy(alpha = 0.2f)  // Электрический синий!
            else
                Color.White.copy(alpha = 0.05f),
            shape = RoundedCornerShape(12.dp)
        )
        .border(
            width = if (isSelected) 2.dp else 1.dp,
            color = if (isSelected) Color(0xFFBAE6FD) else Color.White.copy(alpha = 0.1f),  // Sirius голубой!
            shape = RoundedCornerShape(12.dp)
        )
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp),  // Внутренний padding для текста
        horizontalArrangement = Arrangement.spacedBy(SpacingM),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Radio button
        Box(
            modifier = Modifier
                .size(24.dp)
                .clip(CircleShape)
                .border(
            width = 2.dp,
            color = if (isSelected) Color(0xFF60A5FA) else Color.White.copy(alpha = 0.3f),  // Электрический синий!
            shape = CircleShape
        ),
        contentAlignment = Alignment.Center
    ) {
        if (isSelected) {
            Box(
                modifier = Modifier
                    .size(14.dp)
                    .clip(CircleShape)
                    .background(Color(0xFF60A5FA))  // Электрический синий!
            )
        }
    }
        
        // Text
        Column(
            verticalArrangement = Arrangement.spacedBy(2.dp)
        ) {
            Text(
                text = ageGroup.display,
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = Color.White
            )
            
            Text(
                text = ageGroup.description,
                fontSize = 13.sp,
                color = TextSecondary
            )
        }
    }
}

