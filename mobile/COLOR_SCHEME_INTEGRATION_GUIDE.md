# 🎨 ALADDIN Mobile App - Color Scheme Integration Guide

**Эксперт:** UI/UX Designer + Mobile Developer  
**Дата:** 2025-01-27  
**Цель:** Интеграция единой цветовой схемы "Грозовое небо с золотыми акцентами" в iOS и Android проекты

---

## 🌈 **ЕДИНАЯ ЦВЕТОВАЯ СХЕМА "ГРОЗОВОЕ НЕБО"**

### 🎯 **ОСНОВНЫЕ ЦВЕТА:**
- **Primary:** #1e3a5f (Синий грозового неба)
- **Secondary:** #0a1128 (Темно-синий глубокий)
- **Accent:** #F59E0B (Золотой основной)
- **Text:** #FFFFFF (Белый чистый)
- **Background:** Linear Gradient (0a1128 → 1e3a5f → 2e5090)

### 🎯 **СТАТУСНЫЕ ЦВЕТА:**
- **Success:** #10B981 (Изумрудный)
- **Warning:** #FCD34D (Золотой светлый)
- **Error:** #EF4444 (Рубиновый)
- **Info:** #60A5FA (Голубой молнии)

---

## 🍎 **iOS ИНТЕГРАЦИЯ**

### 📋 **1. StormSkyColors.swift (Обновленная версия):**
```swift
import UIKit
import SwiftUI

// MARK: - Storm Sky Color Scheme
struct StormSkyColors {
    
    // MARK: - Background Gradient Colors
    static let stormSkyDark = UIColor(hex: "#0a1128")     // Темно-синий глубокий
    static let stormSkyMain = UIColor(hex: "#1e3a5f")     // Синий грозового неба
    static let stormSkyMid = UIColor(hex: "#2e5090")      // Средний синий
    
    // MARK: - Accent Colors (Golden)
    static let goldMain = UIColor(hex: "#F59E0B")         // Золотой основной
    static let goldLight = UIColor(hex: "#FCD34D")        // Золотой светлый
    static let goldDark = UIColor(hex: "#D97706")         // Золотой темный
    
    // MARK: - Text & UI Element Colors
    static let white = UIColor.white                       // Белый чистый
    static let lightningBlue = UIColor(hex: "#60A5FA")    // Голубой молнии (info)
    static let successGreen = UIColor(hex: "#10B981")     // Изумрудный успех
    static let errorRed = UIColor(hex: "#EF4444")         // Рубиновый ошибка
    static let warningYellow = UIColor(hex: "#FCD34D")    // Золотой светлый (warning)
    
    // MARK: - Transparent Colors
    static let stormSkyMain80 = UIColor(hex: "#CC1e3a5f")  // 80% opacity
    static let goldMain30 = UIColor(hex: "#4DF59E0B")       // 30% opacity
    static let white60 = UIColor(hex: "#99FFFFFF")          // 60% opacity
    
    // MARK: - Gradients
    static let backgroundGradient: [UIColor] = [
        stormSkyDark,
        stormSkyMain,
        UIColor(hex: "#2e5090"),
        stormSkyMain,
        stormSkyDark
    ]
    
    static let goldGradient: [UIColor] = [
        goldMain,
        goldLight
    ]
    
    static let successGradient: [UIColor] = [
        successGreen,
        UIColor(hex: "#059669")
    ]
    
    static let errorGradient: [UIColor] = [
        errorRed,
        UIColor(hex: "#DC2626")
    ]
    
    // MARK: - Helper Functions
    static func getColorWithAlpha(_ color: UIColor, alpha: CGFloat) -> UIColor {
        return color.withAlphaComponent(alpha)
    }
    
    static func isLightColor(_ color: UIColor) -> Bool {
        var white: CGFloat = 0
        color.getWhite(&white, alpha: nil)
        return white > 0.5
    }
    
    static func getContrastColor(for color: UIColor) -> UIColor {
        return isLightColor(color) ? stormSkyDark : white
    }
}

// MARK: - UIColor Extension
extension UIColor {
    convenience init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        self.init(red: CGFloat(r) / 255, green: CGFloat(g) / 255, blue: CGFloat(b) / 255, alpha: CGFloat(a) / 255)
    }
}

// MARK: - SwiftUI Color Extension
@available(iOS 13.0, *)
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - SwiftUI Storm Sky Colors
@available(iOS 13.0, *)
extension Color {
    static let stormSkyDark = Color(hex: "#0a1128")
    static let stormSkyMain = Color(hex: "#1e3a5f")
    static let stormSkyMid = Color(hex: "#2e5090")
    static let goldMain = Color(hex: "#F59E0B")
    static let goldLight = Color(hex: "#FCD34D")
    static let goldDark = Color(hex: "#D97706")
    static let lightningBlue = Color(hex: "#60A5FA")
    static let successGreen = Color(hex: "#10B981")
    static let errorRed = Color(hex: "#EF4444")
    static let warningYellow = Color(hex: "#FCD34D")
}
```

