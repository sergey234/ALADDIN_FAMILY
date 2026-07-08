import Foundation

#if canImport(HealthKit)
import HealthKit
#endif

/// fws-10 — optional HealthKit fall observer → family push (behind toggle).
final class ElderlyFallDetectionService {
    static let shared = ElderlyFallDetectionService()
    static let enabledKey = "elderly_fall_detection_enabled"

    private let defaults = UserDefaults.standard
    #if canImport(HealthKit)
    private var healthStore: HKHealthStore?
    private var observerQuery: HKObserverQuery?
    #endif

    private init() {}

    var isEnabled: Bool {
        defaults.bool(forKey: Self.enabledKey)
    }

    func setEnabled(_ enabled: Bool) {
        defaults.set(enabled, forKey: Self.enabledKey)
        if enabled {
            Task { await startMonitoring() }
        } else {
            stopMonitoring()
        }
    }

    @MainActor
    func startMonitoring() async {
        #if canImport(HealthKit)
        guard HKHealthStore.isHealthDataAvailable() else { return }
        let store = HKHealthStore()
        healthStore = store

        guard let fallType = Self.fallSampleType else { return }
        do {
            try await store.requestAuthorization(toShare: [], read: Set([fallType]))
        } catch {
            return
        }

        let query = HKObserverQuery(sampleType: fallType, predicate: nil) { [weak self] _, _, error in
            if error != nil { return }
            Task { await self?.handleFallDetected(source: "healthkit_fall") }
        }
        observerQuery = query
        store.execute(query)
        store.enableBackgroundDelivery(for: fallType, frequency: .immediate) { _, _ in }
        #endif
    }

    func stopMonitoring() {
        #if canImport(HealthKit)
        if let store = healthStore, let query = observerQuery {
            store.stop(query)
        }
        observerQuery = nil
        healthStore = nil
        #endif
    }

    @MainActor
    func handleFallDetected(source: String = "healthkit_fall") async {
        guard isEnabled else { return }
        HapticFeedback.notification(.warning)
        try? await WellnessAPIService.shared.reportElderlyFall(source: source)
    }

    #if canImport(HealthKit)
    private static var fallSampleType: HKSampleType? {
        if #available(iOS 15.0, *) {
            let identifier = HKCategoryTypeIdentifier(rawValue: "HKCategoryTypeIdentifierFallDetectionEvent")
            return HKCategoryType.categoryType(forIdentifier: identifier)
        }
        return nil
    }
    #endif
}
