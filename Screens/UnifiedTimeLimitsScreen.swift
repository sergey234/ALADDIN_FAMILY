import SwiftUI

/// W3-3: Single place for ALADDIN local screen-time cap (`TimeTracker`) and server `TimeLimitResponse`, plus sync status.
struct UnifiedTimeLimitsScreen: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var localLimitMinutes: Double = 60
    @State private var serverDailyMinutes: Int?
    @State private var serverBedtimeStart: String?
    @State private var serverBedtimeEnd: String?
    @State private var lastServerSync: Date?
    @State private var lastServerError: String?
    @State private var isLoadingServer = false
    @State private var isSavingServer = false
    @State private var childIdMissing = false
    @State private var pendingExtensionRequest: ChildTimeExtensionRequest?
    @State private var extensionRequestMessage: String?

    private let lastSyncDefaultsKey = "unified_time_limits_last_server_sync"
    private let lastErrorDefaultsKey = "unified_time_limits_last_server_error"

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    localSection
                    extensionRequestsSection
                    serverSection
                    syncSection
                }
                .padding()
            }
            .background(StormMeshBackground(variant: .shield))
            .navigationTitle(localizationManager.localized("unified_time_limits_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button(localizationManager.localized("child_interface_back")) {
                        dismiss()
                    }
                }
            }
            .onAppear {
                localLimitMinutes = Double(max(5, TimeTracker.shared.dailyLimitSec / 60))
                lastServerSync = UserDefaults.standard.object(forKey: lastSyncDefaultsKey) as? Date
                lastServerError = UserDefaults.standard.string(forKey: lastErrorDefaultsKey)
                pendingExtensionRequest = ChildTimeExtensionRequestStore.shared.pendingRequest()
                refreshFromServer()
            }
        }
    }

    private var activeChildId: String? {
        let raw = (UserDefaults.standard.string(forKey: "active_child_profile_server_id") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return raw.isEmpty ? nil : raw
    }

    private var localSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("unified_time_limits_local_section"))
                .font(.headline)
            Text(localizationManager.localized("unified_time_limits_local_hint"))
                .font(.caption)
                .foregroundColor(.secondary)
            HStack {
                Text(localizationManager.localized("unified_time_limits_local_minutes"))
                Spacer()
                Text("\(Int(localLimitMinutes))")
                    .fontWeight(.semibold)
            }
            Slider(value: $localLimitMinutes, in: 5...240, step: 5)
            HStack {
                Text(
                    localizationManager.localized(
                        "unified_time_limits_remaining_fmt",
                        TimeTracker.shared.remainingSecondsToday / 60
                    )
                )
                .font(.caption)
                Spacer()
            }
            Button(localizationManager.localized("unified_time_limits_apply_local")) {
                TimeTracker.shared.setDailyLimitMinutes(Int(localLimitMinutes))
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var serverSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("unified_time_limits_server_section"))
                .font(.headline)
            if childIdMissing {
                Text(localizationManager.localized("unified_time_limits_no_child"))
                    .font(.caption)
                    .foregroundColor(.orange)
            } else if isLoadingServer {
                ProgressView()
            } else if let err = lastServerError, serverDailyMinutes == nil {
                Text(localizationManager.localized("unified_time_limits_server_error_fmt", err))
                    .font(.caption)
                    .foregroundColor(.orange)
            } else {
                Text(
                    localizationManager.localized(
                        "unified_time_limits_server_daily_fmt",
                        serverDailyMinutes ?? 0
                    )
                )
                if let s = serverBedtimeStart, let e = serverBedtimeEnd, !s.isEmpty, !e.isEmpty {
                    Text(localizationManager.localized("unified_time_limits_server_bedtime_fmt", s, e))
                        .font(.caption)
                }
            }
        }
        .padding()
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var extensionRequestsSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("unified_time_limits_extension_requests_title"))
                .font(.headline)
            if let request = pendingExtensionRequest {
                Text(localizationManager.localized("unified_time_limits_extension_pending"))
                    .font(.caption)
                    .foregroundColor(.orange)
                Text(
                    localizationManager.localized(
                        "unified_time_limits_extension_details",
                        request.requestedExtraMinutes,
                        request.childId
                    )
                )
                .font(.caption)
                HStack(spacing: 12) {
                    Button(localizationManager.localized("unified_time_limits_extension_approve")) {
                        if let approved = ChildTimeExtensionRequestStore.shared.approvePendingRequest() {
                            localLimitMinutes = Double(max(5, TimeTracker.shared.dailyLimitSec / 60))
                            pendingExtensionRequest = nil
                            extensionRequestMessage = localizationManager.localized(
                                "unified_time_limits_extension_approved_message",
                                approved.requestedExtraMinutes
                            )
                        }
                    }
                    .buttonStyle(.borderedProminent)

                    Button(localizationManager.localized("unified_time_limits_extension_decline")) {
                        ChildTimeExtensionRequestStore.shared.clearPendingRequest()
                        pendingExtensionRequest = nil
                        extensionRequestMessage = localizationManager.localized("unified_time_limits_extension_declined_message")
                    }
                    .buttonStyle(.bordered)
                }
            } else {
                Text(localizationManager.localized("unified_time_limits_extension_none"))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            if let extensionRequestMessage, !extensionRequestMessage.isEmpty {
                Text(extensionRequestMessage)
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.9))
            }
        }
        .padding()
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var syncSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("unified_time_limits_sync_section"))
                .font(.headline)
            if let t = lastServerSync {
                Text(localizationManager.localized("unified_time_limits_last_sync_fmt", ISO8601DateFormatter().string(from: t)))
                    .font(.caption)
            } else {
                Text(localizationManager.localized("unified_time_limits_never_synced"))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            HStack(spacing: 12) {
                Button(localizationManager.localized("unified_time_limits_pull_server")) {
                    refreshFromServer()
                }
                .buttonStyle(.bordered)
                .disabled(isLoadingServer || childIdMissing)

                Button(localizationManager.localized("unified_time_limits_push_server")) {
                    pushToServer()
                }
                .buttonStyle(.borderedProminent)
                .disabled(isSavingServer || childIdMissing)
            }
        }
        .padding()
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private func refreshFromServer() {
        guard let cid = activeChildId else {
            childIdMissing = true
            return
        }
        childIdMissing = false
        isLoadingServer = true
        ParentalControlManager.shared.loadTimeLimitsFromServer(childId: cid) { result in
            DispatchQueue.main.async {
                isLoadingServer = false
                switch result {
                case .success(let resp):
                    if resp.dailyLimitMinutes > 0 {
                        serverDailyMinutes = resp.dailyLimitMinutes
                    } else {
                        serverDailyMinutes = nil
                    }
                    serverBedtimeStart = resp.bedtimeStart
                    serverBedtimeEnd = resp.bedtimeEnd
                    lastServerError = nil
                    let now = Date()
                    lastServerSync = now
                    UserDefaults.standard.set(now, forKey: lastSyncDefaultsKey)
                    UserDefaults.standard.removeObject(forKey: lastErrorDefaultsKey)
                case .failure(let err):
                    lastServerError = err.localizedDescription
                    UserDefaults.standard.set(err.localizedDescription, forKey: lastErrorDefaultsKey)
                }
            }
        }
    }

    private func pushToServer() {
        guard let cid = activeChildId else {
            childIdMissing = true
            return
        }
        isSavingServer = true
        let minutes = Int(localLimitMinutes)
        ParentalControlManager.shared.saveTimeLimitsToServer(
            childId: cid,
            dailyLimitMinutes: minutes,
            weeklyLimitMinutes: nil,
            bedtimeStart: serverBedtimeStart,
            bedtimeEnd: serverBedtimeEnd
        ) { result in
            DispatchQueue.main.async {
                isSavingServer = false
                switch result {
                case .success(let resp):
                    serverDailyMinutes = resp.dailyLimitMinutes > 0 ? resp.dailyLimitMinutes : minutes
                    let now = Date()
                    lastServerSync = now
                    lastServerError = nil
                    UserDefaults.standard.set(now, forKey: lastSyncDefaultsKey)
                    UserDefaults.standard.removeObject(forKey: lastErrorDefaultsKey)
                case .failure(let err):
                    lastServerError = err.localizedDescription
                    UserDefaults.standard.set(err.localizedDescription, forKey: lastErrorDefaultsKey)
                }
            }
        }
    }
}

#if DEBUG
struct UnifiedTimeLimitsScreen_Previews: PreviewProvider {
    static var previews: some View {
        UnifiedTimeLimitsScreen()
            .environmentObject(LocalizationManager.shared)
    }
}
#endif