### 📋 **2. GradientUtils.swift:**
```swift
import UIKit

class GradientUtils {
    
    enum GradientDirection {
        case topToBottom
        case leftToRight
        case topLeftToBottomRight
        case topRightToBottomLeft
    }
    
    static func createGradientLayer(
        colors: [UIColor],
        direction: GradientDirection = .topToBottom,
        frame: CGRect
    ) -> CAGradientLayer {
        let gradientLayer = CAGradientLayer()
        gradientLayer.colors = colors.map { $0.cgColor }
        gradientLayer.frame = frame
        
        switch direction {
        case .topToBottom:
            gradientLayer.startPoint = CGPoint(x: 0.5, y: 0.0)
            gradientLayer.endPoint = CGPoint(x: 0.5, y: 1.0)
        case .leftToRight:
            gradientLayer.startPoint = CGPoint(x: 0.0, y: 0.5)
            gradientLayer.endPoint = CGPoint(x: 1.0, y: 0.5)
        case .topLeftToBottomRight:
            gradientLayer.startPoint = CGPoint(x: 0.0, y: 0.0)
            gradientLayer.endPoint = CGPoint(x: 1.0, y: 1.0)
        case .topRightToBottomLeft:
            gradientLayer.startPoint = CGPoint(x: 1.0, y: 0.0)
            gradientLayer.endPoint = CGPoint(x: 0.0, y: 1.0)
        }
        
        return gradientLayer
    }
    
    static func applyGradientBackground(
        to view: UIView,
        colors: [UIColor],
        direction: GradientDirection = .topToBottom
    ) {
        let gradientLayer = createGradientLayer(
            colors: colors,
            direction: direction,
            frame: view.bounds
        )
        
        // Remove existing gradient layers
        view.layer.sublayers?.removeAll { $0 is CAGradientLayer }
        
        // Insert gradient at the bottom
        view.layer.insertSublayer(gradientLayer, at: 0)
        
        // Update frame when view bounds change
        DispatchQueue.main.async {
            gradientLayer.frame = view.bounds
        }
    }
    
    static func createGradientButton(
        colors: [UIColor],
        cornerRadius: CGFloat = 8.0
    ) -> CAGradientLayer {
        let gradientLayer = CAGradientLayer()
        gradientLayer.colors = colors.map { $0.cgColor }
        gradientLayer.cornerRadius = cornerRadius
        gradientLayer.startPoint = CGPoint(x: 0.0, y: 0.0)
        gradientLayer.endPoint = CGPoint(x: 1.0, y: 1.0)
        return gradientLayer
    }
}
```

