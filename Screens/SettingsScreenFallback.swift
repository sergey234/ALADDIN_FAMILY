import SwiftUI

/**
 * 🚨 FALLBACK SETTINGS SCREEN
 * Используется для тестирования когда основной SettingsScreen крашится
 * Не содержит сложной логики, computed properties или зависимостей
 */
struct SettingsScreenFallback: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("⚠️ SETTINGS SCREEN FALLBACK")
                .font(.title)
                .foregroundColor(.orange)

            Text("This screen loads when the main SettingsScreen crashes")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)

            VStack(alignment: .leading, spacing: 10) {
                Text("✅ No computed properties: SAFE")
                Text("✅ No complex dependencies: SAFE")
                Text("✅ Basic SwiftUI components only: SAFE")
                Text("❓ If you see this - main SettingsScreen has critical issues")
            }
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(8)

            VStack(spacing: 15) {
                Text("Diagnostic Info:")
                    .font(.headline)

                Text("Thread: \(Thread.isMainThread ? "Main" : "Background")")
                Text("iOS Version: \(UIDevice.current.systemVersion)")
                Text("Device: \(UIDevice.current.model)")
                Text("Time: \(Date())")
            }
            .padding()
            .background(Color.blue.opacity(0.1))
            .cornerRadius(8)

            Spacer()

            Button("Go Back to Onboarding") {
                // Simple navigation without complex logic
                NotificationCenter.default.post(name: NSNotification.Name("NavigateToOnboarding"), object: nil)
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
        }
        .padding()
        .navigationBarTitle("Settings (Fallback)", displayMode: .inline)
        .onAppear {
            print("🚨 [CRASH_DIAG] FALLBACK SettingsScreen appeared!")
            print("🚨 [CRASH_DIAG] This means main SettingsScreen crashed during View construction")
        }
    }
}