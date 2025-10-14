/*
 * TouchFriendlyElements.kt
 * ALADDIN Mobile Security
 *
 * Touch-Friendly UI Elements for Android
 * Optimized for mobile touch interaction with proper sizing and feedback
 *
 * Created by ALADDIN Security Team
 * Date: 2025-01-27
 * Version: 1.0
 */

package com.aladdin.security.ui.touchfriendly

import android.content.Context
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.util.TypedValue
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.animation.Animation
import android.view.animation.ScaleAnimation
import android.widget.*
import androidx.core.content.ContextCompat
import androidx.core.view.ViewCompat
import androidx.core.view.setPadding

// MARK: - Touch-Friendly Configuration
object TouchFriendlyConfig {
    const val MINIMUM_TOUCH_SIZE_DP = 44f  // Google's minimum recommended size
    const val PREFERRED_TOUCH_SIZE_DP = 50f  // Preferred size for better UX
    const val LARGE_TOUCH_SIZE_DP = 60f  // For important actions
    const val TOUCH_PADDING_DP = 8f  // Padding around touch targets
    const val ANIMATION_DURATION_MS = 200L  // Touch animation duration
    const val SCALE_FACTOR = 0.95f  // Scale factor for touch feedback
    const val ALPHA_FACTOR = 0.8f  // Alpha factor for touch feedback
}

// MARK: - Touch-Friendly Button
class TouchFriendlyButton @JvmOverloads constructor(
    context: Context,
    private val minimumSizeDp: Float = TouchFriendlyConfig.MINIMUM_TOUCH_SIZE_DP
) : Button(context) {
    
    private var originalScaleX: Float = 1.0f
    private var originalScaleY: Float = 1.0f
    private var originalAlpha: Float = 1.0f
    
    init {
        setupTouchFriendlyButton()
    }
    
    private fun setupTouchFriendlyButton() {
        // Ensure minimum touch size
        ensureMinimumTouchSize()
        
        // Add touch feedback
        setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    originalScaleX = scaleX
                    originalScaleY = scaleY
                    originalAlpha = alpha
                    
                    // Animate touch feedback
                    animateTouchDown()
                    
                    // Haptic feedback
                    addHapticFeedback()
                    
                    true
                }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                    // Animate back to original state
                    animateTouchUp()
                    false
                }
                else -> false
            }
        }
        
        // Configure button appearance
        configureAppearance()
    }
    
    private fun ensureMinimumTouchSize() {
        val minimumSizePx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            minimumSizeDp,
            resources.displayMetrics
        ).toInt()
        
        val layoutParams = layoutParams ?: ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        )
        
        layoutParams.width = maxOf(layoutParams.width, minimumSizePx)
        layoutParams.height = maxOf(layoutParams.height, minimumSizePx)
        
        this.layoutParams = layoutParams
    }
    
    private fun configureAppearance() {
        // Set text color
        setTextColor(Color.WHITE)
        
        // Set text size
        textSize = 16f
        
        // Set typeface
        typeface = android.graphics.Typeface.DEFAULT_BOLD
        
        // Set padding
        val paddingPx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            TouchFriendlyConfig.TOUCH_PADDING_DP,
            resources.displayMetrics
        ).toInt()
        
        setPadding(paddingPx)
        
        // Set background
        val backgroundDrawable = GradientDrawable().apply {
            cornerRadius = TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP,
                12f,
                resources.displayMetrics
            )
            setColor(Color.argb(25, 255, 255, 255)) // 10% white
            setStroke(
                TypedValue.applyDimension(
                    TypedValue.COMPLEX_UNIT_DIP,
                    1f,
                    resources.displayMetrics
                ).toInt(),
                Color.argb(51, 255, 255, 255) // 20% white
            )
        }
        
        background = backgroundDrawable
    }
    
    private fun animateTouchDown() {
        animate()
            .scaleX(TouchFriendlyConfig.SCALE_FACTOR)
            .scaleY(TouchFriendlyConfig.SCALE_FACTOR)
            .alpha(TouchFriendlyConfig.ALPHA_FACTOR)
            .setDuration(TouchFriendlyConfig.ANIMATION_DURATION_MS)
            .start()
    }
    
    private fun animateTouchUp() {
        animate()
            .scaleX(originalScaleX)
            .scaleY(originalScaleY)
            .alpha(originalAlpha)
            .setDuration(TouchFriendlyConfig.ANIMATION_DURATION_MS)
            .start()
    }
    
    private fun addHapticFeedback() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            vibrator.vibrate(VibrationEffect.createOneShot(50, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }
}

