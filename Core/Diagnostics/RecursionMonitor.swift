import Foundation

/// 🔁 Recursion Monitor (BUILD 95)
/// Лёгкий монитор глубины рекурсии на текущем потоке.
/// Важно: не использует UserDefaults внутри, чтобы не провоцировать рекурсию.
enum RecursionMonitor {
    private static let depthKey = "aladdin.recursion.depth"
    private static let maxDepthKey = "aladdin.recursion.maxDepth"

    static func enter(_ function: String = #function, file: String = #fileID, line: Int = #line, threshold: Int = 80) {
        let dict = Thread.current.threadDictionary
        let current = (dict[depthKey] as? Int) ?? 0
        let next = current + 1
        dict[depthKey] = next

        let maxSeen = (dict[maxDepthKey] as? Int) ?? 0
        if next > maxSeen { dict[maxDepthKey] = next }

        if next == threshold {
            print("🔴 [RecursionMonitor] threshold reached depth=\(next) at \(function) (\(file):\(line))")
        } else if next > threshold, next % 25 == 0 {
            print("🔴 [RecursionMonitor] deep recursion depth=\(next) at \(function) (\(file):\(line))")
        }
    }

    static func leave() {
        let dict = Thread.current.threadDictionary
        let current = (dict[depthKey] as? Int) ?? 0
        dict[depthKey] = max(0, current - 1)
    }

    /// Выполнить блок с автоматическим enter/leave
    static func scoped<T>(_ function: String = #function, file: String = #fileID, line: Int = #line, threshold: Int = 80, _ body: () throws -> T) rethrows -> T {
        enter(function, file: file, line: line, threshold: threshold)
        defer { leave() }
        return try body()
    }

    static func currentDepth() -> Int {
        (Thread.current.threadDictionary[depthKey] as? Int) ?? 0
    }

    static func maxDepthSeen() -> Int {
        (Thread.current.threadDictionary[maxDepthKey] as? Int) ?? 0
    }
}

