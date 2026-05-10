import SwiftUI
import CoreLocation

// Master Logger for UI logging
private let logger = MasterLogger.shared

struct FamilyScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var subscriptionManager: SubscriptionManager // For single-source family limits
    @Environment(\.dismiss) private var dismiss
    @StateObject private var syncEngine = SyncEngine.shared
    
    // ✅ ИСПРАВЛЕНИЕ #7: Убрали @State showAddMemberModal - теперь используем NavigationManager
    // @State private var showAddMemberModal = false
    @State private var showParentalSettingsModal = false
    @State private var showInvitationGuideModal: Bool = false
    @State private var showPostRegistrationDeviceGuide: Bool = false
    @State private var removeMemberErrorMessage: String? = nil
    @State private var removeMemberSuccessMessage: String? = nil
    /// Дружелюбное сообщение при 409 на загрузке списка (несовпадение сохранённой семьи и аккаунта).
    @State private var familySyncContextBanner: String? = nil
    @State private var pendingRemovalMember: FamilyMemberData? = nil
    @State private var deletingMemberIds: Set<String> = []
    // Quick-add sheet was removed; we use navigation to AddMemberOptionsScreen
    
    // UserDefaults ключи для участников семьи
    private let familyMembersKey = "family_members_list"
    private let currentUserRoleKey = "current_user_role"
    private let currentUserNameKey = "current_user_name"
    private let familyMemberSeededKey = "family_member_seeded_once"
    private let familyAdditionOrderKey = "family_addition_order"  // ✅ Stable addition order: new members ALWAYS at bottom. Preserved across syncs.
    private let postRegistrationDeviceNudgePendingKey = "post_registration_device_nudge_pending"
    private let postRegistrationDeviceNudgeLastShownKey = "post_registration_device_nudge_last_shown_ts"
    private let postRegistrationDeviceNudgeCooldown: TimeInterval = 6 * 60 * 60

    // Computed property for stable addition order (persisted across app restarts and syncs)
    private var familyAdditionOrder: [String] {
        get {
            UserDefaults.standard.stringArray(forKey: familyAdditionOrderKey) ?? []
        }
        set {
            UserDefaults.standard.set(newValue, forKey: familyAdditionOrderKey)
            UserDefaults.standard.synchronize()
            VisualLogger.shared.log("📋 FAMILY ORDER updated: \(newValue.count) entries [\(newValue.joined(separator: ","))]", level: .debug, category: "FAMILY")
        }
    }
    
    // Динамический список участников семьи (до 10 человек)
    @State private var familyMembers: [FamilyMemberData] = []
    @State private var isFamilyLoadInProgress: Bool = false
    @State private var isFamilySyncInProgress: Bool = false
    @State private var isFamilyIdentityRepairing: Bool = false
    // ✅ NEW: Debounce protection against sub-second save/reload cycles (main fix for infinite loop)
    @State private var lastFamilyOperationTime: Date = .distantPast
    @State private var lastCoalescedFamilySyncAt: Date = .distantPast
    // ✅ OPTIMIZATION: Cached admin status to prevent expensive computed property spam on every render
    @State private var isCurrentUserCreator: Bool = true
    @State private var isCurrentUserParent: Bool = true
    // Последний набор server-идентификаторов из /api/family/members
    @State private var serverMemberIdsLatest: Set<String> = []
    @State private var optimisticallyRemovedIds: Set<String> = []
    // Лимиты семьи (обновляются из заголовков ответа /api/family/members)
    // Legacy for compatibility; primary source is now subscriptionManager.currentFamilyLimit
    @AppStorage("family_limit") private var familyLimit: Int = 0
    @AppStorage("family_remaining") private var familyRemaining: Int = 0
    // Banner for sync status during partial subset
    @State private var showSyncBanner: Bool = false
    @State private var showClearLocalFamilyCacheConfirmation: Bool = false
    // Lightweight log de-duplication
    @State private var lastLogTimestamps: [String: TimeInterval] = [:]
    @State private var notSeenCounters: [String: Int] = [:]
    private let maxNotSeenConsecutiveSyncs: Int = 3
    // Ретраи для частичных ответов сервера при синхронизации
    @State private var partialSyncRetryCount: Int = 0
    private let maxPartialSyncRetries: Int = 3
    
    // Новые состояния для родительского контроля (7 карточек)
    @State private var showContentBlockModal: Bool = false
    @State private var showTimeControlModalNew: Bool = false
    @State private var showMonitoringModalNew: Bool = false
    @State private var showLocationModal: Bool = false
    @State private var showReportsModal: Bool = false
    @State private var showAdditionalModal: Bool = false
    @State private var showBypassProtectionModal: Bool = false
    @State private var showFamilyNotificationSettings: Bool = false
    
    // Состояния для карточек (сохранение через @AppStorage)
    @AppStorage("family_content_block_enabled") private var isContentBlockEnabled: Bool = true
    @AppStorage("family_time_control_enabled") private var isTimeControlEnabled: Bool = true
    @AppStorage("family_monitoring_enabled") private var isMonitoringEnabled: Bool = true
    @AppStorage("family_location_enabled") private var isLocationEnabled: Bool = true
    @AppStorage("family_reports_enabled") private var isReportsEnabled: Bool = true
    @AppStorage("family_additional_enabled") private var isAdditionalEnabled: Bool = true
    @AppStorage("family_bypass_protection_enabled") private var isBypassProtectionEnabled: Bool = true
    @AppStorage("parental_selected_child_id") private var familyBypassSelectedChildId: String = ""
    @AppStorage("parental_selected_child") private var familyBypassLegacyChild: String = ""
    
    // Данные для карточек (из wireframe)
    
    @State private var timeRemaining: String = LocalizationManager.shared.localized("family_time_remaining_placeholder")
    @State private var timeSchedules: Int = 3
    
    @State private var monitoringWebsites: Int = 342
    @State private var monitoringApps: Int = 28
    
    @State private var locationStatus: String = LocalizationManager.shared.localized("parental_location_home")
    @State private var locationLastUpdate: String = LocalizationManager.shared.localized("family_location_last_update_placeholder")
    @State private var locationWarnings: Int = 2
    
    @State private var reportsToday: Bool = true
    @State private var reportsAlerts: Int = 2
    
    @State private var additionalRequests: Int = 2
    @State private var additionalProtection: Bool = true
    
    // State for the bypass protection card
    @State private var bypassAttemptsToday: Int = 0
    @State private var bypassAttemptsWeek: Int = 0
    @State private var bypassAttemptsBlocked: Int = 0
    @State private var bypassDetectionActive: Int = 3  // обновляется из UserDefaults (тогглы антиобхода)
    
    @State private var unicornBalance: Int = 245
    
    // ✅ BUILD 96: Кешированное значение для предотвращения рекурсии
    @State private var cachedParentalRules: ParentalControlRules? = nil
    
    // Computed property для получения актуального баланса из UserDefaults
    private var currentUnicornBalance: Int {
        UnicornRewardsStore.readBalance(for: UnicornRewardsStore.resolveActiveChildId())
    }

    private var effectiveQuotaUsedForUI: Int {
        if subscriptionManager.familyQuotaSnapshot.source == .persistedCache {
            return familyMembers.count
        }
        return subscriptionManager.familyQuotaSnapshot.used
    }

    /// Единая проверка лимита тарифа для тулбара, кнопки «Добавить» и AddMoreMemberCard (без `let` внутри ViewBuilder).
    private var canAddFamilyMemberUnderTariff: Bool {
        let currentCount = max(familyMembers.count, effectiveQuotaUsedForUI)
        return subscriptionManager.canAddFamilyMember(currentCount: currentCount).allowed
    }

    /// Подсказка, если тариф позволяет больше участников, а с сервера пришёл одиночный ростер и у пользователя нет прав управления (часто child).
    private var incompleteFamilyServerDataBannerText: String? {
        guard familyMembers.count == 1 else { return nil }
        guard subscriptionManager.familyQuotaSnapshot.max > 1 else { return nil }
        guard !canManageFamilyRoster else { return nil }
        return localizationManager.localized("family.incomplete_server_roster_hint")
    }
    
    // MARK: - Log dedup helper
    private func logOnce(_ key: String, ttl: TimeInterval, _ block: () -> Void) {
        let now = Date().timeIntervalSince1970
        let last = lastLogTimestamps[key] ?? 0
        if now - last >= ttl {
            lastLogTimestamps[key] = now
            block()
        }
    }
    
    // ✅ BUILD 96: Асинхронная загрузка для предотвращения рекурсии
    private func loadParentalRules() {
        Task { @MainActor in
            cachedParentalRules = ParentalControlRules(
                websiteBlocking: UserDefaults.standard.bool(forKey: "parental_website_blocking"),
                appBlocking: UserDefaults.standard.bool(forKey: "parental_app_blocking"),
                searchBlocking: UserDefaults.standard.bool(forKey: "parental_search_blocking"),
                safesearch: UserDefaults.standard.bool(forKey: "parental_safesearch"),
                screenTimeLimit: nil,
                bedtimeStart: nil,
                bedtimeEnd: nil,
                appLimits: nil,
                geofences: nil
            )
        }
    }

    private var familyBypassEffectiveChildId: String {
        let trimmedId = familyBypassSelectedChildId.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmedId.isEmpty { return trimmedId }
        return familyBypassLegacyChild.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    /// Карточка «Защита от обхода»: сервер — источник истины; при сбое API — локальный журнал `ParentalControlManager`.
    private func refreshBypassCardFromServer() {
        let raw = familyBypassEffectiveChildId
        let childKey: String? = raw.isEmpty ? nil : raw
        ParentalControlManager.shared.getBypassStats(childId: childKey) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let stats):
                    bypassAttemptsToday = stats.today
                    bypassAttemptsWeek = stats.week
                    bypassAttemptsBlocked = stats.blocked
                case .failure:
                    let local = ParentalControlManager.shared.localBypassAggregates(for: childKey)
                    bypassAttemptsToday = local.today
                    bypassAttemptsWeek = local.week
                    bypassAttemptsBlocked = local.blocked
                }
            }
        }
    }

    private func refreshBypassDetectorsActiveCount() {
        func triStateBool(forKey key: String) -> Bool {
            if UserDefaults.standard.object(forKey: key) == nil { return true }
            return UserDefaults.standard.bool(forKey: key)
        }
        var n = 0
        if triStateBool(forKey: "bypass_incognito_enabled") { n += 1 }
        if triStateBool(forKey: "bypass_tor_enabled") { n += 1 }
        if triStateBool(forKey: "bypass_proxy_enabled") { n += 1 }
        bypassDetectionActive = n
    }
    
    // MARK: - Navigation Helper
    
    private func navigateToMemberScreen(role: FamilyMemberCard.FamilyRole) {
        // Prevent duplicate navigation calls
        if lastFamilyOperationTime.timeIntervalSinceNow > -0.5 {
            print("⚠️ [FamilyScreen] Navigation debounced - too soon after previous action")
            return
        }
        lastFamilyOperationTime = Date()
        // ✅ ШАГ 1: При переходе в профиль родителя/ребёнка — сохраняем информацию для принудительного обновления при возврате
        print("🚨 navigateToMemberScreen triggered for \(role) — will force refresh on return")
        UserDefaults.standard.set(true, forKey: "needs_family_refresh_on_return")
        UserDefaults.standard.synchronize()

        // Navigate based on role
        let targetScreen: NavigationManager.ALADDINScreen
        switch role {
        case .parent:
            targetScreen = .parentalControl
        case .child:
            targetScreen = .childInterface
        case .teenager:
            targetScreen = .childInterface
        case .elderly:
            targetScreen = .elderlyInterface
        }
        
        print("🚨 navigateToMemberScreen: invoking navigationManager.navigateTo(\(targetScreen))")
        navigationManager.navigateTo(targetScreen)
    }

    private func evaluatePostRegistrationDeviceGuide() {
        let defaults = UserDefaults.standard
        guard defaults.bool(forKey: postRegistrationDeviceNudgePendingKey) else { return }

        // После первого успешного расширения семьи подсказка больше не нужна.
        if familyMembers.count > 1 {
            defaults.set(false, forKey: postRegistrationDeviceNudgePendingKey)
            defaults.synchronize()
            return
        }

        let now = Date().timeIntervalSince1970
        let lastShown = defaults.double(forKey: postRegistrationDeviceNudgeLastShownKey)
        if lastShown > 0, (now - lastShown) < postRegistrationDeviceNudgeCooldown {
            return
        }

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
            VisualLogger.shared.log(
                "📣 DEVICE_NUDGE shown (post-registration)",
                level: .info,
                category: "ONBOARDING"
            )
            showPostRegistrationDeviceGuide = true
        }
    }

    private func routePostRegistrationDeviceGuideCTA() {
        let role = UserDefaults.standard.string(forKey: currentUserRoleKey) ?? ""

        if canManageFamilyRoster {
            VisualLogger.shared.log(
                "🧭 DEVICE_NUDGE route: addMemberOptions (manager role)",
                level: .info,
                category: "ONBOARDING"
            )
            navigationManager.navigateTo(.addMemberOptions)
            return
        }

        if role == FamilyRole.child.rawValue || role == FamilyRole.teenager.rawValue {
            VisualLogger.shared.log(
                "🧭 DEVICE_NUDGE route: qrCode (child/teen)",
                level: .info,
                category: "ONBOARDING"
            )
            navigationManager.navigateTo(.qrCode)
            return
        }

        if role == FamilyRole.elderly.rawValue {
            VisualLogger.shared.log(
                "🧭 DEVICE_NUDGE route: invitationCode (elderly)",
                level: .info,
                category: "ONBOARDING"
            )
            navigationManager.navigateTo(.invitationCode)
            return
        }

        VisualLogger.shared.log(
            "🧭 DEVICE_NUDGE route: addMemberOptions (fallback)",
            level: .info,
            category: "ONBOARDING"
        )
        navigationManager.navigateTo(.addMemberOptions)
    }
    
    // MARK: - Family Members Management
    
    // Загрузка участников семьи из UserDefaults и синхронизация с API
    private func loadFamilyMembers() {
        guard !isFamilyLoadInProgress else {
            print("⚠️ [loadFamilyMembers] Загрузка уже выполняется, пропускаем повторный вызов")
            return
        }
        isFamilyLoadInProgress = true
        defer { isFamilyLoadInProgress = false }

        logger.business("Loading family members from storage")
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Синхронизируем UserDefaults перед чтением
        UserDefaults.standard.synchronize()

        // Кэш ростера мог остаться от другой семьи / экрана чата при пустом `family_id` — иначе на 1–5 с показывается «чужой» ребёнок, пока не придёт sync.
        if !FamilyLocalStore.validatePersistedRosterAgainstCurrentFamily() {
            familyMembers = []
        }
        
        // ✅ OPTIMIZATION: Update admin status early
        updateAdminStatus()
        
        // 1) Гидратация из кэша ПЕРЕД API: раньше вызывали sync (async) и сразу читали UD — пока sync не
        //    завершился, диск часто содержал старый список и перетирал in-memory список после add (новый участник пропадал).
        // 2) Не «сжимаем» список из UserDefaults, если в памяти уже больше участников (save мог отложиться из-за debounce).
        if let savedData = UserDefaults.standard.data(forKey: familyMembersKey),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData),
           !decoded.isEmpty {
            let deduped = deduplicateFamilyMembers(decoded)
            let currentIds = Set(familyMembers.map { $0.id })
            let loadedIds = Set(deduped.map { $0.id })
            let cacheNotStaleVersusMemory = familyMembers.isEmpty || deduped.count >= familyMembers.count
            if cacheNotStaleVersusMemory && currentIds != loadedIds {
                familyMembers = deduped
                print("✅ Loaded family members from UserDefaults (deduped): \(familyMembers.count)")
            } else if cacheNotStaleVersusMemory && currentIds == loadedIds {
                print("🔄 Loaded family members: список не изменился (\(familyMembers.count) участников), пропускаем обновление")
            } else {
                #if DEBUG
                print("⚠️ [loadFamilyMembers] Skipped applying UserDefaults cache (would shrink \(familyMembers.count) → \(deduped.count)); waiting for API sync")
                #endif
            }
        }

        // Auto-heal stale persisted quota snapshot: empty roster with non-zero used.
        if familyMembers.isEmpty,
           subscriptionManager.familyQuotaSnapshot.source == .persistedCache,
           subscriptionManager.familyQuotaSnapshot.used > 0 {
            UserDefaults.standard.set(0, forKey: "family_roster_used_last")
            UserDefaults.standard.set(0, forKey: "family_remaining")
            UserDefaults.standard.synchronize()
            MetricsService.shared.trackUserAction(
                action: "quota_vs_roster_mismatch",
                parameters: [
                    "condition": "roster_empty_used_gt_zero",
                    "used": subscriptionManager.familyQuotaSnapshot.used,
                    "max": subscriptionManager.familyQuotaSnapshot.max
                ]
            )
            VisualLogger.shared.log("🩹 FAMILY AUTO-HEAL: reset stale persisted quota used to 0 (empty roster)", level: .warning, category: "FAMILY")
        }
        
        // 2) Синхронизация с сервером (источник истины после merge в syncFamilyMembersFromAPI)
        syncFamilyMembersFromAPI()
        
        // 2. Если нет сохранённых данных - создать карточку текущего пользователя
        // ✅ ИСПРАВЛЕНИЕ: Не перезаписываем, если уже есть участники
        if familyMembers.isEmpty {
            let hasServerFamilyId = !(UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey) ?? "").isEmpty
            let hasSeededMember = UserDefaults.standard.bool(forKey: familyMemberSeededKey)
            guard !hasServerFamilyId, !hasSeededMember else {
                print("ℹ️ [loadFamilyMembers] Seed пропущен (hasServerFamilyId=\(hasServerFamilyId), hasSeededMember=\(hasSeededMember))")
                return
            }

            // Без `family_id` на сервере это только плейсхолдер «владелец устройства» — всегда родитель.
            // Иначе случайный `current_user_role=child` (детский режим / старый UD) рисовал «ребёнка» в блоке «Участники семьи».
            let userName = UserDefaults.standard.string(forKey: currentUserNameKey) ?? localizationManager.localized("family_you")
            let role: FamilyMemberCard.FamilyRole = .parent
            familyMembers = [
                FamilyMemberData(
                    name: userName,
                    role: role,
                    avatar: getAvatarForRole(role),
                    status: .protected,
                    threatsBlocked: 0,
                    lastActive: localizationManager.localized("family_now")
                )
            ]
            print("✅ Created default family placeholder (parent): \(userName)")
            
            // Сохраняем созданный список только если он был пуст
            saveFamilyMembers()
            UserDefaults.standard.set(true, forKey: familyMemberSeededKey)
        }
    }

    /// Ручная очистка локального кэша списка участников (кнопка под блоком «Участники семьи»). Семья на сервере не удаляется.
    private func performClearLocalFamilyRosterCacheAndReload() {
        FamilyLocalStore.clearLocalFamilyRosterCacheForManualReset()
        applyLocalFamilyResetAndForceReload(
            logMessage: "🧹 FAMILY: user cleared local roster cache (manual soft reset)"
        )
    }

    /// Полный локальный reset family-контекста на устройстве (без JWT/trial/subscription).
    private func performFullLocalFamilyContextResetAndReload() {
        FamilyLocalStore.clearLocalFamilyContextForManualReset()
        applyLocalFamilyResetAndForceReload(
            logMessage: "🧨 FAMILY: user performed full local family context reset"
        )
    }

    private func applyLocalFamilyResetAndForceReload(logMessage: String) {
        familyMembers.removeAll()
        notSeenCounters.removeAll()
        serverMemberIdsLatest = []
        VisualLogger.shared.log(logMessage, level: .info, category: "FAMILY")

        // Force subscription sync after reset so quota snapshot is immediately re-aligned with backend.
        Task { @MainActor in
            await SubscriptionManager.shared.forceSync()
            loadFamilyMembers()
        }
    }

    /// Лёгкая перезагрузка только из локального storage без API sync.
    /// Нужна после локального добавления участника, чтобы UI обновлялся мгновенно.
    // ✅ FIXED: reloadFamilyMembersFromStorageOnly — now respects guards and only cleans if needed
    private func reloadFamilyMembersFromStorageOnly() {
        let now = Date()
        guard !isFamilyLoadInProgress && !isFamilySyncInProgress && now.timeIntervalSince(lastFamilyOperationTime) >= 0.3 else {
            #if DEBUG
            print("⚠️ [reloadFamilyMembersFromStorageOnly] Skipped (in progress or debounced)")
            #endif
            return
        }
        lastFamilyOperationTime = now

        if !FamilyLocalStore.validatePersistedRosterAgainstCurrentFamily() {
            familyMembers = []
            return
        }

        guard let savedData = UserDefaults.standard.data(forKey: familyMembersKey),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            return
        }

        let deduped = deduplicateFamilyMembers(decoded)
        if deduped.count != familyMembers.count || familyMembers.isEmpty {
            familyMembers = deduped
            cleanupFamilyMembers(serverIds: serverMemberIdsLatest)
            #if DEBUG
            print("✅ [reloadFamilyMembersFromStorageOnly] Loaded \(familyMembers.count) family members after cleanup")
            #endif
        } else {
            #if DEBUG
            print("🔄 [reloadFamilyMembersFromStorageOnly] No change in storage, skipping reload")
            #endif
        }
    }

    /// fam-7: явный repair по текущему ростеру на экране + уведомление (перезагрузка storage и отложенный GET).
    private func runFamilyIdentityRepairFromCurrentRoster() {
        guard !familyMembers.isEmpty else { return }
        guard !isFamilyIdentityRepairing else { return }
        isFamilyIdentityRepairing = true
        FamilyLocalStore.repairFamilyIdentityFromLocalRoster(familyMembers)
        UserDefaults.standard.synchronize()
        FamilyLocalStore.notifyFamilyMembersUpdated()
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
            isFamilyIdentityRepairing = false
            updateAdminStatus()
        }
    }
    
    // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #2: Синхронизация участников семьи с сервером
    private func syncFamilyMembersFromAPI() {
        guard !isFamilySyncInProgress else {
            print("⚠️ [syncFamilyMembersFromAPI] Синхронизация уже выполняется, пропускаем повторный вызов")
            return
        }

        // Проверяем, есть ли family_id (канонический ключ — FamilyLocalStore)
        guard let familyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey),
              !familyId.isEmpty else {
            print("⚠️ [syncFamilyMembersFromAPI] Family ID не найден, пропускаем синхронизацию")
            return
        }
        
        isFamilySyncInProgress = true
        syncEngine.publish(domain: .family, operation: "family_sync_start", state: .syncing)
        print("🔄 [syncFamilyMembersFromAPI] Начинаем синхронизацию участников семьи с сервером")
        VisualLogger.shared.log("🔄 FAMILY SYNC: start", level: .info, category: "FAMILY")
        let apiService = APIService.shared
        
        apiService.getFamilyMembersWithSyncContext { result in
            DispatchQueue.main.async {
                defer { self.isFamilySyncInProgress = false }
                switch result {
                case .success(let syncContext):
                    let members = syncContext.members
                    let skipCrossFamilyMerge = syncContext.shouldReplaceLocalMembersInsteadOfMerge
                    if skipCrossFamilyMerge {
                        VisualLogger.shared.log(
                            "🛡️ FAMILY SYNC: skip local↔server merge (409 recovery=\(syncContext.recoveredFromFamilyContextConflict), family before/after: «\(syncContext.familyIdSnapshotBeforeFetch)» → «\(syncContext.familyIdSnapshotAfterFetch)»)",
                            level: .warning,
                            category: "FAMILY"
                        )
                    }
                    self.familySyncContextBanner = nil
                    let serverIds = members.map { $0.id }
                    let localIdsBefore = self.familyMembers.map { $0.id }
                    let localCount = localIdsBefore.count
                    let serverCount = members.count
                    
                    // ✅ EXPLICIT DESYNC DETECTION (no more silent masking)
                    if localCount != serverCount {
                        VisualLogger.shared.log("⚠️ FAMILY_DESYNC detected: local=\(localCount), server=\(serverCount). Missing on server: \(Set(localIdsBefore).subtracting(Set(serverIds)))", level: .warning, category: "FAMILY")
                    }
                    
                    print("✅ [syncFamilyMembersFromAPI] Получено \(serverCount) участников с сервера (local was \(localCount))")
                    VisualLogger.shared.log("✅ FAMILY SYNC: server=\(serverCount), local=\(localCount)", level: .success, category: "FAMILY")
                    let serverIdsStr = serverIds.joined(separator: ", ")
                    let localIdsBeforeStr = localIdsBefore.joined(separator: ", ")
                    VisualLogger.shared.log("🧩 IDs server: \(serverIdsStr)", level: .debug, category: "FAMILY")
                    VisualLogger.shared.log("🧩 IDs local(before): \(localIdsBeforeStr)", level: .debug, category: "FAMILY")
                    // Сохраняем последний набор серверных ID для валидации удаления
                    self.serverMemberIdsLatest = Set(serverIds)
                    FamilyLocalStore.reconcileYourMemberIdAfterFamilyMembersResponse(
                        serverResponseIds: serverIds,
                        inMemoryRoster: self.familyMembers
                    )
                    
                    // Обновление счётчиков not-seen теперь выполняется НИЖЕ и только при полном ответе, не при partial subset

                    // Не перетираем локальный непустой список пустым серверным ответом.
                    // Это защищает UI при задержке server-side propagation после локального добавления.
                    if members.isEmpty && !self.familyMembers.isEmpty {
                        print("ℹ️ [syncFamilyMembersFromAPI] Сервер вернул 0, локально есть \(self.familyMembers.count) — сохраняем локальный список")
                        VisualLogger.shared.log("ℹ️ FAMILY SYNC: server empty while local non-empty — keep local", level: .warning, category: "FAMILY")
                        return
                    }
                    
                    // Защита от частичных ответов сервера:
                    // если сервер прислал меньше участников, чем локально, не "усыхаем" список,
                    // а объединяем (merge) и оставляем максимум информации, пока не придёт полный ответ.
                    // После 409 / смены канонического family_id не смешиваем две семьи (B+C).
                    let localBefore = skipCrossFamilyMerge ? [] : self.familyMembers

                    // Захватываем localizationManager до замыкания map
                    let locManager = self.localizationManager
                    
                    // Преобразуем FamilyMemberResponse в FamilyMemberData
                    let convertedMembers: [FamilyMemberData] = members.map { member in
                        // Определяем роль
                        let normalizedRole = member.role.lowercased()
                        let role: FamilyMemberCard.FamilyRole
                        let parentLabels = Set(["parent", locManager.localized("family_role_parent_label").lowercased()])
                        let childLabels = Set(["child", locManager.localized("family_role_child_label").lowercased()])
                        let teenLabels = Set(["teenager", "teen", locManager.localized("family_role_teen_label").lowercased()])
                        let elderlyLabels = Set(["elderly", "grandparent", locManager.localized("family_role_elderly_label").lowercased()])
                        
                        switch normalizedRole {
                        case _ where parentLabels.contains(normalizedRole):
                            role = .parent
                        case _ where childLabels.contains(normalizedRole):
                            role = .child
                        case _ where teenLabels.contains(normalizedRole):
                            role = .teenager
                        case _ where elderlyLabels.contains(normalizedRole):
                            role = .elderly
                        default:
                            role = .parent
                        }
                        
                        // Получаем аватар для роли
                        let avatar: String
                        switch role {
                        case .parent: avatar = "👨"
                        case .child: avatar = "👧"
                        case .teenager: avatar = "🧒"
                        case .elderly: avatar = "👵"
                        }
                        
                        // Преобразуем статус из API в ProtectionStatus
                        let protectionStatus: FamilyMemberCard.ProtectionStatus
                        switch (member.status ?? "protected").lowercased() {
                        case "protected":
                            protectionStatus = .protected
                        case "warning":
                            protectionStatus = .warning
                        case "danger":
                            protectionStatus = .danger
                        case "offline":
                            protectionStatus = .offline
                        default:
                            protectionStatus = .protected // По умолчанию защищён
                        }
                        
                        return FamilyMemberData(
                            id: member.id,
                            serverMemberId: member.id,
                            localOnly: false,
                            name: member.name,
                            role: role,
                            avatar: avatar,
                            status: protectionStatus,
                            threatsBlocked: member.threatsBlocked ?? 0,
                            lastActive: member.lastActive ?? ""
                        )
                    }

                    // ✅ SIMPLIFIED MERGE: локальные записи (в т.ч. только локальные id), затем перезапись данными сервера по ключу MEM_*.
                    // Не подменяем роль «первого в списке» на .parent — это давало детям роль родителя после сортировки и ломало delete/isMe.
                    var mergedById: [String: FamilyMemberData] = [:]
                    if skipCrossFamilyMerge {
                        for item in convertedMembers {
                            let key = item.serverMemberId ?? item.id
                            mergedById[key] = item
                        }
                    } else {
                        for item in localBefore {
                            let key = item.serverMemberId ?? item.id
                            mergedById[key] = item
                        }
                        for item in convertedMembers {
                            let key = item.serverMemberId ?? item.id
                            mergedById[key] = item
                        }
                    }
                    
                    var mergedMembers = Array(mergedById.values)
                    
                    // ✅ STABLE ORDER using persisted familyAdditionOrder (new members ALWAYS at BOTTOM across syncs/restarts)
                    // Prioritizes additionOrder, falls back to current local order for robustness
                    let additionOrder = self.familyAdditionOrder
                    let localOrder = localBefore.map { $0.id }
                    mergedMembers.sort { (a, b) in
                        let indexA = additionOrder.firstIndex(of: a.id) ?? localOrder.firstIndex(of: a.id) ?? Int.max
                        let indexB = additionOrder.firstIndex(of: b.id) ?? localOrder.firstIndex(of: b.id) ?? Int.max
                        if indexA == Int.max && indexB == Int.max {
                            return false // New members (not in order) stay at the END (stable)
                        }
                        return indexA < indexB
                    }
                    VisualLogger.shared.log("📋 FAMILY ORDER: sorted using additionOrder(\(additionOrder.count)) + local(\(localOrder.count))", level: .debug, category: "FAMILY")

                    let serverIdSet = Set(convertedMembers.map { $0.id })
                    let localIdSet = Set(localBefore.map { $0.id })
                    let hasKnownServerMembers = localBefore.contains { ($0.serverMemberId != nil) || $0.id.hasPrefix("MEM_") }
                    let storedFid = familyId.trimmingCharacters(in: .whitespacesAndNewlines)
                    let lastResolved = (UserDefaults.standard.string(forKey: FamilyLocalStore.lastResolvedFamilyIdKey) ?? "")
                        .trimmingCharacters(in: .whitespacesAndNewlines)
                    let syncFlags = FamilyRosterSyncMergePolicy.computeFlags(
                        serverIds: serverIdSet,
                        localIds: localIdSet,
                        serverListNonEmpty: !convertedMembers.isEmpty,
                        storedFamilyId: storedFid,
                        lastResolvedFamilyId: lastResolved
                    )
                    let isServerSubset = syncFlags.isServerSubset
                    let serverFamilyContextConfirmed = syncFlags.serverFamilyContextConfirmed
                    let effectivePartialSubset = syncFlags.effectivePartialSubset
                    if serverFamilyContextConfirmed && isServerSubset {
                        VisualLogger.shared.log(
                            "🛡️ FAMILY SYNC: server returned fewer ids than local while family context matches — keeping merged roster (no server-only prune; GET may be transient/partial)",
                            level: .warning,
                            category: "FAMILY"
                        )
                    }

                    if effectivePartialSubset {
                        print("⚠️ [syncFamilyMembersFromAPI] Частичный ответ сервера (\(serverIdSet.count) < \(localIdSet.count)). Сохраняем ВСЕХ известных участников с serverId.")
                        VisualLogger.shared.log("⚠️ FAMILY SYNC: partial server subset (server \(serverIdSet.count) < local \(localIdSet.count)). KEEPING known members", level: .warning, category: "FAMILY")
                    }

                    // Обновляем только при реальном изменении
                    let oldIds = Set(self.familyMembers.map { $0.id })
                    let newIds = Set(mergedMembers.map { $0.id })
                    
                    let currentRetryCount = UserDefaults.standard.integer(forKey: "family_sync_partial_retry_count")
                    let parentOrElderMissingFromServer = localBefore.contains { m in
                        guard m.role == .parent || m.role == .elderly else { return false }
                        let keys: [String] = [m.id, m.serverMemberId]
                            .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
                            .filter { !$0.isEmpty }
                        guard !keys.isEmpty else { return false }
                        return !keys.contains { serverIdSet.contains($0) }
                    }
                    let mergePick = FamilyRosterSyncMergePolicy.chooseFinalSource(
                        flags: syncFlags,
                        partialRetryCount: currentRetryCount,
                        hasKnownServerMembersInLocal: hasKnownServerMembers,
                        localParentOrElderMissingFromServer: parentOrElderMissingFromServer
                    )
                    var finalMembers = mergePick.source == .merged ? mergedMembers : convertedMembers
                    var mergeOutcome = mergePick.mergeOutcome
                    if mergeOutcome == "server_truth_after_retries_no_known_server_ids" {
                        VisualLogger.shared.log("⚠️ FAMILY SYNC: accepting server truth after 3 retries (NO known server IDs)", level: .warning, category: "FAMILY")
                    } else if mergeOutcome == "keep_merged_partial_subset" {
                        print("🛡️ [partial subset] Защита сработала: сохраняем \(mergedMembers.count) участников вместо \(convertedMembers.count) от сервера")
                    }

                    // 🔥 НОВОЕ: Агрессивная дедупликация ВСЕГДА (даже при partial subset) — теперь local=9 → ~2
                    // Это ключевой фикс: partial subset больше не оставляет 9 дублей.
                    finalMembers = self.deduplicateFamilyMembers(finalMembers)
                    let finalIds = Set(finalMembers.map { $0.id })

                    // FINAL v3: Apply merged server+local list, then cleanup (must bypass sync guards — this runs while isFamilySyncInProgress).
                    let finalAfterCleanup = self.deduplicateFamilyMembers(finalMembers)
                    self.familyMembers = finalAfterCleanup
                    self.cleanupFamilyMembers(serverIds: serverIdSet, allowDuringFamilySync: true)
                    self.saveFamilyMembers(allowDuringFamilySync: true)

                    let rosterFamilyId = familyId.trimmingCharacters(in: .whitespacesAndNewlines)
                    ProfileManager.shared.syncChildRosterFromServer(
                        members: members,
                        familyId: rosterFamilyId.isEmpty ? nil : rosterFamilyId,
                        removeMissingServerLinkedChildren: FamilyRosterSyncMergePolicy.shouldRemoveMissingServerLinkedChildren(
                            serverMemberIds: members.map(\.id),
                            localMemberIds: localBefore.map(\.id)
                        )
                    )
                    if let summary = ProfileManager.shared.lastChildRosterReconcileSummary {
                        VisualLogger.shared.log("🔄 FAMILY/UI roster reconcile: \(summary)", level: .info, category: "FAMILY")
                    }
                    
                    let localIdsAfter = self.familyMembers.map { $0.id }
                    VisualLogger.shared.log("💾 FAMILY SYNC: saved merged+deduped+cleaned members (\(localIdsAfter.count))", level: .success, category: "FAMILY")
                    let localIdsAfterStr = localIdsAfter.joined(separator: ", ")
                    VisualLogger.shared.log("🧩 IDs local(after): \(localIdsAfterStr)", level: .debug, category: "FAMILY")

                    // ✅ PROD FIX: Улучшенная защита от исчезновения (partial subset). 
                    // Никогда не позволяем notSeenCounters "съедать" известных участников с serverMemberId.
                    // Сбрасываем retryCount после addFamilyMember (см. ниже).
                    if effectivePartialSubset && currentRetryCount < self.maxPartialSyncRetries {
                        // Show non-intrusive sync banner while waiting for full server list
                        if !showSyncBanner { showSyncBanner = true }
                        
                        UserDefaults.standard.set(currentRetryCount + 1, forKey: "family_sync_partial_retry_count")
                        // Exponential backoff: 1.5s, 3.0s, 6.0s
                        let delays: [Double] = [1.5, 3.0, 6.0]
                        let delay = delays[min(currentRetryCount, delays.count - 1)]
                        logOnce("FAMILY_SYNC_RETRY_\(currentRetryCount + 1)", ttl: delay) {
                            let delayStr = String(format: "%.1f", delay)
                            VisualLogger.shared.log("🔁 FAMILY SYNC: retry after partial subset (\(currentRetryCount + 1)/\(self.maxPartialSyncRetries)) in \(delayStr)s", level: .warning, category: "FAMILY")
                        }
                        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
                            self.syncFamilyMembersFromAPI()
                        }
                    } else {
                        // Полный ответ ИЛИ после максимума ретраев — сбрасываем счётчик и баннер
                        UserDefaults.standard.set(0, forKey: "family_sync_partial_retry_count")
                        if showSyncBanner { 
                            showSyncBanner = false 
                            print("✅ [syncFamilyMembersFromAPI] Синхронизация завершена — баннер скрыт")
                        }
                        
                        // ✅ SOFTENED: notSeenCounters no longer aggressively prunes members with serverMemberId
                        // This prevents "magical" disappearance of locally created members
                        var updatedCounters = self.notSeenCounters
                        for member in self.familyMembers {
                            let memberIds = [member.id, member.serverMemberId].compactMap { $0 }
                            if memberIds.contains(where: { serverIdSet.contains($0) || $0.hasPrefix("MEM_") }) {
                                updatedCounters[member.id] = 0
                                if let sid = member.serverMemberId {
                                    updatedCounters[sid] = 0
                                }
                            } else {
                                // Max 1 instead of 3+ to reduce pruning
                                let current = updatedCounters[member.id] ?? 0
                                updatedCounters[member.id] = min(current + 1, 1)
                            }
                        }
                        self.notSeenCounters = updatedCounters
                        
                        // ✅ NO MORE AGGRESSIVE CLEANUP on every sync - only if clearly stale
                        let beforeCount = self.familyMembers.count
                        self.familyMembers.removeAll { (self.notSeenCounters[$0.id] ?? 0) >= self.maxNotSeenConsecutiveSyncs }
                        if self.familyMembers.count != beforeCount {
                            self.saveFamilyMembers(allowDuringFamilySync: true)
                            print("🧹 [syncFamilyMembersFromAPI] Удалены фантомные участники (not seen >= \(self.maxNotSeenConsecutiveSyncs))")
                            VisualLogger.shared.log("🧹 PRUNED \(beforeCount - self.familyMembers.count) stale members", level: .warning, category: "FAMILY")
                        } else {
                            print("🛡️ [syncFamilyMembersFromAPI] notSeenCounters сброшены, pruning предотвращён (count=\(self.familyMembers.count))")
                        }
                    }

                    FamilyLocalStore.reconcileYourMemberIdAfterFamilyMembersResponse(
                        serverResponseIds: members.map(\.id),
                        inMemoryRoster: self.familyMembers
                    )

                    let snapFlags = FamilySyncDebugSnapshot.Flags(
                        skipCrossFamilyMerge: skipCrossFamilyMerge,
                        effectivePartialSubset: effectivePartialSubset,
                        isServerSubset: isServerSubset,
                        serverFamilyContextConfirmed: serverFamilyContextConfirmed,
                        mergeOutcome: mergeOutcome,
                        partialRetryCountAtDecision: currentRetryCount,
                        storedFamilyId: familyId.trimmingCharacters(in: .whitespacesAndNewlines),
                        lastResolvedFamilyId: (UserDefaults.standard.string(forKey: FamilyLocalStore.lastResolvedFamilyIdKey) ?? "")
                            .trimmingCharacters(in: .whitespacesAndNewlines)
                    )
                    FamilySyncDebugSnapshot.writeAfterFamilyMembersSync(
                        serverMembers: members,
                        localBefore: localBefore,
                        localAfter: self.familyMembers,
                        flags: snapFlags
                    )

                    print("✅ [syncFamilyMembersFromAPI] Синхронизация завершена: \(convertedMembers.count) участников сохранено")
                    VisualLogger.shared.log("✅ FAMILY SYNC: completed", level: .success, category: "FAMILY")
                    self.syncEngine.publish(
                        domain: .family,
                        operation: "family_sync_complete",
                        state: .synced,
                        metadata: ["memberCount": String(convertedMembers.count)]
                    )
                    self.updateAdminStatus()  // ✅ OPTIMIZATION: Refresh cached admin status after sync
                    self.clearDeleteButtonCache(reason: "after_sync")  // Invalidate only after real data change
                    
                case .failure(let error):
                    print("❌ [syncFamilyMembersFromAPI] Ошибка синхронизации: \(error.localizedDescription)")
                    let net = NetworkError.from(error)
                    if net.isFamilyMembersContextConflict {
                        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.lastResolvedFamilyIdKey)
                        self.familySyncContextBanner = self.localizationManager.currentLanguage == .russian
                            ? "Данные семьи на устройстве не совпали с вашим аккаунтом. Закройте и снова откройте раздел «Семья» или выйдите и войдите в приложение."
                            : "The family data on this device didn’t match your account. Close and reopen Family, or sign out and sign in again."
                        VisualLogger.shared.log("⚠️ FAMILY SYNC: 409 context conflict — showing user banner", level: .warning, category: "FAMILY")
                    } else {
                        VisualLogger.shared.log("❌ FAMILY SYNC: error \(error.localizedDescription)", level: .error, category: "FAMILY")
                    }
                    self.syncEngine.publish(
                        domain: .family,
                        operation: "family_sync_error",
                        state: .error(error.localizedDescription)
                    )
                    // При ошибке продолжаем использовать локальные данные
                }
            }
        }
    }
    
    // ✅ UPDATED: Uses single source of truth from SubscriptionManager.canAddFamilyMember
    // Eliminates bypass and ensures consistent enforcement across all flows
    private func addFamilyMember(_ member: FamilyMemberData) {
        let currentCount = max(familyMembers.count, effectiveQuotaUsedForUI)
        let (allowed, message, _) = subscriptionManager.canAddFamilyMember(currentCount: currentCount)

        if !allowed {
            print("🚫 [addFamilyMember] Tariff limit reached (\(currentCount)/\(subscriptionManager.familyQuotaSnapshot.max)). \(message ?? "")")
            VisualLogger.shared.log("🚫 TARIFF LIMIT: reached \(currentCount)/\(subscriptionManager.familyQuotaSnapshot.max) — block add", level: .warning, category: "FAMILY")
            // TODO: Show user-facing alert with upgrade option (handled in UI layer)
            return
        }

        guard canManageFamilyRoster else {
            print("🚫 [addFamilyMember] Blocked — only parents may add members to the roster")
            VisualLogger.shared.log("🚫 FAMILY ADD: denied — canManageFamilyRoster=false", level: .warning, category: "FAMILY")
            return
        }

        // Improved duplicate check using canonical logic (your_member_id or serverId) — fixes infinite self-duplicates
        let myMemberId = UserDefaults.standard.string(forKey: "your_member_id") ?? ""
        let isDuplicate = familyMembers.contains { existingMember in
            let sameCanonical = (existingMember.id == member.id || 
                                (existingMember.serverMemberId != nil && existingMember.serverMemberId == member.serverMemberId) ||
                                (!myMemberId.isEmpty && (existingMember.id == myMemberId || existingMember.serverMemberId == myMemberId) &&
                                 (member.id == myMemberId || member.serverMemberId == myMemberId)))
            return sameCanonical || (existingMember.name.lowercased() == member.name.lowercased() && existingMember.role == member.role)
        }
        
        if !isDuplicate {
            // ✅ Важное улучшение: если участник уже имеет serverMemberId — используем его
            var memberToAdd = member
            if memberToAdd.serverMemberId == nil && memberToAdd.id.hasPrefix("MEM_") {
                memberToAdd.serverMemberId = memberToAdd.id
            }
            
            familyMembers.append(memberToAdd)
            
            // ✅ STABLE ORDER: Append new member ID to persisted additionOrder (ensures it stays at BOTTOM)
            var currentOrder = familyAdditionOrder
            if !currentOrder.contains(memberToAdd.id) {
                currentOrder.append(memberToAdd.id)
                // Use direct UserDefaults write to avoid mutating computed property from non-mutating context
                UserDefaults.standard.set(currentOrder, forKey: familyAdditionOrderKey)
                UserDefaults.standard.synchronize()
                VisualLogger.shared.log("📋 FAMILY ORDER: appended new member \(memberToAdd.name) (id=\(memberToAdd.id)) — now at bottom", level: .info, category: "FAMILY")
            }
            
            saveFamilyMembers(allowDuringFamilySync: true)
            print("✅ Added new family member: \(memberToAdd.name) (\(memberToAdd.role)) [serverId=\(memberToAdd.serverMemberId ?? "pending")]")
            VisualLogger.shared.log("➕ FAMILY ADD(local): \(memberToAdd.name) [\(memberToAdd.role)] serverId=\(memberToAdd.serverMemberId ?? "pending")", level: .info, category: "FAMILY")

            // ✅ PROD FIX: Сбрасываем счётчики notSeenCounters + retry count для нового участника
            // Это предотвращает исчезновение сразу после добавления
            notSeenCounters[memberToAdd.id] = 0
            if let serverId = memberToAdd.serverMemberId {
                notSeenCounters[serverId] = 0
            }
            UserDefaults.standard.set(0, forKey: "family_sync_partial_retry_count")
            UserDefaults.standard.synchronize()
            // saveNotSeenCounters() встроено в saveFamilyMembers() — вызываем его ниже

            // Локальное сохранение оставляем как кэш для мгновенного UI,
            // затем сразу дожимаем серверную запись и повторный fetch.
            Task {
                // Быстрая проверка контекста авторизации/семьи, чтобы не отправлять запрос в неверном контексте
                let currentToken = AppConfig.authToken ?? KeychainManager.shared.loadString(forKey: .authToken)
                let currentFamilyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)
                guard let _ = currentToken, let famId = currentFamilyId, !member.name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                    await MainActor.run {
                        print("⚠️ [addFamilyMember] Пропускаем серверный add: нет валидного токена/семьи или пустое имя")
                        VisualLogger.shared.log("⚠️ FAMILY ADD(server): skipped — invalid token/familyId or empty name", level: .warning, category: "FAMILY")
                    }
                    return
                }
                do {
                    let roleToSend = serverRole(for: member.role)
                    VisualLogger.shared.log("➡️ FAMILY ADD(debug): familyId=\(famId) name=\(member.name) role=\(roleToSend)", level: .info, category: "FAMILY")
                    let resp = try await APIService.shared.addFamilyMember(name: member.name, role: roleToSend)
                    await MainActor.run {
                        // ✅ PROD FIX: Помечаем admin-add + СБРАСЫВАЕМ retry count (ключевой фикс исчезновения)
                        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "admin_add_recent_ts")
                        UserDefaults.standard.set(0, forKey: "family_sync_partial_retry_count")
                        UserDefaults.standard.synchronize()
                        
                        // Обновляем локальный элемент serverMemberId и подменяем id, если нужно (через копию массива)
                        var arr = self.familyMembers
                        if let idx = arr.firstIndex(where: { $0.name == member.name && $0.role == member.role && (($0.serverMemberId == nil) || !$0.id.hasPrefix("MEM_")) }) {
                            var updated = arr[idx]
                            updated.serverMemberId = resp.id
                            if !updated.id.hasPrefix("MEM_") {
                                updated.id = resp.id
                            }
                            arr[idx] = updated
                            self.familyMembers = arr
                            self.saveFamilyMembers(allowDuringFamilySync: true)
                            VisualLogger.shared.log("✅ FAMILY ADD(local map): bound server id \(resp.id) to \(member.name)", level: .success, category: "FAMILY")
                        }
                        print("✅ [addFamilyMember] Участник добавлен на сервер, запускаем синхронизацию (retry=0)")
                        VisualLogger.shared.log("✅ FAMILY ADD(server): \(member.name) — success, syncing... (partial_retry_reset)", level: .success, category: "FAMILY")
                        syncFamilyMembersFromAPI()
                    }
                } catch {
                    await MainActor.run {
                        print("⚠️ [addFamilyMember] Локально добавлено, но сервер не подтвердил: \(error.localizedDescription)")
                        VisualLogger.shared.log("❌ FAMILY ADD(server): failed \(error.localizedDescription)", level: .error, category: "FAMILY")
                    }
                }
            }
        } else {
            print("⚠️ Family member already exists: \(member.name) (\(member.role))")
            VisualLogger.shared.log("ℹ️ FAMILY ADD(local): duplicate \(member.name) — skipped", level: .info, category: "FAMILY")
        }
    }

    // Quick add flow removed; using navigation to AddMemberOptionsScreen
    
    // ✅ НОВАЯ ФУНКЦИЯ: Удаление участника семьи
    private func requestRemoveFamilyMember(_ member: FamilyMemberData) {
        removeMemberErrorMessage = nil
        VisualLogger.shared.log("🗑️ REMOVE TAP: request for \(member.name) id=\(member.id)", level: .info, category: "FAMILY")
        removeMemberSuccessMessage = nil

        // Блокируем удаление для локальных-only участников, которых ещё нет на сервере
        if (member.localOnly ?? false) || (member.serverMemberId == nil && !member.id.hasPrefix("MEM_")) {
            VisualLogger.shared.log("ℹ️ FAMILY REMOVE: pending member tapped. Wait for server sync.", level: .info, category: "FAMILY")
            removeMemberErrorMessage = localizationManager.currentLanguage == .russian
                ? "Этот участник ещё не синхронизирован с сервером. Подождите подтверждения и повторите."
                : "This member is not yet synchronized with the server. Please try again after sync."
            return
        }

        guard canManageFamilyRoster else {
            removeMemberErrorMessage = localizationManager.currentLanguage == .russian
                ? "Удалять участников могут только родители (до двух родительских аккаунтов в семье)."
                : "Only parent accounts (up to two per family) can remove members."
            return
        }

        let myMemberId = UserDefaults.standard.string(forKey: "your_member_id")
        if let myMemberId = myMemberId, !myMemberId.isEmpty, (member.serverMemberId == myMemberId || member.id == myMemberId) {
            removeMemberErrorMessage = localizationManager.currentLanguage == .russian
                ? "Нельзя удалить самого себя из семьи."
                : "You cannot remove yourself from family."
            return
        }

        if member.role == .parent {
            let parentCount = familyMembers.filter { $0.role == .parent }.count
            if parentCount <= 1 {
                removeMemberErrorMessage = localizationManager.currentLanguage == .russian
                    ? "Нельзя удалить последнего администратора."
                    : "Cannot remove the last administrator."
                return
            }
        }

        // Разрешаем удаление, если у участника есть serverMemberId или корректный MEM_* id,
        // даже если последний серверный список ещё не подтянулся.
        let hasServerId = (member.serverMemberId != nil) || member.id.hasPrefix("MEM_")
        if !hasServerId {
            self.syncFamilyMembersFromAPI()
            removeMemberErrorMessage = localizationManager.currentLanguage == .russian
                ? "Данные ещё синхронизируются. Обновите список семьи и повторите."
                : "Data is still synchronizing. Refresh family list and try again."
            return
        }

        pendingRemovalMember = member
        VisualLogger.shared.log("🗑️ REMOVE DIALOG: opened for \(member.name) id=\(member.id)", level: .info, category: "FAMILY")
    }

    private func removeFamilyMember(_ member: FamilyMemberData) {
        logger.business("Removing family member: \(member.name)")
        // Проверяем, что пользователь является администратором или родителем
        guard canManageFamilyRoster else {
            print("⚠️ Only parent/elderly roster roles can remove family members")
            return
        }
        if deletingMemberIds.contains(member.id) {
            return
        }
        deletingMemberIds.insert(member.id)
        
        print("🗑️ [removeFamilyMember] Начало удаления: \(member.name) (ID: \(member.id))")
        print("🗑️ [removeFamilyMember] Текущее количество участников: \(familyMembers.count)")
        let memberToRemove = member
        
        // Оптимистическое скрытие карточки + удаляем через API (асинхронно, не блокируем UI)
        Task {
            let apiService = APIService.shared
            // Диагностика: покажем актуальный набор server IDs рядом с выбранным
            let currentServerIds = Array(serverMemberIdsLatest).sorted()
            let serverIdsString = currentServerIds.joined(separator: ", ")
            VisualLogger.shared.log("🧩 REMOVE DIAG: chosen=\(member.id) serverIds=\(serverIdsString)", level: .debug, category: "FAMILY")
            // Оптимистически скрываем карточку
            await MainActor.run { optimisticallyRemovedIds.insert(memberToRemove.id) }
            let memberId = await resolveServerMemberIdForRemoval(memberToRemove, apiService: apiService)
            guard let memberId = memberId else {
                await MainActor.run {
                    // Откат + FINAL v3: cleanup after failed resolve (remove local-only dups)
                    optimisticallyRemovedIds.remove(memberToRemove.id)
                    self.cleanupFamilyMembers(serverIds: self.serverMemberIdsLatest)
                    removeMemberErrorMessage = localizationManager.currentLanguage == .russian
                        ? "Не удалось определить ID участника на сервере. Список очищен от дублей."
                        : "Could not resolve server member ID. Duplicates cleaned."
                    HapticFeedback.notification(.warning)
                    deletingMemberIds.remove(memberToRemove.id)
                }
                return
            }
            print("🗑️ [removeFamilyMember] Отправка запроса на удаление через API: \(memberId)")
            
            do {
                let _ = try await apiService.removeFamilyMember(
                    memberId,
                    source: "ui_trash_button",
                    reason: "admin_remove_member"
                )
                await MainActor.run {
                    print("✅ [removeFamilyMember] Успешно удален через API: \(memberToRemove.name)")
                    familyMembers.removeAll { $0.id == memberToRemove.id }
                    optimisticallyRemovedIds.remove(memberToRemove.id)
                    saveFamilyMembers()
                    HapticFeedback.notification(.success)
                    removeMemberErrorMessage = nil
                    removeMemberSuccessMessage = localizationManager.currentLanguage == .russian
                        ? "Участник удален."
                        : "Member removed."
                    // Production-safe: после реального удаления принудительно обновляем Family-блок на MainScreen
                    NotificationCenter.default.post(name: NSNotification.Name("MainFamilyStatsForceRefresh"), object: nil)
                    
                    // Важное исправление: удаляем из deletingMemberIds ДО синхронизации, 
                    // чтобы исключить конфликт с "isServerSubset" защитой.
                    deletingMemberIds.remove(memberToRemove.id)
                    
                    // Авто-ресинк после успешного удаления (правило 5)
                    self.syncFamilyMembersFromAPI()
                    // Дополнительная проверка - убеждаемся что участник не вернулся
                    if familyMembers.contains(where: { $0.id == memberToRemove.id }) {
                        print("⚠️ [removeFamilyMember] Участник все еще в списке, удаляем повторно")
                        familyMembers.removeAll { $0.id == memberToRemove.id }
                        saveFamilyMembers()
                    }
                }
            } catch {
                await MainActor.run {
                    let errorMsg = error.localizedDescription
                    print("❌ [removeFamilyMember] Ошибка при удалении через API: \(errorMsg)")
                    let lower = errorMsg.lowercased()
                    let isSelfRemoval = lower.contains("self-removal") || lower.contains("self removal")
                    
                    // ✅ Self-removal: не портим локальный ростер — откатываем optimistic и тянем правду с сервера.
                    if isSelfRemoval {
                        optimisticallyRemovedIds.remove(memberToRemove.id)
                        VisualLogger.shared.log(
                            "🛡️ REMOVE self-removal отказ сервера — откат optimistic, sync+reconcile your_member_id",
                            level: .warning,
                            category: "FAMILY"
                        )
                        self.reconcileOrSyncAfterRemove()
                        removeMemberErrorMessage = localizationManager.currentLanguage == .russian
                            ? "Сервер считает этого участника вашей учётной записью. Список обновлён — удаление другого профиля выполняйте с того устройства или обратитесь в поддержку."
                            : "The server treats this member as your account. Refresh the list; remove another profile from that device or contact support."
                        HapticFeedback.notification(.warning)
                        deletingMemberIds.remove(memberToRemove.id)
                        return
                    }
                    
                    // ✅ RESILIENT HANDLING: 404 = member not on server → just remove locally, no full cleanup
                    let isNotFound = errorMsg.contains("404") || errorMsg.lowercased().contains("not found")
                    
                    if isNotFound {
                        print("🛠️ [removeFamilyMember] 404 detected - member exists only locally. Removing locally only.")
                        VisualLogger.shared.log("🛠️ REMOVE 404: \(memberToRemove.name) (\(memberToRemove.id)) - removing locally only (no full cleanup)", level: .warning, category: "FAMILY")
                    } else {
                        VisualLogger.shared.log("❌ REMOVE FAILED: \(memberToRemove.name) - \(errorMsg)", level: .error, category: "FAMILY")
                    }
                    
                    // Always remove locally on error (optimistic + resilient)
                    familyMembers.removeAll { $0.id == memberToRemove.id || $0.serverMemberId == memberToRemove.id }
                    optimisticallyRemovedIds.remove(memberToRemove.id)
                    
                    // Save the cleaned state
                    saveFamilyMembers()
                    
                    // Call reconcile (new resilient flow)
                    self.reconcileOrSyncAfterRemove()
                    
                    removeMemberErrorMessage = isNotFound 
                        ? (localizationManager.currentLanguage == .russian ? "Участник удалён локально (сервер не нашёл запись). Синхронизация запущена." : "Member removed locally (not found on server). Sync started.")
                        : (localizationManager.currentLanguage == .russian ? "Ошибка удаления. Список обновлён локально." : "Removal error. List updated locally.")
                    
                    HapticFeedback.notification(.warning)
                    deletingMemberIds.remove(memberToRemove.id)
                }
            }
        }
    }

    private func reconcileOrSyncAfterRemove() {
        VisualLogger.shared.log("🔄 RECONCILE/SYNC: family maintenance (reconcile + refresh)", level: .info, category: "FAMILY")
        
        let familyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)
        let apiService = APIService.shared
        
        apiService.reconcileFamily(familyId: familyId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let body):
                    VisualLogger.shared.log("✅ RECONCILE ok familyId=\(body.familyId) total=\(body.total) fixed=\(body.fixedStatuses)", level: .success, category: "FAMILY")
                    self.syncFamilyMembersFromAPI()
                case .failure(let error):
                    VisualLogger.shared.log("⚠️ RECONCILE failed: \(error.localizedDescription). Falling back to sync", level: .warning, category: "FAMILY")
                    self.syncFamilyMembersFromAPI()
                }
            }
        }
    }
    
    private func checkForDesyncAndReconcile() {
        let localCount = familyMembers.count
        if localCount > 0 {
            VisualLogger.shared.log("🔍 Desync check onAppear (local=\(localCount))", level: .debug, category: "FAMILY")
            reconcileOrSyncAfterRemove()
        }
    }

    private func scheduleCoalescedFamilySync(delay: TimeInterval = 0.8, minInterval: TimeInterval = 2.0) {
        let now = Date()
        guard !isFamilySyncInProgress else { return }
        guard now.timeIntervalSince(lastCoalescedFamilySyncAt) >= minInterval else { return }
        lastCoalescedFamilySyncAt = now
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
            self.syncFamilyMembersFromAPI()
        }
    }

    private func resolveServerMemberIdForRemoval(_ member: FamilyMemberData, apiService: APIService) async -> String? {
        let myMemberId = UserDefaults.standard.string(forKey: "your_member_id") ?? ""
        
        // 0) Быстрый путь: serverMemberId или MEM_* — обязательно сверяем с your_member_id (иначе сервер вернёт Self-removal).
        if let sid = member.serverMemberId?.trimmingCharacters(in: .whitespacesAndNewlines), !sid.isEmpty {
            if !myMemberId.isEmpty, sid == myMemberId {
                print("❌ [resolve] SELF-REMOVAL BLOCKED (serverMemberId == your_member_id) for \(member.name)")
                return nil
            }
            print("🗑️ [resolve] Using direct serverMemberId: \(sid) for \(member.name)")
            return sid
        }
        if member.id.hasPrefix("MEM_") {
            if !myMemberId.isEmpty, member.id == myMemberId {
                print("❌ [resolve] SELF-REMOVAL BLOCKED (id == your_member_id) for \(member.name)")
                return nil
            }
            print("🗑️ [resolve] Using MEM_* ID: \(member.id) for \(member.name)")
            return member.id
        }
        
        // Self-removal protection (moved earlier, but double-check)
        if !myMemberId.isEmpty && (member.id == myMemberId || member.serverMemberId == myMemberId) {
            print("❌ [resolve] SELF-REMOVAL BLOCKED for \(member.name)")
            return nil
        }
        
        // 1) Use latest server list or fetch fresh
        let localCandidates = [member.serverMemberId, member.id]
            .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty && $0 != myMemberId } // exclude self

        do {
            let serverMembers = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<[FamilyMemberResponse], Error>) in
                apiService.getFamilyMembers { result in
                    continuation.resume(with: result)
                }
            }

            await MainActor.run {
                let serverIds = Set(serverMembers.map { $0.id })
                self.serverMemberIdsLatest = serverIds
                // Trigger dedup after fresh server data
                self.familyMembers = self.deduplicateFamilyMembers(self.familyMembers)
            }

            let normalizedName = member.name.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
            let desiredRoles = member.role == .teenager ? Set(["teenager", "teen"]) : Set([member.role.rawValue.lowercased()])

            // 2) Прямое совпадение по ID (самое надежное)
            if let byCandidate = serverMembers.first(where: { localCandidates.contains($0.id) }) {
                print("🗑️ [resolve] Matched by candidate ID: \(byCandidate.id)")
                return byCandidate.id
            }

            // 3) Fallback by name+role (less reliable with duplicates, but dedup should prevent)
            if let byNameAndRole = serverMembers.first(where: { item in
                let itemName = item.name.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
                let itemRole = item.role.lowercased()
                return itemName == normalizedName && desiredRoles.contains(itemRole)
            }) {
                print("🗑️ [resolve] Matched by name+role: \(byNameAndRole.id) for \(member.name)")
                return byNameAndRole.id
            }
            
            // 4) Last resort: any server ID that matches canonical from dedup
            if let canonicalMatch = serverMembers.first(where: { $0.id == member.id || $0.id == member.serverMemberId }) {
                return canonicalMatch.id
            }
            
            print("⚠️ [resolve] No matching ID found for \(member.name). Server has \(serverMembers.count) members. Triggering full sync.")
            await MainActor.run { self.syncFamilyMembersFromAPI() }
        } catch {
            print("❌ [resolveServerMemberIdForRemoval] Error: \(error.localizedDescription)")
            // On error (e.g. 404 context), force dedup and sync
            await MainActor.run {
                self.familyMembers = self.deduplicateFamilyMembers(self.familyMembers)
                self.syncFamilyMembersFromAPI()
            }
        }

        return nil
    }
    
    // Сохранение участников семьи в UserDefaults
    // ✅ FIXED: saveFamilyMembers — reduced logging + debounce protection
    // No more excessive synchronize() or prints on every call. This was flooding console + blocking UI.
    private func saveFamilyMembers(allowDuringFamilySync: Bool = false) {
        // Strong guard against re-entrancy + debounce (minimum 300ms between operations)
        let now = Date()
        let syncBusy = isFamilySyncInProgress && !allowDuringFamilySync
        let debounced = !allowDuringFamilySync && now.timeIntervalSince(lastFamilyOperationTime) < 0.3
        if isFamilyLoadInProgress || syncBusy || debounced {
            #if DEBUG
            if now.timeIntervalSince(lastFamilyOperationTime) < 0.3 {
                print("⏳ [saveFamilyMembers] Debounce: too soon since last operation")
            } else {
                print("⚠️ [saveFamilyMembers] Already in progress, skipping")
            }
            #endif
            return
        }

        lastFamilyOperationTime = now
        clearDeleteButtonCache(reason: "saveFamilyMembers")  // Invalidate cache after any save
        lastFamilyOperationTime = now

        #if DEBUG
        logger.business("Saving \(familyMembers.count) family members to storage")
        #endif

        // Deduplicate before saving
        let deduped = deduplicateFamilyMembers(familyMembers)
        if deduped.count != familyMembers.count {
            #if DEBUG
            print("🧹 [saveFamilyMembers] Deduplicated: \(familyMembers.count) → \(deduped.count)")
            #endif
            familyMembers = deduped
        }

        guard let encoded = try? JSONEncoder().encode(familyMembers) else {
            print("❌ Failed to encode family members")
            return
        }

        UserDefaults.standard.set(encoded, forKey: familyMembersKey)
        let fid = (UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey) ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        FamilyLocalStore.persistRosterSnapshotFamilyId(fid)
        // Persist not-seen counters
        if let countersData = try? JSONEncoder().encode(notSeenCounters) {
            UserDefaults.standard.set(countersData, forKey: "family_not_seen_counters")
        }

        // synchronize() ONLY when necessary — moved here from cleanup to reduce spam
        UserDefaults.standard.synchronize()

        #if DEBUG
        print("✅ Stored \(familyMembers.count) family members in UserDefaults")
        #endif

        // Notify other screens (with guard in .onReceive to prevent loop)
        FamilyLocalStore.notifyFamilyMembersUpdated()
    }
    
    // 🔥 FINAL v3: Агрессивная дедупликация + cleanup — server truth всегда
    // Seed при 0 → 1 (current as .parent). Force role=.parent for creator. Удаляет local-only IDs.
    // Решает "4 вместо 3", role=child/elderly для current user, "no changes skip save", extra MEM_*.
    private func deduplicateFamilyMembers(_ members: [FamilyMemberData]) -> [FamilyMemberData] {
        let myMemberId = UserDefaults.standard.string(forKey: "your_member_id") ?? ""
        var canonicalMap: [String: FamilyMemberData] = [:]
        
        for member in members {
            var canonicalKey = member.id
            if let sid = member.serverMemberId?.trimmingCharacters(in: .whitespacesAndNewlines), !sid.isEmpty {
                canonicalKey = sid
            } else if !myMemberId.isEmpty && (member.id == myMemberId || (member.serverMemberId == myMemberId)) {
                canonicalKey = myMemberId
            }
            
            if let existing = canonicalMap[canonicalKey] {
                let isCurrentUserEntry = !myMemberId.isEmpty && (member.id == myMemberId || member.serverMemberId == myMemberId || canonicalKey == myMemberId)
                if isCurrentUserEntry {
                    let preferNew = (member.role == .parent && existing.role != .parent) ||
                                   (member.serverMemberId != nil && existing.serverMemberId == nil) ||
                                   member.id.hasPrefix("MEM_") || !(member.localOnly ?? false)
                    if preferNew {
                        canonicalMap[canonicalKey] = member
                        print("🧹 [dedup] Updated CURRENT USER entry: \(member.name) (role=\(member.role), serverId=\(member.serverMemberId ?? "nil"))")
                        continue
                    }
                } else if (member.serverMemberId != nil && existing.serverMemberId == nil) {
                    canonicalMap[canonicalKey] = member
                }
                continue
            }
            canonicalMap[canonicalKey] = member
        }
        
        let deduped = Array(canonicalMap.values)
            .sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
        
        if deduped.count < members.count {
            let keptCurrent = deduped.first(where: { $0.isCurrentUser })?.name ?? "unknown"
            print("🧹 [deduplicateFamilyMembers] Removed \(members.count - deduped.count) duplicates. Kept \(deduped.count) (current user: \(keptCurrent))")
            VisualLogger.shared.log("🧹 DEDUP: removed \(members.count - deduped.count) dups → \(deduped.count) (current=\(keptCurrent))", level: .success, category: "FAMILY")
        }
        return deduped
    }
    
    // ✅ FINAL SIMPLIFIED: cleanupFamilyMembers — no more magic, only explicit desync handling
    // This replaces complex notSeenCounters + aggressive pruning with simple, predictable logic.
    private func cleanupFamilyMembers(serverIds: Set<String> = [], allowDuringFamilySync: Bool = false) {
        // Strong debounce - prevent cascade calls
        let now = Date()
        let syncBusy = isFamilySyncInProgress && !allowDuringFamilySync
        let debounced = !allowDuringFamilySync && now.timeIntervalSince(lastFamilyOperationTime) < 0.5
        if isFamilyLoadInProgress || syncBusy || debounced {
            return
        }
        lastFamilyOperationTime = now

        let beforeCount = familyMembers.count
        var cleaned = deduplicateFamilyMembers(familyMembers)
        let myMemberId = UserDefaults.standard.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey) ?? ""

        // Simple local-only cleanup - only if we have fresh server list
        if !serverIds.isEmpty {
            cleaned.removeAll { member in
                let id = member.serverMemberId ?? member.id
                let isKnownOnServer = serverIds.contains(id)
                return !isKnownOnServer && (member.localOnly == true) && id != myMemberId
            }
        }

        let hasRealChanges = cleaned.count != beforeCount

        if hasRealChanges {
            familyMembers = cleaned
            saveFamilyMembers(allowDuringFamilySync: allowDuringFamilySync)
            VisualLogger.shared.log("🧹 CLEANUP: \(beforeCount) → \(cleaned.count) members (real changes applied)", level: .info, category: "FAMILY")
        } else {
            VisualLogger.shared.log("🛡️ CLEANUP: no changes needed (already clean)", level: .debug, category: "FAMILY")
        }

        updateAdminStatus()  // ✅ OPTIMIZATION: Refresh admin status after cleanup

        // Reset counters (only once) - no more aggressive pruning
        notSeenCounters.removeAll()
        UserDefaults.standard.set(0, forKey: "family_sync_partial_retry_count")
        
        // ✅ STABLE ORDER: Sync additionOrder with current cleaned list (prune deleted members, keep new at end)
        let currentIds = familyMembers.map { $0.id }
        var updatedOrder = familyAdditionOrder.filter { currentIds.contains($0) }
        for id in currentIds where !updatedOrder.contains(id) {
            updatedOrder.append(id)
        }
        if updatedOrder != familyAdditionOrder {
            // Use direct UserDefaults write to avoid mutating computed property from non-mutating context
            UserDefaults.standard.set(updatedOrder, forKey: familyAdditionOrderKey)
            UserDefaults.standard.synchronize()
            VisualLogger.shared.log("📋 FAMILY ORDER synced after cleanup: \(updatedOrder.count) entries", level: .debug, category: "FAMILY")
        }
    }
    
    // Вспомогательная функция для получения аватара по роли
    private func getAvatarForRole(_ role: FamilyMemberCard.FamilyRole) -> String {
        switch role {
        case .parent: return "👨"
        case .child: return "👧"
        case .teenager: return "🧒"
        case .elderly: return "👵"
        }
    }

    private func serverRole(for role: FamilyMemberCard.FamilyRole) -> String {
        switch role {
        case .parent:
            return "parent"
        case .child:
            return "child"
        case .teenager:
            return "child"
        case .elderly:
            return "elderly"
        }
    }
    
    // ✅ OPTIMIZED: Cached admin status + delete button cache (prevents spam calls)
    // isCurrentUserCreator/isCurrentUserParent updated ONLY in updateAdminStatus()
    // deleteButtonCache prevents canShowDeleteButton() from running 20-50x per render
    private func updateAdminStatus() {
        let familyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)
        let myMemberId = UserDefaults.standard.string(forKey: "your_member_id") ?? ""
        let isFirstRegistration = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding) == false

        // Invalidate delete button cache ONLY when admin status actually changes (optimization)
        // This prevents cache thrashing on every onAppear/sync

        var newIsCreator = true
        var newIsParent = true

        // ✅ GOLDEN RULE FOR PROD: First registered user is ALWAYS creator + parent
        // This eliminates the root cause of desync (creator saved as child)
        if isFirstRegistration || familyMembers.isEmpty || (familyId == nil || familyId?.isEmpty == true) {
            newIsCreator = true
            newIsParent = true
            print("👑 FIRST REGISTRATION: Forcing isCurrentUserCreator=true and isCurrentUserParent=true")
        } else if !myMemberId.isEmpty && !familyMembers.isEmpty {
            let myInRoster = familyMembers.contains { $0.id == myMemberId || ($0.serverMemberId != nil && $0.serverMemberId == myMemberId) }
            if !myInRoster {
                newIsCreator = false
                newIsParent = false
                #if DEBUG
                print("👤 [updateAdminStatus] your_member_id не найден в ростере — сброс creator/parent до resync")
                #endif
            } else if let creatorStored = FamilyLocalStore.currentFamilyCreatorMemberId(), !creatorStored.isEmpty {
                newIsCreator = (myMemberId == creatorStored)
                newIsParent = FamilyRosterAccess.canManageRoster(members: familyMembers)
            } else {
                // Без сохранённого creator_id не используем «первый в списке» — порядок после сортировки недетерминирован и ломал роли/кнопки.
                newIsCreator = false
                newIsParent = FamilyRosterAccess.canManageRoster(members: familyMembers)
            }
        } else {
            // Fallback: check role from UserDefaults
            if let roleString = UserDefaults.standard.string(forKey: currentUserRoleKey) {
                let normalized = roleString.lowercased()
                newIsParent = normalized.contains("parent") || normalized.contains("родител")
                newIsCreator = newIsParent
            }
        }

        // Update only if changed to minimize @State updates + cache thrashing
        var statusChanged = false
        if isCurrentUserCreator != newIsCreator {
            isCurrentUserCreator = newIsCreator
            statusChanged = true
            #if DEBUG
            print("👤 [updateAdminStatus] isCurrentUserCreator = \(newIsCreator) (myMemberId=\(myMemberId.prefix(8)))")
            #endif
        }
        if isCurrentUserParent != newIsParent {
            isCurrentUserParent = newIsParent
            statusChanged = true
            #if DEBUG
            print("👤 [updateAdminStatus] isCurrentUserParent = \(newIsParent)")
            #endif
        }

        if statusChanged {
            clearDeleteButtonCache(reason: "admin_status_changed")
        }
    }

    // Legacy computed properties for backward compatibility during transition
    private var isFamilyCreator: Bool {
        isCurrentUserCreator
    }

    private var isUserParent: Bool {
        isCurrentUserParent
    }

    /// Добавление/удаление участников: только родитель или пожилой в ростере (не ребёнок/подросток).
    private var canManageFamilyRoster: Bool {
        FamilyAccessPolicy.hasPermission(.manageAppProfiles, members: familyMembers)
    }

    /// Family Sharing операции отделены от app-level профилей:
    /// доступ разрешён только parent-профилю (не elderly/child/teen).
    private var canManageFamilySharing: Bool {
        FamilyAccessPolicy.hasPermission(.manageFamilySharing, members: familyMembers)
    }

    private var familyMembersAsResponse: [FamilyMemberResponse] {
        familyMembers.map { member in
            FamilyMemberResponse(
                id: member.serverMemberId ?? member.id,
                name: member.name,
                role: member.role.rawValue,
                avatar: member.avatar,
                status: member.status.rawValue,
                threatsBlocked: member.threatsBlocked,
                lastActive: member.lastActive,
                devices: nil
            )
        }
    }

    private var shouldShowRosterConflictBanner: Bool {
        canManageFamilySharing && ProfileManager.shared.lastChildRosterConflictCount > 0
    }

    @ViewBuilder
    private var rosterConflictResolutionBanner: some View {
        if shouldShowRosterConflictBanner {
            let ru = localizationManager.currentLanguage == .russian
            VStack(alignment: .leading, spacing: 8) {
                Text(ru ? "Конфликт синхронизации профилей" : "Profile sync conflict")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white)
                Text(ProfileManager.shared.lastChildRosterReconcileSummary ?? (ru
                    ? "Обнаружены конкурирующие изменения между устройствами."
                    : "Competing cross-device updates were detected."))
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
                HStack(spacing: 8) {
                    Button(ru ? "Принять сервер" : "Use server") {
                        _ = ProfileManager.shared.resolveChildRosterConflicts(
                            members: familyMembersAsResponse,
                            familyId: UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey),
                            prefer: .serverWins,
                            removeMissingServerLinkedChildren: true
                        )
                    }
                    .font(.caption2.weight(.semibold))
                    .foregroundColor(.white)
                    .padding(.vertical, 6)
                    .padding(.horizontal, 10)
                    .background(Color.orange.opacity(0.35))
                    .cornerRadius(8)

                    Button(ru ? "Оставить локальное" : "Keep local") {
                        _ = ProfileManager.shared.resolveChildRosterConflicts(
                            members: familyMembersAsResponse,
                            familyId: UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey),
                            prefer: .localWins,
                            removeMissingServerLinkedChildren: true
                        )
                    }
                    .font(.caption2.weight(.semibold))
                    .foregroundColor(.white)
                    .padding(.vertical, 6)
                    .padding(.horizontal, 10)
                    .background(Color.blue.opacity(0.35))
                    .cornerRadius(8)
                }
            }
            .padding(10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.orange.opacity(0.24))
            .cornerRadius(10)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color.orange.opacity(0.5), lineWidth: 1)
            )
        }
    }

    /// Краткий баннер: правило и текущее состояние (ваш id в списке / роль / можно ли управлять составом).
    @ViewBuilder
    private var familyRosterRulesInfoBanner: some View {
        let ru = localizationManager.currentLanguage == .russian
        let myId = UserDefaults.standard.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey) ?? ""
        let parents = FamilyRosterAccess.parentRoleCount(in: familyMembers)
        let roleLabel: String = {
            guard let me = familyMembers.first(where: { $0.id == myId || $0.serverMemberId == myId }) else {
                return ru ? "нет в списке" : "not in list"
            }
            switch me.role {
            case .parent: return ru ? "родитель" : "parent"
            case .elderly: return ru ? "пожилой" : "elderly"
            case .child: return ru ? "ребёнок" : "child"
            case .teenager: return ru ? "подросток" : "teen"
            }
        }()
        VStack(alignment: .leading, spacing: 6) {
            Text(ru ? "Кто может менять состав семьи" : "Who can change the family roster")
                .font(.caption.weight(.semibold))
                .foregroundColor(Color.secondaryGold)
            Text(ru
                 ? "Добавлять и удалять участников могут только родители или пожилой в списке (не ребёнок и не подросток). До двух родительских аккаунтов — по правилам семьи."
                 : "Only a parent or elderly member in the list may add or remove people (not a child or teen). Up to two parent accounts per family.")
                .font(.caption2)
                .foregroundColor(.white.opacity(0.88))
                .fixedSize(horizontal: false, vertical: true)
            Divider().background(Color.white.opacity(0.2))
            Text(ru ? "Сейчас на этом устройстве" : "On this device")
                .font(.caption.weight(.semibold))
                .foregroundColor(Color.secondaryGold)
            Text(ru
                 ? "Ваш ID: \(myId.isEmpty ? "—" : String(myId.prefix(14)))… · роль в списке: \(roleLabel) · родителей в списке: \(parents) · управление составом: \(canManageFamilyRoster ? "да" : "нет")"
                 : "Your ID: \(myId.isEmpty ? "—" : String(myId.prefix(14)))… · role in list: \(roleLabel) · parents in list: \(parents) · can manage roster: \(canManageFamilyRoster ? "yes" : "no")")
                .font(.caption2)
                .foregroundColor(.white.opacity(0.78))
                .fixedSize(horizontal: false, vertical: true)
            Text(ru
                 ? "Family Sharing операции: \(canManageFamilySharing ? "доступны (parent)" : "недоступны")"
                 : "Family Sharing operations: \(canManageFamilySharing ? "allowed (parent)" : "not allowed")")
                .font(.caption2)
                .foregroundColor(.white.opacity(0.72))
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.06))
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(Color.secondaryGold.opacity(0.35), lineWidth: 1)
        )
    }

    // ✅ CACHE for canShowDeleteButton - prevents massive spam during renders/syncs
    @State private var deleteButtonCache: [String: Bool] = [:]
    @State private var lastDeleteButtonLogTime: [String: Date] = [:]  // Prevents repeated VisualLogger spam

    private func clearDeleteButtonCache(reason: String = "manual") {
        if !deleteButtonCache.isEmpty {
            deleteButtonCache.removeAll()
            lastDeleteButtonLogTime.removeAll()
            #if DEBUG
            print("🧹 [clearDeleteButtonCache] Cache cleared (\(familyMembers.count) members). Reason: \(reason)")
            #endif
        }
    }
    
    // Проверяем, новая ли это семья (1 участник или меньше)
    private var isNewFamily: Bool {
        return familyMembers.count <= 1
    }
    
    // Old computed property removed - now uses cached @State via legacy wrapper above
    // (This duplication was causing the build error)
    
    // Получаем список детей из familyMembers (для использования в модальных окнах)
    private var childrenNames: [String] {
        familyMembers
            .filter { member in
                member.role == .child || member.role == .teenager
            }
            .map { $0.name }
    }
    
    // ✅ Sync: number of children for the family protection card
    private var childrenCount: Int {
        familyMembers.filter { member in
            member.role == .child || member.role == .teenager
        }.count
    }
    
    // MARK: - Visibility rules for delete (trash) button
    // Удаление из UI: только родитель/пожилой (canManageFamilyRoster). «Себя» определяем только по совпадению с your_member_id — без флага «создатель» для чужой строки.

    /// Создатель семьи для правил удаления: `family_creator_member_id` с `createFamily`, иначе первый родитель/пожилой в списке (join без creator в API).
    private func resolvedFamilyCreatorMemberForDeletionRules() -> FamilyMemberData? {
        if let cid = FamilyLocalStore.currentFamilyCreatorMemberId() {
            if let m = familyMembers.first(where: { $0.id == cid || $0.serverMemberId == cid }) {
                return m
            }
        }
        return familyMembers.first(where: { $0.role == .parent || $0.role == .elderly })
    }

    private func canShowDeleteButton(for member: FamilyMemberData) -> Bool {
        let key = member.serverMemberId ?? member.id

        // ✅ CACHE HIT - massive reduction in calls (was 20-50x per render)
        if let cached = deleteButtonCache[key] {
            return cached
        }

        let isAdmin = canManageFamilyRoster
        let myMemberId = UserDefaults.standard.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey) ?? ""

        // Для логов: совпадение с серверным создателем семьи (не влияет на isMe после фикса).
        let isCreator: Bool
        if let creatorMember = resolvedFamilyCreatorMemberForDeletionRules() {
            isCreator = (creatorMember.id == member.id || creatorMember.serverMemberId == member.serverMemberId)
                && (member.role == .parent || member.role == .elderly)
        } else {
            isCreator = false
        }

        let isMe = (member.id == myMemberId) || (member.serverMemberId == myMemberId)

        let hasServerId = (member.serverMemberId != nil) || member.id.hasPrefix("MEM_") || member.id.count > 8
        let otherMembersExist = familyMembers.count > 1 ||
                               familyMembers.filter({ !($0.id == myMemberId || ($0.serverMemberId != nil && $0.serverMemberId == myMemberId)) }).count > 0

        let result = isAdmin && !isMe && hasServerId && otherMembersExist

        // Cache the result
        deleteButtonCache[key] = result

        // ✅ DEBOUNCED LOGGING: Both console print and VisualLogger now respect 2s cooldown per key
        let shouldLog = lastDeleteButtonLogTime[key] == nil ||
                        Date().timeIntervalSince(lastDeleteButtonLogTime[key] ?? Date.distantPast) >= 2.0

        if shouldLog {
            lastDeleteButtonLogTime[key] = Date()

            // Console print (DEBUG only) - now also debounced
            #if DEBUG
            let logPrefix = result ? "✅" : "⚠️"
            let statusText = result ? "VISIBLE" : "HIDDEN"
            print("\(logPrefix) [canShowDeleteButton] 🗑️ DELETE BUTTON \(statusText): \(member.name) | isMe=\(isMe) | admin=\(isAdmin) | cacheKey=\(key.prefix(8)) | isCreator=\(isCreator)")
            #endif

            // VisualLogger (production friendly)
            let level: VisualLogger.LogLevel = result ? .success : .warning
            VisualLogger.shared.log(
                "🗑️ DELETE BUTTON \(result ? "VISIBLE" : "HIDDEN"): \(member.name) | admin=\(isAdmin) | isMe=\(isMe) | creator=\(isCreator)",
                level: level,
                category: "FAMILY"
            )
        }

        return result
    }
    
    // Получаем имя первого ребенка (для дефолтного значения)
    private var firstChildName: String {
        childrenNames.first ?? ""
    }

    private var familySyncState: SyncState {
        syncEngine.latestStateByDomain[.family] ?? .idle
    }

    private var familySyncStatusTitle: String {
        familySyncState.localizedTitle(using: localizationManager)
    }

    private var familySyncStatusColor: Color {
        familySyncState.statusColor
    }
    
    var body: some View {
        ZStack {
            // Background gradient
            LinearGradient(
                colors: [Color(red: 0.04, green: 0.07, blue: 0.16), Color(red: 0.12, green: 0.23, blue: 0.37), Color(red: 0.18, green: 0.31, blue: 0.56)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Button(action: {
                        logger.buttonTap("Back", screen: "Family")
                        VisualLogger.shared.log("⬅️ Back button tapped on FamilyScreen → navigating to main", level: .info, category: "NAVIGATION")
                        print("🔙 [FamilyScreen] Back button tapped - using switchToMainScreen()")
                        
                        // ✅ ПРЯМОЙ И НАДЁЖНЫЙ ПЕРЕХОД НА ГЛАВНЫЙ ЭКРАН
                        // После всех правок навигации это самый стабильный способ
                        navigationManager.switchToMainScreen()
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 20, weight: .medium))
                            .foregroundColor(.white)
                            .frame(width: 44, height: 44)
                            .background(Color.white.opacity(0.1))
                            .clipShape(Circle())
                    }
                    .accessibilityIdentifier("family_nav_back")
                    .accessibilityLabel(localizationManager.localized("family_back_button_label"))
                    .accessibilityHint(localizationManager.localized("family_back_button_hint"))
                    
                    Spacer()
                    
                    Text(localizationManager.localized("family_title"))
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                        .accessibilityLabel(localizationManager.localized("family_header_accessibility"))
                        .accessibilityAddTraits(.isHeader)
                    
                    Spacer()
                    
                    HStack(spacing: 10) {
                        // Кнопка настроек уведомлений
                        Button(action: {
                            logger.buttonTap("Family Notification Settings", screen: "Family")
                            showFamilyNotificationSettings = true
                        }) {
                            Image(systemName: "bell.fill")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(Color(red: 0.04, green: 0.07, blue: 0.16))
                                .frame(width: 40, height: 40)
                                .background(Color(red: 0.96, green: 0.62, blue: 0.04))
                                .clipShape(Circle())
                        }
                        .accessibilityLabel(localizationManager.localized("family_notification_settings"))
                        
                        // Toolbar «+»: родитель/пожилой (в т.ч. fallback по роли при рассинх id); тариф — на экране добавления или алерт при жёстком лимите
                        Button(action: {
                            logger.buttonTap("Add Member", screen: "Family")
                            guard canManageFamilyRoster else {
                                UINotificationFeedbackGenerator().notificationOccurred(.warning)
                                VisualLogger.shared.log("🚫 FAMILY ADD toolbar: canManageFamilyRoster=false", level: .warning, category: "FAMILY")
                                return
                            }
                            UserDefaults.standard.set(true, forKey: "admin_add_mode")
                            UserDefaults.standard.synchronize()
                            navigationManager.navigateTo(.addMemberOptions)
                        }) {
                            Image(systemName: "plus")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(Color(red: 0.04, green: 0.07, blue: 0.16))
                                .frame(width: 40, height: 40)
                                .background(Color(red: 0.96, green: 0.62, blue: 0.04))
                                .clipShape(Circle())
                                .opacity(canManageFamilyRoster ? 1 : 0.35)
                        }
                        .accessibilityLabel(localizationManager.localized("add_member_accessibility"))
                        .accessibilityHint(localizationManager.localized("add_member_accessibility_hint"))
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 20)

                HStack {
                    Spacer()
                    Text(familySyncStatusTitle)
                        .font(.caption2.weight(.semibold))
                        .foregroundColor(familySyncStatusColor)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(familySyncStatusColor.opacity(0.15))
                        .clipShape(Capsule())
                }
                .padding(.horizontal, 20)
                .padding(.top, 6)

                if FamilyLocalStore.needsFamilyIdentityRepairHeuristic(
                    members: familyMembers,
                    canManageAppProfiles: canManageFamilyRoster
                ) {
                    HStack(alignment: .top, spacing: 10) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(Color.orange)
                            .font(.system(size: 18, weight: .semibold))
                        VStack(alignment: .leading, spacing: 8) {
                            Text(localizationManager.localized("family_identity_repair_banner_title"))
                                .font(.subheadline.weight(.semibold))
                                .foregroundColor(.white)
                            Text(localizationManager.localized("family_identity_repair_banner_body"))
                                .font(.caption2)
                                .foregroundColor(.white.opacity(0.88))
                                .fixedSize(horizontal: false, vertical: true)
                            Button(action: {
                                runFamilyIdentityRepairFromCurrentRoster()
                            }) {
                                HStack(spacing: 6) {
                                    if isFamilyIdentityRepairing {
                                        ProgressView()
                                            .progressViewStyle(CircularProgressViewStyle(tint: .orange))
                                            .scaleEffect(0.85)
                                    }
                                    Text(localizationManager.localized("family_identity_repair_button"))
                                        .font(.caption.weight(.semibold))
                                }
                                .foregroundColor(.orange)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 7)
                                .background(Color.white.opacity(0.95))
                                .cornerRadius(8)
                            }
                            .disabled(isFamilyIdentityRepairing || familyMembers.isEmpty)
                            .buttonStyle(.plain)
                        }
                        Spacer(minLength: 0)
                    }
                    .padding(12)
                    .background(Color.orange.opacity(0.22))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.orange.opacity(0.45), lineWidth: 1)
                    )
                    .cornerRadius(12)
                    .padding(.horizontal, 20)
                    .padding(.top, 8)
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel(
                        localizationManager.localized("family_identity_repair_banner_title")
                            + ". "
                            + localizationManager.localized("family_identity_repair_banner_body")
                            + ". "
                            + localizationManager.localized("family_identity_repair_button")
                    )
                }
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Family Overview
                        VStack(spacing: 20) {
                            Text(localizationManager.localized("family_protection_title"))
                                .font(.h3)
                                .foregroundColor(Color.secondaryGold)
                                .accessibilityLabel(localizationManager.localized("family_protection_accessibility"))
                                .accessibilityAddTraits(.isHeader)
                            
                            // Improved stats: capacity "X of Y (Plan)" + progress. Single source from SubscriptionManager.
                            let quotaUsed2 = subscriptionManager.familyQuotaSnapshot.source == .persistedCache
                                ? familyMembers.count
                                : subscriptionManager.familyQuotaSnapshot.used
                            let currentCount2 = max(familyMembers.count, quotaUsed2)
                            let limit2 = subscriptionManager.familyQuotaSnapshot.max
                            let capacityText2 = "\(currentCount2) из \(limit2)"
                            let progress = limit2 > 0 ? Double(currentCount2) / Double(limit2) : 0.0

                            HStack(spacing: 15) {
                                StatItem(
                                    icon: "👥",
                                    value: capacityText2,
                                    label: "Участники (\(subscriptionManager.getCurrentLevel().displayName))"
                                )
                                .accessibilityElement(children: .combine)
                                .accessibilityLabel("Семья: \(capacityText2) участников, тариф \(subscriptionManager.getCurrentLevel().displayName)")
                                
                                StatItem(
                                    icon: "👶",
                                    value: "\(childrenCount)",
                                    label: "\(childrenCount == 1 ? localizationManager.localized("family_child") : childrenCount == 0 ? localizationManager.localized("family_no_children") : localizationManager.localized("family_children"))"
                                )
                                .accessibilityElement(children: .combine)
                                .accessibilityLabel(
                                    localizationManager.localized(
                                        childrenCount == 1 ? "family_child_stats_accessibility" : "family_children_stats_accessibility",
                                        childrenCount
                                    )
                                )
                                
                                StatItem(icon: "🛡️", value: "100%", label: localizationManager.localized("family_protection"))
                                    .accessibilityElement(children: .combine)
                                    .accessibilityLabel(localizationManager.localized("family_protection_stats_accessibility"))
                            }
                            .accessibilityElement(children: .contain)
                            .accessibilityLabel(localizationManager.localized("family_statistics_accessibility"))
                            
                            // Updated: Uses single source SubscriptionManager.canAddFamilyMember + capacity display
                            // Shows "X of Y members (Plan)" with progress. Consistent across all add paths.
                            let quotaUsed3 = subscriptionManager.familyQuotaSnapshot.source == .persistedCache
                                ? familyMembers.count
                                : subscriptionManager.familyQuotaSnapshot.used
                            let currentCount3 = max(familyMembers.count, quotaUsed3)
                            let limit3 = subscriptionManager.familyQuotaSnapshot.max
                            let capacityText3 = "\(currentCount3) из \(limit3) участников (Tariff)"

                            Group {
                                if !canManageFamilyRoster {
                                    VStack(spacing: 6) {
                                        Text(localizationManager.localized("family_add_member"))
                                            .font(.system(size: 16, weight: .bold))
                                            .foregroundColor(.white.opacity(0.38))
                                            .frame(maxWidth: .infinity)
                                            .padding(.vertical, 12)
                                            .background(
                                                LinearGradient(
                                                    colors: [Color(red: 0.96, green: 0.62, blue: 0.04).opacity(0.35), Color(red: 0.85, green: 0.47, blue: 0.02).opacity(0.35)],
                                                    startPoint: .leading,
                                                    endPoint: .trailing
                                                )
                                            )
                                            .clipShape(Capsule())
                                        Text(localizationManager.currentLanguage == .russian
                                             ? "Добавлять участников может только родитель (или пожилой) в этой семье."
                                             : "Only a parent (or elderly member) in this family can add members.")
                                            .font(.caption)
                                            .foregroundColor(.white.opacity(0.75))
                                            .multilineTextAlignment(.center)
                                    }
                                } else if canAddFamilyMemberUnderTariff {
                                    Button(action: {
                                        UserDefaults.standard.set(true, forKey: "admin_add_mode")
                                        UserDefaults.standard.synchronize()
                                        navigationManager.navigateTo(.addMemberOptions)
                                    }) {
                                        Text(localizationManager.localized("family_add_member"))
                                            .font(.system(size: 16, weight: .bold))
                                            .foregroundColor(.white)
                                            .frame(maxWidth: .infinity)
                                            .padding(.vertical, 12)
                                            .background(
                                                LinearGradient(
                                                    colors: [Color(red: 0.96, green: 0.62, blue: 0.04), Color(red: 0.85, green: 0.47, blue: 0.02)],
                                                    startPoint: .leading,
                                                    endPoint: .trailing
                                                )
                                            )
                                            .clipShape(Capsule())
                                    }
                                } else {
                                    VStack(spacing: 4) {
                                        Text(localizationManager.localized("family_add_member"))
                                            .font(.system(size: 16, weight: .bold))
                                            .foregroundColor(.white.opacity(0.4))
                                            .frame(maxWidth: .infinity)
                                            .padding(.vertical, 12)
                                            .background(
                                                LinearGradient(
                                                    colors: [Color(red: 0.96, green: 0.62, blue: 0.04).opacity(0.4), Color(red: 0.85, green: 0.47, blue: 0.02).opacity(0.4)],
                                                    startPoint: .leading,
                                                    endPoint: .trailing
                                                )
                                            )
                                            .clipShape(Capsule())
                                        Text("Достигнут лимит (\(capacityText3)). Обновите тариф.")
                                            .font(.caption)
                                            .foregroundColor(.secondaryGold)
                                    }
                                }
                            }
                            .accessibilityLabel(localizationManager.localized("add_member_accessibility"))
                            .accessibilityHint(localizationManager.localized("add_member_accessibility_hint"))
                        }
                        .padding(25)
                        .background(Color.secondaryGold.opacity(0.15))
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.secondaryGold.opacity(0.4), lineWidth: 2)
                        )
                        
                        // Family Members
                        VStack(alignment: .leading, spacing: 20) {
                            Text(localizationManager.localized("family_members_title"))
                                .font(.h3)
                                .foregroundColor(Color.secondaryGold)
                                .accessibilityLabel(localizationManager.localized("family_members_title"))
                                .accessibilityAddTraits(.isHeader)

                            rosterConflictResolutionBanner
                            
                            // ✅ ИСПРАВЛЕНИЕ: Всегда показываем карточки участников когда они есть
                            // WelcomeCardForCreator показывается только если список ПУСТ
                            if !familyMembers.isEmpty {
                                // ✅ ИСПРАВЛЕНИЕ: Заменяем LazyVGrid на VStack для исправления touch events
                                VStack(spacing: 8) {
                                    // Баннер о скрытых локальных записях (C10)
                                    let hiddenCount = familyMembers.filter { (notSeenCounters[$0.id] ?? 0) >= maxNotSeenConsecutiveSyncs }.count
                                    if hiddenCount > 0 {
                                        Text(localizationManager.currentLanguage == .russian
                                             ? "Скрыто \(hiddenCount) локальных записей. Обновите список."
                                             : "\(hiddenCount) local entries hidden. Please refresh.")
                                            .font(.footnote)
                                            .foregroundColor(.white.opacity(0.8))
                                            .padding(.vertical, 6)
                                            .frame(maxWidth: .infinity)
                                            .background(Color.orange.opacity(0.2))
                                            .cornerRadius(8)
                                    }
                                    ForEach(familyMembers.filter { !optimisticallyRemovedIds.contains($0.id) }) { member in
                                        FamilyMemberCard(
                                            name: member.name,
                                            role: member.role,
                                            avatar: member.avatar,
                                            status: member.status,
                                            threatsBlocked: member.threatsBlocked,
                                            lastActive: member.lastActive,
                                            action: {
                                                self.navigateToMemberScreen(role: member.role)
                                            },
                                            onDelete: {
                                                requestRemoveFamilyMember(member)
                                            },
                                            showDeleteButton: canShowDeleteButton(for: member),
                                            isDeleteDisabled: {
                                                let hasServerId = (member.serverMemberId != nil) || member.id.hasPrefix("MEM_")
                                                return deletingMemberIds.contains(member.id) || !hasServerId
                                            }(),
                                            originBadge: ((member.localOnly ?? false) || (member.serverMemberId == nil && !member.id.hasPrefix("MEM_"))) ? "local" : "server",
                                            // ✅ FINAL v3: Use canonical ID for uniqueness to prevent duplicate renders
                                            memberId: member.serverMemberId ?? member.id
                                        )
                                        .environmentObject(localizationManager)
                                        // Гарантируем, что при видимой кнопке удаления хиты проходят
                                        .allowsHitTesting(true)
                                        .contentShape(Rectangle())
                                        .zIndex(1)
                                        .id(member.serverMemberId ?? member.id)  // FINAL v3: Prevent duplicate cards in ForEach
                                        .contextMenu {
                                            // Показываем меню только для администраторов и родителей
                                            if canShowDeleteButton(for: member) {
                                                Button(role: .destructive) {
                                                    requestRemoveFamilyMember(member)
                                                } label: {
                                                    Label(localizationManager.localized("family_remove_member"), systemImage: "trash")
                                                }
                                            }
                                        }
                                    }
                                    
                                    // Updated: AddMoreMemberCard now respects tariff limit via shared guard (no more <10 bypass)
                                    if canAddFamilyMemberUnderTariff && canManageFamilyRoster {
                                        AddMoreMemberCard {
                                            UserDefaults.standard.set(true, forKey: "admin_add_mode")
                                            UserDefaults.standard.synchronize()
                                            navigationManager.navigateTo(.addMemberOptions)
                                        }
                                        .environmentObject(localizationManager)
                                    }
                                    
                                    // ✅ ШАГ 4: Кнопка "Обновить список" + баннер синхронизации (UX-комфорт)
                                    if showSyncBanner {
                                        HStack {
                                            ProgressView()
                                                .scaleEffect(0.8)
                                            Text(localizationManager.localized("family_sync_banner_loading"))
                                                .font(.caption)
                                                .foregroundColor(.white.opacity(0.7))
                                        }
                                        .frame(maxWidth: .infinity)
                                        .padding(.vertical, 8)
                                        .background(Color.blue.opacity(0.2))
                                        .cornerRadius(12)
                                    }
                                    
                                    Button(action: {
                                        logger.buttonTap("Refresh Family List", screen: "Family")
                                        print("🔄 Пользователь нажал 'Обновить список семьи'")
                                        VisualLogger.shared.log("🔄 USER TRIGGERED: Manual family sync", level: .info, category: "FAMILY")
                                        loadFamilyMembers()
                                    }) {
                                        HStack(spacing: 6) {
                                            Image(systemName: "arrow.clockwise.circle.fill")
                                                .font(.system(size: 16))
                                            Text(localizationManager.localized("family_sync_refresh_button"))
                                                .font(.system(size: 14, weight: .medium))
                                        }
                                        .foregroundColor(.white.opacity(0.9))
                                        .padding(.horizontal, 16)
                                        .padding(.vertical, 10)
                                        .background(
                                            LinearGradient(
                                                colors: [Color.white.opacity(0.15), Color.white.opacity(0.05)],
                                                startPoint: .top,
                                                endPoint: .bottom
                                            )
                                        )
                                        .cornerRadius(20)
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 20)
                                                .stroke(Color.white.opacity(0.3), lineWidth: 1)
                                        )
                                    }
                                    
                                    Button {
                                        showClearLocalFamilyCacheConfirmation = true
                                    } label: {
                                        Text(localizationManager.localized("family_clear_local_cache_button"))
                                            .font(.caption)
                                            .foregroundColor(.white.opacity(0.65))
                                            .underline()
                                            .padding(.top, 4)
                                            .frame(maxWidth: .infinity)
                                    }
                                    .buttonStyle(.plain)
                                    .confirmationDialog(
                                        localizationManager.localized("family_clear_local_cache_title"),
                                        isPresented: $showClearLocalFamilyCacheConfirmation,
                                        titleVisibility: .visible
                                    ) {
                                        Button(localizationManager.currentLanguage == .russian ? "Мягкий сброс локального списка" : "Soft reset local list", role: .destructive) {
                                            performClearLocalFamilyRosterCacheAndReload()
                                        }
                                        Button(localizationManager.currentLanguage == .russian ? "Полный локальный сброс семьи (на этом устройстве)" : "Full local family reset (this device)", role: .destructive) {
                                            performFullLocalFamilyContextResetAndReload()
                                        }
                                        Button(localizationManager.localized("common_cancel"), role: .cancel) {}
                                    } message: {
                                        Text(
                                            localizationManager.currentLanguage == .russian
                                            ? "Выберите режим: мягкий сброс очищает только локальный список и счетчики. Полный локальный сброс дополнительно очищает локальный family context (family_id/role/your_member_id) на этом устройстве. Серверная семья, JWT, trial и подписка не изменяются."
                                            : "Choose mode: soft reset clears only local list and counters. Full local reset also clears local family context (family_id/role/your_member_id) on this device. Server family, JWT, trial and subscription are not changed."
                                        )
                                    }
                                }
                            }
                            // Пустое состояние - показываем WelcomeCardForCreator только если список пуст
                            else {
                                VStack(spacing: Spacing.m) {
                                    Text("👨‍👩‍👧‍👦")
                                        .font(.system(size: 48))
                                        .opacity(0.5)
                                    
                                    Text(localizationManager.localized("family_no_members"))
                                        .font(.subheadline)
                                        .foregroundColor(.white.opacity(0.7))
                                    
                                    if canManageFamilyRoster {
                                        Button(action: {
                                            // ✅ ИСПРАВЛЕНИЕ #4: Используем NavigationManager вместо sheet модала
                                            UserDefaults.standard.set(true, forKey: "admin_add_mode")
                                            UserDefaults.standard.synchronize()
                                            navigationManager.navigateTo(.addMemberOptions)
                                        }) {
                                            Text(localizationManager.localized("family_add_first_member"))
                                                .font(.subheadline)
                                                .fontWeight(.semibold)
                                                .foregroundColor(.secondaryGold)
                                                .padding(.vertical, Spacing.s)
                                                .padding(.horizontal, Spacing.m)
                                                .background(Color.secondaryGold.opacity(0.1))
                                                .cornerRadius(CornerRadius.medium)
                                                .overlay(
                                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                                                )
                                        }
                                    }
                                }
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.l)
                            }
                        }
                        .padding(25)
                        .background(Color.secondaryGold.opacity(0.15))
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.secondaryGold.opacity(0.4), lineWidth: 2)
                        )
                        
                        // Parental Controls - НОВАЯ ВЕРСИЯ С КАРТОЧКАМИ 2x3 (только родитель/пожилой в ростере)
                        if canManageFamilyRoster {
                            parentalControlsSection
                        }
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 100)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("family_content_accessibility"))
                
                Spacer()
            }
            // ✅ ИСПРАВЛЕНИЕ: Убираем последний Spacer, который может перекрывать карточки
            // Spacer()  // ЗАКОММЕНТИРОВАНО
        }
        // ✅ ИСПРАВЛЕНИЕ #5: Убрали sheet модал - теперь используем NavigationManager + AddMemberOptionsScreen
        // Это обеспечивает стабильную работу и правильную навигацию "Назад"
        // .sheet(isPresented: $showAddMemberModal) {
        //     AddMemberOptionsModal(isPresented: $showAddMemberModal)
        //         .environmentObject(navigationManager)
        //         .environmentObject(localizationManager)
        // }
        // Новые модалы для родительского контроля (7 карточек)
        .sheet(isPresented: $showContentBlockModal) {
            FamilyContentBlockModal(isPresented: $showContentBlockModal, isEnabled: $isContentBlockEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showTimeControlModalNew) {
            FamilyTimeControlModal(isPresented: $showTimeControlModalNew, isEnabled: $isTimeControlEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showMonitoringModalNew) {
            FamilyMonitoringModal(isPresented: $showMonitoringModalNew, isEnabled: $isMonitoringEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showLocationModal) {
            FamilyLocationModal(isPresented: $showLocationModal, isEnabled: $isLocationEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showReportsModal) {
            FamilyReportsModal(isPresented: $showReportsModal, isEnabled: $isReportsEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAdditionalModal) {
            FamilyAdditionalModal(isPresented: $showAdditionalModal, isEnabled: $isAdditionalEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showFamilyNotificationSettings) {
            FamilyNotificationSettingsModal()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showBypassProtectionModal) {
            FamilyBypassProtectionModal(
                isPresented: $showBypassProtectionModal,
                isEnabled: $isBypassProtectionEnabled
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showParentalSettingsModal) {
            FamilyParentalControlSettingsModal(isPresented: $showParentalSettingsModal)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showPostRegistrationDeviceGuide) {
            PostRegistrationDeviceGuideModal(
                onAddDevice: {
                    let now = Date().timeIntervalSince1970
                    UserDefaults.standard.set(now, forKey: postRegistrationDeviceNudgeLastShownKey)
                    UserDefaults.standard.synchronize()
                    VisualLogger.shared.log(
                        "👉 DEVICE_NUDGE CTA add_now tapped",
                        level: .info,
                        category: "ONBOARDING"
                    )
                    showPostRegistrationDeviceGuide = false
                    routePostRegistrationDeviceGuideCTA()
                },
                onLater: {
                    let now = Date().timeIntervalSince1970
                    UserDefaults.standard.set(now, forKey: postRegistrationDeviceNudgeLastShownKey)
                    UserDefaults.standard.synchronize()
                    VisualLogger.shared.log(
                        "⏰ DEVICE_NUDGE later tapped",
                        level: .info,
                        category: "ONBOARDING"
                    )
                    showPostRegistrationDeviceGuide = false
                }
            )
            .environmentObject(localizationManager)
        }
        // Removed quick add sheet; using navigation flow instead
        .overlay(alignment: .bottom) {
            if let message = removeMemberErrorMessage, !message.isEmpty {
                Text(message)
                    .font(.footnote)
                    .foregroundColor(.white)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 10)
                    .background(Color.dangerRed.opacity(0.92))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .shadow(radius: 6)
                    .padding(.bottom, 18)
                    .onTapGesture { removeMemberErrorMessage = nil }
            }
        }
        .overlay(alignment: .bottom) {
            if let message = removeMemberSuccessMessage, !message.isEmpty {
                Text(message)
                    .font(.footnote)
                    .foregroundColor(.white)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 10)
                    .background(Color.green.opacity(0.92))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .shadow(radius: 6)
                    .padding(.bottom, 62)
                    .onTapGesture { removeMemberSuccessMessage = nil }
            }
        }
        .overlay(alignment: .bottom) {
            if let message = familySyncContextBanner, !message.isEmpty {
                Text(message)
                    .font(.footnote)
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 14)
                    .padding(.vertical, 12)
                    .background(Color.orange.opacity(0.94))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .shadow(radius: 6)
                    .padding(.horizontal, 12)
                    .padding(.bottom, 106)
                    .onTapGesture { familySyncContextBanner = nil }
            }
        }
        .overlay(alignment: .bottom) {
            if let hint = incompleteFamilyServerDataBannerText, !hint.isEmpty {
                Text(hint)
                    .font(.footnote)
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 14)
                    .padding(.vertical, 12)
                    .background(Color.purple.opacity(0.92))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .shadow(radius: 6)
                    .padding(.horizontal, 12)
                    .padding(.bottom, 150)
            }
        }
        .confirmationDialog(
            localizationManager.localized("family_remove_member"),
            isPresented: Binding(
                get: { pendingRemovalMember != nil },
                set: { isPresented in
                    if !isPresented { pendingRemovalMember = nil }
                }
            ),
            titleVisibility: .visible
        ) {
            if let member = pendingRemovalMember {
                Button(
                    localizationManager.currentLanguage == .russian
                        ? "Удалить \(member.name)"
                        : "Remove \(member.name)",
                    role: .destructive
                ) {
                    let target = member
                    pendingRemovalMember = nil
                    VisualLogger.shared.log("🗑️ REMOVE DIALOG: confirm tapped for \(target.name) id=\(target.id)", level: .info, category: "FAMILY")
                    VisualLogger.shared.log("🗑️ REMOVE GATE: bypassed (simplified flow)", level: .info, category: "FAMILY")
                    removeFamilyMember(target)
                }
            }
            Button(localizationManager.localized("common_cancel"), role: .cancel) {
                pendingRemovalMember = nil
            }
        } message: {
            if let member = pendingRemovalMember {
                Text(
                    localizationManager.currentLanguage == .russian
                        ? "Подтвердите удаление участника \(member.name)."
                        : "Confirm removing member \(member.name)."
                )
            }
        }
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("family_lang_\(localizationManager.currentLanguage.rawValue)")
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            // ✅ ИСПРАВЛЕНИЕ: Обновляем только баланс, список участников не перезагружаем
            // чтобы не потерять добавленных участников и не запускать цикл повторных GET /family/members
            unicornBalance = UnicornRewardsStore.readBalance(for: UnicornRewardsStore.resolveActiveChildId())
        }
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("FamilyMembersUpdated"))) { _ in
            // FIXED: Prevent notification feedback loop. Only reload if not already syncing.
            // This was the main source of the infinite save/reload cycle.
            guard !isFamilyLoadInProgress && !isFamilySyncInProgress else {
                #if DEBUG
                print("🔄 [FamilyMembersUpdated] Skipping reload - already in progress")
                #endif
                return
            }
            reloadFamilyMembersFromStorageOnly()
            scheduleCoalescedFamilySync()
            if familyMembers.count > 1 {
                UserDefaults.standard.set(false, forKey: postRegistrationDeviceNudgePendingKey)
                UserDefaults.standard.synchronize()
            }
        }
        .onAppear {
            logger.screenLoad("FamilyScreen")
            // Не сбрасываем admin_add_mode сразу: ждём подтверждения сервера или таймаут
            let addTs = UserDefaults.standard.double(forKey: "admin_add_recent_ts")
            let nowTs = Date().timeIntervalSince1970
            if addTs == 0 || (nowTs - addTs) > 60.0 {
                UserDefaults.standard.set(false, forKey: "admin_add_mode")
                UserDefaults.standard.synchronize()
            }

            // ✅ ШАГ 1 + ШАГ 3: Принудительное обновление + проверка роли админа при каждом появлении экрана
            let needsRefresh = UserDefaults.standard.bool(forKey: "needs_family_refresh_on_return")
            if needsRefresh {
                print("🔄 [FamilyScreen.onAppear] Принудительное обновление списка после возврата из профиля")
                UserDefaults.standard.set(false, forKey: "needs_family_refresh_on_return")
                loadFamilyMembers()  // Полная перезагрузка + синхронизация
            } else if familyMembers.isEmpty {
                print("🔄 [FamilyScreen.onAppear] Список пуст, загружаем участников")
                loadFamilyMembers()
            } else {
                print("🔄 [FamilyScreen.onAppear] Список уже загружен (\(familyMembers.count) участников). Проверяем статус админа...")
                // Лёгкая фоновая синхронизация для актуальности delete button и canManageFamilyRoster
                scheduleCoalescedFamilySync()
            }
            updateAdminStatus()  // ✅ OPTIMIZATION: Update cached admin status once on appear
            clearDeleteButtonCache(reason: "onAppear")  // Clear only on major screen updates
            loadParentalRules()  // ✅ BUILD 96: Загружаем ParentalControlRules асинхронно
            refreshParentalControlDemoStrings()
            evaluatePostRegistrationDeviceGuide()
            refreshBypassCardFromServer()
            refreshBypassDetectorsActiveCount()
        }
        .onChange(of: familyBypassSelectedChildId) { _ in
            refreshBypassCardFromServer()
            refreshBypassDetectorsActiveCount()
        }
        // ✅ ИСПРАВЛЕНИЕ #6: Убрали onChange для showAddMemberModal - теперь используем NavigationManager
        // При возврате с AddMemberOptionsScreen список обновится автоматически через onAppear
        // .onChange(of: showAddMemberModal) { newValue in
        //     if !newValue {
        //         print("🔄 [FamilyScreen] Модал добавления закрыт, обновляем список участников")
        //     }
        // }
    }
}