### 📋 **3. StormSkyTheme.swift:**
```swift
import UIKit

class StormSkyTheme {
    
    // MARK: - Typography
    struct Typography {
        static let h1 = UIFont.systemFont(ofSize: 28, weight: .bold)
        static let h2 = UIFont.systemFont(ofSize: 24, weight: .bold)
        static let h3 = UIFont.systemFont(ofSize: 20, weight: .semibold)
        static let body = UIFont.systemFont(ofSize: 16, weight: .regular)
        static let caption = UIFont.systemFont(ofSize: 14, weight: .regular)
        static let small = UIFont.systemFont(ofSize: 12, weight: .regular)
    }
    
    // MARK: - Spacing
    struct Spacing {
        static let xs: CGFloat = 4
        static let sm: CGFloat = 8
        static let md: CGFloat = 16
        static let lg: CGFloat = 24
        static let xl: CGFloat = 32
        static let xxl: CGFloat = 48
    }
    
    // MARK: - Corner Radius
    struct CornerRadius {
        static let sm: CGFloat = 4
        static let md: CGFloat = 8
        static let lg: CGFloat = 12
        static let xl: CGFloat = 16
        static let round: CGFloat = 50
    }
    
    // MARK: - Shadows
    struct Shadow {
        static let light = CGSize(width: 0, height: 2)
        static let medium = CGSize(width: 0, height: 4)
        static let heavy = CGSize(width: 0, height: 8)
        
        static let lightRadius: CGFloat = 2
        static let mediumRadius: CGFloat = 4
        static let heavyRadius: CGFloat = 8
        
        static let lightOpacity: Float = 0.1
        static let mediumOpacity: Float = 0.2
        static let heavyOpacity: Float = 0.3
    }
    
    // MARK: - Apply Theme
    static func applyTheme(to view: UIView) {
        // Apply background gradient
        GradientUtils.applyGradientBackground(
            to: view,
            colors: StormSkyColors.backgroundGradient
        )
    }
    
    static func applyCardStyle(to view: UIView) {
        view.backgroundColor = StormSkyColors.stormSkyMain80
        view.layer.cornerRadius = CornerRadius.lg
        view.layer.borderWidth = 1
        view.layer.borderColor = StormSkyColors.goldMain30.cgColor
        view.layer.shadowOffset = Shadow.light
        view.layer.shadowRadius = Shadow.lightRadius
        view.layer.shadowOpacity = Shadow.lightOpacity
        view.layer.shadowColor = UIColor.black.cgColor
    }
    
    static func applyButtonStyle(to button: UIButton, style: ButtonStyle = .primary) {
        switch style {
        case .primary:
            button.backgroundColor = StormSkyColors.goldMain
            button.setTitleColor(StormSkyColors.stormSkyDark, for: .normal)
        case .secondary:
            button.backgroundColor = .clear
            button.layer.borderWidth = 1
            button.layer.borderColor = StormSkyColors.goldMain.cgColor
            button.setTitleColor(StormSkyColors.goldMain, for: .normal)
        case .success:
            button.backgroundColor = StormSkyColors.successGreen
            button.setTitleColor(StormSkyColors.white, for: .normal)
        case .error:
            button.backgroundColor = StormSkyColors.errorRed
            button.setTitleColor(StormSkyColors.white, for: .normal)
        }
        
        button.layer.cornerRadius = CornerRadius.md
        button.titleLabel?.font = Typography.body
        button.layer.shadowOffset = Shadow.light
        button.layer.shadowRadius = Shadow.lightRadius
        button.layer.shadowOpacity = Shadow.lightOpacity
        button.layer.shadowColor = UIColor.black.cgColor
    }
    
    enum ButtonStyle {
        case primary
        case secondary
        case success
        case error
    }
}
```

---

## 🤖 **ANDROID ИНТЕГРАЦИЯ**

