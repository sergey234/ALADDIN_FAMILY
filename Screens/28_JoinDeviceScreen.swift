import SwiftUI

/**
 * 📱 Join Device Screen (Экран привязки устройства)
 * Экран для ребенка/дополнительного устройства. Позволяет отсканировать QR или ввести PIN для привязки.
 */
struct JoinDeviceScreen: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var pinCode: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var showSuccessAlert: Bool = false
    @State private var showQRScanner: Bool = false
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.xl) {
                        
                        // Header
                        VStack(spacing: Spacing.s) {
                            Text("Привязать устройство")
                                .font(.h1)
                                .foregroundColor(.textPrimary)
                            
                            Text("Отсканируйте QR-код с экрана администратора или введите 6-значный код.")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .multilineTextAlignment(.center)
                        }
                        .padding(.top, Spacing.xl)
                        
                        // Scan QR Button
                        Button(action: {
                            showQRScanner = true
                        }) {
                            VStack(spacing: Spacing.m) {
                                Image(systemName: "qrcode.viewfinder")
                                    .font(.system(size: 64))
                                    .foregroundColor(.primaryBlue)
                                
                                Text("Сканировать QR-код")
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
                        
                        Text("ИЛИ")
                            .font(.bodyBold)
                            .foregroundColor(.textSecondary)
                        
                        // PIN Input
                        VStack(spacing: Spacing.m) {
                            Text("Введите код привязки вручную")
                                .font(.h4)
                                .foregroundColor(.textPrimary)
                            
                            TextField("Например, 839124", text: $pinCode)
                                .textFieldStyle(ALADDINTextFieldStyle())
                                .keyboardType(.numberPad)
                                .multilineTextAlignment(.center)
                                .font(.system(size: 24, weight: .bold, design: .monospaced))
                            
                            Button(action: {
                                bindDevice(token: "", pin: pinCode)
                            }) {
                                HStack {
                                    if isLoading {
                                        ProgressView()
                                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    } else {
                                        Text("Привязать")
                                            .font(.bodyBold)
                                    }
                                }
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, Spacing.m)
                                .background(pinCode.count >= 6 ? Color.primaryBlue : Color.gray)
                                .cornerRadius(CornerRadius.medium)
                            }
                            .disabled(pinCode.count < 6 || isLoading)
                        }
                        .padding(Spacing.cardPadding)
                        .background(Color.backgroundMedium.opacity(0.4))
                        .cornerRadius(CornerRadius.large)
                        .padding(.horizontal, Spacing.screenPadding)
                        
                    }
                    .padding(.bottom, Spacing.xxl)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        dismiss()
                    }
                    .foregroundColor(.textPrimary)
                }
            }
            .sheet(isPresented: $showQRScanner) {
                // Временно показываем заглушку, тут должен быть QRScannerModal, который вернёт токен.
                VStack {
                    Text("Сканер QR-кода")
                        .font(.h2)
                    Button("Симулировать успешное сканирование") {
                        showQRScanner = false
                        bindDevice(token: "TEST_QR_TOKEN", pin: nil)
                    }
                    .padding()
                }
            }
            .alert("Успех", isPresented: $showSuccessAlert) {
                Button("OK") {
                    dismiss()
                }
            } message: {
                Text("Устройство успешно привязано к вашей семье!")
            }
            .alert("Ошибка", isPresented: .constant(errorMessage != nil)) {
                Button("OK") {
                    errorMessage = nil
                }
            } message: {
                if let error = errorMessage {
                    Text(error)
                }
            }
        }
    }
    
    private func bindDevice(token: String, pin: String?) {
        isLoading = true
        errorMessage = nil
        
        APIService.shared.bindDevice(token: token, pin: pin) { result in
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
}
