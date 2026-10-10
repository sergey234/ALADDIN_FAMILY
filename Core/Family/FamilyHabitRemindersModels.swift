import Foundation

/// fws-02 preset identifiers — 💧 / 📵 / 😴 (reminder only, not bedtime block).
enum FamilyHabitPresetId: String, Codable, CaseIterable, Identifiable {
    case water
    case phoneDown = "phone_down"
    case windDown = "wind_down"
    /// p1-8a — medicine reminder (single daily slot; ping ON by default when Due enabled).
    case medicine

    var id: String { rawValue }

    var emoji: String {
        switch self {
        case .water: return "💧"
        case .phoneDown: return "📵"
        case .windDown: return "😴"
        case .medicine: return "💊"
        }
    }

    var titleKey: String { "family_habit_\(rawValue)_title" }
    var bodyKey: String { "family_habit_\(rawValue)_body" }
}

/// Allowed daily water goals (liters).
enum FamilyHabitWaterDailyLiters: Double, CaseIterable, Identifiable {
    case half = 0.5
    case one = 1.0
    case oneHalf = 1.5
    case two = 2.0
    case twoHalf = 2.5
    case three = 3.0

    var id: Double { rawValue }

    var labelKey: String {
        switch self {
        case .half: return "family_habit_water_liters_0_5"
        case .one: return "family_habit_water_liters_1"
        case .oneHalf: return "family_habit_water_liters_1_5"
        case .two: return "family_habit_water_liters_2"
        case .twoHalf: return "family_habit_water_liters_2_5"
        case .three: return "family_habit_water_liters_3"
        }
    }

    static func nearest(_ value: Double) -> FamilyHabitWaterDailyLiters {
        allCases.min(by: { abs($0.rawValue - value) < abs($1.rawValue - value) }) ?? .two
    }
}

/// Interval between water pushes (minutes).
enum FamilyHabitWaterInterval: Int, CaseIterable, Identifiable {
    case oneHour = 60
    case oneHalf = 90
    case twoHours = 120
    case threeHours = 180

    var id: Int { rawValue }

    var labelKey: String {
        switch self {
        case .oneHour: return "family_habit_water_interval_1h"
        case .oneHalf: return "family_habit_water_interval_1_5h"
        case .twoHours: return "family_habit_water_interval_2h"
        case .threeHours: return "family_habit_water_interval_3h"
        }
    }

    static func nearest(_ minutes: Int) -> FamilyHabitWaterInterval {
        allCases.min(by: { abs($0.rawValue - minutes) < abs($1.rawValue - minutes) }) ?? .twoHours
    }
}

struct FamilyHabitPresetSchedule: Codable, Equatable {
    var enabled: Bool
    /// Start of reminder window (and single daily time for non-water presets).
    var hour: Int
    var minute: Int
    /// End of window (water only; ignored for other presets).
    var endHour: Int
    var endMinute: Int
    /// Minutes between water pushes.
    var intervalMinutes: Int
    /// Daily water goal in liters.
    var dailyLiters: Double
    /// p1-7a — keep pinging until Done (water default OFF).
    var pingUntilDone: Bool
    /// Minutes between due-pings (clamped 15…30).
    var pingIntervalMinutes: Int
    /// Cap due-pings per day.
    var pingMaxPerDay: Int

    static let `default` = FamilyHabitPresetSchedule(
        enabled: false,
        hour: 11,
        minute: 0,
        endHour: 21,
        endMinute: 0,
        intervalMinutes: 120,
        dailyLiters: 2.0,
        pingUntilDone: false,
        pingIntervalMinutes: 20,
        pingMaxPerDay: 6
    )

    enum CodingKeys: String, CodingKey {
        case enabled, hour, minute
        case endHour = "end_hour"
        case endMinute = "end_minute"
        case intervalMinutes = "interval_minutes"
        case dailyLiters = "daily_liters"
        case pingUntilDone = "ping_until_done"
        case pingIntervalMinutes = "ping_interval_minutes"
        case pingMaxPerDay = "ping_max_per_day"
    }

