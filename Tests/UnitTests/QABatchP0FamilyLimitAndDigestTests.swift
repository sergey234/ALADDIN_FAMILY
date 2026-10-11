import XCTest
import SwiftUI
@testable import ALADDIN

/// P0 QA batch: roster limit detection + Safety Week raw-key filter.
final class QABatchP0FamilyLimitAndDigestTests: XCTestCase {

    func testFamilyMemberLimitSSOT() {
        XCTAssertEqual(SubscriptionManager.familyMemberLimitStatic(for: .free), 1)
        XCTAssertEqual(SubscriptionManager.familyMemberLimitStatic(for: .trial), 3)
        XCTAssertEqual(SubscriptionManager.familyMemberLimitStatic(for: .personal), 2)
        XCTAssertEqual(SubscriptionManager.familyMemberLimitStatic(for: .family), 6)
        XCTAssertEqual(SubscriptionManager.familyMemberLimitStatic(for: .premium), 10)
    }

    /// Palette: каждый платный tier визуально отличим от free/trial (канон Shyam).
    func testTariffAccentPalettePaidDistinctFromTrialAndFree() {
        let free = TariffAccentPalette.color(for: .free)
        let trial = TariffAccentPalette.color(for: .trial)
        let personal = TariffAccentPalette.color(for: .personal)
        let family = TariffAccentPalette.color(for: .family)
        let premium = TariffAccentPalette.color(for: .premium)
        XCTAssertNotEqual(free, trial)
        XCTAssertNotEqual(trial, family)
        XCTAssertNotEqual(family, premium)
        XCTAssertNotEqual(personal, family)
        XCTAssertNotEqual(personal, premium)
        XCTAssertNotEqual(trial, premium)
    }

    func testIsFamilyMemberLimitErrorDetectsRUAndEN() {
        let ru = NSError(
            domain: "API",
            code: 403,
            userInfo: [NSLocalizedDescriptionKey: "Лимит участников для вашего тарифа (1) достигнут. Обновите тариф."]
        )
        let en = NSError(
            domain: "API",
            code: 403,
            userInfo: [NSLocalizedDescriptionKey: "Member limit for your plan (2) reached. Upgrade your plan."]
        )
        let other = NSError(
            domain: "API",
            code: 500,
            userInfo: [NSLocalizedDescriptionKey: "Internal server error"]
        )
        XCTAssertTrue(FamilyRegistrationViewModel.isFamilyMemberLimitError(ru))
        XCTAssertTrue(FamilyRegistrationViewModel.isFamilyMemberLimitError(en))
        XCTAssertFalse(FamilyRegistrationViewModel.isFamilyMemberLimitError(other))
    }

    func testVoiceWeeklyDigestSkipsRawLocalizationKeys() {
        XCTAssertTrue(VoiceWeeklyDigestService.looksLikeLocalizationKey("ai_assistant_voice_empty_result"))
        XCTAssertTrue(VoiceWeeklyDigestService.looksLikeLocalizationKey("voice_notes_transcript_error"))
        XCTAssertFalse(VoiceWeeklyDigestService.looksLikeLocalizationKey("Проверили ссылку в чате"))
        XCTAssertFalse(VoiceWeeklyDigestService.looksLikeLocalizationKey("Checked a link today"))

        let cal = Calendar.current
        let now = Date()
        let notes: [VoiceNotesStore.StoredVoiceNote] = [
            .init(
                id: UUID(),
                title: "raw",
                createdAt: now,
                durationSec: 1,
                transcriptPreview: "ai_assistant_voice_empty_result",
                summary: "ai_assistant_voice_empty_result",
                summaryConfidence: 0,
                summaryVersion: 0,
                tags: ["intent_idea"],
                audioPath: ""
            ),
            .init(
                id: UUID(),
                title: "ok",
                createdAt: now,
                durationSec: 1,
                transcriptPreview: "idea line",
                summary: "idea line",
                summaryConfidence: 0,
                summaryVersion: 0,
                tags: ["intent_idea"],
                audioPath: ""
            ),
        ]
        let result = VoiceWeeklyDigestService.build(notes: notes, now: now, calendar: cal)
        XCTAssertFalse(result.topLines.contains(where: { $0.contains("ai_assistant_") }))
        XCTAssertTrue(result.topLines.contains(where: { $0.contains("idea") }))
    }
}
