import SwiftUI
import Combine

/// 📊 Analytics View Model
/// Логика для экрана аналитики
class AnalyticsViewModel: ObservableObject {
    
    // Сохраняем выбранный период в @AppStorage
    @AppStorage("analytics_selected_period") var selectedPeriodRaw: String = TimePeriod.week.rawValue
    var selectedPeriod: TimePeriod {
        get { TimePeriod(rawValue: selectedPeriodRaw) ?? .week }
        set { selectedPeriodRaw = newValue.rawValue }
    }
    
    @Published var threatsDetected: Int = 0
    @Published var threatsBlocked: Int = 0
    @Published var itemsScanned: Int = 0
    @Published var protectionLevel: Double = 0
    @Published var topThreats: [ThreatItem] = []
    
    // Детальная статистика для DetailedStatsModal
    @Published var securityAnalytics: SecurityAnalytics?
    @Published var familyAnalytics: FamilyAnalytics?
    @Published var usageAnalytics: UsageAnalytics?
    @Published var devicesAnalytics: DevicesAnalytics?
    
    enum TimePeriod: String, CaseIterable { case day = "day", week = "week", month = "month" }
    
    struct ThreatItem: Identifiable {
        let id = UUID()
        let name: String
        let count: Int
        let icon: String
    }
    
    private let service: AnalyticsService
    private var currentFilters = AnalyticsFilters(onlyBlocked: false, includeFamily: true, includeDevices: true)
    private var loadTask: Task<Void, Never>? = nil

    init(service: AnalyticsService) {
        self.service = service
    }
    
    @MainActor
    func load() async {
        do {
            let summary = try await service.fetchSummary(period: selectedPeriod.rawValue, filters: currentFilters)
            threatsDetected = summary.threatsDetected
            threatsBlocked = summary.threatsBlocked
            itemsScanned = summary.itemsScanned
            protectionLevel = summary.protectionLevel
            // topThreats оставляем на будущее (требуется отдельный endpoint/модель)
        } catch {
            // минимальная обработка, расширим при подключении Remote
            print("AnalyticsViewModel.load error: \(error)")
        }
    }
    
    @MainActor
    func changePeriod(_ period: TimePeriod) async {
        selectedPeriod = period
        scheduleDebouncedLoad()
    }
    
    @MainActor
    func apply(filters: AnalyticsFilters) async {
        currentFilters = filters
        scheduleDebouncedLoad()
    }

    @MainActor
    private func scheduleDebouncedLoad(delay: UInt64 = 300_000_000) { // 300ms
        loadTask?.cancel()
        loadTask = Task { [weak self] in
            guard let self = self else { return }
            try? await Task.sleep(nanoseconds: delay)
            await self.load()
        }
    }
    
    // MARK: - Детальная статистика
    
    @MainActor
    func loadSecurityAnalytics() async {
        do {
            securityAnalytics = try await service.fetchSecurityAnalytics(period: selectedPeriod.rawValue)
        } catch {
            print("AnalyticsViewModel.loadSecurityAnalytics error: \(error)")
        }
    }
    
    @MainActor
    func loadFamilyAnalytics() async {
        do {
            familyAnalytics = try await service.fetchFamilyAnalytics(period: selectedPeriod.rawValue)
        } catch {
            print("AnalyticsViewModel.loadFamilyAnalytics error: \(error)")
        }
    }
    
    @MainActor
    func loadUsageAnalytics() async {
        do {
            usageAnalytics = try await service.fetchUsageAnalytics(period: selectedPeriod.rawValue)
        } catch {
            print("AnalyticsViewModel.loadUsageAnalytics error: \(error)")
        }
    }
    
    @MainActor
    func loadDevicesAnalytics() async {
        do {
            devicesAnalytics = try await service.fetchDevicesAnalytics(period: selectedPeriod.rawValue)
        } catch {
            print("AnalyticsViewModel.loadDevicesAnalytics error: \(error)")
        }
    }
}



