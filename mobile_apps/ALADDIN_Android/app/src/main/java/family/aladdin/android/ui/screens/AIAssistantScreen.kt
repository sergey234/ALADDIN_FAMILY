package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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

data class ChatMessage(val text: String, val isUser: Boolean, val time: String)

@Composable
fun AIAssistantScreen(navController: NavHostController) {
    var messageText by remember { mutableStateOf("") }
    val messages = remember {
        mutableStateListOf(
            ChatMessage("Здравствуйте! Я AI помощник ALADDIN. Чем могу помочь?", false, "14:30"),
            ChatMessage("Покажи статистику защиты", true, "14:31")
        )
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            ALADDINTopBar(
                title = "AI ПОМОЩНИК",
                subtitle = "Всегда готов помочь",
                onBackClick = { navController.popBackStack() },
                actions = {
                    TopBarAction(icon = Icons.Default.Mic, onClick = {})
                }
            )
            
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .padding(Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.M)
            ) {
                items(messages) { message ->
                    ChatBubble(message)
                }
            }
            
            // Ввод сообщения
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(BackgroundDark.copy(alpha = 0.95f))
                    .padding(Spacing.M),
                horizontalArrangement = Arrangement.spacedBy(Spacing.S)
            ) {
                TextField(
                    value = messageText,
                    onValueChange = { messageText = it },
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("Спросите AI...") }
                )
                
                IconButton(
                    onClick = {
                        if (messageText.isNotEmpty()) {
                            messages.add(ChatMessage(messageText, true, "Now"))
                            messageText = ""
                        }
                    }
                ) {
                    Icon(Icons.Default.Send, contentDescription = "Send")
                }
            }
        }
    }
}

@Composable
private fun ChatBubble(message: ChatMessage) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (message.isUser) Arrangement.End else Arrangement.Start
    ) {
        Surface(
            shape = RoundedCornerShape(CornerRadius.Large),
            color = if (message.isUser)
                PrimaryBlue
            else
                BackgroundMedium
        ) {
            Column(modifier = Modifier.padding(Spacing.M)) {
                Text(message.text, color = TextPrimary)
                Text(message.time, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            }
        }
    }
}



