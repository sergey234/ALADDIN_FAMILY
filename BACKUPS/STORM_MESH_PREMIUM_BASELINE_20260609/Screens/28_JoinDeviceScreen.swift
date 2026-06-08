import SwiftUI

/// Экран нового устройства: QR из приглашения родителя или ввод 6 цифр (гибрид с бэкендом).
struct JoinDeviceScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var pinCode: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @State private var showSuccessAlert: Bool = false
    @State private var showQRScanner: Bool = false

    private var normalizedPin: String {
        pinCode.filter { $0.isNumber }
    }

    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()

            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("join_device_title"),
                    subtitle: localizationManager.localized("join_device_subtitle"),
                    showBackButton: true,
                    onBack: {
                        leaveToSettings(reason: "JoinDeviceScreen cancel")
                    }
                )

                ScrollView {
                    VStack(alignment: .leading, spacing: Spacing.xl) {
                        Button(action: {
                            let gen = UIImpactFeedbackGenerator(style: .medium)
                            gen.impactOccurred()
                            showQRScanner = true
                        }) {
                            VStack(spacing: Spacing.m) {
                                Image(systemName: "qrcode.viewfinder")
                                    .font(.system(size: 64))
                                    .foregroundColor(.primaryBlue)
                                Text(localizationManager.localized("join_device_scan"))
                                    .font(.h4)
                                    .foregroundColor(.textPrimary)
                            }
                            .padding(Spacing.cardPadding)
                            .frame(maxWidth: .infinity)
                            .background(Color.backgroundMedium.opacity(0.4))
                            .cornerRadius(CornerRadius.large)
                            .overlay(
                                RoundedRectangle(cornerRadius: CornerRadius.large)
                                    .stroke(Color.primaryBlue.opacity(0.5), lineWidth: 2)
                            )
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.top, Spacing.l)

                        Text(localizationManager.localized("join_device_or"))
                            .font(.bodyBold)
                            .foregroundColor(.textSecondary)

                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text(localizationManager.localized("join_device_manual_title"))
                                .font(.h4)
                                .foregroundColor(.textPrimary)
                                .frame(maxWidth: .infinity, alignment: .leading)

                            TextField(localizationManager.localized("join_device_placeholder"), text: $pinCode)
                                .textFieldStyle(ALADDINTextFieldStyle())
                                .keyboardType(.numberPad)
                                .multilineTextAlignment(.center)
                                .font(.system(size: 24, weight: .bold, design: .monospaced))
                                .onChange(of: pinCode) { newValue in
                                    let digits = newValue.filter { $0.isNumber }
                                    pinCode = String(digits.prefix(6))
                                }

                            Button(action: {
                                bindWithPinOnly()
                            }) {
                                HStack {
                                    if isLoading {
                                        ProgressView()
                                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    } else {
                                        Text(localizationManager.localized("join_device_bind"))
                                            .font(.bodyBold)
                                    }
                                }
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, Spacing.m)
                                .background(normalizedPin.count == 6 ? Color.primaryBlue : Color.gray)
                                .cornerRadius(CornerRadius.medium)
                            }
                            .disabled(normalizedPin.count != 6 || isLoading)
                        }
                        .padding(Spacing.cardPadding)
                        .background(Color.backgroundMedium.opacity(0.4))
                        .cornerRadius(CornerRadius.large)
                        .padding(.horizontal, Spacing.screenPadding)
                    }
                    .padding(.bottom, Spacing.xxl)
                }
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showQRScanner) {
            QRScannerModal(onCodeScanned: { raw in
                if let token = DevicePairingLinkParser.extractToken(fromScannedString: raw)
                    ?? URL(string: raw).flatMap({ DevicePairingLinkParser.extractToken(from: $0) }) {
                    bindWithToken(token)
                } else {
                    errorMessage = localizationManager.localized("join_device_error_title")
                }
            })
            .environmentObject(navigationManager)
            .environmentObject(localizationManager)
        }
        .alert(localizationManager.localized("join_device_success_title"), isPresented: $showSuccessAlert) {
            Button(localizationManager.localized("common_ok")) {
                notifyRefreshAndLeave()
            }
        } message: {
            Text(localizationManager.localized("join_device_success_message"))
        }
        .alert(localizationManager.localized("join_device_error_title"), isPresented: .constant(errorMessage != nil)) {
            Button(localizationManager.localized("common_ok")) {
                errorMessage = nil
            }
        } message: {
            if let error = errorMessage {
                Text(error)
            }
        }
        .onAppear(perform: consumePendingTokenIfAny)
    }

    private func consumePendingTokenIfAny() {
        if let t = navigationManager.pendingDeviceBindToken?.trimmingCharacters(in: .whitespacesAndNewlines), !t.isEmpty {
            navigationManager.pendingDeviceBindToken = nil
            bindWithToken(t)
            return
        }
        if let s = PendingAuthTokenStore.loadDeviceBindToken() {
            PendingAuthTokenStore.clearDeviceBindToken()
            if let token = DevicePairingLinkParser.extractToken(fromScannedString: s)
                ?? URL(string: s).flatMap({ DevicePairingLinkParser.extractToken(from: $0) }) {
                bindWithToken(token)
            }
        }
    }

    private func bindWithToken(_ token: String) {
        let trimmed = token.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        isLoading = true
        errorMessage = nil
        APIService.shared.bindDevice(token: trimmed, pin: nil) { result in
            DispatchQueue.main.async {
                isLoading = false
                switch result {
                case .success:
                    showSuccessAlert = true
                case .failure(let error):
                    errorMessage = error.localizedDescription
                }
            }
        }
    }

    private func bindWithPinOnly() {
        guard normalizedPin.count == 6 else { return }
        isLoading = true
        errorMessage = nil
        APIService.shared.bindDevice(token: nil, pin: normalizedPin) { result in
            DispatchQueue.main.async {
                isLoading = false
                switch result {
                case .success:
                    showSuccessAlert = true
                case .failure(let error):
                    errorMessage = error.localizedDescription
                }
            }
        }
    }

    private func notifyRefreshAndLeave() {
        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.pendingMainDashboardDevicesRefresh)
        NotificationCenter.default.post(name: NSNotification.Name("FamilyDevicesDidChange"), object: nil)
        leaveToSettings(reason: "JoinDeviceScreen completed")
    }

    private func leaveToSettings(reason: String) {
        if navigationManager.previousScreen == .settings {
            navigationManager.goBack(reason: reason)
        } else {
            navigationManager.navigateToRoot(.settings)
        }
    }
}
