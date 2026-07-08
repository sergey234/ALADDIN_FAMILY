import SwiftUI

#if DEBUG
/// fws-08 — DEBUG-only SFM / antifake health probe (Settings).
struct DebugSFMHealthSection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var componentsSummary: String?
    @State private var antifakeSummary: String?
    @State private var isLoading = false
    @State private var lastChecked: Date?

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("debug_sfm_health_title"))
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.textPrimary)
                Spacer()
                Button {
                    Task { await refresh() }
                } label: {
                    Image(systemName: "arrow.clockwise")
                        .foregroundColor(.blue)
                }
                .disabled(isLoading)
                .accessibilityIdentifier("debug_sfm_health_refresh")
            }
            .accessibilityAddTraits(.isHeader)

            Text(localizationManager.localized("debug_sfm_health_subtitle"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)

            VStack(alignment: .leading, spacing: Spacing.s) {
                if isLoading {
                    HStack(spacing: Spacing.s) {
                        ProgressView()
                        Text(localizationManager.localized("debug_sfm_health_loading"))
                            .font(.subheadline)
                            .foregroundColor(.textSecondary)
                    }
                }

                if let componentsSummary {
                    healthRow(
                        title: localizationManager.localized("debug_sfm_health_components"),
                        value: componentsSummary
                    )
                }

                if let antifakeSummary {
                    healthRow(
                        title: localizationManager.localized("debug_sfm_health_antifake"),
                        value: antifakeSummary
                    )
                }

                if let lastChecked {
                    Text(
                        localizationManager.localized(
                            "debug_sfm_health_checked_at",
                            formatted(date: lastChecked)
                        )
                    )
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
                }

                Text(localizationManager.localized("debug_sfm_health_docs_hint"))
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: 12)
        }
        .accessibilityIdentifier("debug_sfm_health_section")
        .task {
            await refresh()
        }
    }

    @ViewBuilder
    private func healthRow(title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundColor(.textSecondary)
            Text(value)
                .font(.subheadline.monospaced())
                .foregroundColor(.textPrimary)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    @MainActor
    private func refresh() async {
        isLoading = true
        defer { isLoading = false }

        componentsSummary = await fetchComponentsHealth()
        antifakeSummary = await fetchAntifakeMetrics()
        lastChecked = Date()
    }

    private func fetchComponentsHealth() async -> String {
        await withCheckedContinuation { continuation in
            APIService.shared.getComponentsHealth { result in
                switch result {
                case .success(let health):
                    continuation.resume(
                        returning: "\(health.overallHealth) · \(health.healthyComponents)/\(health.totalComponents) ok"
                    )
                case .failure(let error):
                    continuation.resume(returning: "ERR \(shortError(error))")
                }
            }
        }
    }

    private func fetchAntifakeMetrics() async -> String {
        guard AppConfig.authToken != nil else {
            return localizationManager.localized("debug_sfm_health_auth_required")
        }
        return await withCheckedContinuation { continuation in
            APIService.shared.getAntifakeMetrics { result in
                switch result {
                case .success(let metrics):
                    continuation.resume(
                        returning: "checks=\(metrics.checksTotal) fake=\(metrics.fakeDetected) p95=\(metrics.latencyP95Ms)ms"
                    )
                case .failure(let error):
                    continuation.resume(returning: "ERR \(shortError(error))")
                }
            }
        }
    }

    private func shortError(_ error: Error) -> String {
        if let network = error as? NetworkError {
            switch network {
            case .unauthorized: return "401"
            case .serviceUnavailable(let msg): return msg ?? "503"
            default: return "net"
            }
        }
        return String(describing: error).prefix(48).description
    }

    private func formatted(date: Date) -> String {
        let f = DateFormatter()
        f.locale = localizationManager.locale
        f.timeStyle = .medium
        f.dateStyle = .short
        return f.string(from: date)
    }
}
#endif