// MARK: - Touch-Friendly Card
class TouchFriendlyCard @JvmOverloads constructor(
    context: Context,
    private val minimumSizeDp: Float = TouchFriendlyConfig.MINIMUM_TOUCH_SIZE_DP
) : LinearLayout(context) {
    
    private var originalScaleX: Float = 1.0f
    private var originalScaleY: Float = 1.0f
    private var originalAlpha: Float = 1.0f
    private var onTap: (() -> Unit)? = null
    
    init {
        setupTouchFriendlyCard()
    }
    
    private fun setupTouchFriendlyCard() {
        // Ensure minimum touch size
        ensureMinimumTouchSize()
        
        // Add touch feedback
        setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    originalScaleX = scaleX
                    originalScaleY = scaleY
                    originalAlpha = alpha
                    
                    // Animate touch feedback
                    animateTouchDown()
                    
                    // Haptic feedback
                    addHapticFeedback()
                    
                    true
                }
                MotionEvent.ACTION_UP -> {
                    // Animate back to original state
                    animateTouchUp()
                    
                    // Call onTap
                    onTap?.invoke()
                    
                    false
                }
                MotionEvent.ACTION_CANCEL -> {
                    // Animate back to original state
                    animateTouchUp()
                    false
                }
                else -> false
            }
        }
        
        // Configure appearance
        configureAppearance()
    }
    
    private fun ensureMinimumTouchSize() {
        val minimumSizePx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            minimumSizeDp,
            resources.displayMetrics
        ).toInt()
        
        val layoutParams = layoutParams ?: ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        )
        
        layoutParams.width = maxOf(layoutParams.width, minimumSizePx)
        layoutParams.height = maxOf(layoutParams.height, minimumSizePx)
        
        this.layoutParams = layoutParams
    }
    
    private fun configureAppearance() {
        // Set orientation
        orientation = VERTICAL
        
        // Set background
        val backgroundDrawable = GradientDrawable().apply {
            cornerRadius = TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP,
                12f,
                resources.displayMetrics
            )
            setColor(Color.argb(25, 255, 255, 255)) // 10% white
            setStroke(
                TypedValue.applyDimension(
                    TypedValue.COMPLEX_UNIT_DIP,
                    1f,
                    resources.displayMetrics
                ).toInt(),
                Color.argb(51, 255, 255, 255) // 20% white
            )
        }
        
        background = backgroundDrawable
        
        // Set padding
        val paddingPx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            TouchFriendlyConfig.TOUCH_PADDING_DP,
            resources.displayMetrics
        ).toInt()
        
        setPadding(paddingPx)
        
        // Set elevation
        ViewCompat.setElevation(this, 4f)
    }
    
    private fun animateTouchDown() {
        animate()
            .scaleX(TouchFriendlyConfig.SCALE_FACTOR)
            .scaleY(TouchFriendlyConfig.SCALE_FACTOR)
            .alpha(TouchFriendlyConfig.ALPHA_FACTOR)
            .setDuration(TouchFriendlyConfig.ANIMATION_DURATION_MS)
            .start()
    }
    
    private fun animateTouchUp() {
        animate()
            .scaleX(originalScaleX)
            .scaleY(originalScaleY)
            .alpha(originalAlpha)
            .setDuration(TouchFriendlyConfig.ANIMATION_DURATION_MS)
            .start()
    }
    
    private fun addHapticFeedback() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            vibrator.vibrate(VibrationEffect.createOneShot(30, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }
    
    fun setOnTapListener(listener: () -> Unit) {
        onTap = listener
    }
}

