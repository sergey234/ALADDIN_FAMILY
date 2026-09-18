import WidgetKit
import SwiftUI

/// VSL-C P2 — Home Screen “Now” for Voice Safety Log (App Group, no child spy).
struct VoiceSafetyNowWidget: Widget {
    let kind = "VoiceSafetyNowWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: VoiceSafetyNowProvider()) { entry in
            VoiceSafetyNowWidgetView(entry: entry)
        }
        .configurationDisplayName(WidgetL10n.localized("voice_safety_widget_name"))
        .description(WidgetL10n.localized("voice_safety_widget_desc"))
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

struct VoiceSafetyNowEntry: TimelineEntry {
    let date: Date
    let line: String
    let detail: String
}

struct VoiceSafetyNowProvider: TimelineProvider {
    func placeholder(in context: Context) -> VoiceSafetyNowEntry {
        VoiceSafetyNowEntry(
            date: Date(),
            line: WidgetL10n.localized("voice_safety_now_checking"),
            detail: ""
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (VoiceSafetyNowEntry) -> Void) {
        completion(makeEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<VoiceSafetyNowEntry>) -> Void) {
        let entry = makeEntry()
        let next = Calendar.current.date(byAdding: .hour, value: 1, to: Date()) ?? Date().addingTimeInterval(3600)
        completion(Timeline(entries: [entry], policy: .after(next)))
    }

    private func makeEntry() -> VoiceSafetyNowEntry {
        let data = SharedDataManager.getVoiceSafetyWidgetData()
        return VoiceSafetyNowEntry(date: Date(), line: data.line, detail: data.detail)
    }
}

struct VoiceSafetyNowWidgetView: View {
    let entry: VoiceSafetyNowEntry

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.04, green: 0.07, blue: 0.16),
                    Color(red: 0.12, green: 0.23, blue: 0.37)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            VStack(alignment: .leading, spacing: 6) {
                Text(WidgetL10n.localized("voice_safety_now_caption"))
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.7))
                Text(entry.line)
                    .font(.headline)
                    .foregroundColor(.white)
                    .lineLimit(2)
                if !entry.detail.isEmpty {
                    Text(entry.detail)
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.8))
                        .lineLimit(2)
                }
                Spacer(minLength: 0)
            }
            .padding(12)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        }
        .widgetURL(URL(string: "aladdin://voice/log"))
    }
}
