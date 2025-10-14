package family.aladdin.android.ui.components.modals

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import family.aladdin.android.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun ConsentModal(
    onDismiss: () -> Unit = { /* Modal cannot be dismissed */ },
    onAccept: () -> Unit,
    onReadMore: () -> Unit
) {
    val scope = rememberCoroutineScope()
    var isAnimating by remember { mutableStateOf(false) }
    
    LaunchedEffect(Unit) {
        isAnimating = true
    }
    
    Dialog(
        onDismissRequest = { /* Нельзя закрыть свайпом */ },
        properties = DialogProperties(
            dismissOnBackPress = false,
            dismissOnClickOutside = false,
            usePlatformDefaultWidth = false
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.85f))
                .blur(if (isAnimating) 0.dp else 20.dp),
            contentAlignment = Alignment.Center
        ) {
            AnimatedVisibility(
                visible = isAnimating,
                enter = fadeIn(animationSpec = tween(400)) + 
                        scaleIn(initialScale = 0.8f, animationSpec = tween(400)) +
                        slideInVertically(initialOffsetY = { 50 }, animationSpec = tween(400)),
                exit = fadeOut() + scaleOut()
            ) {
                ConsentContent(
                    onAccept = {
                        isAnimating = false
                        scope.launch {
                            delay(300)
                            onAccept()
                        }
                    },
                    onReadMore = onReadMore
                )
            }
        }
    }
}

@Composable
private fun ConsentContent(
    onAccept: () -> Unit,
    onReadMore: () -> Unit
) {
    // Пульсация лого
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val logoScale by infiniteTransition.animateFloat(
        initialValue = 1.0f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = EaseInOut),
            repeatMode = RepeatMode.Reverse
        ),
        label = "logoScale"
    )
    
    Column(
        modifier = Modifier
            .padding(horizontal = 16.dp)
            .widthIn(max = 340.dp)
            .shadow(
                elevation = 30.dp,
                shape = RoundedCornerShape(20.dp),
                ambientColor = Color.Black.copy(alpha = 0.5f)
            )
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF0F172A),
                        Color(0xFF1E3A8A),
                        Color(0xFF3B82F6)
                    )
                ),
                shape = RoundedCornerShape(20.dp)
            )
            .border(
                width = 2.dp,
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFFFCD34D).copy(alpha = 0.5f),
                        Color(0xFFF59E0B).copy(alpha = 0.3f)
                    )
                ),
                shape = RoundedCornerShape(20.dp)
            )
            .padding(25.dp)
    ) {
        // Заголовок
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(
                text = "🛡️",
                fontSize = 48.sp,
                modifier = Modifier.scale(logoScale)
            )
            
            Spacer(modifier = Modifier.height(10.dp))
            
            Text(
                text = "ALADDIN",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFCD34D)
            )
            
            Spacer(modifier = Modifier.height(5.dp))
            
            Text(
                text = "Добро пожаловать в систему\nсемейной безопасности!",
                fontSize = 13.sp,
                color = Color.White.copy(alpha = 0.8f),
                textAlign = TextAlign.Center,
                lineHeight = 18.sp
            )
        }
        
        Spacer(modifier = Modifier.height(20.dp))
        
        // Прокручиваемый контент
        Column(
            modifier = Modifier
                .heightIn(max = 280.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // ❌ Что НЕ собираем
            NotCollectingSection()
            
            // ✅ Военные технологии
            MilitaryTechSection()
            
            // 🛡️ Гарантии
            GuaranteesSection()
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // Кнопки
        ButtonsSection(
            onAccept = onAccept,
            onReadMore = onReadMore
        )
        
        Spacer(modifier = Modifier.height(10.dp))
        
        // Юридический текст
        LegalText(onReadMore = onReadMore)
    }
}

@Composable
private fun NotCollectingSection() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = Color.Black.copy(alpha = 0.3f),
                shape = RoundedCornerShape(12.dp)
            )
            .padding(15.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Text(
            text = "❌ Мы НЕ собираем ваши данные:",
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
            color = Color(0xFFFCD34D)
        )
        
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text("• Имя, email, телефон", fontSize = 12.sp, color = Color.White.copy(alpha = 0.9f))
            Text("• Адрес, паспортные данные", fontSize = 12.sp, color = Color.White.copy(alpha = 0.9f))
            Text("• История посещений", fontSize = 12.sp, color = Color.White.copy(alpha = 0.9f))
            Text("• Личные сообщения", fontSize = 12.sp, color = Color.White.copy(alpha = 0.9f))
        }
    }
}