    init(
        enabled: Bool,
        hour: Int,
        minute: Int,
        endHour: Int = 21,
        endMinute: Int = 0,
        intervalMinutes: Int = 120,
        dailyLiters: Double = 2.0,
        pingUntilDone: Bool = false,
        pingIntervalMinutes: Int = 20,
        pingMaxPerDay: Int = 6
    ) {
        self.enabled = enabled
        self.hour = hour
        self.minute = minute
        self.endHour = endHour
        self.endMinute = endMinute
        self.intervalMinutes = intervalMinutes
        self.dailyLiters = dailyLiters
        self.pingUntilDone = pingUntilDone
        self.pingIntervalMinutes = min(30, max(15, pingIntervalMinutes))
        self.pingMaxPerDay = min(12, max(1, pingMaxPerDay))
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        enabled = try c.decodeIfPresent(Bool.self, forKey: .enabled) ?? false
        hour = try c.decodeIfPresent(Int.self, forKey: .hour) ?? 11
        minute = try c.decodeIfPresent(Int.self, forKey: .minute) ?? 0
        endHour = try c.decodeIfPresent(Int.self, forKey: .endHour) ?? 21
        endMinute = try c.decodeIfPresent(Int.self, forKey: .endMinute) ?? 0
        intervalMinutes = try c.decodeIfPresent(Int.self, forKey: .intervalMinutes) ?? 120
        dailyLiters = try c.decodeIfPresent(Double.self, forKey: .dailyLiters) ?? 2.0
        // p1-7a: water and legacy configs default ping OFF
        pingUntilDone = try c.decodeIfPresent(Bool.self, forKey: .pingUntilDone) ?? false
        let rawPingInterval = try c.decodeIfPresent(Int.self, forKey: .pingIntervalMinutes) ?? 20
        pingIntervalMinutes = min(30, max(15, rawPingInterval))
        let rawPingMax = try c.decodeIfPresent(Int.self, forKey: .pingMaxPerDay) ?? 6
        pingMaxPerDay = min(12, max(1, rawPingMax))
    }

    static func defaultsMap() -> [FamilyHabitPresetId: FamilyHabitPresetSchedule] {
        [
            .water: FamilyHabitPresetSchedule(
                enabled: false, hour: 9, minute: 0, endHour: 21, endMinute: 0,
                intervalMinutes: 120, dailyLiters: 2.0,
                pingUntilDone: false, pingIntervalMinutes: 20, pingMaxPerDay: 6
            ),
            .phoneDown: FamilyHabitPresetSchedule(
                enabled: false, hour: 21, minute: 0,
                pingUntilDone: false, pingIntervalMinutes: 20, pingMaxPerDay: 6
            ),
            .windDown: FamilyHabitPresetSchedule(
                enabled: false, hour: 22, minute: 30,
                pingUntilDone: false, pingIntervalMinutes: 20, pingMaxPerDay: 6
            ),
            // Medicine: same window model as water (09:00–21:00 / interval), not a single daily ping.
            .medicine: FamilyHabitPresetSchedule(
                enabled: false, hour: 9, minute: 0, endHour: 21, endMinute: 0,
                intervalMinutes: 180, dailyLiters: 2.0,
                pingUntilDone: true, pingIntervalMinutes: 20, pingMaxPerDay: 6
            ),
        ]
    }

    /// Compact summary for collapsed water row, e.g. `2 л · каждые 2 ч · 09:00–21:00`.
    func waterSummaryLine(localization: LocalizationManager) -> String {
        let liters = FamilyHabitWaterDailyLiters.nearest(dailyLiters)
        let interval = FamilyHabitWaterInterval.nearest(intervalMinutes)
        let litersLabel = localization.localized(liters.labelKey)
        let intervalLabel = localization.localized(interval.labelKey)
        return "\(litersLabel) · \(intervalLabel) · \(windowTimeRangeLabel)"
    }

