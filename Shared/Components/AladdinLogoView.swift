import SwiftUI

/// 🎨 Стилизованный золотой логотип "Aladdin" в скриптном стиле
/// Создан по образцу изображения: золотой текст на фиолетовом фоне
struct AladdinLogoView: View {
    var size: CGFloat = 24
    var showSubtitle: Bool = true
    
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            // ✅ Стилизованный золотой текст "Aladdin"
            Text(NSLocalizedString("app.name", comment: "App name"))
                .font(.system(size: size, weight: .bold, design: .rounded))
                .foregroundStyle(
                    LinearGradient(
                        colors: [
                            Color(red: 1.0, green: 0.84, blue: 0.0),      // Яркий золотой
                            Color(red: 0.96, green: 0.77, blue: 0.19),     // Средний золотой
                            Color(red: 0.85, green: 0.65, blue: 0.13)        // Тёмный золотой
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .shadow(color: Color(red: 1.0, green: 0.84, blue: 0.0).opacity(0.8), radius: 8, x: 0, y: 2)
                .shadow(color: Color(red: 0.85, green: 0.65, blue: 0.13).opacity(0.6), radius: 4, x: 0, y: 1)
                .overlay(
                    // ✅ Блики для объёмного эффекта
                    Text(NSLocalizedString("app.name", comment: "App name"))
                        .font(.system(size: size, weight: .bold, design: .rounded))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [
                                    Color.white.opacity(0.4),
                                    Color.clear
                                ],
                                startPoint: .topLeading,
                                endPoint: .center
                            )
                        )
                        .blendMode(.overlay)
                )
                .accessibilityLabel("Название приложения Aladdin")
            
            if showSubtitle {
                Text(NSLocalizedString("app.tagline", comment: "App tagline"))
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.7))
                    .dynamicTypeSize(.small ... .medium)
                    .accessibilityLabel("Описание: AI Защита семьи")
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Aladdin - AI Защита семьи")
    }
}

// MARK: - Preview
struct AladdinLogoView_Previews: PreviewProvider {
    static var previews: some View {
        ZStack {
            // Фиолетовый фон как на изображении
            LinearGradient(
                colors: [Color(red: 0.3, green: 0.2, blue: 0.5), Color(red: 0.2, green: 0.1, blue: 0.4)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 40) {
                AladdinLogoView(size: 28, showSubtitle: true)
                
                AladdinLogoView(size: 20, showSubtitle: true)
                
                AladdinLogoView(size: 24, showSubtitle: false)
            }
            .padding()
        }
    }
}




