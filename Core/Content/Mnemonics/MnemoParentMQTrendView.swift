import SwiftUI

/// Parent dashboard MQ sparkline — scores only, no test words (B12-T04).
struct MnemoParentMQTrendView: View {
    let localizationManager: LocalizationManager
    let points: [MnemonicBaselineAssessment.MQTrendPoint]
    let latestMQ: Int?
    let delta: Int?

    private let chartHeight: CGFloat = 56

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("parent_dashboard_mnemo_mq_title"))
                .font(.system(size: 18, weight: .semibold))

            Text(localizationManager.localized("parent_dashboard_mnemo_mq_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.72))

            if points.isEmpty {
                Text(localizationManager.localized("parent_dashboard_mnemo_mq_empty"))
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.72))
            } else {
                if let latestMQ {
                    Text(
                        String(
                            format: localizationManager.localized("parent_dashboard_mnemo_mq_latest"),
                            latestMQ
                        )
                    )
                    .font(.system(size: 14, weight: .semibold))
                    .accessibilityIdentifier("parent_dashboard_mnemo_mq_latest")
                }

                if let delta {
                    Text(
                        String(
                            format: localizationManager.localized("parent_dashboard_mnemo_mq_delta"),
                            delta
                        )
                    )
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(delta >= 0 ? .green.opacity(0.95) : .orange.opacity(0.95))
                }

                sparkline
                    .accessibilityIdentifier("parent_dashboard_mnemo_mq_sparkline")
            }

            Text(localizationManager.localized("parent_dashboard_mnemo_mq_disclaimer"))
                .font(.system(size: 10, weight: .medium))
                .foregroundColor(.white.opacity(0.55))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .accessibilityIdentifier("parent_dashboard_mnemo_mq_trend")
    }

    private var sparkline: some View {
        let maxMQ = max(points.map(\.memoryQuotient).max() ?? 0, 1)
        return HStack(alignment: .bottom, spacing: 8) {
            ForEach(points) { point in
                VStack(spacing: 4) {
                    ZStack(alignment: .bottom) {
                        RoundedRectangle(cornerRadius: 3)
                            .fill(Color.white.opacity(0.06))
                            .frame(height: chartHeight)
                        RoundedRectangle(cornerRadius: 3)
                            .fill(Color.purple.opacity(0.9))
                            .frame(
                                width: 12,
                                height: max(4, chartHeight * CGFloat(point.memoryQuotient) / CGFloat(maxMQ))
                            )
                    }
                    .frame(height: chartHeight)

                    Text(point.quarterLabel)
                        .font(.system(size: 9, weight: .medium))
                        .foregroundColor(.white.opacity(0.75))
                        .lineLimit(1)
                        .minimumScaleFactor(0.7)
                }
                .frame(maxWidth: .infinity)
            }
        }
        .frame(minHeight: chartHeight + 18)
    }
}
