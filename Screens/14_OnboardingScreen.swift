import SwiftUI

/// 🚨 BUILD 65 - КРАЙНЯЯ ДИАГНОСТИКА СИНЕГО ЭКРАНА
/// Полная диагностика проблемы с зависанием OnboardingScreen
struct OnboardingScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager

    var body: some View {
        ZStack {
            Color.blue.opacity(0.1)
                .ignoresSafeArea()

            VStack(spacing: 20) {
                Text("🚨 BUILD 65 - ДИАГНОСТИКА")
                    .font(.title)
                    .foregroundColor(.red)

                Text("Если вы видите этот текст - OnboardingScreen инициализировался!")
                    .font(.headline)
                    .foregroundColor(.green)

                VStack(alignment: .leading, spacing: 10) {
                    Text("🔍 Диагностика компонентов:")

                    Text("✅ NavigationManager: \(navigationManager.currentScreen.rawValue)")
                        .foregroundColor(.blue)

                    Text("✅ Thread.isMainThread: \(String(Thread.isMainThread))")
                        .foregroundColor(.blue)

                    Text("✅ Time: \(Date())")
                        .foregroundColor(.blue)
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)

                Button("Завершить онбординг") {
                    print("🚨 BUILD 65: Кнопка нажата - завершаем онбординг")
                    UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
                    navigationManager.navigateTo(.main)
                    print("🚨 BUILD 65: NavigationManager.navigateTo(.main) вызван")
                }
                .padding()
                .background(Color.green)
                .foregroundColor(.white)
                .cornerRadius(8)

                Button("Тестовый лог") {
                    print("🚨 BUILD 65: Тестовый лог работает!")
                }
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .padding()
        }
        .task {
            print("🚨 BUILD 65: OnboardingScreen.task выполнен!")
        }
        .onAppear {
            print("🚨 BUILD 65: OnboardingScreen.onAppear выполнен!")
        }
    }
}

// MARK: - Preview

struct OnboardingScreen_Previews: PreviewProvider {
    static var previews: some View {
        OnboardingScreen()
    }
}