    /// Medicine / generic window summary without liters.
    func windowSummaryLine(localization: LocalizationManager) -> String {
        let interval = FamilyHabitWaterInterval.nearest(intervalMinutes)
        let intervalLabel = localization.localized(interval.labelKey)
        return "\(intervalLabel) · \(windowTimeRangeLabel)"
    }

    var windowTimeRangeLabel: String {
        String(format: "%02d:%02d–%02d:%02d", hour, minute, endHour, endMinute)
    }

    /// Slot times (hour, minute) from start→end stepping by interval. Cap 12 (water + medicine).
    func waterNotificationSlots(maxSlots: Int = 12) -> [(hour: Int, minute: Int)] {
        windowNotificationSlots(maxSlots: maxSlots)
    }

    /// Shared window slots for water and medicine (same math as WindDown-style calendar repeats).
    func windowNotificationSlots(maxSlots: Int = 12) -> [(hour: Int, minute: Int)] {
        let start = hour * 60 + minute
        var end = endHour * 60 + endMinute
        if end <= start {
            end += 24 * 60
        }
        let step = max(30, FamilyHabitWaterInterval.nearest(intervalMinutes).rawValue)
        var slots: [(Int, Int)] = []
        var t = start
        while t <= end && slots.count < maxSlots {
            let wrapped = t % (24 * 60)
            slots.append((wrapped / 60, wrapped % 60))
            t += step
        }
        if slots.isEmpty {
            slots.append((hour, minute))
        }
        return slots
    }
}

// MARK: - Custom habits (fhc-01 Hybrid Variant 2)

/// Schedule mode for user-defined reminders under Medicine.
enum FamilyHabitCustomMode: String, Codable, CaseIterable, Identifiable {
    case window
    case onceDaily = "once_daily"
    /// One-shot date+time — model/decode in fhc-01; local schedule in fhc-15.
    case onceAt = "once_at"

    var id: String { rawValue }
}

/// fhc-02 — interval chips for custom window mode: 15 / 30 / 60 / 120 (+ free minutes 15…180).
enum FamilyHabitCustomInterval: Int, CaseIterable, Identifiable {
    case minutes15 = 15
    case minutes30 = 30
    case minutes60 = 60
    case minutes120 = 120

    var id: Int { rawValue }

    var labelKey: String {
        switch self {
        case .minutes15: return "family_habit_custom_interval_15m"
        case .minutes30: return "family_habit_custom_interval_30m"
        case .minutes60: return "family_habit_custom_interval_60m"
        case .minutes120: return "family_habit_custom_interval_120m"
        }
    }

    static func clampMinutes(_ minutes: Int) -> Int {
        min(
            FamilyHabitCustomReminder.intervalMaxMinutes,
            max(FamilyHabitCustomReminder.intervalMinMinutes, minutes)
        )
    }

    static func nearest(_ minutes: Int) -> FamilyHabitCustomInterval {
        let clamped = clampMinutes(minutes)
        return allCases.min(by: { abs($0.rawValue - clamped) < abs($1.rawValue - clamped) })
            ?? .minutes60
    }

    static func isChipValue(_ minutes: Int) -> Bool {
        allCases.contains(where: { $0.rawValue == minutes })
    }

    /// Chip highlight + whether minutes are a free (non-chip) value after clamp.
    static func selection(for minutes: Int) -> (chip: FamilyHabitCustomInterval, isCustom: Bool) {
        let clamped = clampMinutes(minutes)
        if let exact = allCases.first(where: { $0.rawValue == clamped }) {
            return (exact, false)
        }
        return (nearest(clamped), true)
    }

    static func intervalLabel(minutes: Int, localization: LocalizationManager) -> String {
        let clamped = clampMinutes(minutes)
        if isChipValue(clamped) {
            return localization.localized(nearest(clamped).labelKey)
        }
        return String(
            format: localization.localized("family_habit_custom_interval_custom_fmt"),
            clamped
        )
    }
}

