import XCTest
@testable import ALADDIN

final class FamilyHabitRemindersPolicyTests: XCTestCase {
    private let testDefaultsSuite = "FamilyHabitRemindersPolicyTests.\(UUID().uuidString)"

    private func makeDefaults() -> UserDefaults {
        let defaults = UserDefaults(suiteName: testDefaultsSuite)!
        defaults.removePersistentDomain(forName: testDefaultsSuite)
        return defaults
    }

    func testEmptyMemberIdsTargetsMinorsOnly() {
        let teen = FamilyMemberData(
            id: "teen-1",
            serverMemberId: "teen-1",
            name: "Teen",
            role: .teenager,
            avatar: "🧒",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
        let config = FamilyHabitRemindersConfig.empty
        let defaults = makeDefaults()
        defaults.set("teen-1", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)

        XCTAssertTrue(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: config,
                members: [teen],
                defaults: defaults
            )
        )
    }

    func testParentReceivesWhenRemindOnThisDeviceDefault() {
        let parent = FamilyMemberData(
            id: "parent-1",
            serverMemberId: "parent-1",
            name: "Parent",
            role: .parent,
            avatar: "👨",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
        let defaults = makeDefaults()
        defaults.set("parent-1", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        // key unset → default ON

        XCTAssertTrue(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: FamilyHabitRemindersConfig.empty,
                members: [parent],
                defaults: defaults
            )
        )
    }

    func testParentExcludedWhenRemindOnThisDeviceOff() {
        let parent = FamilyMemberData(
            id: "parent-1",
            serverMemberId: "parent-1",
            name: "Parent",
            role: .parent,
            avatar: "👨",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
        let defaults = makeDefaults()
        defaults.set("parent-1", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        FamilyHabitRemindersPolicy.setRemindOnThisDevice(false, defaults: defaults)

        XCTAssertFalse(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: FamilyHabitRemindersConfig.empty,
                members: [parent],
                defaults: defaults
            )
        )
    }

    func testParentIncludedWhenListedInMemberIds() {
        let parent = FamilyMemberData(
            id: "parent-1",
            serverMemberId: "parent-1",
            name: "Parent",
            role: .parent,
            avatar: "👨",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
        let defaults = makeDefaults()
        defaults.set("parent-1", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        FamilyHabitRemindersPolicy.setRemindOnThisDevice(false, defaults: defaults)
        var config = FamilyHabitRemindersConfig.empty
        config.memberIds = ["parent-1"]

        XCTAssertTrue(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: config,
                members: [parent],
                defaults: defaults
            )
        )
    }

    func testWaterSlotsAcrossWindow() {
        let schedule = FamilyHabitPresetSchedule(
            enabled: true,
            hour: 9,
            minute: 0,
            endHour: 15,
            endMinute: 0,
            intervalMinutes: 120,
            dailyLiters: 2.0
        )
        let slots = schedule.waterNotificationSlots()
        XCTAssertEqual(slots.map { "\($0.hour):\($0.minute)" }, ["9:0", "11:0", "13:0", "15:0"])
    }

    func testWaterLegacyDecodeDefaultsPingOff() throws {
        let json = """
        {"enabled":true,"hour":10,"minute":30}
        """.data(using: .utf8)!
        let decoded = try JSONDecoder().decode(FamilyHabitPresetSchedule.self, from: json)
        XCTAssertTrue(decoded.enabled)
        XCTAssertEqual(decoded.hour, 10)
        XCTAssertEqual(decoded.endHour, 21)
        XCTAssertEqual(decoded.intervalMinutes, 120)
        XCTAssertEqual(decoded.dailyLiters, 2.0, accuracy: 0.01)
        XCTAssertFalse(decoded.pingUntilDone)
        XCTAssertEqual(decoded.pingIntervalMinutes, 20)
        XCTAssertEqual(decoded.pingMaxPerDay, 6)
    }

    func testPingIntervalClamped15to30() {
        let low = FamilyHabitPresetSchedule(
            enabled: true, hour: 9, minute: 0,
            pingUntilDone: true, pingIntervalMinutes: 5, pingMaxPerDay: 6
        )
        XCTAssertEqual(low.pingIntervalMinutes, 15)
        let high = FamilyHabitPresetSchedule(
            enabled: true, hour: 9, minute: 0,
            pingUntilDone: true, pingIntervalMinutes: 90, pingMaxPerDay: 6
        )
        XCTAssertEqual(high.pingIntervalMinutes, 30)
    }

    func testWaterDefaultPingOffInDefaultsMap() {
        let water = FamilyHabitPresetSchedule.defaultsMap()[.water]!
        XCTAssertFalse(water.pingUntilDone)
    }

    func testNoShowGraceClampAndCheckTime() {
        XCTAssertEqual(GeofenceNoShowSchedule.clampGrace(5), 15)
        XCTAssertEqual(GeofenceNoShowSchedule.clampGrace(45), 30)
        let schedule = GeofenceNoShowSchedule(
            placeName: "School",
            hour: 8,
            minute: 30,
            graceMinutes: 15
        )
        let check = schedule.checkHourMinute()
        XCTAssertEqual(check.hour, 8)
        XCTAssertEqual(check.minute, 45)
        let late = GeofenceNoShowSchedule(
            placeName: "School",
            hour: 8,
            minute: 50,
            graceMinutes: 30
        )
        let check2 = late.checkHourMinute()
        XCTAssertEqual(check2.hour, 9)
        XCTAssertEqual(check2.minute, 20)
    }

    func testMedicineDefaultSlotExists() {
        let medicine = FamilyHabitPresetSchedule.defaultsMap()[.medicine]!
        XCTAssertEqual(medicine.hour, 9)
        XCTAssertEqual(medicine.minute, 0)
        XCTAssertEqual(medicine.endHour, 21)
        XCTAssertEqual(medicine.intervalMinutes, 180)
        XCTAssertTrue(medicine.pingUntilDone)
    }

    func testMedicineWindowSlotsLikeWater() {
        let schedule = FamilyHabitPresetSchedule(
            enabled: true,
            hour: 9,
            minute: 0,
            endHour: 23,
            endMinute: 0,
            intervalMinutes: 120,
            dailyLiters: 2.0
        )
        let slots = schedule.windowNotificationSlots()
        XCTAssertEqual(slots.first?.hour, 9)
        XCTAssertEqual(slots.last?.hour, 23)
        XCTAssertGreaterThanOrEqual(slots.count, 7)
    }

    func testPolicyAllowsEmptyMemberIdWhenRemindOnThisDevice() {
        let defaults = makeDefaults()
        FamilyHabitRemindersPolicy.setRemindOnThisDevice(true, defaults: defaults)
        defaults.removeObject(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        XCTAssertTrue(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: FamilyHabitRemindersConfig.empty,
                members: [],
                defaults: defaults
            )
        )
        FamilyHabitRemindersPolicy.setRemindOnThisDevice(false, defaults: defaults)
        XCTAssertFalse(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: FamilyHabitRemindersConfig.empty,
                members: [],
                defaults: defaults
            )
        )
    }

    func testHasUserScheduledTimesDetectsCustomHour() {
        var config = FamilyHabitRemindersConfig.empty
        XCTAssertFalse(FamilyHabitRemindersService.hasUserScheduledTimes(config))
        var water = config.schedule(for: .water)
        water.hour = 16
        water.minute = 30
        config.setSchedule(water, for: .water)
        XCTAssertTrue(FamilyHabitRemindersService.hasUserScheduledTimes(config))
    }

    func testMergeWindowFieldsKeepsLocalCustomStart() {
        var local = FamilyHabitRemindersConfig.empty
        var water = local.schedule(for: .water)
        water.enabled = true
        water.hour = 16
        water.minute = 30
        water.endHour = 23
        local.setSchedule(water, for: .water)

        var server = FamilyHabitRemindersConfig.empty
        var serverWater = server.schedule(for: .water)
        serverWater.enabled = true
        serverWater.hour = 9
        serverWater.minute = 0
        server.setSchedule(serverWater, for: .water)

        let merged = FamilyHabitRemindersService.mergeWindowFields(server: server, local: local)
        XCTAssertEqual(merged.schedule(for: .water).hour, 16)
        XCTAssertEqual(merged.schedule(for: .water).minute, 30)
    }
}

// MARK: - fhc-01 Custom habit model

final class FamilyHabitCustomReminderTests: XCTestCase {
    private func makeDefaults() -> UserDefaults {
        let suite = "FamilyHabitCustomReminderTests.\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suite)!
        defaults.removePersistentDomain(forName: suite)
        return defaults
    }

    func testLegacyConfigDecodeWithoutCustom() throws {
        let json = """
        {"presets":{},"member_ids":["m1"]}
        """.data(using: .utf8)!
        let decoded = try JSONDecoder().decode(FamilyHabitRemindersConfig.self, from: json)
        XCTAssertEqual(decoded.memberIds, ["m1"])
        XCTAssertTrue(decoded.custom.isEmpty)
    }

    func testCustomRoundTrip() throws {
        var config = FamilyHabitRemindersConfig.empty
        config.custom = [
            FamilyHabitCustomReminder(
                id: "c1",
                title: "Позвонить маме",
                emoji: "📞",
                enabled: true,
                mode: .onceDaily,
                hour: 20,
                minute: 30,
                sortOrder: 1
            )
        ]
        let data = try JSONEncoder().encode(config)
        let decoded = try JSONDecoder().decode(FamilyHabitRemindersConfig.self, from: data)
        XCTAssertEqual(decoded.custom.count, 1)
        XCTAssertEqual(decoded.custom[0].id, "c1")
        XCTAssertEqual(decoded.custom[0].title, "Позвонить маме")
        XCTAssertEqual(decoded.custom[0].emoji, "📞")
        XCTAssertEqual(decoded.custom[0].mode, .onceDaily)
        XCTAssertTrue(decoded.custom[0].modeRecognized)
        XCTAssertEqual(decoded.custom[0].hour, 20)
        XCTAssertEqual(decoded.custom[0].minute, 30)
    }

    func testTitleClampAndEmptyDrop() {
        let long = String(repeating: "a", count: 50)
        let clamped = FamilyHabitCustomReminder(title: "  \(long)  ").clamped()
        XCTAssertEqual(clamped.title.count, FamilyHabitCustomReminder.titleMaxLength)

        let list = FamilyHabitCustomReminder.normalizedList([
            FamilyHabitCustomReminder(title: "   "),
            FamilyHabitCustomReminder(id: "ok", title: "Зарядка", sortOrder: 2)
        ])
        XCTAssertEqual(list.count, 1)
        XCTAssertEqual(list[0].id, "ok")
    }

    func testMaxFiveCustom() {
        let items = (0..<8).map { i in
            FamilyHabitCustomReminder(id: "id-\(i)", title: "Item \(i)", sortOrder: i)
        }
        let normalized = FamilyHabitCustomReminder.normalizedList(items)
        XCTAssertEqual(normalized.count, FamilyHabitCustomReminder.maxPerFamily)
        XCTAssertEqual(normalized.map(\.id), ["id-0", "id-1", "id-2", "id-3", "id-4"])
    }

    func testIntervalClamp15to180() {
        let low = FamilyHabitCustomReminder(title: "A", intervalMinutes: 5)
        XCTAssertEqual(low.intervalMinutes, 15)
        let high = FamilyHabitCustomReminder(title: "B", intervalMinutes: 999)
        XCTAssertEqual(high.intervalMinutes, 180)
    }

    func testUnknownModeDoesNotCrashAndSkipsSchedule() throws {
        let json = """
        {
          "id":"x1",
          "title":"Test",
          "emoji":"⭐️",
          "enabled":true,
          "mode":"weekly_rrule",
          "hour":10,
          "minute":0
        }
        """.data(using: .utf8)!
        let decoded = try JSONDecoder().decode(FamilyHabitCustomReminder.self, from: json)
        XCTAssertFalse(decoded.modeRecognized)
        XCTAssertEqual(decoded.unrecognizedModeRaw, "weekly_rrule")
        XCTAssertFalse(decoded.shouldScheduleLocally)

        let encoded = try JSONEncoder().encode(decoded)
        let again = try JSONDecoder().decode(FamilyHabitCustomReminder.self, from: encoded)
        XCTAssertFalse(again.modeRecognized)
        XCTAssertEqual(again.unrecognizedModeRaw, "weekly_rrule")
    }

    func testOnceAtPastNotSchedulableFutureIs() {
        let past = FamilyHabitCustomReminder(
            title: "Вторник",
            mode: .onceAt,
            fireAt: "2020-01-01T12:00:00Z"
        )
        XCTAssertEqual(past.mode, .onceAt)
        XCTAssertFalse(past.shouldScheduleLocally)
        XCTAssertTrue(past.onceAtIsPast)

        var future = FamilyHabitCustomReminder(title: "Soon", mode: .onceAt)
        let fire = Date().addingTimeInterval(3600)
        future.setFireAtDate(fire)
        XCTAssertTrue(future.shouldScheduleLocally)
        XCTAssertFalse(future.onceAtIsPast)
        XCTAssertEqual(
            FamilyHabitRemindersScheduler.customOnceAtIdentifier(id: future.id),
            "family.habit.custom.\(future.id).at"
        )
    }

    func testReorderSortOrderPersists() {
        var list = [
            FamilyHabitCustomReminder(id: "a", title: "A", sortOrder: 0),
            FamilyHabitCustomReminder(id: "b", title: "B", sortOrder: 1),
            FamilyHabitCustomReminder(id: "c", title: "C", sortOrder: 2)
        ]
        list.swapAt(0, 1)
        for i in list.indices { list[i].sortOrder = i }
        let normalized = FamilyHabitCustomReminder.normalizedList(list)
        XCTAssertEqual(normalized.map(\.id), ["b", "a", "c"])
    }

    func testAnalyticsParamsNeverIncludeTitle() {
        let params = FamilyHabitCustomAnalytics.parameters(id: "abc", mode: "once_daily")
        XCTAssertEqual(Set(params.keys), Set(["id", "mode"]))
        XCTAssertFalse(params.keys.contains("title"))
        XCTAssertEqual(params["id"], "abc")
        for event in [
            FamilyHabitCustomAnalytics.Event.create,
            .done, .edit, .delete, .testPush
        ] {
            XCTAssertFalse(event.rawValue.contains("title"))
        }
    }

    func testWindowSlotsCap12() {
        let item = FamilyHabitCustomReminder(
            title: "Вода своя",
            mode: .window,
            hour: 8,
            minute: 0,
            endHour: 22,
            endMinute: 0,
            intervalMinutes: 15
        )
        let slots = item.windowNotificationSlots()
        XCTAssertEqual(slots.count, FamilyHabitCustomReminder.maxSlotsPerDay)
        XCTAssertEqual(slots.first?.hour, 8)
        XCTAssertTrue(item.shouldScheduleLocally)
    }

    func testEmptyConfigCustomDefault() {
        XCTAssertTrue(FamilyHabitRemindersConfig.empty.custom.isEmpty)
    }

    // MARK: fhc-02 intervals

    func testCustomIntervalNearestAndChips() {
        XCTAssertEqual(FamilyHabitCustomInterval.nearest(14), .minutes15)
        XCTAssertEqual(FamilyHabitCustomInterval.nearest(22), .minutes15)
        XCTAssertEqual(FamilyHabitCustomInterval.nearest(40), .minutes30)
        XCTAssertEqual(FamilyHabitCustomInterval.nearest(70), .minutes60)
        XCTAssertEqual(FamilyHabitCustomInterval.nearest(100), .minutes120)
        XCTAssertEqual(FamilyHabitCustomInterval.nearest(200), .minutes120)
        XCTAssertTrue(FamilyHabitCustomInterval.isChipValue(30))
        XCTAssertFalse(FamilyHabitCustomInterval.isChipValue(45))
        let custom = FamilyHabitCustomInterval.selection(for: 45)
        XCTAssertTrue(custom.isCustom)
        XCTAssertEqual(custom.chip, .minutes30)
        let chip = FamilyHabitCustomInterval.selection(for: 60)
        XCTAssertFalse(chip.isCustom)
        XCTAssertEqual(chip.chip, .minutes60)
    }

    func testCustomIntervalClampMinutes() {
        XCTAssertEqual(FamilyHabitCustomInterval.clampMinutes(5), 15)
        XCTAssertEqual(FamilyHabitCustomInterval.clampMinutes(45), 45)
        XCTAssertEqual(FamilyHabitCustomInterval.clampMinutes(999), 180)
    }

    func testPrefillWindowAndOnceDaily() {
        let window = FamilyHabitCustomReminder.prefill(mode: .window, title: "Зарядка")
        XCTAssertEqual(window.mode, .window)
        XCTAssertEqual(window.hour, 9)
        XCTAssertEqual(window.endHour, 21)
        XCTAssertEqual(window.intervalMinutes, 60)

        let once = FamilyHabitCustomReminder.prefill(mode: .onceDaily, title: "Позвонить")
        XCTAssertEqual(once.mode, .onceDaily)
        XCTAssertEqual(once.hour, 21)
        XCTAssertEqual(once.minute, 0)
    }

    func testScheduleSummaryLineClean() {
        let loc = LocalizationManager.shared
        let window = FamilyHabitCustomReminder.prefill(mode: .window, title: "X")
        let summary = window.scheduleSummaryLine(localization: loc)
        XCTAssertTrue(summary.contains("09:00"), summary)
        XCTAssertTrue(summary.contains("21:00"), summary)
        XCTAssertTrue(summary.contains("·"), summary)
        XCTAssertFalse(summary.localizedCaseInsensitiveContains("thermostat"))
        XCTAssertFalse(summary.localizedCaseInsensitiveContains("термостат"))
        XCTAssertFalse(summary.localizedCaseInsensitiveContains("камера"))

        var customMins = FamilyHabitCustomReminder.prefill(mode: .window, title: "Y")
        customMins.setIntervalMinutes(45)
        let customSummary = customMins.scheduleSummaryLine(localization: loc)
        XCTAssertTrue(customSummary.contains("45"))
        XCTAssertTrue(customSummary.contains("·"))

        let daily = FamilyHabitCustomReminder.prefill(mode: .onceDaily, title: "Z")
        XCTAssertEqual(daily.scheduleSummaryLine(localization: loc), "21:00")
    }

    // MARK: fhc-03 scheduler ids

    func testCustomNotificationIdentifiers() {
        let id = "abc-123"
        XCTAssertEqual(FamilyHabitRemindersScheduler.customPresetRaw(id: id), "custom.abc-123")
        XCTAssertEqual(FamilyHabitRemindersScheduler.customDailyIdentifier(id: id), "family.habit.custom.abc-123")
        XCTAssertEqual(FamilyHabitRemindersScheduler.customSlotPrefix(id: id), "family.habit.custom.abc-123.")
        XCTAssertEqual(FamilyHabitRemindersScheduler.customId(fromPresetRaw: "custom.abc-123"), "abc-123")
        XCTAssertNil(FamilyHabitRemindersScheduler.customId(fromPresetRaw: "water"))
    }

    func testPendingIdentifierMatchesCustomAndDue() {
        let preset = "custom.abc-123"
        XCTAssertTrue(
            FamilyHabitRemindersScheduler.pendingIdentifier(
                "family.habit.custom.abc-123",
                matchesPresetRaw: preset
            )
        )
        XCTAssertTrue(
            FamilyHabitRemindersScheduler.pendingIdentifier(
                "family.habit.custom.abc-123.0",
                matchesPresetRaw: preset
            )
        )
        XCTAssertTrue(
            FamilyHabitRemindersScheduler.pendingIdentifier(
                "family.habit.custom.abc-123.due.1",
                matchesPresetRaw: preset
            )
        )
        XCTAssertFalse(
            FamilyHabitRemindersScheduler.pendingIdentifier(
                "family.habit.custom.other.0",
                matchesPresetRaw: preset
            )
        )
        XCTAssertTrue(
            FamilyHabitRemindersScheduler.pendingIdentifier(
                "family.habit.water.0",
                matchesPresetRaw: "water"
            )
        )
    }

    func testOnceAtPrefillSchedulesFutureAndPendingId() {
        let item = FamilyHabitCustomReminder.prefill(mode: .onceAt, title: "Вторник")
        XCTAssertTrue(item.shouldScheduleLocally)
        XCTAssertNotNil(item.fireAtDate)
        XCTAssertTrue(
            FamilyHabitRemindersScheduler.pendingIdentifier(
                FamilyHabitRemindersScheduler.customOnceAtIdentifier(id: item.id),
                matchesPresetRaw: FamilyHabitRemindersScheduler.customPresetRaw(id: item.id)
            )
        )
        XCTAssertTrue(FamilyHabitCustomReminder.prefill(mode: .window, title: "X").shouldScheduleLocally)
        XCTAssertTrue(FamilyHabitCustomReminder.prefill(mode: .onceDaily, title: "Y").shouldScheduleLocally)
    }

    func testCustomDeepLinkDonePreset() {
        let link = UnicornDeepLinkRouter.habitReminderDeepLink(preset: "custom.abc-123")
        XCTAssertTrue(link.contains("habit"))
        XCTAssertTrue(link.contains("done"))
        XCTAssertTrue(link.contains("preset=custom.abc-123"))
        let url = URL(string: link)!
        XCTAssertEqual(
            UnicornDeepLinkRouter.parse(url),
            .habitDone(preset: "custom.abc-123")
        )
    }

    // MARK: fhc-04 deep link + Done

    func testParseCustomDoneDeepLink() {
        let url = URL(string: "aladdin://habit/done?preset=custom.abc-123")!
        XCTAssertEqual(
            UnicornDeepLinkRouter.parse(url),
            .habitDone(preset: "custom.abc-123")
        )
    }

    func testParseMalformedCustomDoneOpensFamilyNotDone() {
        let url = URL(string: "aladdin://habit/done?preset=custom.")!
        XCTAssertEqual(UnicornDeepLinkRouter.parse(url), .familyHabits)
        XCTAssertNil(UnicornDeepLinkRouter.normalizedDonePreset("custom."))
        XCTAssertNil(UnicornDeepLinkRouter.normalizedDonePreset("custom.   "))
    }

    func testParseCustomPathWithoutDoneOpensFamily() {
        let url = URL(string: "aladdin://habit/custom.abc-123")!
        XCTAssertEqual(UnicornDeepLinkRouter.parse(url), .familyHabits)
    }

    func testHabitPresetFromUserInfoPrefersPresetThenDeepLink() {
        let fromPreset = UnicornDeepLinkRouter.habitPreset(fromUserInfo: [
            "preset": "custom.abc-123",
            "deepLink": "aladdin://habit/done?preset=custom.other"
        ])
        XCTAssertEqual(fromPreset, "custom.abc-123")

        let fromDeepLink = UnicornDeepLinkRouter.habitPreset(fromUserInfo: [
            "deepLink": "aladdin://habit/done?preset=custom.xyz"
        ])
        XCTAssertEqual(fromDeepLink, "custom.xyz")

        XCTAssertNil(UnicornDeepLinkRouter.habitPreset(fromUserInfo: [
            "preset": "custom."
        ]))
    }

    func testCustomAnalyticsParamsHaveNoTitleKey() {
        // Hook compiles; fhc-17 wires full facade. Ensure API surface is id/mode only.
        FamilyHabitCustomAnalytics.log(.done, id: "abc-123", mode: "once_daily")
        FamilyHabitCustomAnalytics.log(.create, id: "abc-123", mode: "window")
        XCTAssertEqual(FamilyHabitCustomAnalytics.Event.done.rawValue, "family_habit_custom_done")
    }

    // MARK: fhc-05 health disclaimer + merge preserves custom

    func testHealthDisclaimerKeywords() {
        XCTAssertTrue(FamilyHabitCustomReminder(title: "Лекарство вечером").needsHealthDisclaimer)
        XCTAssertTrue(FamilyHabitCustomReminder(title: "Take vitamin D").needsHealthDisclaimer)
        XCTAssertFalse(FamilyHabitCustomReminder(title: "Позвонить маме").needsHealthDisclaimer)
    }

    func testMergeWindowFieldsPreservesLocalCustom() {
        var local = FamilyHabitRemindersConfig.empty
        local.custom = [
            FamilyHabitCustomReminder(id: "c1", title: "Зарядка", mode: .onceDaily)
        ]
        let server = FamilyHabitRemindersConfig.empty
        let merged = FamilyHabitRemindersService.mergeWindowFields(server: server, local: local)
        XCTAssertEqual(merged.custom.count, 1)
        XCTAssertEqual(merged.custom[0].id, "c1")
    }

    // MARK: fhc-06 quick templates

    func testQuickTemplatesPrefillTitleEmojiOnly() {
        var draft = FamilyHabitCustomReminder.prefill(mode: .window, title: "")
        draft.hour = 10
        draft.minute = 15
        draft.intervalMinutes = 30
        let beforeHour = draft.hour
        let beforeInterval = draft.intervalMinutes
        FamilyHabitCustomQuickTemplate.call.apply(
            to: &draft,
            localization: LocalizationManager.shared
        )
        XCTAssertFalse(draft.title.isEmpty)
        XCTAssertEqual(draft.emoji, "📞")
        XCTAssertEqual(draft.hour, beforeHour)
        XCTAssertEqual(draft.intervalMinutes, beforeInterval)
        XCTAssertEqual(draft.mode, .window)
    }

    func testQuickTemplatesAreNotSystemPresetsOrMedicine() {
        let ids = Set(FamilyHabitCustomQuickTemplate.allCases.map(\.rawValue))
        for preset in FamilyHabitPresetId.allCases {
            XCTAssertFalse(ids.contains(preset.rawValue), "template collides with system preset \(preset.rawValue)")
        }
        XCTAssertFalse(ids.contains("medicine"))
        XCTAssertFalse(ids.contains("water"))
        let loc = LocalizationManager.shared
        for template in FamilyHabitCustomQuickTemplate.allCases {
            let title = loc.localized(template.titleKey).lowercased()
            XCTAssertFalse(title.contains("medicine"))
            XCTAssertFalse(title.contains("лекар"))
            XCTAssertFalse(FamilyHabitCustomReminder(title: title).needsHealthDisclaimer)
        }
        XCTAssertEqual(FamilyHabitCustomQuickTemplate.allCases.count, 6)
    }

    // MARK: fhc-08 sync body + soft-fail

    func testHabitRemindersBodyEncodesCustom() throws {
        var config = FamilyHabitRemindersConfig.empty
        config.custom = [
            FamilyHabitCustomReminder(id: "c1", title: "Call", mode: .onceDaily, hour: 20, minute: 0)
        ]
        let body = FamilyHabitRemindersService.HabitRemindersBody(from: config)
        let data = try JSONEncoder().encode(body)
        let json = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        XCTAssertNotNil(json["presets"])
        XCTAssertNotNil(json["member_ids"])
        let custom = try XCTUnwrap(json["custom"] as? [[String: Any]])
        XCTAssertEqual(custom.count, 1)
        XCTAssertEqual(custom[0]["id"] as? String, "c1")
        XCTAssertEqual(custom[0]["title"] as? String, "Call")
    }

    func testConfigAfterSyncFailureNeverEmptyWhenHadCustom() {
        var previous = FamilyHabitRemindersConfig.empty
        previous.custom = [FamilyHabitCustomReminder(id: "old", title: "Old", mode: .onceDaily)]
        var attempted = FamilyHabitRemindersConfig.empty
        attempted.custom = [FamilyHabitCustomReminder(id: "new", title: "New", mode: .window)]
        var water = attempted.schedule(for: .water)
        water.enabled = true
        attempted.setSchedule(water, for: .water)

        let kept = FamilyHabitRemindersService.configAfterSyncFailure(
            previous: previous,
            attempted: attempted
        )
        XCTAssertFalse(kept.custom.isEmpty)
        XCTAssertEqual(kept.custom[0].id, "new")
        XCTAssertTrue(kept.schedule(for: .water).enabled)
        XCTAssertNotEqual(kept, FamilyHabitRemindersConfig.empty)
    }

    func testSyncErrorKeyForPermanentWithCustom() {
        let err = NetworkError.badRequest(nil)
        XCTAssertEqual(
            FamilyHabitRemindersService.syncErrorKey(for: err, hadCustom: true),
            "family_habit_custom_server_outdated"
        )
        XCTAssertEqual(
            FamilyHabitRemindersService.syncErrorKey(for: err, hadCustom: false),
            "family_habit_custom_sync_failed"
        )
        XCTAssertEqual(
            FamilyHabitRemindersService.syncErrorKey(for: NetworkError.httpError(422), hadCustom: true),
            "family_habit_custom_server_outdated"
        )
        XCTAssertEqual(
            FamilyHabitRemindersService.syncErrorKey(for: NetworkError.timeout, hadCustom: true),
            "family_habit_custom_sync_failed"
        )
    }

    // MARK: fhc-10 — gate coverage (clamp / slots / legacy / soft-fail / policy)

    func testWindowSixtyMinuteSlotsExactThenCap() {
        let window60 = FamilyHabitCustomReminder(
            title: "Stretch",
            mode: .window,
            hour: 9,
            minute: 0,
            endHour: 15,
            endMinute: 0,
            intervalMinutes: 60
        )
        let slots = window60.windowNotificationSlots()
        XCTAssertEqual(slots.count, 7) // 09…15 inclusive
        XCTAssertEqual(slots.first?.hour, 9)
        XCTAssertEqual(slots.last?.hour, 15)

        let wide = FamilyHabitCustomReminder(
            title: "Wide",
            mode: .window,
            hour: 9,
            minute: 0,
            endHour: 21,
            endMinute: 0,
            intervalMinutes: 60
        )
        XCTAssertEqual(wide.windowNotificationSlots().count, FamilyHabitCustomReminder.maxSlotsPerDay)
    }

    func testOnceDailySchedulableSingleTime() {
        let daily = FamilyHabitCustomReminder(
            id: "d1",
            title: "Call mom",
            mode: .onceDaily,
            hour: 20,
            minute: 30
        )
        XCTAssertTrue(daily.shouldScheduleLocally)
        XCTAssertEqual(daily.scheduleSummaryLine(localization: LocalizationManager.shared), "20:30")
        // once_daily is not a window — slots helper still returns at least start if called
        XCTAssertFalse(daily.windowNotificationSlots().isEmpty)

        var disabled = daily
        disabled.enabled = false
        XCTAssertFalse(disabled.shouldScheduleLocally)
    }

    func testNormalizeCustomDropsEmptyKeepsPresetsUntouched() {
        var config = FamilyHabitRemindersConfig.empty
        var water = config.schedule(for: .water)
        water.enabled = true
        water.hour = 10
        config.setSchedule(water, for: .water)
        config.custom = [
            FamilyHabitCustomReminder(title: "   "),
            FamilyHabitCustomReminder(id: "keep", title: "Door", mode: .onceDaily)
        ]
        config.normalizeCustom()
        XCTAssertEqual(config.custom.count, 1)
        XCTAssertEqual(config.custom[0].id, "keep")
        XCTAssertTrue(config.schedule(for: .water).enabled)
        XCTAssertEqual(config.schedule(for: .water).hour, 10)
    }

    func testHasUserScheduledTimesTrueForCustomOnly() {
        var config = FamilyHabitRemindersConfig.empty
        config.custom = [FamilyHabitCustomReminder(id: "c", title: "X", mode: .onceDaily)]
        XCTAssertTrue(FamilyHabitRemindersService.hasUserScheduledTimes(config))
    }

    func testPolicyUnchangedWithCustomPresent() {
        // Custom reminders must not alter who receives Family habit pushes.
        let parent = FamilyMemberData(
            id: "parent-fhc10",
            serverMemberId: "parent-fhc10",
            name: "Parent",
            role: .parent,
            avatar: "👨",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
        let teen = FamilyMemberData(
            id: "teen-fhc10",
            serverMemberId: "teen-fhc10",
            name: "Teen",
            role: .teenager,
            avatar: "🧒",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
        var config = FamilyHabitRemindersConfig.empty
        config.memberIds = []
        config.custom = [FamilyHabitCustomReminder(id: "x", title: "Call", mode: .onceDaily)]

        let parentDefaults = makeDefaults()
        parentDefaults.set("parent-fhc10", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        XCTAssertTrue(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: config,
                members: [parent, teen],
                defaults: parentDefaults
            )
        )

        let teenDefaults = UserDefaults(suiteName: "FamilyHabitRemindersPolicyTests.teen.\(UUID().uuidString)")!
        teenDefaults.set("teen-fhc10", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        XCTAssertTrue(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: config,
                members: [parent, teen],
                defaults: teenDefaults
            )
        )

        FamilyHabitRemindersPolicy.setRemindOnThisDevice(false, defaults: parentDefaults)
        XCTAssertFalse(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: config,
                members: [parent, teen],
                defaults: parentDefaults
            )
        )
    }
}
