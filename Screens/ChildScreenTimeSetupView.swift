import SwiftUI
import FamilyControls

/// Guided setup on the **child** device (PROD decision P-PICKER=A):
/// Auth → FamilyActivityPicker → persist selection in App Group → start Monitor.
struct ChildScreenTimeSetupView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var selection = FamilyActivitySelection()
    @State private var isPickerPresented = false
    @State private var statusMessage = ""
    @State private var isBusy = false

    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.m) {
                Text(localizationManager.localized("screen_time_child_setup_title"))
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)

                Text(localizationManager.localized("screen_time_child_setup_body"))
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)

                if !statusMessage.isEmpty {
                    Text(statusMessage)
                        .font(.caption)
                        .foregroundColor(.secondaryGold)
                        .multilineTextAlignment(.center)
                }

                Button {
                    Task { await authorizeAndPick() }
                } label: {
                    Text(localizationManager.localized("screen_time_child_setup_cta"))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .disabled(isBusy || !AppStoreBuildPolicy.allowsSystemFamilyControls)
                .padding(.top, Spacing.s)

                if !AppStoreBuildPolicy.allowsSystemFamilyControls {
                    Text(localizationManager.localized("screen_time_unavailable_in_build"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }

                Spacer()
            }
            .padding(Spacing.l)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("common_close")) { dismiss() }
                }
            }
            .familyActivityPicker(isPresented: $isPickerPresented, selection: $selection)
            .onChange(of: isPickerPresented) { presented in
                if !presented {
                    Task { await persistSelectionAndStart() }
                }
            }
        }
    }

    private func authorizeAndPick() async {
        isBusy = true
        defer { isBusy = false }
        do {
            try await ParentalControlManager.shared.requestFamilyAuthorization()
            await MainActor.run {
                isPickerPresented = true
                statusMessage = localizationManager.localized("screen_time_child_setup_pick_apps")
            }
        } catch {
            await MainActor.run {
                statusMessage = error.localizedDescription
            }
        }
    }

    private func persistSelectionAndStart() async {
        guard AppStoreBuildPolicy.allowsSystemFamilyControls else { return }
        do {
            let data = try PropertyListEncoder().encode(selection)
            let defaults = UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId) ?? .standard
            defaults.set(data, forKey: ScreenTimeUsageStore.selectionKey)
            ScreenTimeAppLimitsBridge.bindSelection(selection)

            _ = await ParentalControlManager.shared.applyFamilyControlsPipelineIfPossible()

            let familyId = FamilyLocalStore.loadPersistedFamilyId()
            let memberId = [
                UserDefaults.standard.string(forKey: "your_member_id"),
                UserDefaults.standard.string(forKey: "active_child_profile_server_id"),
                UserDefaults.standard.string(forKey: "user_id")
            ]
            .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .first { !$0.isEmpty } ?? ""

            _ = ScreenTimeUsageStore.upsertToday(
                familyId: familyId,
                memberId: memberId,
                totalSeconds: 0,
                apps: []
            )
            _ = await ScreenTimeUsageSync.postIfChild()

            await MainActor.run {
                statusMessage = localizationManager.localized("screen_time_child_setup_done")
            }
        } catch {
            await MainActor.run {
                statusMessage = error.localizedDescription
            }
        }
    }
}
