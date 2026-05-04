import SwiftUI

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
    @State private var showRoleSelection: Bool = false
    
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
                }
                .padding(.top, 20)
                
                // Поле ввода
                VStack(alignment: .leading, spacing: 8) {
                    Text(localizationManager.localized("invitation_code_field_label"))
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.secondary)
                    
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
                    
                    if let error = errorMessage {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                            .padding(.horizontal, 4)
                    } else if !code.isEmpty && !code.isValidRecoveryCode {
                        Text(localizationManager.localized("invitation_code_format_hint"))
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .padding(.horizontal, 4)
                    }
                }
                
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
                            .fill(code.isValidRecoveryCode ? Color.green : Color.gray)
                    )
                }
                .disabled(code.isEmpty || !code.isValidRecoveryCode || isLoading)
                
                Spacer()
            }
            .padding(.horizontal, 20)
            .navigationTitle(localizationManager.localized("invitation_join_navigation_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        dismissInvitationFlow()
                    }
                }
            }
        }
        .sheet(isPresented: $showRoleSelection) {
            // TODO: Показывать выбор роли после успешной проверки кода
            Text(localizationManager.localized("invitation_role_selection_title"))
        }
        .onAppear {
            // Устанавливаем initialCode если он есть
            if let initialCode = initialCode {
                code = initialCode
            }
        }
    }

    /// При маршруте через `NavigationManager` (`.invitationCode` + `isPresented: .constant(true)`) binding не закрывает экран — нужен `goBack()`.
    private func dismissInvitationFlow() {
        if navigationManager.currentScreen == .invitationCode {
            navigationManager.goBack(reason: "invitation_code_cancel")
        } else {
            isPresented = false
        }
    }
    
    // MARK: - Join Family
    
    private func joinFamily() {
        guard code.isValidRecoveryCode else {
            errorMessage = "Неправильный формат кода"
            return
        }

        isLoading = true
        errorMessage = nil
        
        // Используем встроенный метод joinFamily вьюмодели, который обратится к POST /api/family/join
        registrationVM.joinFamily(withCode: code)
        
        // Ожидаем завершения (viewModel.isLoading станет false)
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.checkJoinStatus()
        }
    }
    
    private func checkJoinStatus() {
        if registrationVM.isLoading {
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
                UserDefaults.standard.set(fid, forKey: FamilyLocalStore.familyIdKey)
            }
            NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
            NotificationCenter.default.post(name: NSNotification.Name("MainFamilyStatsForceRefresh"), object: nil)
            dismissInvitationFlow()
        } else {
            self.isLoading = false
            self.errorMessage = "Не удалось присоединиться к семье"
        }
    }
}

// MARK: - String Extension

extension String {
    var isValidRecoveryCode: Bool {
        // Проверка формата: FAM-XXXX-XXXX-XXXX
        let pattern = #"^FAM-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$"#
        return self.range(of: pattern, options: .regularExpression) != nil
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