/// User-defined family habit reminder (`config.custom[]`, max 5).
struct FamilyHabitCustomReminder: Codable, Equatable, Identifiable {
    static let maxPerFamily = 5
    static let titleMaxLength = 40
    static let intervalMinMinutes = 15
    static let intervalMaxMinutes = 180
    static let maxSlotsPerDay = 12
    static let defaultEmoji = "⭐️"

    var id: String
    var title: String
    var emoji: String
    var enabled: Bool
    var mode: FamilyHabitCustomMode
    /// `false` when JSON had an unknown `mode` string — scheduler must skip (no crash).
    var modeRecognized: Bool
    /// Original wire `mode` when unrecognized (re-encoded as-is; not a separate JSON key).
    var unrecognizedModeRaw: String?
    var hour: Int
    var minute: Int
    var endHour: Int
    var endMinute: Int
    var intervalMinutes: Int
    var pingUntilDone: Bool
    var pingIntervalMinutes: Int
    var pingMaxPerDay: Int
    var sortOrder: Int
    /// ISO8601 for `once_at` (fhc-15); ignored until then.
    var fireAt: String?

    enum CodingKeys: String, CodingKey {
        case id, title, emoji, enabled, mode
        case hour, minute
        case endHour = "end_hour"
        case endMinute = "end_minute"
        case intervalMinutes = "interval_minutes"
        case pingUntilDone = "ping_until_done"
        case pingIntervalMinutes = "ping_interval_minutes"
        case pingMaxPerDay = "ping_max_per_day"
        case sortOrder = "sort_order"
        case fireAt = "fire_at"
    }

    init(
        id: String = UUID().uuidString,
        title: String,
        emoji: String = defaultEmoji,
        enabled: Bool = true,
        mode: FamilyHabitCustomMode = .onceDaily,
        modeRecognized: Bool = true,
        unrecognizedModeRaw: String? = nil,
        hour: Int = 21,
        minute: Int = 0,
        endHour: Int = 21,
        endMinute: Int = 0,
        intervalMinutes: Int = 60,
        pingUntilDone: Bool = false,
        pingIntervalMinutes: Int = 20,
        pingMaxPerDay: Int = 6,
        sortOrder: Int = 0,
        fireAt: String? = nil
    ) {
        self.id = id
        self.title = title
        self.emoji = emoji
        self.enabled = enabled
        self.mode = mode
        self.modeRecognized = modeRecognized
        self.unrecognizedModeRaw = unrecognizedModeRaw
        self.hour = hour
        self.minute = minute
        self.endHour = endHour
        self.endMinute = endMinute
        self.intervalMinutes = intervalMinutes
        self.pingUntilDone = pingUntilDone
        self.pingIntervalMinutes = pingIntervalMinutes
        self.pingMaxPerDay = pingMaxPerDay
        self.sortOrder = sortOrder
        self.fireAt = fireAt
        self = clamped()
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = (try c.decodeIfPresent(String.self, forKey: .id) ?? UUID().uuidString)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if id.isEmpty { id = UUID().uuidString }
        title = try c.decodeIfPresent(String.self, forKey: .title) ?? ""
        emoji = try c.decodeIfPresent(String.self, forKey: .emoji) ?? Self.defaultEmoji
        enabled = try c.decodeIfPresent(Bool.self, forKey: .enabled) ?? true
        if let rawMode = try c.decodeIfPresent(String.self, forKey: .mode) {
            if let parsed = FamilyHabitCustomMode(rawValue: rawMode) {
                mode = parsed
                modeRecognized = true
                unrecognizedModeRaw = nil
            } else {
                mode = .window
                modeRecognized = false
                unrecognizedModeRaw = rawMode
            }
        } else {
            mode = .onceDaily
            modeRecognized = true
            unrecognizedModeRaw = nil
        }
        hour = try c.decodeIfPresent(Int.self, forKey: .hour) ?? 21
        minute = try c.decodeIfPresent(Int.self, forKey: .minute) ?? 0
        endHour = try c.decodeIfPresent(Int.self, forKey: .endHour) ?? 21
        endMinute = try c.decodeIfPresent(Int.self, forKey: .endMinute) ?? 0
        intervalMinutes = try c.decodeIfPresent(Int.self, forKey: .intervalMinutes) ?? 60
        pingUntilDone = try c.decodeIfPresent(Bool.self, forKey: .pingUntilDone) ?? false
        pingIntervalMinutes = try c.decodeIfPresent(Int.self, forKey: .pingIntervalMinutes) ?? 20
        pingMaxPerDay = try c.decodeIfPresent(Int.self, forKey: .pingMaxPerDay) ?? 6
        sortOrder = try c.decodeIfPresent(Int.self, forKey: .sortOrder) ?? 0
        let rawFire = try c.decodeIfPresent(String.self, forKey: .fireAt)
        fireAt = rawFire?.trimmingCharacters(in: .whitespacesAndNewlines)
        if fireAt?.isEmpty == true { fireAt = nil }
        self = clamped()
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        let normalized = clamped()
        try c.encode(normalized.id, forKey: .id)
        try c.encode(normalized.title, forKey: .title)
        try c.encode(normalized.emoji, forKey: .emoji)
        try c.encode(normalized.enabled, forKey: .enabled)
        if let raw = normalized.unrecognizedModeRaw, !normalized.modeRecognized {
            try c.encode(raw, forKey: .mode)
        } else {
            try c.encode(normalized.mode, forKey: .mode)
        }
        try c.encode(normalized.hour, forKey: .hour)
        try c.encode(normalized.minute, forKey: .minute)
        try c.encode(normalized.endHour, forKey: .endHour)
        try c.encode(normalized.endMinute, forKey: .endMinute)
        try c.encode(normalized.intervalMinutes, forKey: .intervalMinutes)
        try c.encode(normalized.pingUntilDone, forKey: .pingUntilDone)
        try c.encode(normalized.pingIntervalMinutes, forKey: .pingIntervalMinutes)
        try c.encode(normalized.pingMaxPerDay, forKey: .pingMaxPerDay)
        try c.encode(normalized.sortOrder, forKey: .sortOrder)
        try c.encodeIfPresent(normalized.fireAt, forKey: .fireAt)
    }

