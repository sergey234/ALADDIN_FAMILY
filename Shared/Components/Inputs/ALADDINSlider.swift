import SwiftUI

/// 🎚️ ALADDIN Slider
/// Кастомный ползунок с дизайном ALADDIN
/// Источник: HTML range inputs на 09_settings.html
struct ALADDINSlider: View {
    
    // MARK: - Properties
    
    let title: String
    let subtitle: String?
    let icon: String?
    @Binding var value: Double
    let range: ClosedRange<Double>
    let step: Double
    let unit: String
    let showValue: Bool
    
    // MARK: - Init
    
    init(
        _ title: String,
        subtitle: String? = nil,
        icon: String? = nil,
        value: Binding<Double>,
        range: ClosedRange<Double> = 0...100,
        step: Double = 1,
        unit: String = "",
        showValue: Bool = true
    ) {
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self._value = value
        self.range = range
        self.step = step
        self.unit = unit
        self.showValue = showValue
    }
    
    // MARK: - Body
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            HStack(spacing: Spacing.m) {
                // Иконка
                if let icon = icon {
                    Text(icon)
                        .font(.system(size: 28))
                }
                
                // Текст
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    HStack {
                        Text(title)
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        // Значение
                        if showValue {
                            Text("\(Int(value))\(unit)")
                                .font(.bodyBold)
                                .foregroundColor(.primaryBlue)
                        }
                    }
                    
                    if let subtitle = subtitle {
                        Text(subtitle)
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
            }
            
            // Ползунок
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    // Трек фона
                    RoundedRectangle(cornerRadius: CornerRadius.small)
                        .fill(Color.backgroundMedium)
                        .frame(height: Size.sliderTrackHeight)
                    
                    // Активная часть
                    RoundedRectangle(cornerRadius: CornerRadius.small)
                        .fill(
                            LinearGradient(
                                colors: [Color.primaryBlue, Color.secondaryBlue],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(
                            width: progressWidth(in: geometry.size.width),
                            height: Size.sliderTrackHeight
                        )
                    
                    // Ползунок
                    Circle()
                        .fill(Color.white)
                        .frame(width: Size.sliderKnob, height: Size.sliderKnob)
                        .shadow(color: Color.black.opacity(0.2), radius: 4, x: 0, y: 2)
                        .overlay(
                            Circle()
                                .stroke(Color.primaryBlue, lineWidth: 2)
                        )
                        .offset(x: progressWidth(in: geometry.size.width) - Size.sliderKnob / 2)
                        .gesture(
                            DragGesture(minimumDistance: 0)
                                .onChanged { gesture in
                                    updateValue(from: gesture.location.x, in: geometry.size.width)
                                }
                        )
                }
            }
            .frame(height: Size.sliderKnob)
            
            // Метки диапазона
            HStack {
                Text("\(Int(range.lowerBound))\(unit)")
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                
                Spacer()
                
                Text("\(Int(range.upperBound))\(unit)")
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Helpers
    
    private func progressWidth(in totalWidth: CGFloat) -> CGFloat {
        let normalized = (value - range.lowerBound) / (range.upperBound - range.lowerBound)
        return totalWidth * CGFloat(normalized)
    }
    
    private func updateValue(from location: CGFloat, in totalWidth: CGFloat) {
        let generator = UIImpactFeedbackGenerator(style: .light)
        
        let normalized = max(0, min(1, location / totalWidth))
        let newValue = range.lowerBound + normalized * (range.upperBound - range.lowerBound)
        
        // Округляем до шага
        let steppedValue = round(newValue / step) * step
        
        // Haptic только при изменении значения
        if abs(steppedValue - value) >= step {
            generator.impactOccurred()
        }
        
        value = max(range.lowerBound, min(range.upperBound, steppedValue))
    }
}

// MARK: - Preview

#if DEBUG
struct ALADDINSlider_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: Spacing.m) {
            // Уровень защиты
            ALADDINSlider(
                "Уровень защиты",
                subtitle: "От низкого до максимального",
                icon: "🛡️",
                value: .constant(75),
                range: 0...100,
                unit: "%"
            )

            // Возраст ребёнка
            ALADDINSlider(
                "Возраст ребёнка",
                icon: "👶",
                value: .constant(10),
                range: 3...18,
                unit: " лет"
            )

            // Время экрана
            ALADDINSlider(
                "Лимит времени экрана",
                subtitle: "Дневное ограничение",
                icon: "⏰",
                value: .constant(3),
                range: 1...12,
                unit: " ч"
            )
        }
        .padding()
        .background(LinearGradient.backgroundGradient)
    }
}
#endif



