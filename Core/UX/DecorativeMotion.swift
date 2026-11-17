import SwiftUI
import UIKit

/// Continuous decorative motion (pulse / breathing) is optional polish.
/// On A13-class phones a forever animation over material + shadow layers keeps the
/// main thread busy every frame; under heat or Low Power that starves input and ends
/// in a 0x8BADF00D watchdog kill. Stop it whenever the scene is not active.
enum DecorativeMotionPolicy {
    static func allowsContinuousMotion(
        reduceMotion: Bool,
        isAppActive: Bool,
        isLowPowerMode: Bool,
        thermalState: ProcessInfo.ThermalState
    ) -> Bool {
        guard !reduceMotion, isAppActive, !isLowPowerMode else { return false }
        switch thermalState {
        case .nominal, .fair:
            return true
        case .serious, .critical:
            return false
        @unknown default:
            return false
        }
    }

    @MainActor
    static func allowsContinuousMotionNow(reduceMotion: Bool) -> Bool {
        allowsContinuousMotion(
            reduceMotion: reduceMotion,
            isAppActive: UIApplication.shared.applicationState == .active,
            isLowPowerMode: ProcessInfo.processInfo.isLowPowerModeEnabled,
            thermalState: ProcessInfo.processInfo.thermalState
        )
    }
}

/// The repeating animation is bound to this view's own state and attached right after
/// `scaleEffect`, so it cannot leak into sibling layout the way
/// `withAnimation(.repeatForever)` inside `onAppear` does under `NavigationView`.
private struct DecorativePulseModifier: ViewModifier {
    let scale: CGFloat
    let duration: Double
    let delay: Double
    let isEnabled: Bool

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.scenePhase) private var scenePhase
    @State private var isPulsing = false

    func body(content: Content) -> some View {
        content
            .scaleEffect(isPulsing ? scale : 1.0)
            .animation(
                isPulsing
                    ? .easeInOut(duration: duration).repeatForever(autoreverses: true).delay(delay)
                    : .easeOut(duration: 0.2),
                value: isPulsing
            )
            .onAppear { refresh() }
            .onDisappear { isPulsing = false }
            .onChange(of: scenePhase) { _ in refresh() }
            .onChange(of: reduceMotion) { _ in refresh() }
            .onChange(of: isEnabled) { _ in refresh() }
            .onReceive(
                NotificationCenter.default
                    .publisher(for: .NSProcessInfoPowerStateDidChange)
                    .receive(on: RunLoop.main)
            ) { _ in refresh() }
            .onReceive(
                NotificationCenter.default
                    .publisher(for: ProcessInfo.thermalStateDidChangeNotification)
                    .receive(on: RunLoop.main)
            ) { _ in refresh() }
    }

    private func refresh() {
        let allowed = isEnabled && DecorativeMotionPolicy.allowsContinuousMotion(
            reduceMotion: reduceMotion,
            isAppActive: scenePhase == .active,
            isLowPowerMode: ProcessInfo.processInfo.isLowPowerModeEnabled,
            thermalState: ProcessInfo.processInfo.thermalState
        )
        if isPulsing != allowed {
            isPulsing = allowed
        }
    }
}

extension View {
    /// Soft breathing scale for decorative elements; off for Reduce Motion, Low Power,
    /// serious heat, whenever the scene is not active, and when `isEnabled` is false
    /// (e.g. a sheet covers the screen).
    func decorativePulse(
        scale: CGFloat = 1.055,
        duration: Double = 1.85,
        delay: Double = 0,
        isEnabled: Bool = true
    ) -> some View {
        modifier(DecorativePulseModifier(scale: scale, duration: duration, delay: delay, isEnabled: isEnabled))
    }
}
