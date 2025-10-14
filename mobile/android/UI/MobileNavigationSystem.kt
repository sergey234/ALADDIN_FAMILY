/*
 * MobileNavigationSystem.kt
 * ALADDIN Mobile Security
 *
 * Mobile Navigation System for Android
 * Adaptive navigation with bottom bar for mobile and desktop navigation
 *
 * Created by ALADDIN Security Team
 * Date: 2025-01-27
 * Version: 1.0
 */

package com.aladdin.security.ui.navigation

import android.content.Context
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.util.TypedValue
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.core.content.ContextCompat
import androidx.core.view.ViewCompat
import androidx.core.view.setPadding
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import androidx.fragment.app.FragmentManager
import androidx.fragment.app.FragmentTransaction

// MARK: - Navigation Item Model
data class NavigationItem(
    val title: String,
    val icon: Int,
    val selectedIcon: Int?,
    val identifier: String,
    val badge: String?,
    val isEnabled: Boolean = true
)

// MARK: - Navigation Delegate
interface MobileNavigationDelegate {
    fun onNavigationItemSelected(item: NavigationItem)
    fun onNavigationBadgeTapped(item: NavigationItem)
}

// MARK: - Mobile Navigation Controller
class MobileNavigationController(
    private val context: Context,
    private val fragmentManager: FragmentManager
) {
    
    // MARK: - Properties
    private var navigationItems: MutableList<NavigationItem> = mutableListOf()
    private var selectedIndex: Int = 0
    private var isMobileLayout: Boolean = true
    private var delegate: MobileNavigationDelegate? = null
    
    // MARK: - UI Components
    private var containerView: ViewGroup? = null
    private var bottomNavigationView: LinearLayout? = null
    private var topNavigationView: LinearLayout? = null
    private var contentFragment: Fragment? = null
    
    // MARK: - Configuration
    private val config = NavigationConfig()
    
    // MARK: - Initialization
    fun setup(
        containerView: ViewGroup,
        navigationItems: List<NavigationItem>,
        contentFragment: Fragment? = null
    ) {
        this.containerView = containerView
        this.navigationItems = navigationItems.toMutableList()
        this.contentFragment = contentFragment
        
        setupNavigationSystem()
        updateLayoutForCurrentSize()
    }
    
    // MARK: - Setup
    private fun setupNavigationSystem() {
        containerView?.let { container ->
            // Create bottom navigation view
            setupBottomNavigationView(container)
            
            // Create top navigation view
            setupTopNavigationView(container)
            
            // Add content fragment
            contentFragment?.let { fragment ->
                val transaction = fragmentManager.beginTransaction()
                transaction.replace(container.id, fragment)
                transaction.commit()
            }
        }
    }
    
    private fun setupBottomNavigationView(container: ViewGroup) {
        bottomNavigationView = LinearLayout(context).apply {
            orientation = LinearLayout.HORIZONTAL
            setBackgroundColor(Color.argb(204, 0, 0, 0)) // 80% black
            setPadding(16, 16, 16, 16)
            
            // Add corner radius
            val cornerRadius = TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP,
                20f,
                context.resources.displayMetrics
            )
            
            val backgroundDrawable = GradientDrawable().apply {
                this.cornerRadius = cornerRadius
                setColor(Color.argb(204, 0, 0, 0))
            }
            
            background = backgroundDrawable
        }
        
        // Add navigation items
        setupNavigationItems()
        
        container.addView(bottomNavigationView)
    }
    
    private fun setupTopNavigationView(container: ViewGroup) {
        topNavigationView = LinearLayout(context).apply {
            orientation = LinearLayout.HORIZONTAL
            setBackgroundColor(Color.TRANSPARENT)
            setPadding(16, 16, 16, 16)
        }
        
        // Add navigation items for desktop
        for (index in navigationItems.indices) {
            val item = navigationItems[index]
            val button = createDesktopNavigationButton(item, index)
            topNavigationView?.addView(button)
        }
        
        container.addView(topNavigationView)
    }
    
    private fun setupNavigationItems() {
        navigationItems.forEachIndexed { index, item ->
            val button = createMobileNavigationButton(item, index)
            bottomNavigationView?.addView(button)
        }
    }
    
    private fun createMobileNavigationButton(item: NavigationItem, index: Int): View {
        val button = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER
            setPadding(8, 8, 8, 8)
            isClickable = true
            isFocusable = true
            tag = index
        }
        
        // Icon
        val iconView = ImageView(context).apply {
            setImageResource(item.icon)
            setColorFilter(Color.argb(153, 255, 255, 255)) // 60% white
            layoutParams = LinearLayout.LayoutParams(
                TypedValue.applyDimension(
                    TypedValue.COMPLEX_UNIT_DIP,
                    24f,
                    context.resources.displayMetrics
                ).toInt(),
                TypedValue.applyDimension(
                    TypedValue.COMPLEX_UNIT_DIP,
                    24f,
                    context.resources.displayMetrics
                ).toInt()
            )
        }
        
        // Title
        val titleView = TextView(context).apply {
            text = item.title
            setTextColor(Color.argb(153, 255, 255, 255)) // 60% white
            textSize = 12f
            gravity = android.view.Gravity.CENTER
            maxLines = 1
        }
        
        // Badge
        if (item.badge != null) {
            val badgeView = TextView(context).apply {
                text = item.badge
                setTextColor(Color.WHITE)
                textSize = 10f
                gravity = android.view.Gravity.CENTER
                setPadding(4, 2, 4, 2)
                setBackgroundColor(Color.argb(255, 245, 158, 11)) // Golden
                layoutParams = LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                ).apply {
                    gravity = android.view.Gravity.CENTER
                }
            }
            
            // Create badge container
            val badgeContainer = FrameLayout(context).apply {
                addView(iconView)
                addView(badgeView)
            }
            
            button.addView(badgeContainer)
        } else {
            button.addView(iconView)
        }
        
        button.addView(titleView)
        
        // Set click listener
        button.setOnClickListener {
            onNavigationButtonClicked(index)
        }
        
        // Set initial state
        updateButtonState(button, item, index == selectedIndex)
        
        return button
    }
    
    private fun createDesktopNavigationButton(item: NavigationItem, index: Int): View {
        val button = LinearLayout(context).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = android.view.Gravity.CENTER
            setPadding(16, 12, 16, 12)
            isClickable = true
            isFocusable = true
            tag = index
        }
        
        // Icon
        val iconView = ImageView(context).apply {
            setImageResource(item.icon)
            setColorFilter(Color.argb(204, 255, 255, 255)) // 80% white
            layoutParams = LinearLayout.LayoutParams(
                TypedValue.applyDimension(
                    TypedValue.COMPLEX_UNIT_DIP,
                    20f,
                    context.resources.displayMetrics
                ).toInt(),
                TypedValue.applyDimension(
                    TypedValue.COMPLEX_UNIT_DIP,
                    20f,
                    context.resources.displayMetrics
                ).toInt()
            )
        }
        
        // Title
        val titleView = TextView(context).apply {
            text = item.title
            setTextColor(Color.argb(204, 255, 255, 255)) // 80% white
            textSize = 16f
            gravity = android.view.Gravity.CENTER
            maxLines = 1
            setPadding(8, 0, 0, 0)
        }
        
        // Badge
        if (item.badge != null) {
            val badgeView = TextView(context).apply {
                text = item.badge
                setTextColor(Color.WHITE)
                textSize = 10f
                gravity = android.view.Gravity.CENTER
                setPadding(4, 2, 4, 2)
                setBackgroundColor(Color.argb(255, 245, 158, 11)) // Golden
                layoutParams = LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                ).apply {
                    gravity = android.view.Gravity.CENTER
                }
            }
            
            // Create badge container
            val badgeContainer = FrameLayout(context).apply {
                addView(iconView)
                addView(badgeView)
            }
            
            button.addView(badgeContainer)
        } else {
            button.addView(iconView)
        }
        
        button.addView(titleView)
        
        // Set click listener
        button.setOnClickListener {
            onNavigationButtonClicked(index)
        }
        
        // Set initial state
        updateButtonState(button, item, index == selectedIndex)
        
        return button
    }
    
    private fun updateButtonState(button: LinearLayout, item: NavigationItem, isSelected: Boolean) {
        // Update icon color
        val iconView = button.getChildAt(0) as? ImageView
        iconView?.setColorFilter(
            if (isSelected) Color.WHITE else Color.argb(153, 255, 255, 255)
        )
        
        // Update title color
        val titleView = button.getChildAt(1) as? TextView
        titleView?.setTextColor(
            if (isSelected) Color.WHITE else Color.argb(153, 255, 255, 255)
        )
        
        // Update background
        if (isSelected) {
            val backgroundDrawable = GradientDrawable().apply {
                cornerRadius = TypedValue.applyDimension(
                    TypedValue.COMPLEX_UNIT_DIP,
                    8f,
                    context.resources.displayMetrics
                )
                setColor(Color.argb(51, 245, 158, 11)) // 20% golden
            }
            button.background = backgroundDrawable
        } else {
            button.background = null
        }
        
        // Update enabled state
        button.isEnabled = item.isEnabled
        button.alpha = if (item.isEnabled) 1.0f else 0.5f
    }
    
    // MARK: - Layout Updates
    fun updateLayoutForCurrentSize() {
        val isCompact = context.resources.configuration.screenWidthDp < 600
        
        if (isCompact != isMobileLayout) {
            isMobileLayout = isCompact
            updateNavigationVisibility()
        }
    }
    
    private fun updateNavigationVisibility() {
        bottomNavigationView?.alpha = if (isMobileLayout) 1.0f else 0.0f
        topNavigationView?.alpha = if (isMobileLayout) 0.0f else 1.0f
    }
    
    // MARK: - Actions
    private fun onNavigationButtonClicked(index: Int) {
        if (index >= navigationItems.size) return
        
        val item = navigationItems[index]
        
        // Update selection
        updateSelection(index)
        
        // Notify delegate
        delegate?.onNavigationItemSelected(item)
        
        // Haptic feedback
        addHapticFeedback()
    }
    
    private fun updateSelection(index: Int) {
        selectedIndex = index
        
        // Update mobile navigation
        bottomNavigationView?.let { view ->
            for (i in 0 until view.childCount) {
                val button = view.getChildAt(i) as? LinearLayout
                val item = navigationItems[i]
                updateButtonState(button ?: return, item, i == index)
            }
        }
        
        // Update desktop navigation
        topNavigationView?.let { view ->
            for (i in 0 until view.childCount) {
                val button = view.getChildAt(i) as? LinearLayout
                val item = navigationItems[i]
                updateButtonState(button ?: return, item, i == index)
            }
        }
    }
    
    private fun addHapticFeedback() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            vibrator.vibrate(VibrationEffect.createOneShot(50, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }
    
    // MARK: - Public Methods
    fun setSelectedIndex(index: Int, animated: Boolean = true) {
        if (index >= navigationItems.size) return
        
        if (animated) {
            // Simple animation - in real implementation, use ValueAnimator
            updateSelection(index)
        } else {
            updateSelection(index)
        }
    }
    
    fun updateBadge(identifier: String, badge: String?) {
        val index = navigationItems.indexOfFirst { it.identifier == identifier }
        if (index == -1) return
        
        // Update model
        navigationItems[index] = navigationItems[index].copy(badge = badge)
        
        // Update UI
        updateBadgeInUI(index, badge)
    }
    
    private fun updateBadgeInUI(index: Int, badge: String?) {
        // Update mobile navigation
        bottomNavigationView?.let { view ->
            if (index < view.childCount) {
                val button = view.getChildAt(index) as? LinearLayout
                updateBadgeInButton(button, badge)
            }
        }
        
        // Update desktop navigation
        topNavigationView?.let { view ->
            if (index < view.childCount) {
                val button = view.getChildAt(index) as? LinearLayout
                updateBadgeInButton(button, badge)
            }
        }
    }
    
    private fun updateBadgeInButton(button: LinearLayout?, badge: String?) {
        // Remove existing badge
        button?.let { btn ->
            for (i in 0 until btn.childCount) {
                val child = btn.getChildAt(i)
                if (child is FrameLayout) {
                    // Remove badge from FrameLayout
                    for (j in 0 until child.childCount) {
                        val badgeView = child.getChildAt(j)
                        if (badgeView is TextView && badgeView.text.toString() != "") {
                            child.removeView(badgeView)
                        }
                    }
                }
            }
        }
        
        // Add new badge if needed
        if (badge != null) {
            // Implementation for adding badge
            // This would require more complex logic to properly add badges
        }
    }
    
    fun setDelegate(delegate: MobileNavigationDelegate?) {
        this.delegate = delegate
    }
    
    fun addNavigationItem(item: NavigationItem) {
        navigationItems.add(item)
        
        // Add to mobile navigation
        val mobileButton = createMobileNavigationButton(item, navigationItems.size - 1)
        bottomNavigationView?.addView(mobileButton)
        
        // Add to desktop navigation
        val desktopButton = createDesktopNavigationButton(item, navigationItems.size - 1)
        topNavigationView?.addView(desktopButton)
    }
    
    fun removeNavigationItem(identifier: String) {
        val index = navigationItems.indexOfFirst { it.identifier == identifier }
        if (index == -1) return
        
        navigationItems.removeAt(index)
        
        // Remove from mobile navigation
        bottomNavigationView?.removeViewAt(index)
        
        // Remove from desktop navigation
        topNavigationView?.removeViewAt(index)
        
        // Update tags
        updateButtonTags()
    }
    
    private fun updateButtonTags() {
        bottomNavigationView?.let { view ->
            for (i in 0 until view.childCount) {
                view.getChildAt(i).tag = i
            }
        }
        
        topNavigationView?.let { view ->
            for (i in 0 until view.childCount) {
                view.getChildAt(i).tag = i
            }
        }
    }
}

