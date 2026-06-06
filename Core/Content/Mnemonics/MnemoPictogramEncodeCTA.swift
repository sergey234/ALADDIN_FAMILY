import SwiftUI

/// ENCODE-phase CTA — co-create a pictogram (B11-T02). Drawing handoff wired in B11-T03.
struct MnemoPictogramEncodeCTA: View {
    @ObservedObject var localizationManager: LocalizationManager
    let itemId: String
    let onDrawTapped: () -> Void

    private var childId: String { MnemonicPictogramStore.activeChildId() }

    private var hasSaved: Bool {
        MnemonicPictogramStore.shared.hasPictogram(itemId: itemId, childId: childId)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Button(action: onDrawTapped) {
                HStack(spacing: 8) {
                    Image(systemName: "paintbrush.pointed.fill")
                        .font(.system(size: 14, weight: .semibold))
                    Text(localizationManager.localized("child_mnemo_pictogram_encode_cta"))
                        .font(.system(size: 14, weight: .semibold))
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 10)
            }
            .buttonStyle(.bordered)
            .tint(.purple)
            .accessibilityIdentifier("child_mnemo_pictogram_encode_cta")

            Text(
                localizationManager.localized(
                    hasSaved
                        ? "child_mnemo_pictogram_saved_badge"
                        : "child_mnemo_pictogram_encode_hint"
                )
            )
            .font(.system(size: 12, weight: .medium))
            .foregroundColor(hasSaved ? .green : .secondary)
            .accessibilityIdentifier(
                hasSaved
                    ? "child_mnemo_pictogram_saved_badge"
                    : "child_mnemo_pictogram_encode_hint"
            )
        }
        .padding(.top, 4)
    }
}
