import UIKit
import Darwin.Mach

/**
 * 🧩 AppDelegate
 * Передает APNs токен в NotificationManager
 * ✅ BUILD 94: Добавлена диагностика крашей на реальном устройстве
 */

// ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
private let crashLogFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale вместо Locale.current
    return formatter
}()

// Глобальная функция для обработки крашей
func crashExceptionHandler(exception: NSException) {
    let timestamp = Date()
    let formattedTime = crashLogFormatter.string(from: timestamp)
    
    // Собираем полный stack trace
    var stackTrace = ""
    for (index, symbol) in exception.callStackSymbols.enumerated() {
        stackTrace += "[\(index)] \(symbol)\n"
    }
    
    let crashLog = """
    🚨 CRASH DETECTED!
    Exception: \(exception.name.rawValue)
    Reason: \(exception.reason ?? "Unknown")
    Time: \(formattedTime)
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

        // ✅ BUILD 109: Безопасная инициализация настроек логгера
        // Читаем UserDefaults ОДИН РАЗ при старте и кешируем в логгере.
        // Это исключает обращения к UserDefaults внутри метода log().
        let enableVisual = UserDefaults.standard.bool(forKey: "enable_visual_logging")
        MasterLogger.shared.updateSettings(enableVisual: enableVisual)

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
    
    // ✅ BUILD 94: Memory Warning Handler для диагностики крашей на реальном устройстве
    func applicationDidReceiveMemoryWarning(_ application: UIApplication) {
        let memoryUsage = getMemoryUsageMB()
        let timestamp = Date()
        // ✅ BUILD 98: Используем статический DateFormatter для предотвращения рекурсии
        let formattedTime = crashLogFormatter.string(from: timestamp)
        
        let memoryWarningLog = """
        🚨 MEMORY WARNING DETECTED!
        Memory Usage: \(String(format: "%.1f", memoryUsage)) MB
        Time: \(formattedTime)
        Device: \(UIDevice.current.model)
        iOS: \(UIDevice.current.systemVersion)
        App Version: \(Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "Unknown")
        Build: \(Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "Unknown")
        """
        
        // Сохраняем в UserDefaults
        UserDefaults.standard.set(memoryWarningLog, forKey: "memory_warning_log")
        UserDefaults.standard.set(timestamp.timeIntervalSince1970, forKey: "memory_warning_timestamp")
        UserDefaults.standard.set(memoryUsage, forKey: "memory_warning_usage_mb")
        UserDefaults.standard.synchronize()
        
        // Сохраняем в файл
        saveMemoryWarningToFile(log: memoryWarningLog, memoryUsage: memoryUsage)
        
        // Отправляем на сервер асинхронно
        sendMemoryWarningToServer(memoryUsage: memoryUsage)
        
        print("🚨 MEMORY WARNING: \(String(format: "%.1f", memoryUsage)) MB")
        
        // ✅ BUILD 94: Сохраняем состояние перед возможным крашем
        savePreCrashState()
    }
    
    // ✅ BUILD 94: Сохранение Memory Warning в файл
    private func saveMemoryWarningToFile(log: String, memoryUsage: Double) {
        guard let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
            return
        }
        
        let memoryWarningFile = documentsPath.appendingPathComponent("memory_warning_log.txt")
        
        do {
            try log.write(to: memoryWarningFile, atomically: true, encoding: .utf8)
            UserDefaults.standard.set(memoryWarningFile.path, forKey: "memory_warning_file_path")
            UserDefaults.standard.synchronize()
        } catch {
            UserDefaults.standard.set("Failed to save memory warning file: \(error.localizedDescription)", forKey: "memory_warning_file_error")
        }
    }
    
    // ✅ BUILD 94: Отправка Memory Warning на сервер
    private func sendMemoryWarningToServer(memoryUsage: Double) {
        DispatchQueue.global(qos: .utility).async {
            guard let url = URL(string: "https://aladdin-ai.ru/api/crash-detection/memory-warning") else {
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            let report: [String: Any] = [
                "memory_usage_mb": memoryUsage,
                "device": UIDevice.current.model,
                "ios_version": UIDevice.current.systemVersion,
                "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "Unknown",
                "build": Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "Unknown",
                "timestamp": Date().timeIntervalSince1970
            ]
            
            if let jsonData = try? JSONSerialization.data(withJSONObject: report) {
                request.httpBody = jsonData
                
                URLSession.shared.dataTask(with: request) { data, response, error in
                    if let error = error {
                        UserDefaults.standard.set("Failed to send memory warning: \(error.localizedDescription)", forKey: "memory_warning_send_error")
                    } else {
                        UserDefaults.standard.set("Memory warning sent successfully", forKey: "memory_warning_send_status")
                    }
                    UserDefaults.standard.synchronize()
                }.resume()
            }
        }
    }
    
    // ✅ BUILD 94: Получение использования памяти в MB
    private func getMemoryUsageMB() -> Double {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4
        
        let kerr: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_,
                         task_flavor_t(MACH_TASK_BASIC_INFO),
                         $0,
                         &count)
            }
        }
        
        if kerr == KERN_SUCCESS {
            return Double(info.resident_size) / 1024.0 / 1024.0
        } else {
            return 0.0
        }
    }
    
    // ✅ BUILD 94: Сохранение состояния перед возможным крашем
    func savePreCrashState() {
        let memoryUsage = getMemoryUsageMB()
        let timestamp = Date().timeIntervalSince1970
        
        let state: [String: Any] = [
            "memory_usage_mb": memoryUsage,
            // Thread.activeThreadCount недоступен на этой платформе, используем длину стека вызовов как приближение
            "active_threads": Thread.callStackSymbols.count,
            "timestamp": timestamp,
            "app_state": UIApplication.shared.applicationState.rawValue,
            "device": UIDevice.current.model,
            "ios_version": UIDevice.current.systemVersion,
            "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "Unknown",
            "build": Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "Unknown"
        ]
        
        if let data = try? JSONSerialization.data(withJSONObject: state) {
            UserDefaults.standard.set(data, forKey: "pre_crash_state")
            UserDefaults.standard.set(timestamp, forKey: "pre_crash_state_timestamp")
            UserDefaults.standard.synchronize()
        }
        
        // Также сохраняем в файл
        savePreCrashStateToFile(state: state)
    }
    
    // ✅ BUILD 94: Сохранение Pre-Crash State в файл
    private func savePreCrashStateToFile(state: [String: Any]) {
        guard let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
            return
        }
        
        let stateFile = documentsPath.appendingPathComponent("pre_crash_state.json")
        
        if let jsonData = try? JSONSerialization.data(withJSONObject: state, options: .prettyPrinted),
           let jsonString = String(data: jsonData, encoding: .utf8) {
            do {
                try jsonString.write(to: stateFile, atomically: true, encoding: .utf8)
                UserDefaults.standard.set(stateFile.path, forKey: "pre_crash_state_file_path")
                UserDefaults.standard.synchronize()
            } catch {
                UserDefaults.standard.set("Failed to save pre-crash state: \(error.localizedDescription)", forKey: "pre_crash_state_file_error")
            }
        }
    }
}


