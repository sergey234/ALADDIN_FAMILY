import SwiftUI

/**
 * 🎯 Dark Web Scan Method Selector
 * Компонент для выбора метода сканирования (безопасное/быстрое)
 */

struct DarkWebScanMethodSelector: View {
    
    @Binding var selectedMethod: DarkWebScanMethod
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showExplanation: Bool = false
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            // Заголовок
            Text(localizationManager.localized("dark_web_scan_method_title"))
                .font(.h2)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            // Вариант 1: Безопасное сканирование
            methodCard(
                method: .secure,
                isSelected: selectedMethod == .secure,
                title: localizationManager.localized("dark_web_scan_method_secure"),
                subtitle: localizationManager.localized("dark_web_scan_method_secure_subtitle"),
                advantages: [
                    localizationManager.localized("dark_web_scan_method_secure_advantage_1"),
                    localizationManager.localized("dark_web_scan_method_secure_advantage_2"),
                    localizationManager.localized("dark_web_scan_method_secure_advantage_3")
                ],
                disadvantages: [
                    localizationManager.localized("dark_web_scan_method_secure_disadvantage_1")
                ],
                isRecommended: true
            )
            
            // Вариант 2: Быстрое сканирование
            methodCard(
                method: .fast,
                isSelected: selectedMethod == .fast,
                title: localizationManager.localized("dark_web_scan_method_fast"),
                subtitle: localizationManager.localized("dark_web_scan_method_fast_subtitle"),
                advantages: [
                    localizationManager.localized("dark_web_scan_method_fast_advantage_1"),
                    localizationManager.localized("dark_web_scan_method_fast_advantage_2")
                ],
                disadvantages: [
                    localizationManager.localized("dark_web_scan_method_fast_disadvantage_1"),
                    localizationManager.localized("dark_web_scan_method_fast_disadvantage_2")
                ],
                isRecommended: false
            )
            
            // Кнопка "Узнать больше"
            Button(action: {
                showExplanation = true
            }) {
                HStack(spacing: Spacing.xs) {
                    Image(systemName: "info.circle")
                    Text(localizationManager.localized("dark_web_scan_method_learn_more"))
                }
                .font(.body)
                .foregroundColor(.primaryBlue)
            }
        }
        .sheet(isPresented: $showExplanation) {
            DarkWebScanExplanationView()
                .environmentObject(localizationManager)
        }
    }
    
    private func methodCard(
        method: DarkWebScanMethod,
        isSelected: Bool,
        title: String,
        subtitle: String,
        advantages: [String],
        disadvantages: [String],
        isRecommended: Bool
    ) -> some View {
        Button(action: {
            selectedMethod = method
        }) {
            VStack(alignment: .leading, spacing: Spacing.s) {
                // Заголовок с иконкой
                HStack(alignment: .top, spacing: Spacing.xs) {
                    Image(systemName: method.icon)
                        .font(.title2)
                        .foregroundColor(method == .secure ? .successGreen : .warningOrange)
                        .padding(.top, 2)
                    
                    if method == .secure {
                        // ✅ ИСПРАВЛЕНИЕ: Разбиваем "Безопасное сканирование" на 2 строчки
                        VStack(alignment: .leading, spacing: 0) {
                            Text(localizationManager.localized("dark_web_scan_method_secure_line1"))
                                .font(.h3)
                                .foregroundColor(.textPrimary)
                                .lineLimit(1)
                            Text(localizationManager.localized("dark_web_scan_method_secure_line2"))
                                .font(.h3)
                                .foregroundColor(.textPrimary)
                                .lineLimit(1)
                        }
                    } else {
                    Text(title)
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                            .lineLimit(2)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    
                    Spacer()
                    
                    if isRecommended {
                        Text(localizationManager.localized("dark_web_scan_method_recommended"))
                            .font(.caption)
                            .foregroundColor(.white)
                            .lineLimit(1)
                            .minimumScaleFactor(0.8)
                            .padding(.horizontal, Spacing.s)
                            .padding(.vertical, Spacing.xs)
                            .background(
                                Capsule()
                                    .fill(Color.successGreen)
                            )
                    }
                    
                    if isSelected {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.title2)
                            .foregroundColor(.primaryBlue)
                    }
                }
                
                // Подзаголовок
                Text(subtitle)
                    .font(.body)
                    .foregroundColor(.textSecondary)
                
                // Преимущества
                if !advantages.isEmpty {
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        ForEach(advantages, id: \.self) { advantage in
                            HStack(alignment: .top, spacing: Spacing.xs) {
                                Image(systemName: "checkmark.circle.fill")
                                    .font(.caption)
                                    .foregroundColor(.successGreen)
                                Text(advantage)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                        }
                    }
                }
                
                // Недостатки
                if !disadvantages.isEmpty {
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        ForEach(disadvantages, id: \.self) { disadvantage in
                            HStack(alignment: .top, spacing: Spacing.xs) {
                                Image(systemName: "exclamationmark.triangle.fill")
                                    .font(.caption)
                                    .foregroundColor(.warningOrange)
                                Text(disadvantage)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                        }
                    }
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(isSelected ? Color.primaryBlue.opacity(0.1) : Color.backgroundMedium.opacity(0.5))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(isSelected ? Color.primaryBlue : Color.clear, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

