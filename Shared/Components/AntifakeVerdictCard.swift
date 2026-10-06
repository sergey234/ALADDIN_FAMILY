import SwiftUI

enum AntifakeVerdictCardVariant: Equatable {
    case standard
    case urlDisinformation
    case media
    case document
}

/// Result card for sync antifake checks (J-01…J-05, F-10, I-01…I-08).
struct AntifakeVerdictCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let verdict: SecurityVerdict
    var variant: AntifakeVerdictCardVariant = .standard
    /// Phone from call check metadata — required for crowd reports (I-01).
    var reportPhone: String? = nil

    @State private var showReportSheet = false
    @State private var showAppealSheet = false
    @State private var reportNote = ""
    @State private var reportLabel = ""
    @State private var isSubmittingReport = false
    @State private var reportFeedback: String?
    @State private var reportError: String?
    @State private var showSafeWordVerify = false
    @State private var showFamilyShareSheet = false
    @State private var familyShareText = ""
    @State private var isSharingWithFamily = false
    @State private var showWasScamSheet = false
    @State private var wasScamNote = ""
    @State private var isSubmittingWasScam = false
    @StateObject private var speechOutput = CompanionSpeechOutput()

    private var presentation: AntifakeVerdictPresentation {
        verdict.presentation
    }

    private var topReasons: [String] {
        if !verdict.reasonsHuman.isEmpty {
            return Array(verdict.reasonsHuman.prefix(3))
        }
        return Array(verdict.reasons.prefix(3))
    }

    private var usesServerHumanReasons: Bool {
        !verdict.reasonsHuman.isEmpty
    }

    private var reasonsSectionTitleKey: String {
        variant == .urlDisinformation ? "antifake_url_why_title" : "antifake_verdict_reasons"
    }

    private var urlTrustCopyKey: String? {
        guard variant == .urlDisinformation else { return nil }
        switch verdict.verdict {
        case .likelyFake: return "antifake_url_trust_copy_fake"
        case .uncertain: return "antifake_url_trust_copy_uncertain"
        case .likelyReal: return "antifake_url_trust_copy_real"
        case .insufficientData: return nil
        }
    }

    private var spoofHints: [String] {
        var hints: [String] = []
        let tags = Set(verdict.reasons.map { $0.lowercased() })
        if tags.contains("display_number_mismatch") {
            hints.append(localizationManager.localized("antifake_spoof_hint_display_mismatch"))
        }
        if tags.contains(where: { $0.contains("authority_label_short_code") || $0.contains("short_code") }) {
            hints.append(localizationManager.localized("antifake_spoof_hint_short_code"))
        }
        if tags.contains(where: {
            $0.contains("authority_label_personal_number")
                || $0.contains("authority_name_non_service")
                || $0.contains("personal_number")
        }) {
            hints.append(localizationManager.localized("antifake_spoof_hint_authority"))
        } else if tags.contains(where: { $0.contains("authority") || $0.contains("spoof") }) {
            hints.append(localizationManager.localized("antifake_spoof_hint_authority"))
        }
        if tags.contains(where: { $0.contains("scam_directory") || $0.contains("ktozvonil") }) {
            hints.append(localizationManager.localized("antifake_spoof_hint_directory"))
        }
        // Deduplicate while preserving order
        var seen = Set<String>()
        return hints.filter { seen.insert($0).inserted }
    }

    private var nextStepsKey: String {
        let joined = (verdict.reasons + verdict.reasonsHuman).joined(separator: " ").lowercased()
        if joined.contains("urgency") || joined.contains("срочн")
            || joined.contains("перевед") || joined.contains("send money") || joined.contains("scam")
            || joined.contains("financial") || joined.contains("счёт") || joined.contains("bank")
            || joined.contains("на карту") || joined.contains("card") {
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
        if verdict.verdict == .uncertain {
            return "antifake_verdict_next_steps_uncertain"
        }
        return "antifake_verdict_next_steps_uncertain"
    }

    /// Short plain-language story under the title (wave 2026-10-01).
    private var storySummaryKey: String {
        switch verdict.verdict {
        case .likelyFake:
            return "antifake_verdict_story_fake"
        case .uncertain, .insufficientData:
            return "antifake_verdict_story_uncertain"
        case .likelyReal:
            return "antifake_verdict_story_real"
        }
    }

    /// Show action tips for fake / uncertain (afhub-p0-05) — not for green authentic.
    private var showsNextSteps: Bool {
        switch verdict.verdict {
        case .likelyFake, .uncertain:
            return true
        case .likelyReal, .insufficientData:
            return false
        }
    }

    private var canShowReportActions: Bool {
        guard let jobId = verdict.jobId, !jobId.isEmpty else { return false }
        guard let phone = normalizedReportPhone, !phone.isEmpty else { return false }
        return true
    }

    private var canSubmitVerdictFeedback: Bool {
        guard let jobId = verdict.jobId, !jobId.isEmpty else { return false }
        return true
    }

    /// afhub-p3-01 — false-negative path: green/uncertain missed a scam.
    private var showsWasScamFeedback: Bool {
        guard canSubmitVerdictFeedback else { return false }
        switch verdict.verdict {
        case .likelyReal, .uncertain, .insufficientData:
            return true
        case .likelyFake:
            return false
        }
    }

    private var showsSafeWordVerify: Bool {
        nextStepsKey == "antifake_verdict_next_steps_family"
            || verdict.reasons.joined(separator: " ").lowercased().contains("родствен")
            || verdict.reasons.joined(separator: " ").lowercased().contains("family")
    }

    private var normalizedReportPhone: String? {
        let raw = reportPhone?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return raw.isEmpty ? nil : raw
    }

    /// fsl-08 — после проверки звонка (есть номер в карточке).
    private var showsCallPlainPhrases: Bool {
        normalizedReportPhone != nil
    }

    private var callPlainLines: [String] {
        let line1Key: String
        switch verdict.verdict {
        case .likelyFake:
            line1Key = "call_plain_line_fake"
        case .likelyReal:
            line1Key = "call_plain_line_real"
        case .uncertain, .insufficientData:
            line1Key = "call_plain_line_uncertain"
        }
        return [
            localizationManager.localized(line1Key),
            localizationManager.localized("call_plain_line_money"),
            localizationManager.localized("call_plain_line_family"),
        ]
    }

    private var speakableVerdictText: String {
        var parts: [String] = [
            localizationManager.localized(presentation.verdictTitleKey),
            localizationManager.localized(storySummaryKey),
        ]
        if let summary = verdict.summaryHuman, !summary.isEmpty {
            parts.append(summary)
        }
        for reason in topReasons.prefix(3) {
            let line = usesServerHumanReasons
                ? reason
                : presentation.localizedReason(reason, localizationManager: localizationManager)
            parts.append(line)
        }
        if showsCallPlainPhrases {
            parts.append(contentsOf: callPlainLines)
        }
        return parts
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
            .joined(separator: ". ")
    }

    private func toggleSpeakVerdict() {
        if speechOutput.isSpeaking {
            speechOutput.stop()
            return
        }
        speechOutput.speak(speakableVerdictText, personalityPreset: "calm", characterId: "aladdin")
        HapticFeedback.selection()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Label(
                    localizationManager.localized(presentation.verdictTitleKey),
                    systemImage: presentation.iconName
                )
                    .font(.title3.weight(.bold))
                    .foregroundColor(.white)
                    .fixedSize(horizontal: false, vertical: true)
                Spacer(minLength: Spacing.s)
                Text(localizationManager.localized(presentation.sourceBadgeKey))
                    .font(.caption.weight(.semibold))
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, 4)
                    .background(Color.white.opacity(0.15))
                    .clipShape(Capsule())
            }

            Text(localizationManager.localized("antifake_verdict_story_lead"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.8))
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityIdentifier("antifake_verdict_story_lead")

            Text(localizationManager.localized(storySummaryKey))
                .font(.body.weight(.semibold))
                .foregroundColor(.white.opacity(0.95))
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityIdentifier("antifake_verdict_story_summary")

            if presentation.showsRiskMeter {
                if variant == .media {
                    HStack(spacing: Spacing.m) {
                        AntifakeConfidenceRingView(
                            percent: presentation.riskPercent,
                            accentColor: presentation.accentColor
                        )
                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            Text(localizationManager.localized("antifake_confidence_ring_label"))
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.75))
                            Text(
                                localizationManager.localized(
                                    "antifake_verdict_fake_risk_value",
                                    presentation.riskPercent,
                                    localizationManager.localized(presentation.riskLevelKey)
                                )
                            )
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(presentation.accentColor)
                        }
                        Spacer(minLength: 0)
                    }
                } else {
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        HStack(alignment: .firstTextBaseline) {
                            Text(localizationManager.localized("antifake_verdict_fake_risk"))
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.75))
                            Spacer()
                            Text(
                                localizationManager.localized(
                                    "antifake_verdict_fake_risk_value",
                                    presentation.riskPercent,
                                    localizationManager.localized(presentation.riskLevelKey)
                                )
                            )
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(presentation.accentColor)
                        }
                        ProgressView(value: presentation.fakeRisk)
                            .tint(presentation.accentColor)
                    }
                }
            } else {
                Text(localizationManager.localized("antifake_verdict_insufficient_hint"))
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.85))
                    .fixedSize(horizontal: false, vertical: true)
            }

            if let summary = verdict.summaryHuman, !summary.isEmpty {
                Text(summary)
                    .font(.body)
                    .foregroundColor(.white.opacity(0.95))
                    .fixedSize(horizontal: false, vertical: true)
                    .accessibilityIdentifier("antifake_verdict_summary_human")
            }

            // fsl-06 — прослушать вердикт голосом героя
            Button {
                toggleSpeakVerdict()
            } label: {
                HStack(spacing: Spacing.s) {
                    Image(systemName: speechOutput.isSpeaking ? "stop.fill" : "speaker.wave.2.fill")
                    Text(
                        localizationManager.localized(
                            speechOutput.isSpeaking ? "verdict_speak_stop" : "verdict_speak_listen"
                        )
                    )
                    .font(.subheadline.weight(.semibold))
                }
                .foregroundColor(.secondaryGold)
                .padding(.vertical, Spacing.s)
                .padding(.horizontal, Spacing.m)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.08))
                .cornerRadius(CornerRadius.medium)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("antifake_verdict_speak_button")
            .accessibilityLabel(localizationManager.localized("verdict_speak_listen"))

            // fsl-08 — 2–3 простые фразы после проверки звонка (для 60+)
            if showsCallPlainPhrases {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(localizationManager.localized("call_plain_title"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.white.opacity(0.9))
                    ForEach(callPlainLines, id: \.self) { line in
                        Text("• \(line)")
                            .font(.body)
                            .foregroundColor(.white.opacity(0.95))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .padding(Spacing.m)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.06))
                .cornerRadius(CornerRadius.medium)
                .accessibilityIdentifier("antifake_call_plain_block")
            }

            if !topReasons.isEmpty {
                Text(localizationManager.localized(reasonsSectionTitleKey))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white.opacity(0.85))

                ForEach(Array(topReasons.enumerated()), id: \.offset) { _, reason in
                    HStack(alignment: .top, spacing: Spacing.xs) {
                        Text("•")
                            .foregroundColor(presentation.accentColor)
                        Text(
                            usesServerHumanReasons
                                ? reason
                                : presentation.localizedReason(reason, localizationManager: localizationManager)
                        )
                            .font(.body)
                            .foregroundColor(.white.opacity(0.95))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }

            if let urlTrustCopyKey {
                Text(localizationManager.localized(urlTrustCopyKey))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.75))
                    .fixedSize(horizontal: false, vertical: true)
            }

            if !verdict.sources.isEmpty {
                Text(localizationManager.localized("antifake_url_sources_title"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.primaryBlue.opacity(0.9))
                ForEach(verdict.sources) { item in
                    if let link = item.url, let url = URL(string: link) {
                        Link(destination: url) {
                            HStack(spacing: Spacing.xs) {
                                Image(systemName: "link")
                                    .font(.caption)
                                Text(localizedSourceTitle(item))
                                    .font(.caption)
                                    .multilineTextAlignment(.leading)
                            }
                        }
                        .foregroundColor(.secondaryGold)
                    }
                }
            } else if variant == .urlDisinformation {
                Text(localizationManager.localized("antifake_url_sources_title"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.primaryBlue.opacity(0.9))
                Text(localizationManager.localized("antifake_url_sources_empty"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
                    .fixedSize(horizontal: false, vertical: true)
                    .accessibilityIdentifier("antifake_url_sources_empty")
            }

            if variant == .document, let provenance = verdict.provenance {
                provenanceSection(provenance)
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

            if showsNextSteps {
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(localizationManager.localized("antifake_verdict_next_steps_title"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.primaryBlue.opacity(0.9))
                    Text(localizationManager.localized(nextStepsKey))
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.9))
                        .fixedSize(horizontal: false, vertical: true)

                    if showsSafeWordVerify {
                        Button {
                            HapticFeedback.impact(.light)
                            showSafeWordVerify = true
                        } label: {
                            Label(
                                localizationManager.localized("antifake_safe_word_verify_button"),
                                systemImage: "key.horizontal.fill"
                            )
                            .font(.subheadline.weight(.semibold))
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .buttonStyle(.plain)
                        .foregroundColor(.secondaryGold)
                        .accessibilityIdentifier("antifake_safe_word_verify_button")
                    }
                }
            }

            // afhub-p2-04 — one-tap share with family (Share sheet + optional family notify)
            Button {
                HapticFeedback.impact(.light)
                shareWithFamilyTapped()
            } label: {
                Label(
                    localizationManager.localized("antifake_share_family_button"),
                    systemImage: "person.3.fill"
                )
                .font(.subheadline.weight(.semibold))
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .buttonStyle(.plain)
            .foregroundColor(.secondaryGold)
            .disabled(isSharingWithFamily)
            .accessibilityIdentifier("antifake_share_family_button")

            if canShowReportActions {
                reportActionsSection
            }
            if canSubmitVerdictFeedback && !canShowReportActions {
                verdictFeedbackSection
            }
            if showsWasScamFeedback && !canShowReportActions {
                wasScamFeedbackSection
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
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: presentation.accentColor)
        .accessibilityIdentifier("antifake_verdict_card")
        .sheet(isPresented: $showReportSheet) {
            reportSheet(isAppeal: false)
        }
        .sheet(isPresented: $showAppealSheet) {
            reportSheet(isAppeal: true)
        }
        .sheet(isPresented: $showSafeWordVerify) {
            FamilySafeWordVerifySheet(context: "antifake")
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showFamilyShareSheet) {
            ShareSheet(activityItems: [familyShareText])
        }
        .sheet(isPresented: $showWasScamSheet) {
            wasScamSheet
        }
    }

    @ViewBuilder
    private var wasScamSheet: some View {
        WellnessNavigationStack {
            Form {
                Section(localizationManager.localized("antifake_feedback_was_scam_note_section")) {
                    WellnessMultilineField(
                        title: localizationManager.localized("antifake_feedback_was_scam_note_placeholder"),
                        text: $wasScamNote
                    )
                }
                Text(localizationManager.localized("antifake_feedback_was_scam_hint"))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .navigationTitle(localizationManager.localized("antifake_feedback_was_scam_button"))
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("common_cancel")) {
                        showWasScamSheet = false
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button(localizationManager.localized("antifake_feedback_was_scam_submit")) {
                        submitWasScamFeedback()
                    }
                    .disabled(isSubmittingWasScam)
                }
            }
        }
    }

    private func shareWithFamilyTapped() {
        familyShareText = AntifakeFamilyShareText.build(
            verdict: verdict,
            localizationManager: localizationManager
        )
        showFamilyShareSheet = true
        isSharingWithFamily = true
        let lang = localizationManager.currentLanguage == .english ? "en" : "ru"
        APIService.shared.antifakeShareVerdictWithFamily(
            verdict: verdict.verdict.rawValue,
            confidence: verdict.confidence,
            jobId: verdict.jobId,
            summary: verdict.summaryHuman,
            lang: lang
        ) { result in
            DispatchQueue.main.async {
                isSharingWithFamily = false
                switch result {
                case .success:
                    reportFeedback = localizationManager.localized("antifake_share_family_done")
                case .failure(let error):
                    if let networkError = error as? NetworkError, case .notFound = networkError {
                        reportError = localizationManager.localized("antifake_share_family_no_family")
                    }
                }
            }
        }
    }

    private func localizedSourceTitle(_ item: AntifakeVerdictSource) -> String {
        if let key = item.titleKey, !key.isEmpty {
            let localized = localizationManager.localized(key)
            if localized != key { return localized }
        }
        if let title = item.title, !title.isEmpty { return title }
        return item.url ?? ""
    }

    @ViewBuilder
    private func provenanceSection(_ provenance: AntifakeVerdictProvenance) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xxs) {
            Text(localizationManager.localized("antifake_provenance_title"))
                .font(.caption.weight(.semibold))
                .foregroundColor(.primaryBlue.opacity(0.9))

            HStack(spacing: Spacing.xs) {
                Image(systemName: provenanceIcon(provenance.status))
                    .foregroundColor(provenanceColor(provenance.status))
                Text(localizationManager.localized(provenanceStatusKey(provenance.status)))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white.opacity(0.9))
            }

            if let issuer = provenance.issuer, !issuer.isEmpty {
                Text(
                    localizationManager.localized(
                        "antifake_provenance_issuer",
                        issuer
                    )
                )
                .font(.caption)
                .foregroundColor(.white.opacity(0.75))
            }
        }
        .accessibilityIdentifier("antifake_provenance_block")
    }

    private func provenanceStatusKey(_ status: AntifakeProvenanceStatus) -> String {
        switch status {
        case .found: return "antifake_provenance_found"
        case .missing: return "antifake_provenance_missing"
        case .tampered: return "antifake_provenance_tampered"
        }
    }

    private func provenanceIcon(_ status: AntifakeProvenanceStatus) -> String {
        switch status {
        case .found: return "checkmark.seal.fill"
        case .missing: return "questionmark.circle.fill"
        case .tampered: return "exclamationmark.triangle.fill"
        }
    }

    private func provenanceColor(_ status: AntifakeProvenanceStatus) -> Color {
        switch status {
        case .found: return .successGreen
        case .missing: return .warningOrange
        case .tampered: return .dangerRed
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

            if canSubmitVerdictFeedback {
                verdictFeedbackSection
            }
            if showsWasScamFeedback {
                wasScamFeedbackSection
            }
        }
        .padding(.top, Spacing.xs)
    }

    @ViewBuilder
    private var verdictFeedbackSection: some View {
        Button {
            submitVerdictFeedback()
        } label: {
            Label(
                localizationManager.localized("antifake_feedback_button"),
                systemImage: "hand.thumbsdown"
            )
            .font(.caption.weight(.semibold))
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .buttonStyle(.plain)
        .foregroundColor(.white.opacity(0.75))
        .accessibilityIdentifier("antifake_feedback_button")
    }

    @ViewBuilder
    private var wasScamFeedbackSection: some View {
        Button {
            wasScamNote = ""
            showWasScamSheet = true
        } label: {
            Label(
                localizationManager.localized("antifake_feedback_was_scam_button"),
                systemImage: "exclamationmark.bubble.fill"
            )
            .font(.caption.weight(.semibold))
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .buttonStyle(.plain)
        .foregroundColor(.warningOrange)
        .disabled(isSubmittingWasScam)
        .accessibilityIdentifier("antifake_feedback_was_scam_button")
    }

    private func submitVerdictFeedback() {
        guard let jobId = verdict.jobId else { return }
        APIService.shared.antifakeVerdictFeedback(jobId: jobId, note: nil, feedback: "incorrect") { result in
            switch result {
            case .success:
                AITrustAnalytics.trackAntifakeFalsePositive(jobId: jobId)
                reportFeedback = localizationManager.localized("antifake_feedback_success")
                HapticFeedback.notification(.success)
            case .failure(let error):
                reportError = localizedReportError(error)
                HapticFeedback.notification(.error)
            }
        }
    }

    private func submitWasScamFeedback() {
        guard let jobId = verdict.jobId else { return }
        let note = wasScamNote.trimmingCharacters(in: .whitespacesAndNewlines)
        guard note.count >= 4 else {
            reportError = localizationManager.localized("antifake_feedback_was_scam_note_required")
            return
        }
        isSubmittingWasScam = true
        APIService.shared.antifakeVerdictFeedback(jobId: jobId, note: note, feedback: "was_scam") { result in
            DispatchQueue.main.async {
                isSubmittingWasScam = false
                showWasScamSheet = false
                switch result {
                case .success(let payload):
                    if payload.lexiconReview?.queued == true {
                        reportFeedback = localizationManager.localized("antifake_feedback_was_scam_queued")
                    } else {
                        reportFeedback = localizationManager.localized("antifake_feedback_was_scam_success")
                    }
                    HapticFeedback.notification(.success)
                case .failure(let error):
                    reportError = localizedReportError(error)
                    HapticFeedback.notification(.error)
                }
            }
        }
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
                AITrustAnalytics.trackAntifakeComplaint(isAppeal: isAppeal, jobId: jobId)
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
