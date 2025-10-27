import SwiftUI

/**
 * 💳 Payment QR Screen
 * Экран оплаты через QR-код (СБП, SberPay, Universal)
 * Для российских пользователей вместо IAP
 */

struct PaymentQRScreen: View {
    
    // MARK: - Properties
    
    @Environment(\.dismiss) var dismiss
    @StateObject private var viewModel: PaymentQRViewModel
    
    let tariff: Tariff
    let onPaymentCompleted: () -> Void
    
    // MARK: - Init
    
    init(tariff: Tariff, onPaymentCompleted: @escaping () -> Void) {
        self.tariff = tariff
        self.onPaymentCompleted = onPaymentCompleted
        self._viewModel = StateObject(wrappedValue: PaymentQRViewModel(tariff: tariff))
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Background
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Navigation Bar
                    ALADDINNavigationBar()
                    
                    // Timer
                    if let expiresAt = viewModel.expiresAt {
                        timerView(expiresAt: expiresAt)
                    }
                    
                    // QR Tabs
                    qrTabsView
                    
                    // Instructions
                    instructionsView
                    
                    // Check Payment Button
                    checkPaymentButton
                    
                    // Payment Info
                    paymentInfoView
                    
                    Spacer()
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
            
            // Loading Overlay
            if viewModel.isLoading {
                Color.black.opacity(0.5)
                    .ignoresSafeArea()
                ProgressView()
                    .scaleEffect(1.5)
                    .tint(.secondaryGold)
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            viewModel.createPayment()
            viewModel.startAutoCheck()
        }
        .onDisappear {
            viewModel.stopAutoCheck()
        }
        .alert("Оплата успешна!", isPresented: $viewModel.showSuccessAlert) {
            Button("Отлично!") {
                onPaymentCompleted()
                dismiss()
            }
        } message: {
            Text("Подписка \(tariff.title) активирована!\n\nСпасибо за покупку!")
        }
        .alert("Ошибка", isPresented: $viewModel.showErrorAlert) {
            Button("OK") {
                viewModel.errorMessage = nil
            }
        } message: {
            if let error = viewModel.errorMessage {
                Text(error)
            }
        }
    }
    
    // MARK: - Timer View
    
    private func timerView(expiresAt: Date) -> some View {
        VStack(spacing: Spacing.xs) {
            Text("⏰")
                .font(.system(size: 32))
            
            Text(timeRemaining(until: expiresAt))
                .font(.h3)
                .foregroundColor(.secondaryGold)
            
            Text("до окончания срока оплаты")
                .font(.caption)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.large)
        .cardShadow()
    }
    
    // MARK: - QR Tabs
    
