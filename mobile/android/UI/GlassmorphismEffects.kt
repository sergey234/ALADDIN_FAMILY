/*
 * GlassmorphismEffects.kt
 * ALADDIN Mobile Security
 *
 * Glassmorphism UI Effects for Android
 * Modern glass-like visual effects with blur and transparency
 *
 * Created by ALADDIN Security Team
 * Date: 2025-01-27
 * Version: 1.0
 */

package com.aladdin.security.ui.glassmorphism

import android.content.Context
import android.graphics.*
import android.graphics.drawable.Drawable
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.FrameLayout
import android.widget.LinearLayout
import androidx.annotation.RequiresApi
import androidx.core.graphics.drawable.DrawableCompat
import androidx.core.view.ViewCompat
import androidx.core.view.setPadding

// MARK: - Glassmorphism Effect Types
enum class GlassmorphismStyle {
    LIGHT,      // Light glass effect
    MEDIUM,     // Medium glass effect
    HEAVY,      // Heavy glass effect
    FROSTED,    // Frosted glass effect
    CRYSTAL,    // Crystal clear effect
    STORM       // Storm sky themed effect
}

// MARK: - Glassmorphism Configuration
data class GlassmorphismConfig(
    val style: GlassmorphismStyle,
    val blurRadius: Float,
    val opacity: Float,
    val cornerRadius: Float,
    val borderWidth: Float,
    val borderColor: Int,
    val shadowRadius: Float,
    val shadowOpacity: Float,
    val shadowOffsetX: Float,
    val shadowOffsetY: Float,
    val shadowColor: Int
) {
    companion object {
        val LIGHT = GlassmorphismConfig(
            style = GlassmorphismStyle.LIGHT,
            blurRadius = 10f,
            opacity = 0.1f,
            cornerRadius = 12f,
            borderWidth = 1f,
            borderColor = Color.argb(51, 255, 255, 255), // 20% white
            shadowRadius = 8f,
            shadowOpacity = 0.1f,
            shadowOffsetX = 0f,
            shadowOffsetY = 4f,
            shadowColor = Color.argb(25, 0, 0, 0) // 10% black
        )
        
        val MEDIUM = GlassmorphismConfig(
            style = GlassmorphismStyle.MEDIUM,
            blurRadius = 20f,
            opacity = 0.15f,
            cornerRadius = 16f,
            borderWidth = 1.5f,
            borderColor = Color.argb(76, 255, 255, 255), // 30% white
            shadowRadius = 12f,
            shadowOpacity = 0.15f,
            shadowOffsetX = 0f,
            shadowOffsetY = 6f,
            shadowColor = Color.argb(38, 0, 0, 0) // 15% black
        )
        
        val HEAVY = GlassmorphismConfig(
            style = GlassmorphismStyle.HEAVY,
            blurRadius = 30f,
            opacity = 0.2f,
            cornerRadius = 20f,
            borderWidth = 2f,
            borderColor = Color.argb(102, 255, 255, 255), // 40% white
            shadowRadius = 16f,
            shadowOpacity = 0.2f,
            shadowOffsetX = 0f,
            shadowOffsetY = 8f,
            shadowColor = Color.argb(51, 0, 0, 0) // 20% black
        )
        
        val FROSTED = GlassmorphismConfig(
            style = GlassmorphismStyle.FROSTED,
            blurRadius = 25f,
            opacity = 0.25f,
            cornerRadius = 18f,
            borderWidth = 1.5f,
            borderColor = Color.argb(127, 255, 255, 255), // 50% white
            shadowRadius = 14f,
            shadowOpacity = 0.18f,
            shadowOffsetX = 0f,
            shadowOffsetY = 7f,
            shadowColor = Color.argb(46, 0, 0, 0) // 18% black
        )
        
        val CRYSTAL = GlassmorphismConfig(
            style = GlassmorphismStyle.CRYSTAL,
            blurRadius = 15f,
            opacity = 0.08f,
            cornerRadius = 14f,
            borderWidth = 0.5f,
            borderColor = Color.argb(153, 255, 255, 255), // 60% white
            shadowRadius = 10f,
            shadowOpacity = 0.12f,
            shadowOffsetX = 0f,
            shadowOffsetY = 5f,
            shadowColor = Color.argb(30, 0, 0, 0) // 12% black
        )
        
        val STORM = GlassmorphismConfig(
            style = GlassmorphismStyle.STORM,
            blurRadius = 22f,
            opacity = 0.18f,
            cornerRadius = 16f,
            borderWidth = 1.5f,
            borderColor = Color.argb(76, 245, 158, 11), // Golden accent
            shadowRadius = 13f,
            shadowOpacity = 0.16f,
            shadowOffsetX = 0f,
            shadowOffsetY = 6f,
            shadowColor = Color.argb(41, 10, 17, 40) // Storm sky color
        )
        
        // Storm Sky themed configurations
        val STORM_SKY_LIGHT = GlassmorphismConfig(
            style = GlassmorphismStyle.STORM,
            blurRadius = 15f,
            opacity = 0.12f,
            cornerRadius = 12f,
            borderWidth = 1f,
            borderColor = Color.argb(51, 245, 158, 11), // 20% golden
            shadowRadius = 8f,
            shadowOpacity = 0.1f,
            shadowOffsetX = 0f,
            shadowOffsetY = 4f,
            shadowColor = Color.argb(25, 10, 17, 40) // 10% storm sky
        )
        
        val STORM_SKY_MEDIUM = GlassmorphismConfig(
            style = GlassmorphismStyle.STORM,
            blurRadius = 22f,
            opacity = 0.18f,
            cornerRadius = 16f,
            borderWidth = 1.5f,
            borderColor = Color.argb(76, 245, 158, 11), // 30% golden
            shadowRadius = 13f,
            shadowOpacity = 0.16f,
            shadowOffsetX = 0f,
            shadowOffsetY = 6f,
            shadowColor = Color.argb(41, 10, 17, 40) // 16% storm sky
        )
        
        val STORM_SKY_HEAVY = GlassmorphismConfig(
            style = GlassmorphismStyle.STORM,
            blurRadius = 30f,
            opacity = 0.25f,
            cornerRadius = 20f,
            borderWidth = 2f,
            borderColor = Color.argb(102, 245, 158, 11), // 40% golden
            shadowRadius = 18f,
            shadowOpacity = 0.22f,
            shadowOffsetX = 0f,
            shadowOffsetY = 8f,
            shadowColor = Color.argb(56, 10, 17, 40) // 22% storm sky
        )
    }
}

