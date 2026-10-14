import Foundation

/// W2 UX36 — human threat card: What / Where / What to do (never raw EICAR English alone).
struct DeviceThreatPresentation: Equatable, Sendable {
    let title: String
    let what: String
    let whereText: String
    let action: String
    /// Optional short technical id kept for logs/a11y, not primary UI.
    let technicalHint: String?

    static func present(
        id: String,
        name: String?,
        description: String?,
        localization: LocalizationManager = .shared
    ) -> DeviceThreatPresentation {
        let blob = [id, name ?? "", description ?? ""].joined(separator: " ").lowercased()
        if blob.contains("eicar") {
            return DeviceThreatPresentation(
                title: localization.localized("threat_eicar_title"),
                what: localization.localized("threat_eicar_what"),
                whereText: localization.localized("threat_eicar_where"),
                action: localization.localized("threat_eicar_action"),
                technicalHint: name ?? id
            )
        }
        let safeName = (name ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        let title: String
        if safeName.isEmpty || looksLikeRawEnglishThreatName(safeName) {
            title = localization.localized("threat_unknown_title")
        } else {
            title = safeName
        }
        let what: String = {
            if let description, !description.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
               !looksLikeRawEnglishThreatName(description) {
                return description
            }
            return localization.localized("threat_unknown_what")
        }()
        return DeviceThreatPresentation(
            title: title,
            what: what,
            whereText: localization.localized("threat_unknown_where"),
            action: localization.localized("threat_unknown_action"),
            technicalHint: safeName.isEmpty ? id : safeName
        )
    }

    static func presentQuarantine(
        originalName: String,
        threatName: String,
        localization: LocalizationManager = .shared
    ) -> DeviceThreatPresentation {
        present(
            id: originalName,
            name: threatName,
            description: originalName,
            localization: localization
        )
    }

    private static func looksLikeRawEnglishThreatName(_ text: String) -> Bool {
        let lower = text.lowercased()
        if lower.contains("eicar") { return true }
        if lower.contains("standard anti") { return true }
        if lower.contains("anti-malware") || lower.contains("anti malware") { return true }
        if lower.hasSuffix(".com") && lower.contains("eicar") { return true }
        return false
    }
}

/// W2 UX36 — never show snake_case API statuses on UI.
enum ComponentStatusCopy {
    static func localized(
        _ raw: String?,
        localization: LocalizationManager = .shared
    ) -> String {
        let key = (raw ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        switch key {
        case "active", "enabled", "on", "ok", "healthy", "protected", "clean":
            return localization.localized("component_status_active")
        case "fallback_active", "degraded", "simple", "fallback":
            return localization.localized("component_status_fallback_active")
        case "error", "failed", "fail", "critical":
            return localization.localized("component_status_error")
        case "disabled", "off", "inactive", "stopped":
            return localization.localized("component_status_disabled")
        case "threat_found", "threats_found", "infected":
            return localization.localized("component_status_threat_found")
        case "":
            return localization.localized("component_status_unknown")
        default:
            if key.contains("_") || key.contains("fallback") {
                return localization.localized("component_status_unknown")
            }
            return localization.localized("component_status_unknown")
        }
    }
}