### 📋 **1. colors.xml (Обновленная версия):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Storm Sky Color Scheme -->
    
    <!-- Background Gradient Colors -->
    <color name="storm_sky_dark">#0a1128</color>      <!-- Темно-синий глубокий -->
    <color name="storm_sky_main">#1e3a5f</color>      <!-- Синий грозового неба -->
    <color name="storm_sky_mid">#2e5090</color>       <!-- Средний синий -->
    
    <!-- Accent Colors (Golden) -->
    <color name="gold_main">#F59E0B</color>           <!-- Золотой основной -->
    <color name="gold_light">#FCD34D</color>          <!-- Золотой светлый -->
    <color name="gold_dark">#D97706</color>           <!-- Золотой темный -->
    
    <!-- Text & UI Element Colors -->
    <color name="white">#FFFFFF</color>               <!-- Белый чистый -->
    <color name="lightning_blue">#60A5FA</color>      <!-- Голубой молнии (info) -->
    <color name="success_green">#10B981</color>       <!-- Изумрудный успех -->
    <color name="error_red">#EF4444</color>           <!-- Рубиновый ошибка -->
    <color name="warning_yellow">#FCD34D</color>      <!-- Золотой светлый (warning) -->
    
    <!-- Transparent Colors -->
    <color name="storm_sky_main_80">#CC1e3a5f</color>  <!-- 80% opacity -->
    <color name="gold_main_30">#4DF59E0B</color>       <!-- 30% opacity -->
    <color name="white_60">#99FFFFFF</color>           <!-- 60% opacity -->
    
    <!-- Gradient Colors -->
    <color name="gradient_start">#0a1128</color>
    <color name="gradient_mid">#1e3a5f</color>
    <color name="gradient_end">#2e5090</color>
    
    <!-- Status Colors -->
    <color name="status_online">#10B981</color>        <!-- Online status -->
    <color name="status_offline">#EF4444</color>       <!-- Offline status -->
    <color name="status_warning">#FCD34D</color>       <!-- Warning status -->
    <color name="status_info">#60A5FA</color>          <!-- Info status -->
</resources>
```

### 📋 **2. drawable/gradient_background.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <gradient
        android:angle="270"
        android:startColor="@color/gradient_start"
        android:centerColor="@color/gradient_mid"
        android:endColor="@color/gradient_end"
        android:type="linear" />
</shape>
```

### 📋 **3. drawable/card_background.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="@color/storm_sky_main_80" />
    <corners android:radius="12dp" />
    <stroke
        android:width="1dp"
        android:color="@color/gold_main_30" />
</shape>
```

### 📋 **4. drawable/button_background.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="@color/gold_main" />
    <corners android:radius="8dp" />
</shape>
```

### 📋 **5. drawable/button_border.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="@android:color/transparent" />
    <corners android:radius="8dp" />
    <stroke
        android:width="1dp"
        android:color="@color/gold_main" />
</shape>
```

### 📋 **6. StormSkyTheme.kt:**
```kotlin
package com.aladdin.ui.theme

import android.content.Context
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.view.View
import androidx.core.content.ContextCompat
import com.aladdin.R

object StormSkyTheme {
    
    // MARK: - Typography
    object Typography {
        const val H1_SIZE = 28f
        const val H2_SIZE = 24f
        const val H3_SIZE = 20f
        const val BODY_SIZE = 16f
        const val CAPTION_SIZE = 14f
        const val SMALL_SIZE = 12f
    }
    
    // MARK: - Spacing
    object Spacing {
        const val XS = 4
        const val SM = 8
        const val MD = 16
        const val LG = 24
        const val XL = 32
        const val XXL = 48
    }
    
    // MARK: - Corner Radius
    object CornerRadius {
        const val SM = 4f
        const val MD = 8f
        const val LG = 12f
        const val XL = 16f
        const val ROUND = 50f
    }
    
    // MARK: - Apply Theme
    fun applyTheme(view: View) {
        view.setBackgroundResource(R.drawable.gradient_background)
    }
    
    fun applyCardStyle(view: View) {
        view.setBackgroundResource(R.drawable.card_background)
    }
    