private struct PostRegistrationDeviceGuideModal: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onAddDevice: () -> Void
    let onLater: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("post_reg_device_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)

            Text(localizationManager.localized("post_reg_device_subtitle"))
                .font(.body)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)

            VStack(alignment: .leading, spacing: Spacing.s) {
                Text("1. \(localizationManager.localized("post_reg_device_step_1"))")
                Text("2. \(localizationManager.localized("post_reg_device_step_2"))")
                Text("3. \(localizationManager.localized("post_reg_device_step_3"))")
            }
            .font(.body)
            .foregroundColor(.textPrimary)

            HStack(spacing: Spacing.s) {
                Button(action: onLater) {
                    Text(localizationManager.localized("post_reg_device_later"))
                        .font(.bodyBold)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(Color.secondaryGold.opacity(0.18))
                        .foregroundColor(.secondaryGold)
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(Color.secondaryGold.opacity(0.35), lineWidth: 1)
                        )
                        .cornerRadius(CornerRadius.medium)
                }
                .accessibilityLabel(localizationManager.localized("post_reg_device_later"))

                Button(action: onAddDevice) {
                    Text(localizationManager.localized("post_reg_device_add_now"))
                        .font(.bodyBold)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(
                            LinearGradient(
                                colors: [Color.primaryBlue, Color.primaryBlue.opacity(0.88)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .foregroundColor(.white)
                        .cornerRadius(CornerRadius.medium)
                }
                .accessibilityLabel(localizationManager.localized("post_reg_device_add_now"))
            }
        }
        .padding(Spacing.l)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(
                    LinearGradient(
                        colors: [Color.backgroundDark, Color.primaryBlue.opacity(0.12)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.white.opacity(0.08), lineWidth: 1)
                )
        )
        .accessibilityElement(children: .contain)
        .accessibilityLabel(localizationManager.localized("post_reg_device_title"))
    }
}