@Composable
private fun MilitaryTechSection() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF10B981).copy(alpha = 0.15f),
                        Color(0xFF059669).copy(alpha = 0.10f)
                    )
                ),
                shape = RoundedCornerShape(12.dp)
            )
            .border(
                width = 1.dp,
                color = Color(0xFF10B981),
                shape = RoundedCornerShape(12.dp)
            )
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text(
            text = "✅ Военные технологии защиты:",
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF10B981)
        )
        
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("🆔 Только персональный ID номер", fontSize = 11.sp, color = Color.White.copy(alpha = 0.9f))
            Text("🔐 AES-256-GCM (банковский сейф А+)", fontSize = 11.sp, color = Color.White.copy(alpha = 0.9f))
            Text("🔒 ChaCha20-Poly1305 (защита ⭐⭐⭐⭐⭐)", fontSize = 11.sp, color = Color.White.copy(alpha = 0.9f))
            Text("🛡️ XChaCha20-Poly1305 (космический уровень)", fontSize = 11.sp, color = Color.White.copy(alpha = 0.9f))
            Text("🇷🇺 Российские серверы (152-ФЗ РФ)", fontSize = 11.sp, color = Color.White.copy(alpha = 0.9f))
            Text("📊 Обезличенная статистика", fontSize = 11.sp, color = Color.White.copy(alpha = 0.9f))
        }
    }
}

@Composable
private fun GuaranteesSection() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = Color.Black.copy(alpha = 0.2f),
                shape = RoundedCornerShape(12.dp)
            )
            .padding(15.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text(
            text = "🛡️ Наши гарантии:",
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF10B981)
        )
        
        Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
            Text("✅ Полная анонимность", fontSize = 11.sp, color = Color.White.copy(alpha = 0.9f))
            Text("✅ Шифрование E2E (сквозное)", fontSize = 11.sp, color = Color.White.copy(alpha = 0.9f))
            Text("✅ Zero-logs VPN (нет логов)", fontSize = 11.sp, color = Color.White.copy(alpha = 0.9f))
            Text("✅ Соответствие 152-ФЗ", fontSize = 11.sp, color = Color.White.copy(alpha = 0.9f))
        }
    }
}

@Composable
private fun ButtonsSection(
    onAccept: () -> Unit,
    onReadMore: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        // Кнопка "Подробнее"
        Button(
            onClick = onReadMore,
            modifier = Modifier
                .weight(1f)
                .height(48.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.White.copy(alpha = 0.1f)
            ),
            shape = RoundedCornerShape(12.dp),
            border = androidx.compose.foundation.BorderStroke(
                width = 1.dp,
                color = Color.White.copy(alpha = 0.3f)
            )
        ) {
            Text(
                text = "Подробнее",
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                color = Color.White
            )
        }
        
        // Кнопка "Принять ✓"
        Button(
            onClick = onAccept,
            modifier = Modifier
                .weight(1f)
                .height(48.dp)
                .shadow(
                    elevation = 15.dp,
                    shape = RoundedCornerShape(12.dp),
                    ambientColor = Color(0xFFF59E0B).copy(alpha = 0.5f)
                ),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.Transparent
            ),
            shape = RoundedCornerShape(12.dp),
            contentPadding = PaddingValues(0.dp)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        brush = Brush.linearGradient(
                            colors = listOf(
                                Color(0xFFFCD34D),
                                Color(0xFFF59E0B),
                                Color(0xFFD97706)
                            )
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "Принять ✓",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            }
        }
    }
}

@Composable
private fun LegalText(onReadMore: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = Color.Black.copy(alpha = 0.2f),
                shape = RoundedCornerShape(8.dp)
            )
            .padding(10.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Нажимая кнопку \"Принять\", вы подтверждаете,",
            fontSize = 10.sp,
            color = Color.White.copy(alpha = 0.7f),
            textAlign = TextAlign.Center
        )
        
        val annotatedText = buildAnnotatedString {
            withStyle(style = SpanStyle(color = Color.White.copy(alpha = 0.7f))) {
                append("что ознакомлены и согласны с ")
            }
            
            pushStringAnnotation(tag = "POLICY", annotation = "policy")
            withStyle(
                style = SpanStyle(
                    color = Color(0xFF3B82F6),
                    textDecoration = TextDecoration.Underline
                )
            ) {
                append("Политикой конфиденциальности")
            }
            pop()
            
            withStyle(style = SpanStyle(color = Color.White.copy(alpha = 0.7f))) {
                append(" системы семейной безопасности ALADDIN и Политикой обработки данных VPN-сервиса в соответствии с требованиями ")
            }
            
            withStyle(style = SpanStyle(color = Color.White.copy(alpha = 0.7f), fontWeight = FontWeight.Bold)) {
                append("Федерального закона от 27.07.2006 № 152-ФЗ \"О персональных данных\" (статья 9)")
            }
        }
        
        Text(
            text = annotatedText,
            fontSize = 10.sp,
            textAlign = TextAlign.Center,
            lineHeight = 14.sp,
            modifier = Modifier.clickable {
                // Handle click on "Политикой конфиденциальности"
                onReadMore()
            }
        )
    }
}



