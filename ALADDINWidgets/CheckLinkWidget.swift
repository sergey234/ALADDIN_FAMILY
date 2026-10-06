import WidgetKit
import SwiftUI

/// fsl-16 — виджет Home Screen «Проверить ссылку» → Antifake Hub.
struct CheckLinkWidget: Widget {
    let kind = "CheckLinkWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: CheckLinkProvider()) { entry in
            CheckLinkWidgetView(entry: entry)
        }
        .configurationDisplayName(WidgetL10n.localized("check_link_widget_name"))
        .description(WidgetL10n.localized("check_link_widget_desc"))
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

struct CheckLinkEntry: TimelineEntry {
    let date: Date
}

struct CheckLinkProvider: TimelineProvider {
    func placeholder(in context: Context) -> CheckLinkEntry {
        CheckLinkEntry(date: Date())
    }

    func getSnapshot(in context: Context, completion: @escaping (CheckLinkEntry) -> Void) {
        completion(CheckLinkEntry(date: Date()))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<CheckLinkEntry>) -> Void) {
        let entry = CheckLinkEntry(date: Date())
        let next = Calendar.current.date(byAdding: .hour, value: 12, to: Date()) ?? Date().addingTimeInterval(43_200)
        completion(Timeline(entries: [entry], policy: .after(next)))
    }
}

struct CheckLinkWidgetView: View {
    let entry: CheckLinkEntry

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.05, green: 0.09, blue: 0.18),
                    Color(red: 0.14, green: 0.28, blue: 0.32),
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            VStack(alignment: .leading, spacing: 8) {
                Image(systemName: "link.badge.plus")
                    .font(.title2.weight(.semibold))
                    .foregroundColor(Color(red: 0.95, green: 0.78, blue: 0.35))
                Text(WidgetL10n.localized("check_link_widget_title"))
                    .font(.headline)
                    .foregroundColor(.white)
                    .lineLimit(2)
                Text(WidgetL10n.localized("check_link_widget_subtitle"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
                    .lineLimit(3)
                Spacer(minLength: 0)
            }
            .padding(12)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        }
        .widgetURL(URL(string: "aladdin://antifake/check"))
    }
}
