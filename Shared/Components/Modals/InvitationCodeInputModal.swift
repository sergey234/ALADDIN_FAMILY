import SwiftUI
import UIKit

/**
 * Invitation Code Input Modal — join existing family (hybrid name, no letter step).
 * Dark family chrome; role + age + display name (RU/EN).
 */

struct InvitationCodeInputModal: View {

    @Binding var isPresented: Bool
    let initialCode: String?
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager

    @State private var code: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @State private var preflightMessage: String?
    @State private var rawInvitePayload: String?
    @State private var selectedRole: FamilyRole?
    @State private var selectedAgeGroup: AgeGroup?
    @State private var displayName: String = ""
    @State private var roleExpanded = true
    @State private var ageExpanded = false
    @State private var joinPollAttempts: Int = 0
    @State private var autoBindState: CurrentDeviceAutoBindState = .idle
    @State private var autoBindMessage: String?

    init(isPresented: Binding<Bool>, initialCode: String? = nil) {
        self._isPresented = isPresented
        self.initialCode = initialCode
    }

    @StateObject private var registrationVM = FamilyRegistrationViewModel()
    private let apiService = APIService.shared

    private let panelBg = Color.white.opacity(0.10)
    private let fieldBg = Color.white.opacity(0.12)
    private let textPrimary = Color.white
    private let textSecondary = Color.white.opacity(0.72)

    var body: some View {
        NavigationView {
            scrollContent
                .background(joinBackground.ignoresSafeArea())
                .navigationTitle(localizationManager.localized("invitation_join_navigation_title"))
                .navigationBarTitleDisplayMode(.inline)
                .navigationBarItems(
                    leading: Button(localizationManager.localized("common_cancel")) {
                        dismissInvitationFlow()
                    }
                    .foregroundColor(.white)
                )
        }
        .navigationViewStyle(StackNavigationViewStyle())
        .compatibleToolbarColorScheme(.dark, forNavigationBar: true)
        .onAppear {
            seedInviteFromNavigationOrInitial()
            preflightInviteIfPossible()
        }
    }

