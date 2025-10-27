import SwiftUI

/// 💳 Tariffs Screen
/// Экран тарифов - выбор подписки
/// Источник дизайна: /mobile/wireframes/09_tariffs_screen.html
struct TariffsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = TariffsViewModel()
    @State private var selectedTariff: TariffType = .family
    @State private var showPaymentQRScreen = false
    @State private var selectedTariffForPayment: Tariff?
    
    enum TariffType {
        case free, personal, family, premium
        
        var title: String {
            switch self {
            case .free: return "БАЗОВЫЙ"
            case .personal: return "ЛИЧНЫЙ"
            case .family: return "СЕМЕЙНЫЙ"
            case .premium: return "ПРЕМИУМ"
            }
        }
        
        var price: String {
            switch self {
            case .free: return "0 ₽"
            case .personal: return "290 ₽"
            case .family: return "590 ₽"
            case .premium: return "990 ₽"
            }
        }
        
        var period: String {
            switch self {
            case .free: return "Бесплатно"
            case .personal, .family, .premium: return "в месяц"
            }
        }
        
        var features: [String] {
            switch self {
            case .free: return ["VPN базовый", "1 устройство", "Реклама"]
            case .personal: return ["VPN Pro", "3 устройства", "Без рекламы", "AI помощник"]
            case .family: return [
                "VPN Ultra", "10 устройств",
                "Родительский контроль", "AI + Аналитика",
                "Приоритетная поддержка"
            ]
            case .premium: return [
                "VPN Max", "Неограниченно",
                "Всё из Семейного", "Консьерж-сервис",
                "Премиум поддержка 24/7"
            ]
            }
        }
        
        var color: Color {
            switch self {
            case .free: return .textSecondary
            case .personal: return .primaryBlue
            case .family: return .secondaryGold
            case .premium: return Color(hex: "#A855F7")
            }
        }
        
        var recommended: Bool {
            return self == .family
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: "ТАРИФЫ",
                    subtitle: "Выберите подходящий план",
                    showBackButton: true,
                    onBack: {
                        dismiss()
                    }
                )
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Карточки тарифов
                        tariffCard(.free)
                        tariffCard(.personal)
                        tariffCard(.family)
                        tariffCard(.premium)
                        
                        // Сравнение тарифов
                        comparisonButton
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showPaymentQRScreen) {
            if let tariff = selectedTariffForPayment {
                PaymentQRScreen(tariff: tariff) {
                    // Callback после успешной оплаты
                    print("✅ Подписка успешно оплачена!")
                }
            }
        }
    }
    
    // MARK: - Helpers
    
    private func getButtonText(for tariff: TariffType) -> String {
        if tariff == .free {
            return "БЕСПЛАТНО"
        } else if selectedTariff == tariff {
            return "✓ ВЫБРАН"
        } else {
            // Проверяем регион
            if AppConfig.useAlternativePayments {
                return "ОПЛАТИТЬ ЧЕРЕЗ QR"
            } else {
                return "ПОДКЛЮЧИТЬ"
            }
        }
    }
    
    // MARK: - Tariff Card
    
    private func tariffCard(_ tariff: TariffType) -> some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Бейдж "Рекомендуем"
            if tariff.recommended {
                HStack {
                    Spacer()
                    Text("⭐ РЕКОМЕНДУЕМ")
                        .font(.captionBold)
                        .foregroundColor(.backgroundDark)
                        .padding(.horizontal, Spacing.m)
                        .padding(.vertical, Spacing.xs)
                        .background(
                            Capsule()
                                .fill(tariff.color)
                        )
                }
            }
            
            // Заголовок тарифа
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(tariff.title)
                        .font(.h2)
                        .foregroundColor(tariff.color)
                    
                    HStack(alignment: .firstTextBaseline, spacing: Spacing.xs) {
                        Text(tariff.price)
                            .font(.system(size: 36, weight: .bold))
                            .foregroundColor(.white)
                        
                        Text(tariff.period)
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                Spacer()
            }
            
            // Разделитель
            Rectangle()
                .fill(tariff.color.opacity(0.3))
                .frame(height: 1)
            
            // Список функций
            VStack(alignment: .leading, spacing: Spacing.s) {
                ForEach(tariff.features, id: \.self) { feature in
                    HStack(spacing: Spacing.s) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 18))
                            .foregroundColor(tariff.color)
                        
                        Text(feature)
                            .font(.body)
                            .foregroundColor(.textPrimary)
                    }
                }
            }
            
            // Кнопка выбора/оплаты
            Button(action: {
                HapticFeedback.impact(.medium)
                selectedTariff = tariff
                
                // Если тариф бесплатный
                if tariff == .free {
                    print("Активирован бесплатный тариф")
                    return
                }
                
                // Создаем Tariff объект для передачи в PaymentQRScreen
                let tariffObj = Tariff(
                    id: String(describing: tariff),
                    title: tariff.title,
                    price: tariff.price,
                    period: tariff.period,
                    features: tariff.features,
                    product: nil,
                    isPurchased: false
                )
                
                // Проверяем регион
                if AppConfig.useAlternativePayments {
                    // Россия → QR оплата
                    selectedTariffForPayment = tariffObj
                    showPaymentQRScreen = true
                } else {
                    // За границей → IAP (не реализовано в простой версии)
                    print("IAP purchase for: \(tariff.title)")
                }
            }) {
                Text(getButtonText(for: tariff))
                    .font(.buttonText)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: Size.buttonHeight)
                    .background(
                        selectedTariff == tariff ?
                        LinearGradient(
                            colors: [Color.successGreen, Color(hex: "#16A34A")],
                            startPoint: .leading,
                            endPoint: .trailing
                        ) :
                        LinearGradient(
                            colors: [tariff.color, tariff.color.opacity(0.8)],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .cornerRadius(CornerRadius.large)
            }
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(
                            selectedTariff == tariff ?
                            tariff.color :
                            Color.white.opacity(0.1),
                            lineWidth: selectedTariff == tariff ? 2 : 1
                        )
                )
        )
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Comparison Button
    
    private var comparisonButton: some View {
        Button(action: {
            print("Сравнить тарифы")
        }) {
            HStack(spacing: Spacing.m) {
                Text("📊")
                    .font(.system(size: 24))
                
                Text("Сравнить все тарифы")
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Preview

#if DEBUG
struct TariffsScreen_Previews: PreviewProvider {
    static var previews: some View {
        TariffsScreen()
    }
}
#endif

