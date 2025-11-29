import Foundation
import SwiftUI

/// 📊 Protection Level History Entry
/// Запись истории изменения уровня защиты
struct ProtectionLevelHistoryEntry: Identifiable, Codable {
    let id: UUID
    let level: Int
    let date: Date
    let enabledFeatures: [String] // ID включенных функций
    
    init(level: Int, date: Date = Date(), enabledFeatures: [String] = []) {
        self.id = UUID()
        self.level = level
        self.date = date
        self.enabledFeatures = enabledFeatures
    }
}

/// 📈 Protection Level History Manager
/// Менеджер для хранения и загрузки истории уровней защиты
class ProtectionLevelHistoryManager: ObservableObject {
    static let shared = ProtectionLevelHistoryManager()
    
    @Published var history: [ProtectionLevelHistoryEntry] = []
    
    private let historyKey = "protection_level_history"
    private let maxHistoryDays = 30 // Храним историю 30 дней
    
    private init() {
        loadHistory()
        cleanOldHistory()
    }
    
    // MARK: - Save History Entry
    
    /// Сохраняет новую запись в истории при изменении уровня защиты
    func saveLevelChange(_ level: Int, enabledFeatures: [String]) {
        let entry = ProtectionLevelHistoryEntry(
            level: level,
            date: Date(),
            enabledFeatures: enabledFeatures
        )
        
        // Проверяем, что уровень действительно изменился
        if let lastEntry = history.last, lastEntry.level == level {
            // Если уровень тот же, обновляем последнюю запись
            if let index = history.lastIndex(where: { $0.level == level && Calendar.current.isDate($0.date, inSameDayAs: Date()) }) {
                history[index] = entry
            } else {
                history.append(entry)
            }
        } else {
            history.append(entry)
        }
        
        saveHistory()
    }
    
    // MARK: - Get History
    
    /// Получает историю за последние N дней
    func getHistoryForDays(_ days: Int) -> [ProtectionLevelHistoryEntry] {
        let cutoffDate = Calendar.current.date(byAdding: .day, value: -days, to: Date()) ?? Date()
        return history.filter { $0.date >= cutoffDate }.sorted { $0.date > $1.date }
    }
    
    /// Получает историю за последние 7 дней для графика
    func getWeeklyHistory() -> [ProtectionLevelHistoryEntry] {
        return getHistoryForDays(7)
    }
    
    /// Получает историю за последние 30 дней
    func getMonthlyHistory() -> [ProtectionLevelHistoryEntry] {
        return getHistoryForDays(30)
    }
    
    /// Получает средний уровень защиты за период
    func getAverageLevel(for days: Int) -> Double {
        let periodHistory = getHistoryForDays(days)
        guard !periodHistory.isEmpty else { return 0 }
        let sum = periodHistory.reduce(0) { $0 + $1.level }
        return Double(sum) / Double(periodHistory.count)
    }
    
    // MARK: - Clean Old History
    
    private func cleanOldHistory() {
        let cutoffDate = Calendar.current.date(byAdding: .day, value: -maxHistoryDays, to: Date()) ?? Date()
        history = history.filter { $0.date >= cutoffDate }
        saveHistory()
    }
    
    // MARK: - Save/Load
    
    private func saveHistory() {
        if let encoded = try? JSONEncoder().encode(history) {
            UserDefaults.standard.set(encoded, forKey: historyKey)
        }
    }
    
    private func loadHistory() {
        if let data = UserDefaults.standard.data(forKey: historyKey),
           let decoded = try? JSONDecoder().decode([ProtectionLevelHistoryEntry].self, from: data) {
            history = decoded.sorted { $0.date > $1.date }
        }
    }
}
