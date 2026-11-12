import SwiftUI
import UIKit

/// JOB13 / H20 — compose Life360-style invite OG: globe template + inviter photo in gold pin.
/// Template C = empty pin center; B = silhouette fallback. Export target 1200×630.
enum InviteOGComposer {
    /// Normalized pin hole on `ICON_ALIVE_HERO_H20_InviteOG_EmptyPin` @ 1200×630 (measured 2026-11-12).
    static let pinCenterX: CGFloat = 0.7871
    static let pinCenterY: CGFloat = 0.2016
    /// Radius as fraction of min(width, height).
    static let pinRadiusNorm: CGFloat = 0.143873

    static let ogSize = CGSize(width: 1200, height: 630)

    /// Composites inviter avatar into empty-pin template. Falls back to silhouette asset if no photo.
    static func renderOGImage(avatar: UIImage?) -> UIImage {
        let size = ogSize
        let format = UIGraphicsImageRendererFormat.default()
        format.scale = 1
        format.opaque = true
        let renderer = UIGraphicsImageRenderer(size: size, format: format)
        return renderer.image { ctx in
            let rect = CGRect(origin: .zero, size: size)
            let templateName = avatar == nil
                ? "ICON_ALIVE_HERO_H20_InviteOG_Silhouette"
                : "ICON_ALIVE_HERO_H20_InviteOG_EmptyPin"
            if let template = UIImage(named: templateName) {
                template.draw(in: rect)
            } else {
                UIColor(red: 0.06, green: 0.09, blue: 0.16, alpha: 1).setFill()
                ctx.fill(rect)
            }

            guard let avatar else { return }

            let minSide = min(size.width, size.height)
            let radius = pinRadiusNorm * minSide
            let center = CGPoint(x: pinCenterX * size.width, y: pinCenterY * size.height)
            let hole = CGRect(
                x: center.x - radius,
                y: center.y - radius,
                width: radius * 2,
                height: radius * 2
            )

            ctx.cgContext.saveGState()
            UIBezierPath(ovalIn: hole).addClip()
            let scale = max(hole.width / max(avatar.size.width, 1), hole.height / max(avatar.size.height, 1))
            let drawSize = CGSize(width: avatar.size.width * scale, height: avatar.size.height * scale)
            let drawOrigin = CGPoint(
                x: hole.midX - drawSize.width / 2,
                y: hole.midY - drawSize.height / 2
            )
            avatar.draw(in: CGRect(origin: drawOrigin, size: drawSize))
            ctx.cgContext.restoreGState()
        }
    }

    static func jpegData(avatar: UIImage?, quality: CGFloat = 0.9) -> Data? {
        renderOGImage(avatar: avatar).jpegData(compressionQuality: quality)
    }
}

/// In-app preview card (share sheet / invite modal).
struct InviteOGPreviewCard: View {
    var avatar: UIImage?
    var height: CGFloat = 168

    var body: some View {
        Image(uiImage: InviteOGComposer.renderOGImage(avatar: avatar))
            .resizable()
            .scaledToFit()
            .frame(maxWidth: .infinity)
            .frame(height: height)
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
            .accessibilityHidden(true)
            .accessibilityIdentifier("family_invite_og_preview")
    }
}