// MARK: - Glassmorphism Drawable
class GlassmorphismDrawable(
    private val config: GlassmorphismConfig,
    private val context: Context
) : Drawable() {
    
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val borderPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val shadowPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    
    init {
        setupPaints()
    }
    
    private fun setupPaints() {
        // Background paint
        paint.color = Color.argb(
            (255 * config.opacity).toInt(),
            255, 255, 255
        )
        paint.style = Paint.Style.FILL
        
        // Border paint
        borderPaint.color = config.borderColor
        borderPaint.style = Paint.Style.STROKE
        borderPaint.strokeWidth = config.borderWidth
        
        // Shadow paint
        shadowPaint.color = config.shadowColor
        shadowPaint.style = Paint.Style.FILL
        shadowPaint.maskFilter = BlurMaskFilter(config.shadowRadius, BlurMaskFilter.Blur.NORMAL)
    }
    
    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val rect = RectF(
            bounds.left.toFloat(),
            bounds.top.toFloat(),
            bounds.right.toFloat(),
            bounds.bottom.toFloat()
        )
        
        // Draw shadow
        canvas.drawRoundRect(
            rect.left + config.shadowOffsetX,
            rect.top + config.shadowOffsetY,
            rect.right + config.shadowOffsetX,
            rect.bottom + config.shadowOffsetY,
            config.cornerRadius,
            config.cornerRadius,
            shadowPaint
        )
        
        // Draw background
        canvas.drawRoundRect(rect, config.cornerRadius, config.cornerRadius, paint)
        
        // Draw border
        canvas.drawRoundRect(rect, config.cornerRadius, config.cornerRadius, borderPaint)
    }
    
    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
        borderPaint.alpha = alpha
        shadowPaint.alpha = alpha
    }
    
    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
        borderPaint.colorFilter = colorFilter
        shadowPaint.colorFilter = colorFilter
    }
    
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}

// MARK: - Glassmorphism View
class GlassmorphismView @JvmOverloads constructor(
    context: Context,
    private val config: GlassmorphismConfig = GlassmorphismConfig.MEDIUM
) : FrameLayout(context) {
    
    private val glassmorphismDrawable: GlassmorphismDrawable
    
    init {
        glassmorphismDrawable = GlassmorphismDrawable(config, context)
        background = glassmorphismDrawable
    }
    
    fun updateConfig(newConfig: GlassmorphismConfig) {
        val newDrawable = GlassmorphismDrawable(newConfig, context)
        background = newDrawable
    }
    
    fun animateConfigChange(newConfig: GlassmorphismConfig, duration: Long = 300) {
        // Simple animation - in real implementation, use ValueAnimator
        updateConfig(newConfig)
    }
}

