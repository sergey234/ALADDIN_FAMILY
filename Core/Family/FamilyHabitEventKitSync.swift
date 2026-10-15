import EventKit
import Foundation

/// ProdQA S16 — mirror enabled family habits into Apple Calendar (same times as local push).
@MainActor
final class FamilyHabitEventKitSync {
    static let shared = FamilyHabitEventKitSync()

    private let store = EKEventStore()
    private let defaultsKey = "family_habit_eventkit_sync_enabled_v1"
    private let eventIdPrefix = "aladdin.habit."

    private init() {}

    var isEnabled: Bool {
        get { UserDefaults.standard.bool(forKey: defaultsKey) }
        set { UserDefaults.standard.set(newValue, forKey: defaultsKey) }
    }

    /// Request access then upsert today's events for enabled presets (+ custom once_daily).
    func syncIfEnabled(config: FamilyHabitRemindersConfig) async {
        guard isEnabled else { return }
        let granted = await requestAccess()
        guard granted else {
            print("📅 family habits EventKit: access denied")
            return
        }
        await upsertEvents(config: config)
    }

    func requestAccess() async -> Bool {
        if #available(iOS 17.0, *) {
            do {
                return try await store.requestFullAccessToEvents()
            } catch {
                print("📅 EventKit access error: \(error.localizedDescription)")
                return false
            }
        } else {
            return await withCheckedContinuation { cont in
                store.requestAccess(to: .event) { ok, _ in
                    cont.resume(returning: ok)
                }
            }
        }
    }

    private func upsertEvents(config: FamilyHabitRemindersConfig) async {
        let cal = store.defaultCalendarForNewEvents ?? store.calendars(for: .event).first
        guard let calendar = cal else { return }

        let loc = LocalizationManager.shared
        let dayStart = Calendar.current.startOfDay(for: Date())
        guard let dayEnd = Calendar.current.date(byAdding: .day, value: 1, to: dayStart) else { return }

        // Remove prior ALADDIN habit events for today, then recreate.
        let predicate = store.predicateForEvents(withStart: dayStart, end: dayEnd, calendars: [calendar])
        let existing = store.events(matching: predicate).filter {
            ($0.notes ?? "").hasPrefix(eventIdPrefix) || ($0.title ?? "").hasPrefix("ALADDIN ·")
        }
        for ev in existing {
            do { try store.remove(ev, span: .thisEvent, commit: false) } catch { /* best-effort */ }
        }

        for preset in FamilyHabitPresetId.allCases {
            let schedule = config.schedule(for: preset)
            guard schedule.enabled else { continue }
            let title = "ALADDIN · \(loc.localized(preset.titleKey))"
            let notes = "\(eventIdPrefix)\(preset.rawValue)"
            switch preset {
            case .water, .medicine:
                let slots = schedule.windowNotificationSlots(maxSlots: 8)
                for (idx, slot) in slots.enumerated() {
                    addEvent(
                        title: title,
                        notes: "\(notes).\(idx)",
                        hour: slot.hour,
                        minute: slot.minute,
                        calendar: calendar
                    )
                }
            default:
                addEvent(
                    title: title,
                    notes: notes,
                    hour: schedule.hour,
                    minute: schedule.minute,
                    calendar: calendar
                )
            }
        }

        for custom in config.custom where custom.enabled {
            let title = "ALADDIN · \(custom.title)"
            let notes = "\(eventIdPrefix)custom.\(custom.id)"
            addEvent(
                title: title,
                notes: notes,
                hour: custom.hour,
                minute: custom.minute,
                calendar: calendar
            )
        }

        do {
            try store.commit()
            print("📅 family habits EventKit: synced")
        } catch {
            print("📅 EventKit commit error: \(error.localizedDescription)")
        }
    }

    private func addEvent(
        title: String,
        notes: String,
        hour: Int,
        minute: Int,
        calendar: EKCalendar
    ) {
        var comps = Calendar.current.dateComponents([.year, .month, .day], from: Date())
        comps.hour = hour
        comps.minute = minute
        guard let start = Calendar.current.date(from: comps) else { return }
        let end = start.addingTimeInterval(15 * 60)
        let event = EKEvent(eventStore: store)
        event.title = title
        event.notes = notes
        event.startDate = start
        event.endDate = end
        event.calendar = calendar
        event.addAlarm(EKAlarm(relativeOffset: 0))
        do {
            try store.save(event, span: .thisEvent, commit: false)
        } catch {
            print("📅 EventKit save error: \(error.localizedDescription)")
        }
    }
}
