import SwiftUI

/// ✅ НОВОЕ: View для отображения загрузки приложения
struct AppLoadingView: View {
    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 20) {
                Spacer()

                // Логотип или иконка приложения
                ZStack {
                    Circle()
                        .fill(Color.yellow.opacity(0.2))
                        .frame(width: 120, height: 120)

                    Text("🦄")
                        .font(.system(size: 60))
                }

                // Текст загрузки
                Text("ALADDIN")
                    .font(.system(size: 32, weight: .bold))
                    .foregroundColor(.yellow)
                    .shadow(color: Color.yellow.opacity(0.5), radius: 10)

                Text("Подготовка приложения...")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.8))

                // Анимация загрузки
                ProgressView()
                    .scaleEffect(1.2)
                    .tint(.yellow)
                    .padding(.top, 16)

                Spacer()
            }
            .padding(.horizontal, 20)
        }
    }
}