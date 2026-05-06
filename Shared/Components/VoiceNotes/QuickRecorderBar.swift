import SwiftUI

struct QuickRecorderBar: View {
    @ObservedObject var viewModel: VoiceNotesViewModel
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        VStack(spacing: 10) {
            HStack(spacing: 12) {
                Circle()
                    .fill(viewModel.recordingState == .recording ? Color.red : Color.gray)
                    .frame(width: 12, height: 12)
                Text(localizationManager.localized(viewModel.currentStatusText.isEmpty ? "voice_notes_status_idle" : viewModel.currentStatusText))
                    .font(.subheadline)
                Spacer()
                Text(timeString(viewModel.elapsedSec))
                    .font(.system(.body, design: .monospaced))
            }

            ProgressView(value: viewModel.noiseLevel)
                .tint(.orange)

            HStack(spacing: 10) {
                Button(localizationManager.localized("voice_notes_record")) {
                    viewModel.startRecording()
                }
                .buttonStyle(.borderedProminent)
                .disabled(viewModel.recordingState == .recording)

                Button(localizationManager.localized("voice_notes_pause")) {
                    viewModel.pauseRecording()
                }
                .buttonStyle(.bordered)
                .disabled(viewModel.recordingState != .recording)

                Button(localizationManager.localized("voice_notes_resume")) {
                    viewModel.resumeRecording()
                }
                .buttonStyle(.bordered)
                .disabled(viewModel.recordingState != .paused)

                Button(localizationManager.localized("voice_notes_stop")) {
                    viewModel.stopAndSaveRecording()
                }
                .buttonStyle(.bordered)
                .disabled(!(viewModel.recordingState == .recording || viewModel.recordingState == .paused))
            }
        }
        .padding()
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }

    private func timeString(_ sec: Int) -> String {
        let m = sec / 60
        let s = sec % 60
        return String(format: "%02d:%02d", m, s)
    }
}