// MARK: - Parental Controls Section

extension FamilyScreen {

    /// Демо-строки карточек родительского контроля — всегда из `localizationManager`, не из «замороженного» init `@State`.
    fileprivate func refreshParentalControlDemoStrings() {
        timeRemaining = localizationManager.localized("family_time_remaining_placeholder")
        locationStatus = localizationManager.localized("parental_location_home")
        locationLastUpdate = localizationManager.localized("family_location_last_update_placeholder")
    }
    
    private var parentalControlsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
                            HStack {
                Text(localizationManager.localized("family_parental_control"))
                    .font(.h3)
                    .foregroundColor(Color.secondaryGold)
                    .accessibilityAddTraits(.isHeader)
                                
                                Spacer()
                                
                Button(action: {
                    HapticFeedback.impact(.light)
                    showParentalSettingsModal = true
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "gearshape.fill")
                            .font(.system(size: 16))
                            .foregroundColor(Color.secondaryGold)
                        Text(localizationManager.localized("family_settings"))
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(Color.secondaryGold)
                    }
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, Spacing.xs)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.small)
                            .fill(Color.secondaryGold.opacity(0.15))
                            .overlay(
                                RoundedRectangle(cornerRadius: CornerRadius.small)
                                    .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                            )
                    )
                }
                .accessibilityLabel(localizationManager.localized("family_parental_settings_accessibility"))
            }
            
            // Сетка 2x3 - НОВЫЕ КАРТОЧКИ
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: Spacing.s), count: 2), spacing: Spacing.s) {
                // 1. Блокировка контента
                FamilyParentalControlCard(
                    icon: "🔒",
                    title: localizationManager.localized("parental_content_block"),
                    statusBadge: isContentBlockEnabled
                        ? localizationManager.localized("family_content_block_card_badge_on")
                        : localizationManager.localized("family_content_block_card_badge_off"),
                    statusText: isContentBlockEnabled
                        ? localizationManager.localized("family_content_block_card_status_on")
                        : localizationManager.localized("family_content_block_card_status_off"),
                    metric: localizationManager.localized("family_content_block_card_metric_hint"),
                    cardColor: .red.opacity(0.2),
                    borderColor: .red.opacity(0.4),
                    badgeColor: .successGreen,
                    isEnabled: Binding(
                        get: { isContentBlockEnabled },
                        set: { newValue in
                            isContentBlockEnabled = newValue
                            VisualLogger.shared.log("🔄 family_content_block_enabled = \(newValue)", level: .info, category: "PARENTAL.UI")
                        }
                    ),
                    action: { showContentBlockModal = true }
                )
                .environmentObject(localizationManager)
                
                // 2. Управление временем
                FamilyParentalControlCard(
                    icon: "⏱️",
                    title: localizationManager.localized("parental_time_control"),
                    statusBadge: "⏳",
                    statusText: "⏳ \(timeRemaining)",
                    metric: "\(timeSchedules) \(localizationManager.localized("parental_schedules"))",
                    cardColor: .blue.opacity(0.2),
                    borderColor: .blue.opacity(0.4),
                    badgeColor: .warningOrange,
                    isEnabled: Binding(
                        get: { isTimeControlEnabled },
                        set: { newValue in
                            isTimeControlEnabled = newValue
                            VisualLogger.shared.log("🔄 family_time_control_enabled = \(newValue)", level: .info, category: "PARENTAL.UI")
                        }
                    ),
                    action: { showTimeControlModalNew = true }
                )
                .environmentObject(localizationManager)
                
                // 3. Мониторинг
                FamilyParentalControlCard(
                    icon: "👀",
                    title: localizationManager.localized("parental_monitoring"),
                    statusBadge: "4/5",
                    statusText: "📊 \(monitoringWebsites) \(localizationManager.localized("parental_sites"))",
                    metric: "\(monitoringApps) \(localizationManager.localized("parental_apps"))",
                    cardColor: .purple.opacity(0.2),
                    borderColor: .purple.opacity(0.4),
                    badgeColor: .successGreen,
                    isEnabled: Binding(
                        get: { isMonitoringEnabled },
                        set: { newValue in
                            isMonitoringEnabled = newValue
                            VisualLogger.shared.log("🔄 family_monitoring_enabled = \(newValue)", level: .info, category: "PARENTAL.UI")
                        }
                    ),
                    action: { showMonitoringModalNew = true }
                )
                .environmentObject(localizationManager)
                
                // 4. Геолокация
                FamilyParentalControlCard(
                    icon: "📍",
                    title: localizationManager.localized("parental_geofence"),
                    statusBadge: "🏠",
                    statusText: "🏠 \(locationStatus.isEmpty ? localizationManager.localized("parental_location_home") : locationStatus)",
                    metric: localizationManager.localized("parental_location_accuracy_50m") + " • " + locationLastUpdate,
                    cardColor: .green.opacity(0.2),
                    borderColor: .green.opacity(0.4),
                    badgeColor: .successGreen,
                    isEnabled: Binding(
                        get: { isLocationEnabled },
                        set: { newValue in
                            isLocationEnabled = newValue
                            VisualLogger.shared.log("🔄 family_location_enabled = \(newValue)", level: .info, category: "PARENTAL.UI")
                        }
                    ),
                    action: { showLocationModal = true }
                )
                .environmentObject(localizationManager)
                
                // 5. Отчёты
                FamilyParentalControlCard(
                    icon: "📊",
                    title: localizationManager.localized("parental_reports"),
                    statusBadge: "⚠️ \(reportsAlerts)",
                    statusText: reportsToday ? "📅 \(localizationManager.localized("parental_reports_today"))" : "📅 \(localizationManager.localized("parental_reports_week"))",
                    metric: "\(reportsAlerts) \(localizationManager.localized("parental_alerts"))",
                    cardColor: .orange.opacity(0.2),
                    borderColor: .orange.opacity(0.4),
                    badgeColor: .dangerRed,
                    isEnabled: Binding(
                        get: { isReportsEnabled },
                        set: { newValue in
                            isReportsEnabled = newValue
                            VisualLogger.shared.log("🔄 family_reports_enabled = \(newValue)", level: .info, category: "PARENTAL.UI")
                        }
                    ),
                    action: { showReportsModal = true }
                )
                .environmentObject(localizationManager)
                
                // 6. Дополнительно
                FamilyParentalControlCard(
                    icon: "⚙️",
                    title: localizationManager.localized("parental_additional"),
                    statusBadge: "✋ \(additionalRequests)",
                    statusText: "✋ \(additionalRequests) \(localizationManager.localized("parental_requests"))",
                    metric: additionalProtection ? "🛡️ \(localizationManager.localized("parental_protection_on"))" : "🛡️ \(localizationManager.localized("parental_protection_off"))",
                    cardColor: .gray.opacity(0.2),
                    borderColor: .gray.opacity(0.4),
                    badgeColor: .warningOrange,
                    isEnabled: Binding(
                        get: { isAdditionalEnabled },
                        set: { newValue in
                            isAdditionalEnabled = newValue
                            VisualLogger.shared.log("🔄 family_additional_enabled = \(newValue)", level: .info, category: "PARENTAL.UI")
                        }
                    ),
                    action: { showAdditionalModal = true }
                )
                .environmentObject(localizationManager)
                
                // 7. Защита от обхода (НОВАЯ)
                FamilyParentalControlCard(
                    icon: "🚨",
                    title: localizationManager.localized("parental_bypass_protection"),
                    statusBadge: bypassAttemptsToday > 0
                        ? "🚨 \(bypassAttemptsToday)"
                        : (DNSProtectionManager.shared.isEnabled
                            ? localizationManager.localized("parental_dns_secure")
                            : localizationManager.localized("parental_dns_off")),
                    statusText: DNSProtectionManager.shared.isEnabled
                        ? localizationManager.localized("parental_dns_status_active")
                        : localizationManager.localized("parental_dns_status_inactive"),
                    metric: "\(bypassDetectionActive)/3 \(localizationManager.localized("parental_detection_active"))",
                    cardColor: Color.warningOrange.opacity(0.2),
                    borderColor: Color.warningOrange.opacity(0.4),
                    badgeColor: bypassAttemptsToday > 0 ? .dangerRed : .successGreen,
                    isEnabled: Binding(
                        get: { isBypassProtectionEnabled },
                        set: { newValue in
                            if newValue {
                                DNSProtectionManager.shared.enableProtection()
                            } else {
                                DNSProtectionManager.shared.disableProtection()
                            }
                            isBypassProtectionEnabled = newValue
                            VisualLogger.shared.log("🔄 family_bypass_protection_enabled = \(newValue)", level: .info, category: "PARENTAL.UI")
                        }
                    ),
                    action: { showBypassProtectionModal = true }
                )
                .environmentObject(localizationManager)
            }
            
            // Разделитель и заголовок для геймификации
            VStack(spacing: Spacing.s) {
                Divider()
                    .background(Color.secondaryGold.opacity(0.3))
                    .padding(.vertical, Spacing.m)
                
                HStack {
                    Text(localizationManager.localized("family_gamification"))
                        .font(.h3)
                        .foregroundColor(Color.secondaryGold)
                        .accessibilityAddTraits(.isHeader)
                    
                    Spacer()
                }
            }
            .padding(.top, Spacing.s)
            
            // Reward card (full width)
            // ✅ Fixed: card spans full width, text fits on a single line
            // ✅ Unified entry: always navigate to ChildRewardsScreen
            Button(action: {
                HapticFeedback.impact(.medium)
                logger.buttonTap("Open Game from Family", screen: "Family")
                navigationManager.navigateTo(.childRewards)
            }) {
                HStack(spacing: Spacing.m) {
                    // Large unicorn icon on the left
                    Text("🦄")
                        .font(.system(size: 40))
                        .animation(.easeInOut(duration: 2).repeatForever(autoreverses: true), value: true)
                    
                    // Localized child reward title expands to full width
                    Text(localizationManager.localized("family_child_reward"))
                        .font(.bodyBold)
                        .foregroundColor(Color(red: 0.75, green: 0.52, blue: 0.99))
                        .lineLimit(1)
                        .minimumScaleFactor(0.9) // Немного уменьшаем шрифт если не влезает
                        .frame(maxWidth: .infinity, alignment: .leading) // Text takes maximum width
                    
                    Image(systemName: "chevron.right")
                        .font(.system(size: 14))
                        .foregroundColor(.textTertiary)
                }
                .frame(maxWidth: .infinity, alignment: .leading) // Карточка на всю ширину
                .padding(Spacing.m)
                .background(
                    LinearGradient(
                        colors: [
                            Color(red: 0.66, green: 0.33, blue: 0.97).opacity(0.15),
                            Color(red: 0.93, green: 0.28, blue: 0.6).opacity(0.15)
                        ],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color(red: 0.66, green: 0.33, blue: 0.97).opacity(0.4), lineWidth: 2)
                )
                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
            }
            .buttonStyle(PlainButtonStyle())
            .cardShadow()
            .id("rewardsCard_\(currentUnicornBalance)") // Принудительное обновление при изменении баланса
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                        .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
    }
}

