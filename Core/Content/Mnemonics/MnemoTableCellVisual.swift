import SwiftUI
import UIKit

/// Mnemotable cell — emoji default, optional co-created pictogram from B11 store (B13-T03).
struct MnemoTableCellVisual: View {
    let cell: MnemonicTableEngine.Cell
    let parentItemId: String
    var emojiFontSize: CGFloat = 28
    var imageMaxHeight: CGFloat = 52
    var showEmojiBadgeWhenPictogram: Bool = true

    private var pictogramItemId: String {
        MnemonicTableEngine.shared.pictogramItemId(for: cell, parentItemId: parentItemId)
    }

    private var childId: String { MnemonicPictogramStore.activeChildId() }

    private var savedImage: UIImage? {
        guard MnemonicPictogramStore.supportsCoCreation(itemId: pictogramItemId) else { return nil }
        return MnemonicPictogramStore.shared.loadImage(itemId: pictogramItemId, childId: childId)
    }

    var body: some View {
        ZStack(alignment: .topTrailing) {
            if let savedImage {
                Image(uiImage: savedImage)
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: .infinity, maxHeight: imageMaxHeight)
                    .accessibilityIdentifier("child_mnemo_table_cell_pictogram_\(cell.slotIndex)")
            } else {
                Text(cell.emoji)
                    .font(.system(size: emojiFontSize, weight: .bold))
                    .accessibilityIdentifier("child_mnemo_table_cell_emoji_\(cell.slotIndex)")
            }

            if showEmojiBadgeWhenPictogram, savedImage != nil {
                Text(cell.emoji)
                    .font(.system(size: max(12, emojiFontSize * 0.35), weight: .bold))
                    .padding(3)
                    .background(Circle().fill(Color.white.opacity(0.92)))
                    .offset(x: 4, y: -4)
            }
        }
        .frame(maxWidth: .infinity)
    }
}