    /// Clamp fields; does not drop empty titles (list normalize does).
    func clamped() -> FamilyHabitCustomReminder {
        var copy = self
        let trimmedTitle = title.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmedTitle.count <= Self.titleMaxLength {
            copy.title = trimmedTitle
        } else {
            copy.title = String(trimmedTitle.prefix(Self.titleMaxLength))
        }
        copy.emoji = Self.firstGrapheme(emoji) ?? Self.defaultEmoji
        copy.hour = min(23, max(0, hour))
        copy.minute = min(59, max(0, minute))
        copy.endHour = min(23, max(0, endHour))
        copy.endMinute = min(59, max(0, endMinute))
        copy.intervalMinutes = FamilyHabitCustomInterval.clampMinutes(intervalMinutes)
        copy.pingIntervalMinutes = min(30, max(15, pingIntervalMinutes))
        copy.pingMaxPerDay = min(12, max(1, pingMaxPerDay))
        copy.sortOrder = max(0, sortOrder)
        if let fire = fireAt?.trimmingCharacters(in: .whitespacesAndNewlines), !fire.isEmpty {
            copy.fireAt = fire
        } else {
            copy.fireAt = nil
        }
        if copy.id.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            copy.id = UUID().uuidString
        }
        return copy
    }

    /// Window / once_daily always when enabled; once_at only with future `fire_at` (fhc-15).
    var shouldScheduleLocally: Bool {
        guard enabled, modeRecognized, !title.isEmpty else { return false }
        switch mode {
        case .window, .onceDaily:
            return true
        case .onceAt:
            guard let date = fireAtDate else { return false }
            return date > Date()
        }
    }

    /// Parsed `fire_at` in device-local calendar (S5).
    var fireAtDate: Date? {
        Self.parseFireAt(fireAt)
    }

    /// True when once_at has a past `fire_at` (UI hint; do not schedule).
    var onceAtIsPast: Bool {
        guard mode == .onceAt, let date = fireAtDate else { return false }
        return date <= Date()
    }

    mutating func setFireAtDate(_ date: Date) {
        fireAt = Self.encodeFireAt(date)
        let cal = Calendar.current
        hour = cal.component(.hour, from: date)
        minute = cal.component(.minute, from: date)
    }

    static func parseFireAt(_ raw: String?) -> Date? {
        guard let raw = raw?.trimmingCharacters(in: .whitespacesAndNewlines), !raw.isEmpty else {
            return nil
        }
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let d = iso.date(from: raw) { return d }
        iso.formatOptions = [.withInternetDateTime]
        if let d = iso.date(from: raw) { return d }
        let local = DateFormatter()
        local.locale = Locale(identifier: "en_US_POSIX")
        local.timeZone = .current
        local.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        return local.date(from: raw)
    }

    static func encodeFireAt(_ date: Date) -> String {
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime]
        iso.timeZone = .current
        return iso.string(from: date)
    }

    /// Prefill for editor (fhc-02/05): window 09–21 / 60m; once_daily 21:00; once_at shell.
    static func prefill(
        mode: FamilyHabitCustomMode,
        title: String = "",
        emoji: String = defaultEmoji
    ) -> FamilyHabitCustomReminder {
        switch mode {
        case .window:
            return FamilyHabitCustomReminder(
                title: title,
                emoji: emoji,
                mode: .window,
                hour: 9,
                minute: 0,
                endHour: 21,
                endMinute: 0,
                intervalMinutes: FamilyHabitCustomInterval.minutes60.rawValue
            )
        case .onceDaily:
            return FamilyHabitCustomReminder(
                title: title,
                emoji: emoji,
                mode: .onceDaily,
                hour: 21,
                minute: 0,
                intervalMinutes: FamilyHabitCustomInterval.minutes60.rawValue
            )
        case .onceAt:
            var item = FamilyHabitCustomReminder(
                title: title,
                emoji: emoji,
                mode: .onceAt,
                hour: 21,
                minute: 0,
                fireAt: nil
            )
            // Default: tomorrow 21:00 device-local (editor can change).
            if let tomorrow = Calendar.current.date(byAdding: .day, value: 1, to: Date()) {
                var comps = Calendar.current.dateComponents([.year, .month, .day], from: tomorrow)
                comps.hour = 21
                comps.minute = 0
                if let fire = Calendar.current.date(from: comps) {
                    item.setFireAtDate(fire)
                }
            }
            return item
        }
    }

    /// Compact row summary — time / interval only (no IoT / thermostat copy).
    func scheduleSummaryLine(localization: LocalizationManager) -> String {
        switch mode {
        case .window:
            let interval = FamilyHabitCustomInterval.intervalLabel(
                minutes: intervalMinutes,
                localization: localization
            )
            return "\(interval) · \(windowTimeRangeLabel)"
        case .onceDaily:
            return String(format: "%02d:%02d", hour, minute)
        case .onceAt:
            if let fireAt, !fireAt.isEmpty {
                return fireAt
            }
            return localization.localized("family_habit_custom_once_at_needs_date")
        }
    }

    var windowTimeRangeLabel: String {
        String(format: "%02d:%02d–%02d:%02d", hour, minute, endHour, endMinute)
    }

    /// Apply chip or free minutes (clamped) — for interval picker binding.
    mutating func setIntervalMinutes(_ minutes: Int) {
        intervalMinutes = FamilyHabitCustomInterval.clampMinutes(minutes)
    }

    /// Short health-like disclaimer when title looks like medicine (fhc-05).
    var needsHealthDisclaimer: Bool {
        let lowered = title.lowercased()
        let keys = [
            "лекар", "таблет", "medicine", "pill", "vitamin", "витамин",
            "insulin", "инсулин", "dose", "доза", "аспирин", "aspirin"
        ]
        return keys.contains { lowered.contains($0) }
    }

    /// Emoji chips for the custom editor (not system presets).
    static let editorEmojiChoices = ["⭐️", "📞", "💪", "🚪", "☕", "📚", "🧹", "🧘", "🦷", "🎧"]

    /// Slot times for `window` mode (cap 12). Step = clamped interval (15…180).
    func windowNotificationSlots(maxSlots: Int = maxSlotsPerDay) -> [(hour: Int, minute: Int)] {
        let start = hour * 60 + minute
        var end = endHour * 60 + endMinute
        if end <= start {
            end += 24 * 60
        }
        let step = FamilyHabitCustomInterval.clampMinutes(intervalMinutes)
        var slots: [(Int, Int)] = []
        var t = start
        while t <= end && slots.count < maxSlots {
            let wrapped = t % (24 * 60)
            slots.append((wrapped / 60, wrapped % 60))
            t += step
        }
        if slots.isEmpty {
            slots.append((hour, minute))
        }
        return slots
    }

    /// Keep at most `maxPerFamily`, drop empty titles, clamp each row, stable sort_order.
    static func normalizedList(_ items: [FamilyHabitCustomReminder]) -> [FamilyHabitCustomReminder] {
        var result: [FamilyHabitCustomReminder] = []
        result.reserveCapacity(min(items.count, maxPerFamily))
        for (index, item) in items.enumerated() {
            var row = item.clamped()
            guard !row.title.isEmpty else { continue }
            if row.sortOrder == 0 {
                row.sortOrder = index
            }
            result.append(row)
            if result.count >= maxPerFamily { break }
        }
        return result.sorted { lhs, rhs in
            if lhs.sortOrder != rhs.sortOrder { return lhs.sortOrder < rhs.sortOrder }
            return lhs.id < rhs.id
        }
    }

    private static func firstGrapheme(_ value: String) -> String? {
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }
        let range = trimmed.rangeOfComposedCharacterSequence(at: trimmed.startIndex)
        return String(trimmed[range])
    }
}

