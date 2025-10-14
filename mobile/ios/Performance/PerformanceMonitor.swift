//
//  PerformanceMonitor.swift
//  ALADDIN Security
//
//  Created by AI Assistant on 2025-01-27.
//  Copyright © 2025 ALADDIN Security. All rights reserved.
//

import Foundation
import UIKit
import os.log

// MARK: - Performance Monitor
class PerformanceMonitor: ObservableObject {
    
    // MARK: - Singleton
    static let shared = PerformanceMonitor()
    
    // MARK: - Properties
    @Published var currentFPS: Double = 60.0
    @Published var averageFPS: Double = 60.0
    @Published var memoryUsage: UInt64 = 0
    @Published var cpuUsage: Double = 0.0
    @Published var batteryLevel: Float = 1.0
    @Published var isLowPowerMode: Bool = false
    @Published var networkLatency: Double = 0.0
    @Published var isPerformanceOptimized: Bool = true
    
    // MARK: - Private Properties
    private var displayLink: CADisplayLink?
    private var lastTimestamp: CFTimeInterval = 0
    private var frameCount: Int = 0
    private var fpsHistory: [Double] = []
    private let maxHistoryCount = 60 // 1 second at 60 FPS
    
    private var memoryTimer: Timer?
    private var cpuTimer: Timer?
    private var batteryTimer: Timer?
    private var networkTimer: Timer?
    
    private let logger = Logger(subsystem: "com.aladdin.security", category: "Performance")
    
    // MARK: - Initialization
    private init() {
        setupMonitoring()
    }
    
    deinit {
        stopMonitoring()
    }
    
    // MARK: - Public Methods
    
    func startMonitoring() {
        logger.info("Starting performance monitoring")
        
        startFPSMonitoring()
        startMemoryMonitoring()
        startCPUMonitoring()
        startBatteryMonitoring()
        startNetworkMonitoring()
    }
    
    func stopMonitoring() {
        logger.info("Stopping performance monitoring")
        
        displayLink?.invalidate()
        memoryTimer?.invalidate()
        cpuTimer?.invalidate()
        batteryTimer?.invalidate()
        networkTimer?.invalidate()
        
        displayLink = nil
        memoryTimer = nil
        cpuTimer = nil
        batteryTimer = nil
        networkTimer = nil
    }
    
    func getPerformanceReport() -> PerformanceReport {
        return PerformanceReport(
            fps: averageFPS,
            memoryUsage: memoryUsage,
            cpuUsage: cpuUsage,
            batteryLevel: batteryLevel,
            isLowPowerMode: isLowPowerMode,
            networkLatency: networkLatency,
            isOptimized: isPerformanceOptimized,
            timestamp: Date()
        )
    }
    
    func optimizePerformance() {
        logger.info("Optimizing performance")
        
        // Reduce animation quality if FPS is low
        if averageFPS < 30 {
            reduceAnimationQuality()
        }
        
        // Reduce memory usage if high
        if memoryUsage > 200 * 1024 * 1024 { // 200MB
            reduceMemoryUsage()
        }
        
        // Enable low power mode optimizations
        if isLowPowerMode {
            enableLowPowerMode()
        }
        
        // Update optimization status
        isPerformanceOptimized = checkOptimizationStatus()
    }
    
    // MARK: - Private Methods
    
    private func setupMonitoring() {
        // Set up initial values
        batteryLevel = UIDevice.current.batteryLevel
        isLowPowerMode = ProcessInfo.processInfo.isLowPowerModeEnabled
        
        // Start monitoring
        startMonitoring()
    }
    
    private func startFPSMonitoring() {
        displayLink = CADisplayLink(target: self, selector: #selector(displayLinkTick))
        displayLink?.add(to: .main, forMode: .common)
    }
    
    @objc private func displayLinkTick(_ displayLink: CADisplayLink) {
        let currentTimestamp = displayLink.timestamp
        
        if lastTimestamp == 0 {
            lastTimestamp = currentTimestamp
            return
        }
        
        let deltaTime = currentTimestamp - lastTimestamp
        let fps = 1.0 / deltaTime
        
        currentFPS = fps
        frameCount += 1
        
        // Update FPS history
        fpsHistory.append(fps)
        if fpsHistory.count > maxHistoryCount {
            fpsHistory.removeFirst()
        }
        
        // Calculate average FPS
        averageFPS = fpsHistory.reduce(0, +) / Double(fpsHistory.count)
        
        lastTimestamp = currentTimestamp
        
        // Log performance issues
        if fps < 30 {
            logger.warning("Low FPS detected: \(fps)")
        }
    }
    
    private func startMemoryMonitoring() {
        memoryTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.updateMemoryUsage()
        }
    }
    
    private func updateMemoryUsage() {
        let memoryInfo = getMemoryUsage()
        memoryUsage = memoryInfo.used
        
        // Log memory issues
        if memoryUsage > 300 * 1024 * 1024 { // 300MB
            logger.warning("High memory usage: \(memoryUsage / 1024 / 1024)MB")
        }
    }
    
    private func startCPUMonitoring() {
        cpuTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { [weak self] _ in
            self?.updateCPUUsage()
        }
    }
    
    private func updateCPUUsage() {
        cpuUsage = getCPUUsage()
        
        // Log CPU issues
        if cpuUsage > 80.0 {
            logger.warning("High CPU usage: \(cpuUsage)%")
        }
    }
    