// MARK: - Touch-Friendly Switch
class TouchFriendlySwitch @JvmOverloads constructor(
    context: Context,
    private val minimumSizeDp: Float = TouchFriendlyConfig.MINIMUM_TOUCH_SIZE_DP
) : Switch(context) {
    
    init {
        setupTouchFriendlySwitch()
    }
    
    private fun setupTouchFriendlySwitch() {
        // Ensure minimum touch size
        ensureMinimumTouchSize()
        
        // Add touch feedback
        setOnCheckedChangeListener { _, _ ->
            addHapticFeedback()
        }
        
        // Configure appearance
        configureAppearance()
    }
    
    private fun ensureMinimumTouchSize() {
        val minimumSizePx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            minimumSizeDp,
            resources.displayMetrics
        ).toInt()
        
        val layoutParams = layoutParams ?: ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        )
        
        layoutParams.width = maxOf(layoutParams.width, minimumSizePx)
        layoutParams.height = maxOf(layoutParams.height, minimumSizePx)
        
        this.layoutParams = layoutParams
    }
    
    private fun configureAppearance() {
        // Set colors
        thumbTintList = ContextCompat.getColorStateList(context, android.R.color.white)
        trackTintList = ContextCompat.getColorStateList(context, android.R.color.white)
        
        // Set scale
        scaleX = 1.2f
        scaleY = 1.2f
    }
    
    private fun addHapticFeedback() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            vibrator.vibrate(VibrationEffect.createOneShot(30, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }
}

// MARK: - Touch-Friendly Slider
class TouchFriendlySlider @JvmOverloads constructor(
    context: Context,
    private val minimumSizeDp: Float = TouchFriendlyConfig.MINIMUM_TOUCH_SIZE_DP
) : SeekBar(context) {
    
    init {
        setupTouchFriendlySlider()
    }
    
    private fun setupTouchFriendlySlider() {
        // Ensure minimum touch size
        ensureMinimumTouchSize()
        
        // Add touch feedback
        setOnSeekBarChangeListener(object : OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                if (fromUser) {
                    addHapticFeedback()
                }
            }
            
            override fun onStartTrackingTouch(seekBar: SeekBar?) {
                // Optional: Add haptic feedback when starting to drag
            }
            
            override fun onStopTrackingTouch(seekBar: SeekBar?) {
                // Optional: Add haptic feedback when stopping drag
            }
        })
        
        // Configure appearance
        configureAppearance()
    }
    
    private fun ensureMinimumTouchSize() {
        val minimumSizePx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            minimumSizeDp,
            resources.displayMetrics
        ).toInt()
        
        val layoutParams = layoutParams ?: ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        )
        
        layoutParams.height = maxOf(layoutParams.height, minimumSizePx)
        
        this.layoutParams = layoutParams
    }
    
    private fun configureAppearance() {
        // Set colors
        progressTintList = ContextCompat.getColorStateList(context, android.R.color.white)
        thumbTintList = ContextCompat.getColorStateList(context, android.R.color.white)
        
        // Set scale
        scaleY = 1.5f
    }
    
    private fun addHapticFeedback() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            vibrator.vibrate(VibrationEffect.createOneShot(20, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }
}

