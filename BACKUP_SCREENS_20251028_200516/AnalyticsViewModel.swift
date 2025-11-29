import SwiftUI
import Combine

/// 📊 Analytics View Model
/// Логика для экрана аналитики
class AnalyticsViewModel: ObservableObject {
    
    @Published var selectedPeriod: TimePeriod = .week
    @Published var threatsDetected: Int = 47
    @Published var threatsBlocked: Int = 45
    @Published var itemsScanned: Int = 5234
    @Published var protectionLevel: Double = 96
    @Published var topThreats: [ThreatItem] = []
    
    enum TimePeriod: String, CaseIterable {
        case day = "День"
        case week = "Неделя"
        case month = "Месяц"
    }
    
    struct ThreatItem: Identifiable {
        let id = UUID()
        let name: String
        let count: Int
        let icon: String
    }
    
    init() {
        loadAnalytics()
    }
    
    func loadAnalytics() {
        topThreats = [
            ThreatItem(name: "Вредоносные сайты", count: 23, icon: "🌐"),
            ThreatItem(name: "Фишинг", count: 12, icon: "🎣"),
            ThreatItem(name: "Трекеры", count: 8, icon: "👁️"),
            ThreatItem(name: "Вирусы", count: 4, icon: "🦠")
        ]
    }
    
    func changePeriod(_ period: TimePeriod) {
        selectedPeriod = period
        updateStatsForPeriod()
    }
    
    private func updateStatsForPeriod() {
        switch selectedPeriod {
        case .day:
            threatsDetected = 12
            threatsBlocked = 12
            itemsScanned = 847
        case .week:
            threatsDetected = 47
            threatsBlocked = 45
            itemsScanned = 5234
        case .month:
            threatsDetected = 189
            threatsBlocked = 185
            itemsScanned = 21890
        }
    }
}



