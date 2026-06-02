import Foundation
import WidgetKit

/**
 * 📊 Shared Data Manager
 * Общий менеджер данных для виджетов и основного приложения
 * Использует App Groups для обмена данными
 */

class SharedDataManager {
    
    // MARK: - App Group Identifier
    
    private static let appGroupIdentifier = "group.com.aladdin.family"
    private static let userDefaults = UserDefaults(suiteName: appGroupIdentifier)!
    
    // MARK: - Keys
    
    private enum Keys {
        static let familyProtectionEnabled = "family_protection_enabled"
        static let childrenOnline = "children_online"
        static let threatsBlocked = "threats_blocked"
        static let networkProtectionConnected = "network_protection_connected"
        static let networkProtectionServer = "network_protection_server"
        static let networkProtectionSpeed = "network_protection_speed"
        static let networkProtectionUptime = "network_protection_uptime"
        static let websitesBlocked = "websites_blocked"
        static let appsBlocked = "apps_blocked"
        static let dataSaved = "data_saved"
        static let protectionLevel = "protection_level"
        static let lastUpdate = "last_update"
        static let wellnessWidgetTitle = "wellness_widget_title"
        static let wellnessWidgetTap = "wellness_widget_tap"
        static let wellnessLastMood = "wellness_last_mood"
    }
    
    // MARK: - Family Protection Data
    
    static func updateFamilyProtectionData(
        isEnabled: Bool,
        childrenOnline: Int,
        threatsBlocked: Int
    ) {
        userDefaults.set(isEnabled, forKey: Keys.familyProtectionEnabled)
        userDefaults.set(childrenOnline, forKey: Keys.childrenOnline)
        userDefaults.set(threatsBlocked, forKey: Keys.threatsBlocked)
        userDefaults.set(Date(), forKey: Keys.lastUpdate)
        
        // Обновить виджеты
        WidgetCenter.shared.reloadAllTimelines()
    }
    
    static func getFamilyProtectionData() -> (isEnabled: Bool, childrenOnline: Int, threatsBlocked: Int) {
        let isEnabled = userDefaults.bool(forKey: Keys.familyProtectionEnabled)
        let childrenOnline = userDefaults.integer(forKey: Keys.childrenOnline)
        let threatsBlocked = userDefaults.integer(forKey: Keys.threatsBlocked)
        
        return (isEnabled, childrenOnline, threatsBlocked)
    }
    
    // MARK: - Network Protection Data
    
    static func updateNetworkProtectionData(
        isConnected: Bool,
        server: String,
        speed: String,
        uptime: String
    ) {
        userDefaults.set(isConnected, forKey: Keys.networkProtectionConnected)
        userDefaults.set(server, forKey: Keys.networkProtectionServer)
        userDefaults.set(speed, forKey: Keys.networkProtectionSpeed)
        userDefaults.set(uptime, forKey: Keys.networkProtectionUptime)
        userDefaults.set(Date(), forKey: Keys.lastUpdate)
        
        // Обновить виджеты
        WidgetCenter.shared.reloadAllTimelines()
    }
    
    static func getNetworkProtectionData() -> (isConnected: Bool, server: String, speed: String, uptime: String) {
        let isConnected = userDefaults.bool(forKey: Keys.networkProtectionConnected)
        let server = userDefaults.string(forKey: Keys.networkProtectionServer) ?? "Не подключен"
        let speed = userDefaults.string(forKey: Keys.networkProtectionSpeed) ?? "0 Мбит/с"
        let uptime = userDefaults.string(forKey: Keys.networkProtectionUptime) ?? "0м"
        
        return (isConnected, server, speed, uptime)
    }
    
    // MARK: - Analytics Data
    