// MARK: - Touch-Friendly Text Field
class TouchFriendlyTextField @JvmOverloads constructor(
    context: Context,
    private val minimumSizeDp: Float = TouchFriendlyConfig.MINIMUM_TOUCH_SIZE_DP
) : EditText(context) {
    
    init {
        setupTouchFriendlyTextField()
    }
    
    private fun setupTouchFriendlyTextField() {
        // Ensure minimum touch size
        ensureMinimumTouchSize()
        
        // Configure appearance
        configureAppearance()
    }
    
    private fun ensureMinimumTouchSize() {
        val minimumSizePx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            minimumSizeDp,
            resources.displayMetrics
        ).toInt()
        
        val layoutParams = layoutParams ?: ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        )
        
        layoutParams.height = maxOf(layoutParams.height, minimumSizePx)
        
        this.layoutParams = layoutParams
    }
    
    private fun configureAppearance() {
        // Set background
        val backgroundDrawable = GradientDrawable().apply {
            cornerRadius = TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP,
                8f,
                resources.displayMetrics
            )
            setColor(Color.argb(25, 255, 255, 255)) // 10% white
            setStroke(
                TypedValue.applyDimension(
                    TypedValue.COMPLEX_UNIT_DIP,
                    1f,
                    resources.displayMetrics
                ).toInt(),
                Color.argb(51, 255, 255, 255) // 20% white
            )
        }
        
        background = backgroundDrawable
        
        // Set text color
        setTextColor(Color.WHITE)
        
        // Set hint color
        setHintTextColor(Color.argb(153, 255, 255, 255)) // 60% white
        
        // Set text size
        textSize = 16f
        
        // Set padding
        val paddingPx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            12f,
            resources.displayMetrics
        ).toInt()
        
        setPadding(paddingPx, paddingPx, paddingPx, paddingPx)
        
        // Set input type
        inputType = android.text.InputType.TYPE_CLASS_TEXT
        imeOptions = android.view.inputmethod.EditorInfo.IME_ACTION_DONE
    }
}

// MARK: - Touch-Friendly List Item
class TouchFriendlyListItem @JvmOverloads constructor(
    context: Context,
    private val minimumSizeDp: Float = TouchFriendlyConfig.MINIMUM_TOUCH_SIZE_DP
) : LinearLayout(context) {
    
    private var originalScaleX: Float = 1.0f
    private var originalScaleY: Float = 1.0f
    private var originalAlpha: Float = 1.0f
    private var onTap: (() -> Unit)? = null
    
    init {
        setupTouchFriendlyListItem()
    }
    
    private fun setupTouchFriendlyListItem() {
        // Ensure minimum touch size
        ensureMinimumTouchSize()
        
        // Add touch feedback
        setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    originalScaleX = scaleX
                    originalScaleY = scaleY
                    originalAlpha = alpha
                    
                    // Animate touch feedback
                    animateTouchDown()
                    
                    // Haptic feedback
                    addHapticFeedback()
                    
                    true
                }
                MotionEvent.ACTION_UP -> {
                    // Animate back to original state
                    animateTouchUp()
                    
                    // Call onTap
                    onTap?.invoke()
                    
                    false
                }
                MotionEvent.ACTION_CANCEL -> {
                    // Animate back to original state
                    animateTouchUp()
                    false
                }
                else -> false
            }
        }
        
        // Configure appearance
        configureAppearance()
    }
    
    private fun ensureMinimumTouchSize() {
        val minimumSizePx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            minimumSizeDp,
            resources.displayMetrics
        ).toInt()
        
        val layoutParams = layoutParams ?: ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        )
        
        layoutParams.height = maxOf(layoutParams.height, minimumSizePx)
        
        this.layoutParams = layoutParams
    }
    
    private fun configureAppearance() {
        // Set orientation
        orientation = HORIZONTAL
        
        // Set background
        val backgroundDrawable = GradientDrawable().apply {
            cornerRadius = TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP,
                8f,
                resources.displayMetrics
            )
            setColor(Color.argb(25, 255, 255, 255)) // 10% white
            setStroke(
                TypedValue.applyDimension(
                    TypedValue.COMPLEX_UNIT_DIP,
                    1f,
                    resources.displayMetrics
                ).toInt(),
                Color.argb(51, 255, 255, 255) // 20% white
            )
        }
        
        background = backgroundDrawable
        
        // Set padding
        val paddingPx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            TouchFriendlyConfig.TOUCH_PADDING_DP,
            resources.displayMetrics
        ).toInt()
        
        setPadding(paddingPx)
        
        // Set elevation
        ViewCompat.setElevation(this, 2f)
    }
    
    private fun animateTouchDown() {
        animate()
            .scaleX(TouchFriendlyConfig.SCALE_FACTOR)
            .scaleY(TouchFriendlyConfig.SCALE_FACTOR)
            .alpha(TouchFriendlyConfig.ALPHA_FACTOR)
            .setDuration(TouchFriendlyConfig.ANIMATION_DURATION_MS)
            .start()
    }
    
    private fun animateTouchUp() {
        animate()
            .scaleX(originalScaleX)
            .scaleY(originalScaleY)
            .alpha(originalAlpha)
            .setDuration(TouchFriendlyConfig.ANIMATION_DURATION_MS)
            .start()
    }
    
    private fun addHapticFeedback() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            vibrator.vibrate(VibrationEffect.createOneShot(30, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }
    
    fun setOnTapListener(listener: () -> Unit) {
        onTap = listener
    }
}

