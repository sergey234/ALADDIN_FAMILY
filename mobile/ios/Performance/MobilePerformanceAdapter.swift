//
//  MobilePerformanceAdapter.swift
//  ALADDIN Security
//
//  Created by AI Assistant on 2025-01-27.
//  Copyright © 2025 ALADDIN Security. All rights reserved.
//

import Foundation
import UIKit
import Network

/**
 * Mobile Performance Adapter
 * Адаптер для интеграции существующего мониторинга производительности
 * с мобильным приложением ALADDIN
 */

class MobilePerformanceAdapter: ObservableObject {
    
    // MARK: - Published Properties
    @Published var cpuUsage: Double = 0.0
    @Published var memoryUsage: Double = 0.0
    @Published var batteryLevel: Float = 0.0
    @Published var batteryState: UIDevice.BatteryState = .unknown
    @Published var fps: Double = 60.0
    @Published var networkStatus: NetworkStatus = .unknown
    @Published var vpnStatus: VPNStatus = .disconnected
    @Published var isOptimized: Bool = false
    
    // MARK: - Private Properties
    private var displayLink: CADisplayLink?
    private var lastTimestamp: CFTimeInterval = 0
    private var frameCount: Int = 0
    private var monitoringTimer: Timer?
    private let networkMonitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "performance.monitor")
    
    // MARK: - Performance Metrics
    private var performanceMetrics = PerformanceMetrics()
    
    // MARK: - Initialization
    init() {
        setupMonitoring()
        startPerformanceMonitoring()
    }
    
    deinit {
        stopMonitoring()
    }
    
    // MARK: - Setup Methods
    
    private func setupMonitoring() {
        // Enable battery monitoring
        UIDevice.current.isBatteryMonitoringEnabled = true
        
        // Setup network monitoring
        networkMonitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.updateNetworkStatus(path)
            }
        }
        networkMonitor.start(queue: queue)
        
        // Setup FPS monitoring
        setupFPSMonitoring()
    }
    
    private func setupFPSMonitoring() {
        displayLink = CADisplayLink(target: self, selector: #selector(displayLinkTick))
        displayLink?.add(to: .main, forMode: .common)
    }
    
    @objc private func displayLinkTick(displayLink: CADisplayLink) {
        let currentTimestamp = displayLink.timestamp
        
        if lastTimestamp == 0 {
            lastTimestamp = currentTimestamp
            return
        }
        
        frameCount += 1
        let elapsed = currentTimestamp - lastTimestamp
        
        if elapsed >= 1.0 {
            fps = Double(frameCount) / elapsed
            frameCount = 0
            lastTimestamp = currentTimestamp
            
            // Update performance metrics
            performanceMetrics.updateFPS(fps)
        }
    }
    
    // MARK: - Monitoring Methods
    
    private func startPerformanceMonitoring() {
        monitoringTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.updateSystemMetrics()
        }
    }
    
    private func updateSystemMetrics() {
        // Update CPU usage
        cpuUsage = getCPUUsage()
        
        // Update memory usage
        memoryUsage = getMemoryUsage()
        
        // Update battery info
        batteryLevel = UIDevice.current.batteryLevel
        batteryState = UIDevice.current.batteryState
        
        // Update performance metrics
        performanceMetrics.updateCPU(cpuUsage)
        performanceMetrics.updateMemory(memoryUsage)
        performanceMetrics.updateBattery(batteryLevel)
        
        // Check if system is optimized
        checkOptimizationStatus()
    }
    
    private func updateNetworkStatus(_ path: NWPath) {
        if path.status == .satisfied {
            if path.usesInterfaceType(.wifi) {
                networkStatus = .wifi
            } else if path.usesInterfaceType(.cellular) {
                networkStatus = .cellular
            } else {
                networkStatus = .ethernet
            }
        } else {
            networkStatus = .disconnected
        }
    }
    
    // MARK: - System Metrics
    
    private func getCPUUsage() -> Double {
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
            return Double(info.resident_size) / (1024 * 1024) // Convert to MB
        }
        
        return 0.0
    }
    
    private func getMemoryUsage() -> Double {
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
            let memoryMB = Double(info.resident_size) / (1024 * 1024)
            let totalMemory = Double(ProcessInfo.processInfo.physicalMemory) / (1024 * 1024)
            return (memoryMB / totalMemory) * 100
        }
        
        return 0.0
    }
    
    // MARK: - Optimization Methods
    
    private func checkOptimizationStatus() {
        let isCPUGood = cpuUsage < 80.0
        let isMemoryGood = memoryUsage < 85.0
        let isFPSGood = fps >= 55.0
        let isBatteryGood = batteryLevel > 0.1 || batteryState == .charging
        
        isOptimized = isCPUGood && isMemoryGood && isFPSGood && isBatteryGood
    }
    
    // MARK: - Public Methods
    
    func getPerformanceReport() -> PerformanceReport {
        return PerformanceReport(
            cpuUsage: cpuUsage,
            memoryUsage: memoryUsage,
            batteryLevel: batteryLevel,
            batteryState: batteryState,
            fps: fps,
            networkStatus: networkStatus,
            vpnStatus: vpnStatus,
            isOptimized: isOptimized,
            timestamp: Date(),
            metrics: performanceMetrics
        )
    }
    
    func optimizePerformance() {
        // Trigger garbage collection
        autoreleasepool {
            // Force memory cleanup
        }
        
        // Optimize UI if needed
        if fps < 55.0 {
            // Reduce animation complexity
            // Disable heavy effects
        }
        
        // Update optimization status
        checkOptimizationStatus()
    }
    
    func stopMonitoring() {
        displayLink?.invalidate()
        monitoringTimer?.invalidate()
        networkMonitor.cancel()
    }
}

