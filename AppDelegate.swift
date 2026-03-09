import UIKit

/**
 * 🧩 AppDelegate
 * Передает APNs токен в NotificationManager
 */

// Глобальная функция для обработки крашей
func crashExceptionHandler(exception: NSException) {
    let timestamp = Date()
    let formatter = DateFormatter()
    formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
    
    // Собираем полный stack trace
    var stackTrace = ""
    for (index, symbol) in exception.callStackSymbols.enumerated() {
        stackTrace += "[\(index)] \(symbol)\n"
    }
    
    let crashLog = """
    🚨 CRASH DETECTED!
    Exception: \(exception.name.rawValue)
    Reason: \(exception.reason ?? "Unknown")
    Time: \(formatter.string(from: timestamp))
    Device: \(UIDevice.current.model)
    iOS: \(UIDevice.current.systemVersion)
    App Version: \(Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "Unknown")
    Build: \(Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "Unknown")
    
    STACK TRACE:
    \(stackTrace)
    """

    // Сохраняем в UserDefaults (для получения через getCrashLogs())
    UserDefaults.standard.set(crashLog, forKey: "last_crash_log")
    UserDefaults.standard.set(timestamp.timeIntervalSince1970, forKey: "crash_timestamp")
    
    // ✅ ДОПОЛНИТЕЛЬНО: Сохраняем stack trace отдельно для анализа
    UserDefaults.standard.set(stackTrace, forKey: "last_crash_stack_trace")
    UserDefaults.standard.synchronize()

    // ✅ КРИТИЧНО: Сохраняем в файл для TestFlight (работает в RELEASE)
    saveCrashLogToFile(crashLog: crashLog, stackTrace: stackTrace)
    
    // ✅ КРИТИЧНО: Отправляем на сервер асинхронно (не блокируем краш)
    sendCrashLogToServer(crashLog: crashLog, stackTrace: stackTrace, exceptionName: exception.name.rawValue, reason: exception.reason ?? "Unknown")
    
    print("💥 CRASH LOG SAVED: \(crashLog)")
}

// ✅ СОХРАНЕНИЕ ЛОГА В ФАЙЛ (работает в RELEASE/TestFlight)
private func saveCrashLogToFile(crashLog: String, stackTrace: String) {
    guard let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
        return
    }
    
    let crashLogFile = documentsPath.appendingPathComponent("crash_log.txt")
    let stackTraceFile = documentsPath.appendingPathComponent("crash_stack_trace.txt")
    
    do {
        try crashLog.write(to: crashLogFile, atomically: true, encoding: .utf8)
        try stackTrace.write(to: stackTraceFile, atomically: true, encoding: .utf8)
        
        // Сохраняем путь к файлу в UserDefaults для доступа
        UserDefaults.standard.set(crashLogFile.path, forKey: "crash_log_file_path")
        UserDefaults.standard.set(stackTraceFile.path, forKey: "crash_stack_trace_file_path")
        UserDefaults.standard.synchronize()
    } catch {
        // В случае ошибки сохраняем хотя бы в UserDefaults
        UserDefaults.standard.set("Failed to save file: \(error.localizedDescription)", forKey: "crash_log_file_error")
    }
}

// ✅ ОТПРАВКА ЛОГА НА СЕРВЕР (асинхронно, не блокирует краш)
private func sendCrashLogToServer(crashLog: String, stackTrace: String, exceptionName: String, reason: String) {
    // Отправляем в фоне, не блокируя краш
    DispatchQueue.global(qos: .utility).async {
        guard let url = URL(string: "https://aladdin-ai.ru/api/crash-detection/report") else {
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let crashReport: [String: Any] = [
            "exception_name": exceptionName,
            "reason": reason,
            "device": UIDevice.current.model,
            "ios_version": UIDevice.current.systemVersion,
            "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "Unknown",
            "build": Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "Unknown",
            "timestamp": Date().timeIntervalSince1970,
            "stack_trace": stackTrace,
            "full_log": crashLog
        ]
        
        if let jsonData = try? JSONSerialization.data(withJSONObject: crashReport) {
            request.httpBody = jsonData
            
            URLSession.shared.dataTask(with: request) { data, response, error in
                if let error = error {
                    // Сохраняем ошибку отправки
                    UserDefaults.standard.set("Failed to send: \(error.localizedDescription)", forKey: "crash_log_send_error")
                } else {
                    UserDefaults.standard.set("Sent successfully", forKey: "crash_log_send_status")
                }
                UserDefaults.standard.synchronize()
            }.resume()
        }
    }
}

class AppDelegate: NSObject, UIApplicationDelegate {

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        print("🚀 ALADDIN AppDelegate: Starting performance optimizations...")

        // 🛑 CRASH HANDLER - для диагностики крашей при запуске
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

        // Устанавливаем глобальный обработчик крашей
        NSSetUncaughtExceptionHandler(crashExceptionHandler)

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