// MARK: - Family Parental Control Card Component

struct FamilyParentalControlCard: View {
    let icon: String
    let title: String
    let statusBadge: String
    let statusText: String
    let metric: String
    let cardColor: Color
    let borderColor: Color
    let badgeColor: Color
    @Binding var isEnabled: Bool
    let action: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: 4) {
            Button(action: {
                HapticFeedback.impact(.medium)
                action()
            }) {
                VStack(spacing: 4) {
                // Badge в верхнем правом углу
                HStack {
                Spacer()
                    Text(statusBadge)
                        .font(.captionSmall)
                        .fontWeight(.bold)
                        .foregroundColor(badgeColor)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(badgeColor.opacity(0.2))
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(badgeColor.opacity(0.5), lineWidth: 1)
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                }
                .frame(height: 20)
                
                // Иконка (уменьшена)
                Text(icon)
                    .font(.system(size: 28))
                    .frame(height: 32)
                
                // Название (меньший шрифт, больше места)
                Text(title)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                    .lineLimit(2)
                    .minimumScaleFactor(0.85)
                    .frame(height: 32)
                    .fixedSize(horizontal: false, vertical: true)
                
                // Статус
                Text(statusText)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                    .lineLimit(1)
                    .frame(height: 14)
                
                // Метрика
                Text(metric)
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
                    .multilineTextAlignment(.center)
                    .lineLimit(1)
                    .frame(height: 14)
                }
            }
            .buttonStyle(PlainButtonStyle())

            Spacer(minLength: 4)

            // Отдельная зона toggle, чтобы не конфликтовать с тапом по карточке
            HStack(spacing: 4) {
                Circle()
                    .fill(isEnabled ? Color.successGreen : Color.textTertiary)
                    .frame(width: 8, height: 8)

                Text(isEnabled ? localizationManager.localized("toggle_on") : localizationManager.localized("toggle_off"))
                    .font(.captionSmall)
                    .fontWeight(.bold)
                    .foregroundColor(isEnabled ? .successGreen : .textTertiary)
                    .frame(width: 24)

                Button(action: {
                    withAnimation(.easeInOut(duration: 0.3)) {
                        isEnabled.toggle()
                    }
                    HapticFeedback.impact(.medium)
                }) {
                    ZStack {
                        RoundedRectangle(cornerRadius: 12)
                            .fill(
                                LinearGradient(
                                    colors: isEnabled ?
                                        [Color(hex: "#8B5CF6"), Color(hex: "#A78BFA")] :
                                        [Color.backgroundMedium, Color.backgroundMedium.opacity(0.5)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                            .frame(width: 40, height: 24)

                        Circle()
                            .fill(Color.white)
                            .frame(width: 20, height: 20)
                            .shadow(color: Color.black.opacity(0.2), radius: 3, x: 0, y: 2)
                            .offset(x: isEnabled ? 8 : -8)
                    }
                }
                .buttonStyle(PlainButtonStyle())
            }
            .frame(height: 24)
        }
        .frame(height: 190)
        .frame(maxWidth: .infinity)
        .padding(.horizontal, 8)
        .padding(.vertical, 10)
        .background(cardColor)
        .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
        // Ободок только если включено (без захода на toggle)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .stroke(
                    isEnabled ? Color.secondaryGold.opacity(0.5) : Color.clear,
                    lineWidth: isEnabled ? 2 : 0
                )
        )
        .buttonStyle(PlainButtonStyle())
        .cardShadow()
    }
}

// MARK: - Content Block Item Component

struct FamilyContentBlockItem: View {
    let icon: String
    let title: String
    let description: String
    @Binding var isEnabled: Bool
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 28))
                .frame(width: 40, height: 40)
            
            // Информация
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer(minLength: 8)
            
            // Toggle без ободков - используем кастомный без padding
            Button(action: {
                withAnimation(.easeInOut(duration: 0.3)) {
                    isEnabled.toggle()
                }
                HapticFeedback.impact(.medium)
            }) {
                ZStack {
                    RoundedRectangle(cornerRadius: 15)
                        .fill(
                            LinearGradient(
                                colors: isEnabled ?
                                    [Color(hex: "#8B5CF6"), Color(hex: "#A78BFA")] :
                                    [Color.backgroundMedium, Color.backgroundMedium.opacity(0.5)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 50, height: 30)
                    
                    Circle()
                        .fill(Color.white)
                        .frame(width: 26, height: 26)
                        .shadow(color: Color.black.opacity(0.2), radius: 4, x: 0, y: 2)
                        .offset(x: isEnabled ? 10 : -10)
                }
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
        // Убрали белый ободок - теперь только фон
    }
}

// MARK: - Config Button Item Component

struct FamilyConfigButtonItem: View {
    let icon: String
    let title: String
    let description: String
    let buttonTitle: String
    let action: () -> Void
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 28))
                .frame(width: 40, height: 40)
            
            // Информация
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer(minLength: 8)
            
            // Золотая кнопка
            Button(action: {
                HapticFeedback.impact(.medium)
                action()
            }) {
                Text(buttonTitle)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.secondaryGold)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.xs)
                    .background(Color.secondaryGold.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.secondaryGold.opacity(0.5), lineWidth: 1)
                    )
                    .cornerRadius(8)
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
    }
}

// MARK: - Badge Item Component

struct FamilyBadgeItem: View {
    let icon: String
    let title: String
    let description: String
    let badgeText: String
    let badgeColor: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            action()
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка
                Text(icon)
                    .font(.system(size: 28))
                    .frame(width: 40, height: 40)
                
                // Информация
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                        .lineLimit(2)
                        .fixedSize(horizontal: false, vertical: true)
                    
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                }
                
                Spacer(minLength: 8)
                
                // Badge
                Text(badgeText)
                    .font(.captionSmall)
                    .fontWeight(.bold)
                    .foregroundColor(badgeColor)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, 4)
                    .background(badgeColor.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(badgeColor.opacity(0.5), lineWidth: 1)
                    )
                    .cornerRadius(8)
            }
            .padding(Spacing.m)
            .background(Color.backgroundMedium.opacity(0.2))
            .cornerRadius(CornerRadius.medium)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Action Button Item Component

struct FamilyActionButtonItem: View {
    let icon: String
    let title: String
    let description: String
    let buttonTitle: String
    let action: () -> Void
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 28))
                .frame(width: 40, height: 40)
            
            // Информация
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer(minLength: 8)
            
            // Красная кнопка действия
            Button(action: {
                HapticFeedback.impact(.medium)
                action()
            }) {
                Text(buttonTitle)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.dangerRed)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.xs)
                    .background(Color.dangerRed.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.dangerRed.opacity(0.5), lineWidth: 1)
                    )
                    .cornerRadius(8)
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
    }
}

