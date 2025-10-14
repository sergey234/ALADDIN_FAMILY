package family.aladdin.android.ui.components.modals

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import family.aladdin.android.models.FamilyRole
import family.aladdin.android.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * 👋 Role Selection Modal
 * Модальное окно выбора роли в семье
 * Окно #1 в процессе регистрации
 */

@Composable
fun RoleSelectionModal(
    onRoleSelected: (FamilyRole) -> Unit,
    onDismiss: () -> Unit = { /* Modal cannot be dismissed */ }
) {
    var selectedRole by remember { mutableStateOf<FamilyRole?>(null) }
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
                    // Header
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(SpacingM)
                    ) {
                        Text(
                            text = "👋",
                            fontSize = 40.sp
                        )
                        
                        Text(
                            text = "Добро пожаловать!",
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFFFCD34D)  // Яркое золото из иконки!
                        )
                        
                        Text(
                            text = "Кто вы в семье?",
                            fontSize = 16.sp,
                            color = TextPrimary
                        )
                    }
                    
                    // Role cards
                    Column(verticalArrangement = Arrangement.spacedBy(SpacingM)) {
                        Row(horizontalArrangement = Arrangement.spacedBy(SpacingM)) {
                            RoleCard(
                                icon = "👨‍👩‍👧‍👦",
                                title = "РОДИТЕЛЬ",
                                features = listOf("Полный доступ", "Контроль семьи"),
                                isSelected = selectedRole == FamilyRole.PARENT,
                                onClick = {
                                    selectedRole = FamilyRole.PARENT
                                    scope.launch {
                                        delay(300)
                                        onRoleSelected(FamilyRole.PARENT)
                                    }
                                }
                            )
                            
                            RoleCard(
                                icon = "👶",
                                title = "РЕБЁНОК",
                                features = listOf("Детский режим", "Безопасность"),
                                isSelected = selectedRole == FamilyRole.CHILD,
                                onClick = {
                                    selectedRole = FamilyRole.CHILD
                                    scope.launch {
                                        delay(300)
                                        onRoleSelected(FamilyRole.CHILD)
                                    }
                                }
                            )
                        }
                        
                        Row(horizontalArrangement = Arrangement.spacedBy(SpacingM)) {
                            RoleCard(
                                icon = "👴",
                                title = "ЛЮДИ 60+",
                                features = listOf("Упрощённый UI", "Большие кнопки"),
                                isSelected = selectedRole == FamilyRole.ELDERLY,
                                onClick = {
                                    selectedRole = FamilyRole.ELDERLY
                                    scope.launch {
                                        delay(300)
                                        onRoleSelected(FamilyRole.ELDERLY)
                                    }
                                }
                            )
                            
                    RoleCard(
                        icon = "👤",
                        title = "ЧЕЛОВЕК",
                                features = listOf("Стандартный", "Полный доступ"),
                                isSelected = selectedRole == FamilyRole.OTHER,
                                onClick = {
                                    selectedRole = FamilyRole.OTHER
                                    scope.launch {
                                        delay(300)
                                        onRoleSelected(FamilyRole.OTHER)
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
fun RoleCard(
    icon: String,
    title: String,
    features: List<String>,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .width(140.dp)  // Исправлено: 140dp вместо 148dp (чтобы помещалось!)
            .height(160.dp)
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) 
                Color(0xFF60A5FA).copy(alpha = 0.3f)  // Электрический синий из иконки!
            else 
                Color.White.copy(alpha = 0.1f)
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isSelected) 8.dp else 0.dp
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(SpacingM),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(SpacingM)
        ) {
            Text(
                text = icon,
                fontSize = 60.sp
            )
            
            Text(
                text = title,
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                textAlign = TextAlign.Center
            )
            
            Column(
                verticalArrangement = Arrangement.spacedBy(SpacingXS)
            ) {
                features.forEach { feature ->
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "•",
                            fontSize = 12.sp,
                            color = TextSecondary
                        )
                        Text(
                            text = feature,
                            fontSize = 12.sp,
                            color = TextSecondary
                        )
                    }
                }
            }
        }
    }
}

