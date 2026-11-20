import Foundation

/// Growth P.4: after home geofence arrival, optionally offer system Share once per day.
enum ShareArrivedHomeOffer {
    static let offerNotification = Notification.Name("aladdin.share.arrived_home_offer")
    private static let lastDayKey = "share_arrived_home_last_day_v1"

    /// Call when `geofence_home_arrival` fires for the current device.
    static func noteHomeArrivalIfEligible(now: Date = Date(), calendar: Calendar = .current) {
        let day = calendar.startOfDay(for: now).timeIntervalSince1970
        let last = UserDefaults.standard.double(forKey: lastDayKey)
        if last > 0, abs(last - day) < 1 {
            return
        }
        UserDefaults.standard.set(day, forKey: lastDayKey)
        NotificationCenter.default.post(name: offerNotification, object: nil)
    }
}