/// fhc-06 — quick templates for new custom reminders (not the 4 system presets; not medicine).
enum FamilyHabitCustomQuickTemplate: String, CaseIterable, Identifiable {
    case call
    case stretch
    case door
    case breakTime = "break"
    case read
    case tidy

    var id: String { rawValue }

    var emoji: String {
        switch self {
        case .call: return "📞"
        case .stretch: return "💪"
        case .door: return "🚪"
        case .breakTime: return "☕"
        case .read: return "📚"
        case .tidy: return "🧹"
        }
    }

    var titleKey: String { "family_habit_custom_tpl_\(rawValue)" }

    /// Prefill title + emoji only — schedule stays as-is until user edits / Save.
    func apply(to draft: inout FamilyHabitCustomReminder, localization: LocalizationManager) {
        draft.title = localization.localized(titleKey)
        draft.emoji = emoji
    }
}

struct FamilyHabitRemindersConfig: Codable, Equatable {
    var presets: [String: FamilyHabitPresetSchedule]
    var memberIds: [String]
    /// fhc-01 — user custom reminders (max 5). Absent in legacy JSON → `[]`.
    var custom: [FamilyHabitCustomReminder]

    enum CodingKeys: String, CodingKey {
        case presets
        case memberIds = "member_ids"
        case custom
    }

