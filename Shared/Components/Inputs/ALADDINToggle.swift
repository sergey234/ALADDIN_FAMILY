import SwiftUI

/**
 * 🔄 ALADDIN Toggle - УЛУЧШЕННАЯ ВЕРСИЯ
 * Красивый переключатель без белых ободков
 * Градиентный дизайн в стиле ALADDIN
 */

struct ALADDINToggle: View {
    
    // MARK: - Properties
    
    @Binding var isOn: Bool
    let size: CGFloat
    let animationDuration: Double
    
    // MARK: - Init
    
    init(isOn: Binding<Bool>, size: CGFloat = 40, animationDuration: Double = 0.3) {
        self._isOn = isOn
        self.size = size
        self.animationDuration = animationDuration
    }
    
    // MARK: - Body
    
    var body: some View {
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
}

// MARK: - Preview

struct ALADDINToggle_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 20) {
            HStack {
                Text("Защита сети")
                Spacer()
                ALADDINToggle(isOn: .constant(true))
            }
            
            HStack {
                Text("Push уведомления")
                Spacer()
                ALADDINToggle(isOn: .constant(false))
            }
            
            HStack {
                Text("Face ID")
                Spacer()
                ALADDINToggle(isOn: .constant(true))
            }
        }
        .padding()
        .background(Color.black)
        .previewDisplayName("ALADDIN Toggle")
    }
}