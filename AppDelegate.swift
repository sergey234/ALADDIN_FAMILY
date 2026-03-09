import UIKit

/**
 * 🧩 AppDelegate
 * Передает APNs токен в NotificationManager
 */

class AppDelegate: NSObject, UIApplicationDelegate {

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        print("🚀 ALADDIN AppDelegate: Starting performance optimizations...")

        // 🛑 ДОБАВИТЬ CRASH HANDLER ДЛЯ ЛОВЛИ КРАШЕЙ
        setupCrashHandler()

        // 🚫 ВРЕМЕННО ОТКЛЮЧЕНО: DNS prefetching вызывает краш
        // performDNSPrefetching()

        // 🚫 ВРЕМЕННО ОТКЛЮЧЕНО: Connection warming вызывает краш
        // performConnectionWarming()

        // 📊 Production monitoring инициализируется автоматически через shared

        print("✅ AppDelegate optimizations completed")
        return true
    }

    private func setupCrashHandler() {
        print("🛑 Setting up crash handler...")

        // Сохраняем логи при краше
        let exceptionHandler = NSGetUncaughtExceptionHandler()
        NSSetUncaughtExceptionHandler { exception in
            let crashLog = """
            🚨 CRASH DETECTED!
            Exception: \(exception.name.rawValue)
            Reason: \(exception.reason ?? "Unknown")
            Time: \(Date())
            Device: \(UIDevice.current.model)
            iOS: \(UIDevice.current.systemVersion)
            """

            // Сохраняем в UserDefaults
            UserDefaults.standard.set(crashLog, forKey: "last_crash_log")
            UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "crash_timestamp")
            UserDefaults.standard.synchronize()

            print("💥 CRASH LOG SAVED: \(crashLog)")

            // Вызываем оригинальный handler
            if let originalHandler = exceptionHandler {
                originalHandler(exception)
            }
        }

        print("✅ Crash handler installed")
    }

    /**
     * 🌐 DNS prefetching - предварительное разрешение DNS для быстрого первого запроса
     */
    private func performDNSPrefetching() {
        print("🌐 Performing DNS prefetching...")

        // Prefetch основного API домена
        let prefetchURL = URL(string: "https://aladdin-ai.ru/api/health")!
        let prefetchRequest = URLRequest(url: prefetchURL, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 1.0)

        // Выполняем prefetch в фоне
        URLSession.shared.dataTask(with: prefetchRequest) { data, response, error in
            if let error = error {
                print("⚠️ DNS prefetch failed: \(error.localizedDescription)")
            } else {
                print("✅ DNS prefetch successful")
            }
        }.resume()
    }

    /**
     * 🔄 Connection warming - предварительное открытие соединений для быстрого первого запроса
     */
    private func performConnectionWarming() {
        print("🔄 Performing connection warming...")

        let warmupURLs = [
            "https://aladdin-ai.ru/api/health",
            "https://aladdin-ai.ru/api/components/status/crash_detection_agent",
            "https://aladdin-ai.ru/api/components/status/phishing_protection_agent"
        ]

        for urlString in warmupURLs {
            guard let url = URL(string: urlString) else { continue }

            let request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 2.0)

            URLSession.shared.dataTask(with: request) { data, response, error in
                if let error = error {
                    print("⚠️ Connection warming failed for \(urlString): \(error.localizedDescription)")
                } else {
                    print("✅ Connection warmed for \(urlString)")
                }
            }.resume()
        }
    }

    func application(_ application: UIApplication,
                     didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        NotificationManager.shared.didRegisterForRemoteNotifications(deviceToken: deviceToken)
    }
    
    func application(_ application: UIApplication,
                     didFailToRegisterForRemoteNotificationsWithError error: Error) {
        NotificationManager.shared.didFailToRegisterForRemoteNotifications(error: error)
    }
}


