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
                    
                    Text("Введите код приглашения")
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.primary)
                    
                    Text("Попросите у администратора семьи код вида: FAM-XXXX-XXXX-XXXX")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(.top, 20)
                
                // Поле ввода
                VStack(alignment: .leading, spacing: 8) {
                    Text("Код приглашения")
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
                        Text("Формат: FAM-XXXX-XXXX-XXXX")
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
                            Text("Присоединиться к семье")
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
            .navigationTitle("Присоединение")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
        }
        .sheet(isPresented: $showRoleSelection) {
            // TODO: Показывать выбор роли после успешной проверки кода
            Text("Выбор роли")
        }
        .onAppear {
            // Устанавливаем initialCode если он есть
            if let initialCode = initialCode {
                code = initialCode
            }
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

        let familyId = code
            .replacingOccurrences(of: "-", with: "")
            .replacingOccurrences(of: "FAM", with: "FAM_")

        // 1) Сначала получаем JWT по recovery code (чтобы family API сразу были авторизованы)
        apiService.loginByRecoveryCode(familyID: familyId, recoveryCode: code) { loginResult in
            DispatchQueue.main.async {
                switch loginResult {
                case .success(let loginResponse):
                    AppConfig.authToken = loginResponse.access_token
                    if let refreshToken = loginResponse.refresh_token, !refreshToken.isEmpty {
                        KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
                    }

                    // 2) После токена восстанавливаем доступ и тянем семью
                    registrationVM.recoverAccess(withCode: code)
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
                        if !registrationVM.isLoading {
                            if let error = registrationVM.errorMessage {
                                self.errorMessage = error
                                self.isLoading = false
                            } else if registrationVM.familyID != nil {
                                self.isLoading = false
                                UserDefaults.standard.set(registrationVM.familyID, forKey: "family_id")
                                NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
                                NotificationCenter.default.post(name: NSNotification.Name("MainFamilyStatsForceRefresh"), object: nil)
                                isPresented = false
                            } else {
                                self.isLoading = false
                                self.errorMessage = "Не удалось восстановить доступ к семье"
                            }
                        }
                    }
                case .failure(let error):
                    self.isLoading = false
                    self.errorMessage = error.localizedDescription
                }
            }
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
    }
}
