import Foundation

enum MnemonicJourneyPath {
    static let stopCount = 40

    static func stopLocalizationKey(index: Int) -> String {
        let clamped = max(1, min(index, stopCount))
        return String(format: "child_mnemo_journey_stop_%02d", clamped)
    }

    static func stopTitle(index: Int, localization: LocalizationManager) -> String {
        localization.localized(stopLocalizationKey(index: index))
    }
}
