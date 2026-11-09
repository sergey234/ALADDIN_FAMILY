import SwiftUI

/// Round2 S17/S29 — pan + pinch photo inside a circular (or Life360-style) mask so nothing clips badly.
struct AvatarCropEditor: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let image: UIImage
    var maskDiameter: CGFloat = 220
    var onCommit: (UIImage) -> Void
    var onCancel: () -> Void

    @State private var scale: CGFloat = 1.0
    @State private var lastScale: CGFloat = 1.0
    @State private var offset: CGSize = .zero
    @State private var lastOffset: CGSize = .zero

    var body: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("avatar_crop_title"))
                .font(.system(.title3, design: .serif).weight(.bold))
                .foregroundColor(.secondaryGold)
                .padding(.top, Spacing.m)

            Text(localizationManager.localized("avatar_crop_hint"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            ZStack {
                Color.black.opacity(0.35)
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
                    .scaleEffect(scale)
                    .offset(offset)
                    .frame(width: maskDiameter, height: maskDiameter)
                    .clipShape(Circle())
                    .overlay(Circle().stroke(Color.secondaryGold, lineWidth: 2))
                    .gesture(
                        DragGesture()
                            .onChanged { value in
                                offset = CGSize(
                                    width: lastOffset.width + value.translation.width,
                                    height: lastOffset.height + value.translation.height
                                )
                            }
                            .onEnded { _ in
                                lastOffset = offset
                                HapticFeedback.selection()
                            }
                    )
                    .simultaneousGesture(
                        MagnificationGesture()
                            .onChanged { value in
                                scale = min(3.0, max(1.0, lastScale * value))
                            }
                            .onEnded { _ in
                                lastScale = scale
                                HapticFeedback.selection()
                            }
                    )
            }
            .frame(height: maskDiameter + 40)

            HStack(spacing: Spacing.m) {
                Button(action: onCancel) {
                    Text(localizationManager.localized("common_cancel"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(Color.white.opacity(0.12))
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(.plain)

                Button {
                    onCommit(renderCropped())
                } label: {
                    Text(localizationManager.localized("avatar_crop_apply"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.backgroundDark)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, Spacing.l)
            .padding(.bottom, Spacing.l)
        }
        .background(StormMeshBackground(variant: .shield).ignoresSafeArea())
        .accessibilityIdentifier("avatar_crop_editor")
    }

    private func renderCropped() -> UIImage {
        let size = CGSize(width: maskDiameter * 2, height: maskDiameter * 2)
        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.image { _ in
            let ctx = UIGraphicsGetCurrentContext()
            ctx?.addEllipse(in: CGRect(origin: .zero, size: size))
            ctx?.clip()

            let imgSize = image.size
            let base = max(size.width / max(imgSize.width, 1), size.height / max(imgSize.height, 1))
            let drawScale = base * scale
            let drawW = imgSize.width * drawScale
            let drawH = imgSize.height * drawScale
            let x = (size.width - drawW) / 2 + offset.width * 2
            let y = (size.height - drawH) / 2 + offset.height * 2
            image.draw(in: CGRect(x: x, y: y, width: drawW, height: drawH))
        }
    }
}
