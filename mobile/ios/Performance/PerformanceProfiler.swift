import Foundation
import UIKit

class PerformanceProfiler {
    static let shared = PerformanceProfiler()
    
    private var isMonitoring = false
    private var monitoringTimer: Timer?
    private var metrics: [PerformanceMetric] = []
    
    private init() {}
    
    // MARK: - Monitoring Control
    
    func startMonitoring() {
        guard !isMonitoring else { return }
        
        isMonitoring = true
        print("📊 Performance monitoring started")
        
        monitoringTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.collectMetrics()
        }
    }
    
    func stopMonitoring() {
        guard isMonitoring else { return }
        
        isMonitoring = false
        monitoringTimer?.invalidate()
        monitoringTimer = nil
        
        print("📊 Performance monitoring stopped")
    }
    
    // MARK: - Metrics Collection
    
    private func collectMetrics() {
        let metric = PerformanceMetric(
            cpuUsage: getCPUUsage(),
            memoryUsage: getMemoryUsage(),
            fps: getFPS(),
            batteryLevel: getBatteryLevel(),
            networkActivity: getNetworkActivity(),
            timestamp: Date()
        )
        
        metrics.append(metric)
        
        // Keep only last 60 metrics (1 minute)
        if metrics.count > 60 {
            metrics.removeFirst()
        }
    }
    
    // MARK: - CPU Usage
    
    private func getCPUUsage() -> Double {
        var totalUsageOfCPU: Double = 0.0
        var threadsList: thread_act_array_t?
        var threadsCount = mach_msg_type_number_t(0)
        let threadsResult = withUnsafeMutablePointer(to: &threadsList) {
            return $0.withMemoryRebound(to: thread_act_array_t?.self, capacity: 1) {
                task_threads(mach_task_self_, $0, &threadsCount)
            }
        }
        
        if threadsResult == KERN_SUCCESS, let threadsList = threadsList {
            for index in 0..<threadsCount {
                var threadInfo = thread_basic_info()
                var threadInfoCount = mach_msg_type_number_t(THREAD_INFO_MAX)
                let infoResult = withUnsafeMutablePointer(to: &threadInfo) {
                    $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                        thread_info(threadsList[Int(index)], thread_flavor_t(THREAD_BASIC_INFO), $0, &threadInfoCount)
                    }
                }
                
                guard infoResult == KERN_SUCCESS else {
                    break
                }
                
                let threadBasicInfo = threadInfo as thread_basic_info
                if threadBasicInfo.flags & TH_FLAGS_IDLE == 0 {
                    totalUsageOfCPU += (Double(threadBasicInfo.cpu_usage) / Double(TH_USAGE_SCALE)) * 100.0
                }
            }
        }
        
        vm_deallocate(mach_task_self_, vm_address_t(UInt(bitPattern: threadsList)), vm_size_t(Int(threadsCount) * MemoryLayout<thread_t>.stride))
        
        return totalUsageOfCPU
    }
    
    // MARK: - Memory Usage
    
    private func getMemoryUsage() -> UInt64 {
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
            return info.resident_size
        }
        
        return 0
    }
    
    // MARK: - FPS
    
    private var displayLink: CADisplayLink?
    private var lastTimestamp: CFTimeInterval = 0
    private var frameCount: Int = 0
    private var currentFPS: Double = 60.0
    
    private func getFPS() -> Double {
        return currentFPS
    }
    
    func startFPSMonitoring() {
        displayLink = CADisplayLink(target: self, selector: #selector(displayLinkTick))
        displayLink?.add(to: .main, forMode: .common)
    }
    
    func stopFPSMonitoring() {
        displayLink?.invalidate()
        displayLink = nil
    }
    
    @objc private func displayLinkTick(displayLink: CADisplayLink) {
        if lastTimestamp == 0 {
            lastTimestamp = displayLink.timestamp
            return
        }
        
        frameCount += 1
        let elapsed = displayLink.timestamp - lastTimestamp
        
        if elapsed >= 1.0 {
            currentFPS = Double(frameCount) / elapsed
            frameCount = 0
            lastTimestamp = displayLink.timestamp
        }
    }
    
    // MARK: - Battery Level
    
    private func getBatteryLevel() -> Float {
        UIDevice.current.isBatteryMonitoringEnabled = true
        return UIDevice.current.batteryLevel
    }
    
    // MARK: - Network Activity
    
    private var lastNetworkBytes: UInt64 = 0
    
    private func getNetworkActivity() -> Double {
        let currentBytes = getNetworkBytes()
        let delta = currentBytes - lastNetworkBytes
        lastNetworkBytes = currentBytes
        
        // Convert to KB/s
        return Double(delta) / 1024.0
    }
    
    private func getNetworkBytes() -> UInt64 {
        var ifaddr: UnsafeMutablePointer<ifaddrs>?
        var totalBytes: UInt64 = 0
        
        if getifaddrs(&ifaddr) == 0 {
            var ptr = ifaddr
            while ptr != nil {
                defer { ptr = ptr?.pointee.ifa_next }
                
                let interface = ptr?.pointee
                let addrFamily = interface?.ifa_addr.pointee.sa_family
                
                if addrFamily == UInt8(AF_LINK) {
                    let data = unsafeBitCast(interface?.ifa_data, to: UnsafeMutablePointer<if_data>.self)
                    totalBytes += UInt64(data.pointee.ifi_ibytes) + UInt64(data.pointee.ifi_obytes)
                }
            }
            freeifaddrs(ifaddr)
        }
        
        return totalBytes
    }
    
    // MARK: - Reports
    
    func getCurrentMetrics() -> PerformanceMetric? {
        return metrics.last
    }
    
    func getAverageMetrics() -> PerformanceMetric? {
        guard !metrics.isEmpty else { return nil }
        
        let avgCPU = metrics.map { $0.cpuUsage }.reduce(0, +) / Double(metrics.count)
        let avgMemory = metrics.map { $0.memoryUsage }.reduce(0, +) / UInt64(metrics.count)
        let avgFPS = metrics.map { $0.fps }.reduce(0, +) / Double(metrics.count)
        let avgBattery = metrics.map { $0.batteryLevel }.reduce(0, +) / Float(metrics.count)
        let avgNetwork = metrics.map { $0.networkActivity }.reduce(0, +) / Double(metrics.count)
        
        return PerformanceMetric(
            cpuUsage: avgCPU,
            memoryUsage: avgMemory,
            fps: avgFPS,
            batteryLevel: avgBattery,
            networkActivity: avgNetwork,
            timestamp: Date()
        )
    }
    
    func getDetailedReport() -> String {
        guard let current = getCurrentMetrics(),
              let average = getAverageMetrics() else {
            return "No metrics available"
        }
        
        var report = "📊 Performance Report\n"
        report += "====================\n\n"
        
        report += "Current Metrics:\n"
        report += "- CPU Usage: \(String(format: "%.1f", current.cpuUsage))%\n"
        report += "- Memory: \(formatBytes(current.memoryUsage))\n"
        report += "- FPS: \(String(format: "%.1f", current.fps))\n"
        report += "- Battery: \(String(format: "%.0f", current.batteryLevel * 100))%\n"
        report += "- Network: \(String(format: "%.1f", current.networkActivity)) KB/s\n\n"
        
        report += "Average Metrics (Last Minute):\n"
        report += "- CPU Usage: \(String(format: "%.1f", average.cpuUsage))%\n"
        report += "- Memory: \(formatBytes(average.memoryUsage))\n"
        report += "- FPS: \(String(format: "%.1f", average.fps))\n"
        report += "- Battery: \(String(format: "%.0f", average.batteryLevel * 100))%\n"
        report += "- Network: \(String(format: "%.1f", average.networkActivity)) KB/s\n"
        
        return report
    }
    
    private func formatBytes(_ bytes: UInt64) -> String {
        let formatter = ByteCountFormatter()
        formatter.countStyle = .memory
        return formatter.string(fromByteCount: Int64(bytes))
    }
}

// MARK: - Performance Metric

struct PerformanceMetric {
    let cpuUsage: Double
    let memoryUsage: UInt64
    let fps: Double
    let batteryLevel: Float
    let networkActivity: Double
    let timestamp: Date
}

