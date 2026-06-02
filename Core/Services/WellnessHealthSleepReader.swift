import Foundation

#if canImport(HealthKit)
import HealthKit
#endif

/// p2-36 — read last night's sleep from Apple Health (optional; requires HealthKit entitlement).
enum WellnessHealthSleepReader {
    struct Result {
        let hours: Double
        let source: String
    }

    static var isAvailable: Bool {
        #if canImport(HealthKit)
        return HKHealthStore.isHealthDataAvailable()
        #else
        return false
        #endif
    }

    @MainActor
    static func requestSleepHours() async -> Result? {
        #if canImport(HealthKit)
        guard HKHealthStore.isHealthDataAvailable() else { return nil }
        let store = HKHealthStore()
        guard let sleepType = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else {
            return nil
        }
        let read = Set([sleepType])
        do {
            try await store.requestAuthorization(toShare: [], read: read)
        } catch {
            return nil
        }
        let end = Date()
        let start = Calendar.current.date(byAdding: .hour, value: -24, to: end) ?? end.addingTimeInterval(-86400)
        let predicate = HKQuery.predicateForSamples(withStart: start, end: end, options: .strictStartDate)
        return await withCheckedContinuation { continuation in
            let query = HKSampleQuery(
                sampleType: sleepType,
                predicate: predicate,
                limit: HKObjectQueryNoLimit,
                sortDescriptors: [NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)]
            ) { _, samples, _ in
                let asleep = (samples as? [HKCategorySample])?.filter {
                    Self.isAsleepSample(value: $0.value)
                } ?? []
                let total = asleep.reduce(0.0) { acc, sample in
                    acc + sample.endDate.timeIntervalSince(sample.startDate)
                }
                let hours = total / 3600.0
                if hours >= 0.5 {
                    continuation.resume(returning: Result(hours: min(14, hours), source: "healthkit"))
                } else {
                    continuation.resume(returning: nil)
                }
            }
            store.execute(query)
        }
        #else
        return nil
        #endif
    }

    #if canImport(HealthKit)
    /// iOS 16+ sleep stages vs legacy `.asleep` (iOS 15 deployment).
    private static func isAsleepSample(value: Int) -> Bool {
        if #available(iOS 16.0, *) {
            return value == HKCategoryValueSleepAnalysis.asleepUnspecified.rawValue
                || value == HKCategoryValueSleepAnalysis.asleepCore.rawValue
                || value == HKCategoryValueSleepAnalysis.asleepDeep.rawValue
                || value == HKCategoryValueSleepAnalysis.asleepREM.rawValue
        }
        return value == HKCategoryValueSleepAnalysis.asleep.rawValue
    }
    #endif
}