    private var joinBackground: some View {
        LinearGradient(
            colors: [
                Color(red: 0.04, green: 0.06, blue: 0.12),
                Color(red: 0.08, green: 0.12, blue: 0.22)
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }

    private var scrollContent: some View {
        ScrollView {
            VStack(spacing: 20) {
                headerBlock
                codeBlock
                profileBlock
                joinButton
                if autoBindState != .idle {
                    autoBindStatusCard
                }
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 28)
        }
    }

    private var codeFieldBorderColor: Color {
        if code.isEmpty {
            return Color.white.opacity(0.15)
        }
        return isInviteCodeValid ? Color.green : Color.red.opacity(0.85)
    }

    /// Accepts FAM-XXXX display codes and QR JSON payloads already parsed into `code`.
    private var isInviteCodeValid: Bool {
        if code.isValidRecoveryCode { return true }
        return FamilyInviteCodeParser.parse(rawInvitePayload ?? code) != nil
    }

    private var headerBlock: some View {
        VStack(spacing: 10) {
            Image(systemName: "person.3.fill")
                .font(.system(size: 40))
                .foregroundColor(Color(red: 0.35, green: 0.78, blue: 0.55))
                .padding(.top, 12)

            Text(localizationManager.localized("invitation_code_enter_title"))
                .font(AladdinFamilyType.title2())
                .foregroundColor(textPrimary)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)

            Text(localizationManager.localized("invitation_code_enter_subtitle"))
                .font(AladdinFamilyType.subheadline())
                .foregroundColor(textSecondary)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)

            Text(localizationManager.localized("invitation_code_family_hint"))
                .font(AladdinFamilyType.caption())
                .foregroundColor(textSecondary)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private var codeBlock: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(localizationManager.localized("invitation_code_field_label"))
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(textSecondary)
                Spacer()
                Button(localizationManager.localized("invitation_paste_code_button")) {
                    if let pasted = UIPasteboard.general.string {
                        applyInviteInput(pasted)
                    }
                }
                .font(.caption.weight(.semibold))
                .foregroundColor(Color(red: 0.45, green: 0.85, blue: 0.60))
            }

            TextField("FAM-XXXX-XXXX-XXXX", text: $code)
                .font(.system(size: 16, weight: .medium, design: .monospaced))
                .foregroundColor(textPrimary)
                .padding(16)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(fieldBg)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(codeFieldBorderColor, lineWidth: 2)
                        )
                )
                .autocapitalization(.allCharacters)
                .disableAutocorrection(true)
                .onChange(of: code) { newValue in
                    errorMessage = nil
                    applyInviteInput(newValue)
                }

            statusLines
        }
    }

    @ViewBuilder
    private var statusLines: some View {
        if let error = errorMessage {
            Text(error)
                .font(.caption)
                .foregroundColor(Color(red: 1.0, green: 0.45, blue: 0.45))
                .fixedSize(horizontal: false, vertical: true)
                .padding(.horizontal, 4)
        } else if let preflight = preflightMessage {
            Text(preflight)
                .font(.caption)
                .foregroundColor(Color(red: 0.45, green: 0.85, blue: 0.60))
                .fixedSize(horizontal: false, vertical: true)
                .padding(.horizontal, 4)
        } else if isLikelyDevicePin(code) {
            Text(localizationManager.localized("family_invite_wrong_flow_device_code"))
                .font(.caption)
                .foregroundColor(.orange)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.horizontal, 4)
        } else if !code.isEmpty && !isInviteCodeValid {
            Text(localizationManager.localized("invitation_code_format_hint"))
                .font(.caption)
                .foregroundColor(textSecondary)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.horizontal, 4)
        }
    }

    private var profileBlock: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(localizationManager.localized("invitation_profile_section_title"))
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(textSecondary)

            accordionHeader(
                step: "1",
                title: localizationManager.localized("invitation_role_picker_label"),
                subtitle: selectedRole.map(roleTitle) ?? localizationManager.localized("invitation_picker_placeholder"),
                expanded: roleExpanded
            ) {
                roleExpanded.toggle()
                if roleExpanded { ageExpanded = false }
            }
            if roleExpanded {
                VStack(spacing: 8) {
                    ForEach(FamilyRole.selectableRoles) { role in
                        choiceRow(title: roleTitle(role), selected: selectedRole == role) {
                            selectedRole = role
                            errorMessage = nil
                            roleExpanded = false
                            ageExpanded = true
                        }
                    }
                }
            }

            accordionHeader(
                step: "2",
                title: localizationManager.localized("invitation_age_picker_label"),
                subtitle: selectedAgeGroup.map(ageTitle) ?? localizationManager.localized("invitation_picker_placeholder"),
                expanded: ageExpanded
            ) {
                ageExpanded.toggle()
                if ageExpanded { roleExpanded = false }
            }
            if ageExpanded {
                VStack(spacing: 8) {
                    ForEach(AgeGroup.allCases) { age in
                        choiceRow(title: ageTitle(age), selected: selectedAgeGroup == age) {
                            selectedAgeGroup = age
                            errorMessage = nil
                            ageExpanded = false
                        }
                    }
                }
            }

            VStack(alignment: .leading, spacing: 8) {
                Text("3 · " + localizationManager.localized("invitation_display_name_label"))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(textPrimary)
                Text(localizationManager.localized("invitation_display_name_hint"))
                    .font(.caption)
                    .foregroundColor(textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
                TextField(localizationManager.localized("invitation_display_name_placeholder"), text: $displayName)
                    .font(AladdinFamilyType.body())
                    .foregroundColor(textPrimary)
                    .padding(14)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(fieldBg)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.white.opacity(0.18), lineWidth: 1)
                            )
                    )
                    .disableAutocorrection(true)
                    .onChange(of: displayName) { _ in
                        errorMessage = nil
                    }
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(panelBg)
        )
    }

    private func accordionHeader(step: String, title: String, subtitle: String, expanded: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack {
                Text("\(step) · \(title)")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(textPrimary)
                Spacer()
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundColor(textSecondary)
                    .lineLimit(1)
                Image(systemName: expanded ? "chevron.up" : "chevron.down")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(textSecondary)
            }
            .padding(.vertical, 6)
        }
        .buttonStyle(.plain)
    }

    private func choiceRow(title: String, selected: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack {
                Text(title)
                    .foregroundColor(textPrimary)
                Spacer()
                if selected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(Color(red: 0.45, green: 0.85, blue: 0.60))
                }
            }
            .padding(12)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(selected ? Color.white.opacity(0.16) : Color.white.opacity(0.06))
            )
        }
        .buttonStyle(.plain)
    }

    private var joinButton: some View {
        Button(action: { joinFamily() }) {
            HStack {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    Text(localizationManager.localized("invitation_join_family_button"))
                        .font(.system(size: 16, weight: .semibold))
                }
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(canSubmit ? Color.green : Color.gray.opacity(0.55))
            )
        }
        .disabled(!canSubmit)
    }

    private enum CurrentDeviceAutoBindState: Equatable {
        case idle
        case binding
        case bound
        case failed
    }

    private var normalizedDisplayName: String {
        displayName
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .replacingOccurrences(of: "\\s+", with: " ", options: .regularExpression)
    }

    private var isDisplayNameValid: Bool {
        let n = normalizedDisplayName
        guard n.count >= 2, n.count <= 24 else { return false }
        return n.unicodeScalars.allSatisfy { scalar in
            CharacterSet.letters.contains(scalar)
                || CharacterSet.whitespaces.contains(scalar)
                || scalar == "-"
        }
    }

    private var canSubmit: Bool {
        isInviteCodeValid &&
        selectedRole != nil &&
        selectedAgeGroup != nil &&
        isDisplayNameValid &&
        !isLoading &&
        autoBindState == .idle
    }

    @ViewBuilder
    private var autoBindStatusCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 10) {
                if autoBindState == .binding {
                    ProgressView()
                } else {
                    Image(systemName: autoBindState == .bound ? "checkmark.circle.fill" : "exclamationmark.triangle.fill")
                        .foregroundColor(autoBindState == .bound ? .green : .orange)
                }
                Text(autoBindMessage ?? localizationManager.localized("family_join_autobind_progress"))
                    .font(.subheadline)
                    .foregroundColor(textPrimary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            if autoBindState == .bound {
                Button(localizationManager.localized("common_done")) {
                    dismissInvitationFlow()
                }
                .font(.caption.weight(.semibold))
                .foregroundColor(.green)
            } else if autoBindState == .failed {
                HStack(spacing: 12) {
                    Button(localizationManager.localized("family_join_autobind_manual_button")) {
                        dismissInvitationFlow()
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                            navigationManager.navigateTo(.joinDevice)
                        }
                    }
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.green)

                    Button(localizationManager.localized("family_join_autobind_skip_button")) {
                        dismissInvitationFlow()
                    }
                    .font(.caption.weight(.semibold))
                    .foregroundColor(textSecondary)
                }
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(panelBg)
        )
    }

    private func seedInviteFromNavigationOrInitial() {
        if let pendingPayload = navigationManager.pendingFamilyInvitePayload,
           let invite = FamilyInviteCodeParser.parse(pendingPayload) {
            rawInvitePayload = pendingPayload
            code = invite.displayCode
            navigationManager.pendingFamilyInvitePayload = nil
            navigationManager.pendingFamilyInviteCode = nil
        } else if let pendingCode = navigationManager.pendingFamilyInviteCode,
                  let invite = FamilyInviteCodeParser.parse(pendingCode) {
            rawInvitePayload = pendingCode
            code = invite.displayCode
            navigationManager.pendingFamilyInviteCode = nil
        } else if let initialCode = initialCode,
                  let invite = FamilyInviteCodeParser.parse(initialCode) {
            rawInvitePayload = initialCode
            code = invite.displayCode
        }
    }

    private func isLikelyDevicePin(_ value: String) -> Bool {
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.count == 6 && trimmed.allSatisfy { $0.isNumber }
    }

    private func dismissInvitationFlow() {
        if navigationManager.currentScreen == .invitationCode {
            navigationManager.goBack(reason: "invitation_code_cancel")
        } else {
            isPresented = false
        }
    }

    private func applyInviteInput(_ raw: String) {
        guard !raw.isEmpty else {
            rawInvitePayload = nil
            preflightMessage = nil
            return
        }
        guard let invite = FamilyInviteCodeParser.parse(raw) else { return }
        if raw == code, rawInvitePayload != nil, invite.displayCode == code {
            return
        }
        rawInvitePayload = raw
        if code != invite.displayCode {
            code = invite.displayCode
        }
        preflightMessage = nil
        preflightInviteIfPossible()
    }

    private func joinFamily() {
        guard isInviteCodeValid else {
            errorMessage = localizationManager.localized("invitation_invalid_code")
            return
        }
        guard let role = selectedRole,
              let ageGroup = selectedAgeGroup else {
            errorMessage = localizationManager.localized("invitation_join_profile_required")
            return
        }
        guard isDisplayNameValid else {
            errorMessage = localizationManager.localized("invitation_display_name_invalid")
            return
        }

        let name = normalizedDisplayName
        isLoading = true
        joinPollAttempts = 0
        errorMessage = nil
        preflightMessage = nil

        registrationVM.selectedRole = role
        registrationVM.selectedAgeGroup = ageGroup
        registrationVM.selectedDisplayName = name

        guard let invitePayload = FamilyInviteCodeParser.parse(rawInvitePayload ?? code) else {
            isLoading = false
            errorMessage = localizationManager.localized("invitation_invalid_code")
            return
        }

        let preflightRequest = FamilyInvitePreflightRequest(
            family_id: invitePayload.familyId,
            invite_code: invitePayload.displayCode,
            invite_token: invitePayload.inviteToken
        )

        apiService.preflightFamilyInvite(request: preflightRequest) { result in
            DispatchQueue.main.async {
                switch result {
                case .success:
                    self.preflightMessage = self.localizationManager.localized("invitation_code_preflight_ok")
                    self.registrationVM.joinFamily(withCode: self.rawInvitePayload ?? self.code)
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                        self.checkJoinStatus()
                    }
                case .failure(let error):
                    self.isLoading = false
                    self.errorMessage = self.humanizedJoinError(error)
                }
            }
        }
    }

    private func preflightInviteIfPossible() {
        guard let invitePayload = FamilyInviteCodeParser.parse(rawInvitePayload ?? code) else { return }
        let request = FamilyInvitePreflightRequest(
            family_id: invitePayload.familyId,
            invite_code: invitePayload.displayCode,
            invite_token: invitePayload.inviteToken
        )
        apiService.preflightFamilyInvite(request: request) { result in
            DispatchQueue.main.async {
                switch result {
                case .success:
                    self.preflightMessage = self.localizationManager.localized("invitation_code_preflight_ok")
                    self.errorMessage = nil
                case .failure(let error):
                    self.preflightMessage = nil
                    self.errorMessage = self.humanizedJoinError(error)
                }
            }
        }
    }

    private func humanizedJoinError(_ error: Error) -> String {
        if let networkError = error as? NetworkError {
            let text = networkError.localizedDescription
            if text.lowercased().contains("not found") || text.contains("Не найдено") {
                return localizationManager.localized("invitation_code_not_found_friendly")
            }
            return text
        }
        let text = error.localizedDescription
        if text.lowercased().contains("not found") {
            return localizationManager.localized("invitation_code_not_found_friendly")
        }
        return text
    }

    private func checkJoinStatus() {
        if registrationVM.isLoading {
            joinPollAttempts += 1
            if joinPollAttempts >= 20 {
                registrationVM.isLoading = false
                isLoading = false
                errorMessage = localizationManager.localized("invitation_join_family_failed")
                return
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                self.checkJoinStatus()
            }
            return
        }

        if let error = registrationVM.errorMessage {
            self.errorMessage = error
            self.isLoading = false
        } else if registrationVM.familyID != nil {
            self.isLoading = false
            if let fid = registrationVM.familyID {
                FamilyLocalStore.resetPersistedCachesIfFamilyChanged(newFamilyId: fid)
                FamilyLocalStore.persistFamilyId(fid)
            }
            FamilyLocalStore.notifyFamilyMembersUpdated()
            autoBindCurrentDeviceAfterJoin()
        } else {
            self.isLoading = false
            self.errorMessage = localizationManager.localized("invitation_join_family_failed")
        }
    }

    private func autoBindCurrentDeviceAfterJoin() {
        guard autoBindState == .idle else { return }
        guard let memberId = joinedMemberIdForDeviceBind() else {
            autoBindState = .failed
            autoBindMessage = localizationManager.localized("family_join_autobind_missing_member")
            return
        }

        let roleLabel = selectedRole.map(roleTitle) ?? localizationManager.localized("family_role_child_label")
        let modelName = DeviceMarketingName.displayName()
        let deviceType = currentDeviceType()
        autoBindState = .binding
        autoBindMessage = localizationManager.localized("family_join_autobind_progress")

        apiService.addDevice(
            name: DeviceMarketingName.modelPlusRole(roleLabel: roleLabel),
            type: deviceType,
            owner: roleLabel,
            ownerMemberId: memberId,
            modelName: modelName
        ) { result in
            DispatchQueue.main.async {
                switch result {
                case .success:
                    FamilyLocalStore.notifyFamilyMembersUpdated()
                    NotificationCenter.default.post(name: NSNotification.Name("FamilyDevicesDidChange"), object: nil)
                    self.autoBindState = .bound
                    self.autoBindMessage = self.localizationManager.localized("family_join_autobind_success")
                case .failure:
                    self.autoBindState = .failed
                    self.autoBindMessage = self.localizationManager.localized("family_join_autobind_failed")
                }
            }
        }
    }

    private func joinedMemberIdForDeviceBind() -> String? {
        let candidate = registrationVM.lastJoinedMemberId ?? UserDefaults.standard.string(forKey: "your_member_id")
        let trimmed = candidate?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return trimmed.isEmpty ? nil : trimmed
    }

    private func currentDeviceType() -> String {
        UIDevice.current.userInterfaceIdiom == .pad ? "ipad" : "iphone"
    }

    private func roleTitle(_ role: FamilyRole) -> String {
        switch role {
        case .parent: return localizationManager.localized("family_role_parent_label")
        case .child: return localizationManager.localized("family_role_child_label")
        case .teenager: return localizationManager.localized("family_role_teen_label")
        case .elderly: return localizationManager.localized("family_role_elderly_label")
        }
    }

    private func ageTitle(_ age: AgeGroup) -> String {
        switch age {
        case .toddler: return localizationManager.localized("invitation_age_toddler")
        case .child: return localizationManager.localized("invitation_age_child")
        case .teen: return localizationManager.localized("invitation_age_teen")
        case .adult: return localizationManager.localized("invitation_age_adult")
        case .senior: return localizationManager.localized("invitation_age_senior")
        }
    }
}

// MARK: - FAM display-code format (restored — missing after hybrid rewrite)

extension String {
    /// `FAM-XXXX-XXXX-XXXX` (letters/digits). Used by join UI border + submit gate.
    var isValidRecoveryCode: Bool {
        let pattern = #"^FAM-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$"#
        return range(of: pattern, options: .regularExpression) != nil
    }
}
