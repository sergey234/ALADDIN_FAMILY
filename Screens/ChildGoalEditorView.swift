import SwiftUI

/// 🎯 Child Goal Editor View
/// Редактор цели ребёнка
/// Позволяет ребёнку установить свою цель и отправить запрос родителям
struct ChildGoalEditorView: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    
    // Данные для отправки родителям (AppStorage)
    @AppStorage("child_goal_title_pending") private var goalTitlePending: String = ""
    @AppStorage("child_goal_cost_pending") private var goalCostPending: Int = 0
    @AppStorage("child_goal_approval_pending") private var goalApprovalPending: Bool = false
    
    // Локальное состояние формы
    @State private var title: String = ""
    @State private var cost: String = ""
    @State private var showConfirmation: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Информационная карточка
                        infoCard
                        
                        // Форма установки цели
                        goalForm
                        
                        // Кнопка отправки
                        submitButton
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .alert(localizationManager.localized("child_goal_editor_success_title"), isPresented: $showConfirmation) {
            Button(localizationManager.localized("child_goal_editor_ok")) {
                HapticFeedback.impact(.medium)
                navigationManager.goBack()
            }
        } message: {
            Text(localizationManager.localized("child_goal_editor_success_message"))
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        HStack {
            Button(action: {
                HapticFeedback.impact(.light)
                navigationManager.goBack()
            }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.textPrimary)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.backgroundMedium.opacity(0.5))
                    )
            }
            
            Text(localizationManager.localized("child_goal_editor_title"))
                .font(.h2)
                .foregroundColor(.secondaryGold)
            
            Spacer()
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
    }
    
    // MARK: - Info Card
    
    private var infoCard: some View {
        HStack(spacing: Spacing.m) {
            Text("💡")
                .font(.system(size: 24))
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(localizationManager.localized("child_goal_editor_info_title"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("child_goal_editor_info_description"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.secondaryGold.opacity(0.15))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Goal Form
    
    private var goalForm: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Поле: название подарка
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(localizationManager.localized("child_goal_editor_goal_title"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                TextField(localizationManager.localized("child_goal_editor_placeholder"), text: $title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.5))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(title.isEmpty ? Color.textSecondary.opacity(0.3) : Color.secondaryGold.opacity(0.5), lineWidth: 1)
                    )
                
                Text(localizationManager.localized("child_goal_editor_goal_hint"))
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
            
            // Поле: стоимость
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(localizationManager.localized("child_goal_editor_cost_title"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                HStack(spacing: Spacing.s) {
                    TextField("100", text: $cost)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .keyboardType(.numberPad)
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.backgroundMedium.opacity(0.5))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(cost.isEmpty ? Color.textSecondary.opacity(0.3) : Color.secondaryGold.opacity(0.5), lineWidth: 1)
                        )
                    
                    Text("🦄")
                        .font(.system(size: 32))
                }
                
                Text(localizationManager.localized("child_goal_editor_cost_hint"))
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Submit Button
    
    private var submitButton: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            submitGoal()
        }) {
            HStack {
                Text(localizationManager.localized("child_goal_editor_submit_button"))
                    .font(.bodyBold)
                    .foregroundColor(.white)
                
                Spacer()
                
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.white.opacity(0.9))
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(canSubmit ? 
                          LinearGradient(
                              colors: [.secondaryGold, .warningOrange],
                              startPoint: .leading,
                              endPoint: .trailing
                          ) :
                          LinearGradient(
                              colors: [.textSecondary, .textSecondary],
                              startPoint: .leading,
                              endPoint: .trailing
                          )
                    )
            )
            .shadow(color: canSubmit ? Color.secondaryGold.opacity(0.3) : Color.clear, radius: 10, x: 0, y: 5)
        }
        .buttonStyle(PlainButtonStyle())
        .disabled(!canSubmit)
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Computed Properties
    
    private var canSubmit: Bool {
        !title.isEmpty && !cost.isEmpty && Int(cost) != nil && Int(cost)! > 0
    }
    
    // MARK: - Methods
    
    private func submitGoal() {
        guard let costValue = Int(cost), costValue > 0 else {
            return
        }
        
        // Сохраняем запрос в AppStorage
        goalTitlePending = title
        goalCostPending = costValue
        goalApprovalPending = true
        
        // Показываем подтверждение
        HapticFeedback.notification(.success)
        showConfirmation = true
    }
}


