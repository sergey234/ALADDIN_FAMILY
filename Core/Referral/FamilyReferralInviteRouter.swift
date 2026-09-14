import Foundation

/// Deep-link / invite code attach for Family Invite Pro.
enum FamilyReferralInviteRouter {
    private static let pendingCodeKey = "pending_family_referral_a_code"

    /// Parses `https://aladdin-ai.ru/invite/CODE` or `aladdin://invite/CODE`.
    static func extractInviteCode(from url: URL) -> String? {
        let host = (url.host ?? "").lowercased()
        let path = url.path
        let parts = path.split(separator: "/").map(String.init)

        let isInviteHost =
            host.contains("aladdin-ai.ru")
            || host.contains("aladdin.family")
            || host == "invite"
            || url.scheme?.lowercased() == "aladdin"

        guard isInviteHost || parts.first?.lowercased() == "invite" else {
            if parts.count >= 2, parts[0].lowercased() == "invite" {
                return sanitize(parts[1])
            }
            return nil
        }

        if parts.first?.lowercased() == "invite", parts.count >= 2 {
            return sanitize(parts[1])
        }
        // aladdin://invite/CODE → host may be "invite"
        if host == "invite", let code = parts.first {
            return sanitize(code)
        }
        return nil
    }

    static func savePendingCode(_ code: String) {
        let c = sanitize(code)
        guard let c, !c.isEmpty else { return }
        UserDefaults.standard.set(c, forKey: pendingCodeKey)
        FamilyReferralAnalytics.track(.linkOpen, parameters: ["code_len": c.count])
    }

    static func loadPendingCode() -> String? {
        guard let raw = UserDefaults.standard.string(forKey: pendingCodeKey) else { return nil }
        return sanitize(raw)
    }

    static func clearPendingCode() {
        UserDefaults.standard.removeObject(forKey: pendingCodeKey)
    }

    /// Attach pending code to current user via API (idempotent).
    @MainActor
    static func attachPendingIfNeeded(api: APIService? = nil) {
        let service = api ?? APIService.shared
        guard let code = loadPendingCode(), !code.isEmpty else { return }
        service.attachFamilyReferralA(code: code) { result in
            Task { @MainActor in
                switch result {
                case .success:
                    FamilyReferralAnalytics.track(.signupAttach, parameters: ["status": "ok"])
                    clearPendingCode()
                case .failure(let error):
                    #if DEBUG
                    print("⚠️ FamilyReferralInviteRouter.attach: \(error.localizedDescription)")
                    #endif
                }
            }
        }
    }

    @MainActor
    static func notifyGrantIfNeeded(days: Int, tier: String?) {
        guard days > 0 else { return }
        let title = LocalizationManager.shared.localized("referral_a_grant_push_title")
        let body = String(
            format: LocalizationManager.shared.localized("referral_a_grant_push_body"),
            days
        )
        NotificationManager.shared.sendLocalNotification(
            title: title,
            body: body,
            category: .general,
            userInfo: [
                "type": "family_referral_a_grant",
                "days": days,
                "tier": tier ?? "",
            ]
        )
        FamilyReferralAnalytics.track(.grant, parameters: ["days": days, "tier": tier ?? ""])
    }

    private static func sanitize(_ raw: String) -> String? {
        let c = raw.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
        guard c.count >= 4, c.count <= 20 else { return nil }
        let allowed = CharacterSet.alphanumerics
        guard c.unicodeScalars.allSatisfy({ allowed.contains($0) }) else { return nil }
        return c
    }
}
