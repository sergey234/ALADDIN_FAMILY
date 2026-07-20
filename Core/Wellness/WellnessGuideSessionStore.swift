import Foundation
import SwiftUI

/// psych-02/08 — session guide mode (ids = reflective_modes_v1.json).
/// Mode changes **session instruction only** — never `primary_pillar` / session pillar lock.
final class WellnessGuideSessionStore: ObservableObject {
    static let shared = WellnessGuideSessionStore()

    static let featureFlagKey = "feature_wellness_guide_modes"
    static let modeKey = "wellness_guide_mode_id"
    static let presenceNudgeKey = "wellness_guide_presence_nudge"
    /// SSOT ids — must match `wellness_i18n/reflective_modes_v1.json` + `wellness_guide_role.py`.
    static let ssotModeIds: [String] = [
        "presence",
        "structured_view",
        "deep_explore",
        "blind_spots",
        "single_question",
    ]

    /// Client mirror of FEATURE_WELLNESS_GUIDE_MODES (default ON for A+B UX).
    @Published var guideModesEnabled: Bool {
        didSet { UserDefaults.standard.set(guideModesEnabled, forKey: Self.featureFlagKey) }
    }

    @Published var selectedModeId: String {
        didSet { UserDefaults.standard.set(selectedModeId, forKey: Self.modeKey) }
    }

    @Published var showPresenceNudge: Bool = false

    struct ModeOption: Identifiable, Equatable {
        let id: String
        let labelKey: String
        let hintKey: String
        let allowedForChild: Bool
    }

    static let allModes: [ModeOption] = [
        ModeOption(id: "presence", labelKey: "wellness_mode_presence", hintKey: "wellness_mode_presence_hint", allowedForChild: true),
        ModeOption(id: "structured_view", labelKey: "wellness_mode_structured", hintKey: "wellness_mode_structured_hint", allowedForChild: false),
        ModeOption(id: "deep_explore", labelKey: "wellness_mode_deep", hintKey: "wellness_mode_deep_hint", allowedForChild: false),
        ModeOption(id: "blind_spots", labelKey: "wellness_mode_blind_spots", hintKey: "wellness_mode_blind_spots_hint", allowedForChild: false),
        ModeOption(id: "single_question", labelKey: "wellness_mode_one_question", hintKey: "wellness_mode_one_question_hint", allowedForChild: false),
    ]

    static let defaultModeId = "structured_view"

    private init() {
        if UserDefaults.standard.object(forKey: Self.featureFlagKey) == nil {
            guideModesEnabled = true
        } else {
            guideModesEnabled = UserDefaults.standard.bool(forKey: Self.featureFlagKey)
        }
        selectedModeId = UserDefaults.standard.string(forKey: Self.modeKey) ?? Self.defaultModeId
    }

    /// Safe for API default args (not MainActor-isolated).
    static var activeGuideModeIdForAPI: String? {
        let enabled: Bool
        if UserDefaults.standard.object(forKey: featureFlagKey) == nil {
            enabled = true
        } else {
            enabled = UserDefaults.standard.bool(forKey: featureFlagKey)
        }
        guard enabled else { return nil }
        let ageBand = CompanionUserContext.companionAgeBand
        let stored = UserDefaults.standard.string(forKey: modeKey) ?? defaultModeId
        if ageBand == "child" {
            return "presence"
        }
        if allModes.contains(where: { $0.id == stored }) {
            return stored
        }
        return defaultModeId
    }

    var activeGuideModeId: String? { Self.activeGuideModeIdForAPI }

    func modes(forAgeBand ageBand: String) -> [ModeOption] {
        if ageBand == "child" {
            return Self.allModes.filter(\.allowedForChild)
        }
        return Self.allModes
    }

    func normalizedMode(for ageBand: String) -> String {
        let modes = modes(forAgeBand: ageBand)
        if modes.contains(where: { $0.id == selectedModeId }) {
            return selectedModeId
        }
        return ageBand == "child" ? "presence" : Self.defaultModeId
    }

    func selectMode(_ id: String, ageBand: String) {
        let allowed = modes(forAgeBand: ageBand).map(\.id)
        selectedModeId = allowed.contains(id) ? id : normalizedMode(for: ageBand)
        // psych-02: intentionally does NOT call WellnessSessionStore.setActivePillar
    }

    /// psych-09 — each new guide session starts from safe default (not yesterday's deep).
    func beginNewGuideSession(ageBand: String) {
        let resetId = ageBand == "child" ? "presence" : Self.defaultModeId
        selectMode(resetId, ageBand: ageBand)
        showPresenceNudge = false
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: Self.sessionStartedAtKey)
        showSessionSoftNudge = false
    }

    static let sessionStartedAtKey = "wellness_guide_session_started_at"
    static let softNudgeMinutes = 12

    @Published var showSessionSoftNudge: Bool = false

    /// psych-04b — soft nudge after ~12 min (no hard cutoff).
    func evaluateSessionSoftNudge() {
        let started = UserDefaults.standard.double(forKey: Self.sessionStartedAtKey)
        guard started > 0 else { return }
        let elapsed = Date().timeIntervalSince1970 - started
        if elapsed >= Double(Self.softNudgeMinutes * 60) {
            showSessionSoftNudge = true
        }
    }

    func dismissSessionSoftNudge() {
        showSessionSoftNudge = false
        // Push start forward so we don't re-nag immediately
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: Self.sessionStartedAtKey)
    }

    /// psych-06 — soft nudge toward presence when escalation / strong emotion.
    func applyPresenceNudgeIfNeeded(escalation: String?) {
        let esc = (escalation ?? "L0").uppercased()
        guard esc == "L1" || esc == "L2" else { return }
        showPresenceNudge = true
        if CompanionUserContext.companionAgeBand != "child" {
            UserDefaults.standard.set(true, forKey: Self.presenceNudgeKey)
        }
    }

    func acceptPresenceNudge(ageBand: String) {
        selectMode("presence", ageBand: ageBand)
        showPresenceNudge = false
    }

    func dismissPresenceNudge() {
        showPresenceNudge = false
    }
}
