import SwiftUI

/// 📊 Analytics View Model
/// Упрощённый state для экрана аналитики
class AnalyticsViewModel: ObservableObject {
    @Published private(set) var threatsDetected: Int = 0
    @Published private(set) var threatsBlocked: Int = 0
    @Published private(set) var itemsScanned: Int = 0
    @Published private(set) var protectionLevel: Double = 0
    @Published private(set) var threatCategories: [ThreatTypeCount] = []
    @Published private(set) var isLoading: Bool = false
    @Published private(set) var errorMessage: String?
    
    private let service: AnalyticsService
    private let defaultPeriod = "day"
    private let defaultFilters = AnalyticsFilters(onlyBlocked: false, includeFamily: true, includeDevices: true)
    
    init(service: AnalyticsService) {
        self.service = service
    }
    
    @MainActor
    func load() async {
        isLoading = true
        errorMessage = nil
        
        do {
            async let summaryTask = service.fetchSummary(period: defaultPeriod, filters: defaultFilters)
            async let securityTask = service.fetchSecurityAnalytics(period: defaultPeriod)
            
            let (summary, security) = try await (summaryTask, securityTask)
            apply(summary: summary)
            apply(securityAnalytics: security)
        } catch {
            errorMessage = "Не удалось загрузить аналитику"
            resetState()
            print("[AnalyticsViewModel] load error: \(error)")
        }
        
        isLoading = false
    }
    
    // MARK: - Private helpers
    private func apply(summary: AnalyticsSummary) {
        threatsDetected = summary.threatsDetected
        threatsBlocked = summary.threatsBlocked
        itemsScanned = summary.itemsScanned
        protectionLevel = summary.protectionLevel
    }
    
    private func apply(securityAnalytics: SecurityAnalytics) {
        threatCategories = securityAnalytics.blockedThreats
    }
    
    @MainActor
    private func resetState() {
        threatsDetected = 0
        threatsBlocked = 0
        itemsScanned = 0
        protectionLevel = 0
        threatCategories = []
    }
}
