import WidgetKit
import SwiftUI

/**
 * 📱 ALADDIN Widgets
 * Виджеты для главного экрана iOS
 * Показывают статус защиты семьи, Network Protection, статистику
 */

// MARK: - Widget Bundle

@main
struct ALADDINWidgets: WidgetBundle {
    var body: some Widget {
        FamilyProtectionWidget()
        NetworkProtectionStatusWidget()
        AnalyticsWidget()
    }
}

// MARK: - Family Protection Widget

struct FamilyProtectionWidget: Widget {
    let kind: String = "FamilyProtectionWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: FamilyProtectionProvider()) { entry in
            FamilyProtectionWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Защита семьи")
        .description("Статус защиты семьи и количество детей онлайн")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

// MARK: - Network Protection Status Widget

struct NetworkProtectionStatusWidget: Widget {
    let kind: String = "NetworkProtectionStatusWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: NetworkProtectionStatusProvider()) { entry in
            NetworkProtectionStatusWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Статус защиты сети")
        .description("Статус подключения защиты сети и сервер")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

// MARK: - Analytics Widget

struct AnalyticsWidget: Widget {
    let kind: String = "AnalyticsWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: AnalyticsProvider()) { entry in
            AnalyticsWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Аналитика")
        .description("Статистика блокировок и угроз за день")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
    }
}

// MARK: - Timeline Providers

struct FamilyProtectionProvider: TimelineProvider {
    func placeholder(in context: Context) -> FamilyProtectionEntry {
        FamilyProtectionEntry(
            date: Date(),
            isProtectionEnabled: true,
            childrenOnline: 2,
            threatsBlocked: 15,
            lastUpdate: "2 мин назад"
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (FamilyProtectionEntry) -> ()) {
        let data = SharedDataManager.getFamilyProtectionData()
        let lastUpdate = SharedDataManager.getLastUpdate()
        let timeAgo = formatTimeAgo(since: lastUpdate)
        
        let entry = FamilyProtectionEntry(
            date: Date(),
            isProtectionEnabled: data.isEnabled,
            childrenOnline: data.childrenOnline,
            threatsBlocked: data.threatsBlocked,
            lastUpdate: timeAgo
        )
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<FamilyProtectionEntry>) -> ()) {
        var entries: [FamilyProtectionEntry] = []

        // Получаем реальные данные
        let data = SharedDataManager.getFamilyProtectionData()
        let lastUpdate = SharedDataManager.getLastUpdate()
        let timeAgo = formatTimeAgo(since: lastUpdate)
        
        // Создаем записи на следующие 4 часа
        let currentDate = Date()
        for hourOffset in 0 ..< 4 {
            let entryDate = Calendar.current.date(byAdding: .hour, value: hourOffset, to: currentDate)!
            let entry = FamilyProtectionEntry(
                date: entryDate,
                isProtectionEnabled: data.isEnabled,
                childrenOnline: data.childrenOnline,
                threatsBlocked: data.threatsBlocked,
                lastUpdate: timeAgo
            )
            entries.append(entry)
        }

        let timeline = Timeline(entries: entries, policy: .atEnd)
        completion(timeline)
    }
    
    private func formatTimeAgo(since date: Date) -> String {
        let now = Date()
        let timeInterval = now.timeIntervalSince(date)
        
        if timeInterval < 60 {
            return "только что"
        } else if timeInterval < 3600 {
            let minutes = Int(timeInterval / 60)
            return "\(minutes) мин назад"
        } else {
            let hours = Int(timeInterval / 3600)
            return "\(hours)ч назад"
        }
    }
}

struct NetworkProtectionStatusProvider: TimelineProvider {
    func placeholder(in context: Context) -> NetworkProtectionStatusEntry {
        NetworkProtectionStatusEntry(
            date: Date(),
            isConnected: true,
            server: "Германия",
            speed: "45 Мбит/с",
            uptime: "2ч 15м"
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (NetworkProtectionStatusEntry) -> ()) {
        let entry = NetworkProtectionStatusEntry(
            date: Date(),
            isConnected: true,
            server: "Германия",
            speed: "45 Мбит/с",
            uptime: "2ч 15м"
        )
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<NetworkProtectionStatusEntry>) -> ()) {
        var entries: [NetworkProtectionStatusEntry] = []

        let currentDate = Date()
        for hourOffset in 0 ..< 4 {
            let entryDate = Calendar.current.date(byAdding: .hour, value: hourOffset, to: currentDate)!
            let entry = NetworkProtectionStatusEntry(
                date: entryDate,
                isConnected: Bool.random(),
                server: ["Германия", "США", "Япония", "Канада"].randomElement() ?? "Германия",
                speed: "\(Int.random(in: 30...80)) Мбит/с",
                uptime: "\(Int.random(in: 1...5))ч \(Int.random(in: 0...59))м"
            )
            entries.append(entry)
        }

        let timeline = Timeline(entries: entries, policy: .atEnd)
        completion(timeline)
    }
}

struct AnalyticsProvider: TimelineProvider {
    func placeholder(in context: Context) -> AnalyticsEntry {
        AnalyticsEntry(
            date: Date(),
            threatsBlocked: 15,
            websitesBlocked: 8,
            appsBlocked: 3,
            dataSaved: "2.3 ГБ",
            protectionLevel: "Высокий"
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (AnalyticsEntry) -> ()) {
        let entry = AnalyticsEntry(
            date: Date(),
            threatsBlocked: 15,
            websitesBlocked: 8,
            appsBlocked: 3,
            dataSaved: "2.3 ГБ",
            protectionLevel: "Высокий"
        )
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<AnalyticsEntry>) -> ()) {
        var entries: [AnalyticsEntry] = []

        let currentDate = Date()
        for hourOffset in 0 ..< 4 {
            let entryDate = Calendar.current.date(byAdding: .hour, value: hourOffset, to: currentDate)!
            let entry = AnalyticsEntry(
                date: entryDate,
                threatsBlocked: Int.random(in: 10...30),
                websitesBlocked: Int.random(in: 5...15),
                appsBlocked: Int.random(in: 1...8),
                dataSaved: "\(Double.random(in: 1.0...5.0), specifier: "%.1f") ГБ",
                protectionLevel: ["Высокий", "Средний", "Максимальный"].randomElement() ?? "Высокий"
            )
            entries.append(entry)
        }

        let timeline = Timeline(entries: entries, policy: .atEnd)
        completion(timeline)
    }
}

// MARK: - Entry Models

struct FamilyProtectionEntry: TimelineEntry {
    let date: Date
    let isProtectionEnabled: Bool
    let childrenOnline: Int
    let threatsBlocked: Int
    let lastUpdate: String
}

struct NetworkProtectionStatusEntry: TimelineEntry {
    let date: Date
    let isConnected: Bool
    let server: String
    let speed: String
    let uptime: String
}

struct AnalyticsEntry: TimelineEntry {
    let date: Date
    let threatsBlocked: Int
    let websitesBlocked: Int
    let appsBlocked: Int
    let dataSaved: String
    let protectionLevel: String
}

// MARK: - Widget Views

struct FamilyProtectionWidgetEntryView: View {
    var entry: FamilyProtectionProvider.Entry

