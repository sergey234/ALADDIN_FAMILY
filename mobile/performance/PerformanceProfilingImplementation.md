# 📊 Performance Profiling - План Реализации

## 🎯 **ЧТО ЭТО ТАКОЕ?**
**Performance Profiling** - это мониторинг производительности приложения в реальном времени. Это как датчики в машине - они показывают, как работает двигатель, сколько топлива тратится, и предупреждают о проблемах.

## ⚠️ **ЗАЧЕМ НУЖНО?**
- **Оптимизация производительности** - находить узкие места
- **Мониторинг ресурсов** - CPU, память, батарея
- **Предотвращение падений** - выявление проблем заранее
- **Улучшение UX** - плавная работа приложения

## 📱 **РЕАЛИЗАЦИЯ ДЛЯ iOS (Instruments + Custom Profiling)**

### Шаг 1: Создание Performance Monitor
```swift
// mobile/ios/Performance/PerformanceMonitor.swift
import Foundation
import os.signpost

class PerformanceMonitor {
    static let shared = PerformanceMonitor()
    
    private var metrics: [String: PerformanceMetric] = [:]
    private var timer: Timer?
    private let log = OSLog(subsystem: "com.aladdin.mobile", category: "Performance")
    
    // Начало мониторинга
    func startMonitoring() {
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            self.collectMetrics()
        }
    }
    
    // Остановка мониторинга
    func stopMonitoring() {
        timer?.invalidate()
        timer = nil
    }
    
    // Измерение времени выполнения
    func measureTime<T>(_ operation: () throws -> T, operationName: String) rethrows -> T {
        let startTime = CFAbsoluteTimeGetCurrent()
        
        os_signpost(.begin, log: log, name: "Operation", "%{public}s", operationName)
        
        defer {
            let timeElapsed = CFAbsoluteTimeGetCurrent() - startTime
            os_signpost(.end, log: log, name: "Operation", "%{public}s - %{public}f", operationName, timeElapsed)
            
            updateMetric(operationName, value: timeElapsed, type: .executionTime)
        }
        
        return try operation()
    }
    
    // Измерение использования памяти
    func measureMemory<T>(_ operation: () throws -> T, operationName: String) rethrows -> T {
        let startMemory = getMemoryUsage()
        
        defer {
            let endMemory = getMemoryUsage()
            let memoryDelta = endMemory - startMemory
            
            updateMetric(operationName, value: Double(memoryDelta), type: .memoryUsage)
        }
        
        return try operation()
    }
    
    // Сбор метрик
    private func collectMetrics() {
        let cpuUsage = getCPUUsage()
        let memoryUsage = getMemoryUsage()
        let batteryLevel = getBatteryLevel()
        let networkUsage = getNetworkUsage()
        
        updateMetric("cpu_usage", value: cpuUsage, type: .cpuUsage)
        updateMetric("memory_usage", value: Double(memoryUsage), type: .memoryUsage)
        updateMetric("battery_level", value: batteryLevel, type: .batteryLevel)
        updateMetric("network_usage", value: Double(networkUsage), type: .networkUsage)
        
        // Проверка на аномалии
        checkForAnomalies()
    }
    
    // Получение использования CPU
    private func getCPUUsage() -> Double {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4
        
        let kerr: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }
        
        if kerr == KERN_SUCCESS {
            return Double(info.resident_size) / 1024.0 / 1024.0 // MB
        }
        
        return 0.0
    }
    
    // Получение использования памяти
    private func getMemoryUsage() -> UInt64 {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4
        
        let kerr: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }
        
        if kerr == KERN_SUCCESS {
            return info.resident_size
        }
        
        return 0
    }
    
    // Получение уровня батареи
    private func getBatteryLevel() -> Double {
        UIDevice.current.isBatteryMonitoringEnabled = true
        return Double(UIDevice.current.batteryLevel)
    }
    
    // Получение использования сети
    private func getNetworkUsage() -> UInt64 {
        // Реализация получения статистики сети
        return 0
    }
    
    // Обновление метрики
    private func updateMetric(_ name: String, value: Double, type: MetricType) {
        if metrics[name] == nil {
            metrics[name] = PerformanceMetric(name: name, type: type)
        }
        
        metrics[name]?.addValue(value)
    }
    
    // Проверка на аномалии
    private func checkForAnomalies() {
        for (name, metric) in metrics {
            if metric.isAnomalous() {
                handleAnomaly(name, metric: metric)
            }
        }
    }
    
    // Обработка аномалий
    private func handleAnomaly(_ name: String, metric: PerformanceMetric) {
        // Логирование аномалии
        os_log("Performance anomaly detected: %{public}s = %{public}f", log: log, name, metric.currentValue)
        
        // Отправка в аналитику
        AnalyticsManager.shared.track("performance_anomaly", properties: [
            "metric_name": name,
            "metric_value": metric.currentValue,
            "metric_type": metric.type.rawValue
        ])
        
        // Уведомление разработчиков
        if metric.type == .memoryUsage && metric.currentValue > 200.0 { // 200MB
            sendCriticalAlert("High memory usage: \(metric.currentValue)MB")
        }
    }
}

// Структура метрики
struct PerformanceMetric {
    let name: String
    let type: MetricType
    private var values: [Double] = []
    private let maxValues = 100
    
    var currentValue: Double {
        return values.last ?? 0.0
    }
    
    var averageValue: Double {
        return values.isEmpty ? 0.0 : values.reduce(0, +) / Double(values.count)
    }
    
    mutating func addValue(_ value: Double) {
        values.append(value)
        if values.count > maxValues {
            values.removeFirst()
        }
    }
    
    func isAnomalous() -> Bool {
        guard values.count > 10 else { return false }
        
        let recent = Array(values.suffix(5))
        let average = recent.reduce(0, +) / Double(recent.count)
        let threshold = average * 2.0 // 200% от среднего
        
        return currentValue > threshold
    }
}

enum MetricType: String {
    case executionTime = "execution_time"
    case memoryUsage = "memory_usage"
    case cpuUsage = "cpu_usage"
    case batteryLevel = "battery_level"
    case networkUsage = "network_usage"
}
```