// MARK: - Supporting Types

enum NetworkStatus {
    case wifi
    case cellular
    case ethernet
    case disconnected
    case unknown
}

enum VPNStatus {
    case connected
    case connecting
    case disconnected
    case error
}

struct PerformanceMetrics {
    var cpuHistory: [Double] = []
    var memoryHistory: [Double] = []
    var fpsHistory: [Double] = []
    var batteryHistory: [Float] = []
    
    mutating func updateCPU(_ cpu: Double) {
        cpuHistory.append(cpu)
        if cpuHistory.count > 60 { // Keep last 60 seconds
            cpuHistory.removeFirst()
        }
    }
    
    mutating func updateMemory(_ memory: Double) {
        memoryHistory.append(memory)
        if memoryHistory.count > 60 {
            memoryHistory.removeFirst()
        }
    }
    
    mutating func updateFPS(_ fps: Double) {
        fpsHistory.append(fps)
        if fpsHistory.count > 60 {
            fpsHistory.removeFirst()
        }
    }
    
    mutating func updateBattery(_ battery: Float) {
        batteryHistory.append(battery)
        if batteryHistory.count > 60 {
            batteryHistory.removeFirst()
        }
    }
    
    var averageCPU: Double {
        return cpuHistory.isEmpty ? 0.0 : cpuHistory.reduce(0, +) / Double(cpuHistory.count)
    }
    
    var averageMemory: Double {
        return memoryHistory.isEmpty ? 0.0 : memoryHistory.reduce(0, +) / Double(memoryHistory.count)
    }
    
    var averageFPS: Double {
        return fpsHistory.isEmpty ? 0.0 : fpsHistory.reduce(0, +) / Double(fpsHistory.count)
    }
    
    var averageBattery: Float {
        return batteryHistory.isEmpty ? 0.0 : batteryHistory.reduce(0, +) / Float(batteryHistory.count)
    }
}

struct PerformanceReport {
    let cpuUsage: Double
    let memoryUsage: Double
    let batteryLevel: Float
    let batteryState: UIDevice.BatteryState
    let fps: Double
    let networkStatus: NetworkStatus
    let vpnStatus: VPNStatus
    let isOptimized: Bool
    let timestamp: Date
    let metrics: PerformanceMetrics
    
    var summary: String {
        return """
        CPU: \(String(format: "%.1f", cpuUsage))%
        Memory: \(String(format: "%.1f", memoryUsage))%
        Battery: \(String(format: "%.0f", batteryLevel * 100))%
        FPS: \(String(format: "%.1f", fps))
        Network: \(networkStatus)
        VPN: \(vpnStatus)
        Optimized: \(isOptimized ? "Yes" : "No")
        """
    }
}