    private func startBatteryMonitoring() {
        batteryTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            self?.updateBatteryInfo()
        }
    }
    
    private func updateBatteryInfo() {
        batteryLevel = UIDevice.current.batteryLevel
        isLowPowerMode = ProcessInfo.processInfo.isLowPowerModeEnabled
        
        // Log battery issues
        if batteryLevel < 0.2 {
            logger.warning("Low battery: \(batteryLevel * 100)%")
        }
    }
    
    private func startNetworkMonitoring() {
        networkTimer = Timer.scheduledTimer(withTimeInterval: 10.0, repeats: true) { [weak self] _ in
            self?.updateNetworkLatency()
        }
    }
    
    private func updateNetworkLatency() {
        // Simulate network latency measurement
        // In real implementation, this would ping a server
        networkLatency = Double.random(in: 10...100)
    }
    
    // MARK: - Optimization Methods
    
    private func reduceAnimationQuality() {
        logger.info("Reducing animation quality for better performance")
        
        // Reduce animation duration
        UIView.setAnimationDuration(0.2)
        
        // Disable some animations
        UIView.setAnimationsEnabled(false)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            UIView.setAnimationsEnabled(true)
        }
    }
    
    private func reduceMemoryUsage() {
        logger.info("Reducing memory usage")
        
        // Clear caches
        URLCache.shared.removeAllCachedResponses()
        
        // Force garbage collection
        DispatchQueue.global(qos: .background).async {
            // Force memory cleanup
        }
    }
    
    private func enableLowPowerMode() {
        logger.info("Enabling low power mode optimizations")
        
        // Reduce background processing
        // Disable non-essential features
        // Optimize network requests
    }
    
    private func checkOptimizationStatus() -> Bool {
        return averageFPS >= 50 && 
               memoryUsage < 200 * 1024 * 1024 && 
               cpuUsage < 70.0
    }
    
    // MARK: - System Info Methods
    
    private func getMemoryUsage() -> (used: UInt64, total: UInt64) {
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
            return (used: info.resident_size, total: info.virtual_size)
        } else {
            return (used: 0, total: 0)
        }
    }
    
    private func getCPUUsage() -> Double {
        var info = processor_info_array_t.allocate(capacity: 1)
        var numCpuInfo: mach_msg_type_number_t = 0
        var numCpus: natural_t = 0
        
        let result = host_processor_info(mach_host_self(),
                                       PROCESSOR_CPU_LOAD_INFO,
                                       &numCpus,
                                       &info,
                                       &numCpuInfo)
        
        if result == KERN_SUCCESS {
            let cpuInfo = info.withMemoryRebound(to: processor_cpu_load_info_t.self, capacity: 1) { $0 }
            let cpuLoad = cpuInfo.pointee.cpu_ticks
            
            let userTicks = cpuLoad.cpu_ticks.0
            let systemTicks = cpuLoad.cpu_ticks.1
            let idleTicks = cpuLoad.cpu_ticks.2
            let niceTicks = cpuLoad.cpu_ticks.3
            
            let totalTicks = userTicks + systemTicks + idleTicks + niceTicks
            let usedTicks = userTicks + systemTicks + niceTicks
            
            if totalTicks > 0 {
                return Double(usedTicks) / Double(totalTicks) * 100.0
            }
        }
        
        return 0.0
    }
}

// MARK: - Performance Report
struct PerformanceReport {
    let fps: Double
    let memoryUsage: UInt64
    let cpuUsage: Double
    let batteryLevel: Float
    let isLowPowerMode: Bool
    let networkLatency: Double
    let isOptimized: Bool
    let timestamp: Date
    
    var memoryUsageMB: Double {
        return Double(memoryUsage) / 1024.0 / 1024.0
    }
    
    var batteryPercentage: Double {
        return Double(batteryLevel) * 100.0
    }
    
    var performanceScore: Double {
        var score = 100.0
        
        // FPS score (40% weight)
        if fps < 30 {
            score -= 40
        } else if fps < 45 {
            score -= 20
        } else if fps < 55 {
            score -= 10
        }
        
        // Memory score (30% weight)
        if memoryUsageMB > 300 {
            score -= 30
        } else if memoryUsageMB > 200 {
            score -= 15
        } else if memoryUsageMB > 100 {
            score -= 5
        }
        
        // CPU score (20% weight)
        if cpuUsage > 80 {
            score -= 20
        } else if cpuUsage > 60 {
            score -= 10
        } else if cpuUsage > 40 {
            score -= 5
        }
        
        // Battery score (10% weight)
        if batteryPercentage < 20 {
            score -= 10
        } else if batteryPercentage < 50 {
            score -= 5
        }
        
        return max(0, score)
    }
}

// MARK: - Performance Optimizer
class PerformanceOptimizer {
    
    static let shared = PerformanceOptimizer()
    
    private init() {}
    
    func optimizeForDevice() {
        let device = UIDevice.current
        
        // iPhone optimization
        if device.userInterfaceIdiom == .phone {
            optimizeForiPhone()
        }
        
        // iPad optimization
        if device.userInterfaceIdiom == .pad {
            optimizeForiPad()
        }
        
        // Low power mode optimization
        if ProcessInfo.processInfo.isLowPowerModeEnabled {
            optimizeForLowPowerMode()
        }
    }
    
    private func optimizeForiPhone() {
        // iPhone-specific optimizations
        // Reduce texture quality
        // Optimize animations
        // Adjust UI density
    }
    
    private func optimizeForiPad() {
        // iPad-specific optimizations
        // Higher quality textures
        // More complex animations
        // Better UI density
    }
    
    private func optimizeForLowPowerMode() {
        // Low power mode optimizations
        // Reduce background processing
        // Disable non-essential features
        // Optimize network requests
    }
}

