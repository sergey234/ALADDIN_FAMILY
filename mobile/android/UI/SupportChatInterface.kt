package com.aladdin.mobile.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.*
import java.text.SimpleDateFormat
import java.util.*

// MARK: - Support Chat Interface для Android
class SupportChatInterface : AppCompatActivity() {
    
    // UI Components
    private lateinit var chatRecyclerView: RecyclerView
    private lateinit var messageInputView: LinearLayout
    private lateinit var messageEditText: EditText
    private lateinit var sendButton: Button
    private lateinit var quickActionsView: LinearLayout
    private lateinit var statusIndicator: View
    private lateinit var typingIndicator: ProgressBar
    
    // Properties
    private val messages = mutableListOf<SupportMessage>()
    private val supportAPI = UnifiedSupportAPIManager()
    private var isTyping = false
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_support_chat)
        
        setupUI()
        setupRecyclerView()
        setupClickListeners()
        loadInitialMessages()
    }
    
    private fun setupUI() {
        // Find views
        chatRecyclerView = findViewById(R.id.chatRecyclerView)
        messageInputView = findViewById(R.id.messageInputView)
        messageEditText = findViewById(R.id.messageEditText)
        sendButton = findViewById(R.id.sendButton)
        quickActionsView = findViewById(R.id.quickActionsView)
        statusIndicator = findViewById(R.id.statusIndicator)
        typingIndicator = findViewById(R.id.typingIndicator)
        
        // Setup appearance
        setupAppearance()
        setupQuickActions()
    }
    
    private fun setupAppearance() {
        // Set theme colors
        messageInputView.setBackgroundColor(StormSkyColors.backgroundSecondary)
        messageInputView.background = createRoundedBackground(StormSkyColors.backgroundSecondary)
        
        sendButton.setBackgroundColor(StormSkyColors.accent)
        sendButton.background = createRoundedBackground(StormSkyColors.accent)
        
        statusIndicator.setBackgroundColor(StormSkyColors.success)
        statusIndicator.background = createRoundedBackground(StormSkyColors.success)
        
        // Text colors
        messageEditText.setTextColor(StormSkyColors.textPrimary)
        messageEditText.hint = "Напишите ваш вопрос..."
        
        // Status indicator
        statusIndicator.visibility = View.VISIBLE
    }
    
    private fun setupQuickActions() {
        val actions = listOf(
            "🛡️ Безопасность" to "security",
            "👨‍👩‍👧‍👦 Семья" to "family", 
            "🔧 Настройки" to "settings",
            "❓ Помощь" to "help"
        )
        
        quickActionsView.removeAllViews()
        
        actions.forEach { (title, action) ->
            val button = Button(this).apply {
                text = title
                textSize = 12f
                setTextColor(StormSkyColors.textPrimary)
                setBackgroundColor(StormSkyColors.backgroundSecondary)
                background = createRoundedBackground(StormSkyColors.backgroundSecondary)
                setOnClickListener { sendQuickAction(action) }
            }
            
            val layoutParams = LinearLayout.LayoutParams(
                0, 
                LinearLayout.LayoutParams.WRAP_CONTENT, 
                1f
            ).apply {
                marginEnd = 8
            }
            
            quickActionsView.addView(button, layoutParams)
        }
    }
    
    private fun setupRecyclerView() {
        chatRecyclerView.layoutManager = LinearLayoutManager(this).apply {
            stackFromEnd = true
        }
        chatRecyclerView.adapter = SupportMessageAdapter(messages)
    }
    
    private fun setupClickListeners() {
        sendButton.setOnClickListener { sendMessage() }
        
        messageEditText.setOnEditorActionListener { _, _, _ ->
            sendMessage()
            true
        }
    }
    
    private fun sendMessage() {
        val text = messageEditText.text.toString().trim()
        if (text.isEmpty()) return
        
        val userMessage = SupportMessage(
            id = UUID.randomUUID().toString(),
            text = text,
            isFromUser = true,
            timestamp = Date(),
            category = "general"
        )
        
        addMessage(userMessage)
        messageEditText.text.clear()
        
        // Send to API
        sendToAPI(text)
    }
    
    private fun sendQuickAction(action: String) {
        val quickMessages = mapOf(
            "security" to "Расскажи о функциях безопасности ALADDIN",
            "family" to "Как настроить родительский контроль?",
            "settings" to "Помоги с настройками приложения",
            "help" to "Мне нужна помощь с приложением"
        )
        
        quickMessages[action]?.let { message ->
            messageEditText.setText(message)
            sendMessage()
        }
    }
    
    private fun sendToAPI(text: String) {
        showTypingIndicator(true)
        
        val request = SupportRequest(
            message = text,
            category = "general",
            priority = SupportPriority.MEDIUM,
            context = SupportContext(
                userID = "current_user",
                deviceInfo = "Android",
                appVersion = "1.0.0"
            )
        )
        
        scope.launch {
            try {
                val response = withContext(Dispatchers.IO) {
                    supportAPI.sendSupportRequest(request)
                }
                handleAPIResponse(response)
            } catch (e: Exception) {
                showError(e.message ?: "Ошибка отправки сообщения")
            } finally {
                showTypingIndicator(false)
            }
        }
    }
    
    private fun handleAPIResponse(response: SupportResponse) {
        val aiMessage = SupportMessage(
            id = UUID.randomUUID().toString(),
            text = response.message,
            isFromUser = false,
            timestamp = Date(),
            category = response.category ?: "general"
        )
        
        addMessage(aiMessage)
    }
    
    private fun addMessage(message: SupportMessage) {
        messages.add(message)
        chatRecyclerView.adapter?.notifyItemInserted(messages.size - 1)
        chatRecyclerView.scrollToPosition(messages.size - 1)
    }
    
    private fun loadInitialMessages() {
        val welcomeMessage = SupportMessage(
            id = "welcome",
            text = "👋 Привет! Я AI помощник ALADDIN. Чем могу помочь?",
            isFromUser = false,
            timestamp = Date(),
            category = "welcome"
        )
        
        addMessage(welcomeMessage)
    }
    
    private fun showTypingIndicator(show: Boolean) {
        isTyping = show
        typingIndicator.visibility = if (show) View.VISIBLE else View.GONE
    }
    
    private fun showError(message: String) {
        Toast.makeText(this, "Ошибка: $message", Toast.LENGTH_LONG).show()
    }
    
    private fun createRoundedBackground(color: Int): android.graphics.drawable.Drawable {
        val drawable = android.graphics.drawable.GradientDrawable()
        drawable.setColor(color)
        drawable.cornerRadius = 25f
        return drawable
    }
    
    override fun onDestroy() {
        super.onDestroy()
        scope.cancel()
    }
}

