import SwiftUI
import Foundation

/// 🧪 MonitoredAppStorage (BUILD 95)
/// Обёртка над @AppStorage для измерения времени чтения/записи.
/// Использовать точечно на ключевых значениях, чтобы не засорять логи.
@propertyWrapper
struct MonitoredAppStorage<Value>: DynamicProperty {
    @AppStorage private var value: Value
    private let key: String
    /// Порог медленной операции в миллисекундах
    private var slowThresholdMs: Double = 50

    var wrappedValue: Value {
        get {
            RecursionMonitor.enter("MonitoredAppStorage.get \(key)")
            defer { RecursionMonitor.leave() }
            let start = CFAbsoluteTimeGetCurrent()
            let v = value
            let ms = (CFAbsoluteTimeGetCurrent() - start) * 1000.0
            if ms >= slowThresholdMs {
                print("⚠️ [@AppStorage READ] slow \(String(format: "%.1f", ms))ms key='\(key)'")
            }
            return v
        }
        nonmutating set {
            RecursionMonitor.enter("MonitoredAppStorage.set \(key)")
            defer { RecursionMonitor.leave() }
            let start = CFAbsoluteTimeGetCurrent()
            value = newValue
            let ms = (CFAbsoluteTimeGetCurrent() - start) * 1000.0
            if ms >= slowThresholdMs {
                print("⚠️ [@AppStorage WRITE] slow \(String(format: "%.1f", ms))ms key='\(key)'")
            }
        }
    }

    var projectedValue: Binding<Value> {
        Binding(
            get: { self.wrappedValue },
            set: { self.wrappedValue = $0 }
        )
    }
}

