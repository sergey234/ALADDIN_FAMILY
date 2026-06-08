import SwiftUI

/// p2-19 — mood journal + exercises timeline.
struct WellnessTimelineScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var timeline: WellnessTimelineResponse?
    @State private var errorText: String?
    @State private var showPaywall = false
    @State private var sharePDFURL: URL?

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .neutral)

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header
                    if timeline != nil {
                        Button {
                            Task { await exportPDF() }
                        } label: {
                            Label(
                                localizationManager.localized("wellness_pdf_share"),
                                systemImage: "square.and.arrow.up"
                            )
                        }
                        .buttonStyle(.bordered)
                        .tint(.white)
                    }
                    if let timeline {
                        if timeline.checkins.isEmpty && timeline.exercises.isEmpty {
                            Text(localizationManager.localized("wellness_timeline_empty"))
                                .foregroundColor(.white.opacity(0.85))
                        }
                        if !timeline.checkins.isEmpty {
                            Text(localizationManager.localized("wellness_timeline_mood_chart"))
                                .font(.headline)
                            ForEach(timeline.checkins) { row in
                                HStack {
                                    Text(row.day)
                                    Spacer()
                                    Text(row.moodEmoji ?? "—")
                                    if let stress = row.stressLevel {
                                        Text("· \(stress)/5").font(.caption)
                                    }
                                }
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .stormGlassCard(cornerRadius: 10)
                            }
                        }
                        if !timeline.exercises.isEmpty {
                            Text(localizationManager.localized("wellness_timeline_exercises"))
                                .font(.headline)
                                .padding(.top, 8)
                            ForEach(timeline.exercises) { ex in
                                HStack {
                                    Text(ex.exerciseType)
                                    Spacer()
                                    Text(ex.pillar)
                                        .font(.caption)
                                        .foregroundColor(.white.opacity(0.75))
                                }
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .stormGlassCard(cornerRadius: 10)
                            }
                        }
                    } else if let errorText {
                        Text(errorText).foregroundStyle(.orange)
                    } else {
                        ProgressView().tint(.white)
                    }
                }
                .padding()
            }
        }
        .foregroundColor(.white)
        .navigationBarHidden(true)
        .task { await load() }
        .sheet(isPresented: $showPaywall) {
            WellnessPremiumPaywallSheet()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: Binding(
            get: { sharePDFURL != nil },
            set: { if !$0 { sharePDFURL = nil } }
        )) {
            if let url = sharePDFURL {
                ShareSheet(activityItems: [url])
            }
        }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.goBack() } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            Text(localizationManager.localized("wellness_timeline_title"))
                .font(.headline.bold())
            Spacer()
        }
    }

    private func load() async {
        do {
            timeline = try await WellnessAPIService.shared.fetchTimeline(days: 14)
        } catch {
            if let gate = try? await WellnessAPIService.shared.fetchPremiumEligibility(),
               gate.isPremiumAllowed == false {
                showPaywall = true
                errorText = localizationManager.localized(
                    gate.messageKey ?? "wellness_error_premium_subscription"
                )
            } else {
                errorText = localizationManager.localized("wellness_error_offline_pillars")
            }
        }
    }

    private func exportPDF() async {
        guard let timeline else { return }
        let labels = (try? await WellnessAPIService.shared.fetchPdfLabels()) ?? [:]
        sharePDFURL = WellnessProgressPDFService.generateWeeklyPDF(
            timeline: timeline,
            labels: labels,
            locale: localizationManager
        )
    }
}
