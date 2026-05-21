import SwiftUI

struct QuickRecorderBar: View {
    @ObservedObject var viewModel: VoiceNotesViewModel
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("voice_notes_howto"))
                .font(.caption)
                .foregroundColor(.secondary)

            HStack(spacing: 12) {
                Circle()
                    .fill(recordingIndicatorColor)
                    .frame(width: 12, height: 12)
                Text(localizationManager.localized(statusKey))
                    .font(.subheadline.weight(.medium))
                Spacer()
                Text(timeString(viewModel.elapsedSec))
                    .font(.system(.body, design: .monospaced))
            }

            if viewModel.recordingState == .recording || viewModel.recordingState == .paused {
                VoiceLevelBarsView(
                    level: viewModel.noiseLevel,
                    activeColor: viewModel.recordingState == .recording ? .red : .orange
                )
            }

            if viewModel.showNearLimitWarning {
                Text(localizationManager.localized("voice_notes_limit_warning"))
                    .font(.caption)
                    .foregroundColor(.orange)
            }

            recorderButtons
        }
        .padding()
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }

    @ViewBuilder
    private var recorderButtons: some View {
        switch viewModel.recordingState {
        case .idle, .saved, .failed:
            Button {
                viewModel.startRecording()
            } label: {
                Label(
                    localizationManager.localized("voice_notes_start"),
                    systemImage: "mic.circle.fill"
                )
                .frame(maxWidth: .infinity, minHeight: 44)
            }
            .buttonStyle(.borderedProminent)
            .tint(.red)

        case .recording:
            HStack(spacing: 10) {
                Button {
                    viewModel.pauseRecording()
                } label: {
                    Label(
                        localizationManager.localized("voice_notes_pause"),
                        systemImage: "pause.fill"
                    )
                    .frame(maxWidth: .infinity, minHeight: 44)
                }
                .buttonStyle(.bordered)

                Button {
                    viewModel.stopAndSaveRecording()
                } label: {
                    Label(
                        localizationManager.localized("voice_notes_stop_save"),
                        systemImage: "stop.fill"
                    )
                    .frame(maxWidth: .infinity, minHeight: 44)
                }
                .buttonStyle(.borderedProminent)
                .tint(.orange)
            }

        case .paused:
            HStack(spacing: 10) {
                Button {
                    viewModel.resumeRecording()
                } label: {
                    Label(
                        localizationManager.localized("voice_notes_resume"),
                        systemImage: "play.fill"
                    )
                    .frame(maxWidth: .infinity, minHeight: 44)
                }
                .buttonStyle(.bordered)

                Button {
                    viewModel.stopAndSaveRecording()
                } label: {
                    Label(
                        localizationManager.localized("voice_notes_stop_save"),
                        systemImage: "stop.fill"
                    )
                    .frame(maxWidth: .infinity, minHeight: 44)
                }
                .buttonStyle(.borderedProminent)
                .tint(.orange)
            }

        case .processing:
            HStack {
                ProgressView()
                Text(localizationManager.localized("voice_notes_status_processing"))
                    .font(.subheadline)
            }
            .frame(maxWidth: .infinity, minHeight: 44)
        }
    }

    private var statusKey: String {
        if viewModel.currentStatusText.isEmpty {
            return "voice_notes_status_idle"
        }
        return viewModel.currentStatusText
    }

    private var recordingIndicatorColor: Color {
        switch viewModel.recordingState {
        case .recording: return .red
        case .paused: return .orange
        case .processing: return .blue
        default: return .gray
        }
    }

    private func timeString(_ sec: Int) -> String {
        let m = sec / 60
        let s = sec % 60
        return String(format: "%02d:%02d", m, s)
    }
}