struct FamilyTimeControlModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для детальных модалов настроек
    @State private var showScreenTimeSettings = false
    @State private var showScheduleSettings = false
    @State private var showSleepTimeSettings = false
    @State private var showAppLimitsSettings = false
    
    // Настройки времени с сохранением в UserDefaults
    @AppStorage("parental_screen_time_limit") private var screenTimeLimit: String = "3h/day"
    @AppStorage("parental_screen_time_remaining") private var screenTimeRemaining: String = "1h 24m"
    @AppStorage("parental_schedule_weekdays") private var scheduleWeekdays: String = "15:00-18:00"
    @AppStorage("parental_schedule_weekends") private var scheduleWeekends: String = "10:00-20:00"
    @AppStorage("parental_bedtime_start") private var bedtimeStart: String = "22:00"
    @AppStorage("parental_bedtime_end") private var bedtimeEnd: String = "07:00"
    @AppStorage("parental_instagram_limit") private var instagramLimit: String = "30 min"
    @AppStorage("parental_tiktok_limit") private var tiktokLimit: String = "20 min"
    
    // Статистика
    @State private var totalTimeUsed: String = "1h 36m"
    @State private var totalTimeLimit: String = "3h"
    @State private var instagramUsed: String = "18 min"
    @State private var instagramLimitStat: String = "30 min"
    @State private var tiktokUsed: String = "12 min"
    @State private var tiktokLimitStat: String = "20 min"
    
    var body: some View {
        FamilyModalBaseView(
            title: "⏱️ \(localizationManager.localized("family_time_management"))",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Экранное время
                FamilyConfigButtonItem(
                    icon: "📱",
                    title: localizationManager.localized("family_screen_time"),
                    description: "\(localizationManager.localized("family_screen_time_now")) \(screenTimeLimit) (\(localizationManager.localized("family_screen_time_remaining")) \(screenTimeRemaining))",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showScreenTimeSettings = true }
                )
                
                // 2. Расписание доступа
                FamilyConfigButtonItem(
                    icon: "📅",
                    title: localizationManager.localized("family_schedule_access"),
                    description: "\(localizationManager.localized("family_weekdays_short")) \(scheduleWeekdays), \(localizationManager.localized("family_weekends_short")) \(scheduleWeekends)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showScheduleSettings = true }
                )
                
                // 3. Время сна
                FamilyConfigButtonItem(
                    icon: "🌙",
                    title: localizationManager.localized("family_bedtime"),
                    description: "\(localizationManager.localized("family_bedtime_block")) \(bedtimeStart) - \(bedtimeEnd)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showSleepTimeSettings = true }
                )
                
                // 4. Лимиты по приложениям
                FamilyConfigButtonItem(
                    icon: "⏰",
                    title: localizationManager.localized("family_app_limits"),
                    description: "\(localizationManager.localized("family_instagram")) \(instagramLimit), \(localizationManager.localized("family_tiktok")) \(tiktokLimit)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showAppLimitsSettings = true }
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_today"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text(localizationManager.localized("family_total_time"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(totalTimeUsed) / \(totalTimeLimit)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_instagram"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(instagramUsed) / \(instagramLimitStat)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_tiktok"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(tiktokUsed) / \(tiktokLimitStat)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        // Детальные модалы настроек
        .sheet(isPresented: $showScreenTimeSettings) {
            ScreenTimeSettingsModal(isPresented: $showScreenTimeSettings)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showScheduleSettings) {
            ScheduleSettingsModal(isPresented: $showScheduleSettings)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showSleepTimeSettings) {
            SleepTimeSettingsModal(isPresented: $showSleepTimeSettings)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAppLimitsSettings) {
            AppLimitsSettingsModal(isPresented: $showAppLimitsSettings)
                .environmentObject(localizationManager)
        }
        .onAppear {
            // Загружаем статистику при открытии модала
            loadTimeStatistics()
        }
        .withVisualLogger()
    }
    
    // Загрузка статистики времени из UserDefaults
    private func loadTimeStatistics() {
        if let stats = UserDefaults.standard.dictionary(forKey: "parental_time_stats") as? [String: String] {
            totalTimeUsed = stats["totalTimeUsed"] ?? "1h 36m"
            totalTimeLimit = stats["totalTimeLimit"] ?? "3h"
            instagramUsed = stats["instagramUsed"] ?? "18 min"
            instagramLimitStat = stats["instagramLimitStat"] ?? "30 min"
            tiktokUsed = stats["tiktokUsed"] ?? "12 min"
            tiktokLimitStat = stats["tiktokLimitStat"] ?? "20 min"
        }
    }
}

// MARK: - Local network layers (Smart DNS / Safari CB on parent device, int-12 / int-13)

private struct FamilyNetworkLayersLocalStatusBlock: View {
    @ObservedObject private var dnsManager = DNSProtectionManager.shared
    @ObservedObject private var contentBlockerManager = ContentBlockerManager.shared
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("family_modal_network_layers_title"))
                .font(.bodyBold)
                .foregroundColor(.secondaryGold)

            Text(localizationManager.localized("family_modal_network_layers_scope"))
                .font(.captionSmall)
                .foregroundColor(.textTertiary)
                .fixedSize(horizontal: false, vertical: true)

            Text(localizationManager.localized("family_modal_network_layers_p2_note"))
                .font(.captionSmall)
                .foregroundColor(.textTertiary)
                .fixedSize(horizontal: false, vertical: true)

            Text(localizationManager.localized("main_family_smart_dns_status", dnsShortLabel))
                .font(.caption)
                .foregroundColor(.textSecondary)

            Text(localizationManager.localized("main_family_safari_cb_status", safariShortLabel))
                .font(.caption)
                .foregroundColor(.textSecondary)

            Text(localizationManager.localized("main_family_network_layers_hint"))
                .font(.captionSmall)
                .foregroundColor(.textTertiary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(CornerRadius.medium)
        .onAppear {
            dnsManager.loadStatus()
            Task {
                await contentBlockerManager.checkBlockingStatus()
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: Notification.Name.networkLayerIndicatorsRefresh)) { _ in
            dnsManager.loadStatus()
            Task {
                await contentBlockerManager.checkBlockingStatus()
            }
        }
    }

    private var dnsShortLabel: String {
        dnsManager.isEnabled
            ? localizationManager.localized("main_toggle_short_on")
            : localizationManager.localized("main_toggle_short_off")
    }

    private var safariShortLabel: String {
        contentBlockerManager.isEnabled
            ? localizationManager.localized("main_toggle_short_on")
            : localizationManager.localized("main_toggle_short_off")
    }
}

struct FamilyMonitoringModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @AppStorage("parental_selected_child_id") private var selectedChildId: String = ""
    @AppStorage("parental_selected_child") private var legacySelectedChild: String = ""
    
    // Состояния для toggle-элементов с сохранением в UserDefaults
    @AppStorage("parental_messages_monitoring") private var isMessagesMonitoringEnabled: Bool = false
    @AppStorage("parental_screenshots_enabled") private var isScreenshotsEnabled: Bool = false
    
    // Состояния для детальных модалов просмотра
    @State private var showBrowserHistory = false
    @State private var showAppHistory = false
    @State private var showContacts = false
    
    @State private var browserSitesCount: Int = 0
    @State private var appsUsedCount: Int = 0
    @State private var contactsCount: Int = 0
    
    @State private var topSite: String = "—"
    @State private var topSiteVisits: Int = 0
    @State private var topApp: String = "—"
    @State private var topAppTime: String = "—"
    @State private var activeContacts: Int = 0
    
    @State private var isLoadingMonitoringDetail = false
    @State private var parentalMonitoringSyncTask: Task<Void, Never>?
    @State private var isApplyingParentalMonitoringSettings = false
    
    private var effectiveChildId: String {
        if !selectedChildId.isEmpty { return selectedChildId }
        return legacySelectedChild
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_monitoring_modal_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. История браузера - Badge Item (кликабельный)
                FamilyBadgeItem(
                    icon: "🌐",
                    title: localizationManager.localized("family_browser_history"),
                    description: "\(browserSitesCount) \(localizationManager.localized("family_sites")) \(localizationManager.localized("family_per_week"))",
                    badgeText: localizationManager.localized("family_active_badge"),
                    badgeColor: .successGreen,
                    action: { showBrowserHistory = true }
                )
                
                // 2. История приложений - Badge Item (кликабельный)
                FamilyBadgeItem(
                    icon: "📲",
                    title: localizationManager.localized("family_app_history"),
                    description: "\(appsUsedCount) \(localizationManager.localized("family_apps")) \(localizationManager.localized("family_used"))",
                    badgeText: localizationManager.localized("family_active_badge"),
                    badgeColor: .successGreen,
                    action: { showAppHistory = true }
                )
                
                // 3. Мониторинг сообщений - Toggle Item
                FamilyContentBlockItem(
                    icon: "💬",
                    title: localizationManager.localized("family_message_monitoring"),
                    description: localizationManager.localized("family_message_monitoring_desc"),
                    isEnabled: $isMessagesMonitoringEnabled
                )
                
                // 4. Просмотр контактов - Badge Item (кликабельный)
                FamilyBadgeItem(
                    icon: "👥",
                    title: localizationManager.localized("family_contacts_view"),
                    description: localizationManager.localized("family_contacts_desc"),
                    badgeText: localizationManager.localized("family_active_badge"),
                    badgeColor: .successGreen,
                    action: { showContacts = true }
                )
                
                // 5. Скриншоты экрана - Toggle Item
                FamilyContentBlockItem(
                    icon: "📸",
                    title: localizationManager.localized("family_screenshots"),
                    description: localizationManager.localized("family_screenshots_desc"),
                    isEnabled: $isScreenshotsEnabled
                )

                FamilyNetworkLayersLocalStatusBlock()
                    .environmentObject(localizationManager)
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_week_detailed"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text(localizationManager.localized("family_top_site"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(topSite) (\(topSiteVisits) \(localizationManager.localized("family_visits")))")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_top_app"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(topApp) (\(topAppTime))")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_contacts"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(activeContacts) \(localizationManager.localized("family_active"))")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        // Детальные модалы просмотра (создадим полноценные ниже)
        .sheet(isPresented: $showBrowserHistory) {
            BrowserHistoryDetailModal(
                isPresented: $showBrowserHistory,
                childId: effectiveChildId.isEmpty ? nil : effectiveChildId
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAppHistory) {
            AppHistoryDetailModal(
                isPresented: $showAppHistory,
                childId: effectiveChildId.isEmpty ? nil : effectiveChildId
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showContacts) {
            ContactsDetailModal(
                isPresented: $showContacts,
                childId: effectiveChildId.isEmpty ? nil : effectiveChildId
            )
            .environmentObject(localizationManager)
        }
        .onAppear {
            refreshMonitoringSummaryFromServer()
            loadParentalMonitoringTogglesFromServerForModal()
        }
        .onChange(of: selectedChildId) { _ in
            refreshMonitoringSummaryFromServer()
            loadParentalMonitoringTogglesFromServerForModal()
        }
        .onChange(of: isMessagesMonitoringEnabled) { _ in
            scheduleParentalMonitoringSyncFromFamilyModal()
        }
        .onChange(of: isScreenshotsEnabled) { _ in
            scheduleParentalMonitoringSyncFromFamilyModal()
        }
        // UI-логи parental toggles централизованы в AdvancedProtectionSettingsScreen,
        // чтобы не дублировать одинаковые записи в mini-log.
        .withVisualLogger()
    }

    private func loadParentalMonitoringTogglesFromServerForModal() {
        Task { @MainActor in
            isApplyingParentalMonitoringSettings = true
            let flags = await ComponentConfigurationService.shared.loadParentalMonitoringTogglesFromServer()
            if let m = flags.messages { isMessagesMonitoringEnabled = m }
            if let s = flags.screenshots { isScreenshotsEnabled = s }
            isApplyingParentalMonitoringSettings = false
        }
    }

    private func scheduleParentalMonitoringSyncFromFamilyModal() {
        guard !isApplyingParentalMonitoringSettings else { return }
        parentalMonitoringSyncTask?.cancel()
        parentalMonitoringSyncTask = Task {
            try? await Task.sleep(nanoseconds: 250_000_000)
            if Task.isCancelled { return }
            await syncParentalMonitoringTogglesToServerFromFamilyModal()
        }
    }

    @MainActor
    private func syncParentalMonitoringTogglesToServerFromFamilyModal() async {
        do {
            try await ComponentConfigurationService.shared.saveParentalMonitoringTogglesToServer(
                messagesEnabled: isMessagesMonitoringEnabled,
                screenshotsEnabled: isScreenshotsEnabled
            )
        } catch {
            // Ошибка уже в логах компонента; модалка не блокирует UX.
        }
    }
    
    private func refreshMonitoringSummaryFromServer() {
        guard !isLoadingMonitoringDetail else { return }
        isLoadingMonitoringDetail = true
        let cid = effectiveChildId.isEmpty ? nil : effectiveChildId
        ParentalControlManager.shared.getMonitoringDetail(childId: cid) { result in
            DispatchQueue.main.async {
                isLoadingMonitoringDetail = false
                switch result {
                case .success(let detail):
                    let s = detail.summary
                    browserSitesCount = s.browserSitesWeek
                    appsUsedCount = s.appsUsedWeek
                    contactsCount = s.contactsActive
                    activeContacts = s.contactsActive
                    if let first = detail.topSites.first {
                        topSite = first.site
                        topSiteVisits = first.visits
                    } else {
                        topSite = "—"
                        topSiteVisits = 0
                    }
                    if let app = detail.topApps.first {
                        topApp = app.name
                        topAppTime = formatMonitoringUsageMinutes(app.usageMinutes)
                    } else {
                        topApp = "—"
                        topAppTime = "—"
                    }
                case .failure:
                    break
                }
            }
        }
    }
    
    private func formatMonitoringUsageMinutes(_ minutes: Int) -> String {
        let h = minutes / 60
        let m = minutes % 60
        let hourUnit = localizationManager.localized("analytics_hour")
        let minuteUnit = localizationManager.localized("analytics_min")
        if h == 0 { return "\(m) \(minuteUnit)" }
        if m == 0 { return "\(h) \(hourUnit)" }
        return "\(h) \(hourUnit) \(m) \(minuteUnit)"
    }
}

struct FamilyLocationModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // ✅ ИНТЕГРАЦИЯ LocationManager
    @StateObject private var locationManager = LocationManager.shared
    
    // API сервис для загрузки данных
    private let apiService = APIService.shared
    
    // Состояния для toggle-элементов с сохранением в UserDefaults
    @AppStorage("parental_location_enabled") private var isLocationEnabledState: Bool = true
    @AppStorage("parental_sos_enabled") private var isSOSEnabled: Bool = true
    
    // Состояния для детальных модалов
    @State private var showGeofencesSettings = false
    @State private var showLocationHistory = false
    
    // Данные (загружаются из API и UserDefaults)
    @State private var locationStatus: String = ""
    @State private var locationLastUpdate: String = ""
    @State private var geofencesCount: Int = 2
    @State private var geofencesList: String = ""
    @State private var isLoadingLocationData: Bool = false
    
    // Статистика событий сегодня (загружается из UserDefaults)
    @State private var todayEvents: [LocationEvent] = []
    
    // Ключ для статистики геолокации
    private let statsKey = "parental_location_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_location"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Местоположение - Toggle Item
                FamilyContentBlockItem(
                    icon: "📍",
                    title: localizationManager.localized("family_location"),
                    description: "\(locationStatus) • \(locationLastUpdate)",
                    isEnabled: $isLocationEnabledState
                )
                
                // 2. Геозоны - Config Button Item
                FamilyConfigButtonItem(
                    icon: "🗺️",
                    title: localizationManager.localized("family_geofences"),
                    description: "\(geofencesCount) \(localizationManager.localized("family_active_colon")) \(geofencesList)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showGeofencesSettings = true }
                )
                
                // 3. История перемещений - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📜",
                    title: localizationManager.localized("family_movement_history"),
                    description: localizationManager.localized("family_movement_desc"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showLocationHistory = true }
                )
                
                // 4. Кнопка SOS - Toggle Item
                FamilyContentBlockItem(
                    icon: "🆘",
                    title: localizationManager.localized("family_sos_button"),
                    description: localizationManager.localized("family_sos_desc"),
                    isEnabled: $isSOSEnabled
                )

                // Точность геозоны — аккуратно ниже кнопки SOS
                Text("\(localizationManager.localized("parental_location_accuracy_50m"))"
                     + (locationLastUpdate.isEmpty ? "" : " • \(locationLastUpdate)"))
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, Spacing.s)
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_today_detailed"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(todayEvents) { event in
                        HStack {
                            Text("• \(event.time) - \(event.action)")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text(event.status.icon)
                                .font(.caption)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .sheet(isPresented: $showGeofencesSettings) {
            GeofencesSettingsModal(isPresented: $showGeofencesSettings)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showLocationHistory) {
            LocationHistoryDetailModal(isPresented: $showLocationHistory)
                .environmentObject(localizationManager)
        }
        .id("location_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            // ✅ ИНТЕГРАЦИЯ: Запрос разрешения и запуск Significant-Change
            setupLocationServices()
            // Загружаем статистику при открытии модала
            loadLocationStatistics()
        }
        .onChange(of: isLocationEnabledState) { newValue in
            VisualLogger.shared.log(
                "🔄 family_location_enabled = \(newValue)",
                level: .info,
                category: "PARENTAL.UI"
            )
            print("✅ Geolocation: \(newValue ? "ON" : "OFF")")
            if newValue {
                // ✅ ИНТЕГРАЦИЯ: Запуск мониторинга при включении
                setupLocationServices()
            } else {
                // ✅ ИНТЕГРАЦИЯ: Остановка мониторинга при выключении
                locationManager.stopSignificantLocationChanges()
            }
        }
        .onChange(of: isSOSEnabled) { newValue in
            VisualLogger.shared.log(
                "🔄 family_sos_enabled = \(newValue)",
                level: .info,
                category: "PARENTAL.UI"
            )
            print("✅ SOS button: \(newValue ? "ON" : "OFF")")
        }
        .withVisualLogger()
    }
    
    // ✅ ИНТЕГРАЦИЯ: Настройка LocationManager
    private func setupLocationServices() {
        print("📍 FamilyLocationModal: Настройка LocationManager...")
        
        // Запрос разрешения Always (для Significant-Change и Region Monitoring)
        if locationManager.authorizationStatus != .authorizedAlways {
            locationManager.requestAuthorization(always: true)
        }
        
        // Запуск Significant-Change Location Service
        if isLocationEnabledState && locationManager.hasRequiredAuthorization(forBackground: true) {
            locationManager.startSignificantLocationChanges()
            print("✅ FamilyLocationModal: Significant-Change запущен")
        }
        
        // Загрузка и мониторинг геозон
        loadAndMonitorGeofences()
    }
    
    // ✅ ИНТЕГРАЦИЯ: Загрузка и мониторинг геозон
    private func loadAndMonitorGeofences() {
        // Загружаем геозоны из UserDefaults
        let geofencesKey = "geofences_settings"
        guard let data = UserDefaults.standard.data(forKey: geofencesKey),
              let decoded = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data) else {
            print("⚠️ FamilyLocationModal: Геозоны не найдены")
            return
        }
        
        // Мониторим каждую геозону через LocationManager
        for geofenceCodable in decoded {
            // Получаем координаты из адреса (здесь нужна геокодировка)
            // Для примера используем координаты Москвы
            let center = CLLocationCoordinate2D(latitude: 55.7558, longitude: 37.6173)
            
            do {
                // Используем координаты по умолчанию (Москва)
                // TODO: Добавить геокодировку адреса для получения реальных координат
                let geofenceCenter = center
                
                let geofence = GeofenceItem(
                    name: geofenceCodable.name,
                    address: geofenceCodable.address,
                    radius: geofenceCodable.radius
                )
                
                try locationManager.startMonitoring(geofence: geofence, center: geofenceCenter)
                print("✅ FamilyLocationModal: Геозона '\(geofence.name)' добавлена в мониторинг")
            } catch {
                print("❌ FamilyLocationModal: Ошибка добавления геозоны '\(geofenceCodable.name)': \(error.localizedDescription)")
            }
        }
    }
    
    // Загрузка статистики геолокации из UserDefaults и API
    private func loadLocationStatistics() {
        print("🔍 FamilyLocationModal: Загрузка статистики геолокации...")
        
        // ✅ ИНТЕГРАЦИЯ: Получение текущего местоположения
        Task {
            do {
                let currentLocation = try await locationManager.getCurrentLocation()
                print("✅ FamilyLocationModal: Текущее местоположение: \(currentLocation.coordinate.latitude), \(currentLocation.coordinate.longitude)")
                
                // Обновляем статус местоположения
                DispatchQueue.main.async {
                    self.locationStatus = String(format: "📍 %.4f, %.4f", currentLocation.coordinate.latitude, currentLocation.coordinate.longitude)
                    self.locationLastUpdate = String(format: localizationManager.localized("family_min_ago_format"), 0)
                }
            } catch {
                print("⚠️ FamilyLocationModal: Ошибка получения местоположения: \(error.localizedDescription)")
            }
        }
        
        // Пробуем загрузить из API
        loadLocationDataFromAPI()
        
        // Fallback на UserDefaults и значения по умолчанию
        let home = localizationManager.localized("geofences_home")
        let street = localizationManager.localized("geofences_street_lenin")
        let school = localizationManager.localized("geofences_school")
        let defaultStatus = "🏠 \(home) (\(street))"
        let defaultLastUpdate = String(format: localizationManager.localized("family_min_ago_format"), 2)
        let defaultGeofences = [home, school]
        let defaultGeofenceList = defaultGeofences.joined(separator: ", ")
        
        // Устанавливаем значения по умолчанию
        locationStatus = defaultStatus
        locationLastUpdate = defaultLastUpdate
        geofencesCount = defaultGeofences.count
        geofencesList = defaultGeofenceList
        
        // Загружаем статус и данные (если есть сохранённые значения)
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            locationStatus = stats["locationStatus"] as? String ?? defaultStatus
            locationLastUpdate = stats["locationLastUpdate"] as? String ?? defaultLastUpdate
            geofencesCount = stats["geofencesCount"] as? Int ?? defaultGeofences.count
            geofencesList = stats["geofencesList"] as? String ?? defaultGeofenceList
            print("✅ FamilyLocationModal: Загружено из UserDefaults")
        } else {
            print("⚠️ FamilyLocationModal: Используются значения по умолчанию")
        }
        
        // Загружаем события сегодня (по умолчанию примерные)
        todayEvents = [
            LocationEvent(time: "08:30", action: localizationManager.localized("location_left_home"), status: .departure),
            LocationEvent(time: "09:15", action: localizationManager.localized("location_arrived_school"), status: .arrival),
            LocationEvent(time: "15:45", action: localizationManager.localized("location_returned_home"), status: .arrival)
        ]
    }
    
    /// Загрузка данных геолокации из API
    private func loadLocationDataFromAPI() {
        guard !isLoadingLocationData else { return }
        
        isLoadingLocationData = true
        print("🔍 FamilyLocationModal: Загрузка данных геолокации из API...")
        
        // Загружаем статистику геолокации
        apiService.getLocationStats { result in
            DispatchQueue.main.async {
                self.isLoadingLocationData = false
                
                switch result {
                case .success(let stats):
                    print("✅ FamilyLocationModal: Данные геолокации загружены из API")
                    // Обновляем данные из API (если есть реальные данные)
                    // TODO: Интегрировать реальные данные из stats
                    _ = stats  // Используем для будущей интеграции
                    
                case .failure(let error):
                    print("⚠️ FamilyLocationModal: Ошибка загрузки данных из API: \(error.localizedDescription)")
                    // Используем данные из UserDefaults (fallback)
                }
            }
        }
        
        // Загружаем запросы местоположения
        apiService.getLocationRequests(limit: 10) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let requests):
                    print("✅ FamilyLocationModal: Загружено \(requests.count) запросов местоположения")
                    // TODO: Обработать запросы и обновить UI
                    
                case .failure(let error):
                    print("⚠️ FamilyLocationModal: Ошибка загрузки запросов: \(error.localizedDescription)")
                }
            }
        }
    }
}

// MARK: - Location Event Model

// Models moved to global APIModels.swift

struct FamilyReportsModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Выбранный ребёнок для загрузки статистики (новый ID + legacy fallback)
    @AppStorage("parental_selected_child_id") private var selectedChildId: String = ""
    @AppStorage("parental_selected_child") private var legacySelectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Состояния для детальных модалов просмотра
    @State private var showWeeklyReport = false
    @State private var showSuspiciousActivity = false
    @State private var showTopSites = false
    @State private var showTopApps = false
    @State private var showUsageHours = false
    @State private var showBypassAttempts = false
    
    @State private var suspiciousActivityCount: Int = 0
    @State private var bypassAttemptsCount: Int = 0
    
    // Статистика предупреждений (загружается из UserDefaults)
    @State private var warnings: [ReportWarning] = []
    
    // Ключ для статистики отчётов
    private let statsKey = "parental_reports_stats"
    
    private var effectiveChildId: String {
        if !selectedChildId.isEmpty { return selectedChildId }
        return legacySelectedChild
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("reports_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Еженедельный отчёт - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📅",
                    title: localizationManager.localized("family_weekly_report"),
                    description: localizationManager.localized("family_weekly_report_desc"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showWeeklyReport = true }
                )
                
                // 2. Подозрительная активность - Badge Item
                FamilyBadgeItem(
                    icon: "⚠️",
                    title: localizationManager.localized("family_suspicious_activity_title"),
                    description: "\(suspiciousActivityCount) \(localizationManager.localized("family_new")) \(localizationManager.localized("family_warnings"))",
                    badgeText: "\(suspiciousActivityCount)",
                    badgeColor: .dangerRed,
                    action: { showSuspiciousActivity = true }
                )
                
                // 3. Top-5 сайтов - Config Button Item
                FamilyConfigButtonItem(
                    icon: "🌐",
                    title: localizationManager.localized("family_top_5_sites"),
                    description: localizationManager.localized("family_top_sites_desc"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showTopSites = true }
                )
                
                // 4. Top-5 приложений - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📱",
                    title: localizationManager.localized("family_top_5_apps"),
                    description: localizationManager.localized("family_usage_by_time"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showTopApps = true }
                )
                
                // 5. Пиковые часы активности - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📊",
                    title: localizationManager.localized("reports_peak_hours"),
                    description: localizationManager.localized("reports_peak_hours_desc"),
                    buttonTitle: localizationManager.localized("reports_view"),
                    action: { showUsageHours = true }
                )
                
                // 6. Попытки обхода блокировок - Badge Item
                FamilyBadgeItem(
                    icon: "🛡️",
                    title: localizationManager.localized("reports_bypass_attempts"),
                    description: localizationManager.localized("reports_bypass_attempts_desc"),
                    badgeText: "\(bypassAttemptsCount)",
                    badgeColor: .successGreen,
                    action: { showBypassAttempts = true }
                )

                FamilyNetworkLayersLocalStatusBlock()
                    .environmentObject(localizationManager)
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика предупреждений
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_suspicious_activity"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(warnings) { warning in
                        HStack {
                            Text("• \(warning.text)")
                                .font(.caption)
                                .foregroundColor(warning.color)
                            Spacer()
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .sheet(isPresented: $showWeeklyReport) {
            WeeklyReportDetailModal(
                isPresented: $showWeeklyReport,
                childId: effectiveChildId.isEmpty ? nil : effectiveChildId
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showSuspiciousActivity) {
            SuspiciousActivityDetailModal(
                isPresented: $showSuspiciousActivity,
                childId: effectiveChildId.isEmpty ? nil : effectiveChildId
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showTopSites) {
            TopSitesDetailModal(
                isPresented: $showTopSites,
                childId: effectiveChildId.isEmpty ? nil : effectiveChildId
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showTopApps) {
            TopAppsDetailModal(
                isPresented: $showTopApps,
                childId: effectiveChildId.isEmpty ? nil : effectiveChildId
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showUsageHours) {
            UsageHoursDetailModal(
                isPresented: $showUsageHours,
                childId: effectiveChildId.isEmpty ? nil : effectiveChildId
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showBypassAttempts) {
            BypassAttemptsDetailModal(isPresented: $showBypassAttempts)
                .environmentObject(localizationManager)
        }
        .id("reports_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadChildren()
            if selectedChildId.isEmpty && !legacySelectedChild.isEmpty {
                selectedChildId = legacySelectedChild
            }
            // Загружаем статистику при открытии модала
            loadReportsStatistics()
        }
        .onChange(of: selectedChildId) { _ in
            loadReportsStatistics()
        }
        .withVisualLogger()
    }
    
    // Загрузка списка детей из family_members_list
    private func loadChildren() {
        guard let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            children = []
            return
        }
        
        children = decoded
            .filter { member in
                member.role == .child || member.role == .teenager
            }
            .map { $0.name }
    }
    
    // Загрузка статистики отчётов из UserDefaults и API
    private func loadReportsStatistics() {
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            bypassAttemptsCount = stats["bypassAttemptsCount"] as? Int ?? 0
        }
        
        let cid = effectiveChildId.isEmpty ? nil : effectiveChildId
        ParentalControlManager.shared.getMonitoringDetail(childId: cid) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let detail):
                    suspiciousActivityCount = detail.suspicious.count
                    warnings = detail.suspicious.prefix(5).map { row in
                        ReportWarning(
                            text: row.text,
                            color: row.level == "high" ? .dangerRed : .warningOrange
                        )
                    }
                    var cachedStats = UserDefaults.standard.dictionary(forKey: self.statsKey) ?? [:]
                    cachedStats["suspiciousActivityCount"] = detail.suspicious.count
                    UserDefaults.standard.set(cachedStats, forKey: self.statsKey)
                case .failure:
                    suspiciousActivityCount = 0
                    warnings = []
                }
            }
        }
        
        let manager = ParentalControlManager.shared
        manager.getBypassStats(childId: effectiveChildId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let stats):
                    self.bypassAttemptsCount = stats.week
                    var cachedStats = UserDefaults.standard.dictionary(forKey: self.statsKey) ?? [:]
                    cachedStats["bypassAttemptsCount"] = stats.week
                    UserDefaults.standard.set(cachedStats, forKey: self.statsKey)
                case .failure(let error):
                    print("⚠️ Failed to load bypass statistics: \(error.localizedDescription)")
                    let local = ParentalControlManager.shared.localBypassAggregates(
                        for: effectiveChildId.isEmpty ? nil : effectiveChildId
                    )
                    self.bypassAttemptsCount = local.week
                    var cachedStats = UserDefaults.standard.dictionary(forKey: self.statsKey) ?? [:]
                    cachedStats["bypassAttemptsCount"] = local.week
                    UserDefaults.standard.set(cachedStats, forKey: self.statsKey)
                }
            }
        }
    }
}

// MARK: - Report Warning Model

// ReportWarning moved to global APIModels.swift

struct FamilyAdditionalModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для toggle-элементов с сохранением в UserDefaults
    @AppStorage("parental_homework_mode") private var isHomeworkModeEnabled: Bool = false
    
    // Состояния для детальных модалов
    @State private var showRemoteLockConfirmation = false
    @State private var showRemoteWipeConfirmation = false
    @State private var showAccessRequests = false
    @State private var showYouTubeSettings = false
    
    // Mock-данные (загружаются из UserDefaults)
    @State private var accessRequestsCount: Int = 2
    @State private var deviceName: String = "iPhone 12 (Alexey)"
    @State private var deviceStatus: String = ""
    @State private var deviceBattery: String = "67%"
    
    // Статистика запросов (загружается из UserDefaults)
    @State private var requests: [AccessRequest] = []
    
    // Ключ для статистики дополнительных настроек
    private let statsKey = "parental_additional_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("additional_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Удалённая блокировка - Action Button Item
                FamilyActionButtonItem(
                    icon: "🔒",
                    title: localizationManager.localized("remote_lock_title"),
                    description: localizationManager.localized("remote_lock_desc"),
                    buttonTitle: localizationManager.localized("remote_lock_confirm"),
                    action: { showRemoteLockConfirmation = true }
                )
                
                // 2. Удаление данных - Action Button Item
                FamilyActionButtonItem(
                    icon: "🗑️",
                    title: localizationManager.localized("data_deletion_title"),
                    description: localizationManager.localized("data_deletion_desc"),
                    buttonTitle: localizationManager.localized("data_deletion_button"),
                    action: { showRemoteWipeConfirmation = true }
                )
                
                // 3. Запросы доступа - Badge Item
                FamilyBadgeItem(
                    icon: "✋",
                    title: localizationManager.localized("family_access_requests"),
                    description: "\(accessRequestsCount) \(localizationManager.localized("family_access_requests_count"))",
                    badgeText: "\(accessRequestsCount)",
                    badgeColor: .warningOrange,
                    action: { showAccessRequests = true }
                )
                
                // 4. YouTube фильтрация - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📺",
                    title: localizationManager.localized("family_youtube_filtering"),
                    description: localizationManager.localized("family_age_restriction"),
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: {
                        VisualLogger.shared.log("⚙️ Open YouTube settings", level: .info, category: "PARENTAL.UI")
                        showYouTubeSettings = true
                    }
                )
                
                // 5. Режим "Homework mode" - Toggle Item
                FamilyContentBlockItem(
                    icon: "📚",
                    title: localizationManager.localized("family_homework_mode"),
                    description: localizationManager.localized("family_homework_desc"),
                    isEnabled: $isHomeworkModeEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика запросов
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_access_requests"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(requests) { request in
                        HStack {
                            Text("• \(localizationManager.localized("family_unlock")) \(request.app) (\(request.time))")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .sheet(isPresented: $showRemoteLockConfirmation) {
            RemoteLockConfirmationModal(isPresented: $showRemoteLockConfirmation, deviceName: deviceName, deviceStatus: deviceStatus, deviceBattery: deviceBattery)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showRemoteWipeConfirmation) {
            RemoteWipeConfirmationModal(isPresented: $showRemoteWipeConfirmation)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAccessRequests) {
            AccessRequestsModal(isPresented: $showAccessRequests, requests: $requests)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showYouTubeSettings) {
            YouTubeSettingsModal(isPresented: $showYouTubeSettings)
                .environmentObject(localizationManager)
        }
        .id("additional_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            // Загружаем статистику при открытии модала
            loadAdditionalStatistics()
        }
        .onChange(of: isHomeworkModeEnabled) { newValue in
            VisualLogger.shared.log(
                "🔄 homework_mode_enabled = \(newValue)",
                level: .info,
                category: "PARENTAL.UI"
            )
            print("✅ Homework mode: \(newValue ? "ON" : "OFF")")
        }
        .withVisualLogger()
    }
    
    // Загрузка статистики дополнительных настроек из UserDefaults
    private func loadAdditionalStatistics() {
        let defaultDeviceStatus = localizationManager.localized("remote_lock_status_online")
        deviceStatus = defaultDeviceStatus
        
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            accessRequestsCount = stats["accessRequestsCount"] as? Int ?? 2
            deviceName = stats["deviceName"] as? String ?? "iPhone 12 (Alexey)"
            deviceStatus = stats["deviceStatus"] as? String ?? defaultDeviceStatus
            deviceBattery = stats["deviceBattery"] as? String ?? "67%"
        }
        
        // Загружаем запросы доступа (по умолчанию примерные)
        if requests.isEmpty {
            requests = [
                AccessRequest(app: "Instagram", time: String(format: localizationManager.localized("family_min_ago_format"), 10), reason: localizationManager.localized("family_request_check_messages"), limit: "30 \(localizationManager.localized("family_limit_minutes"))/\(localizationManager.localized("family_per_day")) (\(localizationManager.localized("family_limit_used")))"),
                AccessRequest(app: "YouTube", time: String(format: localizationManager.localized("family_min_ago_format"), 5), reason: localizationManager.localized("family_request_review_lesson"), limit: "45 \(localizationManager.localized("family_limit_minutes"))/\(localizationManager.localized("family_per_day")) (\(String(format: localizationManager.localized("family_limit_remaining"), 12)))")
            ]
        }
    }
}

