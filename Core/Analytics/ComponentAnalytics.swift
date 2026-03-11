import Foundation

/**
 * 📊 Component Analytics
 * Аналитика для отслеживания использования 42 компонентов
 * Интеграция с AnalyticsManager
 */

class ComponentAnalytics {
    
    // MARK: - Recursion Protection
    private static let recursionKey = "ComponentAnalytics.isTracking"
    
    // MARK: - Singleton
    
    static let shared = ComponentAnalytics()
    
    private let analyticsManager = AnalyticsManager.shared
    
    private init() {}
    
    // MARK: - Component Toggle Tracking
    
    /**
     * Отследить переключение компонента
     * ✅ BUILD 102: Dictionary создается на main thread автоматически благодаря @MainActor
     */
    func trackComponentToggle(componentId: String, enabled: Bool) {
        // ✅ BUILD 112: Гарантируем выполнение на Main Thread внутри метода
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // 🛡️ BUILD 110: Защита от рекурсии на главном потоке
            let threadDict = Thread.current.threadDictionary
            if threadDict[Self.recursionKey] != nil {
                print("⚠️ [ComponentAnalytics] Recursion detected and blocked for \(componentId)")
                return
            }
            threadDict[Self.recursionKey] = true
            defer { threadDict.removeObject(forKey: Self.recursionKey) }
            
            let parameters: [String: Any] = [
                "component_id": componentId,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
            self.analyticsManager.trackEvent("component_toggle", parameters: parameters)
        }
    }
    
    // MARK: - Component Settings Tracking
    
    /**
     * Отследить открытие настроек компонента
     */
    func trackComponentSettingsOpened(componentId: String) {
        // ✅ BUILD 112: Внутренняя асинхронность
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // 🛡️ BUILD 111: Защита от рекурсии
            let threadDict = Thread.current.threadDictionary
            if threadDict[Self.recursionKey] != nil { return }
            threadDict[Self.recursionKey] = true
            defer { threadDict.removeObject(forKey: Self.recursionKey) }
            
            let parameters: [String: Any] = [
                "component_id": componentId,
                "timestamp": Date().timeIntervalSince1970
            ]
            self.analyticsManager.trackEvent("component_settings_opened", parameters: parameters)
        }
    }
    
    /**
     * Отследить сохранение настроек компонента
     */
    func trackComponentSettingsSaved(componentId: String, settings: [String: Any]) {
        // ✅ BUILD 112: Внутренняя асинхронность
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // 🛡️ BUILD 111: Защита от рекурсии
            let threadDict = Thread.current.threadDictionary
            if threadDict[Self.recursionKey] != nil { return }
            threadDict[Self.recursionKey] = true
            defer { threadDict.removeObject(forKey: Self.recursionKey) }
            
            let parameters: [String: Any] = [
                "component_id": componentId,
                "settings": settings,
                "timestamp": Date().timeIntervalSince1970
            ]
            self.analyticsManager.trackEvent("component_settings_saved", parameters: parameters)
        }
    }

    /**
     * Отследить переключение настройки компонента
     */
    func trackSettingToggle(componentId: String, settingKey: String, enabled: Bool) {
        // ✅ BUILD 112: Внутренняя асинхронность
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // 🛡️ BUILD 111: Защита от рекурсии
            let threadDict = Thread.current.threadDictionary
            if threadDict[Self.recursionKey] != nil { return }
            threadDict[Self.recursionKey] = true
            defer { threadDict.removeObject(forKey: Self.recursionKey) }
            
            let parameters: [String: Any] = [
                "component_id": componentId,
                "setting_key": settingKey,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
            self.analyticsManager.trackEvent("component_setting_toggle", parameters: parameters)
        }
    }
    
    // MARK: - Component Error Tracking
    
    /**
     * Отследить ошибку компонента
     */
    func trackComponentError(componentId: String, error: Error) {
        // ✅ BUILD 112: Внутренняя асинхронность
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // 🛡️ BUILD 111: Защита от рекурсии
            let threadDict = Thread.current.threadDictionary
            if threadDict[Self.recursionKey] != nil { return }
            threadDict[Self.recursionKey] = true
            defer { threadDict.removeObject(forKey: Self.recursionKey) }
            
            let parameters: [String: Any] = [
                "component_id": componentId,
                "error_type": String(describing: type(of: error)),
                "error_message": error.localizedDescription,
                "timestamp": Date().timeIntervalSince1970
            ]
            self.analyticsManager.trackEvent("component_error", parameters: parameters)
        }
    }
    
    // MARK: - Component Status Tracking
    
    /**
     * Отследить загрузку статуса компонента
     */
    func trackComponentStatusLoaded(componentId: String, isEnabled: Bool, loadTime: TimeInterval) {
        // ✅ BUILD 112: Внутренняя асинхронность
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // 🛡️ BUILD 111: Защита от рекурсии
            let threadDict = Thread.current.threadDictionary
            if threadDict[Self.recursionKey] != nil { return }
            threadDict[Self.recursionKey] = true
            defer { threadDict.removeObject(forKey: Self.recursionKey) }
            
            let parameters: [String: Any] = [
                "component_id": componentId,
                "is_enabled": isEnabled,
                "load_time": loadTime,
                "timestamp": Date().timeIntervalSince1970
            ]
            self.analyticsManager.trackEvent("component_status_loaded", parameters: parameters)
        }
    }
    
    // MARK: - Component Usage Statistics
    
    /**
     * Отследить использование компонента (включен/выключен)
     */
    func trackComponentUsage(componentId: String, duration: TimeInterval, enabled: Bool) {
        // ✅ BUILD 112: Внутренняя асинхронность
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // 🛡️ BUILD 111: Защита от рекурсии
            let threadDict = Thread.current.threadDictionary
            if threadDict[Self.recursionKey] != nil { return }
            threadDict[Self.recursionKey] = true
            defer { threadDict.removeObject(forKey: Self.recursionKey) }
            
            let parameters: [String: Any] = [
                "component_id": componentId,
                "duration": duration,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
            self.analyticsManager.trackEvent("component_usage", parameters: parameters)
        }
    }
    
    // MARK: - Screen Tracking
    
    /**
     * Отследить просмотр экрана с компонентами
     */
    func trackComponentScreenView(screenName: String, componentCount: Int) {
        // ✅ BUILD 112: Внутренняя асинхронность
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // 🛡️ BUILD 111: Защита от рекурсии
            let threadDict = Thread.current.threadDictionary
            if threadDict[Self.recursionKey] != nil { return }
            threadDict[Self.recursionKey] = true
            defer { threadDict.removeObject(forKey: Self.recursionKey) }
            
            self.analyticsManager.trackScreen(
                screenName,
                screenClass: "ComponentScreen"
            )
            
            let parameters: [String: Any] = [
                "screen_name": screenName,
                "component_count": componentCount,
                "timestamp": Date().timeIntervalSince1970
            ]
            self.analyticsManager.trackEvent("component_screen_view", parameters: parameters)
        }
    }
}

