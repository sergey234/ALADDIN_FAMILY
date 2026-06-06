import SwiftUI
import UIKit

/// RECALL hint level 1 — show the child's saved co-created pictogram (B11-T04).
struct MnemoPictogramRecallHint: View {
    @ObservedObject var localizationManager: LocalizationManager
    let itemId: String

    private var childId: String { MnemonicPictogramStore.activeChildId() }

    private var savedImage: UIImage? {
        guard MnemonicPictogramStore.supportsCoCreation(itemId: itemId) else { return nil }
        return MnemonicPictogramStore.shared.loadImage(itemId: itemId, childId: childId)
    }

    var body: some View {
        if let savedImage {
            VStack(alignment: .leading, spacing: 8) {
                Text(localizationManager.localized("child_mnemo_pictogram_recall_hint"))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.purple)

                Image(uiImage: savedImage)
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: .infinity, maxHeight: 160)
                    .padding(8)
                    .background(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(Color.white)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .stroke(Color.purple.opacity(0.35), lineWidth: 1)
                    )
                    .accessibilityLabel(localizationManager.localized("child_mnemo_pictogram_recall_hint"))
            }
            .accessibilityIdentifier("child_mnemo_pictogram_recall_hint")
        }
    }
}
