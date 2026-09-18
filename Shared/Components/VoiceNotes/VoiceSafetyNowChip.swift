import SwiftUI

/// VSL-C P1 — home chip «Сейчас: …» (tap → Voice Notes).
struct VoiceSafetyNowChip: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    var onTap: () -> Void

    @State private var snapshot: VoiceSafetyNowStore.Snapshot?

    var body: some View {
        Group {
            if let snap = snapshot {
                Button(action: onTap) {
                    HStack(spacing: 8) {
                        Image(systemName: "mic.circle.fill")
                            .foregroundColor(Color(hex: "F5C542"))
                        VStack(alignment: .leading, spacing: 2) {
                            Text(localizationManager.localized("voice_safety_now_caption"))
                                .font(.caption2.weight(.semibold))
                                .foregroundColor(.white.opacity(0.7))
                            Text(line(for: snap))
                                .font(.subheadline.weight(.medium))
                                .foregroundColor(.white)
                                .lineLimit(2)
                        }
                        Spacer(minLength: 0)
                        Image(systemName: "chevron.right")
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.white.opacity(0.5))
                    }
                    .padding(12)
                    .background(Color.white.opacity(0.10))
                    .cornerRadius(12)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("voice_safety_now_chip")
            }
        }
        .onAppear { snapshot = VoiceSafetyNowStore.load() }
        .onReceive(NotificationCenter.default.publisher(for: .voiceSafetyNowDidChange)) { _ in
            snapshot = VoiceSafetyNowStore.load()
        }
    }

    private func line(for snap: VoiceSafetyNowStore.Snapshot) -> String {
        let title = localizationManager.localized(snap.localizationKey)
        let detail = snap.detail.trimmingCharacters(in: .whitespacesAndNewlines)
        if detail.isEmpty { return title }
        return "\(title): \(detail)"
    }
}