    fun applyButtonStyle(view: View, style: ButtonStyle = ButtonStyle.PRIMARY) {
        when (style) {
            ButtonStyle.PRIMARY -> {
                view.setBackgroundResource(R.drawable.button_background)
            }
            ButtonStyle.SECONDARY -> {
                view.setBackgroundResource(R.drawable.button_border)
            }
            ButtonStyle.SUCCESS -> {
                val drawable = GradientDrawable().apply {
                    setColor(ContextCompat.getColor(view.context, R.color.success_green))
                    cornerRadius = CornerRadius.MD
                }
                view.background = drawable
            }
            ButtonStyle.ERROR -> {
                val drawable = GradientDrawable().apply {
                    setColor(ContextCompat.getColor(view.context, R.color.error_red))
                    cornerRadius = CornerRadius.MD
                }
                view.background = drawable
            }
        }
    }
    
    enum class ButtonStyle {
        PRIMARY,
        SECONDARY,
        SUCCESS,
        ERROR
    }
}
```

### 📋 **7. GradientUtils.kt:**
```kotlin
package com.aladdin.utils

import android.content.Context
import android.graphics.drawable.GradientDrawable
import android.view.View
import com.aladdin.R
import com.aladdin.ui.colors.StormSkyColors

object GradientUtils {
    
    enum class GradientDirection {
        TOP_TO_BOTTOM,
        LEFT_TO_RIGHT,
        TOP_LEFT_TO_BOTTOM_RIGHT,
        TOP_RIGHT_TO_BOTTOM_LEFT
    }
    
    fun applyGradientBackground(
        view: View,
        colors: IntArray,
        direction: GradientDirection = GradientDirection.TOP_TO_BOTTOM
    ) {
        val gradientDrawable = GradientDrawable().apply {
            this.colors = colors
            when (direction) {
                GradientDirection.TOP_TO_BOTTOM -> {
                    orientation = GradientDrawable.Orientation.TOP_BOTTOM
                }
                GradientDirection.LEFT_TO_RIGHT -> {
                    orientation = GradientDrawable.Orientation.LEFT_RIGHT
                }
                GradientDirection.TOP_LEFT_TO_BOTTOM_RIGHT -> {
                    orientation = GradientDrawable.Orientation.TL_BR
                }
                GradientDirection.TOP_RIGHT_TO_BOTTOM_LEFT -> {
                    orientation = GradientDrawable.Orientation.TR_BL
                }
            }
        }
        
        view.background = gradientDrawable
    }
    
    fun createGradientButton(
        context: Context,
        colors: IntArray,
        cornerRadius: Float = 8f
    ): GradientDrawable {
        return GradientDrawable().apply {
            this.colors = colors
            this.cornerRadius = cornerRadius
            orientation = GradientDrawable.Orientation.TL_BR
        }
    }
    
    fun getBackgroundGradient(): IntArray {
        return StormSkyColors.BACKGROUND_GRADIENT
    }
    
    fun getGoldGradient(): IntArray {
        return StormSkyColors.GOLD_GRADIENT
    }
}
```

---

## 🎨 **КОМПОНЕНТЫ С ЦВЕТОВОЙ СХЕМОЙ**

### 📋 **iOS - StatusCardView.swift (Обновленная версия):**
```swift
import UIKit

class StatusCardView: UIView {
    
    private lazy var titleLabel: UILabel = {
        let label = UILabel()
        label.text = "СТАТУС ЗАЩИТЫ"
        label.font = StormSkyTheme.Typography.body
        label.textColor = StormSkyColors.goldMain
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var statusLabel: UILabel = {
        let label = UILabel()
        label.text = "🟢 ВСЕ УСТРОЙСТВА ЗАЩИЩЕНЫ"
        label.font = StormSkyTheme.Typography.h3
        label.textColor = StormSkyColors.white
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var detailsLabel: UILabel = {
        let label = UILabel()
        label.text = "⚡ 0.2 мс время реакции • 🛡️ 26 модулей активны"
        label.font = StormSkyTheme.Typography.caption
        label.textColor = StormSkyColors.lightningBlue
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupUI()
    }
    
    private func setupUI() {
        // Apply card style
        StormSkyTheme.applyCardStyle(to: self)
        
        addSubview(titleLabel)
        addSubview(statusLabel)
        addSubview(detailsLabel)
        
        setupConstraints()
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: topAnchor, constant: StormSkyTheme.Spacing.md),
            titleLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: StormSkyTheme.Spacing.md),
            titleLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -StormSkyTheme.Spacing.md),
            
            statusLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: StormSkyTheme.Spacing.sm),
            statusLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: StormSkyTheme.Spacing.md),
            statusLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -StormSkyTheme.Spacing.md),
            
            detailsLabel.topAnchor.constraint(equalTo: statusLabel.bottomAnchor, constant: StormSkyTheme.Spacing.sm),
            detailsLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: StormSkyTheme.Spacing.md),
            detailsLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -StormSkyTheme.Spacing.md),
            detailsLabel.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -StormSkyTheme.Spacing.md)
        ])
    }
    
    func updateStatus(_ status: SecurityStatus) {
        statusLabel.text = status.isSecure ? "🟢 ВСЕ УСТРОЙСТВА ЗАЩИЩЕНЫ" : "🔴 ОБНАРУЖЕНЫ УГРОЗЫ"
        statusLabel.textColor = status.isSecure ? StormSkyColors.successGreen : StormSkyColors.errorRed
        
        detailsLabel.text = "⚡ \(status.responseTime) мс время реакции • 🛡️ \(status.activeModules) модулей активны"
    }
}
```

### 📋 **Android - StatusCardView.kt (Обновленная версия):**
```kotlin
package com.aladdin.components.cards

import android.content.Context
import android.util.AttributeSet
import android.view.LayoutInflater
import android.widget.LinearLayout
import com.aladdin.R
import com.aladdin.databinding.ViewStatusCardBinding
import com.aladdin.models.SecurityStatus
import com.aladdin.ui.theme.StormSkyTheme

class StatusCardView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {
    
    private val binding: ViewStatusCardBinding
    
    init {
        binding = ViewStatusCardBinding.inflate(LayoutInflater.from(context), this, true)
        setupUI()
    }
    
    private fun setupUI() {
        // Apply card style
        StormSkyTheme.applyCardStyle(this)
        
        // Set text colors
        binding.titleText.setTextColor(ContextCompat.getColor(context, R.color.gold_main))
        binding.statusText.setTextColor(ContextCompat.getColor(context, R.color.success_green))
        binding.detailsText.setTextColor(ContextCompat.getColor(context, R.color.lightning_blue))
    }
    
    fun updateStatus(status: SecurityStatus) {
        binding.titleText.text = "СТАТУС ЗАЩИТЫ"
        binding.statusText.text = if (status.isSecure) "🟢 ВСЕ УСТРОЙСТВА ЗАЩИЩЕНЫ" else "🔴 ОБНАРУЖЕНЫ УГРОЗЫ"
        binding.detailsText.text = "⚡ ${status.responseTime} мс время реакции • 🛡️ ${status.activeModules} модулей активны"
        
        // Update colors based on status
        val statusColor = if (status.isSecure) R.color.success_green else R.color.error_red
        binding.statusText.setTextColor(ContextCompat.getColor(context, statusColor))
    }
}
```

---

## 🚀 **СЛЕДУЮЩИЕ ШАГИ**

1. **Интегрировать цветовую схему** в оба проекта
2. **Создать компоненты** с единым стилем
3. **Применить градиенты** к фонам
4. **Настроить анимации** с цветовой схемой
5. **Протестировать** на разных устройствах
6. **Оптимизировать** производительность

**🎯 ЦВЕТОВАЯ СХЕМА ГОТОВА К ИНТЕГРАЦИИ!**

**📱 ПЕРЕХОДИМ К API ИНТЕГРАЦИИ!**

