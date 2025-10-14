package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

data class ChatMessage(val text: String, val isUser: Boolean, val time: String)

class AIAssistantViewModel : ViewModel() {
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages
    
    init {
        _messages.value = listOf(
            ChatMessage("Здравствуйте! Я AI помощник ALADDIN.", false, "14:30")
        )
    }
    
    fun sendMessage(text: String) {
        val userMsg = ChatMessage(text, true, "Now")
        _messages.value = _messages.value + userMsg
    }
}