// MARK: - Navigation Configuration
object NavigationConfig {
    const val BOTTOM_BAR_HEIGHT_DP = 80f
    const val TOP_BAR_HEIGHT_DP = 60f
    const val CORNER_RADIUS_DP = 20f
    const val BLUR_OPACITY = 0.8f
    const val ANIMATION_DURATION_MS = 300L
    const val HAPTIC_FEEDBACK_ENABLED = true
}

// MARK: - Navigation Factory
object NavigationFactory {
    
    fun createALADDINNavigation(): List<NavigationItem> {
        return listOf(
            NavigationItem(
                title = "Главная",
                icon = android.R.drawable.ic_menu_home,
                selectedIcon = android.R.drawable.ic_menu_home,
                identifier = "home"
            ),
            NavigationItem(
                title = "Защита",
                icon = android.R.drawable.ic_menu_manage,
                selectedIcon = android.R.drawable.ic_menu_manage,
                identifier = "security"
            ),
            NavigationItem(
                title = "Семья",
                icon = android.R.drawable.ic_menu_myplaces,
                selectedIcon = android.R.drawable.ic_menu_myplaces,
                identifier = "family"
            ),
            NavigationItem(
                title = "Аналитика",
                icon = android.R.drawable.ic_menu_info_details,
                selectedIcon = android.R.drawable.ic_menu_info_details,
                identifier = "analytics"
            ),
            NavigationItem(
                title = "Настройки",
                icon = android.R.drawable.ic_menu_preferences,
                selectedIcon = android.R.drawable.ic_menu_preferences,
                identifier = "settings"
            )
        )
    }
    