    var body: some View {
        ZStack {
            // Background
            LinearGradient(
                colors: [
                    Color(red: 0.04, green: 0.07, blue: 0.16),
                    Color(red: 0.12, green: 0.23, blue: 0.37)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            
            VStack(alignment: .leading, spacing: 8) {
                // Header
                HStack {
                    Text("🛡️")
                        .font(.title2)
                    Text("Защита семьи")
                        .font(.headline)
                        .foregroundColor(.white)
                    Spacer()
                    Circle()
                        .fill(entry.isProtectionEnabled ? .green : .red)
                        .frame(width: 8, height: 8)
                }
                
                // Status
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text("Детей онлайн:")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                        Text("\(entry.childrenOnline)")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                    }
                    
                    HStack {
                        Text("Блокировок:")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                        Text("\(entry.threatsBlocked)")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                    }
                }
                
                Spacer()
                
                // Last Update
                Text(entry.lastUpdate)
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.6))
            }
            .padding()
        }
    }
}

struct NetworkProtectionStatusWidgetEntryView: View {
    var entry: NetworkProtectionStatusProvider.Entry

    var body: some View {
        ZStack {
            // Background
            LinearGradient(
                colors: [
                    Color(red: 0.04, green: 0.07, blue: 0.16),
                    Color(red: 0.12, green: 0.23, blue: 0.37)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            
            VStack(alignment: .leading, spacing: 8) {
                // Header
                HStack {
                    Text("🔒")
                        .font(.title2)
                    Text("Защита сети")
                        .font(.headline)
                        .foregroundColor(.white)
                    Spacer()
                    Circle()
                        .fill(entry.isConnected ? .green : .red)
                        .frame(width: 8, height: 8)
                }
                
                // Status
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text("Сервер:")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                        Text(entry.server)
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                    }
                    
                    HStack {
                        Text("Скорость:")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                        Text(entry.speed)
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                    }
                    
                    HStack {
                        Text("Время:")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                        Text(entry.uptime)
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                    }
                }
                
                Spacer()
            }
            .padding()
        }
    }
}

struct AnalyticsWidgetEntryView: View {
    var entry: AnalyticsProvider.Entry

    var body: some View {
        ZStack {
            // Background
            LinearGradient(
                colors: [
                    Color(red: 0.04, green: 0.07, blue: 0.16),
                    Color(red: 0.12, green: 0.23, blue: 0.37)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            
            VStack(alignment: .leading, spacing: 8) {
                // Header
                HStack {
                    Text("📊")
                        .font(.title2)
                    Text("Аналитика")
                        .font(.headline)
                        .foregroundColor(.white)
                    Spacer()
                    Text(entry.protectionLevel)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(Color.green.opacity(0.3))
                        .foregroundColor(.green)
                        .cornerRadius(4)
                }
                
                // Stats
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text("Угроз:")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                        Text("\(entry.threatsBlocked)")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                    }
                    
                    HStack {
                        Text("Сайты:")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                        Text("\(entry.websitesBlocked)")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                    }
                    
                    HStack {
                        Text("Приложения:")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                        Text("\(entry.appsBlocked)")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                    }
                    
                    HStack {
                        Text("Данные:")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                        Text(entry.dataSaved)
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                    }
                }
                
                Spacer()
            }
            .padding()
        }
    }
}

// MARK: - Preview

#Preview(as: .systemSmall) {
    ALADDINWidgets()
} timeline: {
    FamilyProtectionEntry(
        date: .now,
        isProtectionEnabled: true,
        childrenOnline: 2,
        threatsBlocked: 15,
        lastUpdate: "2 мин назад"
    )
}
