import SwiftUI

/**
 * 👨‍👩‍👧‍👦 Add Member Options Screen
 * Экран выбора способа добавления члена семьи
 * 
 * Варианты:
 * 1. Создать новую семью (MainScreenWithRegistration)
 * 2. Сканировать QR-код (QRScannerModal)
 * 3. Ввести код приглашения (InvitationCodeInputModal)
 */

struct AddMemberOptionsScreen: View {
    
    // MARK: - Properties
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var subscriptionManager: SubscriptionManager // Single source for tariff limits
    @State private var isProcessingCreateFamily: Bool = false // ✅ Защита от двойного клика

    /// Уже есть семья на устройстве — первый сценарий ведёт в addFamilyMember (через admin_add_mode), а не в family/create.
    private var hasExistingFamilyOnDevice: Bool {
        let fid = (UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return !fid.isEmpty
    }

    /// Число участников для баннера лимита (из кэша).
    private var cachedFamilyMemberCount: Int {
        guard let data = UserDefaults.standard.data(forKey: FamilyLocalStore.familyMembersKey),
              let list = try? JSONDecoder().decode([FamilyMemberData].self, from: data) else { return 0 }
        return list.count
    }

    /// Ростер из UserDefaults (как на FamilyScreen) — для проверки прав до «добавить в текущую семью».
    private var cachedFamilyMembersForRoster: [FamilyMemberData] {
        guard let data = UserDefaults.standard.data(forKey: FamilyLocalStore.familyMembersKey),
              let list = try? JSONDecoder().decode([FamilyMemberData].self, from: data) else { return [] }
        return list
    }

    /// Тот же критерий, что `canManageFamilyRoster` на экране семьи (родитель/пожилой в списке).
    private var canManageFamilyRosterFromCache: Bool {
        FamilyRosterAccess.canManageRoster(
            members: cachedFamilyMembersForRoster,
            myMemberId: UserDefaults.standard.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey),
            currentUserRoleFallback: UserDefaults.standard.string(forKey: "current_user_role")
        )
    }
    
    // Temporary states for navigation (will be removed in next cleanup)
    @State private var showCreateFamily: Bool = false
    @State private var showQRScanner: Bool = false
    @State private var showCodeInput: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        GeometryReader { proxy in
            ZStack {
                // Фон
                LinearGradient(
                    colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                VStack(spacing: 20) {
                    // Кнопка назад — отступ с учётом safe area (Dynamic Island / чёлка)
                    HStack {
                        Button(action: {
                            navigationManager.goBack()
                        }) {
                            HStack {
                                Image(systemName: "chevron.left")
                                    .foregroundColor(.white)
                                Text(localizationManager.localized("common_back"))
                                    .foregroundColor(.white)
                            }
                        }
                        Spacer()
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, max(20, proxy.safeAreaInsets.top + 12))
                
                // Заголовок + Limit Banner (consistent with FamilyScreen)
                VStack(spacing: 8) {
                    Text(localizationManager.localized("add_member_title"))
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text(localizationManager.localized("add_member_subtitle"))
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.8))
                }
                .padding(.top, 10)

                // Limit banner using single source of truth
                let currentCount = cachedFamilyMemberCount
                let (canAddHere, limitMessage, _) = subscriptionManager.canAddFamilyMember(currentCount: currentCount)
                if !canAddHere, let msg = limitMessage {
                    Text(msg)
                        .font(.caption)
                        .foregroundColor(.orange)
                        .multilineTextAlignment(.center)
                        .padding()
                        .background(Color.orange.opacity(0.1))
                        .cornerRadius(8)
                        .padding(.horizontal, 20)
                }
                
                // Варианты добавления
                VStack(spacing: 12) {
                    // Вариант 1: новая семья ИЛИ добавление в текущую — только родитель/пожилой в ростере (QR/код ниже доступны всем для присоединения).
                    VStack(alignment: .leading, spacing: 6) {
                        optionButton(
                            icon: "plus.circle.fill",
                            title: localizationManager.localized(
                                hasExistingFamilyOnDevice ? "add_member_to_current_family" : "add_member_create_family"
                            ),
                            description: localizationManager.localized(
                                hasExistingFamilyOnDevice ? "add_member_to_current_family_desc" : "add_member_create_family_desc"
                            ),
                            color: .orange,
                            enabled: canManageFamilyRosterFromCache
                        ) {
                            // ✅ FIXED: Pure navigation - no internal modals
                            guard !isProcessingCreateFamily else {
                                print("⚠️ AddMemberOptionsScreen: Already processing create family, ignoring duplicate tap")
                                return
                            }

                            isProcessingCreateFamily = true
                            if hasExistingFamilyOnDevice {
                                UserDefaults.standard.set(true, forKey: "admin_add_mode")
                                UserDefaults.standard.synchronize()
                                print("✅ AddMemberOptionsScreen: admin_add_mode ON → registration flow uses addFamilyMember for current family")
                            }
                            print("✅ AddMemberOptionsScreen: Navigating to registration (create or add-to-current)")

                            navigationManager.navigateTo(.mainWithRegistration)

                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                                isProcessingCreateFamily = false
                            }
                        }
                        if !canManageFamilyRosterFromCache {
                            Text(localizationManager.currentLanguage == .russian
                                 ? "Этот пункт только для родителя (или пожилого) в семье. Присоединиться по QR или коду можно ниже."
                                 : "This option is for a parent (or elderly member) in the family. Use QR or code below to join.")
                                .font(.caption2)
                                .foregroundColor(.orange.opacity(0.95))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    
                    // Вариант 2: Сканировать QR-код
                    optionButton(
                        icon: "qrcode.viewfinder",
                        title: localizationManager.localized("add_member_scan_qr"),
                        description: localizationManager.localized("add_member_scan_qr_desc"),
                        color: .blue
                    ) {
                        navigationManager.navigateTo(.qrCode)
                    }
                    
                    // Вариант 3: Ввести код приглашения
                    optionButton(
                        icon: "textformat.123",
                        title: localizationManager.localized("add_member_enter_code"),
                        description: localizationManager.localized("add_member_enter_code_desc"),
                        color: .green
                    ) {
                        navigationManager.navigateTo(.invitationCode)
                    }
                }
                
                // Текст о конфиденциальности
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "lock.shield.fill")
                            .font(.system(size: 16))
                            .foregroundColor(.blue)
                        Text(localizationManager.localized("add_member_privacy_title"))
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.primary)
                    }
                    