    fun createVPNNavigation(): List<NavigationItem> {
        return listOf(
            NavigationItem(
                title = "Подключение",
                icon = android.R.drawable.ic_menu_share,
                selectedIcon = android.R.drawable.ic_menu_share,
                identifier = "connection"
            ),
            NavigationItem(
                title = "Серверы",
                icon = android.R.drawable.ic_menu_manage,
                selectedIcon = android.R.drawable.ic_menu_manage,
                identifier = "servers"
            ),
            NavigationItem(
                title = "Статистика",
                icon = android.R.drawable.ic_menu_info_details,
                selectedIcon = android.R.drawable.ic_menu_info_details,
                identifier = "statistics"
            ),
            NavigationItem(
                title = "Настройки",
                icon = android.R.drawable.ic_menu_preferences,
                selectedIcon = android.R.drawable.ic_menu_preferences,
                identifier = "settings"
            )
        )
    }
}

// MARK: - Navigation Extensions
fun MobileNavigationController.setupWithALADDINNavigation(
    containerView: ViewGroup,
    contentFragment: Fragment? = null
) {
    val navigationItems = NavigationFactory.createALADDINNavigation()
    setup(containerView, navigationItems, contentFragment)
}

fun MobileNavigationController.setupWithVPNNavigation(
    containerView: ViewGroup,
    contentFragment: Fragment? = null
) {
    val navigationItems = NavigationFactory.createVPNNavigation()
    setup(containerView, navigationItems, contentFragment)
}

