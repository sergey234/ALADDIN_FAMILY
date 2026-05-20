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
    /// Последний `family_id`, с которым был сохранён `family_members_list` (защита от «чужого» кэша с другого аккаунта/чата).
    static let rosterSnapshotFamilyIdKey = "family_members_roster_snapshot_family_id"
    /// После «Добавить в текущую семью»: предложить зарегистрировать устройство для нового `MEM_*` (очищается после выбора пользователя).
    static let pendingPostAdminAddDeviceMemberIdKey = "pending_post_admin_add_device_member_id"
    static let pendingPostAdminAddDeviceMemberNameKey = "pending_post_admin_add_device_member_name"

    // MARK: - P0: family_id в Keychain (не UserDefaults)

    static func loadPersistedFamilyId() -> String {
        if let keychainId = KeychainManager.shared.loadString(forKey: .familyId)?
            .trimmingCharacters(in: .whitespacesAndNewlines), !keychainId.isEmpty {
            return keychainId
        }
        if let legacy = UserDefaults.standard.string(forKey: familyIdKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines), !legacy.isEmpty {
            persistFamilyId(legacy)
            return legacy
        }
        return ""
    }

    static func persistFamilyId(_ newFamilyId: String) {
        let newId = newFamilyId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !newId.isEmpty else {
            KeychainManager.shared.delete(forKey: .familyId)
            UserDefaults.standard.removeObject(forKey: familyIdKey)
            return
        }
        KeychainManager.shared.save(newId, forKey: .familyId)
        UserDefaults.standard.removeObject(forKey: familyIdKey)
    }

    /// Сбрасывает сохранённый ростер и связанные ключи, если новый `family_id` отличается от уже сохранённого.
    /// Не трогает `your_member_id` и токены — вызывающий код обновляет их отдельно.
    /// - Returns: `true`, если выполнен сброс (семья сменилась или в хранилище был другой id).
    @discardableResult
    static func resetPersistedCachesIfFamilyChanged(newFamilyId: String) -> Bool {
        let newId = newFamilyId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !newId.isEmpty else { return false }

        let previous = loadPersistedFamilyId()
        guard newId != previous else { return false }

        let defaults = UserDefaults.standard
        defaults.removeObject(forKey: familyMembersKey)
        defaults.removeObject(forKey: familyAdditionOrderKey)
        defaults.removeObject(forKey: partialSyncRetryCountKey)
        defaults.removeObject(forKey: familyMemberSeededKey)
        defaults.removeObject(forKey: lastResolvedFamilyIdKey)
        defaults.removeObject(forKey: familyCreatorMemberIdKey)
        defaults.removeObject(forKey: rosterSnapshotFamilyIdKey)
        defaults.removeObject(forKey: pendingPostAdminAddDeviceMemberIdKey)
        defaults.removeObject(forKey: pendingPostAdminAddDeviceMemberNameKey)
        defaults.synchronize()
        NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
        return true
    }

    /// Уведомляет подписчиков UI о необходимости обновить экраны семьи после изменения локального ростера.
    static func notifyFamilyMembersUpdated() {
        NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
    }

    /// Записать снимок семьи для текущего кэша ростера (вызывать вместе с сохранением `family_members_list`).
    static func persistRosterSnapshotFamilyId(_ familyId: String, defaults: UserDefaults = .standard) {
        let v = familyId.trimmingCharacters(in: .whitespacesAndNewlines)
        if v.isEmpty {
            defaults.removeObject(forKey: rosterSnapshotFamilyIdKey)
        } else {
            defaults.set(v, forKey: rosterSnapshotFamilyIdKey)
        }
        defaults.synchronize()
    }

    /// Удалить только локальный ростер и метаданные слияния (не трогает `family_id` / токены).
    private static func clearPersistedRosterListAndMergeMeta(defaults: UserDefaults = .standard) {
        defaults.removeObject(forKey: familyMembersKey)
        defaults.removeObject(forKey: rosterSnapshotFamilyIdKey)
        defaults.removeObject(forKey: familyAdditionOrderKey)
        defaults.removeObject(forKey: partialSyncRetryCountKey)
        defaults.removeObject(forKey: familyMemberSeededKey)
        defaults.synchronize()
    }

    /// Ручной сброс локального кэша списка участников (как кнопка «Очистить кэш» на экране Семья).
    /// Не удаляет семью на сервере, не трогает `family_id`, JWT, `your_member_id`, детские профили в `ProfileManager`.
    static func clearLocalFamilyRosterCacheForManualReset(defaults: UserDefaults = .standard) {
        defaults.removeObject(forKey: familyMembersKey)
        defaults.removeObject(forKey: rosterSnapshotFamilyIdKey)
        defaults.removeObject(forKey: familyAdditionOrderKey)
        defaults.removeObject(forKey: partialSyncRetryCountKey)
        defaults.removeObject(forKey: familyMemberSeededKey)
        defaults.removeObject(forKey: "family_not_seen_counters")
        // Also clear quota snapshot helpers to prevent stale "X of Y" lock after reinstall/manual cache clear.
        defaults.removeObject(forKey: "family_roster_used_last")
        defaults.removeObject(forKey: "family_quota_source_last")
        defaults.removeObject(forKey: "family_quota_family_id_last")
        defaults.removeObject(forKey: "family_remaining")
        defaults.synchronize()
    }

    /// Полный локальный reset family-контекста для текущего устройства.
    /// ВАЖНО (guardrails anti-abuse):
    /// - НЕ трогаем trial status / JWT / subscription payload.
    /// - НЕ трогаем серверные данные семьи.
    /// - Удаляем только локальный family roster/context cache, который будет восстановлен серверным sync.
    static func clearLocalFamilyContextForManualReset(defaults: UserDefaults = .standard) {
        clearLocalFamilyRosterCacheForManualReset(defaults: defaults)
        defaults.removeObject(forKey: familyIdKey)
        defaults.removeObject(forKey: lastResolvedFamilyIdKey)
        defaults.removeObject(forKey: familyCreatorMemberIdKey)
        defaults.removeObject(forKey: yourMemberIdUserDefaultsKey)
        defaults.removeObject(forKey: "current_user_role")
        defaults.removeObject(forKey: "admin_add_mode")
        defaults.removeObject(forKey: "family_not_seen_counters")
        defaults.synchronize()
        NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
    }

    /// Перед чтением `family_members_list`: отбрасываем кэш, если он не относится к текущему `family_id` или при пустом `family_id` содержит серверные MEM_*.
    @discardableResult
    static func validatePersistedRosterAgainstCurrentFamily(defaults: UserDefaults = .standard) -> Bool {
        let fid = (defaults.string(forKey: familyIdKey) ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        let snap = (defaults.string(forKey: rosterSnapshotFamilyIdKey) ?? "").trimmingCharacters(in: .whitespacesAndNewlines)

        guard let data = defaults.data(forKey: familyMembersKey),
              let list = try? JSONDecoder().decode([FamilyMemberData].self, from: data),
              !list.isEmpty else {
            return true
        }

        let hasServerLinked = list.contains { row in
            let id = (row.serverMemberId ?? row.id).trimmingCharacters(in: .whitespacesAndNewlines)
            return id.hasPrefix("MEM_")
        }

        if fid.isEmpty {
            if hasServerLinked {
                clearPersistedRosterListAndMergeMeta(defaults: defaults)
                NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
                return false
            }
            return true
        }

        if !snap.isEmpty && snap != fid {
            clearPersistedRosterListAndMergeMeta(defaults: defaults)
            NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
            return false
        }

        // Миграция: впервые фиксируем снимок для уже сохранённого ростера под текущим `family_id`.
        if !fid.isEmpty && snap.isEmpty {
            persistRosterSnapshotFamilyId(fid, defaults: defaults)
        }

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

    /// MEM_* из ответа сервера плюс все MEM_* из локального ростера (память) — reconcile не ломается при неполном GET.
    static func unionServerMemberIdsWithLocalMEM(
        serverResponseIds: [String],
        inMemoryRoster: [FamilyMemberData]
    ) -> Set<String> {
        var u = Set(serverResponseIds)
        for m in inMemoryRoster {
            let id = m.id.trimmingCharacters(in: .whitespacesAndNewlines)
            if id.hasPrefix("MEM_") { u.insert(id) }
            if let sid = m.serverMemberId?.trimmingCharacters(in: .whitespacesAndNewlines), sid.hasPrefix("MEM_") {
                u.insert(sid)
            }
        }
        return u
    }

    private static func persistedFamilyMembersDecoded() -> [FamilyMemberData] {
        guard let data = UserDefaults.standard.data(forKey: familyMembersKey),
              let list = try? JSONDecoder().decode([FamilyMemberData].self, from: data) else { return [] }
        return list
    }

    /// После `GET /api/family/members`: union id + выравнивание `your_member_id`.
    static func reconcileYourMemberIdAfterFamilyMembersResponse(
        serverResponseIds: [String],
        inMemoryRoster: [FamilyMemberData]
    ) {
        let ids = unionServerMemberIdsWithLocalMEM(serverResponseIds: serverResponseIds, inMemoryRoster: inMemoryRoster)
        reconcileYourMemberIdWithServerRoster(serverMemberIds: ids, localRosterForRoleFallback: inMemoryRoster)
    }

    /// После успешного sync: если `your_member_id` не входит в множество id — JWT; затем один родитель/пожилой из ростера при роли parent/elderly в UD.
    static func reconcileYourMemberIdWithServerRoster(
        serverMemberIds: Set<String>,
        localRosterForRoleFallback: [FamilyMemberData]? = nil
    ) {
        guard !serverMemberIds.isEmpty else { return }

        let current = UserDefaults.standard.string(forKey: yourMemberIdUserDefaultsKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""

        if !current.isEmpty, serverMemberIds.contains(current) {
            return
        }

        guard let jwt = AppConfig.authToken, !jwt.isEmpty else {
            if tryRosterRoleFallback(serverMemberIds: serverMemberIds, localRosterForRoleFallback: localRosterForRoleFallback) {
                return
            }
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

        if tryRosterRoleFallback(serverMemberIds: serverMemberIds, localRosterForRoleFallback: localRosterForRoleFallback) {
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

    /// - Returns: `true`, если выставили `your_member_id`.
    @discardableResult
    private static func tryRosterRoleFallback(
        serverMemberIds: Set<String>,
        localRosterForRoleFallback: [FamilyMemberData]?
    ) -> Bool {
        let roster = localRosterForRoleFallback ?? persistedFamilyMembersDecoded()
        let roleFallback = (UserDefaults.standard.string(forKey: "current_user_role") ?? "").lowercased()
        guard roleFallback == "parent" || roleFallback == "elderly" else { return false }

        var candidates: [String] = []
        for m in roster where m.role == .parent || m.role == .elderly {
            let cid = (m.serverMemberId ?? m.id).trimmingCharacters(in: .whitespacesAndNewlines)
            guard cid.hasPrefix("MEM_"), serverMemberIds.contains(cid) else { continue }
            candidates.append(cid)
        }
        let unique = Array(Set(candidates))
        guard unique.count == 1, let pick = unique.first else { return false }

        UserDefaults.standard.set(pick, forKey: yourMemberIdUserDefaultsKey)
        UserDefaults.standard.synchronize()
        VisualLogger.shared.log(
            "✅ FAMILY ID: your_member_id выровнен по ростеру+роли (единственный parent/elderly в union): \(pick.prefix(12))…",
            level: .success,
            category: "FAMILY"
        )
        return true
    }

    private static func memberRowMatchesYourMemberId(_ row: FamilyMemberData, myMemberId: String) -> Bool {
        let my = myMemberId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !my.isEmpty else { return false }
        let sid = row.serverMemberId?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let rid = row.id.trimmingCharacters(in: .whitespacesAndNewlines)
        let canon = row.canonicalId.trimmingCharacters(in: .whitespacesAndNewlines)
        return rid == my || (!sid.isEmpty && sid == my) || (!canon.isEmpty && canon == my)
    }

    /// fam-7: показывать CTA «Восстановить» — семья есть, но `your_member_id` не сходится с ростром или заявлен родитель/пожилой при `canManageAppProfiles == false`.
    static func needsFamilyIdentityRepairHeuristic(members: [FamilyMemberData], canManageAppProfiles: Bool) -> Bool {
        let fid = (UserDefaults.standard.string(forKey: familyIdKey) ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !fid.isEmpty, !members.isEmpty else { return false }

        let my = (UserDefaults.standard.string(forKey: yourMemberIdUserDefaultsKey) ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        let inRoster = !my.isEmpty && members.contains { memberRowMatchesYourMemberId($0, myMemberId: my) }

        if my.isEmpty || !inRoster { return true }
        if canManageAppProfiles { return false }

        let role = (UserDefaults.standard.string(forKey: "current_user_role") ?? "").lowercased()
        if role.contains("parent") || role.contains("elderly") { return true }
        if role.contains("родит") || role.contains("пожил") { return true }
        return false
    }

    /// Выравнивает `current_user_role` по строке ростера для текущего `your_member_id` (после reconcile / repair).
    static func alignCurrentUserRoleFromPersistedRoster(_ members: [FamilyMemberData]) {
        let my = (UserDefaults.standard.string(forKey: yourMemberIdUserDefaultsKey) ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !my.isEmpty else { return }
        guard let me = members.first(where: { memberRowMatchesYourMemberId($0, myMemberId: my) }) else { return }

        let raw = me.role.rawValue
        let prev = (UserDefaults.standard.string(forKey: "current_user_role") ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard prev.lowercased() != raw.lowercased() else { return }

        UserDefaults.standard.set(raw, forKey: "current_user_role")
        UserDefaults.standard.synchronize()
        VisualLogger.shared.log("✅ FAMILY ID: current_user_role синхронизирован с ростром: \(raw)", level: .info, category: "FAMILY")
    }

    /// fam-7: явный repair — union MEM_* из локального ростера + JWT reconcile + роль из ростера.
    static func repairFamilyIdentityFromLocalRoster(_ members: [FamilyMemberData]) {
        let ids = unionServerMemberIdsWithLocalMEM(serverResponseIds: [], inMemoryRoster: members)
        guard !ids.isEmpty else {
            VisualLogger.shared.log("⚠️ FAMILY ID repair: нет MEM_* в ростере", level: .warning, category: "FAMILY")
            return
        }
        reconcileYourMemberIdWithServerRoster(serverMemberIds: ids, localRosterForRoleFallback: members)
        alignCurrentUserRoleFromPersistedRoster(members)
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
        defaults.removeObject(forKey: rosterSnapshotFamilyIdKey)
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