                    Text(localizationManager.localized("add_member_privacy_text"))
                        .font(.system(size: 12))
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding(16)
                .background(Color.blue.opacity(0.05))
                .cornerRadius(12)
                
                Spacer()
                
                // Кнопка отмены
                Button(localizationManager.localized("add_member_cancel")) {
                    // ✅ ИСПРАВЛЕНИЕ: Используем navigationManager.goBack() для правильной навигации
                    navigationManager.goBack()
                }
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity)
                .frame(height: 44)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(12)
                .padding(.bottom, 20)
            }
            .padding(.horizontal, 20)
            .id("add_member_screen_lang_\(localizationManager.currentLanguage.rawValue)")
            }
            }
        // ✅ FIXED: Removed all internal .fullScreenCover and .sheet to prevent "single sheet is supported" warning
        // Now uses pure NavigationManager navigation (no nested presentation)
        .onChange(of: showCreateFamily) { newValue in
            if newValue {
                // Navigate instead of using fullScreenCover
                showCreateFamily = false
                navigationManager.navigateTo(.mainWithRegistration)
            }
        }
        .onChange(of: showQRScanner) { newValue in
            if newValue {
                showQRScanner = false
                navigationManager.navigateTo(.qrCode)
            }
        }
        .onChange(of: showCodeInput) { newValue in
            if newValue {
                showCodeInput = false
                navigationManager.navigateTo(.invitationCode)
            }
        }
    }
    
    // MARK: - Navigation Helpers
    
    // Simplified - most navigation now happens directly via NavigationManager
    private func checkRoleAndNavigate() {
        print("✅ [AddMemberOptionsScreen] Registration completed - navigating to family")
        dismiss()
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            if navigationManager.navigationStack.isEmpty {
                navigationManager.navigationStack = [.main]
            }
            navigationManager.navigateTo(.family)
        }
    }
    
    // MARK: - Option Button
    
    private func optionButton(
        icon: String,
        title: String,
        description: String,
        color: Color,
        enabled: Bool = true,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: {
            guard enabled else {
                UINotificationFeedbackGenerator().notificationOccurred(.warning)
                return
            }
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
            action()
        }) {
            HStack(spacing: 16) {
                Image(systemName: icon)
                    .font(.system(size: 28))
                    .foregroundColor(color)
                    .frame(width: 50, height: 50)
                    .background(
                        Circle()
                            .fill(color.opacity(0.15))
                    )
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.primary)
                    
                    Text(description)
                        .font(.system(size: 13))
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.secondary)
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.gray.opacity(0.05))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(color.opacity(0.3), lineWidth: 1)
                    )
            )
            .opacity(enabled ? 1 : 0.48)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Preview

struct AddMemberOptionsScreen_Previews: PreviewProvider {
    static var previews: some View {
        AddMemberOptionsScreen()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}
