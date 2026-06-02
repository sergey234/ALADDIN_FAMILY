import SwiftUI

/// p3-18 — 1-tap mood widget (lock screen / home).
struct WellnessCheckinWidget: Widget {
    let kind = "WellnessCheckinWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: WellnessCheckinProvider()) { entry in
            WellnessCheckinWidgetView(entry: entry)
        }
        .configurationDisplayName("Wellness")
        .description("Quick mood check-in")
        .supportedFamilies([.systemSmall, .accessoryCircular, .accessoryRectangular])
    }
}

struct WellnessCheckinEntry: TimelineEntry {
    let date: Date
    let title: String
    let tapHint: String
    let lastMood: String
}

struct WellnessCheckinProvider: TimelineProvider {
    func placeholder(in context: Context) -> WellnessCheckinEntry {
        WellnessCheckinEntry(date: Date(), title: "How are you?", tapHint: "Tap to log", lastMood: "🙂")
    }

    func getSnapshot(in context: Context, completion: @escaping (WellnessCheckinEntry) -> Void) {
        completion(makeEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<WellnessCheckinEntry>) -> Void) {
        let entry = makeEntry()
        let next = Calendar.current.date(byAdding: .hour, value: 2, to: Date()) ?? Date().addingTimeInterval(7200)
        completion(Timeline(entries: [entry], policy: .after(next)))
    }

    private func makeEntry() -> WellnessCheckinEntry {
        let data = SharedDataManager.getWellnessWidgetData()
        return WellnessCheckinEntry(
            date: Date(),
            title: data.title,
            tapHint: data.tapHint,
            lastMood: data.lastMood
        )
    }
}

struct WellnessCheckinWidgetView: View {
    let entry: WellnessCheckinEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(entry.title).font(.headline)
            Text(entry.lastMood).font(.largeTitle)
            Text(entry.tapHint).font(.caption2).foregroundStyle(.secondary)
        }
        .padding(8)
        .widgetURL(URL(string: "aladdin://wellness/checkin"))
    }
}
