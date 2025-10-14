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

// MARK: - Support Main Interface для Android
class SupportMainInterface : AppCompatActivity() {
    
    // UI Components
    private lateinit var scrollView: ScrollView
    private lateinit var contentLayout: LinearLayout
    private lateinit var headerCard: LinearLayout
    private lateinit var titleText: TextView
    private lateinit var subtitleText: TextView
    private lateinit var statusView: LinearLayout
    private lateinit var statusIndicator: View
    private lateinit var statusText: TextView
    
    // Quick Actions
    private lateinit var quickActionsLayout: LinearLayout
    private lateinit var chatButton: SupportActionButton
    private lateinit var faqButton: SupportActionButton
    private lateinit var contactButton: SupportActionButton
    private lateinit var emergencyButton: SupportActionButton
    
    // Categories
    private lateinit var categoriesLayout: LinearLayout
    private lateinit var categoriesTitle: TextView
    
    // Recent Activity
    private lateinit var recentActivityLayout: LinearLayout
    private lateinit var recentActivityTitle: TextView
    private lateinit var recentActivityRecyclerView: RecyclerView
    
    // Properties
    private val supportAPI = UnifiedSupportAPIManager()
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private var recentTickets = listOf<SupportTicket>()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_support_main)
        
        setupUI()
        setupRecyclerView()
        loadData()
    }
    
    private fun setupUI() {
        // Find views
        scrollView = findViewById(R.id.scrollView)
        contentLayout = findViewById(R.id.contentLayout)
        headerCard = findViewById(R.id.headerCard)
        titleText = findViewById(R.id.titleText)
        subtitleText = findViewById(R.id.subtitleText)
        statusView = findViewById(R.id.statusView)
        statusIndicator = findViewById(R.id.statusIndicator)
        statusText = findViewById(R.id.statusText)
        
        quickActionsLayout = findViewById(R.id.quickActionsLayout)
        chatButton = findViewById(R.id.chatButton)
        faqButton = findViewById(R.id.faqButton)
        contactButton = findViewById(R.id.contactButton)
        emergencyButton = findViewById(R.id.emergencyButton)
        
        categoriesLayout = findViewById(R.id.categoriesLayout)
        categoriesTitle = findViewById(R.id.categoriesTitle)
        
        recentActivityLayout = findViewById(R.id.recentActivityLayout)
        recentActivityTitle = findViewById(R.id.recentActivityTitle)
        recentActivityRecyclerView = findViewById(R.id.recentActivityRecyclerView)
        
        // Setup appearance
        setupAppearance()
        setupQuickActions()
        setupCategories()
    }
    
    private fun setupAppearance() {
        // Header
        titleText.text = "AI Помощник ALADDIN"
        titleText.setTextColor(StormSkyColors.textPrimary)
        
        subtitleText.text = "Ваш персональный помощник по безопасности"
        subtitleText.setTextColor(StormSkyColors.textSecondary)
        
        // Status
        statusIndicator.setBackgroundColor(StormSkyColors.success)
        statusText.text = "Онлайн"
        statusText.setTextColor(StormSkyColors.textPrimary)
        
        // Categories title
        categoriesTitle.text = "Категории поддержки"
        categoriesTitle.setTextColor(StormSkyColors.textPrimary)
        
        // Recent activity title
        recentActivityTitle.text = "Недавние обращения"
        recentActivityTitle.setTextColor(StormSkyColors.textPrimary)
    }
    
    private fun setupQuickActions() {
        // Chat Button
        chatButton.configure(
            title = "💬 Чат с AI",
            subtitle = "Задайте вопрос помощнику",
            action = { openChat() }
        )
        
        // FAQ Button
        faqButton.configure(
            title = "❓ Частые вопросы",
            subtitle = "Быстрые ответы на популярные вопросы",
            action = { openFAQ() }
        )
        
        // Contact Button
        contactButton.configure(
            title = "📞 Связаться с нами",
            subtitle = "Техническая поддержка и консультации",
            action = { openContact() }
        )
        
        // Emergency Button
        emergencyButton.configure(
            title = "🚨 Экстренная помощь",
            subtitle = "Критические ситуации и срочная поддержка",
            action = { openEmergency() }
        )
        emergencyButton.setEmergencyStyle()
    }
    
    private fun setupCategories() {
        val categories = listOf(
            Triple("🛡️ Безопасность", "security", "Защита семьи и устройств"),
            Triple("👨‍👩‍👧‍👦 Семья", "family", "Родительский контроль и детская безопасность"),
            Triple("🔧 Настройки", "settings", "Конфигурация приложения"),
            Triple("💳 Платежи", "payments", "Подписки и оплата"),
            Triple("📱 Устройства", "devices", "Подключение и синхронизация"),
            Triple("🔐 Безопасность данных", "privacy", "Конфиденциальность и шифрование")
        )
        
        categories.forEach { (title, category, description) ->
            val categoryView = SupportCategoryView(this).apply {
                configure(title, description, category)
                setOnClickListener { openCategory(category) }
            }
            categoriesLayout.addView(categoryView)
        }
    }
    
    private fun setupRecyclerView() {
        recentActivityRecyclerView.layoutManager = LinearLayoutManager(this)
        recentActivityRecyclerView.adapter = SupportTicketAdapter(recentTickets) { ticket ->
            openTicketDetails(ticket)
        }
    }
    
    private fun loadData() {
        loadRecentTickets()
        checkSupportStatus()
    }
    
    private fun loadRecentTickets() {
        scope.launch {
            try {
                val tickets = withContext(Dispatchers.IO) {
                    supportAPI.getRecentTickets()
                }
                recentTickets = tickets
                recentActivityRecyclerView.adapter = SupportTicketAdapter(tickets) { ticket ->
                    openTicketDetails(ticket)
                }
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
    
    private fun checkSupportStatus() {
        scope.launch {
            try {
                val status = withContext(Dispatchers.IO) {
                    supportAPI.getSupportStatus()
                }
                updateStatusIndicator(status)
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
    
    private fun updateStatusIndicator(status: SupportStatus) {
        when (status) {
            SupportStatus.ONLINE -> {
                statusIndicator.setBackgroundColor(StormSkyColors.success)
                statusText.text = "Онлайн"
            }
            SupportStatus.BUSY -> {
                statusIndicator.setBackgroundColor(StormSkyColors.warning)
                statusText.text = "Занят"
            }
            SupportStatus.OFFLINE -> {
                statusIndicator.setBackgroundColor(StormSkyColors.error)
                statusText.text = "Офлайн"
            }
        }
    }
    
    // MARK: - Actions
    private fun openChat() {
        val intent = android.content.Intent(this, SupportChatInterface::class.java)
        startActivity(intent)
    }
    
    private fun openFAQ() {
        val intent = android.content.Intent(this, SupportFAQActivity::class.java)
        startActivity(intent)
    }
    
    private fun openContact() {
        val intent = android.content.Intent(this, SupportContactActivity::class.java)
        startActivity(intent)
    }
    
    private fun openEmergency() {
        val intent = android.content.Intent(this, SupportEmergencyActivity::class.java)
        startActivity(intent)
    }
    
    private fun openCategory(category: String) {
        val intent = android.content.Intent(this, SupportCategoryActivity::class.java)
        intent.putExtra("category", category)
        startActivity(intent)
    }
    
    private fun openTicketDetails(ticket: SupportTicket) {
        val intent = android.content.Intent(this, SupportTicketDetailsActivity::class.java)
        intent.putExtra("ticket_id", ticket.id)
        startActivity(intent)
    }
    
    override fun onDestroy() {
        super.onDestroy()
        scope.cancel()
    }
}

// MARK: - Support Action Button
class SupportActionButton : LinearLayout {
    private val iconText: TextView
    private val titleText: TextView
    private val subtitleText: TextView
    private var action: (() -> Unit)? = null
    
    constructor(context: android.content.Context) : super(context) {
        iconText = TextView(context)
        titleText = TextView(context)
        subtitleText = TextView(context)
        init()
    }
    
    constructor(context: android.content.Context, attrs: android.util.AttributeSet?) : super(context, attrs) {
        iconText = TextView(context)
        titleText = TextView(context)
        subtitleText = TextView(context)
        init()
    }
    
    private fun init() {
        orientation = HORIZONTAL
        setPadding(16, 16, 16, 16)
        setBackgroundColor(StormSkyColors.backgroundSecondary)
        background = createRoundedBackground(StormSkyColors.backgroundSecondary)
        
        // Icon
        iconText.textSize = 24f
        iconText.textAlignment = android.view.View.TEXT_ALIGNMENT_CENTER
        
        // Title
        titleText.textSize = 18f
        titleText.setTextColor(StormSkyColors.textPrimary)
        titleText.typeface = android.graphics.Typeface.DEFAULT_BOLD
        
        // Subtitle
        subtitleText.textSize = 14f
        subtitleText.setTextColor(StormSkyColors.textSecondary)
        subtitleText.maxLines = 2
        
        // Layout
        val iconParams = LayoutParams(120, LayoutParams.WRAP_CONTENT).apply {
            gravity = android.view.Gravity.CENTER_VERTICAL
        }
        addView(iconText, iconParams)
        
        val textLayout = LinearLayout(context).apply {
            orientation = VERTICAL
            layoutParams = LayoutParams(0, LayoutParams.WRAP_CONTENT, 1f).apply {
                leftMargin = 12
            }
        }
        
        textLayout.addView(titleText)
        textLayout.addView(subtitleText)
        addView(textLayout)
        
        // Click listener
        setOnClickListener { action?.invoke() }
    }
    
    fun configure(title: String, subtitle: String, action: () -> Unit) {
        val parts = title.split(" ", limit = 2)
        if (parts.size > 1) {
            iconText.text = parts[0]
            titleText.text = parts[1]
        } else {
            titleText.text = title
        }
        subtitleText.text = subtitle
        this.action = action
    }
    
    fun setEmergencyStyle() {
        setBackgroundColor(StormSkyColors.error)
        background = createRoundedBackground(StormSkyColors.error)
        titleText.setTextColor(android.graphics.Color.WHITE)
        subtitleText.setTextColor(android.graphics.Color.WHITE)
    }
    
    private fun createRoundedBackground(color: Int): android.graphics.drawable.Drawable {
        val drawable = android.graphics.drawable.GradientDrawable()
        drawable.setColor(color)
        drawable.cornerRadius = 16f
        return drawable
    }
}

// MARK: - Support Category View
class SupportCategoryView : LinearLayout {
    private val titleText: TextView
    private val descriptionText: TextView
    private val arrowIcon: TextView
    
    constructor(context: android.content.Context) : super(context) {
        titleText = TextView(context)
        descriptionText = TextView(context)
        arrowIcon = TextView(context)
        init()
    }
    
    constructor(context: android.content.Context, attrs: android.util.AttributeSet?) : super(context, attrs) {
        titleText = TextView(context)
        descriptionText = TextView(context)
        arrowIcon = TextView(context)
        init()
    }
    
    private fun init() {
        orientation = HORIZONTAL
        setPadding(16, 12, 16, 12)
        setBackgroundColor(StormSkyColors.backgroundSecondary)
        background = createRoundedBackground(StormSkyColors.backgroundSecondary)
        
        // Title
        titleText.textSize = 16f
        titleText.setTextColor(StormSkyColors.textPrimary)
        titleText.typeface = android.graphics.Typeface.DEFAULT_BOLD
        
        // Description
        descriptionText.textSize = 14f
        descriptionText.setTextColor(StormSkyColors.textSecondary)
        descriptionText.maxLines = 2
        
        // Arrow
        arrowIcon.text = ">"
        arrowIcon.textSize = 18f
        arrowIcon.setTextColor(StormSkyColors.accent)
        
        // Layout
        val textLayout = LinearLayout(context).apply {
            orientation = VERTICAL
            layoutParams = LayoutParams(0, LayoutParams.WRAP_CONTENT, 1f)
        }
        
        textLayout.addView(titleText)
        textLayout.addView(descriptionText)
        addView(textLayout)
        
        val arrowParams = LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT).apply {
            gravity = android.view.Gravity.CENTER_VERTICAL
            leftMargin = 8
        }
        addView(arrowIcon, arrowParams)
    }
    
    fun configure(title: String, description: String, category: String) {
        titleText.text = title
        descriptionText.text = description
    }
    
    private fun createRoundedBackground(color: Int): android.graphics.drawable.Drawable {
        val drawable = android.graphics.drawable.GradientDrawable()
        drawable.setColor(color)
        drawable.cornerRadius = 12f
        return drawable
    }
}

// MARK: - Support Ticket Adapter
class SupportTicketAdapter(
    private val tickets: List<SupportTicket>,
    private val onTicketClick: (SupportTicket) -> Unit
) : RecyclerView.Adapter<SupportTicketAdapter.TicketViewHolder>() {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TicketViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_support_ticket, parent, false)
        return TicketViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: TicketViewHolder, position: Int) {
        holder.bind(tickets[position])
    }
    
    override fun getItemCount(): Int = tickets.size
    
    class TicketViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val titleText: TextView = itemView.findViewById(R.id.ticketTitle)
        private val statusText: TextView = itemView.findViewById(R.id.ticketStatus)
        private val dateText: TextView = itemView.findViewById(R.id.ticketDate)
        private val lastMessageText: TextView = itemView.findViewById(R.id.ticketLastMessage)
        
        fun bind(ticket: SupportTicket) {
            titleText.text = ticket.title
            statusText.text = ticket.status.name
            dateText.text = formatDate(ticket.createdAt)
            lastMessageText.text = ticket.lastMessage ?: "Нет сообщений"
            
            // Set status color
            when (ticket.status) {
                TicketStatus.OPEN -> statusText.setTextColor(StormSkyColors.warning)
                TicketStatus.IN_PROGRESS -> statusText.setTextColor(StormSkyColors.accent)
                TicketStatus.RESOLVED -> statusText.setTextColor(StormSkyColors.success)
                TicketStatus.CLOSED -> statusText.setTextColor(StormSkyColors.textSecondary)
            }
        }
        
        private fun formatDate(date: Date): String {
            val formatter = java.text.SimpleDateFormat("dd.MM.yyyy", Locale.getDefault())
            return formatter.format(date)
        }
    }
}

// MARK: - Support Models
data class SupportTicket(
    val id: String,
    val title: String,
    val status: TicketStatus,
    val category: String,
    val createdAt: Date,
    val lastMessage: String?
)

enum class TicketStatus {
    OPEN, IN_PROGRESS, RESOLVED, CLOSED
}

enum class SupportStatus {
    ONLINE, BUSY, OFFLINE
}