    init(
        presets: [String: FamilyHabitPresetSchedule],
        memberIds: [String],
        custom: [FamilyHabitCustomReminder] = []
    ) {
        self.presets = presets
        self.memberIds = memberIds
        self.custom = FamilyHabitCustomReminder.normalizedList(custom)
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        presets = try c.decodeIfPresent([String: FamilyHabitPresetSchedule].self, forKey: .presets) ?? [:]
        memberIds = try c.decodeIfPresent([String].self, forKey: .memberIds) ?? []
        let rawCustom = try c.decodeIfPresent([FamilyHabitCustomReminder].self, forKey: .custom) ?? []
        custom = FamilyHabitCustomReminder.normalizedList(rawCustom)
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(presets, forKey: .presets)
        try c.encode(memberIds, forKey: .memberIds)
        try c.encode(FamilyHabitCustomReminder.normalizedList(custom), forKey: .custom)
    }

    static let empty = FamilyHabitRemindersConfig(
        presets: FamilyHabitPresetId.allCases.reduce(into: [:]) { acc, preset in
            acc[preset.rawValue] = FamilyHabitPresetSchedule.defaultsMap()[preset] ?? .default
        },
        memberIds: [],
        custom: []
    )

    func schedule(for preset: FamilyHabitPresetId) -> FamilyHabitPresetSchedule {
        presets[preset.rawValue] ?? FamilyHabitPresetSchedule.defaultsMap()[preset] ?? .default
    }

