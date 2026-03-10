import Foundation

/// 📚 Stack Size Monitor (BUILD 95)
/// Фиксирует stack size текущего потока (главный поток тоже), чтобы сравнивать device vs simulator.
enum StackSizeMonitor {
    static func currentThreadStackSizeBytes() -> UInt64 {
        // pthread_get_stacksize_np доступен на Apple платформах
        let size = pthread_get_stacksize_np(pthread_self())
        return UInt64(size)
    }

    static func logCurrentThreadStackSize(context: String) {
        let bytes = currentThreadStackSizeBytes()
        let kb = Double(bytes) / 1024.0
        print("📚 [StackSizeMonitor] \(context): stackSize=\(String(format: "%.0f", kb)) KB")
    }

    static func logMainThreadStackSize(context: String) {
        if Thread.isMainThread {
            logCurrentThreadStackSize(context: context)
            return
        }
        DispatchQueue.main.async {
            logCurrentThreadStackSize(context: context)
        }
    }
}

