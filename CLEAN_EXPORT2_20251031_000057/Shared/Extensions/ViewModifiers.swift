import SwiftUI

// MARK: - View Modifiers
/// 🎨 Custom View Modifiers for ALADDIN App
/// Содержит все кастомные модификаторы для UI компонентов

// MARK: - Card Shadow Modifier
struct CardShadowModifier: ViewModifier {
    let radius: CGFloat
    let opacity: Double
    let x: CGFloat
    let y: CGFloat
    
    init(radius: CGFloat = 8, opacity: Double = 0.15, x: CGFloat = 0, y: CGFloat = 4) {
        self.radius = radius
        self.opacity = opacity
        self.x = x
        self.y = y
    }
    
    func body(content: Content) -> some View {
        content
            .shadow(
                color: Color.black.opacity(opacity),
                radius: radius,
                x: x,
                y: y
            )
    }
}

// MARK: - Glassmorphism Modifier
struct GlassmorphismModifier: ViewModifier {
    let opacity: Double
    let blur: CGFloat
    let cornerRadius: CGFloat
    
    init(opacity: Double = 0.1, blur: CGFloat = 10, cornerRadius: CGFloat = 16) {
        self.opacity = opacity
        self.blur = blur
        self.cornerRadius = cornerRadius
    }
    
    func body(content: Content) -> some View {
        content
            .background(
                RoundedRectangle(cornerRadius: cornerRadius)
                    .fill(
                        LinearGradient(
                            colors: [
                                Color.white.opacity(opacity),
                                Color.white.opacity(opacity * 0.5)
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .blur(radius: blur)
            )
    }
}

// MARK: - Primary Button Modifier
struct PrimaryButtonModifier: ViewModifier {
    let isEnabled: Bool
    let isLoading: Bool
    
    init(isEnabled: Bool = true, isLoading: Bool = false) {
        self.isEnabled = isEnabled
        self.isLoading = isLoading
    }
    
    func body(content: Content) -> some View {
        content
            .font(.system(size: 16, weight: .semibold))
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(
                        isEnabled ? 
                        LinearGradient(
                            colors: [Color.blue, Color.blue.opacity(0.8)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ) :
                        LinearGradient(
                            colors: [Color.gray, Color.gray.opacity(0.6)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(
                        isEnabled ? Color.blue.opacity(0.3) : Color.gray.opacity(0.3),
                        lineWidth: 1
                    )
            )
            .scaleEffect(isEnabled ? 1.0 : 0.95)
            .opacity(isEnabled ? 1.0 : 0.6)
            .disabled(!isEnabled || isLoading)
            .overlay(
                Group {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .scaleEffect(0.8)
                    }
                }
            )
    }
}

// MARK: - Secondary Button Modifier
struct SecondaryButtonModifier: ViewModifier {
    let isEnabled: Bool
    let isLoading: Bool
    
    init(isEnabled: Bool = true, isLoading: Bool = false) {
        self.isEnabled = isEnabled
        self.isLoading = isLoading
    }
    
    func body(content: Content) -> some View {
        content
            .font(.system(size: 16, weight: .medium))
            .foregroundColor(isEnabled ? .blue : .gray)
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.clear)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(
                        isEnabled ? Color.blue : Color.gray,
                        lineWidth: 2
                    )
            )
            .scaleEffect(isEnabled ? 1.0 : 0.95)
            .opacity(isEnabled ? 1.0 : 0.6)
            .disabled(!isEnabled || isLoading)
            .overlay(
                Group {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .blue))
                            .scaleEffect(0.8)
                    }
                }
            )
    }
}

// MARK: - View Extensions
extension View {
    /// 🎨 Добавляет тень для карточек
    /// - Parameters:
    ///   - radius: Радиус тени (по умолчанию 8)
    ///   - opacity: Прозрачность тени (по умолчанию 0.15)
    ///   - x: Смещение по X (по умолчанию 0)
    ///   - y: Смещение по Y (по умолчанию 4)
    func cardShadow(
        radius: CGFloat = 8,
        opacity: Double = 0.15,
        x: CGFloat = 0,
        y: CGFloat = 4
    ) -> some View {
        modifier(CardShadowModifier(radius: radius, opacity: opacity, x: x, y: y))
    }
    
    /// 🔮 Добавляет эффект стекла (glassmorphism)
    /// - Parameters:
    ///   - opacity: Прозрачность (по умолчанию 0.1)
    ///   - blur: Размытие (по умолчанию 10)
    ///   - cornerRadius: Радиус углов (по умолчанию 16)
    func glassmorphism(
        opacity: Double = 0.1,
        blur: CGFloat = 10,
        cornerRadius: CGFloat = 16
    ) -> some View {
        modifier(GlassmorphismModifier(opacity: opacity, blur: blur, cornerRadius: cornerRadius))
    }
    
    /// 🔵 Применяет стиль основной кнопки
    /// - Parameters:
    ///   - isEnabled: Включена ли кнопка (по умолчанию true)
    ///   - isLoading: Загружается ли (по умолчанию false)
    func primaryButton(
        isEnabled: Bool = true,
        isLoading: Bool = false
    ) -> some View {
        modifier(PrimaryButtonModifier(isEnabled: isEnabled, isLoading: isLoading))
    }
    
    /// ⚪ Применяет стиль вторичной кнопки
    /// - Parameters:
    ///   - isEnabled: Включена ли кнопка (по умолчанию true)
    ///   - isLoading: Загружается ли (по умолчанию false)
    func secondaryButton(
        isEnabled: Bool = true,
        isLoading: Bool = false
    ) -> some View {
        modifier(SecondaryButtonModifier(isEnabled: isEnabled, isLoading: isLoading))
    }
}

// MARK: - Preview
#if DEBUG
struct ViewModifiers_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 20) {
            // Card Shadow Example
            Text("Card with Shadow")
                .padding()
                .background(Color.blue.opacity(0.1))
                .cornerRadius(12)
                .cardShadow()
            
            // Glassmorphism Example
            Text("Glassmorphism Effect")
                .padding()
                .appGlassmorphism()
            
            // Primary Button Example
            Button("Primary Button") { }
                .primaryButton()
            
            // Secondary Button Example
            Button("Secondary Button") { }
                .secondaryButton()
        }
        .padding()
        .background(Color.gray.opacity(0.1))
    }
}
#endif