    mutating func setSchedule(_ schedule: FamilyHabitPresetSchedule, for preset: FamilyHabitPresetId) {
        presets[preset.rawValue] = schedule
    }

    /// Re-apply clamp / max-5 / drop empty titles (call before save).
    mutating func normalizeCustom() {
        custom = FamilyHabitCustomReminder.normalizedList(custom)
    }
}

struct FamilyHabitRemindersResponse: Codable, Equatable {
    let familyId: String?
    let config: FamilyHabitRemindersConfig
    let configured: Bool
    let updatedAt: String?

    enum CodingKeys: String, CodingKey {
        case familyId = "family_id"
        case config
        case configured
        case updatedAt = "updated_at"
    }
}

struct FamilyHabitRemindersSaveResponse: Codable, Equatable {
    let familyId: String?
    let config: FamilyHabitRemindersConfig
    let configured: Bool
    let updatedAt: String?

    enum CodingKeys: String, CodingKey {
        case familyId = "family_id"
        case config
        case configured
        case updatedAt = "updated_at"
    }
}

enum FamilyHabitRemindersPolicy {
    /// Local: this phone wants habit pushes for the signed-in member (parents default ON).
    static let remindOnThisDeviceKey = "family_habit_remind_on_this_device_v1"

    /// Empty `member_ids` → minors + elderly on their devices.
    /// Parent / unknown on this phone → only if `remindOnThisDevice` (each adult configures for self).
    /// Non-empty `member_ids` → only listed members (may include parents).
    static func remindOnThisDevice(defaults: UserDefaults = .standard) -> Bool {
        if defaults.object(forKey: remindOnThisDeviceKey) == nil {
            return true
        }
        return defaults.bool(forKey: remindOnThisDeviceKey)
    }

    static func setRemindOnThisDevice(_ enabled: Bool, defaults: UserDefaults = .standard) {
        defaults.set(enabled, forKey: remindOnThisDeviceKey)
    }

    static func shouldReceiveReminders(
        config: FamilyHabitRemindersConfig,
        members: [FamilyMemberData],
        defaults: UserDefaults = .standard
    ) -> Bool {
        let myMemberId = (defaults.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)

        // No member id yet (fresh install / before family sync): still honor
        // «на этом телефоне» so water/medicine match WindDown reliability.
        if myMemberId.isEmpty {
            return remindOnThisDevice(defaults: defaults)
        }

        if !config.memberIds.isEmpty {
            return config.memberIds.contains(where: { id in
                matchesMember(id: id, myMemberId: myMemberId, members: members)
            })
        }

        let role = FamilyAccessPolicy.resolveActorRole(members: members, defaults: defaults)
        switch role {
        case .child, .teenager, .elderly:
            return true
        case .parent, .unknown:
            return remindOnThisDevice(defaults: defaults)
        }
    }

    private static func matchesMember(
        id: String,
        myMemberId: String,
        members: [FamilyMemberData]
    ) -> Bool {
        if id == myMemberId { return true }
        return members.contains { member in
            let sid = member.serverMemberId?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            let canon = member.canonicalId.trimmingCharacters(in: .whitespacesAndNewlines)
            let rid = member.id.trimmingCharacters(in: .whitespacesAndNewlines)
            return sid == id || canon == id || rid == id || sid == myMemberId || canon == myMemberId
        }
    }
}

struct WellnessHabitCreateResponse: Codable, Equatable {
    let ok: Bool?
}
