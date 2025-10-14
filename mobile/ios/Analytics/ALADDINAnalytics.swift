//
//  ALADDINAnalytics.swift
//  ALADDIN Security
//
//  Created by AI Assistant on 2025-01-27.
//  Copyright © 2025 ALADDIN Security. All rights reserved.
//

import Foundation
import UIKit

/**
 * ALADDIN Analytics
 * Система аналитики для мобильного приложения ALADDIN Security
 * Отслеживание пользовательского поведения, производительности и безопасности
 */

class ALADDINAnalytics: ObservableObject {
    
    // MARK: - Singleton
    static let shared = ALADDINAnalytics()
    
    // MARK: - Properties
    @Published var isEnabled: Bool = true
    @Published var isDebugMode: Bool = false
    
    private var sessionId: String = ""
    private var userId: String = ""
    private var userProperties: [String: Any] = [:]
    private var eventQueue: [AnalyticsEvent] = []
    private var timer: Timer?
    
    // MARK: - Analytics Providers
    private var providers: [AnalyticsProvider] = []
    
    // MARK: - Initialization
    private init() {
        setupAnalytics()
        startSession()
    }
    
    deinit {
        stopSession()
    }
    
    // MARK: - Setup Methods
    
    private func setupAnalytics() {
        // Add analytics providers
        providers.append(FirebaseAnalyticsProvider())
        providers.append(ALADDINServerAnalyticsProvider())
        providers.append(LocalAnalyticsProvider())
        
        // Setup session tracking
        setupSessionTracking()
        
        // Setup performance monitoring
        setupPerformanceMonitoring()
        
        // Setup crash reporting
        setupCrashReporting()
    }
    