    private var qrTabsView: some View {
        VStack(spacing: Spacing.m) {
            // Tab Selector
            HStack(spacing: Spacing.s) {
                ForEach(PaymentMethod.allCases, id: \.self) { method in
                    Button(action: {
                        viewModel.selectedMethod = method
                        HapticFeedback.selection()
                    }) {
                        VStack(spacing: Spacing.xxs) {
                            Text("💳")
                                .font(.system(size: 24))
                            Text(method.displayName)
                                .font(.captionBold)
                                .foregroundColor(viewModel.selectedMethod == method ? .secondaryGold : .textSecondary)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.s)
                        .background(
                            viewModel.selectedMethod == method ?
                            Color.primaryBlue.opacity(0.3) :
                            Color.clear
                        )
                        .cornerRadius(CornerRadius.medium)
                    }
                }
            }
            
            // QR Code Display
            if let qrImage = viewModel.currentQRImage {
                VStack(spacing: Spacing.m) {
                    Text(viewModel.selectedMethod.displayName)
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    AsyncImage(url: URL(string: qrImage)) { phase in
                        switch phase {
                        case .success(let image):
                            image
                                .resizable()
                                .interpolation(.none)
                                .scaledToFit()
                                .frame(width: 280, height: 280)
                                .background(Color.white)
                                .cornerRadius(CornerRadius.large)
                        case .failure(_):
                            placeholder
                        case .empty:
                            ProgressView()
                        @unknown default:
                            placeholder
                        }
                    }
                    
                    Text("Отсканируйте QR-код в приложении вашего банка для оплаты")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .padding(Spacing.cardPadding)
                .background(
                    LinearGradient.cardGradient
                        .appGlassmorphism()
                )
                .cornerRadius(CornerRadius.large)
                .cardShadow()
            }
        }
    }
    
    private var placeholder: some View {
        Rectangle()
            .fill(Color.surfaceDark)
            .frame(width: 280, height: 280)
            .cornerRadius(CornerRadius.large)
            .overlay(
                Text("QR-код недоступен")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            )
    }
    
    // MARK: - Instructions
    
    private var instructionsView: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("КАК ОПЛАТИТЬ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            VStack(alignment: .leading, spacing: Spacing.s) {
                instructionStep(number: 1, text: "Откройте приложение вашего банка")
                instructionStep(number: 2, text: "Найдите раздел \"Оплата по QR\"")
                instructionStep(number: 3, text: "Отсканируйте QR-код выше")
                instructionStep(number: 4, text: "Подтвердите оплату")
                instructionStep(number: 5, text: "Дождитесь активации подписки")
            }
        }
        .padding(Spacing.cardPadding)
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.large)
        .cardShadow()
    }
    
    private func instructionStep(number: Int, text: String) -> some View {
        HStack(spacing: Spacing.m) {
            Text("\(number)")
                .font(.h3)
                .foregroundColor(.secondaryGold)
                .frame(width: 32, height: 32)
                .background(Color.surfaceDark)
                .cornerRadius(CornerRadius.small)
            
            Text(text)
                .font(.body)
                .foregroundColor(.textPrimary)
        }
    }
    
    // MARK: - Check Payment Button
    
    private var checkPaymentButton: some View {
        Button(action: {
            viewModel.checkPaymentStatus()
        }) {
            Text("Проверить оплату")
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .frame(height: 48)
                .background(Color.primaryBlue)
                .cornerRadius(8)
        }
        .disabled(viewModel.isLoading)
    }
    
    // MARK: - Payment Info
    
    private var paymentInfoView: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("ИНФОРМАЦИЯ О ПЛАТЕЖЕ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            VStack(spacing: Spacing.s) {
                infoRow(label: "Тариф", value: tariff.title)
                infoRow(label: "Сумма", value: tariff.price)
                infoRow(label: "Период", value: tariff.period)
                
                if let merchantInfo = viewModel.merchantInfo {
                    Divider()
                        .background(Color.textTertiary)
                    
                    infoRow(label: "Получатель", value: merchantInfo.name)
                    infoRow(label: "Адрес", value: merchantInfo.address)
                    infoRow(label: "Телефон СБП", value: merchantInfo.phone ?? "Не указан")
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.large)
        .cardShadow()
    }
    
    private func infoRow(label: String, value: String) -> some View {
        HStack {
            Text(label)
                .font(.body)
                .foregroundColor(.textSecondary)
            Spacer()
            Text(value)
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
        }
    }
    
    // MARK: - Helpers
    
    private func timeRemaining(until date: Date) -> String {
        let now = Date()
        let remaining = date.timeIntervalSince(now)
        
        if remaining <= 0 {
            return "Истек срок"
        }
        
        let hours = Int(remaining) / 3600
        let minutes = (Int(remaining) % 3600) / 60
        
        return String(format: "%02d:%02d", hours, minutes)
    }
}


// MARK: - Merchant Info


// MARK: - Preview

struct PaymentQRScreen_Previews: PreviewProvider {
    static var previews: some View {
        PaymentQRScreen(
            tariff: Tariff(
                id: "test",
                title: "Семейный",
                price: "590 ₽",
                period: "в месяц",
                features: ["До 5 устройств", "Полная защита"],
                product: nil,
                isPurchased: false
            ),
            onPaymentCompleted: {}
        )
    }
}

