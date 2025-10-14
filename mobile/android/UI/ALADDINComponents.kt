package com.aladdin.security.ui

import android.content.Context
import android.graphics.*
import android.graphics.drawable.GradientDrawable
import android.util.AttributeSet
import android.view.View
import android.widget.*
import androidx.core.content.ContextCompat
import androidx.core.graphics.drawable.DrawableCompat
import kotlin.math.cos
import kotlin.math.sin

/**
 * ALADDIN UI Components для Android
 * Красивые компоненты с грозовым небом и золотыми акцентами
 */

// MARK: - ALADDIN Button
class ALADDINButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : Button(context, attrs, defStyleAttr) {
    
    enum class ButtonStyle {
        PRIMARY,
        SECONDARY,
        DANGER,
        GHOST,
        GLASSMORPHISM,
        NEUMORPHISM
    }
    
    private var buttonStyle = ButtonStyle.PRIMARY
    private val stormSkyColors = StormSkyColors()
    
    init {
        setupButton()
    }
    
    fun setStyle(style: ButtonStyle) {
        buttonStyle = style
        setupButton()
    }
    
    private fun setupButton() {
        when (buttonStyle) {
            ButtonStyle.PRIMARY -> setupPrimaryButton()
            ButtonStyle.SECONDARY -> setupSecondaryButton()
            ButtonStyle.DANGER -> setupDangerButton()
            ButtonStyle.GHOST -> setupGhostButton()
            ButtonStyle.GLASSMORPHISM -> setupGlassmorphismButton()
            ButtonStyle.NEUMORPHISM -> setupNeumorphismButton()
        }
        
        // Common properties
        textSize = 16f
        setTextColor(getTextColor())
        setPadding(24, 16, 24, 16)
        minHeight = 56 // Touch-friendly
        elevation = 0f
    }
    
    private fun setupPrimaryButton() {
        val gradient = GradientDrawable(
            GradientDrawable.Orientation.LEFT_RIGHT,
            intArrayOf(stormSkyColors.goldenAccent, stormSkyColors.goldenAccentDark)
        )
        gradient.cornerRadius = 16f
        background = gradient
    }
    
    private fun setupSecondaryButton() {
        val gradient = GradientDrawable(
            GradientDrawable.Orientation.LEFT_RIGHT,
            intArrayOf(stormSkyColors.stormSkyBlue, stormSkyColors.stormSkyMedium)
        )
        gradient.cornerRadius = 16f
        background = gradient
    }
    
    private fun setupDangerButton() {
        val gradient = GradientDrawable(
            GradientDrawable.Orientation.LEFT_RIGHT,
            intArrayOf(Color.RED, Color.parseColor("#CC0000"))
        )
        gradient.cornerRadius = 16f
        background = gradient
    }
    
    private fun setupGhostButton() {
        background = null
        setTextColor(stormSkyColors.goldenAccent)
        setBackgroundResource(R.drawable.ghost_button_background)
    }
    
    private fun setupGlassmorphismButton() {
        background = ContextCompat.getDrawable(context, R.drawable.glassmorphism_button_background)
    }
    
    private fun setupNeumorphismButton() {
        background = ContextCompat.getDrawable(context, R.drawable.neumorphism_button_background)
    }
    
    private fun getTextColor(): Int {
        return when (buttonStyle) {
            ButtonStyle.PRIMARY, ButtonStyle.DANGER -> Color.WHITE
            ButtonStyle.SECONDARY, ButtonStyle.GHOST, ButtonStyle.GLASSMORPHISM, ButtonStyle.NEUMORPHISM -> stormSkyColors.goldenAccent
        }
    }
}

// MARK: - ALADDIN Card
class ALADDINCard @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {
    
    enum class CardStyle {
        GLASSMORPHISM,
        NEUMORPHISM,
        SOLID,
        GRADIENT
    }
    
    private var cardStyle = CardStyle.GLASSMORPHISM
    private val stormSkyColors = StormSkyColors()
    
    init {
        setupCard()
    }
    
    fun setStyle(style: CardStyle) {
        cardStyle = style
        setupCard()
    }
    
    private fun setupCard() {
        setPadding(20, 20, 20, 20)
        
        when (cardStyle) {
            CardStyle.GLASSMORPHISM -> setupGlassmorphismCard()
            CardStyle.NEUMORPHISM -> setupNeumorphismCard()
            CardStyle.SOLID -> setupSolidCard()
            CardStyle.GRADIENT -> setupGradientCard()
        }
    }
    
    private fun setupGlassmorphismCard() {
        background = ContextCompat.getDrawable(context, R.drawable.glassmorphism_card_background)
    }
    
    private fun setupNeumorphismCard() {
        background = ContextCompat.getDrawable(context, R.drawable.neumorphism_card_background)
    }
    