// MARK: - Access Request Model

struct AccessRequest: Identifiable {
    let id = UUID()
    let app: String
    let time: String
    let reason: String
    let limit: String
}

// MARK: - Family Modal Base View

struct FamilyModalBaseView<Content: View>: View {
    let title: String
    @Binding var isPresented: Bool
    let content: Content
    
    init(title: String, isPresented: Binding<Bool>, @ViewBuilder content: () -> Content) {
        self.title = title
        self._isPresented = isPresented
        self.content = content()
    }
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Text(title)
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    Spacer()
                    
                    Button(action: {
                        HapticFeedback.impact(.light)
                        isPresented = false
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 28))
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: 0)
                        .fill(Color.backgroundMedium.opacity(0.5))
                )
                
                // Content
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        content
                    }
                    .padding(Spacing.m)
                }
            }
        }
    }
}

// MARK: - Supporting Views

struct ControlCard: View {
    let icon: String
    let title: String
    let info: String
    let status: ControlStatus
    let action: () -> Void
    
    enum ControlStatus {
        case green, red
    }
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                HStack(spacing: 4) {
                    Text(icon)
                        .font(.system(size: 16))
                    
                    Text(title)
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                }
                
                Text(info)
                    .font(.system(size: 11))
                    .foregroundColor(.white.opacity(0.9))
                
                Spacer()
                
                Text(status == .green ? "🟢" : "🔴")
                    .font(.system(size: 28))
                    .animation(.easeInOut(duration: 2).repeatForever(autoreverses: true), value: status)
            }
            .frame(height: 90)
            .frame(maxWidth: .infinity)
            .padding(8)
            .background(Color(red: 0.96, green: 0.62, blue: 0.04).opacity(0.1))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color(red: 0.96, green: 0.62, blue: 0.04), lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: 10))
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Modals

struct AddMemberModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: 20) {
            Text(localizationManager.localized("family_add_member_title"))
                .font(.title2)
                .foregroundColor(.white)
            
            Text(localizationManager.localized("family_scan_qr_code"))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
            
            Button(localizationManager.localized("family_close")) {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

struct RewardsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: 20) {
            Text(localizationManager.localized("family_rewards_modal_title"))
                .font(.title2)
                .foregroundColor(Color(red: 0.75, green: 0.52, blue: 0.99))
            
            Text(localizationManager.localized("family_unicorn_balance_format", 245))
                .foregroundColor(.gray)
            
