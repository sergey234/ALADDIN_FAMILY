import SwiftUI

/// 🦄 Rewards Quick Modal
/// Упрощённое модальное окно для быстрых действий с вознаграждениями
/// Источник дизайна: /mobile/wireframes/03_family_screen.html (модальное окно)
/// ⚠️ ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ - доступ ограничен по роли!
struct RewardsQuickModal: View {
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var unicornBalance: Int
    @AppStorage("parental_selected_child_id") private var selectedChildId: String = ""
    
    // Проверка роли пользователя
    private var isUserParent: Bool {
        let storedRole = UserDefaults.standard.string(forKey: "current_user_role") ?? ""
        print("🔍 DEBUG RewardsQuickModal.isUserParent:")
        print("   - roleString = '\(storedRole)'")
        
        guard let role = FamilyRole(storageValue: storedRole) else {
            print("   - Результат: false (роль не найдена или невалидна)")
            return false
        }
        
        let isParent = role == .parent
        print("   - role = \(role.rawValue)")
        print("   - Результат: \(isParent)")
        return isParent
    }

    private var rewardsScopeChildId: String? {
        let trimmed = selectedChildId.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmed.isEmpty { return trimmed }
        return UnicornRewardsStore.resolveActiveChildId()
    }
    
    @State private var showParentAuthDeniedAlert = false
    
    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .growWarm)
                
                if isUserParent {
                    VStack(spacing: Spacing.l) {
                        // Баланс
                        VStack(spacing: Spacing.m) {
                            Text("🦄")
                                .font(.system(size: 48))
                            
                            Text("\(unicornBalance)")
                                .font(.system(size: 36, weight: .bold))
                                .foregroundColor(Color(hex: "C084FC"))
                            
                            Text(localizationManager.localized("rewards_quick_balance_label"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.l)
                        .stormGlassCard(cornerRadius: CornerRadius.large)
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.large)
                                .stroke(Color(hex: "A855F7").opacity(0.4), lineWidth: 2)
                        )
                        .padding(.horizontal, Spacing.screenPadding)
                        
                        // Быстрые действия
                        HStack(spacing: Spacing.m) {
                            quickActionButton(icon: "✅", title: localizationManager.localized("rewards_quick_action_reward"), color: .successGreen) {
                                rewardChild()
                            }
                            
                            quickActionButton(icon: "❌", title: localizationManager.localized("rewards_quick_action_punish"), color: .dangerRed) {
                                punishChild()
                            }
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                        
                        Spacer()
                    }
                    .padding(.top, Spacing.l)
                } else {
                    // Блокировка для не-родителей
                    VStack(spacing: Spacing.l) {
                        Text("🔒")
                            .font(.system(size: 64))
                        Text(localizationManager.localized("rewards_quick_access_limited_title"))
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                        Text(localizationManager.localized("rewards_quick_access_limited_message"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        Button(action: {
                            HapticFeedback.impact(.medium)
                            dismiss()
                        }) {
                            Text(localizationManager.localized("rewards_quick_acknowledge"))
                                .font(.bodyBold)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.primaryBlue)
                                .cornerRadius(CornerRadius.medium)
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                    }
                    .padding(.top, Spacing.xxl)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    HStack(spacing: Spacing.xs) {
                        Text("🦄")
                            .font(.system(size: 20))
                        Text(localizationManager.localized("rewards_quick_title"))
                            .font(.h3)
                            .foregroundColor(Color(hex: "C084FC"))
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.textSecondary)
                    }
                }
            }
            .alert(isPresented: $showParentAuthDeniedAlert) {
                SwiftUI.Alert(
                    title: Text(localizationManager.localized("games_parental_auth_alert_title")),
                    message: Text(localizationManager.localized("child_rewards_parent_auth_required")),
                    dismissButton: .default(Text(localizationManager.localized("common_ok")))
                )
            }
        }
    }
    
    private func quickActionButton(icon: String, title: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: Spacing.xs) {
                Text(icon)
                    .font(.system(size: 32))
                Text(title)
                    .font(.caption)
                    .foregroundColor(color)
            }
            .frame(maxWidth: .infinity)
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(color.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(color, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private func rewardChild() {
        // ✅ Только родители могут награждать
        guard isUserParent else {
            HapticFeedback.notification(.error)
            return
        }
        
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        // Обновляем баланс в UserDefaults (синхронизация)
        let currentBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
        let newBalance = currentBalance + 10
        UnicornRewardsStore.writeBalance(newBalance, for: rewardsScopeChildId)
        
        unicornBalance = newBalance
        dismiss()
    }
    
    private func punishChild() {
        // ✅ Только родители могут наказывать
        guard isUserParent else {
            HapticFeedback.notification(.error)
            return
        }
        
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        // Обновляем баланс в UserDefaults (синхронизация)
        let currentBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
        let newBalance = max(0, currentBalance - 10)
        UnicornRewardsStore.writeBalance(newBalance, for: rewardsScopeChildId)
        
        unicornBalance = newBalance
        dismiss()
    }
}

#if DEBUG
struct RewardsQuickModal_Previews: PreviewProvider {
    static var previews: some View {
        RewardsQuickModal(unicornBalance: .constant(245))
    }
}
#endif