    private fun setupSolidCard() {
        val drawable = GradientDrawable()
        drawable.setColor(stormSkyColors.stormSkyBlue)
        drawable.cornerRadius = 20f
        drawable.setStroke(2, stormSkyColors.goldenAccent)
        background = drawable
    }
    
    private fun setupGradientCard() {
        val gradient = GradientDrawable(
            GradientDrawable.Orientation.TL_BR,
            intArrayOf(
                stormSkyColors.stormSkyDark,
                stormSkyColors.stormSkyBlue
            )
        )
        gradient.cornerRadius = 20f
        background = gradient
    }
}

// MARK: - ALADDIN Text Field
class ALADDINTextField @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : EditText(context, attrs, defStyleAttr) {
    
    enum class TextFieldStyle {
        GLASSMORPHISM,
        NEUMORPHISM,
        SOLID
    }
    
    private var textFieldStyle = TextFieldStyle.GLASSMORPHISM
    private val stormSkyColors = StormSkyColors()
    
    init {
        setupTextField()
    }
    
    fun setStyle(style: TextFieldStyle) {
        textFieldStyle = style
        setupTextField()
    }
    
    private fun setupTextField() {
        setPadding(16, 16, 16, 16)
        setTextColor(Color.WHITE)
        textSize = 16f
        hintTextColor = Color.WHITE.copy(alpha = 0.7f)
        
        when (textFieldStyle) {
            TextFieldStyle.GLASSMORPHISM -> setupGlassmorphismTextField()
            TextFieldStyle.NEUMORPHISM -> setupNeumorphismTextField()
            TextFieldStyle.SOLID -> setupSolidTextField()
        }
    }
    
    private fun setupGlassmorphismTextField() {
        background = ContextCompat.getDrawable(context, R.drawable.glassmorphism_textfield_background)
    }
    
    private fun setupNeumorphismTextField() {
        background = ContextCompat.getDrawable(context, R.drawable.neumorphism_textfield_background)
    }
    
    private fun setupSolidTextField() {
        val drawable = GradientDrawable()
        drawable.setColor(stormSkyColors.stormSkyBlue)
        drawable.cornerRadius = 12f
        drawable.setStroke(2, stormSkyColors.goldenAccent)
        background = drawable
    }
}

// MARK: - ALADDIN Status Indicator
class ALADDINStatusIndicator @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {
    
    enum class Status {
        CONNECTED,
        CONNECTING,
        DISCONNECTED,
        ERROR
    }
    
    private var status = Status.DISCONNECTED
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val strokePaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var animationValue = 0f
    private var isAnimating = false
    
    init {
        setupPaint()
    }
    
    fun setStatus(newStatus: Status) {
        status = newStatus
        isAnimating = status == Status.CONNECTING
        invalidate()
    }
    
    private fun setupPaint() {
        strokePaint.color = Color.WHITE
        strokePaint.style = Paint.Style.STROKE
        strokePaint.strokeWidth = 4f
    }
    
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        
        val centerX = width / 2f
        val centerY = height / 2f
        val radius = minOf(width, height) / 2f - 4f
        
        // Draw status circle
        paint.color = getStatusColor()
        canvas.drawCircle(centerX, centerY, radius, paint)
        
        // Draw white border
        canvas.drawCircle(centerX, centerY, radius, strokePaint)
        
        // Draw connecting animation
        if (isAnimating) {
            drawConnectingAnimation(canvas, centerX, centerY, radius)
        }
    }
    
    private fun getStatusColor(): Int {
        return when (status) {
            Status.CONNECTED -> Color.GREEN
            Status.CONNECTING -> Color.YELLOW
            Status.DISCONNECTED -> Color.GRAY
            Status.ERROR -> Color.RED
        }
    }
    
    private fun drawConnectingAnimation(canvas: Canvas, centerX: Float, centerY: Float, radius: Float) {
        val animatedRadius = radius + (radius * 0.2f * animationValue)
        val alpha = (255 * (1 - animationValue)).toInt()
        
        paint.alpha = alpha
        canvas.drawCircle(centerX, centerY, animatedRadius, paint)
        
        if (isAnimating) {
            animationValue += 0.05f
            if (animationValue >= 1f) {
                animationValue = 0f
            }
            postInvalidateDelayed(50)
        }
    }
}

// MARK: - ALADDIN Loading View
class ALADDINLoadingView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {
    
    private val progressBar: ProgressBar
    private val messageText: TextView
    private val stormSkyColors = StormSkyColors()
    
