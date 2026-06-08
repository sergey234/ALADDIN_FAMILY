import SwiftUI

struct ActivationCodeScreen: View {
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = ActivationCodeViewModel()
    @FocusState private var isTextFieldFocused: Bool
    
    // ✅ Согласие на обработку ПДн (152-ФЗ)
    @State private var consentAccepted: Bool = false
    @AppStorage("personal_data_consent_accepted") private var savedConsentAccepted: Bool = false
    @AppStorage("personal_data_consent_date") private var consentDate: String = ""
    
    var body: some View {
        ZStack {
            StormMeshBackground(variant: .premium)
            
            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("activation_code_title"),
                    subtitle: localizationManager.localized("activation_code_subtitle"),
                    showBackButton: true,
                    onBack: {
                        navigationManager.goBack(reason: "ActivationCode.onBack")
                    }
                )
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        infoCard
                        codeInputCard
                        consentCard  // ✅ Блок согласия на обработку ПДн
                        debugLogsCard  // 🔍 Панель с логами
                        helpCard
                    }
                    .padding(.top, Spacing.l)
                }
            }
        }
        .navigationBarHidden(true)
        .alert(viewModel.successMessage ?? "", isPresented: Binding(
            get: { viewModel.successMessage != nil },
            set: { if !$0 { viewModel.successMessage = nil } }
        )) {
            Button(localizationManager.localized("common_ok")) {}
        }
        .alert(viewModel.errorMessage ?? "", isPresented: Binding(
            get: { viewModel.errorMessage != nil },
            set: { if !$0 { viewModel.errorMessage = nil } }
        )) {
            Button(localizationManager.localized("common_ok")) {}
        }
    }
    
    private var infoCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("activation_code_instruction_title"))
                .font(.headline)
                .foregroundColor(.textPrimary)
            Text(localizationManager.localized("activation_code_instruction_body"))
                .font(.subheadline)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private var codeInputCard: some View {
        VStack(spacing: Spacing.m) {
            TextField(
                localizationManager.localized("activation_code_placeholder"),
                text: $viewModel.code
            )
            .textInputAutocapitalization(.characters)
            .disableAutocorrection(true)
            .keyboardType(.asciiCapable)
            .padding()
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.white.opacity(0.08))
            )
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.15), lineWidth: 1)
            )
            .focused($isTextFieldFocused)
            
            Button(action: {
                HapticFeedback.impact(.medium)
                isTextFieldFocused = false
                // ✅ Сохраняем согласие перед активацией
                if consentAccepted {
                    savedConsentAccepted = true
                    consentDate = ISO8601DateFormatter().string(from: Date())
                }
                viewModel.activateCode()
            }) {
                if viewModel.isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        .frame(maxWidth: .infinity)
                        .padding()
                } else {
                    Text(localizationManager.localized("activation_code_button"))
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                }
            }
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(viewModel.isLoading ? Color.gray : Color.primaryBlue)
            )
            .disabled(viewModel.isLoading || viewModel.code.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || !consentAccepted)
            
            if let planName = viewModel.activatedPlanName {
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("activation_code_plan") + ": \(planName)")
                        .font(.subheadline)
                        .foregroundColor(.textPrimary)
                    if let expiresAt = viewModel.activationExpiration {
                        Text(localizationManager.localized("activation_code_expires") + ": \(expiresAt)")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.top, Spacing.s)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.4))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private var helpCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("activation_code_help_title"))
                .font(.headline)
                .foregroundColor(.textPrimary)
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("• " + localizationManager.localized("activation_code_help_step_1"))
                Text("• " + localizationManager.localized("activation_code_help_step_2"))
                Text("• " + localizationManager.localized("activation_code_help_step_3"))
            }
            .font(.subheadline)
            .foregroundColor(.textSecondary)
            
            Button {
                HapticFeedback.impact(.light)
                URLHelper.openWebsite(urlString: AppConfig.subscriptionWebsiteURL, tariffId: nil)
            } label: {
                HStack {
                    Image(systemName: "safari")
                    Text(localizationManager.localized("tariffs_subscribe_on_website"))
                }
                .font(.subheadline.bold())
                .padding(Spacing.s)
                .frame(maxWidth: .infinity)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .fill(Color.white.opacity(0.1))
                )
            }
        }
        .padding()
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.bottom, Spacing.xl)
    }
    
    // MARK: - Debug Logs Card
    
    private var debugLogsCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text(localizationManager.localized("activation_logs_title"))
                    .font(.headline.bold())
                    .foregroundColor(.white)
                
                Spacer()
                
                if !viewModel.logs.isEmpty {
                    Button(action: {
                        viewModel.clearLogs()
                    }) {
                        Text(localizationManager.localized("activation_logs_clear"))
                            .font(.caption.bold())
                            .foregroundColor(.white)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(Color.red.opacity(0.7))
                            .cornerRadius(8)
                    }
                }
            }
            
            if viewModel.logs.isEmpty {
                VStack(spacing: 8) {
                    Text(localizationManager.localized("activation_logs_empty_title"))
                        .font(.subheadline)
                        .foregroundColor(.textSecondary)
                        .italic()
                    Text(localizationManager.localized("activation_logs_empty_subtitle"))
                        .font(.caption)
                        .foregroundColor(.textSecondary.opacity(0.7))
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 20)
            } else {
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(alignment: .leading, spacing: 6) {
                        ForEach(Array(viewModel.logs.enumerated()), id: \.offset) { index, log in
                            HStack(alignment: .top, spacing: 4) {
                                Text("\(index + 1).")
                                    .font(.system(size: 9, design: .monospaced))
                                    .foregroundColor(.textSecondary)
                                    .frame(width: 25, alignment: .trailing)
                                
                                Text(log)
                                    .font(.system(size: 11, design: .monospaced))
                                    .foregroundColor(logColor(for: log))
                                    .frame(maxWidth: .infinity, alignment: .leading)
                            }
                            .padding(.vertical, 2)
                        }
                    }
                    .padding(8)
                }
                .frame(maxHeight: 350)
                .background(Color.black.opacity(0.4))
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.white.opacity(0.2), lineWidth: 1)
                )
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Color.blue.opacity(0.5), lineWidth: 2)
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func logColor(for log: String) -> Color {
        if log.contains("❌") || log.contains("Ошибка") {
            return .red
        } else if log.contains("✅") || log.contains("успеш") {
            return .green
        } else if log.contains("⚠️") || log.contains("уже") {
            return .orange
        } else if log.contains("🔵") || log.contains("Шаг") {
            return .blue
        } else {
            return .textSecondary
        }
    }
    
    // MARK: - Consent Card (152-ФЗ)
    
    private var consentCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(alignment: .top, spacing: Spacing.s) {
                Button(action: {
                    HapticFeedback.impact(.light)
                    withAnimation {
                        consentAccepted.toggle()
                    }
                }) {
                    Image(systemName: consentAccepted ? "checkmark.square.fill" : "square")
                        .font(.system(size: 20))
                        .foregroundColor(consentAccepted ? .primaryBlue : .textSecondary)
                }
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(localizationManager.localized("activation_consent_title"))
                        .font(.subheadline.bold())
                        .foregroundColor(.textPrimary)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(localizationManager.localized("activation_consent_message"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        HStack(spacing: 4) {
                            Button(action: {
                                URLHelper.openWebsite(urlString: "https://aladdin-ai.ru/consent.html", tariffId: nil)
                            }) {
                                Text(localizationManager.localized("activation_consent_link_title"))
                                    .font(.caption)
                                    .foregroundColor(.primaryBlue)
                                    .underline()
                            }
                            
                            Text(localizationManager.localized("common_and"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            
                            Button(action: {
                                URLHelper.openWebsite(urlString: "https://aladdin-ai.ru/privacy.html", tariffId: nil)
                            }) {
                                Text(localizationManager.localized("privacy_policy"))
                                    .font(.caption)
                                    .foregroundColor(.primaryBlue)
                                    .underline()
                            }
                            
                            Text(".")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                }
            }
            
            if !consentAccepted && !viewModel.code.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                Text(localizationManager.localized("activation_consent_required_warning"))
                    .font(.caption)
                    .foregroundColor(.orange)
                    .padding(.leading, 28)
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(consentAccepted ? Color.primaryBlue.opacity(0.3) : Color.secondaryGold.opacity(0.3), lineWidth: 1)
        )
        .padding(.horizontal, Spacing.screenPadding)
        .onAppear {
            // ✅ Восстанавливаем сохраненное согласие
            if savedConsentAccepted {
                consentAccepted = true
            }
        }
    }
}

#if DEBUG
struct ActivationCodeScreen_Previews: PreviewProvider {
    static var previews: some View {
        ActivationCodeScreen()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}
#endif

