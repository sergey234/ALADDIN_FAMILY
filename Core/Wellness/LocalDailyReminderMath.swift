import Foundation

/// Pure calendar math for local daily reminders (habits + wind-down).
enum LocalDailyReminderMath {
    static func leadTime(bedtimeHour: Int, bedtimeMinute: Int, minutesBefore: Int) -> (hour: Int, minute: Int) {
        let total = bedtimeHour * 60 + bedtimeMinute - minutesBefore
        let wrapped = ((total % (24 * 60)) + (24 * 60)) % (24 * 60)
        return (wrapped / 60, wrapped % 60)
    }

    static func nextFire(hour: Int, minute: Int, now: Date = Date(), calendar: Calendar = .current) -> Date {
        var comps = calendar.dateComponents([.year, .month, .day], from: now)
        comps.hour = max(0, min(23, hour))
        comps.minute = max(0, min(59, minute))
        comps.second = 0
        let candidate = calendar.date(from: comps) ?? now
        if candidate > now {
            return candidate
        }
        return calendar.date(byAdding: .day, value: 1, to: candidate) ?? candidate
    }

    static func isSameDay(_ lhs: Date, _ rhs: Date, calendar: Calendar = .current) -> Bool {
        calendar.isDate(lhs, inSameDayAs: rhs)
    }

    static func nextFireLine(date: Date, localization: LocalizationManager, now: Date = Date()) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "HH:mm"
        let time = formatter.string(from: date)
        let key = Calendar.current.isDate(date, inSameDayAs: now)
            ? "habit_next_reminder_today_fmt"
            : "habit_next_reminder_tomorrow_fmt"
        return String(format: localization.localized(key), time)
    }
}