    init {
        orientation = VERTICAL
        gravity = android.view.Gravity.CENTER
        setPadding(32, 32, 32, 32)
        
        // Progress bar
        progressBar = ProgressBar(context, null, android.R.attr.progressBarStyleLarge)
        progressBar.indeterminateDrawable = createCustomProgressDrawable()
        addView(progressBar)
        
        // Message text
        messageText = TextView(context)
        messageText.text = "Загрузка..."
        messageText.setTextColor(Color.WHITE)
        messageText.textSize = 16f
        messageText.gravity = android.view.Gravity.CENTER
        messageText.setPadding(0, 16, 0, 0)
        addView(messageText)
    }
    
    fun setMessage(message: String) {
        messageText.text = message
    }
    
    private fun createCustomProgressDrawable(): android.graphics.drawable.Drawable {
        val drawable = ContextCompat.getDrawable(context, android.R.drawable.progress_horizontal)
        val wrappedDrawable = DrawableCompat.wrap(drawable!!)
        DrawableCompat.setTint(wrappedDrawable, stormSkyColors.goldenAccent)
        return wrappedDrawable
    }
}

// MARK: - ALADDIN Bottom Navigation
class ALADDINBottomNavigation @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {
    
    enum class Tab {
        VPN,
        FAMILY,
        ANALYTICS,
        SETTINGS,
        AI
    }
    
    private var selectedTab = Tab.VPN
    private val stormSkyColors = StormSkyColors()
    private val tabButtons = mutableListOf<LinearLayout>()
    private var onTabSelectedListener: ((Tab) -> Unit)? = null
    
    init {
        setupBottomNavigation()
    }
    
    fun setOnTabSelectedListener(listener: (Tab) -> Unit) {
        onTabSelectedListener = listener
    }
    
    fun setSelectedTab(tab: Tab) {
        selectedTab = tab
        updateTabSelection()
    }
    
    private fun setupBottomNavigation() {
        orientation = HORIZONTAL
        setPadding(16, 12, 16, 12)
        background = ContextCompat.getDrawable(context, R.drawable.bottom_navigation_background)
        
        val tabs = Tab.values()
        for (tab in tabs) {
            val tabButton = createTabButton(tab)
            tabButtons.add(tabButton)
            addView(tabButton)
        }
        
        updateTabSelection()
    }
    
    private fun createTabButton(tab: Tab): LinearLayout {
        val tabButton = LinearLayout(context)
        tabButton.orientation = VERTICAL
        tabButton.gravity = android.view.Gravity.CENTER
        tabButton.setPadding(8, 8, 8, 8)
        tabButton.minimumHeight = 44 // Touch-friendly
        
        // Icon
        val icon = ImageView(context)
        icon.setImageResource(getTabIcon(tab))
        icon.layoutParams = LinearLayout.LayoutParams(48, 48)
        tabButton.addView(icon)
        
        // Title
        val title = TextView(context)
        title.text = getTabTitle(tab)
        title.setTextColor(Color.WHITE)
        title.textSize = 10f
        title.gravity = android.view.Gravity.CENTER
        title.setPadding(0, 4, 0, 0)
        tabButton.addView(title)
        
        // Click listener
        tabButton.setOnClickListener {
            selectedTab = tab
            updateTabSelection()
            onTabSelectedListener?.invoke(tab)
        }
        
        return tabButton
    }
    
    private fun updateTabSelection() {
        tabButtons.forEachIndexed { index, tabButton ->
            val tab = Tab.values()[index]
            val isSelected = tab == selectedTab
            
            // Update icon color
            val icon = tabButton.getChildAt(0) as ImageView
            val iconColor = if (isSelected) stormSkyColors.goldenAccent else Color.WHITE.copy(alpha = 0.7f)
            icon.setColorFilter(iconColor)
            
            // Update title color
            val title = tabButton.getChildAt(1) as TextView
            title.setTextColor(iconColor)
        }
    }
    
    private fun getTabIcon(tab: Tab): Int {
        return when (tab) {
            Tab.VPN -> android.R.drawable.ic_dialog_info // Replace with custom icon
            Tab.FAMILY -> android.R.drawable.ic_dialog_info
            Tab.ANALYTICS -> android.R.drawable.ic_dialog_info
            Tab.SETTINGS -> android.R.drawable.ic_dialog_info
            Tab.AI -> android.R.drawable.ic_dialog_info
        }
    }
    
    private fun getTabTitle(tab: Tab): String {
        return when (tab) {
            Tab.VPN -> "VPN"
            Tab.FAMILY -> "Семья"
            Tab.ANALYTICS -> "Аналитика"
            Tab.SETTINGS -> "Настройки"
            Tab.AI -> "AI"
        }
    }
}

// MARK: - Storm Sky Colors
class StormSkyColors {
    val stormSkyDark = Color.parseColor("#0f172a")
    val stormSkyBlue = Color.parseColor("#1E3A8A")
    val stormSkyMedium = Color.parseColor("#3B82F6")
    val goldenAccent = Color.parseColor("#F59E0B")
    val goldenAccentDark = Color.parseColor("#D97706")
}