// MARK: - Glassmorphism Button
class GlassmorphismButton @JvmOverloads constructor(
    context: Context,
    private val config: GlassmorphismConfig = GlassmorphismConfig.MEDIUM
) : Button(context) {
    
    private val glassmorphismView: GlassmorphismView
    
    init {
        glassmorphismView = GlassmorphismView(context, config)
        setupButton()
    }
    
    private fun setupButton() {
        // Add glassmorphism view as background
        addView(glassmorphismView, 0)
        glassmorphismView.layoutParams = LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
        
        // Button styling
        setTextColor(Color.WHITE)
        textSize = 16f
        typeface = Typeface.DEFAULT_BOLD
        
        // Add touch effects
        setOnTouchListener { _, event ->
            when (event.action) {
                android.view.MotionEvent.ACTION_DOWN -> {
                    scaleX = 0.95f
                    scaleY = 0.95f
                    alpha = 0.8f
                }
                android.view.MotionEvent.ACTION_UP,
                android.view.MotionEvent.ACTION_CANCEL -> {
                    scaleX = 1.0f
                    scaleY = 1.0f
                    alpha = 1.0f
                }
            }
            false
        }
    }
    
    fun updateGlassmorphismConfig(newConfig: GlassmorphismConfig) {
        glassmorphismView.updateConfig(newConfig)
    }
}

// MARK: - Glassmorphism Card
class GlassmorphismCard @JvmOverloads constructor(
    context: Context,
    private val config: GlassmorphismConfig = GlassmorphismConfig.MEDIUM
) : FrameLayout(context) {
    
    private val glassmorphismView: GlassmorphismView
    private val contentView: LinearLayout
    
    init {
        glassmorphismView = GlassmorphismView(context, config)
        contentView = LinearLayout(context)
        setupCard()
    }
    
    private fun setupCard() {
        // Add glassmorphism view as background
        addView(glassmorphismView, 0)
        glassmorphismView.layoutParams = LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
        
        // Setup content view
        addView(contentView)
        contentView.layoutParams = LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
        contentView.setPadding(16)
        contentView.orientation = LinearLayout.VERTICAL
    }
    
    fun addContent(view: View) {
        contentView.addView(view)
    }
    
    fun updateGlassmorphismConfig(newConfig: GlassmorphismConfig) {
        glassmorphismView.updateConfig(newConfig)
    }
}

// MARK: - Glassmorphism Utility Functions
object GlassmorphismUtils {
    
    fun createGlassmorphismBackground(view: View, config: GlassmorphismConfig = GlassmorphismConfig.MEDIUM) {
        val glassmorphismView = GlassmorphismView(view.context, config)
        (view as? ViewGroup)?.addView(glassmorphismView, 0)
        
        glassmorphismView.layoutParams = ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
    }
    
    fun createGradientGlassmorphism(
        view: View,
        colors: IntArray,
        config: GlassmorphismConfig = GlassmorphismConfig.MEDIUM
    ) {
        val gradientDrawable = GradientDrawable(
            GradientDrawable.Orientation.TL_BR,
            colors
        )
        gradientDrawable.cornerRadius = config.cornerRadius
        
        val glassmorphismView = GlassmorphismView(view.context, config)
        glassmorphismView.background = gradientDrawable
        
        (view as? ViewGroup)?.addView(glassmorphismView, 0)
        glassmorphismView.layoutParams = ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
    }
    
    @RequiresApi(Build.VERSION_CODES.S)
    fun createBlurGlassmorphism(
        view: View,
        config: GlassmorphismConfig = GlassmorphismConfig.MEDIUM
    ) {
        val blurEffect = android.graphics.BlurMaskFilter(config.blurRadius, BlurMaskFilter.Blur.NORMAL)
        val glassmorphismView = GlassmorphismView(view.context, config)
        
        // Apply blur effect
        glassmorphismView.layerType = View.LAYER_TYPE_SOFTWARE
        glassmorphismView.setLayerType(View.LAYER_TYPE_SOFTWARE, null)
        
        (view as? ViewGroup)?.addView(glassmorphismView, 0)
        glassmorphismView.layoutParams = ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
    }
}

// MARK: - Glassmorphism Extension Functions
fun View.applyGlassmorphism(config: GlassmorphismConfig = GlassmorphismConfig.MEDIUM) {
    val glassmorphismView = GlassmorphismView(context, config)
    (parent as? ViewGroup)?.let { parentView ->
        val index = parentView.indexOfChild(this)
        parentView.addView(glassmorphismView, index)
        glassmorphismView.layoutParams = layoutParams
        layoutParams = ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
    }
}

fun Button.applyGlassmorphismButton(config: GlassmorphismConfig = GlassmorphismConfig.MEDIUM) {
    val glassmorphismButton = GlassmorphismButton(context, config)
    glassmorphismButton.text = text
    glassmorphismButton.setTextColor(textColors)
    glassmorphismButton.textSize = textSize
    glassmorphismButton.typeface = typeface
    
    (parent as? ViewGroup)?.let { parentView ->
        val index = parentView.indexOfChild(this)
        parentView.removeView(this)
        parentView.addView(glassmorphismButton, index)
    }
}