            Button(localizationManager.localized("family_close")) {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

// MARK: - Detailed Modals

// MARK: 1. Подтверждения (приоритетные)

struct RemoteLockConfirmationModal: View {
    @Binding var isPresented: Bool
    let deviceName: String
    let deviceStatus: String
    let deviceBattery: String
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var showSuccess = false
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("remote_lock_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Предупреждение
                VStack(spacing: Spacing.m) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 64))
                        .foregroundColor(.warningOrange)
                    
                    Text(localizationManager.localized("remote_lock_warning"))
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    Text(localizationManager.localized("remote_lock_desc"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(Spacing.l)
                .background(Color.warningOrange.opacity(0.1))
                .cornerRadius(CornerRadius.large)
                
                // Информация об устройстве
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("remote_lock_device_info"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    HStack {
                        Text(localizationManager.localized("remote_lock_device"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text(deviceName)
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                    }
                    
                    HStack {
                        Text(localizationManager.localized("remote_lock_status"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text(deviceStatus)
                            .font(.bodyBold)
                            .foregroundColor(.successGreen)
                    }
                    
                    HStack {
                        Text(localizationManager.localized("remote_lock_battery"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text(deviceBattery)
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Действия
                if showSuccess {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.successGreen)
                        
                        Text(localizationManager.localized("remote_lock_success"))
                            .font(.bodyBold)
                            .foregroundColor(.successGreen)
                    }
                    .padding(Spacing.l)
                } else {
                    VStack(spacing: Spacing.m) {
                        Button(action: {
                            HapticFeedback.impact(.heavy)
                            withAnimation {
                                showSuccess = true
                            }
                            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                                isPresented = false
                            }
                        }) {
                            Text(localizationManager.localized("remote_lock_confirm"))
                                .font(.bodyBold)
                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.dangerRed)
                                .cornerRadius(CornerRadius.medium)
                        }
                        
                        Button(action: {
                            HapticFeedback.impact(.light)
                            isPresented = false
                        }) {
                            Text(localizationManager.localized("edit_profile_cancel"))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .cornerRadius(CornerRadius.medium)
                        }
                    }
                }
            }
        }
        .id("remote_lock_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

struct RemoteWipeConfirmationModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var showSuccess = false
    @State private var confirmationText = ""
    @State private var isConfirmationValid = false
    
    private var confirmTextRequired: String {
        localizationManager.localized("data_deletion_confirm_keyword").uppercased()
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("data_deletion_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Критическое предупреждение
                VStack(spacing: Spacing.m) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.dangerRed)
                    
                    Text(localizationManager.localized("data_deletion_danger"))
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.dangerRed)
                    
                    Text(localizationManager.localized("data_deletion_desc"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(Spacing.l)
                .background(Color.dangerRed.opacity(0.15))
                .cornerRadius(CornerRadius.large)
                
                // Подтверждение
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("data_deletion_confirm"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    
                    TextField(localizationManager.localized("data_deletion_placeholder"), text: $confirmationText)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.5))
                        .cornerRadius(CornerRadius.medium)
                        .autocapitalization(.allCharacters)
                        .onChange(of: confirmationText) { newValue in
                            isConfirmationValid = newValue.uppercased() == confirmTextRequired
                        }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Действия
                if showSuccess {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "trash.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.dangerRed)
                        
                        Text(localizationManager.localized("data_deletion_deleting"))
                            .font(.bodyBold)
                            .foregroundColor(.dangerRed)
                    }
                    .padding(Spacing.l)
                } else {
                    VStack(spacing: Spacing.m) {
                        Button(action: {
                            HapticFeedback.impact(.heavy)
                            withAnimation {
                                showSuccess = true
                            }
                            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                isPresented = false
            }
                        }) {
                            Text(localizationManager.localized("data_deletion_button"))
                                .font(.bodyBold)
            .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(isConfirmationValid ? Color.dangerRed : Color.dangerRed.opacity(0.5))
                                .cornerRadius(CornerRadius.medium)
                        }
                        .disabled(!isConfirmationValid)
                        
                        Button(action: {
                            HapticFeedback.impact(.light)
                            isPresented = false
                        }) {
                            Text(localizationManager.localized("edit_profile_cancel"))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .cornerRadius(CornerRadius.medium)
                        }
                    }
                }
            }
        }
        .id("data_deletion_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

// MARK: 2. Запросы доступа

struct AccessRequestsModal: View {
    @Binding var isPresented: Bool
    @Binding var requests: [AccessRequest]
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Manager для обработки запросов
    @ObservedObject private var manager = ParentalControlManager.shared
    @State private var processingRequestId: String?
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_access_requests_modal_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                if requests.isEmpty {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.successGreen)
                        
                        Text(localizationManager.localized("family_no_new_requests"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Text(localizationManager.localized("family_all_requests_processed"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                    .padding(Spacing.xl)
                } else {
                    ForEach(requests) { request in
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            HStack {
                                Text(request.app)
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Spacer()
                                
                                Text(request.time)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Text(request.reason)
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .lineLimit(2)
                            
                            Text(request.limit)
                                .font(.caption)
                                .foregroundColor(.warningOrange)
                            
                            Divider()
                            
                            HStack(spacing: Spacing.m) {
                                Button(action: {
                                    handleAccessRequest(requestId: request.id.uuidString, action: "accept")
                                }) {
                                    Text(localizationManager.localized("family_request_approve"))
                                        .font(.bodyBold)
                                        .foregroundColor(.white)
                                        .frame(maxWidth: .infinity)
                                        .padding(Spacing.s)
                                        .background(processingRequestId == request.id.uuidString ? Color.gray : Color.successGreen)
                                        .cornerRadius(CornerRadius.small)
                                }
                                .disabled(processingRequestId == request.id.uuidString || manager.isLoading)
                                
                                Button(action: {
                                    handleAccessRequest(requestId: request.id.uuidString, action: "reject")
                                }) {
                                    Text(localizationManager.localized("family_request_reject"))
                                        .font(.bodyBold)
                                        .foregroundColor(.white)
                                        .frame(maxWidth: .infinity)
                                        .padding(Spacing.s)
                                        .background(processingRequestId == request.id.uuidString ? Color.gray : Color.dangerRed)
                                        .cornerRadius(CornerRadius.small)
                                }
                                .disabled(processingRequestId == request.id.uuidString || manager.isLoading)
                            }
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
            }
        }
        .onAppear {
            // Загружаем запросы из API при открытии
            loadAccessRequests()
        }
    }
    
    // Загрузка запросов доступа из API
    private func loadAccessRequests() {
        manager.getAccessRequests { result in
            switch result {
            case .success(let apiRequests):
                // Конвертируем API ответы в локальные модели
                requests = apiRequests.map { apiRequest in
                    AccessRequest(
                        app: apiRequest.app,
                        time: apiRequest.time,
                        reason: apiRequest.reason,
                        limit: apiRequest.limit
                    )
                }
                print("✅ Loaded \(requests.count) access requests")
            case .failure(let error):
                print("❌ Failed to load access requests: \(error.localizedDescription)")
                // Оставляем существующие mock-данные при ошибке
            }
        }
    }
    
    // Обработка запроса доступа
    private func handleAccessRequest(requestId: String, action: String) {
        HapticFeedback.impact(.medium)
        processingRequestId = requestId
        
        manager.handleAccessRequest(requestId: requestId, action: action) { (success: Bool, error: String?) in
            DispatchQueue.main.async {
                processingRequestId = nil
                
                if success {
                    // Удаляем запрос из списка после успешной обработки
                    withAnimation {
                        requests.removeAll { $0.id.uuidString == requestId }
                    }
                    print("✅ Request \(requestId) \(action == "accept" ? "approved" : "rejected")")
                } else {
                    print("❌ Failed to process request: \(error ?? "Unknown error")")
                }
            }
        }
    }
}

// MARK: 3. История браузера

struct BrowserHistoryDetailModal: View {
    @Binding var isPresented: Bool
    var childId: String? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var browserHistory: [BrowserHistoryItem] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_monitoring_browser_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика
                HStack(spacing: Spacing.m) {
                    VStack(alignment: .leading) {
                        Text(localizationManager.localized("family_monitoring_browser_total_sites"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(browserHistory.count)")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text(localizationManager.localized("family_monitoring_browser_total_time"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text(formatDuration(totalBrowserDuration.hours, minutes: totalBrowserDuration.minutes))
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Топ-5 сайтов
                Text(localizationManager.localized("family_monitoring_browser_top_week"))
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                ForEach(Array(browserHistory.enumerated()), id: \.element.id) { index, item in
                    HStack(spacing: Spacing.m) {
                        // Номер
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.site)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text("\(item.visits) \(localizationManager.localized("family_monitoring_browser_visits"))")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text(formatDuration(item.hours, minutes: item.minutes))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Text(localizationManager.localized(item.categoryKey))
                                .font(.captionSmall)
                                .foregroundColor(item.color)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(item.color.opacity(0.2))
                                .cornerRadius(8)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("family_monitoring_browser_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadBrowserHistoryFromServer()
        }
    }
    
    private func browserCategoryKey(for apiCategory: String) -> String {
        switch apiCategory.lowercased() {
        case "video": return "family_monitoring_browser_category_video"
        case "social": return "family_monitoring_browser_category_social"
        case "search": return "family_monitoring_browser_category_search"
        default: return "family_monitoring_browser_category_search"
        }
    }
    
    private func browserCategoryColor(for apiCategory: String) -> Color {
        switch apiCategory.lowercased() {
        case "video": return .red
        case "social": return .purple
        case "search": return .blue
        default: return .blue
        }
    }
    
    private func loadBrowserHistoryFromServer() {
        ParentalControlManager.shared.getMonitoringDetail(childId: childId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let detail):
                    browserHistory = detail.browserHistory.map { row in
                        BrowserHistoryItem(
                            site: row.site,
                            visits: row.visits,
                            hours: row.hours,
                            minutes: row.minutes,
                            categoryKey: browserCategoryKey(for: row.category),
                            color: browserCategoryColor(for: row.category)
                        )
                    }
                case .failure:
                    browserHistory = []
                }
            }
        }
    }
    
    private var totalBrowserDuration: (hours: Int, minutes: Int) {
        let totalMinutes = browserHistory.reduce(0) { partialResult, item in
            partialResult + (item.hours * 60) + item.minutes
        }
        return (hours: totalMinutes / 60, minutes: totalMinutes % 60)
    }
    
    private func formatDuration(_ hours: Int, minutes: Int) -> String {
        let hourUnit = localizationManager.localized("analytics_hour")
        let minuteUnit = localizationManager.localized("analytics_min")
        
        if hours == 0 {
            return "\(minutes) \(minuteUnit)"
        }
        
        if minutes == 0 {
            return "\(hours) \(hourUnit)"
        }
        
        return "\(hours) \(hourUnit) \(minutes) \(minuteUnit)"
    }
}

struct BrowserHistoryItem: Identifiable {
    let id: UUID
    let site: String
    let visits: Int
    let hours: Int
    let minutes: Int
    let categoryKey: String
    let color: Color
    
    init(id: UUID = UUID(), site: String, visits: Int, hours: Int, minutes: Int, categoryKey: String, color: Color) {
        self.id = id
        self.site = site
        self.visits = visits
        self.hours = hours
        self.minutes = minutes
        self.categoryKey = categoryKey
        self.color = color
    }
}

// MARK: 4. История приложений

struct AppHistoryDetailModal: View {
    @Binding var isPresented: Bool
    var childId: String? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var appHistory: [AppHistoryItem] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("app_history_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика
                HStack(spacing: Spacing.m) {
                    VStack(alignment: .leading) {
                        Text(localizationManager.localized("app_history_total_apps"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(appHistory.count)")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text(localizationManager.localized("app_history_limit_exceeded"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(appHistory.filter { $0.exceeded }.count)")
                            .font(.h3)
                            .foregroundColor(.dangerRed)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Топ-5 приложений
                Text(localizationManager.localized("app_history_top_5_week"))
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                ForEach(Array(appHistory.enumerated()), id: \.element.id) { index, item in
                    HStack(spacing: Spacing.m) {
                        // Номер
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.app)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text(formatDurationFromMinutes(item.usageMinutes))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text(formatLimit(item.limitMinutes))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            if item.exceeded, let exceededByMinutes = item.exceededByMinutes {
                                HStack {
                                    Image(systemName: "exclamationmark.triangle.fill")
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                    
                                    Text("\(localizationManager.localized("app_history_exceeded_by")) \(formatDurationFromMinutes(exceededByMinutes))")
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.dangerRed.opacity(0.2))
                                .cornerRadius(8)
                            } else {
                                HStack {
                                    Image(systemName: "checkmark.circle.fill")
                                        .font(.captionSmall)
                                        .foregroundColor(.successGreen)
                                    
                                    Text(localizationManager.localized("app_history_within_limit"))
                                        .font(.captionSmall)
                                        .foregroundColor(.successGreen)
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.successGreen.opacity(0.2))
                                .cornerRadius(8)
                            }
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(item.exceeded ? Color.dangerRed.opacity(0.1) : Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(item.exceeded ? Color.dangerRed.opacity(0.5) : Color.clear, lineWidth: 2)
                    )
                }
            }
        }
        .id("app_history_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadAppHistoryFromServer()
        }
    }
    
    private func loadAppHistoryFromServer() {
        ParentalControlManager.shared.getMonitoringDetail(childId: childId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let detail):
                    appHistory = detail.appHistory.map { row in
                        let exceededBy: Int? = {
                            guard row.limitMinutes > 0, row.usageMinutes > row.limitMinutes else { return nil }
                            return row.usageMinutes - row.limitMinutes
                        }()
                        return AppHistoryItem(
                            app: row.name,
                            usageMinutes: row.usageMinutes,
                            limitMinutes: row.limitMinutes,
                            exceeded: row.exceeded,
                            exceededByMinutes: exceededBy,
                            color: appHistoryColor(for: row.name)
                        )
                    }
                case .failure:
                    appHistory = []
                }
            }
        }
    }
    
    private func appHistoryColor(for name: String) -> Color {
        let lower = name.lowercased()
        if lower.contains("instagram") { return .purple }
        if lower.contains("tiktok") { return .black }
        if lower.contains("youtube") { return .red }
        if lower.contains("whatsapp") { return .green }
        if lower.contains("vk") { return .blue }
        return .blue
    }
    
    private func formatDurationFromMinutes(_ minutes: Int) -> String {
        let hours = minutes / 60
        let remainingMinutes = minutes % 60
        return formatDuration(hours: hours, minutes: remainingMinutes)
    }
    
    private func formatDuration(hours: Int, minutes: Int) -> String {
        let hourUnit = localizationManager.localized("analytics_hour")
        let minuteUnit = localizationManager.localized("analytics_min")
        
        if hours == 0 {
            return "\(minutes) \(minuteUnit)"
        }
        
        if minutes == 0 {
            return "\(hours) \(hourUnit)"
        }
        
        return "\(hours) \(hourUnit) \(minutes) \(minuteUnit)"
    }
    
    private func formatLimit(_ minutes: Int) -> String {
        localizationManager.localized("app_history_limit_format", minutes)
    }
}

struct AppHistoryItem: Identifiable {
    let id: UUID
    let app: String
    let usageMinutes: Int
    let limitMinutes: Int
    let exceeded: Bool
    let exceededByMinutes: Int?
    let color: Color
    
    init(id: UUID = UUID(), app: String, usageMinutes: Int, limitMinutes: Int, exceeded: Bool, exceededByMinutes: Int?, color: Color) {
        self.id = id
        self.app = app
        self.usageMinutes = usageMinutes
        self.limitMinutes = limitMinutes
        self.exceeded = exceeded
        self.exceededByMinutes = exceededByMinutes
        self.color = color
    }
}

// MARK: 5. Контакты

struct ContactsDetailModal: View {
    @Binding var isPresented: Bool
    var childId: String? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var contacts: [ContactItem] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_contacts_view"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика
                HStack(spacing: Spacing.m) {
                    VStack(alignment: .leading) {
                        Text(localizationManager.localized("family_contacts_total"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(contacts.count)")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text(localizationManager.localized("family_messages_title"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(contacts.reduce(0) { $0 + $1.messages })")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Топ-5 контактов
                if contacts.isEmpty {
                    EmptyStateView(
                        icon: "👥",
                        title: localizationManager.localized("family_contacts_empty_title"),
                        description: localizationManager.localized("family_contacts_empty_description"),
                        actionTitle: nil,
                        action: nil
                    )
                    .padding()
                } else {
                    Text(localizationManager.localized("family_top_5_contacts"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    ForEach(Array(contacts.enumerated()), id: \.element.id) { index, contact in
                    HStack(spacing: Spacing.m) {
                        // Номер
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(contact.name)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                    Text(localizationManager.localized("family_messages_format", contact.messages))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                    Text(localizationManager.localized("family_calls_format", contact.calls))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                                Text("\(localizationManager.localized("family_last_contact_prefix")) \(contact.lastContact)")
                                .font(.captionSmall)
                                .foregroundColor(contact.color)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(contact.color.opacity(0.2))
                                .cornerRadius(8)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    }
                }
            }
        }
        .onAppear {
            loadContacts()
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            loadContacts() // Синхронизируем при изменении данных
        }
    }
    
    private func loadContacts() {
        ParentalControlManager.shared.getMonitoringDetail(childId: childId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let detail):
                    if !detail.contacts.isEmpty {
                        contacts = detail.contacts.map { row in
                            let last = row.lastContact.trimmingCharacters(in: .whitespacesAndNewlines)
                            return ContactItem(
                                name: row.name,
                                messages: row.messages,
                                calls: row.calls,
                                lastContact: last.isEmpty ? localizationManager.localized("family_last_contact_recently") : last,
                                color: .successGreen
                            )
                        }
                        return
                    }
                case .failure:
                    break
                }
                loadContactsFromLocalCacheOnly()
            }
        }
    }
    
    private func loadContactsFromLocalCacheOnly() {
        if let savedData = UserDefaults.standard.data(forKey: "child_family_contacts_list"),
           let decoded = try? JSONDecoder().decode([ChildFamilyContact].self, from: savedData),
           !decoded.isEmpty {
            contacts = decoded.prefix(5).map { contact in
                ContactItem(
                    name: contact.name,
                    messages: 0,
                    calls: 0,
                    lastContact: localizationManager.localized("family_last_contact_recently"),
                    color: .successGreen
                )
            }
            return
        }
        
        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData),
           !decoded.isEmpty {
            contacts = decoded.prefix(5).map { member in
                ContactItem(
                    name: member.name,
                    messages: 0,
                    calls: 0,
                    lastContact: localizationManager.localized("family_last_contact_recently"),
                    color: .successGreen
                )
            }
            return
        }
        
        contacts = []
    }
}

struct ContactItem: Identifiable {
    let id: UUID
    let name: String
    let messages: Int
    let calls: Int
    let lastContact: String
    let color: Color
    
    init(id: UUID = UUID(), name: String, messages: Int, calls: Int, lastContact: String, color: Color) {
        self.id = id
        self.name = name
        self.messages = messages
        self.calls = calls
        self.lastContact = lastContact
        self.color = color
    }
}

// MARK: 6. Остальные настройки и просмотры

// MARK: Настройки времени

struct ScreenTimeSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Сохранение настроек в UserDefaults
    @AppStorage("screen_time_weekday_limit") private var weekdayLimit: Double = 120 // минуты
    @AppStorage("screen_time_weekend_limit") private var weekendLimit: Double = 180 // минуты
    @AppStorage("screen_time_is_weekday_selected") private var isWeekdaySelected = true
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("screen_time_settings_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Выбор режима
                HStack(spacing: Spacing.m) {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = true
                        VisualLogger.shared.log(
                            "🔄 screen_time_mode = weekdays",
                            level: .info,
                            category: "ADVANCED.UI"
                        )
                    }) {
                        Text(localizationManager.localized("screen_time_weekdays"))
                            .font(.bodyBold)
                            .foregroundColor(isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                    
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = false
                        VisualLogger.shared.log(
                            "🔄 screen_time_mode = weekends",
                            level: .info,
                            category: "ADVANCED.UI"
                        )
                    }) {
                        Text(localizationManager.localized("screen_time_weekends"))
                            .font(.bodyBold)
                            .foregroundColor(!isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(!isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                }
                
                // Ползунок лимита
                VStack(alignment: .leading, spacing: Spacing.m) {
                    HStack {
                        Text(localizationManager.localized("screen_time_limit"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Text("\(Int(isWeekdaySelected ? weekdayLimit : weekendLimit)) \(localizationManager.localized("screen_time_limit_min"))")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Slider(value: isWeekdaySelected ? $weekdayLimit : $weekendLimit, in: 30...480, step: 15) {
                        Text(localizationManager.localized("screen_time_limit"))
                    }
                    .tint(.secondaryGold)
                    
                    HStack {
                        Text("30 \(localizationManager.localized("screen_time_limit_min"))")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Spacer()
                        
                        Text("8 \(localizationManager.localized("analytics_hour"))")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Рекомендации
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("💡 \(localizationManager.localized("screen_time_recommendations"))")
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    VStack(alignment: .leading, spacing: 6) {
                        Text(localizationManager.localized("screen_time_children_6_10"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        
                        Text(localizationManager.localized("screen_time_teens"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(Color.secondaryGold.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    print("✅ Screen time saved: weekdays \(Int(weekdayLimit)) min, weekends \(Int(weekendLimit)) min")
                isPresented = false
                }) {
                    Text(localizationManager.localized("screen_time_save"))
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("screen_time_settings_lang_\(localizationManager.currentLanguage.rawValue)")
        .onChange(of: weekdayLimit) { newValue in
            VisualLogger.shared.log(
                "🎚️ screen_time_weekday_limit = \(Int(newValue)) min",
                level: .info,
                category: "ADVANCED.UI"
            )
            print("✅ Weekday limit: \(Int(newValue)) min")
        }
        .onChange(of: weekendLimit) { newValue in
            VisualLogger.shared.log(
                "🎚️ screen_time_weekend_limit = \(Int(newValue)) min",
                level: .info,
                category: "ADVANCED.UI"
            )
            print("✅ Weekend limit: \(Int(newValue)) min")
        }
        .withVisualLogger()
    }
}

struct ScheduleSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    
    // ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
    private static let timeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: "ru_RU")  // Статический locale вместо Locale.current
        return formatter
    }()
    
    // Сохранение дат через TimeInterval в UserDefaults
    @AppStorage("schedule_weekday_start") private var weekdayStartInterval: Double = 0
    @AppStorage("schedule_weekday_end") private var weekdayEndInterval: Double = 0
    @AppStorage("schedule_weekend_start") private var weekendStartInterval: Double = 0
    @AppStorage("schedule_weekend_end") private var weekendEndInterval: Double = 0
    @AppStorage("schedule_is_weekday_selected") private var isWeekdaySelected = true
    
    // Вычисляемые свойства для работы с Date
    private var weekdayStart: Binding<Date> {
        Binding(
            get: {
                weekdayStartInterval == 0 ? Date() : Date(timeIntervalSince1970: weekdayStartInterval)
            },
            set: { weekdayStartInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var weekdayEnd: Binding<Date> {
        Binding(
            get: {
                weekdayEndInterval == 0 ? Date() : Date(timeIntervalSince1970: weekdayEndInterval)
            },
            set: { weekdayEndInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var weekendStart: Binding<Date> {
        Binding(
            get: {
                weekendStartInterval == 0 ? Date() : Date(timeIntervalSince1970: weekendStartInterval)
            },
            set: { weekendStartInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var weekendEnd: Binding<Date> {
        Binding(
            get: {
                weekendEndInterval == 0 ? Date() : Date(timeIntervalSince1970: weekendEndInterval)
            },
            set: { weekendEndInterval = $0.timeIntervalSince1970 }
        )
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("schedule_settings_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Выбор режима
                HStack(spacing: Spacing.m) {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = true
                    }) {
                        Text(localizationManager.localized("screen_time_weekdays"))
                            .font(.bodyBold)
                            .foregroundColor(isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                    
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = false
                    }) {
                        Text(localizationManager.localized("screen_time_weekends"))
                            .font(.bodyBold)
                            .foregroundColor(!isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(!isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                }
                
                // Время начала и окончания
                VStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("schedule_access_from"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: isWeekdaySelected ? weekdayStart : weekendStart, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("schedule_access_to"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: isWeekdaySelected ? weekdayEnd : weekendEnd, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    // ✅ BUILD 98: Используем статический DateFormatter для предотвращения рекурсии
                    print("✅ Schedule saved: weekdays \(Self.timeFormatter.string(from: weekdayStart.wrappedValue)) - \(Self.timeFormatter.string(from: weekdayEnd.wrappedValue)), weekends \(Self.timeFormatter.string(from: weekendStart.wrappedValue)) - \(Self.timeFormatter.string(from: weekendEnd.wrappedValue))")
                    Task {
                        await syncScheduleSettingsToServer()
                        await MainActor.run { isPresented = false }
                    }
                }) {
                    Text(localizationManager.localized("schedule_save"))
                        .font(.bodyBold)
            .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("schedule_settings_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            // Инициализация дат по умолчанию если они не сохранены
            if weekdayStartInterval == 0 {
                weekdayStartInterval = Date().timeIntervalSince1970
            }
            if weekdayEndInterval == 0 {
                weekdayEndInterval = Date().timeIntervalSince1970
            }
            if weekendStartInterval == 0 {
                weekendStartInterval = Date().timeIntervalSince1970
            }
            if weekendEndInterval == 0 {
                weekendEndInterval = Date().timeIntervalSince1970
            }
        }
        .withVisualLogger()
    }

    @MainActor
    private func syncScheduleSettingsToServer() async {
        let payload: [String: AnyCodable] = [
            "scheduleWeekdayStart": AnyCodable(weekdayStartInterval),
            "scheduleWeekdayEnd": AnyCodable(weekdayEndInterval),
            "scheduleWeekendStart": AnyCodable(weekendStartInterval),
            "scheduleWeekendEnd": AnyCodable(weekendEndInterval),
            "scheduleIsWeekdaySelected": AnyCodable(isWeekdaySelected)
        ]
        VisualLogger.shared.log(
            "🔵 ADVANCED.API schedule POST start",
            level: .info,
            category: "ADVANCED.API"
        )
        do {
            let existing = try? await configurationService.getConfiguration(for: "parental_control_bot")
            var merged = existing?.additionalSettings ?? [:]
            payload.forEach { merged[$0.key] = $0.value }
            let config = ComponentConfiguration(isEnabled: true, priority: .normal, additionalSettings: merged)
            try await configurationService.saveConfiguration(componentId: "parental_control_bot", configuration: config)
            VisualLogger.shared.log("✅ ADVANCED.API schedule POST ok", level: .info, category: "ADVANCED.API")
        } catch {
            VisualLogger.shared.log("❌ ADVANCED.API schedule POST failed: \(error.localizedDescription)", level: .error, category: "ADVANCED.API")
        }
    }
}

struct SleepTimeSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    
    // ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
    private static let timeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: "ru_RU")  // Статический locale вместо Locale.current
        return formatter
    }()
    
    // Сохранение дат через TimeInterval в UserDefaults
    @AppStorage("sleep_bedtime_start") private var bedtimeStartInterval: Double = 0
    @AppStorage("sleep_bedtime_end") private var bedtimeEndInterval: Double = 0
    @AppStorage("sleep_emergency_calls_enabled") private var isEmergencyCallsEnabled = true
    
    // Вычисляемые свойства для работы с Date
    private var bedtimeStart: Binding<Date> {
        Binding(
            get: {
                bedtimeStartInterval == 0 ? Date() : Date(timeIntervalSince1970: bedtimeStartInterval)
            },
            set: { bedtimeStartInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var bedtimeEnd: Binding<Date> {
        Binding(
            get: {
                bedtimeEndInterval == 0 ? Date() : Date(timeIntervalSince1970: bedtimeEndInterval)
            },
            set: { bedtimeEndInterval = $0.timeIntervalSince1970 }
        )
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("bedtime_settings_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Время сна
                VStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("bedtime_block_from"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: bedtimeStart, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("bedtime_block_to"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: bedtimeEnd, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Экстренные вызовы
                FamilyContentBlockItem(
                    icon: "🆘",
                    title: localizationManager.localized("bedtime_emergency_calls"),
                    description: localizationManager.localized("bedtime_emergency_calls_desc"),
                    isEnabled: $isEmergencyCallsEnabled
                )
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    // ✅ BUILD 98: Используем статический DateFormatter для предотвращения рекурсии
                    print("✅ Bedtime saved: \(Self.timeFormatter.string(from: bedtimeStart.wrappedValue)) - \(Self.timeFormatter.string(from: bedtimeEnd.wrappedValue)), emergency calls \(isEmergencyCallsEnabled ? "ON" : "OFF")")
                    Task {
                        await syncSleepSettingsToServer()
                        await MainActor.run { isPresented = false }
                    }
                }) {
                    Text(localizationManager.localized("bedtime_save"))
                        .font(.bodyBold)
                .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("bedtime_settings_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            // Инициализация дат по умолчанию если они не сохранены
            if bedtimeStartInterval == 0 {
                bedtimeStartInterval = Date().timeIntervalSince1970
            }
            if bedtimeEndInterval == 0 {
                bedtimeEndInterval = Date().timeIntervalSince1970
            }
        }
        .onChange(of: isEmergencyCallsEnabled) { newValue in
            VisualLogger.shared.log(
                "🔄 sleep_emergency_calls_enabled = \(newValue)",
                level: .info,
                category: "ADVANCED.UI"
            )
            print("✅ Emergency calls: \(newValue ? "ON" : "OFF")")
        }
        .withVisualLogger()
    }

    @MainActor
    private func syncSleepSettingsToServer() async {
        let payload: [String: AnyCodable] = [
            "sleepBedtimeStart": AnyCodable(bedtimeStartInterval),
            "sleepBedtimeEnd": AnyCodable(bedtimeEndInterval),
            "sleepEmergencyCallsEnabled": AnyCodable(isEmergencyCallsEnabled)
        ]
        VisualLogger.shared.log(
            "🔵 ADVANCED.API sleep POST start",
            level: .info,
            category: "ADVANCED.API"
        )
        do {
            let existing = try? await configurationService.getConfiguration(for: "parental_control_bot")
            var merged = existing?.additionalSettings ?? [:]
            payload.forEach { merged[$0.key] = $0.value }
            let config = ComponentConfiguration(isEnabled: true, priority: .normal, additionalSettings: merged)
            try await configurationService.saveConfiguration(componentId: "parental_control_bot", configuration: config)
            VisualLogger.shared.log("✅ ADVANCED.API sleep POST ok", level: .info, category: "ADVANCED.API")
        } catch {
            VisualLogger.shared.log("❌ ADVANCED.API sleep POST failed: \(error.localizedDescription)", level: .error, category: "ADVANCED.API")
        }
    }
}

struct AppLimitsSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    
    // Сохранение лимитов приложений в UserDefaults
    private let limitsKey = "app_limits_settings"
    
    // ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
    private static let timeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: "ru_RU")  // Статический locale вместо Locale.current
        return formatter
    }()
    
    @State private var appLimits: [AppLimitItem] = []
    
    // Загрузка лимитов из UserDefaults
    private func loadAppLimits() {
        // ✅ ИСПРАВЛЕНО: Сначала загружаем из общего массива, затем проверяем индивидуальные ключи
        var loadedLimits: [AppLimitItem] = []
        
        if let data = UserDefaults.standard.data(forKey: limitsKey),
           let decoded = try? JSONDecoder().decode([AppLimitItemCodable].self, from: data) {
            loadedLimits = decoded.map { AppLimitItem(app: $0.app, limit: $0.limit, color: Color(hex: $0.colorHex)) }
        } else {
            // Значения по умолчанию
            loadedLimits = [
                AppLimitItem(app: "Instagram", limit: 30.0, color: .purple),
                AppLimitItem(app: "TikTok", limit: 20.0, color: .black),
                AppLimitItem(app: "WhatsApp", limit: 60.0, color: .green),
                AppLimitItem(app: "Telegram", limit: 60.0, color: .blue),
                AppLimitItem(app: "YouTube", limit: 45.0, color: .red),
                AppLimitItem(app: "VK", limit: 30.0, color: .blue),
                AppLimitItem(app: "Odnoklassniki", limit: 20.0, color: .orange),
                AppLimitItem(app: "Discord", limit: 30.0, color: .indigo),
                AppLimitItem(app: "Games", limit: 60.0, color: .pink)
            ]
        }
        
        // ✅ BUILD 96: Асинхронная загрузка для предотвращения рекурсии
        // Проверяем индивидуальные ключи для каждого приложения (приоритет выше)
        // Устанавливаем начальные значения сразу
        appLimits = loadedLimits
        
        // Затем обновляем асинхронно
        Task { @MainActor in
            var updatedLimits = appLimits
            for index in updatedLimits.indices {
                let app = updatedLimits[index].app
                let appKey = "app_\(app.lowercased().replacingOccurrences(of: " ", with: "_"))_time_limit"
                if UserDefaults.standard.object(forKey: appKey) != nil {
                    let savedLimit = UserDefaults.standard.double(forKey: appKey)
                    if savedLimit > 0 {
                        updatedLimits[index].limit = savedLimit
                    }
                }
            }
            // Обновляем appLimits на main thread после загрузки
            appLimits = updatedLimits
        }
    }
    
    // Сохранение лимитов в UserDefaults
    private func saveAppLimits() {
        let codable = appLimits.map { AppLimitItemCodable(app: $0.app, limit: $0.limit, colorHex: "") }
        if let encoded = try? JSONEncoder().encode(codable) {
            UserDefaults.standard.set(encoded, forKey: limitsKey)
        }
    }
    
    // ✅ ИСПРАВЛЕНО: Автоматическое сохранение лимита для конкретного приложения
    private func saveAppLimitForApp(app: String, limit: Double) {
        // Сохраняем в UserDefaults с динамическим ключом для каждого приложения
        let appKey = "app_\(app.lowercased().replacingOccurrences(of: " ", with: "_"))_time_limit"
        UserDefaults.standard.set(limit, forKey: appKey)
        
        // Также обновляем общий массив и сохраняем его
        if let index = appLimits.firstIndex(where: { $0.app == app }) {
            appLimits[index].limit = limit
        }
        saveAppLimits()
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("app_limits_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach($appLimits) { $limit in
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(limit.app)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Text("\(Int(limit.limit)) \(localizationManager.localized("app_limits_min_per_day"))")
                                .font(.bodyBold)
                                .foregroundColor(.secondaryGold)
                        }
                        
                        // ✅ ИСПРАВЛЕНО: Используем Binding с автоматическим сохранением в UserDefaults
                        Slider(value: Binding(
                            get: { limit.limit },
                            set: { newValue in
                                limit.limit = newValue
                                // Автоматическое сохранение при изменении слайдера
                                saveAppLimitForApp(app: limit.app, limit: newValue)
                                VisualLogger.shared.log(
                                    "🎚️ app_limit_\(limit.app) = \(Int(newValue)) min/day",
                                    level: .info,
                                    category: "ADVANCED.UI"
                                )
                            }
                        ), in: 5...120, step: 5) {
                            Text(limit.app)
                        }
                        .tint(limit.color)
                        
                        HStack {
                            Text(localizationManager.localized("app_limits_5_min"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            
                            Spacer()
                            
                            Text(localizationManager.localized("app_limits_2_hours"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    saveAppLimits()
                    print("✅ App limits saved: \(appLimits.count) apps")
                    Task {
                        await syncAppLimitsToServer()
                        await MainActor.run { isPresented = false }
                    }
                }) {
                    Text(localizationManager.localized("app_limits_save_all"))
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("app_limits_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadAppLimits()
        }
        .withVisualLogger()
    }

    @MainActor
    private func syncAppLimitsToServer() async {
        let serializableLimits = appLimits.map { ["app": $0.app, "limit": $0.limit] }
        let payload: [String: AnyCodable] = [
            "appLimits": AnyCodable(serializableLimits)
        ]
        VisualLogger.shared.log(
            "🔵 ADVANCED.API appLimits POST start count=\(appLimits.count)",
            level: .info,
            category: "ADVANCED.API"
        )
        do {
            let existing = try? await configurationService.getConfiguration(for: "parental_control_bot")
            var merged = existing?.additionalSettings ?? [:]
            payload.forEach { merged[$0.key] = $0.value }
            let config = ComponentConfiguration(isEnabled: true, priority: .normal, additionalSettings: merged)
            try await configurationService.saveConfiguration(componentId: "parental_control_bot", configuration: config)
            VisualLogger.shared.log("✅ ADVANCED.API appLimits POST ok", level: .info, category: "ADVANCED.API")
        } catch {
            VisualLogger.shared.log("❌ ADVANCED.API appLimits POST failed: \(error.localizedDescription)", level: .error, category: "ADVANCED.API")
        }
    }
}

// Вспомогательная структура для Codable
// AppLimit models moved to global APIModels.swift

// MARK: Геолокация

struct GeofencesSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Сохранение геозон в UserDefaults
    private let geofencesKey = "geofences_settings"
    
    @State private var geofences: [GeofenceItem] = []
    
    @State private var showAddForm = false
    @State private var newGeofenceName = ""
    @State private var newGeofenceAddress = ""
    @State private var newGeofenceRadius: Double = 100
    @State private var showValidationAlert = false
    @State private var validationAlertMessage = ""
    
    // Загрузка геозон из UserDefaults
    private func loadGeofences() {
        if let data = UserDefaults.standard.data(forKey: geofencesKey),
           let decoded = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data) {
            geofences = decoded.map { GeofenceItem(name: $0.name, address: $0.address, radius: $0.radius) }
        } else {
            // Значения по умолчанию - используем локализованные строки
            geofences = [
                GeofenceItem(name: localizationManager.localized("geofences_home"), address: localizationManager.localized("geofences_street_lenin"), radius: 100),
                GeofenceItem(name: localizationManager.localized("geofences_school"), address: localizationManager.localized("geofences_street_pushkin"), radius: 200)
            ]
        }
    }
    
    // Сохранение геозон в UserDefaults
    private func saveGeofences() {
        let codable = geofences.map { GeofenceItemCodable(name: $0.name, address: $0.address, radius: $0.radius) }
        if let encoded = try? JSONEncoder().encode(codable) {
            UserDefaults.standard.set(encoded, forKey: geofencesKey)
        }
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("geofences_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Существующие геозоны
                ForEach($geofences) { $geofence in
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(geofence.name)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Button(action: {
                                HapticFeedback.impact(.medium)
                                VisualLogger.shared.log(
                                    "🗑️ geofence_remove name=\(geofence.name)",
                                    level: .info,
                                    category: "PARENTAL.UI"
                                )
                                geofences.removeAll { $0.id == geofence.id }
                                saveGeofences()
                            }) {
                                Image(systemName: "trash")
                                    .font(.body)
                                    .foregroundColor(.dangerRed)
                            }
                        }
                        
                        Text(geofence.address)
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        
                        HStack {
                            Text(localizationManager.localized("geofences_radius"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            
                            Text("\(Int(geofence.radius)) \(localizationManager.localized("geofences_radius_m"))")
                                .font(.caption)
                                .foregroundColor(.secondaryGold)
                                .fontWeight(.semibold)
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
                
                // Форма добавления
                if showAddForm {
                    VStack(spacing: Spacing.m) {
                        TextField(localizationManager.localized("geofences_name_placeholder"), text: $newGeofenceName)
                            .font(.body)
                            .foregroundColor(.textPrimary)
                            .padding(Spacing.m)
                            .background(Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                        
                        TextField(localizationManager.localized("geofences_address_placeholder"), text: $newGeofenceAddress)
                            .font(.body)
                            .foregroundColor(.textPrimary)
                            .padding(Spacing.m)
                            .background(Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                        
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            HStack {
                                Text(localizationManager.localized("geofences_radius"))
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Spacer()
                                
                                Text("\(Int(newGeofenceRadius)) \(localizationManager.localized("geofences_radius_m"))")
                                    .font(.bodyBold)
                                    .foregroundColor(.secondaryGold)
                            }
                            
                            Slider(value: $newGeofenceRadius, in: 50...500, step: 10) {
                                Text(localizationManager.localized("geofences_radius"))
                            }
                            .tint(.secondaryGold)
                            .onChange(of: newGeofenceRadius) { newValue in
                                VisualLogger.shared.log(
                                    "🎚️ geofence_radius = \(Int(newValue)) m",
                                    level: .info,
                                    category: "PARENTAL.UI"
                                )
                            }
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                        
                        HStack(spacing: Spacing.m) {
                            Button(action: {
                                HapticFeedback.impact(.medium)
                                showAddForm = false
                            }) {
                                Text(localizationManager.localized("edit_profile_cancel"))
                                    .font(.body)
                                    .foregroundColor(.textSecondary)
                                    .frame(maxWidth: .infinity)
                                    .padding(Spacing.m)
                                    .background(Color.backgroundMedium.opacity(0.5))
                                    .cornerRadius(CornerRadius.medium)
                            }
                            
                            Button(action: {
                                HapticFeedback.impact(.medium)
                                let trimmedName = newGeofenceName.trimmingCharacters(in: .whitespacesAndNewlines)
                                let trimmedAddress = newGeofenceAddress.trimmingCharacters(in: .whitespacesAndNewlines)
                                
                                guard !trimmedName.isEmpty, !trimmedAddress.isEmpty else {
                                    validationAlertMessage = localizationManager.currentLanguage == .russian
                                        ? "Введите название и адрес геозоны"
                                        : "Enter geofence name and address"
                                    showValidationAlert = true
                                    VisualLogger.shared.log(
                                        "⚠️ geofence_add_validation_failed nameEmpty=\(trimmedName.isEmpty) addressEmpty=\(trimmedAddress.isEmpty)",
                                        level: .warning,
                                        category: "PARENTAL.UI"
                                    )
                                    return
                                }
                                
                                geofences.append(GeofenceItem(name: trimmedName, address: trimmedAddress, radius: newGeofenceRadius))
                                VisualLogger.shared.log(
                                    "➕ geofence_add name=\(trimmedName) radius=\(Int(newGeofenceRadius))",
                                    level: .info,
                                    category: "PARENTAL.UI"
                                )
                                newGeofenceName = ""
                                newGeofenceAddress = ""
                                newGeofenceRadius = 100
                                showAddForm = false
                                saveGeofences()
                            }) {
                                Text(localizationManager.localized("geofences_add"))
                                    .font(.bodyBold)
            .foregroundColor(.white)
                                    .frame(maxWidth: .infinity)
                                    .padding(Spacing.m)
                                    .background(Color.secondaryGold)
                                    .cornerRadius(CornerRadius.medium)
                            }
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.secondaryGold.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                } else {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        showAddForm = true
                    }) {
                        HStack {
                            Image(systemName: "plus.circle.fill")
                                .font(.body)
                                .foregroundColor(.secondaryGold)
                            
                            Text(localizationManager.localized("geofences_add_geofence"))
                                .font(.bodyBold)
                                .foregroundColor(.secondaryGold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold.opacity(0.2))
                        .cornerRadius(CornerRadius.medium)
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(Color.secondaryGold.opacity(0.5), lineWidth: 1)
                        )
                    }
                }
            }
        }
        .id("geofences_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadGeofences()
        }
        .alert(localizationManager.currentLanguage == .russian ? "Проверьте поля" : "Check fields", isPresented: $showValidationAlert) {
            Button(localizationManager.currentLanguage == .russian ? "OK" : "OK", role: .cancel) {}
        } message: {
            Text(validationAlertMessage)
        }
        .withVisualLogger()
    }
}

// Вспомогательная структура для Codable
// Geofence models moved to global GeofenceModels.swift

struct LocationHistoryDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var locationHistory: [LocationHistoryItem] = []
    @State private var frequentPlaces: [FrequentPlace] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("location_history_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Частые места
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("location_frequent_places"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(frequentPlaces) { place in
                        HStack {
                            Text(place.name)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Text("\(place.visits) \(localizationManager.localized("location_visits"))")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
                
                Divider()
                
                // История событий
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("location_events_today"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(locationHistory) { item in
                        HStack(spacing: Spacing.m) {
                            Text(item.icon)
                                .font(.system(size: 32))
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text(item.action)
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Text(item.location)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Spacer()
                            
                            Text(item.time)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
            }
        }
        .id("location_history_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadLocationData()
        }
    }
    
    private func loadLocationData() {
        // Загружаем локализованные данные
        locationHistory = [
            LocationHistoryItem(time: "08:30", location: localizationManager.localized("geofences_street_lenin"), action: localizationManager.localized("location_left_home"), icon: "🚶"),
            LocationHistoryItem(time: "09:15", location: localizationManager.localized("geofences_street_pushkin"), action: localizationManager.localized("location_arrived_school"), icon: "✅"),
            LocationHistoryItem(time: "15:45", location: localizationManager.localized("geofences_street_lenin"), action: localizationManager.localized("location_returned_home"), icon: "🏠"),
            LocationHistoryItem(time: "17:30", location: localizationManager.localized("location_mall"), action: localizationManager.localized("location_visited_mall"), icon: "🛒")
        ]
        
        frequentPlaces = [
            FrequentPlace(name: localizationManager.localized("geofences_home"), visits: 45, color: .successGreen),
            FrequentPlace(name: localizationManager.localized("geofences_school"), visits: 32, color: .blue),
            FrequentPlace(name: localizationManager.localized("location_mall"), visits: 8, color: .warningOrange)
        ]
    }
}

struct LocationHistoryItem: Identifiable {
    let id = UUID()
    let time: String
    let location: String
    let action: String
    let icon: String
}

struct FrequentPlace: Identifiable {
    let id = UUID()
    let name: String
    let visits: Int
    let color: Color
}

// MARK: Отчёты

struct WeeklyReportDetailModal: View {
    @Binding var isPresented: Bool
    /// Идентификатор ребёнка для query `childId` на `GET /api/parental-control/reports/weekly`; `nil` — отчёты целевого пользователя токена.
    var childId: String? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var reports: [ParentalReportItem] = []
    @State private var isLoading = true
    @State private var loadError: String?
    
    var body: some View {
        FamilyModalBaseView(
            title: "📅 \(localizationManager.localized("family_weekly_report"))",
            isPresented: $isPresented
        ) {
            Group {
                if isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.l)
                } else if let loadError {
                    Text(loadError)
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(Spacing.m)
                } else if let latest = reports.first {
                    weeklyReportDetailBody(latest: latest)
                } else {
                    VStack(spacing: Spacing.s) {
                        Text(localizationManager.localized("family_reports_empty_title"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                            .multilineTextAlignment(.center)
                        Text(localizationManager.localized("family_reports_empty_hint_jwt"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(Spacing.m)
                }
            }
        }
        .onAppear {
            fetchWeeklyReports()
        }
    }
    
    private var emDash: String { "—" }
    
    private func weeklyReportDetailBody(latest: ParentalReportItem) -> some View {
        let content = latest.content
        let extraKeys = content.keys.filter { !knownWeeklyContentKeys.contains($0) }.sorted()
        let extraLines: [String] = extraKeys.compactMap { kvLine(key: $0, value: content[$0]?.value) }
        return VStack(alignment: .leading, spacing: Spacing.m) {
            Text(latest.createdAt.formatted(date: .abbreviated, time: .shortened))
                .font(.caption)
                .foregroundColor(.textTertiary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            ReportStatCard(
                icon: "🌐",
                title: localizationManager.localized("family_web_activity"),
                value: weeklyValue(
                    scalar: firstScalarString(in: content, keys: ["sites_count", "web_sites_count", "total_sites", "sites", "web_sites"]),
                    suffix: localizationManager.localized("family_sites")
                ),
                color: .blue
            )
            ReportStatCard(
                icon: "📱",
                title: localizationManager.localized("family_applications"),
                value: weeklyValue(
                    scalar: firstScalarString(in: content, keys: ["apps_count", "applications_count", "apps", "applications"]),
                    suffix: localizationManager.localized("family_apps")
                ),
                color: .purple
            )
            ReportStatCard(
                icon: "⏰",
                title: localizationManager.localized("family_screen_time"),
                value: screenTimeDisplay(content) ?? emDash,
                color: .orange
            )
            ReportStatCard(
                icon: "🚫",
                title: localizationManager.localized("family_blocked_attempts"),
                value: weeklyValue(
                    scalar: firstScalarString(in: content, keys: ["blocked_attempts", "blocked_count", "blocked", "blocks"]),
                    suffix: localizationManager.localized("family_attempts")
                ),
                color: .red
            )
            ReportStatCard(
                icon: "📍",
                title: localizationManager.localized("family_movements"),
                value: weeklyValue(
                    scalar: firstScalarString(in: content, keys: ["movements", "location_events", "locations_count"]),
                    suffix: localizationManager.localized("family_events")
                ),
                color: .green
            )
            ReportStatCard(
                icon: "⚠️",
                title: localizationManager.localized("family_warnings_new"),
                value: weeklyValue(
                    scalar: firstScalarString(in: content, keys: ["warnings_count", "warnings", "suspicious_count", "new_warnings"]),
                    suffix: localizationManager.localized("family_new")
                ),
                color: .warningOrange
            )
            
            if !extraLines.isEmpty {
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_week_detailed"))
                        .font(.captionBold)
                        .foregroundColor(.textSecondary)
                    ForEach(Array(extraLines.enumerated()), id: \.offset) { _, line in
                        Text(line)
                            .font(.caption)
                            .foregroundColor(.textTertiary)
                    }
                }
                .padding(Spacing.s)
                .background(Color.backgroundMedium.opacity(0.2))
                .cornerRadius(CornerRadius.small)
            }
        }
    }
    
    private var knownWeeklyContentKeys: Set<String> {
        [
            "sites_count", "web_sites_count", "total_sites", "sites", "web_sites",
            "apps_count", "applications_count", "apps", "applications",
            "screen_time", "screenTime", "total_screen_time", "screen_time_hours", "screen_time_minutes", "hours", "minutes",
            "blocked_attempts", "blocked_count", "blocked", "blocks",
            "movements", "location_events", "locations_count",
            "warnings_count", "warnings", "suspicious_count", "new_warnings"
        ]
    }
    
    private func weeklyValue(scalar: String?, suffix: String) -> String {
        guard let scalar, !scalar.isEmpty else { return emDash }
        return "\(scalar) \(suffix)"
    }
    
    private func screenTimeDisplay(_ content: [String: AnyCodable]) -> String? {
        if let s = firstScalarString(in: content, keys: ["screen_time", "screenTime", "total_screen_time"]), !s.isEmpty {
            return s
        }
        let hours = firstInt(in: content, keys: ["screen_time_hours", "hours"])
        let minutes = firstInt(in: content, keys: ["screen_time_minutes", "minutes"])
        if hours != nil || minutes != nil {
            return "\(hours ?? 0)h \(minutes ?? 0)m"
        }
        return nil
    }
    
    private func firstScalarString(in content: [String: AnyCodable], keys: [String]) -> String? {
        for key in keys {
            guard let any = content[key]?.value else { continue }
            if let i = any as? Int { return String(i) }
            if let d = any as? Double { return String(Int(d)) }
            if let s = any as? String, !s.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { return s }
            if let b = any as? Bool { return b ? "1" : "0" }
        }
        return nil
    }
    
    private func firstInt(in content: [String: AnyCodable], keys: [String]) -> Int? {
        for key in keys {
            guard let any = content[key]?.value else { continue }
            if let i = any as? Int { return i }
            if let d = any as? Double { return Int(d) }
            if let s = any as? String, let v = Int(s.trimmingCharacters(in: .whitespaces)) { return v }
        }
        return nil
    }
    
    private func kvLine(key: String, value: Any?) -> String? {
        guard let value else { return nil }
        if let arr = value as? [Any] { return "\(key): \(arr.count) items" }
        if let dict = value as? [String: Any] { return "\(key): \(dict.count) keys" }
        return "\(key): \(value)"
    }
    
    private func fetchWeeklyReports() {
        isLoading = true
        loadError = nil
        APIService.shared.getWeeklyReports(childId: childId) { result in
            DispatchQueue.main.async {
                isLoading = false
                switch result {
                case .success(let items):
                    reports = items.sorted { $0.createdAt > $1.createdAt }
                case .failure(let error):
                    loadError = error.localizedDescription
                }
            }
        }
    }
}

struct ReportStatCard: View {
    let icon: String
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 32))
                .frame(width: 50, height: 50)
                .background(color.opacity(0.2))
                .cornerRadius(25)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textSecondary)
                
                Text(value)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            
            Spacer()
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(CornerRadius.medium)
    }
}

struct SuspiciousActivityDetailModal: View {
    @Binding var isPresented: Bool
    var childId: String? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var warnings: [SuspiciousWarning] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_suspicious_activity_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                if warnings.isEmpty {
                    Text(localizationManager.localized("parental_usage_no_data"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(Spacing.m)
                }
                ForEach(warnings) { warning in
                    HStack(spacing: Spacing.m) {
                        Image(systemName: warning.level == .high ? "exclamationmark.triangle.fill" : "exclamationmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(warning.level == .high ? .dangerRed : .warningOrange)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(warning.text)
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            
                            Text(warning.time.isEmpty ? "—" : warning.time)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(warning.level == .high ? Color.dangerRed.opacity(0.1) : Color.warningOrange.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(warning.level == .high ? Color.dangerRed.opacity(0.5) : Color.warningOrange.opacity(0.5), lineWidth: 2)
                    )
                }
            }
        }
        .id("suspicious_activity_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadSuspiciousFromServer()
        }
    }
    
    private func loadSuspiciousFromServer() {
        ParentalControlManager.shared.getMonitoringDetail(childId: childId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let detail):
                    warnings = detail.suspicious.map { row in
                        let lvl: SuspiciousWarning.WarningLevel = row.level == "high" ? .high : .medium
                        return SuspiciousWarning(text: row.text, level: lvl, time: row.time)
                    }
                case .failure:
                    warnings = []
                }
            }
        }
    }
}

struct SuspiciousWarning: Identifiable {
    let id: UUID
    let text: String
    let level: WarningLevel
    let time: String
    
    enum WarningLevel {
        case high, medium
    }
    
    init(id: UUID = UUID(), text: String, level: WarningLevel, time: String) {
        self.id = id
        self.text = text
        self.level = level
        self.time = time
    }
}

struct TopSitesDetailModal: View {
    @Binding var isPresented: Bool
    var childId: String? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var topSites: [TopSiteItem] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("top_sites_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(Array(topSites.enumerated()), id: \.element.id) { index, site in
                    HStack(spacing: Spacing.m) {
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(site.site)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                    Text("\(site.visits) \(localizationManager.localized("top_sites_visits"))")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                    Text(formatDuration(hours: site.hours, minutes: site.minutes))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                                Text(localizationManager.localized(site.categoryKey))
                                .font(.captionSmall)
                                    .foregroundColor(site.color)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(site.color.opacity(0.2))
                                .cornerRadius(8)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("top_sites_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadTopSites()
        }
    }
    
    private func topSitesCategoryKey(for apiCategory: String) -> String {
        switch apiCategory.lowercased() {
        case "video": return "top_sites_category_video"
        case "social": return "top_sites_category_social"
        case "search": return "top_sites_category_search"
        default: return "top_sites_category_search"
        }
    }
    
    private func topSitesCategoryColor(for apiCategory: String) -> Color {
        switch apiCategory.lowercased() {
        case "video": return .red
        case "social": return .purple
        case "search": return .blue
        default: return .blue
        }
    }
    
    private func loadTopSites() {
        ParentalControlManager.shared.getMonitoringDetail(childId: childId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let detail):
                    topSites = detail.topSites.map { row in
                        TopSiteItem(
                            site: row.site,
                            visits: row.visits,
                            hours: row.hours,
                            minutes: row.minutes,
                            categoryKey: topSitesCategoryKey(for: row.category),
                            color: topSitesCategoryColor(for: row.category)
                        )
                    }
                case .failure:
                    topSites = []
                }
            }
        }
    }
    
    private func formatDuration(hours: Int, minutes: Int) -> String {
        let hourUnit = localizationManager.localized("analytics_hour")
        let minuteUnit = localizationManager.localized("analytics_min")
        
        if hours == 0 {
            return "\(minutes) \(minuteUnit)"
        }
        
        if minutes == 0 {
            return "\(hours) \(hourUnit)"
        }
        
        return "\(hours) \(hourUnit) \(minutes) \(minuteUnit)"
    }
}

struct TopSiteItem: Identifiable {
    let id: UUID
    let site: String
    let visits: Int
    let hours: Int
    let minutes: Int
    let categoryKey: String
    let color: Color
    
    init(id: UUID = UUID(), site: String, visits: Int, hours: Int, minutes: Int, categoryKey: String, color: Color) {
        self.id = id
        self.site = site
        self.visits = visits
        self.hours = hours
        self.minutes = minutes
        self.categoryKey = categoryKey
        self.color = color
    }
}

struct TopAppsDetailModal: View {
    @Binding var isPresented: Bool
    var childId: String? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var topApps: [TopAppItem] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("top_apps_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(Array(topApps.enumerated()), id: \.element.id) { index, app in
                    HStack(spacing: Spacing.m) {
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(app.app)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text(formatDurationFromMinutes(app.usageMinutes))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("\(localizationManager.localized("top_apps_limit")) \(formatLimit(app.limitMinutes))")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            if app.exceeded {
                                HStack {
                                    Image(systemName: "exclamationmark.triangle.fill")
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                    
                                    Text(localizationManager.localized("top_apps_exceeded"))
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.dangerRed.opacity(0.2))
                                .cornerRadius(8)
                            }
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(app.exceeded ? Color.dangerRed.opacity(0.1) : Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(app.exceeded ? Color.dangerRed.opacity(0.5) : Color.clear, lineWidth: 2)
                    )
                }
            }
        }
        .id("top_apps_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadTopApps()
        }
    }
    
    private func loadTopApps() {
        ParentalControlManager.shared.getMonitoringDetail(childId: childId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let detail):
                    topApps = detail.topApps.map { row in
                        TopAppItem(
                            app: row.name,
                            usageMinutes: row.usageMinutes,
                            limitMinutes: row.limitMinutes,
                            exceeded: row.exceeded,
                            color: topAppsRowColor(for: row.name)
                        )
                    }
                case .failure:
                    topApps = []
                }
            }
        }
    }
    
    private func topAppsRowColor(for name: String) -> Color {
        let lower = name.lowercased()
        if lower.contains("instagram") { return .purple }
        if lower.contains("tiktok") { return .black }
        if lower.contains("youtube") { return .red }
        if lower.contains("whatsapp") { return .green }
        if lower.contains("vk") { return .blue }
        return .blue
    }
    
    private func formatDurationFromMinutes(_ minutes: Int) -> String {
        let hours = minutes / 60
        let remainingMinutes = minutes % 60
        let hourUnit = localizationManager.localized("analytics_hour")
        let minuteUnit = localizationManager.localized("analytics_min")
        
        if hours == 0 {
            return "\(remainingMinutes) \(minuteUnit)"
        }
        
        if remainingMinutes == 0 {
            return "\(hours) \(hourUnit)"
        }
        
        return "\(hours) \(hourUnit) \(remainingMinutes) \(minuteUnit)"
    }
    
    private func formatLimit(_ minutes: Int) -> String {
        String(format: localizationManager.localized("top_apps_limit_value"), minutes)
    }
}

struct TopAppItem: Identifiable {
    let id: UUID
    let app: String
    let usageMinutes: Int
    let limitMinutes: Int
    let exceeded: Bool
    let color: Color
    
    init(id: UUID = UUID(), app: String, usageMinutes: Int, limitMinutes: Int, exceeded: Bool, color: Color) {
        self.id = id
        self.app = app
        self.usageMinutes = usageMinutes
        self.limitMinutes = limitMinutes
        self.exceeded = exceeded
        self.color = color
    }
}

struct UsageHoursDetailModal: View {
    @Binding var isPresented: Bool
    var childId: String? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var usageHours: [UsageHourItem] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("peak_hours_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(usageHours) { item in
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(item.hour)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Text("\(item.usage)%")
                                .font(.bodyBold)
                                .foregroundColor(item.color)
                        }
                        
                        GeometryReader { geometry in
                            ZStack(alignment: .leading) {
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(Color.backgroundMedium.opacity(0.3))
                                    .frame(height: 20)
                                
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(item.color)
                                    .frame(width: geometry.size.width * CGFloat(item.usage) / 100, height: 20)
                            }
                        }
                        .frame(height: 20)
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("peak_hours_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadPeakHoursFromServer()
        }
    }
    
    private func loadPeakHoursFromServer() {
        ParentalControlManager.shared.getMonitoringDetail(childId: childId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let detail):
                    usageHours = detail.peakHours.map { row in
                        let pct = max(0, min(100, row.usagePercent))
                        let level: UsageHourItem.UsageLevel
                        let color: Color
                        switch pct {
                        case ..<25:
                            level = .low
                            color = .blue
                        case ..<50:
                            level = .medium
                            color = .green
                        case ..<75:
                            level = .high
                            color = .orange
                        default:
                            level = .veryHigh
                            color = .red
                        }
                        return UsageHourItem(hour: row.label, usage: pct, level: level, color: color)
                    }
                case .failure:
                    usageHours = []
                }
            }
        }
    }
}

struct UsageHourItem: Identifiable {
    let id: UUID
    let hour: String
    let usage: Int
    let level: UsageLevel
    let color: Color
    
    enum UsageLevel {
        case low, medium, high, veryHigh
    }
    
    init(id: UUID = UUID(), hour: String, usage: Int, level: UsageLevel, color: Color) {
        self.id = id
        self.hour = hour
        self.usage = usage
        self.level = level
        self.color = color
    }
}

struct BypassAttemptsDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @ObservedObject private var manager = ParentalControlManager.shared
    @AppStorage("parental_selected_child_id") private var selectedChildId: String = ""
    @AppStorage("parental_selected_child") private var legacySelectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Статистика (загружается через API)
    @State private var today: Int = 0
    @State private var week: Int = 0
    @State private var blocked: Int = 0
    @State private var incognitoCount: Int = 0
    @State private var torCount: Int = 0
    @State private var proxyCount: Int = 0
    @State private var isLoading: Bool = true
    
    private var effectiveChildId: String {
        if !selectedChildId.isEmpty { return selectedChildId }
        return legacySelectedChild
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("bypass_attempts_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                if isLoading {
                    ProgressView()
                        .padding(Spacing.l)
                } else {
                    // Общая статистика
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("bypass_stats"))
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                        
                        HStack(spacing: Spacing.m) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(localizationManager.localized("bypass_attempts_today"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                Text("\(today)")
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                            }
                            
                            Spacer()
                            
                            VStack(alignment: .trailing, spacing: 4) {
                                Text(localizationManager.localized("bypass_attempts_week"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                Text("\(week)")
                                    .font(.bodyBold)
                                    .foregroundColor(.warningOrange)
                            }
                        }
                        
                        HStack {
                            Text(localizationManager.localized("bypass_blocked"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(blocked)")
                                .font(.bodyBold)
                                .foregroundColor(.successGreen)
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Детализация по типам
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("bypass_details"))
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                        
                        // Скрытый режим
                        BypassTypeCard(
                            icon: "🕶️",
                            title: localizationManager.localized("bypass_incognito_type"),
                            count: incognitoCount,
                            color: .warningOrange
                        )
                        .environmentObject(localizationManager)
                        
                        // Tor
                        BypassTypeCard(
                            icon: "🧅",
                            title: localizationManager.localized("bypass_tor_type"),
                            count: torCount,
                            color: .dangerRed
                        )
                        .environmentObject(localizationManager)
                        
                        // Proxy
                        BypassTypeCard(
                            icon: "🔀",
                            title: localizationManager.localized("bypass_proxy_type"),
                            count: proxyCount,
                            color: .infoBlue
                        )
                        .environmentObject(localizationManager)
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("bypass_attempts_detail_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadBypassStatistics()
        }
        .onChange(of: selectedChildId) { _ in
            loadBypassStatistics()
        }
    }
    
    private func loadBypassStatistics() {
        isLoading = true
        manager.getBypassStats(childId: effectiveChildId) { result in
            DispatchQueue.main.async {
                self.isLoading = false
                switch result {
                case .success(let stats):
                    self.today = stats.today
                    self.week = stats.week
                    self.blocked = stats.blocked
                    self.incognitoCount = stats.incognito
                    self.torCount = stats.tor
                    self.proxyCount = stats.proxy
                case .failure(let error):
                    print("⚠️ Failed to load bypass statistics: \(error.localizedDescription)")
                    let local = manager.localBypassAggregates(
                        for: effectiveChildId.isEmpty ? nil : effectiveChildId
                    )
                    today = local.today
                    week = local.week
                    blocked = local.blocked
                    incognitoCount = local.incognito
                    torCount = local.tor
                    proxyCount = local.proxy
                }
            }
        }
    }
}

// MARK: - Bypass Type Card Component

struct BypassTypeCard: View {
    let icon: String
    let title: String
    let count: Int
    let color: Color
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 32))
                .frame(width: 50, height: 50)
                .background(color.opacity(0.2))
                .cornerRadius(25)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                Text("\(count) \(localizationManager.localized("bypass_attempts_count"))")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            Text("\(count)")
                .font(.title3)
                .foregroundColor(color)
                .bold()
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .stroke(color.opacity(0.5), lineWidth: 2)
        )
    }
}

// BypassAttempt (старая версия для модалов) - переименована для избежания конфликта с ParentalControlManager.BypassAttempt
struct BypassAttemptOld: Identifiable {
    let id = UUID()
    let method: String
    let count: Int
    let lastTime: String
    let color: Color
}

// MARK: YouTube настройки

struct YouTubeSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Сохранение настроек YouTube в UserDefaults
    @AppStorage("youtube_safe_mode") private var isSafeModeEnabled = true
    @AppStorage("youtube_age_restriction_enabled") private var isAgeRestrictionEnabled = true
    @AppStorage("youtube_age_restriction") private var ageRestriction = 12
    @AppStorage("youtube_time_limit") private var timeLimit: Double = 45
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("youtube_settings_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Безопасный режим
                FamilyContentBlockItem(
                    icon: "🛡️",
                    title: localizationManager.localized("youtube_safe_mode"),
                    description: localizationManager.localized("youtube_safe_mode_desc"),
                    isEnabled: $isSafeModeEnabled
                )
                
                // Возрастные ограничения
                VStack(alignment: .leading, spacing: Spacing.m) {
                    HStack {
                        Text(localizationManager.localized("youtube_age_restriction"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Toggle("", isOn: $isAgeRestrictionEnabled)
                            .labelsHidden()
                            .tint(.secondaryGold)
                    }
                    
                    if isAgeRestrictionEnabled {
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(String(format: localizationManager.localized("youtube_age_restriction_value"), ageRestriction))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                            
                            Text(localizationManager.localized("youtube_age_restriction_desc"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Лимит времени
                VStack(alignment: .leading, spacing: Spacing.m) {
                    HStack {
                        Text(localizationManager.localized("youtube_time_limit"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Text("\(Int(timeLimit)) \(localizationManager.localized("youtube_time_limit_value"))")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Slider(value: $timeLimit, in: 15...120, step: 15) {
                        Text(localizationManager.localized("youtube_time_limit"))
                    }
                    .tint(.secondaryGold)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    VisualLogger.shared.log(
                        "💾 youtube_settings_save safeMode=\(isSafeModeEnabled) ageEnabled=\(isAgeRestrictionEnabled) age=\(ageRestriction) limit=\(Int(timeLimit))",
                        level: .success,
                        category: "PARENTAL.UI"
                    )
                    isPresented = false
                }) {
                    Text(localizationManager.localized("youtube_save"))
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("youtube_settings_lang_\(localizationManager.currentLanguage.rawValue)")
        .onChange(of: isSafeModeEnabled) { newValue in
            VisualLogger.shared.log(
                "🔄 youtube_safe_mode = \(newValue)",
                level: .info,
                category: "PARENTAL.UI"
            )
            print("✅ YouTube Safe Mode: \(newValue ? "ON" : "OFF")")
        }
        .onChange(of: isAgeRestrictionEnabled) { newValue in
            VisualLogger.shared.log(
                "🔄 youtube_age_restriction_enabled = \(newValue)",
                level: .info,
                category: "PARENTAL.UI"
            )
            print("✅ YouTube Age Restriction: \(newValue ? "ON" : "OFF")")
        }
        .onChange(of: ageRestriction) { newValue in
            VisualLogger.shared.log(
                "🔄 youtube_age_restriction = \(newValue)+",
                level: .info,
                category: "PARENTAL.UI"
            )
            print("✅ YouTube Age Restriction: \(newValue)+")
        }
        .onChange(of: timeLimit) { newValue in
            VisualLogger.shared.log(
                "🎚️ youtube_time_limit = \(Int(newValue)) min/day",
                level: .info,
                category: "PARENTAL.UI"
            )
            print("✅ YouTube Time Limit: \(Int(newValue)) min/day")
        }
        .withVisualLogger()
    }
}

// MARK: - Parental Control Settings Modal

struct FamilyParentalControlSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Manager для применения правил
    @ObservedObject private var manager = ParentalControlManager.shared
    
    // Выбор ребёнка: server ID (для API) + name (только для отображения)
    @AppStorage("parental_selected_child_id") private var selectedChildId: String = ""
    @AppStorage("parental_selected_child_name") private var selectedChildName: String = ""
    // Legacy key: раньше здесь часто хранилось имя, теперь сохраняем ID для совместимости
    @AppStorage("parental_selected_child") private var legacySelectedChild: String = ""
    
    // Список детей (динамический): ID + имя
    @State private var children: [ChildOption] = []
    private let apiService = APIService.shared
    
    private struct ChildOption: Identifiable, Equatable {
        let id: String
        let name: String
    }
    
    // Уровень защиты по возрасту
    enum AgeGroup: String, CaseIterable {
        case toddler
        case school
        case teen
        case adult
        
        var titleKey: String {
            switch self {
            case .toddler: return "family_age_group_toddler"
            case .school: return "family_age_group_school"
            case .teen: return "family_age_group_teen"
            case .adult: return "family_age_group_adult"
            }
        }
        
        var descriptionKey: String {
            switch self {
            case .toddler: return "family_age_group_toddler_desc"
            case .school: return "family_age_group_school_desc"
            case .teen: return "family_age_group_teen_desc"
            case .adult: return "family_age_group_adult_desc"
            }
        }
        
        static func fromStoredValue(_ value: String) -> AgeGroup {
            if let direct = AgeGroup(rawValue: value) {
                return direct
            }
            let manager = LocalizationManager()
            let normalized = value.lowercased()
            let ru = manager.translations[.russian] ?? [:]
            let en = manager.translations[.english] ?? [:]
            let toddlerLabels = Set([
                "1-6",
                ru["family_age_group_toddler"]?.lowercased(),
                en["family_age_group_toddler"]?.lowercased(),
                ru["family_for_1_6"]?.lowercased(),
                en["family_for_1_6"]?.lowercased()
            ].compactMap { $0 })
            let schoolLabels = Set([
                "7-13",
                ru["family_age_group_school"]?.lowercased(),
                en["family_age_group_school"]?.lowercased(),
                ru["family_for_7_13"]?.lowercased(),
                en["family_for_7_13"]?.lowercased()
            ].compactMap { $0 })
            let teenLabels = Set([
                "14-17",
                ru["family_age_group_teen"]?.lowercased(),
                en["family_age_group_teen"]?.lowercased(),
                ru["family_for_14_17"]?.lowercased(),
                en["family_for_14_17"]?.lowercased()
            ].compactMap { $0 })
            let adultLabels = Set([
                "18+",
                ru["family_age_group_adult"]?.lowercased(),
                en["family_age_group_adult"]?.lowercased(),
                ru["family_for_18_plus"]?.lowercased(),
                en["family_for_18_plus"]?.lowercased()
            ].compactMap { $0 })
            if toddlerLabels.contains(normalized) { return .toddler }
            if schoolLabels.contains(normalized) { return .school }
            if teenLabels.contains(normalized) { return .teen }
            if adultLabels.contains(normalized) { return .adult }
            return .school
        }
    }
    
    // Сохранение возраста в UserDefaults
    @AppStorage("parental_age_group") private var selectedAgeGroupRaw: String = AgeGroup.school.rawValue
    
    // Вычисляемое свойство для работы с enum
    private var selectedAgeGroup: AgeGroup {
        get {
            AgeGroup.fromStoredValue(selectedAgeGroupRaw)
        }
        set {
            selectedAgeGroupRaw = newValue.rawValue
        }
    }
    
    // Автоматические правила с сохранением в UserDefaults
    @AppStorage("parental_automated_rules_enabled") private var isAutomatedRulesEnabled: Bool = true // По умолчанию ВКЛЮЧЕНЫ
    @State private var showAutomatedRulesModal = false
    
    // Применение правил при изменении возраста
    private func applyAgeBasedRules() {
        guard isAutomatedRulesEnabled else { return }
        VisualLogger.shared.log(
            "🔵 AUTO RULES apply start child=\(selectedChildName) age=\(selectedAgeGroup.rawValue)",
            level: .info,
            category: "PARENTAL.API"
        )
        
        // Сохраняем настройки в UserDefaults
        let rules: [String: Any] = [
            "selectedChildId": selectedChildId,
            "selectedChildName": selectedChildName,
            "ageGroup": selectedAgeGroup.rawValue,
            "isEnabled": isAutomatedRulesEnabled,
            "appliedDate": Date().timeIntervalSince1970
        ]
        
        // Сохраняем через UserDefaults
        UserDefaults.standard.set(rules, forKey: "parental_control_rules_\(selectedChildId)")
        
        // Логируем применение правил
        print("✅ Rules applied for \(selectedChildName) [\(selectedChildId)], age group: \(selectedAgeGroup.rawValue)")
        
        // ✅ BUILD 96: Используем значения по умолчанию для предотвращения рекурсии
        // В этой функции (FamilyParentalControlSettingsModal) нет доступа к cachedParentalRules из FamilyScreen
        // Используем прямые значения из UserDefaults асинхронно
        let parentalRules = ParentalControlRules(
            websiteBlocking: false,
            appBlocking: false,
            searchBlocking: false,
            safesearch: false,
            screenTimeLimit: nil,
            bedtimeStart: nil,
            bedtimeEnd: nil,
            appLimits: nil,
            geofences: nil
        )
        
        // ✅ BUILD 96: Загружаем значения асинхронно для предотвращения рекурсии
        Task { @MainActor in
            let loadedRules = ParentalControlRules(
                websiteBlocking: UserDefaults.standard.bool(forKey: "parental_website_blocking"),
                appBlocking: UserDefaults.standard.bool(forKey: "parental_app_blocking"),
                searchBlocking: UserDefaults.standard.bool(forKey: "parental_search_blocking"),
                safesearch: UserDefaults.standard.bool(forKey: "parental_safesearch"),
                screenTimeLimit: nil,
                bedtimeStart: nil,
                bedtimeEnd: nil,
                appLimits: nil,
                geofences: nil
            )
            // Используем загруженные правила для применения через API
            // (parentalRules уже используется ниже, поэтому это для будущего использования)
            _ = loadedRules
        }
        
        // Преобразуем возрастную группу в формат API
        let ageGroupString: String = {
            switch selectedAgeGroup {
            case .toddler: return "1-6"
            case .school: return "7-13"
            case .teen: return "14-17"
            case .adult: return "18+"
            }
        }()
        
        manager.applyRules(
            childId: selectedChildId,
            ageGroup: ageGroupString,
            rules: parentalRules
        ) { success, error in
            if success {
                print("✅ Rules applied via API for \(selectedChildName) [\(selectedChildId)]")
                VisualLogger.shared.log(
                    "✅ AUTO RULES apply ok child=\(selectedChildName) age=\(ageGroupString)",
                    level: .success,
                    category: "PARENTAL.API"
                )
            } else {
                print("⚠️ Failed to apply rules: \(error ?? "Unknown error")")
                VisualLogger.shared.log(
                    "❌ AUTO RULES apply failed: \(error ?? "Unknown error")",
                    level: .error,
                    category: "PARENTAL.API"
                )
            }
        }
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_parental_settings_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Выбор ребёнка
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_select_child"))
                         .font(.bodyBold)
                         .foregroundColor(.textPrimary)
                     
                    Picker(localizationManager.localized("family_child"), selection: $selectedChildId) {
                        ForEach(children) { child in
                            Text(child.name).tag(child.id)
                        }
                    }
                    .pickerStyle(.segmented)
                    .tint(Color.secondaryGold)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // 2. Уровень защиты по возрасту
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_protection_level"))
                         .font(.bodyBold)
                         .foregroundColor(.textPrimary)
                     
                    Picker(localizationManager.localized("family_age_restrictions"), selection: Binding(
                         get: { selectedAgeGroup },
                         set: { newValue in
                             selectedAgeGroupRaw = newValue.rawValue
                         }
                     )) {
                         ForEach(AgeGroup.allCases, id: \.self) { age in
                             Text(localizationManager.localized(age.titleKey)).tag(age)
                         }
                     }
                    .pickerStyle(.menu)
                    .tint(Color.secondaryGold)
                    .onChange(of: selectedAgeGroupRaw) { _ in
                        // Автоматически применяем правила при изменении возраста
                        applyAgeBasedRules()
                    }
                    
                    Text(localizationManager.localized(selectedAgeGroup.descriptionKey))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .padding(.top, Spacing.xs)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // 3. Автоматические правила
                FamilyConfigButtonItem(
                    icon: "🤖",
                    title: localizationManager.localized("family_auto_rules_title"),
                    description: isAutomatedRulesEnabled ? localizationManager.localized("family_auto_rules_enabled_desc") : localizationManager.localized("family_auto_rules_disabled_desc"),
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showAutomatedRulesModal = true }
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Информация
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_how_it_works"))
                         .font(.bodyBold)
                         .foregroundColor(.secondaryGold)
                     
                    Text(localizationManager.localized("family_auto_rules"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                 }
                .padding(Spacing.m)
                .background(Color.secondaryGold.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                
                // Кнопка применения правил
                if isAutomatedRulesEnabled {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        VisualLogger.shared.log(
                            "🟡 AUTO RULES manual apply tapped",
                            level: .info,
                            category: "PARENTAL.UI"
                        )
                        applyAgeBasedRules()
                    }) {
                        Text(localizationManager.localized("family_apply_rules"))
                            .font(.bodyBold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                    }
                    .padding(.top, Spacing.s)
                }
            }
        }
        .onAppear {
            // ✅ ЗАГРУЗКА ДЕТЕЙ: Загружаем список детей при открытии модала
            loadChildren()
            
            // Применяем правила при открытии модала (если уже включены)
            if isAutomatedRulesEnabled {
                applyAgeBasedRules()
            }
        }
        .onChange(of: selectedChildId) { _ in
            syncSelectedChildName()
            VisualLogger.shared.log(
                "🔄 auto_rules_child = \(selectedChildName)",
                level: .info,
                category: "PARENTAL.UI"
            )
            // Применяем правила при смене ребёнка
            if isAutomatedRulesEnabled {
                applyAgeBasedRules()
            }
        }
        .onChange(of: isAutomatedRulesEnabled) { newValue in
            VisualLogger.shared.log(
                "🔄 parental_automated_rules_enabled = \(newValue)",
                level: .info,
                category: "PARENTAL.UI"
            )
            if newValue {
                // Применяем правила при включении
                applyAgeBasedRules()
            }
            print("✅ Automated rules: \(newValue ? "ON" : "OFF")")
        }
        .sheet(isPresented: $showAutomatedRulesModal) {
            AutomatedRulesModal(isPresented: $showAutomatedRulesModal, isEnabled: $isAutomatedRulesEnabled, ageGroup: selectedAgeGroup) {
                // Обновляем правила при изменении в модале автоматических правил
                applyAgeBasedRules()
            }
            .environmentObject(localizationManager)
        }
        .withVisualLogger()
    }
    
    // ✅ ГИБРИД: сначала кэш (быстро), потом сервер (актуально)
    private func loadChildren() {
        guard let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            children = []
            print("⚠️ Нет данных о детях в UserDefaults")
            loadChildrenFromServer()
            return
        }
        
        children = decoded
            .filter { member in
                member.role == .child || member.role == .teenager
            }
            .map { ChildOption(id: $0.serverMemberId ?? $0.id, name: $0.name) }
        
        print("✅ Загружено детей: \(children.count)")
        
        // Миграция legacy значения: если там было имя, пытаемся найти и заменить на ID
        if !legacySelectedChild.isEmpty, UUID(uuidString: legacySelectedChild) == nil {
            if let byName = children.first(where: { $0.name == legacySelectedChild }) {
                selectedChildId = byName.id
            }
        }
        
        // Если выбранный ребёнок не в списке, выбираем первого
        if !children.isEmpty && !children.map({ $0.id }).contains(selectedChildId) {
            selectedChildId = children.first?.id ?? ""
        }
        
        syncSelectedChildName()
        loadChildrenFromServer()
    }
    
    private func loadChildrenFromServer() {
        apiService.getFamilyMembers { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let members):
                    let serverChildren = members
                        .filter { $0.role.lowercased() == "child" || $0.role.lowercased() == "teenager" }
                        .map { ChildOption(id: $0.id, name: $0.name) }
                    
                    guard !serverChildren.isEmpty else { return }
                    self.children = serverChildren
                    
                    if !self.children.map({ $0.id }).contains(self.selectedChildId) {
                        self.selectedChildId = self.children.first?.id ?? ""
                    }
                    self.syncSelectedChildName()
                case .failure(let error):
                    print("⚠️ Не удалось обновить список детей с сервера: \(error.localizedDescription)")
                }
            }
        }
    }
    
    private func syncSelectedChildName() {
        if let child = children.first(where: { $0.id == selectedChildId }) {
            selectedChildName = child.name
        }
        // Для обратной совместимости: старый ключ теперь хранит ID
        legacySelectedChild = selectedChildId
    }
}

// MARK: - Automated Rules Modal

struct AutomatedRulesModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    let ageGroup: FamilyParentalControlSettingsModal.AgeGroup
    var onRulesChanged: (() -> Void)? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для правил
    @State private var showAgeBasedFilteringExplanation = false
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_auto_rules_modal_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Toggle включения правил
                FamilyContentBlockItem(
                    icon: "🤖",
                    title: localizationManager.localized("family_auto_rules_title"),
                    description: isEnabled ? localizationManager.localized("family_auto_rules_enabled_desc") : localizationManager.localized("family_auto_rules_disabled_desc"),
                    isEnabled: $isEnabled
                )
                .onChange(of: isEnabled) { newValue in
                    // Применяем правила при изменении toggle
                    print("✅ AutomatedRulesModal: rules \(newValue ? "ENABLED" : "DISABLED")")
                    VisualLogger.shared.log(
                        "🔄 automated_rules_modal_enabled = \(newValue)",
                        level: .info,
                        category: "PARENTAL.UI"
                    )
                    if newValue {
                        onRulesChanged?()
                    }
                }
                
                if isEnabled {
                    Divider()
                        .background(Color.white.opacity(0.2))
                        .padding(.vertical, Spacing.s)
                    
                    // Правило 1: Фильтрация контента по возрасту (с объяснением)
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(localizationManager.localized("family_content_filtering"))
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Button(action: {
                                HapticFeedback.impact(.light)
                                showAgeBasedFilteringExplanation.toggle()
                            }) {
                                Image(systemName: showAgeBasedFilteringExplanation ? "chevron.up" : "chevron.down")
                                    .font(.system(size: 14))
                                    .foregroundColor(.secondaryGold)
                            }
                        }
                        
                        if showAgeBasedFilteringExplanation {
                            ageBasedFilteringExplanation
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .onAppear {
            // Логируем текущее состояние при открытии
            print("✅ AutomatedRulesModal opened: age group \(ageGroup.rawValue), rules state \(isEnabled ? "ON" : "OFF")")
            VisualLogger.shared.log(
                "⚙️ AutomatedRulesModal opened age=\(ageGroup.rawValue) enabled=\(isEnabled)",
                level: .info,
                category: "PARENTAL.UI"
            )
        }
        .withVisualLogger()
    }
    
    private var ageBasedFilteringExplanation: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.xs)
            
            switch ageGroup {
            case .toddler:
                Text(localizationManager.localized("family_for_1_6"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_rules_1_6_youtube"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_1_6_cartoons"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_1_6_games"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_1_6_social"))
                         .font(.caption)
                         .foregroundColor(.dangerRed)
                    Text(localizationManager.localized("family_rules_1_6_messengers"))
                         .font(.caption)
                         .foregroundColor(.dangerRed)
                }
                .font(.caption)
                .foregroundColor(.textSecondary)
                
            case .school:
                Text(localizationManager.localized("family_for_7_13"))
                     .font(.bodyBold)
                     .foregroundColor(.secondaryGold)
                 
                 VStack(alignment: .leading, spacing: 4) {
                     Text(localizationManager.localized("family_rules_7_13_youtube"))
                          .font(.caption)
                          .foregroundColor(.textSecondary)
                     Text(localizationManager.localized("family_rules_7_13_cartoons"))
                          .font(.caption)
                          .foregroundColor(.textSecondary)
                     Text(localizationManager.localized("family_rules_7_13_games"))
                          .font(.caption)
                          .foregroundColor(.textSecondary)
                     Text(localizationManager.localized("family_rules_7_13_social"))
                          .font(.caption)
                          .foregroundColor(.dangerRed)
                     Text(localizationManager.localized("family_rules_7_13_messengers"))
                          .font(.caption)
                          .foregroundColor(.successGreen)
                  }

            case .teen:
                Text(localizationManager.localized("family_for_14_17"))
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("family_rules_14_17_youtube"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_14_17_cartoons"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_14_17_games"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_14_17_social"))
                         .font(.caption)
                         .foregroundColor(.successGreen)
                    Text(localizationManager.localized("family_rules_14_17_messengers"))
                         .font(.caption)
                         .foregroundColor(.successGreen)
                 }

            case .adult:
                Text(localizationManager.localized("family_for_18_plus"))
                    .font(.bodyBold)
                    .foregroundColor(.successGreen)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("family_rules_18_youtube"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_18_cartoons"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_18_games"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_18_social"))
                         .font(.caption)
                         .foregroundColor(.successGreen)
                    Text(localizationManager.localized("family_rules_18_messengers"))
                         .font(.caption)
                         .foregroundColor(.successGreen)
                 }
            }
        }
        .padding(.top, Spacing.xs)
    }
}

// MARK: - Family Member Data Model

// FamilyMemberData moved to global APIModels.swift

// Codable Extensions removed

// MARK: - Family Bypass Protection Modal

struct FamilyBypassProtectionModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Manager для обработки защиты от обхода
    @ObservedObject private var manager = ParentalControlManager.shared
    // Manager для включения/выключения Smart DNS профиля
    @ObservedObject private var dnsProtectionManager = DNSProtectionManager.shared
    
    // Выбранный ребёнок (новый ID + legacy fallback)
    @AppStorage("parental_selected_child_id") private var selectedChildId: String = ""
    @AppStorage("parental_selected_child") private var legacySelectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Состояния для 3 переключателей с сохранением в UserDefaults
    @AppStorage("bypass_incognito_enabled") private var isIncognitoDetectionEnabled: Bool = true
    @AppStorage("bypass_tor_enabled") private var isTorDetectionEnabled: Bool = true
    @AppStorage("bypass_proxy_enabled") private var isProxyDetectionEnabled: Bool = true
    
    // Статистика
    @State private var attemptsToday: Int = 0
    @State private var attemptsWeek: Int = 0
    @State private var attemptsBlocked: Int = 0
    
    // Детализация по типам
    @State private var incognitoAttempts: Int = 0
    @State private var torAttempts: Int = 0
    @State private var proxyAttempts: Int = 0
    
    private var effectiveChildId: String {
        if !selectedChildId.isEmpty { return selectedChildId }
        return legacySelectedChild
    }

    private var smartDNSOffReason: String {
        if effectiveChildId.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            return "Нет выбранного ребёнка"
        }

        let error = (dnsProtectionManager.lastError ?? "").lowercased()
        if error.contains("конфигурация dns пуста") || error.contains("ошибка получения конфига") {
            return "Нет DNS-конфига с сервера"
        }
        if error.contains("не удалось сохранить профиль ios") || error.contains("savetopreferences") {
            return "Не удалось сохранить профиль iOS"
        }
        return "Не удалось активировать Smart DNS"
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("bypass_protection_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Incognito detection toggle
                FamilyContentBlockItem(
                    icon: "🕶️",
                    title: localizationManager.localized("bypass_incognito_detection"),
                    description: localizationManager.localized("bypass_incognito_desc"),
                    isEnabled: $isIncognitoDetectionEnabled
                )
                
                // 2. Детекция Tor
                FamilyContentBlockItem(
                    icon: "🧅",
                    title: localizationManager.localized("bypass_tor_detection"),
                    description: localizationManager.localized("bypass_tor_desc"),
                    isEnabled: $isTorDetectionEnabled
                )
                
                // 3. Детекция Proxy
                FamilyContentBlockItem(
                    icon: "🔀",
                    title: localizationManager.localized("bypass_proxy_detection"),
                    description: localizationManager.localized("bypass_proxy_desc"),
                    isEnabled: $isProxyDetectionEnabled
                )
                
                // 4. Smart DNS enable/disable (ниже детекторов)
                FamilyContentBlockItem(
                    icon: "🌐",
                    title: "Smart DNS",
                    description: dnsProtectionManager.isEnabled
                        ? localizationManager.localized("parental_dns_status_active")
                        : localizationManager.localized("parental_dns_status_inactive"),
                    isEnabled: Binding(
                        get: { dnsProtectionManager.isEnabled },
                        set: { newValue in
                            if newValue {
                                // В FamilyScreen для выбранного ребёнка обычно хранится имя,
                                // а не UUID childId. DNSConfig принимает childId, только если он корректный UUID.
                                let childId: String? = effectiveChildId.isEmpty ? nil : effectiveChildId
                                dnsProtectionManager.enableProtection(childId: childId)
                            } else {
                                dnsProtectionManager.disableProtection()
                            }
                        }
                    )
                )
                
                if !dnsProtectionManager.isEnabled {
                    HStack {
                        Text("Причина OFF: \(smartDNSOffReason)")
                            .font(.caption)
                            .foregroundColor(.warningOrange)
                        Spacer()
                    }
                    .padding(.horizontal, Spacing.m)
                }

                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("bypass_stats_week"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    HStack(spacing: Spacing.m) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(localizationManager.localized("bypass_attempts_today"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text("\(attemptsToday)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                    }
                    
                    HStack {
                        Text(localizationManager.localized("bypass_blocked"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(attemptsBlocked)")
                            .font(.bodyBold)
                            .foregroundColor(.successGreen)
                    }
                    
                    // Детализация по типам (с заменой названий)
                    VStack(spacing: Spacing.xs) {
                        HStack {
                            Text(localizationManager.localized("bypass_incognito_type"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(incognitoAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("bypass_tor_type"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(torAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("bypass_proxy_type"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(proxyAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                    }
                    .padding(.top, Spacing.s)

                    // Статистика за неделю — ниже детального блока
                    HStack {
                        Text(localizationManager.localized("bypass_attempts_week"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(attemptsWeek)")
                            .font(.bodyBold)
                            .foregroundColor(.warningOrange)
                    }
                    .padding(.top, Spacing.xs)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .id("bypass_protection_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadBypassStatistics()
            dnsProtectionManager.loadStatus()
        }
        .onChange(of: selectedChildId) { _ in
            loadBypassStatistics()
            dnsProtectionManager.loadStatus()
        }
        .onChange(of: isIncognitoDetectionEnabled) { newValue in
            VisualLogger.shared.log(
                "🔄 bypass_incognito_enabled = \(newValue)",
                level: .info,
                category: "PARENTAL.UI"
            )
            applyBypassProtection()
        }
        .onChange(of: isTorDetectionEnabled) { newValue in
            VisualLogger.shared.log(
                "🔄 bypass_tor_enabled = \(newValue)",
                level: .info,
                category: "PARENTAL.UI"
            )
            applyBypassProtection()
        }
        .onChange(of: isProxyDetectionEnabled) { newValue in
            VisualLogger.shared.log(
                "🔄 bypass_proxy_enabled = \(newValue)",
                level: .info,
                category: "PARENTAL.UI"
            )
            applyBypassProtection()
        }
        .withVisualLogger()
    }
    
    private func loadBypassStatistics() {
        // Загружаем статистику из API через manager
        manager.getBypassStats(childId: effectiveChildId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let stats):
                    self.attemptsToday = stats.today
                    self.attemptsWeek = stats.week
                    self.attemptsBlocked = stats.blocked
                    self.incognitoAttempts = stats.incognito
                    self.torAttempts = stats.tor
                    self.proxyAttempts = stats.proxy
                case .failure(let error):
                    print("⚠️ Failed to load bypass statistics: \(error.localizedDescription)")
                    let local = manager.localBypassAggregates(
                        for: effectiveChildId.isEmpty ? nil : effectiveChildId
                    )
                    attemptsToday = local.today
                    attemptsWeek = local.week
                    attemptsBlocked = local.blocked
                    incognitoAttempts = local.incognito
                    torAttempts = local.tor
                    proxyAttempts = local.proxy
                }
            }
        }
    }
    
    private func applyBypassProtection() {
        // Применяем настройки защиты от обхода через API
        manager.applyBypassProtection(
            childId: effectiveChildId,
            incognito: isIncognitoDetectionEnabled,
            tor: isTorDetectionEnabled,
            proxy: isProxyDetectionEnabled
        ) { success, errorMessage in
            DispatchQueue.main.async {
                if success {
                    print("✅ Bypass protection applied: Incognito=\(self.isIncognitoDetectionEnabled), Tor=\(self.isTorDetectionEnabled), Proxy=\(self.isProxyDetectionEnabled)")
                    // Обновляем статистику после применения
                    self.loadBypassStatistics()
                } else {
                    print("❌ Failed to apply bypass protection: \(errorMessage ?? "Unknown error")")
                }
            }
        }
    }
}

struct FamilyRolesHelpView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationView {
            ScrollView {
                let ru = localizationManager.currentLanguage == .russian
                VStack(alignment: .leading, spacing: 14) {
                    Text(ru ? "Apple Family Sharing не равен профилям ALADDIN." : "Apple Family Sharing is different from ALADDIN app profiles.")
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    Text(ru
                         ? "В ALADDIN роли (parent/elderly/child/teen) определяют, кто может менять состав семьи, лимиты и чувствительные настройки внутри приложения."
                         : "In ALADDIN, roles (parent/elderly/child/teen) define who can manage roster, limits, and sensitive settings inside the app.")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Text(ru
                         ? "Family Sharing в iOS отвечает за покупки, подписки и Ask to Buy на уровне Apple ID, но не заменяет app-level permissions ALADDIN."
                         : "iOS Family Sharing controls purchases, subscriptions, and Ask to Buy at Apple ID level, but does not replace ALADDIN app-level permissions.")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
                .padding(Spacing.m)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationTitle(localizationManager.currentLanguage == .russian ? "Роли и профили" : "Roles & Profiles")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.currentLanguage == .russian ? "Готово" : "Done") { dismiss() }
                }
            }
        }
    }
}

struct FamilyScreen_Previews: PreviewProvider {
    static var previews: some View {
        FamilyScreen()
    }
}
