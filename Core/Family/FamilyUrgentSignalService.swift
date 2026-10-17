import CoreMotion
import Foundation
import UserNotifications
#if canImport(HealthKit)
import HealthKit
#endif

/// WAVE3 G — «Срочный сигнал семье» / Family urgent safety signal.
@MainActor
final class FamilyUrgentSignalService: ObservableObject {
    static let shared = FamilyUrgentSignalService()

    @Published private(set) var isMonitoring = false
    @Published private(set) var lastSentAt: Date?

    private let motion = CMMotionManager()
    private let defaultsKey = "family_urgent_signal_opt_in"
    private var lastAccelSpikeAt: Date?

    var isOptedIn: Bool {
        get { UserDefaults.standard.bool(forKey: defaultsKey) }
        set {
            UserDefaults.standard.set(newValue, forKey: defaultsKey)
            if newValue {
                startMonitoringIfAllowed()
            } else {
                stopMonitoring()
            }
        }
    }

    private init() {
        if isOptedIn {
            startMonitoringIfAllowed()
        }
    }

    func startMonitoringIfAllowed() {
        guard AppStoreBuildPolicy.allowsHealthKitIntegration else { return }
        guard isOptedIn else { return }
        requestHealthAccessIfNeeded()
        startMotionWatch()
        isMonitoring = true
    }

    func stopMonitoring() {
        motion.stopAccelerometerUpdates()
        isMonitoring = false
    }

    func sendUrgentSignal(reason: String = "manual") async {
        guard AppStoreBuildPolicy.allowsHealthKitIntegration else { return }
        await deliver(reason: reason)
    }

    private func requestHealthAccessIfNeeded() {
        #if canImport(HealthKit)
        guard HKHealthStore.isHealthDataAvailable() else { return }
        let store = HKHealthStore()
        let types: Set<HKObjectType> = [HKObjectType.workoutType()]
        store.requestAuthorization(toShare: [], read: types) { _, _ in }
        #endif
    }

    private func startMotionWatch() {
        guard motion.isAccelerometerAvailable else { return }
        motion.accelerometerUpdateInterval = 0.2
        motion.startAccelerometerUpdates(to: .main) { [weak self] data, _ in
            guard let self, let data else { return }
            let g = sqrt(
                data.acceleration.x * data.acceleration.x +
                data.acceleration.y * data.acceleration.y +
                data.acceleration.z * data.acceleration.z
            )
            guard g > 3.5 else { return }
            if let last = self.lastAccelSpikeAt, Date().timeIntervalSince(last) < 60 { return }
            self.lastAccelSpikeAt = Date()
            Task { await self.deliver(reason: "motion_impact") }
        }
    }

    private func deliver(reason: String) async {
        lastSentAt = Date()
        let loc = LocalizationManager.shared
        let title = loc.localized("family_urgent_signal_title")
        let body = loc.localized("family_urgent_signal_body")

        let useCritical = FamilyCriticalAlertsService.shared.shouldUseCriticalDelivery
        NotificationManager.shared.scheduleLocalNotification(
            identifier: "family.urgent.\(UUID().uuidString)",
            title: title,
            body: body,
            category: .family,
            userInfo: [
                "type": "family_urgent_signal",
                "reason": reason,
                "critical": useCritical
            ],
            trigger: UNTimeIntervalNotificationTrigger(timeInterval: 0.3, repeats: false),
            useCriticalAlert: useCritical
        )

        GeofenceFamilyBridge.notifyParentsUrgentSignal(reason: reason)
        print("🆘 FamilyUrgentSignalService: sent reason=\(reason)")
    }
}
