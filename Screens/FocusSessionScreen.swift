import SwiftUI

/// p2-8a–c — Opal-light Focus 25/60 (flagged; not a Screen Time clone).
struct FocusSessionScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var store = FocusSessionStore.shared

    @State private var rewardNote: String?

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .neutral).ignoresSafeArea()
            VStack(alignment: .leading, spacing: 16) {
                header
                Text(localizationManager.localized("focus_session_subtitle"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
                Text(localizationManager.localized("focus_session_disclaimer"))
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.55))

                if !FamilyFocusSessionFeature.isEnabled {
                    Text(localizationManager.localized("focus_session_flag_off"))
                        .font(.subheadline)
                        .foregroundColor(.orange)
                    Spacer()
                } else {
                    durationPicker
                    timerRing
                    statusBlock
                    actionButtons
                    Spacer(minLength: 0)
                }
            }
            .padding()
        }
        .foregroundColor(.white)
        .navigationBarHidden(true)
        .accessibilityIdentifier("focus_session_screen")
    }

    private var header: some View {
        HStack {
            Button {
                if store.phase == .running {
                    store.abort(softMessage: localizationManager.localized("focus_session_aborted"))
                }
                navigationManager.goBackToPreviousScreen(reason: "focusSession")
            } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            Text(localizationManager.localized("focus_session_title"))
                .font(.headline.bold())
            Spacer()
        }
    }

    private var durationPicker: some View {
        HStack(spacing: 10) {
            ForEach(FocusSessionStore.DurationMinutes.allCases) { d in
                Button {
                    store.select(d)
                } label: {
                    Text("\(d.rawValue) " + localizationManager.localized("focus_session_min"))
                        .font(.subheadline.weight(.semibold))
                        .padding(.horizontal, 14)
                        .padding(.vertical, 10)
                        .background(
                            store.selectedDuration == d
                                ? Color(hex: "8B5CF6")
                                : Color.white.opacity(0.12)
                        )
                        .cornerRadius(12)
                }
                .buttonStyle(.plain)
                .disabled(store.phase == .running)
                .accessibilityIdentifier("focus_session_duration_\(d.rawValue)")
            }
        }
    }

    private var timerRing: some View {
        let total = store.selectedDuration.rawValue * 60
        let progress = total > 0
            ? CGFloat(total - store.secondsRemaining) / CGFloat(total)
            : 0
        return ZStack {
            Circle()
                .stroke(Color.white.opacity(0.15), lineWidth: 10)
                .frame(width: 180, height: 180)
            Circle()
                .trim(from: 0, to: progress)
                .stroke(Color(hex: "8B5CF6"), style: StrokeStyle(lineWidth: 10, lineCap: .round))
                .rotationEffect(.degrees(-90))
                .frame(width: 180, height: 180)
            Text(timeLabel)
                .font(.title.monospacedDigit().bold())
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .accessibilityIdentifier("focus_session_timer")
    }

    private var timeLabel: String {
        let m = store.secondsRemaining / 60
        let s = store.secondsRemaining % 60
        return String(format: "%d:%02d", m, s)
    }

    @ViewBuilder
    private var statusBlock: some View {
        if store.phase == .completed {
            Text(localizationManager.localized("focus_session_completed"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.green.opacity(0.9))
            if let rewardNote {
                Text(rewardNote).font(.caption).foregroundColor(.green.opacity(0.85))
            }
        } else if store.phase == .aborted, let msg = store.softAbortMessage {
            Text(msg)
                .font(.subheadline)
                .foregroundColor(.orange.opacity(0.95))
        }
    }

    private var actionButtons: some View {
        VStack(spacing: 10) {
            switch store.phase {
            case .idle, .aborted:
                Button {
                    store.start()
                    rewardNote = nil
                } label: {
                    Text(localizationManager.localized("focus_session_start"))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.borderedProminent)
                .tint(Color(hex: "8B5CF6"))
                .accessibilityIdentifier("focus_session_start")
            case .running:
                Button {
                    store.abort(softMessage: localizationManager.localized("focus_session_aborted"))
                } label: {
                    Text(localizationManager.localized("focus_session_stop"))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.bordered)
                .accessibilityIdentifier("focus_session_stop")
            case .completed:
                Button {
                    store.resetToIdle()
                    rewardNote = nil
                } label: {
                    Text(localizationManager.localized("focus_session_again"))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.borderedProminent)
                .tint(Color(hex: "8B5CF6"))
                .onAppear {
                    if store.lastGrantApplied == false {
                        rewardNote = localizationManager.localized("focus_session_xp_already")
                    } else {
                        rewardNote = localizationManager.localized("focus_session_xp")
                    }
                }
            }
        }
    }
}
