import SwiftUI
import os.log

/// 🔍 SettingsScreenMinimal - ДИАГНОСТИЧЕСКАЯ ВЕРСИЯ
/// Минимальная версия SettingsScreen для точного определения источника краша SwiftUI Type Resolution
/// Используется только для диагностики проблемы
struct SettingsScreenMinimal: View {

    // MARK: - State (МИНИМАЛЬНЫЙ НАБОР)

    @Environment(\.dismiss) private var dismiss

    // MARK: - Body (МИНИМАЛЬНАЯ СТРУКТУРА)

    var body: some View {
        // ✅ ДИАГНОСТИКА: Простой Text для проверки базовой работоспособности
        Text("Settings Minimal Test")
            .font(.largeTitle)
            .foregroundColor(.white)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
            )
            .onAppear {
                print("✅ SettingsScreenMinimal: onAppear - экран загружен успешно")
                print("✅ SettingsScreenMinimal: Thread.isMainThread = \(Thread.isMainThread)")
            }
    }
}

#if DEBUG
struct SettingsScreenMinimal_Previews: PreviewProvider {
    static var previews: some View {
        SettingsScreenMinimal()
            .environmentObject(NavigationManager.shared)
            .environmentObject(LocalizationManager.shared)
    }
}
#endif