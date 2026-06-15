import SwiftUI

/// Result card for sync antifake checks (J-01…J-05, F-10, I-01…I-08).
struct AntifakeVerdictCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let verdict: SecurityVerdict
    /// Phone from call check metadata — required for crowd reports (I-01).
    var reportPhone: String? = nil

    @State private var showReportSheet = false
    @State private var showAppealSheet = false
    @State private var reportNote = ""
    @State private var reportLabel = ""
    @State private var isSubmittingReport = false
    @State private var reportFeedback: String?
    @State private var reportError: String?

    private var accentColor: Color {
        switch verdict.verdict {
        case .likelyFake: return .dangerRed
        case .uncertain: return .warningOrange
        case .likelyReal: return .successGreen
        }
    }

    private var iconName: String {
        switch verdict.verdict {
        case .likelyFake: return "exclamationmark.shield.fill"
        case .uncertain: return "questionmark.circle.fill"
        case .likelyReal: return "checkmark.shield.fill"
        }
    }

    private var verdictTitleKey: String {
        switch verdict.verdict {
        case .likelyFake: return "antifake_verdict_likely_fake"
        case .uncertain: return "antifake_verdict_uncertain"
        case .likelyReal: return "antifake_verdict_likely_real"
        }
    }

    private var sourceBadgeKey: String {
        let normalized = verdict.source.lowercased()
        if normalized.contains("probe")
            || (normalized.contains("heuristic") && !normalized.contains("local_ml")) {
            return "antifake_verdict_source_probe"
        }
        if normalized.contains("real")
            || normalized.contains("agent")
            || normalized.contains("sfm")
            || normalized.contains("local_ml") {
            return "antifake_verdict_source_ai"
        }
        return "antifake_verdict_source_rules"
    }

    private var topReasons: [String] {
        Array(verdict.reasons.prefix(3))
    }

    private var spoofHints: [String] {
        var hints: [String] = []
        let tags = Set(verdict.reasons.map { $0.lowercased() })
        if tags.contains("display_number_mismatch") {
            hints.append(localizationManager.localized("antifake_spoof_hint_display_mismatch"))
        }
        if tags.contains(where: { $0.contains("authority") || $0.contains("spoof") }) {
            hints.append(localizationManager.localized("antifake_spoof_hint_authority"))
        }
        return hints
    }

    private var nextStepsKey: String {
        let joined = verdict.reasons.joined(separator: " ").lowercased()
        if joined.contains("перевед") || joined.contains("send money") || joined.contains("scam")
            || joined.contains("счёт") || joined.contains("bank") {
            return "antifake_verdict_next_steps_bank"
        }
        if joined.contains("родствен") || joined.contains("family") {
            return "antifake_verdict_next_steps_family"
        }
        if joined.contains("налог") || joined.contains("tax") || joined.contains("gosuslugi") {
            return "antifake_verdict_next_steps_tax"
        }
        if verdict.verdict == .likelyFake {
            return "antifake_verdict_next_steps_fake"
        }
        return "antifake_verdict_next_steps_uncertain"
    }

    private var canShowReportActions: Bool {
        guard let jobId = verdict.jobId, !jobId.isEmpty else { return false }
        guard let phone = normalizedReportPhone, !phone.isEmpty else { return false }
        return true
    }

    private var normalizedReportPhone: String? {
        let raw = reportPhone?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return raw.isEmpty ? nil : raw
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Label(localizationManager.localized(verdictTitleKey), systemImage: iconName)
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                Text(localizationManager.localized(sourceBadgeKey))
                    .font(.caption2.weight(.semibold))
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, 4)
                    .background(Color.white.opacity(0.15))
                    .clipShape(Capsule())
            }

            VStack(alignment: .leading, spacing: Spacing.xs) {
                HStack {
                    Text(localizationManager.localized("antifake_verdict_confidence"))
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.75))
                    Spacer()
                    Text("\(Int((verdict.confidence * 100).rounded()))%")
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(accentColor)
                }
                ProgressView(value: min(max(verdict.confidence, 0), 1))
                    .tint(accentColor)
            }

            if !topReasons.isEmpty {
                Text(localizationManager.localized("antifake_verdict_reasons"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.7))

                ForEach(Array(topReasons.enumerated()), id: \.offset) { _, reason in
                    HStack(alignment: .top, spacing: Spacing.xs) {
                        Text("•")
                            .foregroundColor(accentColor)
                        Text(reason)
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.9))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }

            if !spoofHints.isEmpty {
                Text(localizationManager.localized("antifake_spoof_hint_title"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.warningOrange)
                ForEach(Array(spoofHints.enumerated()), id: \.offset) { _, hint in
                    Text("→ \(hint)")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.85))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            if verdict.verdict != .likelyReal {
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(localizationManager.localized("antifake_verdict_next_steps_title"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.primaryBlue.opacity(0.9))
                    Text(localizationManager.localized(nextStepsKey))
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.9))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            if canShowReportActions {
                reportActionsSection
            }

            if let reportFeedback {
                Text(reportFeedback)
                    .font(.subheadline)
                    .foregroundColor(.successGreen)
            }
            if let reportError {
                Text(reportError)
                    .font(.subheadline)
                    .foregroundColor(.dangerRed)
            }

            Text(localizationManager.localized("antifake_verdict_disclaimer"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.55))
        }
        .padding(Spacing.l)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: accentColor)
        .accessibilityIdentifier("antifake_verdict_card")
        .sheet(isPresented: $showReportSheet) {
            reportSheet(isAppeal: false)
        }
        .sheet(isPresented: $showAppealSheet) {
            reportSheet(isAppeal: true)
        }
    }

    @ViewBuilder
    private var reportActionsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("antifake_report_section_title"))
                .font(.caption.weight(.semibold))
                .foregroundColor(.white.opacity(0.75))

            if verdict.verdict != .likelyReal {
                Button {
                    reportNote = ""
                    reportLabel = ""
                    reportError = nil
                    showReportSheet = true
                } label: {
                    Label(
                        localizationManager.localized("antifake_report_scam_button"),
                        systemImage: "flag.fill"
                    )
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.plain)
                .foregroundColor(.dangerRed)
                .accessibilityIdentifier("antifake_report_scam_button")
            }

            if verdict.verdict == .likelyFake || verdict.verdict == .uncertain {
                Button {
                    reportNote = ""
                    reportError = nil
                    showAppealSheet = true
                } label: {
                    Label(
                        localizationManager.localized("antifake_appeal_button"),
                        systemImage: "hand.raised.fill"
                    )
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.plain)
                .foregroundColor(.primaryBlue)
                .accessibilityIdentifier("antifake_appeal_button")
            }

            if let phone = normalizedReportPhone {
                Button {
                    addToWhitelist(phone: phone)
                } label: {
                    Label(
                        localizationManager.localized("antifake_whitelist_add_button"),
                        systemImage: "person.crop.circle.badge.checkmark"
                    )
                    .font(.caption.weight(.semibold))
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.plain)
                .foregroundColor(.white.opacity(0.85))
                .accessibilityIdentifier("antifake_whitelist_add_button")
            }
        }
        .padding(.top, Spacing.xs)
    }

    @ViewBuilder
    private func reportSheet(isAppeal: Bool) -> some View {
        WellnessNavigationStack {
            Form {
                if let phone = normalizedReportPhone {
                    Section(localizationManager.localized("antifake_report_phone_section")) {
                        Text(phone)
                    }
                }
                if !isAppeal {
                    Section(localizationManager.localized("antifake_report_label_section")) {
                        TextField(
                            localizationManager.localized("antifake_report_label_placeholder"),
                            text: $reportLabel
                        )
                    }
                }
                Section(localizationManager.localized("antifake_report_note_section")) {
                    WellnessMultilineField(
                        title: localizationManager.localized("antifake_report_note_placeholder"),
                        text: $reportNote
                    )
                }
                if let reportError {
                    Section {
                        Text(reportError)
                            .foregroundColor(.dangerRed)
                    }
                }
            }
            .navigationTitle(
                localizationManager.localized(
                    isAppeal ? "antifake_appeal_sheet_title" : "antifake_report_sheet_title"
                )
            )
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button(localizationManager.localized("common_cancel")) {
                    if isAppeal { showAppealSheet = false } else { showReportSheet = false }
                },
                trailing: Button(localizationManager.localized("antifake_report_submit")) {
                    submitReport(isAppeal: isAppeal)
                }
                .disabled(isSubmittingReport || normalizedReportPhone == nil || verdict.jobId == nil)
            )
        }
        .modifier(AntifakeMediumSheetDetentModifier())
    }

    private func submitReport(isAppeal: Bool) {
        guard let jobId = verdict.jobId, let phone = normalizedReportPhone else { return }
        isSubmittingReport = true
        reportError = nil

        let completion: (Result<AntifakeReportSubmissionResponse, Error>) -> Void = { result in
            isSubmittingReport = false
            switch result {
            case .success(let response):
                reportFeedback = response.message
                    ?? localizationManager.localized("antifake_report_success")
                if isAppeal { showAppealSheet = false } else { showReportSheet = false }
                HapticFeedback.notification(.success)
            case .failure(let error):
                reportError = localizedReportError(error)
                HapticFeedback.notification(.error)
            }
        }

        if isAppeal {
            APIService.shared.antifakeAppealScam(
                jobId: jobId,
                phone: phone,
                note: reportNote.isEmpty ? nil : reportNote,
                completion: completion
            )
        } else {
            APIService.shared.antifakeReportScam(
                jobId: jobId,
                phone: phone,
                label: reportLabel.isEmpty ? nil : reportLabel,
                note: reportNote.isEmpty ? nil : reportNote,
                completion: completion
            )
        }
    }

    private func addToWhitelist(phone: String) {
        APIService.shared.antifakeAddWhitelist(phones: [phone]) { result in
            switch result {
            case .success:
                reportFeedback = localizationManager.localized("antifake_whitelist_added")
                HapticFeedback.notification(.success)
            case .failure(let error):
                reportError = localizedReportError(error)
                HapticFeedback.notification(.error)
            }
        }
    }

    private func localizedReportError(_ error: Error) -> String {
        if let networkError = error as? NetworkError {
            switch networkError {
            case .tooManyRequests:
                return localizationManager.localized("antifake_report_rate_limited")
            case .forbidden(let message):
                return message ?? localizationManager.localized("antifake_error_unauthorized")
            case .badRequest(let message):
                if let message, message.lowercased().contains("whitelist") {
                    return localizationManager.localized("antifake_report_whitelisted")
                }
                return localizationManager.localized("antifake_report_failed")
            default:
                break
            }
        }
        return localizationManager.localized("antifake_report_failed")
    }
}

private struct AntifakeMediumSheetDetentModifier: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 16.0, *) {
            content.presentationDetents([.medium])
        } else {
            content
        }
    }
}
