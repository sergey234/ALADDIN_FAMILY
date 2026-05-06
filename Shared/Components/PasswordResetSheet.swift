import SwiftUI

/// Единый UX сброса пароля: email → POST /api/auth/forgot_password
struct PasswordResetSheet: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var email: String
    @State private var isSending = false
    @State private var showSuccessAlert = false
    @State private var showErrorAlert = false
    @State private var errorMessage: String = ""

    private let api: APIService

    init(initialEmail: String, api: APIService? = nil) {
        _email = State(initialValue: initialEmail)
        self.api = api ?? APIService.shared
    }

    var body: some View {
        NavigationView {
            Form {
                Section {
                    TextField(
                        localizationManager.localized("password_reset_email_placeholder"),
                        text: $email
                    )
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled(true)
                    .keyboardType(.emailAddress)
                } header: {
                    Text(localizationManager.localized("password_reset_sheet_hint"))
                }
            }
            .navigationTitle(localizationManager.localized("password_reset_sheet_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("password_reset_sheet_cancel")) {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button(localizationManager.localized("password_reset_sheet_send")) {
                        sendRequest()
                    }
                    .disabled(isSending || !Self.isValidEmail(email))
                }
            }
            .alert(
                localizationManager.localized("password_reset_success_title"),
                isPresented: $showSuccessAlert
            ) {
                Button(localizationManager.localized("profile_edit_ok")) {
                    dismiss()
                }
            } message: {
                Text(localizationManager.localized("password_reset_success_message"))
            }
            .alert(
                localizationManager.localized("password_reset_error_title"),
                isPresented: $showErrorAlert
            ) {
                Button(localizationManager.localized("profile_edit_ok"), role: .cancel) { }
            } message: {
                Text(errorMessage)
            }
        }
    }

    private func sendRequest() {
        let trimmed = email.trimmingCharacters(in: .whitespacesAndNewlines)
        guard Self.isValidEmail(trimmed) else {
            errorMessage = localizationManager.localized("password_reset_error_invalid_email")
            showErrorAlert = true
            return
        }
        isSending = true
        api.requestPasswordReset(email: trimmed) { result in
            DispatchQueue.main.async {
                isSending = false
                switch result {
                case .success:
                    showSuccessAlert = true
                case .failure(let err):
                    errorMessage = err.localizedDescription.isEmpty
                        ? localizationManager.localized("password_reset_error_network")
                        : err.localizedDescription
                    showErrorAlert = true
                }
            }
        }
    }

    private static func isValidEmail(_ raw: String) -> Bool {
        let t = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard t.count >= 5 else { return false }
        return t.contains("@") && t.contains(".")
    }
}

/// Email для сброса: сохранённый логин → профильный alias → user_email
enum PasswordResetEmailResolver {
    static func resolved(storedAlias: String) -> String {
        if let e = UserDefaults.standard.string(forKey: "saved_login_email")?.trimmingCharacters(in: .whitespacesAndNewlines),
           !e.isEmpty { return e }
        if let e = UserDefaults.standard.string(forKey: "user_email")?.trimmingCharacters(in: .whitespacesAndNewlines),
           !e.isEmpty { return e }
        return storedAlias.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}