### Шаг 2: Создание Performance Dashboard
```swift
// mobile/ios/UI/PerformanceDashboard.swift
class PerformanceDashboard: UIView {
    @IBOutlet weak var cpuLabel: UILabel!
    @IBOutlet weak var memoryLabel: UILabel!
    @IBOutlet weak var batteryLabel: UILabel!
    @IBOutlet weak var networkLabel: UILabel!
    @IBOutlet weak var statusLabel: UILabel!
    
    private let performanceMonitor = PerformanceMonitor.shared
    
    override func awakeFromNib() {
        super.awakeFromNib()
        setupDashboard()
    }
    
    private func setupDashboard() {
        // Обновление каждые 2 секунды
        Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { _ in
            self.updateMetrics()
        }
    }
    
    private func updateMetrics() {
        let metrics = performanceMonitor.getCurrentMetrics()
        
        DispatchQueue.main.async {
            self.cpuLabel.text = "CPU: \(String(format: "%.1f", metrics.cpuUsage))%"
            self.memoryLabel.text = "Memory: \(String(format: "%.1f", metrics.memoryUsage))MB"
            self.batteryLabel.text = "Battery: \(String(format: "%.1f", metrics.batteryLevel * 100))%"
            self.networkLabel.text = "Network: \(String(format: "%.1f", metrics.networkUsage))KB/s"
            
            self.updateStatus(metrics)
        }
    }
    
    private func updateStatus(_ metrics: PerformanceMetrics) {
        if metrics.memoryUsage > 200.0 {
            statusLabel.text = "⚠️ High Memory Usage"
            statusLabel.textColor = .orange
        } else if metrics.cpuUsage > 80.0 {
            statusLabel.text = "⚠️ High CPU Usage"
            statusLabel.textColor = .orange
        } else if metrics.batteryLevel < 0.2 {
            statusLabel.text = "⚠️ Low Battery"
            statusLabel.textColor = .red
        } else {
            statusLabel.text = "✅ Performance OK"
            statusLabel.textColor = .green
        }
    }
}
```

