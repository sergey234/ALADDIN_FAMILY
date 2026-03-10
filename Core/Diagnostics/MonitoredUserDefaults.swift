import Foundation

/// 🧪 MonitoredUserDefaults (BUILD 95)
/// Точечный мониторинг медленных операций UserDefaults на реальном устройстве.
/// Важно: не пишет результаты обратно в UserDefaults (чтобы не провоцировать рекурсию).
enum MonitoredUserDefaults {
    static var slowThresholdMs: Double = 50

    static func object(forKey key: String, file: String = #fileID, line: Int = #line) -> Any? {
        return measure("READ", key: key, file: file, line: line) {
            UserDefaults.standard.object(forKey: key)
        }
    }

    static func string(forKey key: String, file: String = #fileID, line: Int = #line) -> String? {
        return measure("READ", key: key, file: file, line: line) {
            UserDefaults.standard.string(forKey: key)
        }
    }

    static func bool(forKey key: String, file: String = #fileID, line: Int = #line) -> Bool {
        return measure("READ", key: key, file: file, line: line) {
            UserDefaults.standard.bool(forKey: key)
        }
    }

    static func data(forKey key: String, file: String = #fileID, line: Int = #line) -> Data? {
        return measure("READ", key: key, file: file, line: line) {
            UserDefaults.standard.data(forKey: key)
        }
    }

    static func set(_ value: Any?, forKey key: String, file: String = #fileID, line: Int = #line) {
        _ = measure("WRITE", key: key, file: file, line: line) { () -> Bool in
            UserDefaults.standard.set(value, forKey: key)
            return true
        }
    }

    static func removeObject(forKey key: String, file: String = #fileID, line: Int = #line) {
        _ = measure("WRITE", key: key, file: file, line: line) { () -> Bool in
            UserDefaults.standard.removeObject(forKey: key)
            return true
        }
    }

    @discardableResult
    private static func measure<T>(_ op: String, key: String, file: String, line: Int, _ block: () -> T) -> T {
        RecursionMonitor.enter("MonitoredUserDefaults.\(op)")
        defer { RecursionMonitor.leave() }

        let start = CFAbsoluteTimeGetCurrent()
        let result = block()
        let ms = (CFAbsoluteTimeGetCurrent() - start) * 1000.0

        if ms >= slowThresholdMs {
            print("⚠️ [UserDefaults \(op)] slow \(String(format: "%.1f", ms))ms key='\(key)' at \(file):\(line)")
        }
        return result
    }
}

