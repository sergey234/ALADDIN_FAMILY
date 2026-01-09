import SwiftUI

/// ⚙️ Модальное окно настроек вознаграждений
/// Показывается при нажатии на кнопку шестерёнки на экране ChildRewardsScreen
struct ChildRewardsSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Настройки цели
    @AppStorage("child_goal_title") private var goalTitle: String = ""
    @AppStorage("child_goal_cost") private var goalCost: Int = 800
    @State private var editingGoalTitle: String = ""
    @State private var editingGoalCost: String = ""
    @State private var isEditingGoal: Bool = false
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Заголовок
                        VStack(spacing: Spacing.xs) {
                            Text(localizationManager.localized("child_rewards_settings_title"))
                                .font(.h2)
                                .foregroundColor(.textPrimary)
                            
                            Text(localizationManager.localized("child_rewards_settings_subtitle"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(.top, Spacing.xl)
                        .padding(.bottom, Spacing.m)
                        
                        // Настройки цели
                        goalSettingsCard
                        
                        // Информация
                        infoCard
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        HapticFeedback.selection()
                        isPresented = false
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
        .onAppear {
            editingGoalTitle = goalTitle
            editingGoalCost = String(goalCost)
        }
    }
    
    // MARK: - Goal Settings Card
    
    private var goalSettingsCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("🎯")
                    .font(.system(size: 24))
                
                Text(localizationManager.localized("child_rewards_settings_goal_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            
            Divider()
                .background(Color.textTertiary)
            
            // Название цели
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(localizationManager.localized("child_rewards_settings_goal_name_label"))
                    .font(.captionBold)
                    .foregroundColor(.textSecondary)
                
                if isEditingGoal {
                    TextField(localizationManager.localized("child_rewards_settings_goal_name_placeholder"), text: $editingGoalTitle)
                        .textFieldStyle(.roundedBorder)
                        .foregroundColor(.textPrimary)
                } else {
                    Text(goalTitle)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .padding(.vertical, Spacing.xs)
                }
            }
            
            // Стоимость цели
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(localizationManager.localized("child_rewards_settings_goal_cost_label"))
                    .font(.captionBold)
                    .foregroundColor(.textSecondary)
                
                if isEditingGoal {
                    TextField(localizationManager.localized("child_rewards_settings_goal_cost_placeholder"), text: $editingGoalCost)
                        .textFieldStyle(.roundedBorder)
                        .keyboardType(.numberPad)
                        .foregroundColor(.textPrimary)
                } else {
                    Text("\(goalCost) 🦄")
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .padding(.vertical, Spacing.xs)
                }
            }
            
            // Кнопка редактирования/сохранения
            Button(action: {
                HapticFeedback.selection()
                if isEditingGoal {
                    // Сохраняем изменения
                    goalTitle = editingGoalTitle
                    if let cost = Int(editingGoalCost), cost > 0 {
                        goalCost = cost
                    }
                }
                withAnimation {
                    isEditingGoal.toggle()
                }
            }) {
                HStack {
                    Text(isEditingGoal ? 
                         localizationManager.localized("child_rewards_settings_save_button") :
                         localizationManager.localized("child_rewards_settings_edit_button"))
                        .font(.body)
                        .fontWeight(.semibold)
                    
                    Spacer()
                    
                    Image(systemName: isEditingGoal ? "checkmark.circle.fill" : "pencil.circle.fill")
                        .font(.system(size: 20))
                }
                .foregroundColor(.white)
                .padding(.vertical, Spacing.s)
                .padding(.horizontal, Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(isEditingGoal ? Color.successGreen : Color.secondaryGold)
                )
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
    }
    
    // MARK: - Info Card
    
    private var infoCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("ℹ️")
                    .font(.system(size: 24))
                
                Text(localizationManager.localized("child_rewards_settings_info_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            
            Divider()
                .background(Color.textTertiary)
            
            Text(localizationManager.localized("child_rewards_settings_info_text"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.primaryBlue.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
    }
}

#if DEBUG
struct ChildRewardsSettingsModal_Previews: PreviewProvider {
    static var previews: some View {
        ChildRewardsSettingsModal(isPresented: .constant(true))
            .environmentObject(LocalizationManager())
    }
}
#endif