## 🤖 **РЕАЛИЗАЦИЯ ДЛЯ ANDROID (Custom Profiling + Firebase Performance)**

### Шаг 1: Создание Performance Monitor
```kotlin
// mobile/android/Performance/PerformanceMonitor.kt
class PerformanceMonitor @Inject constructor(
    private val context: Context
) {
    private val metrics = mutableMapOf<String, PerformanceMetric>()
    private var timer: Timer? = null
    private val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
    private val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager
    
    // Начало мониторинга
    fun startMonitoring() {
        timer = Timer()
        timer?.scheduleAtFixedRate(object : TimerTask() {
            override fun run() {
                collectMetrics()
            }
        }, 0, 1000) // Каждую секунду
    }
    
    // Остановка мониторинга
    fun stopMonitoring() {
        timer?.cancel()
        timer = null
    }
    
    // Измерение времени выполнения
    inline fun <T> measureTime(operationName: String, operation: () -> T): T {
        val startTime = System.nanoTime()
        
        return try {
            operation()
        } finally {
            val timeElapsed = (System.nanoTime() - startTime) / 1_000_000.0 // ms
            updateMetric(operationName, timeElapsed, MetricType.EXECUTION_TIME)
        }
    }
    
    // Измерение использования памяти
    inline fun <T> measureMemory(operationName: String, operation: () -> T): T {
        val startMemory = getMemoryUsage()
        
        return try {
            operation()
        } finally {
            val endMemory = getMemoryUsage()
            val memoryDelta = endMemory - startMemory
            updateMetric(operationName, memoryDelta.toDouble(), MetricType.MEMORY_USAGE)
        }
    }
    
    // Сбор метрик
    private fun collectMetrics() {
        val cpuUsage = getCPUUsage()
        val memoryUsage = getMemoryUsage()
        val batteryLevel = getBatteryLevel()
        val networkUsage = getNetworkUsage()
        
        updateMetric("cpu_usage", cpuUsage, MetricType.CPU_USAGE)
        updateMetric("memory_usage", memoryUsage.toDouble(), MetricType.MEMORY_USAGE)
        updateMetric("battery_level", batteryLevel, MetricType.BATTERY_LEVEL)
        updateMetric("network_usage", networkUsage.toDouble(), MetricType.NETWORK_USAGE)
        
        // Проверка на аномалии
        checkForAnomalies()
    }
    
    // Получение использования CPU
    private fun getCPUUsage(): Double {
        val processInfo = activityManager.runningAppProcesses
        val myPid = android.os.Process.myPid()
        
        val myProcess = processInfo?.find { it.pid == myPid }
        return myProcess?.importance?.toDouble() ?: 0.0
    }
    
    // Получение использования памяти
    private fun getMemoryUsage(): Long {
        val memoryInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memoryInfo)
        return memoryInfo.totalMem - memoryInfo.availMem
    }
    
    // Получение уровня батареи
    private fun getBatteryLevel(): Double {
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val level = batteryIntent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = batteryIntent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        
        return if (level >= 0 && scale > 0) {
            level.toDouble() / scale.toDouble()
        } else {
            0.0
        }
    }
    
    // Получение использования сети
    private fun getNetworkUsage(): Long {
        // Реализация получения статистики сети
        return 0L
    }
    
    // Обновление метрики
    private fun updateMetric(name: String, value: Double, type: MetricType) {
        val metric = metrics.getOrPut(name) { PerformanceMetric(name, type) }
        metric.addValue(value)
    }
    
    // Проверка на аномалии
    private fun checkForAnomalies() {
        for ((name, metric) in metrics) {
            if (metric.isAnomalous()) {
                handleAnomaly(name, metric)
            }
        }
    }
    
    // Обработка аномалий
    private fun handleAnomaly(name: String, metric: PerformanceMetric) {
        Log.w("PerformanceMonitor", "Anomaly detected: $name = ${metric.currentValue}")
        
        // Отправка в аналитику
        FirebaseAnalytics.getInstance(context).logEvent("performance_anomaly", Bundle().apply {
            putString("metric_name", name)
            putDouble("metric_value", metric.currentValue)
            putString("metric_type", metric.type.name)
        })
        
        // Уведомление разработчиков
        if (metric.type == MetricType.MEMORY_USAGE && metric.currentValue > 200.0) {
            sendCriticalAlert("High memory usage: ${metric.currentValue}MB")
        }
    }
}

// Класс метрики
data class PerformanceMetric(
    val name: String,
    val type: MetricType,
    private val values: MutableList<Double> = mutableListOf()
) {
    val currentValue: Double
        get() = values.lastOrNull() ?: 0.0
    
    val averageValue: Double
        get() = if (values.isEmpty()) 0.0 else values.average()
    
    fun addValue(value: Double) {
        values.add(value)
        if (values.size > 100) {
            values.removeAt(0)
        }
    }
    
    fun isAnomalous(): Boolean {
        if (values.size < 10) return false
        
        val recent = values.takeLast(5)
        val average = recent.average()
        val threshold = average * 2.0 // 200% от среднего
        
        return currentValue > threshold
    }
}

enum class MetricType {
    EXECUTION_TIME,
    MEMORY_USAGE,
    CPU_USAGE,
    BATTERY_LEVEL,
    NETWORK_USAGE
}
```