    static func updateAnalyticsData(
        threatsBlocked: Int,
        websitesBlocked: Int,
        appsBlocked: Int,
        dataSaved: String,
        protectionLevel: String
    ) {
        userDefaults.set(threatsBlocked, forKey: Keys.threatsBlocked)
        userDefaults.set(websitesBlocked, forKey: Keys.websitesBlocked)
        userDefaults.set(appsBlocked, forKey: Keys.appsBlocked)
        userDefaults.set(dataSaved, forKey: Keys.dataSaved)
        userDefaults.set(protectionLevel, forKey: Keys.protectionLevel)
        userDefaults.set(Date(), forKey: Keys.lastUpdate)
        
        // Обновить виджеты
        WidgetCenter.shared.reloadAllTimelines()
    }
    
    static func getAnalyticsData() -> (threatsBlocked: Int, websitesBlocked: Int, appsBlocked: Int, dataSaved: String, protectionLevel: String) {
        let threatsBlocked = userDefaults.integer(forKey: Keys.threatsBlocked)
        let websitesBlocked = userDefaults.integer(forKey: Keys.websitesBlocked)
        let appsBlocked = userDefaults.integer(forKey: Keys.appsBlocked)
        let dataSaved = userDefaults.string(forKey: Keys.dataSaved) ?? "0 ГБ"
        let protectionLevel = userDefaults.string(forKey: Keys.protectionLevel) ?? "Средний"
        
        return (threatsBlocked, websitesBlocked, appsBlocked, dataSaved, protectionLevel)
    }
    
    // MARK: - Last Update
    
    static func getLastUpdate() -> Date {
        return userDefaults.object(forKey: Keys.lastUpdate) as? Date ?? Date()
    }

    // MARK: - Wellness Widget (p3-18)

    static func updateWellnessWidgetData(title: String, tapHint: String, lastMood: String) {
        userDefaults.set(title, forKey: Keys.wellnessWidgetTitle)
        userDefaults.set(tapHint, forKey: Keys.wellnessWidgetTap)
        userDefaults.set(lastMood, forKey: Keys.wellnessLastMood)
        userDefaults.set(Date(), forKey: Keys.lastUpdate)
        WidgetCenter.shared.reloadTimelines(ofKind: "WellnessCheckinWidget")
    }

    static func getWellnessWidgetData() -> (title: String, tapHint: String, lastMood: String) {
        (
            userDefaults.string(forKey: Keys.wellnessWidgetTitle) ?? "How are you?",
            userDefaults.string(forKey: Keys.wellnessWidgetTap) ?? "Tap to log",
            userDefaults.string(forKey: Keys.wellnessLastMood) ?? "🙂"
        )
    }

    // MARK: - Clear Data
    
    static func clearAllData() {
        let keys = [
            Keys.familyProtectionEnabled,
            Keys.childrenOnline,
            Keys.threatsBlocked,
            Keys.networkProtectionConnected,
            Keys.networkProtectionServer,
            Keys.networkProtectionSpeed,
            Keys.networkProtectionUptime,
            Keys.websitesBlocked,
            Keys.appsBlocked,
            Keys.dataSaved,
            Keys.protectionLevel,
            Keys.lastUpdate
        ]
        
        for key in keys {
            userDefaults.removeObject(forKey: key)
        }
        
        WidgetCenter.shared.reloadAllTimelines()
    }
}

// MARK: - Mock Data for Testing

extension SharedDataManager {
    
    static func setMockData() {
        // Mock Family Protection Data
        updateFamilyProtectionData(
            isEnabled: true,
            childrenOnline: 2,
            threatsBlocked: 15
        )
        
        // Mock Network Protection Data
        updateNetworkProtectionData(
            isConnected: true,
            server: "Германия",
            speed: "45 Мбит/с",
            uptime: "2ч 15м"
        )
        
        // Mock Analytics Data
        updateAnalyticsData(
            threatsBlocked: 15,
            websitesBlocked: 8,
            appsBlocked: 3,
            dataSaved: "2.3 ГБ",
            protectionLevel: "Высокий"
        )
    }
}
