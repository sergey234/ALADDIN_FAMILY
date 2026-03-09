import SwiftUI
import Foundation

// MARK: - Minimal ALADDIN App for Crash Diagnostics

@main
struct ALADDINApp: App {

    // 🔍 ТЕСТОВОЕ ЛОГИРОВАНИЕ - проверяем работу при старте приложения
    private let appStartLogger: Void = {
        print("🚀 ALADDIN_APP: Application starting...")
        print("🚀 ALADDIN_APP: Testing logger initialization...")
        return ()
    }()

    var body: some Scene {
        WindowGroup {
            // 🚫 АБСОЛЮТНЫЙ МИНИМУМ: Только базовый SwiftUI для диагностики
            VStack {
                Text("ALADDIN")
                    .font(.largeTitle)
                    .foregroundColor(.blue)
                Text("BUILD 85 - Crash Diagnostics")
                    .font(.headline)
                    .foregroundColor(.green)
                Text("If you see this - no crash!")
                    .font(.body)
                    .foregroundColor(.gray)
            }
            .onAppear {
                print("🎯 ALADDIN_APP: onAppear - ABSOLUTE MINIMUM TEST")
                print("✅ SwiftUI rendered successfully - no crashes!")

                // 🔍 ДИАГНОСТИКА
                print("📱 Device: \(UIDevice.current.model)")
                print("🍎 iOS: \(UIDevice.current.systemVersion)")
                print("🕒 Time: \(Date())")

                // 🧪 ТЕСТИРУЕМ VisualLogger
                VisualLogger.shared.log("🧪 VisualLogger test from onAppear", level: .info)
                print("✅ VisualLogger.log() succeeded")

                // 🧪 ТЕСТИРУЕМ UserDefaults
                UserDefaults.standard.set("TEST_LOG_85", forKey: "crash_test")
                UserDefaults.standard.synchronize()
                print("✅ UserDefaults test passed")

                print("🎉 ALL DIAGNOSTIC TESTS COMPLETED - NO CRASHES!")
            }
        }
    }
}