// MARK: - Touch-Friendly Utility Functions
object TouchFriendlyUtils {
    
    fun ensureMinimumTouchSize(view: View, minimumSizeDp: Float = TouchFriendlyConfig.MINIMUM_TOUCH_SIZE_DP) {
        val minimumSizePx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            minimumSizeDp,
            view.context.resources.displayMetrics
        ).toInt()
        
        val layoutParams = view.layoutParams ?: ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        )
        
        layoutParams.width = maxOf(layoutParams.width, minimumSizePx)
        layoutParams.height = maxOf(layoutParams.height, minimumSizePx)
        
        view.layoutParams = layoutParams
    }
    
    fun addTouchFeedback(
        view: View,
        scaleFactor: Float = TouchFriendlyConfig.SCALE_FACTOR,
        alphaFactor: Float = TouchFriendlyConfig.ALPHA_FACTOR
    ) {
        var originalScaleX = 1.0f
        var originalScaleY = 1.0f
        var originalAlpha = 1.0f
        
        view.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    originalScaleX = view.scaleX
                    originalScaleY = view.scaleY
                    originalAlpha = view.alpha
                    
                    view.animate()
                        .scaleX(scaleFactor)
                        .scaleY(scaleFactor)
                        .alpha(alphaFactor)
                        .setDuration(TouchFriendlyConfig.ANIMATION_DURATION_MS)
                        .start()
                    
                    true
                }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                    view.animate()
                        .scaleX(originalScaleX)
                        .scaleY(originalScaleY)
                        .alpha(originalAlpha)
                        .setDuration(TouchFriendlyConfig.ANIMATION_DURATION_MS)
                        .start()
                    
                    false
                }
                else -> false
            }
        }
    }
    
    fun addHapticFeedback(view: View, duration: Long = 50) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val vibrator = view.context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            vibrator.vibrate(VibrationEffect.createOneShot(duration, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }
}

// MARK: - Touch-Friendly Extensions
fun View.makeTouchFriendly(minimumSizeDp: Float = TouchFriendlyConfig.MINIMUM_TOUCH_SIZE_DP) {
    TouchFriendlyUtils.ensureMinimumTouchSize(this, minimumSizeDp)
}

fun View.addTouchFeedback(
    scaleFactor: Float = TouchFriendlyConfig.SCALE_FACTOR,
    alphaFactor: Float = TouchFriendlyConfig.ALPHA_FACTOR
) {
    TouchFriendlyUtils.addTouchFeedback(this, scaleFactor, alphaFactor)
}

fun View.addHapticFeedback(duration: Long = 50) {
    TouchFriendlyUtils.addHapticFeedback(this, duration)
}

