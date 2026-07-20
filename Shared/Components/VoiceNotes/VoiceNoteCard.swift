import SwiftUI

struct VoiceNoteCard: View {
    let note: VoiceNotesViewModel.VoiceNoteItem
    @ObservedObject var playback: VoiceNotePlaybackController
    var onRegenerateSummary: (() -> Void)?
    var onSendToAI: ((String) -> Void)?
    var onStructure: ((String) -> Void)?
    var isStructuring: Bool = false
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var waveformSamples: [CGFloat]?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(note.title)
                .font(.headline)

            if !note.audioPath.isEmpty, FileManager.default.fileExists(atPath: note.audioPath) {
                HStack(spacing: 10) {
                    VoiceNoteWaveformView(
                        durationSec: note.durationSec,
                        seed: note.id.hashValue,
                        samples: waveformSamples
                    )
                    Button {
                        playback.toggle(noteId: note.id, filePath: note.audioPath)
                    } label: {
                        Image(systemName: playback.playingNoteId == note.id ? "pause.circle.fill" : "play.circle.fill")
                            .font(.title2)
                            .foregroundColor(.orange)
                    }
                    if playback.playingNoteId == note.id {
                        ProgressView(value: min(max(playback.progress, 0), 1))
                            .frame(maxWidth: .infinity)
                    }
                }
            }

            Text(transcriptText)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .lineLimit(3)
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

            HStack(spacing: 8) {
                if let onRegenerateSummary {
                    Button(action: onRegenerateSummary) {
                        Label(localizationManager.localized("voice_notes_summary_retry"), systemImage: "arrow.clockwise")
                            .font(.caption.weight(.semibold))
                    }
                    .buttonStyle(.bordered)
                    .controlSize(.small)
                }

                if !note.audioPath.isEmpty, FileManager.default.fileExists(atPath: note.audioPath) {
                    Button {
                        shareAudioFile(path: note.audioPath)
                    } label: {
                        Label(localizationManager.localized("voice_notes_share"), systemImage: "square.and.arrow.up")
                            .font(.caption.weight(.semibold))
                    }
                    .buttonStyle(.bordered)
                    .controlSize(.small)
                }

                if let onSendToAI {
                    Button {
                        onSendToAI(exportText)
                    } label: {
                        Label(localizationManager.localized("voice_notes_send_to_ai"), systemImage: "brain.head.profile")
                            .font(.caption.weight(.semibold))
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.small)
                    .tint(.blue)
                }

                if let onStructure, !exportText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    Button {
                        onStructure(exportText)
                    } label: {
                        Label(
                            localizationManager.localized("voice_structure_button"),
                            systemImage: isStructuring ? "hourglass" : "list.bullet.rectangle"
                        )
                        .font(.caption.weight(.semibold))
                    }
                    .buttonStyle(.bordered)
                    .controlSize(.small)
                    .disabled(isStructuring)
                    .accessibilityIdentifier("voice_structure_button")
                }
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
        .task(id: note.audioPath) {
            guard !note.audioPath.isEmpty else { return }
            let path = note.audioPath
            let samples = await Task.detached(priority: .utility) {
                VoiceNoteWaveformSampler.samples(forFilePath: path)
            }.value
            waveformSamples = samples
        }
    }

    private var exportText: String {
        let raw = note.transcriptPreview
        if !raw.hasPrefix("voice_notes_"), !raw.hasPrefix("ai_assistant_"), !raw.isEmpty {
            return raw
        }
        if !note.summary.isEmpty { return note.summary }
        return note.title
    }
}

private extension VoiceNoteCard {
    func shareAudioFile(path: String) {
        DispatchQueue.main.async {
            let url = URL(fileURLWithPath: path)
            let controller = UIActivityViewController(activityItems: [url], applicationActivities: nil)
            if let popover = controller.popoverPresentationController {
                popover.sourceView = UIApplication.shared.windows.first { $0.isKeyWindow }
                popover.sourceRect = CGRect(x: UIScreen.main.bounds.midX, y: UIScreen.main.bounds.midY, width: 1, height: 1)
            }
            guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
                  let root = scene.windows.first(where: { $0.isKeyWindow })?.rootViewController else { return }
            var presenter = root
            while let presented = presenter.presentedViewController {
                presenter = presented
            }
            presenter.present(controller, animated: true)
        }
    }

    var transcriptText: String {
        if note.transcriptPreview.hasPrefix("voice_notes_") || note.transcriptPreview.hasPrefix("ai_assistant_") {
            return localizationManager.localized(note.transcriptPreview)
        }
        return note.transcriptPreview
    }
}
