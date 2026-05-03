import Foundation

/// Единая точка сброса локальных кэшей семьи при смене `family_id` (create / join / recovery).
enum FamilyLocalStore {
    static let familyIdKey = "family_id"
    static let familyMembersKey = "family_members_list"
    static let familyAdditionOrderKey = "family_addition_order"
    static let partialSyncRetryCountKey = "family_sync_partial_retry_count"
    static let familyMemberSeededKey = "family_member_seeded_once"
    /// Последний `family_id`, с которым сервер отдал ответ `GET /api/family/members` (заголовок `X-Resolved-Family-Id`).
    static let lastResolvedFamilyIdKey = "family_members_last_resolved_family_id"
    /// Создатель семьи (`creator_member_id` из `POST /api/family/create`) — не путать с `your_member_id` присоединившегося.
    static let familyCreatorMemberIdKey = "family_creator_member_id"
    static let yourMemberIdUserDefaultsKey = "your_member_id"

    /// Сбрасывает сохранённый ростер и связанные ключи, если новый `family_id` отличается от уже сохранённого.
    /// Не трогает `your_member_id` и токены — вызывающий код обновляет их отдельно.
    /// - Returns: `true`, если выполнен сброс (семья сменилась или в хранилище был другой id).
    @discardableResult
    static func resetPersistedCachesIfFamilyChanged(newFamilyId: String) -> Bool {
        let newId = newFamilyId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !newId.isEmpty else { return false }

        let previous = UserDefaults.standard.string(forKey: familyIdKey)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        guard newId != previous else { return false }

        let defaults = UserDefaults.standard
        defaults.removeObject(forKey: familyMembersKey)
        defaults.removeObject(forKey: familyAdditionOrderKey)
        defaults.removeObject(forKey: partialSyncRetryCountKey)
        defaults.removeObject(forKey: familyMemberSeededKey)
        defaults.removeObject(forKey: lastResolvedFamilyIdKey)
        defaults.removeObject(forKey: familyCreatorMemberIdKey)
        defaults.synchronize()
        NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
        return true
    }

    // MARK: - Family creator (server createFamily only)

    static func persistFamilyCreatorMemberId(_ raw: String) {
        let id = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard id.hasPrefix("MEM_"), !id.isEmpty else { return }
        UserDefaults.standard.set(id, forKey: familyCreatorMemberIdKey)
        UserDefaults.standard.synchronize()
    }

    static func currentFamilyCreatorMemberId() -> String? {
        let v = UserDefaults.standard.string(forKey: familyCreatorMemberIdKey)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return v.isEmpty ? nil : v
    }

    // MARK: - JWT payload (align your_member_id with roster when possible)

    static func jwtPayloadDictionary(from jwt: String) -> [String: Any]? {
        let parts = jwt.split(separator: ".")
        guard parts.count >= 2 else { return nil }
        var base64 = String(parts[1])
            .replacingOccurrences(of: "-", with: "+")
            .replacingOccurrences(of: "_", with: "/")
        let padding = 4 - (base64.count % 4)
        if padding < 4 {
            base64 += String(repeating: "=", count: padding)
        }
        guard
            let data = Data(base64Encoded: base64),
            let json = try? JSONSerialization.jsonObject(with: data),
            let payload = json as? [String: Any]
        else {
            return nil
        }
        return payload
    }

    /// Ищет `MEM_*` в известных полях и во всех строковых значениях payload (порядок не гарантирован — см. reconcile).
    static func hintedFamilyMemberIdsInJWT(_ jwt: String) -> [String] {
        guard let payload = jwtPayloadDictionary(from: jwt) else { return [] }
        var found: [String] = []
        let preferredKeys = [
            "family_member_id", "familyMemberId", "member_id", "memberId",
            "family_member", "mem_id", "aladdin_member_id"
        ]
        for key in preferredKeys {
            if let s = payload[key] as? String { collectMemIds(from: s, into: &found) }
        }
        for (_, value) in payload {
            if let s = value as? String { collectMemIds(from: s, into: &found) }
        }
        return Array(Set(found))
    }

