import SwiftUI

/**
 * 🔄 ALADDIN Toggle - УНИВЕРСАЛЬНАЯ ВЕРСИЯ
 * Объединяет старую и новую версии для полной совместимости
 * 
 * ✅ Поддерживает:
 * - Старый API: ALADDINToggle("Заголовок", subtitle: "Подзаголовок", isOn: $binding)
 * - Новый API: ALADDINToggle(isOn: $binding, size: 40)
 * - Фиолетовый градиентный дизайн ALADDIN
 * - Настраиваемый размер
 * - Тактильный отклик
 * 
 * Импорты: Spacing, Colors определены в Shared/Styles/
 */

struct ALADDINToggle: View {
    
    // MARK: - Properties
    
    @Binding var isOn: Bool
    let title: String?
    let subtitle: String?
    let size: CGFloat
    let animationDuration: Double
    
    // MARK: - Init
    
    // ✅ Новый API: простой инициализатор (как в новой версии)
    init(isOn: Binding<Bool>, size: CGFloat = 40, animationDuration: Double = 0.3) {
        self._isOn = isOn
        self.title = nil
        self.subtitle = nil
        self.size = size
        self.animationDuration = animationDuration
    }
    
    // ✅ Старый API: полный инициализатор для совместимости (как в старой версии)
    init(_ title: String, subtitle: String? = nil, isOn: Binding<Bool>) {
        self._isOn = isOn
        self.title = title
        self.subtitle = subtitle
        self.size = 40 // Дефолтный размер для старого API
        self.animationDuration = 0.3
    }
    
    // MARK: - Body
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // ✅ Поддержка title/subtitle (старый API)
            if let title = title {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                    
                    if let subtitle = subtitle {
                        Text(subtitle)
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                Spacer()
            }
            
            // ✅ Новый дизайн: фиолетовый градиентный переключатель
            Button(action: {
                withAnimation(.easeInOut(duration: animationDuration)) {
                    isOn.toggle()
                }
                
                // Тактильный отклик
                let generator = UIImpactFeedbackGenerator(style: .medium)
                generator.impactOccurred()
            }) {
                ZStack {
                    // Фон переключателя
                    RoundedRectangle(cornerRadius: size / 2)
                        .fill(
                            LinearGradient(
                                colors: isOn ? 
                                    [Color(hex: "#8B5CF6"), Color(hex: "#A78BFA")] :
                                    [Color.backgroundMedium, Color.backgroundMedium.opacity(0.5)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: size, height: size / 2)
                    
                    // Кнопка переключателя
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color.white, Color.white.opacity(0.9)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: (size / 2) - 4, height: (size / 2) - 4)
                        .shadow(
                            color: Color.black.opacity(0.2),
                            radius: 4,
                            x: 0,
                            y: 2
                        )
                        .offset(x: isOn ? size / 4 - 2 : -size / 4 + 2)
                        .animation(.easeInOut(duration: animationDuration), value: isOn)
                    
                    // Иконка состояния
                    Image(systemName: isOn ? "checkmark" : "xmark")
                        .font(.system(size: size / 6, weight: .bold))
                        .foregroundColor(isOn ? .primaryBlue : .gray)
                        .offset(x: isOn ? size / 4 - 2 : -size / 4 + 2)
                        .animation(.easeInOut(duration: animationDuration), value: isOn)
                }
            }
            .buttonStyle(PlainButtonStyle())
            .accessibilityLabel(isOn ? "Включено" : "Выключено")
            .accessibilityAddTraits(isOn ? .isSelected : [])
        }
        // ✅ Старый стиль: padding и background только если есть title
        .if(title != nil) { view in
            view
                .padding()
                .background(Color(.systemBackground))
                .cornerRadius(12)
        }
    }
}

// MARK: - View Extension для условного модификатора

extension View {
    @ViewBuilder
    func `if`<Transform: View>(_ condition: Bool, transform: (Self) -> Transform) -> some View {
        if condition {
            transform(self)
        } else {
            self
        }
    }
}

// MARK: - Preview

struct ALADDINToggle_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 20) {
            // Новый API (без title)
            HStack {
                Text("Защита сети")
                Spacer()
                ALADDINToggle(isOn: .constant(true))
            }
            
            HStack {
                Text("Push уведомления")
                Spacer()
                ALADDINToggle(isOn: .constant(false), size: 40)
            }
            
            // Старый API (с title)
            ALADDINToggle("Face ID", subtitle: "Быстрый вход", isOn: .constant(true))
            
            ALADDINToggle("Защита устройства", isOn: .constant(false))
        }
        .padding()
        .background(Color.black)
        .previewDisplayName("ALADDIN Toggle - Универсальная версия")
    }
}