// MARK: - Support Message Model
data class SupportMessage(
    val id: String,
    val text: String,
    val isFromUser: Boolean,
    val timestamp: Date,
    val category: String
)

// MARK: - Support Message Adapter
class SupportMessageAdapter(private val messages: List<SupportMessage>) :
    RecyclerView.Adapter<SupportMessageAdapter.MessageViewHolder>() {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MessageViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_support_message, parent, false)
        return MessageViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: MessageViewHolder, position: Int) {
        holder.bind(messages[position])
    }
    
    override fun getItemCount(): Int = messages.size
    
    class MessageViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val messageText: TextView = itemView.findViewById(R.id.messageText)
        private val timeText: TextView = itemView.findViewById(R.id.timeText)
        private val bubbleView: LinearLayout = itemView.findViewById(R.id.bubbleView)
        
        fun bind(message: SupportMessage) {
            messageText.text = message.text
            timeText.text = formatTime(message.timestamp)
            
            if (message.isFromUser) {
                // User message - right aligned
                bubbleView.setBackgroundColor(StormSkyColors.accent)
                messageText.setTextColor(android.graphics.Color.WHITE)
                timeText.setTextColor(android.graphics.Color.WHITE)
                
                val layoutParams = bubbleView.layoutParams as LinearLayout.LayoutParams
                layoutParams.gravity = android.view.Gravity.END
                layoutParams.marginStart = 60
                layoutParams.marginEnd = 16
                bubbleView.layoutParams = layoutParams
            } else {
                // AI message - left aligned
                bubbleView.setBackgroundColor(StormSkyColors.backgroundSecondary)
                messageText.setTextColor(StormSkyColors.textPrimary)
                timeText.setTextColor(StormSkyColors.textSecondary)
                
                val layoutParams = bubbleView.layoutParams as LinearLayout.LayoutParams
                layoutParams.gravity = android.view.Gravity.START
                layoutParams.marginStart = 16
                layoutParams.marginEnd = 60
                bubbleView.layoutParams = layoutParams
            }
        }
        
        private fun formatTime(date: Date): String {
            val formatter = SimpleDateFormat("HH:mm", Locale.getDefault())
            return formatter.format(date)
        }
    }
}

// MARK: - Layout Resources (activity_support_chat.xml)
/*
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="@color/storm_sky_background_primary">

    <!-- Status Indicator -->
    <View
        android:id="@+id/statusIndicator"
        android:layout_width="12dp"
        android:layout_height="12dp"
        android:layout_marginTop="16dp"
        android:layout_marginEnd="16dp"
        android:layout_gravity="end"
        android:background="@drawable/circle_background" />

    <!-- Chat RecyclerView -->
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/chatRecyclerView"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:padding="8dp" />

    <!-- Typing Indicator -->
    <ProgressBar
        android:id="@+id/typingIndicator"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:layout_marginBottom="8dp"
        android:visibility="gone" />

    <!-- Quick Actions -->
    <LinearLayout
        android:id="@+id/quickActionsView"
        android:layout_width="match_parent"
        android:layout_height="60dp"
        android:orientation="horizontal"
        android:padding="8dp" />

    <!-- Message Input -->
    <LinearLayout
        android:id="@+id/messageInputView"
        android:layout_width="match_parent"
        android:layout_height="50dp"
        android:layout_margin="16dp"
        android:orientation="horizontal"
        android:padding="8dp"
        android:background="@drawable/rounded_background">

        <EditText
            android:id="@+id/messageEditText"
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_weight="1"
            android:background="@null"
            android:hint="Напишите ваш вопрос..."
            android:inputType="textMultiLine"
            android:maxLines="3"
            android:padding="8dp"
            android:textColor="@color/storm_sky_text_primary"
            android:textColorHint="@color/storm_sky_text_secondary" />

        <Button
            android:id="@+id/sendButton"
            android:layout_width="40dp"
            android:layout_height="40dp"
            android:layout_gravity="center_vertical"
            android:layout_marginStart="8dp"
            android:text="📤"
            android:textSize="16sp" />

    </LinearLayout>

</LinearLayout>
*/

// MARK: - Message Item Layout (item_support_message.xml)
/*
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:padding="8dp">

    <LinearLayout
        android:id="@+id/bubbleView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="12dp"
        android:background="@drawable/message_bubble">

        <TextView
            android:id="@+id/messageText"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="16sp"
            android:textColor="@color/storm_sky_text_primary" />

        <TextView
            android:id="@+id/timeText"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="4dp"
            android:textSize="12sp"
            android:textColor="@color/storm_sky_text_secondary" />

    </LinearLayout>

</LinearLayout>
*/

