import SwiftUI
import UIKit

/**
 * 🔢 Invitation Code Input Modal
 * Модальное окно для ввода кода приглашения
 * 
 * Пользователь вводит Recovery Code: FAM-A1B2-C3D4-E5F6
 * Система распознаёт семью и присоединяет пользователя
 */

struct InvitationCodeInputModal: View {
    
    // MARK: - Properties
    
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
    @State private var selectedLetter: String?
    @State private var joinPollAttempts: Int = 0
    @State private var autoBindState: CurrentDeviceAutoBindState = .idle
    @State private var autoBindMessage: String?
    
    init(isPresented: Binding<Bool>, initialCode: String? = nil) {
        self._isPresented = isPresented
        self.initialCode = initialCode
    }
    
    // ViewModel для регистрации
    @StateObject private var registrationVM = FamilyRegistrationViewModel()
    private let apiService = APIService.shared
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Заголовок
                VStack(spacing: 8) {
                    Image(systemName: "textformat.123")
                        .font(.system(size: 50))
                        .foregroundColor(.green)
                    
                    Text(localizationManager.localized("invitation_code_enter_title"))
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.primary)
                    
                    Text(localizationManager.localized("invitation_code_enter_subtitle"))
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)

                    Text(localizationManager.localized("invitation_code_family_hint"))
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(.top, 20)
                
                // Поле ввода
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text(localizationManager.localized("invitation_code_field_label"))
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(.secondary)

                        Spacer()

                        Button(localizationManager.localized("invitation_paste_code_button")) {
                            if let pasted = UIPasteboard.general.string {
                                applyInviteInput(pasted)
                            }
                        }
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.green)
                    }
                    
                    TextField("FAM-XXXX-XXXX-XXXX", text: $code)
                        .font(.system(size: 16, weight: .medium, design: .monospaced))
                        .padding(16)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.gray.opacity(0.1))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(code.isEmpty ? Color.clear : (code.isValidRecoveryCode ? Color.green : Color.red), lineWidth: 2)
                                )
                        )
                        .autocapitalization(.allCharacters)
                        .disableAutocorrection(true)
                        .onChange(of: code) { newValue in
                            applyInviteInput(newValue)
                        }
                    
                    if let error = errorMessage {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                            .padding(.horizontal, 4)
                    } else if let preflight = preflightMessage {
                        Text(preflight)
                            .font(.caption)
                            .foregroundColor(.green)
                            .padding(.horizontal, 4)
                    } else if isLikelyDevicePin(code) {
                        Text(localizationManager.localized("family_invite_wrong_flow_device_code"))
                            .font(.caption)
                            .foregroundColor(.orange)
                            .padding(.horizontal, 4)
                    } else if !code.isEmpty && !code.isValidRecoveryCode {
                        Text(localizationManager.localized("invitation_code_format_hint"))
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .padding(.horizontal, 4)
                    }
                }
                
                VStack(alignment: .leading, spacing: 12) {
                    Text(localizationManager.localized("invitation_profile_section_title"))
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.secondary)

                    Picker(localizationManager.localized("invitation_role_picker_label"), selection: $selectedRole) {
                        Text(localizationManager.localized("invitation_picker_placeholder")).tag(Optional<FamilyRole>.none)
                        ForEach(FamilyRole.selectableRoles) { role in
                            Text(roleTitle(role)).tag(Optional(role))
                        }
                    }
                    .pickerStyle(.menu)

                    Picker(localizationManager.localized("invitation_age_picker_label"), selection: $selectedAgeGroup) {
                        Text(localizationManager.localized("invitation_picker_placeholder")).tag(Optional<AgeGroup>.none)
                        ForEach(AgeGroup.allCases) { age in
                            Text(ageTitle(age)).tag(Optional(age))
                        }
                    }
                    .pickerStyle(.menu)

                    Picker(localizationManager.localized("invitation_letter_picker_label"), selection: $selectedLetter) {
                        Text(localizationManager.localized("invitation_picker_placeholder")).tag(Optional<String>.none)
                        ForEach(Self.availableLetters, id: \.self) { letter in
                            Text(letter).tag(Optional(letter))
                        }
                    }
                    .pickerStyle(.menu)
                }
                .padding(16)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.gray.opacity(0.08))
                )

                // Кнопка присоединения
                Button(action: {
                    joinFamily()
                }) {
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
                            .fill(canSubmit ? Color.green : Color.gray)
                    )
                }
                .disabled(!canSubmit)

                if autoBindState != .idle {
                    autoBindStatusCard
                }
                
                Spacer()
            }
            .padding(.horizontal, 20)
            .navigationTitle(localizationManager.localized("invitation_join_navigation_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("common_cancel")) {
                        dismissInvitationFlow()
                    }
                }
            }
        }
        .onAppear {
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
            preflightInviteIfPossible()
        }
    }

    private static let availableLetters = (65...90).compactMap { UnicodeScalar($0).map(String.init) }

    private enum CurrentDeviceAutoBindState: Equatable {
        case idle
        case binding
        case bound
        case failed
    }

    private var canSubmit: Bool {
        code.isValidRecoveryCode &&
        selectedRole != nil &&
        selectedAgeGroup != nil &&
        selectedLetter != nil &&
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
                    .foregroundColor(.primary)
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
                    .foregroundColor(.secondary)
                }
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.gray.opacity(0.08))
        )
    }

    private func isLikelyDevicePin(_ value: String) -> Bool {
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.count == 6 && trimmed.allSatisfy { $0.isNumber }
    }

    /// При маршруте через `NavigationManager` (`.invitationCode` + `isPresented: .constant(true)`) binding не закрывает экран — нужен `goBack()`.
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
    }
    
    // MARK: - Join Family
    
    private func joinFamily() {
        guard code.isValidRecoveryCode else {
            errorMessage = localizationManager.localized("invitation_invalid_code")
            return
        }
        guard let role = selectedRole,
              let ageGroup = selectedAgeGroup,
              let letter = selectedLetter else {
            errorMessage = localizationManager.localized("invitation_join_profile_required")
            return
        }

        isLoading = true
        joinPollAttempts = 0
        errorMessage = nil
        preflightMessage = nil

        registrationVM.selectedRole = role
        registrationVM.selectedAgeGroup = ageGroup
        registrationVM.selectedLetter = letter

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
                    self.errorMessage = error.localizedDescription
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
                case .failure(let error):
                    self.preflightMessage = nil
                    self.errorMessage = error.localizedDescription
                }
            }
        }
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
            // Если все еще грузится, проверяем еще раз через секунду
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
                    autoBindState = .bound
                    autoBindMessage = localizationManager.localized("family_join_autobind_success")
                case .failure:
                    autoBindState = .failed
                    autoBindMessage = localizationManager.localized("family_join_autobind_failed")
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

// MARK: - String Extension

extension String {
    var isValidRecoveryCode: Bool {
        FamilyInviteCodeParser.parse(self)?.displayCode == self.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
    }
}

// MARK: - Preview

struct InvitationCodeInputModal_Previews: PreviewProvider {
    @State static var isPresented = true
    
    static var previews: some View {
        InvitationCodeInputModal(isPresented: $isPresented)
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager.shared)
    }
}