    private func setupSessionTracking() {
        sessionId = UUID().uuidString
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(appDidBecomeActive),
            name: UIApplication.didBecomeActiveNotification,
            object: nil
        )
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(appWillResignActive),
            name: UIApplication.willResignActiveNotification,
            object: nil
        )
    }
    
    private func setupPerformanceMonitoring() {
        // Monitor app launch time
        trackAppLaunchTime()
        
        // Monitor memory usage
        startMemoryMonitoring()
        
        // Monitor battery usage
        startBatteryMonitoring()
        
        // Monitor network performance
        startNetworkMonitoring()
    }
    
    private func setupCrashReporting() {
        // Setup crash reporting
        NSSetUncaughtExceptionHandler { exception in
            ALADDINAnalytics.shared.trackCrash(exception: exception)
        }
    }
    
    // MARK: - Session Management
    
    private func startSession() {
        let sessionEvent = AnalyticsEvent(
            name: "session_start",
            parameters: [
                "session_id": sessionId,
                "timestamp": Date().timeIntervalSince1970,
                "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown",
                "os_version": UIDevice.current.systemVersion,
                "device_model": UIDevice.current.model
            ]
        )
        
        trackEvent(sessionEvent)
    }
    
    private func stopSession() {
        let sessionEvent = AnalyticsEvent(
            name: "session_end",
            parameters: [
                "session_id": sessionId,
                "timestamp": Date().timeIntervalSince1970,
                "duration": getSessionDuration()
            ]
        )
        
        trackEvent(sessionEvent)
    }
    
    @objc private func appDidBecomeActive() {
        startSession()
    }
    
    @objc private func appWillResignActive() {
        stopSession()
    }
    
    // MARK: - Event Tracking
    
    func trackEvent(_ event: AnalyticsEvent) {
        guard isEnabled else { return }
        
        // Add session and user context
        var enrichedEvent = event
        enrichedEvent.parameters["session_id"] = sessionId
        enrichedEvent.parameters["user_id"] = userId
        enrichedEvent.parameters["timestamp"] = Date().timeIntervalSince1970
        
        // Add to queue
        eventQueue.append(enrichedEvent)
        
        // Send to providers
        for provider in providers {
            provider.trackEvent(enrichedEvent)
        }
        
        // Debug logging
        if isDebugMode {
            print("📊 Analytics Event: \(enrichedEvent.name) - \(enrichedEvent.parameters)")
        }
    }
    
    func trackEvent(name: String, parameters: [String: Any] = [:]) {
        let event = AnalyticsEvent(name: name, parameters: parameters)
        trackEvent(event)
    }
    
    // MARK: - User Management
    
    func setUserId(_ userId: String) {
        self.userId = userId
        
        let event = AnalyticsEvent(
            name: "user_identified",
            parameters: [
                "user_id": userId,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
        trackEvent(event)
    }
    
    func setUserProperty(key: String, value: Any) {
        userProperties[key] = value
        
        let event = AnalyticsEvent(
            name: "user_property_set",
            parameters: [
                "property_key": key,
                "property_value": value,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
        trackEvent(event)
    }
    
    // MARK: - Screen Tracking
    
    func trackScreenView(screenName: String, screenClass: String? = nil) {
        let event = AnalyticsEvent(
            name: "screen_view",
            parameters: [
                "screen_name": screenName,
                "screen_class": screenClass ?? screenName,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
        trackEvent(event)
    }
    
    // MARK: - VPN Analytics
    
    func trackVPNConnection(server: String, protocol: String, success: Bool) {
        let event = AnalyticsEvent(
            name: "vpn_connection",
            parameters: [
                "server": server,
                "protocol": protocol,
                "success": success,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
        trackEvent(event)
    }
    
    func trackVPNDisconnection(duration: TimeInterval, dataTransferred: Int64) {
        let event = AnalyticsEvent(
            name: "vpn_disconnection",
            parameters: [
                "duration": duration,
                "data_transferred": dataTransferred,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
        trackEvent(event)
    }
    
    // MARK: - Security Analytics
    
    func trackSecurityEvent(eventType: String, severity: String, details: [String: Any] = [:]) {
        let event = AnalyticsEvent(
            name: "security_event",
            parameters: [
                "event_type": eventType,
                "severity": severity,
                "details": details,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
        trackEvent(event)
    }
    
    func trackThreatDetected(threatType: String, source: String, blocked: Bool) {
        let event = AnalyticsEvent(
            name: "threat_detected",
            parameters: [
                "threat_type": threatType,
                "source": source,
                "blocked": blocked,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
        trackEvent(event)
    }
    
    // MARK: - Family Analytics
    
    func trackFamilyEvent(eventType: String, childId: String? = nil, details: [String: Any] = [:]) {
        var parameters: [String: Any] = [
            "event_type": eventType,
            "timestamp": Date().timeIntervalSince1970
        ]
        
        if let childId = childId {
            parameters["child_id"] = childId
        }
        
        parameters.merge(details) { (_, new) in new }
        
        let event = AnalyticsEvent(name: "family_event", parameters: parameters)
        trackEvent(event)
    }
    
    // MARK: - Performance Analytics
    
    func trackPerformanceMetric(metric: String, value: Double, unit: String = "") {
        let event = AnalyticsEvent(
            name: "performance_metric",
            parameters: [
                "metric": metric,
                "value": value,
                "unit": unit,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
        trackEvent(event)
    }
    
    func trackAppLaunchTime() {
        let launchTime = Date().timeIntervalSince1970
        trackPerformanceMetric(metric: "app_launch_time", value: launchTime, unit: "seconds")
    }
    
    // MARK: - Error Tracking
    
    func trackError(error: Error, context: String = "") {
        let event = AnalyticsEvent(
            name: "error_occurred",
            parameters: [
                "error_description": error.localizedDescription,
                "error_domain": (error as NSError).domain,
                "error_code": (error as NSError).code,
                "context": context,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
        trackEvent(event)
    }
    
    func trackCrash(exception: NSException) {
        let event = AnalyticsEvent(
            name: "crash_occurred",
            parameters: [
                "exception_name": exception.name.rawValue,
                "exception_reason": exception.reason ?? "unknown",
                "call_stack": exception.callStackSymbols,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
        trackEvent(event)
    }
    
    // MARK: - Monitoring Methods
    
    private func startMemoryMonitoring() {
        timer = Timer.scheduledTimer(withTimeInterval: 30.0, repeats: true) { _ in
            let memoryUsage = self.getMemoryUsage()
            self.trackPerformanceMetric(metric: "memory_usage", value: memoryUsage, unit: "MB")
        }
    }
    
    private func startBatteryMonitoring() {
        UIDevice.current.isBatteryMonitoringEnabled = true
        
        timer = Timer.scheduledTimer(withTimeInterval: 60.0, repeats: true) { _ in
            let batteryLevel = UIDevice.current.batteryLevel
            if batteryLevel >= 0 {
                self.trackPerformanceMetric(metric: "battery_level", value: Double(batteryLevel * 100), unit: "percent")
            }
        }
    }
    
    private func startNetworkMonitoring() {
        // Monitor network performance
        timer = Timer.scheduledTimer(withTimeInterval: 60.0, repeats: true) { _ in
            self.trackNetworkPerformance()
        }
    }
    
    private func trackNetworkPerformance() {
        // Track network performance metrics
        let event = AnalyticsEvent(
            name: "network_performance",
            parameters: [
                "timestamp": Date().timeIntervalSince1970,
                "connection_type": getConnectionType(),
                "is_connected": isNetworkConnected()
            ]
        )
        trackEvent(event)
    }
    
    // MARK: - Helper Methods
    
    private func getSessionDuration() -> TimeInterval {
        // Calculate session duration
        return Date().timeIntervalSince1970 - (userProperties["session_start_time"] as? TimeInterval ?? 0)
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
            return Double(info.resident_size) / (1024 * 1024) // Convert to MB
        }
        
        return 0.0
    }
    
    private func getConnectionType() -> String {
        // Determine connection type (WiFi, Cellular, etc.)
        return "unknown" // Implement based on your needs
    }
    
    private func isNetworkConnected() -> Bool {
        // Check if network is connected
        return true // Implement based on your needs
    }
}

// MARK: - Supporting Types

struct AnalyticsEvent {
    let name: String
    var parameters: [String: Any]
    let timestamp: TimeInterval
    
    init(name: String, parameters: [String: Any] = [:]) {
        self.name = name
        self.parameters = parameters
        self.timestamp = Date().timeIntervalSince1970
    }
}

protocol AnalyticsProvider {
    func trackEvent(_ event: AnalyticsEvent)
}

// MARK: - Analytics Providers

class FirebaseAnalyticsProvider: AnalyticsProvider {
    func trackEvent(_ event: AnalyticsEvent) {
        // Implement Firebase Analytics integration
        print("🔥 Firebase Analytics: \(event.name)")
    }
}

class ALADDINServerAnalyticsProvider: AnalyticsProvider {
    func trackEvent(_ event: AnalyticsEvent) {
        // Implement ALADDIN server analytics integration
        print("🛡️ ALADDIN Server Analytics: \(event.name)")
    }
}

class LocalAnalyticsProvider: AnalyticsProvider {
    func trackEvent(_ event: AnalyticsEvent) {
        // Implement local analytics storage
        print("💾 Local Analytics: \(event.name)")
    }
}