    private static func collectMemIds(from string: String, into found: inout [String]) {
        let trimmed = string.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        if trimmed.hasPrefix("MEM_") {
            let token = memTokenPrefix(from: trimmed)
            if !token.isEmpty { found.append(token) }
        }
        let parts = trimmed.split { !$0.isLetter && !$0.isNumber && $0 != "_" }
        for p in parts where p.hasPrefix("MEM_") {
            let token = memTokenPrefix(from: String(p))
            if !token.isEmpty { found.append(token) }
        }
    }

    private static func memTokenPrefix(from s: String) -> String {
        var out = ""
        for ch in s {
            if ch == "_" || ch.isLetter || ch.isNumber {
                out.append(ch)
                if out.count >= 40 { break }
            } else if !out.isEmpty {
                break
            }
        }
        return out.hasPrefix("MEM_") && out.count >= 8 ? out : ""
    }

    /// Вызывается из `NetworkManager` при ответе `GET /api/family/members`, если бэкенд присылает заголовок.
    static func applyYourMemberIdFromFamilyMembersHeaderIfPresent(_ raw: String?) {
        guard let raw = raw?.trimmingCharacters(in: .whitespacesAndNewlines), !raw.isEmpty else { return }
        guard raw.hasPrefix("MEM_") else { return }
        UserDefaults.standard.set(raw, forKey: yourMemberIdUserDefaultsKey)
        UserDefaults.standard.synchronize()
        VisualLogger.shared.log("✅ FAMILY ID: your_member_id из заголовка ответа members: \(raw.prefix(12))…", level: .success, category: "FAMILY")
    }

    /// После успешного sync: если `your_member_id` не входит в ростер — пробуем JWT; иначе оставляем как есть.
    static func reconcileYourMemberIdWithServerRoster(serverMemberIds: Set<String>) {
        guard !serverMemberIds.isEmpty else { return }

        let current = UserDefaults.standard.string(forKey: yourMemberIdUserDefaultsKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""

        if !current.isEmpty, serverMemberIds.contains(current) {
            return
        }

        guard let jwt = AppConfig.authToken, !jwt.isEmpty else {
            if !current.isEmpty {
                VisualLogger.shared.log(
                    "⚠️ FAMILY ID: your_member_id=\(current.prefix(8))… не в ростере; JWT отсутствует — требуется повторный вход или заголовок X-Current-Member-Id",
                    level: .warning,
                    category: "FAMILY"
                )
            }
            return
        }

        let hints = hintedFamilyMemberIdsInJWT(jwt)
        for hint in hints where serverMemberIds.contains(hint) {
            UserDefaults.standard.set(hint, forKey: yourMemberIdUserDefaultsKey)
            UserDefaults.standard.synchronize()
            VisualLogger.shared.log(
                "✅ FAMILY ID: your_member_id выровнен по JWT+ростеру: \(hint.prefix(12))…",
                level: .success,
                category: "FAMILY"
            )
            return
        }

        if !current.isEmpty {
            VisualLogger.shared.log(
                "⚠️ FAMILY ID: your_member_id=\(current.prefix(8))… не в ростере; JWT не содержит подходящего MEM_* — проверьте токен на сервере",
                level: .warning,
                category: "FAMILY"
            )
        }
    }

    /// Сервер явно сообщил, что у аккаунта нет семьи (`X-Family-Context: none`) или 404 на `GET /members` с устаревшим `familyId`.
    static func clearPersistedFamilyContextWhenServerReportsNoFamily() {
        let defaults = UserDefaults.standard
        defaults.removeObject(forKey: familyIdKey)
        defaults.removeObject(forKey: familyMembersKey)
        defaults.removeObject(forKey: lastResolvedFamilyIdKey)
        defaults.removeObject(forKey: familyAdditionOrderKey)
        defaults.removeObject(forKey: partialSyncRetryCountKey)
        defaults.removeObject(forKey: familyMemberSeededKey)
        defaults.removeObject(forKey: familyCreatorMemberIdKey)
        defaults.removeObject(forKey: yourMemberIdUserDefaultsKey)
        defaults.synchronize()
        NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
    }

    /// 404 от `GET /api/family/members` при «нет семьи / неверный query» (после смены контракта бэкенда).
    static func shouldClearFamilyCacheAfterMembersRequestFailure(_ error: Error) -> Bool {
        switch NetworkError.from(error) {
        case .notFound(let msg):
            let m = (msg ?? "").lowercased()
            return m.contains("no family registered") || m.contains("invalid familyid")
        default:
            return false
        }
    }
}