### Шаг 2: Интеграция с Firebase Performance
```kotlin
// mobile/android/Performance/FirebasePerformanceIntegration.kt
class FirebasePerformanceIntegration @Inject constructor() {
    
    fun startTrace(traceName: String): Trace {
        return FirebasePerformance.getInstance().newTrace(traceName)
    }
    
    fun measureNetworkRequest(url: String, request: () -> Unit) {
        val trace = startTrace("network_request_$url")
        trace.start()
        
        try {
            request()
        } finally {
            trace.stop()
        }
    }
    
    fun measureDatabaseOperation(operationName: String, operation: () -> Unit) {
        val trace = startTrace("database_$operationName")
        trace.start()
        
        try {
            operation()
        } finally {
            trace.stop()
        }
    }
}
```

## 📋 **ПЛАН ВНЕДРЕНИЯ (1 неделя)**

### День 1-2: Базовая реализация
- [ ] Создать PerformanceMonitor для iOS
- [ ] Создать PerformanceMonitor для Android
- [ ] Реализовать сбор базовых метрик

### День 3-4: Интеграция с UI
- [ ] Создать PerformanceDashboard для iOS
- [ ] Создать PerformanceDashboard для Android
- [ ] Добавить визуализацию метрик

### День 5-7: Оптимизация и тестирование
- [ ] Интегрировать с Firebase Performance
- [ ] Добавить алерты и уведомления
- [ ] Тестирование и оптимизация

## 🎨 **UI КОМПОНЕНТЫ**

### Performance Chart
```swift
// iOS
class PerformanceChartView: UIView {
    private var chartData: [Double] = []
    
    func updateChart(with data: [Double]) {
        chartData = data
        setNeedsDisplay()
    }
    
    override func draw(_ rect: CGRect) {
        // Отрисовка графика производительности
    }
}
```

```kotlin
// Android
class PerformanceChartView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {
    
    private var chartData: List<Double> = emptyList()
    
    fun updateChart(data: List<Double>) {
        chartData = data
        invalidate()
    }
    
    override fun onDraw(canvas: Canvas?) {
        super.onDraw(canvas)
        // Отрисовка графика производительности
    }
}
```

## ⚠️ **ВАЖНЫЕ МОМЕНТЫ**

### ✅ **ПЛЮСЫ:**
- Реальное время мониторинга
- Предотвращение проблем
- Оптимизация производительности
- Лучший пользовательский опыт

### ⚠️ **МИНУСЫ:**
- Дополнительное потребление ресурсов
- Сложность реализации
- Необходимость интерпретации данных
- Потенциальные ложные срабатывания

## 📊 **МЕТРИКИ УСПЕХА**
- [ ] 99%+ время работы без аномалий
- [ ] <5% влияние на производительность
- [ ] 90%+ точность обнаружения проблем
- [ ] <1 секунда время отклика на аномалии

---

*Критически важно для поддержания высокой производительности!*

