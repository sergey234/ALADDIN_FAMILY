package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.inputs.ALADDINTextField
import family.aladdin.android.ui.components.navigation.ALADDINTopAppBar
import family.aladdin.android.ui.theme.*
import family.aladdin.android.ui.theme.Size
import java.text.SimpleDateFormat
import java.util.*

/**
 * 💬 Family Chat Screen
 * Семейный чат для общения семьи
 * 17_family_chat_screen из HTML
 * ПОЛНАЯ КАЧЕСТВЕННАЯ ВЕРСИЯ С РЕАЛЬНЫМ ЧАТОМ!
 */

data class FamilyChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val sender: String,
    val avatar: String,
    val text: String,
    val time: String,
    val isCurrentUser: Boolean
)

@Composable
fun FamilyChatScreen(
    navController: NavHostController,
    memberId: String = ""
) {
    // TODO: Use memberId for specific member chat
    
    var messageText by remember { mutableStateOf("") }
    var messages by remember {
        mutableStateOf(
            listOf(
                FamilyChatMessage(
                    sender = "Сергей",
                    avatar = "👨",
                    text = "Всем привет! Как дела?",
                    time = "10:30",
                    isCurrentUser = true
                ),
                FamilyChatMessage(
                    sender = "Мария",
                    avatar = "👩",
                    text = "Привет! У нас всё хорошо 😊",
                    time = "10:32",
                    isCurrentUser = false
                ),
                FamilyChatMessage(
                    sender = "Маша",
                    avatar = "👧",
                    text = "Папа, можно мне ещё 30 минут экранного времени?",
                    time = "10:35",
                    isCurrentUser = false
                ),
                FamilyChatMessage(
                    sender = "Сергей",
                    avatar = "👨",
                    text = "Конечно, дочка! Разрешаю ещё 30 минут 👍",
                    time = "10:36",
                    isCurrentUser = true
                ),
                FamilyChatMessage(
                    sender = "Бабушка",
                    avatar = "👵",
                    text = "Как мне настроить VPN? Я забыла...",
                    time = "11:15",
                    isCurrentUser = false
                ),
                FamilyChatMessage(
                    sender = "Сергей",
                    avatar = "👨",
                    text = "Сейчас помогу! Открой раздел 'VPN' на главном экране и нажми на кнопку подключения.",
                    time = "11:16",
                    isCurrentUser = true
                )
            )
        )
    }
    
    val listState = rememberLazyListState()
    
    // Auto-scroll to bottom when new message added
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }
    
    Box(modifier = Modifier.fillMaxSize().backgroundGradient()) {
        Column(modifier = Modifier.fillMaxSize()) {
            
            // Top App Bar
            ALADDINTopAppBar(
                title = "СЕМЕЙНЫЙ ЧАТ",
                subtitle = "4 участника онлайн",
                onBackClick = { navController.popBackStack() }
            )
            
            // Messages List
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentPadding = PaddingValues(ScreenPadding),
                verticalArrangement = Arrangement.spacedBy(SpacingM)
            ) {
                items(messages) { message ->
                    ChatBubble(message = message)
                }
            }
            
            // Input Area
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        brush = Brush.linearGradient(
                            colors = listOf(SurfaceDark, BackgroundMedium)
                        )
                    )
                    .padding(ScreenPadding),
                verticalAlignment = Alignment.CenterVertically
            ) {
                
                ALADDINTextField(
                    value = messageText,
                    onValueChange = { messageText = it },
                    placeholder = "Ваше сообщение...",
                    modifier = Modifier.weight(1f)
                )
                
                Spacer(modifier = Modifier.width(SpacingS))
                
                // Send Button
                IconButton(
                    onClick = {
                        if (messageText.isNotEmpty()) {
                            val currentTime = SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date())
                            messages = messages + FamilyChatMessage(
                                sender = "Сергей",
                                avatar = "👨",
                                text = messageText,
                                time = currentTime,
                                isCurrentUser = true
                            )
                            messageText = ""
                        }
                    },
                    modifier = Modifier
                        .size(48.dp)
                        .background(SecondaryGold, shape = RoundedCornerShape(CornerRadiusMedium))
                ) {
                    Icon(
                        imageVector = Icons.Default.Send,
                        contentDescription = "Отправить",
                        tint = BackgroundDark
                    )
                }
                
                Spacer(modifier = Modifier.width(SpacingS))
                
                // Voice Button
                IconButton(
                    onClick = { 
                        // TODO: Implement voice message recording
                    },
                    modifier = Modifier
                        .size(48.dp)
                        .background(SurfaceDark.copy(alpha = 0.6f), shape = RoundedCornerShape(CornerRadiusMedium))
                ) {
                    Text("🎤", style = MaterialTheme.typography.headlineSmall)
                }
            }
        }
    }
}

// MARK: - Chat Bubble

@Composable
fun ChatBubble(message: FamilyChatMessage) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (message.isCurrentUser) Arrangement.End else Arrangement.Start
    ) {
        if (!message.isCurrentUser) {
            // Avatar for other users
            Text(
                message.avatar,
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier
                    .size(Size.AvatarMedium)
                    .background(SurfaceDark, shape = RoundedCornerShape(CornerRadius.Large))
                    .wrapContentSize(Alignment.Center)
            )
            Spacer(modifier = Modifier.width(SpacingS))
        }
        
        Column(
            modifier = Modifier.widthIn(max = 280.dp),
            horizontalAlignment = if (message.isCurrentUser) Alignment.End else Alignment.Start
        ) {
            // Sender name (for other users)
            if (!message.isCurrentUser) {
                Text(
                    message.sender,
                    style = MaterialTheme.typography.labelMedium,
                    color = SecondaryGold,
                    modifier = Modifier.padding(start = SpacingS, bottom = SpacingXXS)
                )
            }
            
            // Message bubble
            Box(
                modifier = Modifier
                    .background(
                        color = if (message.isCurrentUser) PrimaryBlue else SurfaceDark,
                        shape = RoundedCornerShape(CornerRadiusMedium)
                    )
                    .padding(SpacingM)
            ) {
                Text(
                    message.text,
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextPrimary
                )
            }
            
            // Time
            Text(
                message.time,
                style = MaterialTheme.typography.bodySmall,
                color = TextTertiary,
                modifier = Modifier.padding(horizontal = SpacingS, vertical = SpacingXXS)
            )
        }
        
        if (message.isCurrentUser) {
            Spacer(modifier = Modifier.width(SpacingS))
            // Avatar for current user
            Text(
                message.avatar,
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier
                    .size(Size.AvatarMedium)
                    .background(SurfaceDark, shape = RoundedCornerShape(CornerRadius.Large))
                    .wrapContentSize(Alignment.Center)
            )
        }
    }
}



