import SwiftUI

struct VoiceNoteCard: View {
    let note: VoiceNotesViewModel.VoiceNoteItem
    /// Повторная генерация summary (вынесена из swipe у `List`, чтобы сохранить один общий скролл).
    var onRegenerateSummary: (() -> Void)?
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(note.title)
                .font(.headline)
            Text(transcriptText)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .lineLimit(2)
                .multilineTextAlignment(.leading)

            if !note.summary.isEmpty {
                Text(note.summary)
                    .font(.subheadline)
            }

            HStack {
                Text("AI \(localizationManager.localized("voice_notes_summary_confidence")): \(Int(note.summaryConfidence * 100))%")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text("v\(max(note.summaryVersion, 1))")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                Spacer()
                Text("\(note.durationSec)s")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            if let onRegenerateSummary {
                Button(action: onRegenerateSummary) {
                    Label(localizationManager.localized("voice_notes_summary_retry"), systemImage: "arrow.clockwise")
                        .font(.caption.weight(.semibold))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .controlSize(.small)
                .tint(.orange)
            }

            if !note.tags.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 6) {
                        ForEach(note.tags, id: \.self) { tag in
                            Text("#\(tag)")
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.orange.opacity(0.15))
                                .clipShape(Capsule())
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

private extension VoiceNoteCard {
    var transcriptText: String {
        if note.transcriptPreview.hasPrefix("voice_notes_") || note.transcriptPreview.hasPrefix("ai_assistant_") {
            return localizationManager.localized(note.transcriptPreview)
        }
        return note.transcriptPreview
    }
}
