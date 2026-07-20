import SwiftUI

/// P1.5 — day recap sheet: 5 bullets + tell family CTAs.
struct VoiceDayRecapSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @Environment(\.dismiss) private var dismiss

    let result: VoiceDayRecapResult

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .warm).ignoresSafeArea()
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(alignment: .leading, spacing: 14) {
                        Text(localizationManager.localized("voice_day_recap_bullets"))
                            .font(.subheadline.weight(.semibold))
                        if result.bullets.isEmpty {
                            Text("—")
                                .foregroundColor(.white.opacity(0.5))
                        } else {
                            ForEach(Array(result.bullets.enumerated()), id: \.offset) { _, bullet in
                                Text("• \(bullet)")
                                    .font(.subheadline)
                            }
                        }

                        if !result.tellFamily.isEmpty {
                            VStack(alignment: .leading, spacing: 6) {
                                Text(localizationManager.localized("voice_day_recap_tell_family"))
                                    .font(.subheadline.weight(.semibold))
                                Text(result.tellFamily)
                                    .font(.body)
                            }
                            .padding(10)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.white.opacity(0.08))
                            .cornerRadius(10)
                        }

                        if let raw = result.rawFallback, !raw.isEmpty {
                            Text(localizationManager.localized("voice_day_recap_raw_fallback"))
                                .font(.caption.weight(.semibold))
                            Text(raw)
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.8))
                        }

                        Button {
                            let draft = ([result.tellFamily] + result.bullets)
                                .filter { !$0.isEmpty }
                                .joined(separator: "\n")
                            UserDefaults.standard.set(draft, forKey: VoiceDayRecapService.familyChatDraftKey)
                            dismiss()
                            navigationManager.navigateTo(.familyChat)
                        } label: {
                            Label(
                                localizationManager.localized("voice_day_recap_cta_family"),
                                systemImage: "bubble.left.and.bubble.right"
                            )
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(Color(hex: "8B5CF6"))
                    }
                    .padding()
                }
            }
            .foregroundColor(.white)
            .navigationTitle(localizationManager.localized("voice_day_recap_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_guide_cancel")) { dismiss() }
                }
            }
        }
        .accessibilityIdentifier("voice_day_recap_sheet")
    }
}
