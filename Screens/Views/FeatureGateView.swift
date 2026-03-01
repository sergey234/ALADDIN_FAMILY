//
//  FeatureGateView.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2025 ALADDIN. All rights reserved.
//
//  🛡️ CRITICAL SECURITY COMPONENT - Feature Access Control
//  Universal UI blocking component for subscription-based features
//  Protects premium functions from unauthorized access
//

import SwiftUI

/// 🛡️ Feature Gate View - Universal UI Blocking Component
/// Блокирует доступ к премиум функциям с замками и upgrade prompts
struct FeatureGateView<Content: View>: View {

    // MARK: - Properties

    /// Контент, который нужно защитить
    let content: Content

    /// ID функции для проверки доступа
    let featureId: String

    /// Требуемый уровень подписки
    let requiredLevel: SubscriptionLevel

    /// Сообщение о блокировке
    let lockMessage: String?

    /// Показывать upgrade prompt
    let showUpgradePrompt: Bool

    /// Тип блокировки
    let gateType: GateType

    // MARK: - Environment

    @EnvironmentObject private var subscriptionManager: SubscriptionManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    // MARK: - State

    @State private var showingUpgradePrompt = false
    @State private var isAnimating = false

    // MARK: - Types

    enum GateType {
        case lock      // Замок с оверлеем
        case blur      // Blur эффект
        case disabled  // Серый и неактивный
        case hidden    // Полностью скрытый
    }

    // MARK: - Initialization

    init(
        featureId: String,
        requiredLevel: SubscriptionLevel = .premium,
        lockMessage: String? = nil,
        showUpgradePrompt: Bool = true,
        gateType: GateType = .lock,
        @ViewBuilder content: () -> Content
    ) {
        self.featureId = featureId
        self.requiredLevel = requiredLevel
        self.lockMessage = lockMessage
        self.showUpgradePrompt = showUpgradePrompt
        self.gateType = gateType
        self.content = content()
    }

    // MARK: - Body

    var body: some View {
        ZStack {
            // Основной контент
            content
                .opacity(gateType == .disabled && !isFeatureAccessible ? 0.5 : 1.0)
                .blur(radius: gateType == .blur && !isFeatureAccessible ? 3 : 0)
                .disabled(gateType == .disabled && !isFeatureAccessible)

            // Оверлей блокировки
            if !isFeatureAccessible && gateType != .hidden {
                lockOverlay
                    .transition(.opacity.animation(.easeInOut(duration: 0.3)))
            }
        }
        .sheet(isPresented: $showingUpgradePrompt) {
            upgradePromptSheet
        }
        .onTapGesture {
            if !isFeatureAccessible && showUpgradePrompt {
                showingUpgradePrompt = true
                isAnimating = true

                // Анимация для привлечения внимания
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                        isAnimating = false
                    }
                }
            }
        }
    }

    // MARK: - Computed Properties

    /// Проверяет доступ к функции
    private var isFeatureAccessible: Bool {
        subscriptionManager.canAccessFeature(featureId)
    }

    /// Текущий уровень подписки пользователя
    private var currentLevel: SubscriptionLevel {
        subscriptionManager.getCurrentLevel()
    }

    /// Нужно ли показать upgrade
    private var shouldShowUpgrade: Bool {
        currentLevel.numericLevel < requiredLevel.numericLevel
    }

    // MARK: - Subviews

    /// 🛡️ Оверлей блокировки с замком
    private var lockOverlay: some View {
        ZStack {
            // Полупрозрачный фон
            Color.black.opacity(0.3)
                .ignoresSafeArea()

            // Контент блокировки
            VStack(spacing: Spacing.l) {
                // Иконка замка
                ZStack {
                    Circle()
                        .fill(Color.white.opacity(0.9))
                        .frame(width: 80, height: 80)
                        .shadow(color: Color.black.opacity(0.2), radius: 10)

                    Image(systemName: "lock.fill")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.orange)
                        .scaleEffect(isAnimating ? 1.2 : 1.0)
                }
                .scaleEffect(isAnimating ? 1.1 : 1.0)

                // Сообщение
                VStack(spacing: Spacing.s) {
                    Text(lockMessage ?? defaultLockMessage)
                        .font(.headline)
                        .foregroundColor(.white)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, Spacing.l)

                    if shouldShowUpgrade {
                        Text(upgradeMessage)
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.8))
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, Spacing.l)
                    }
                }

                // Кнопка апгрейда
                if shouldShowUpgrade && showUpgradePrompt {
                    Button(action: {
                        showingUpgradePrompt = true
                    }) {
                        Text(localizationManager.localized("feature_gate_upgrade_button"))
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding(.horizontal, Spacing.xl)
                            .padding(.vertical, Spacing.m)
                            .background(Color.orange)
                            .cornerRadius(25)
                            .shadow(color: Color.orange.opacity(0.3), radius: 5)
                    }
                    .scaleEffect(isAnimating ? 1.05 : 1.0)
                }
            }
            .padding(Spacing.xl)
        }
    }

    /// 💰 Upgrade Prompt Sheet
    private var upgradePromptSheet: some View {
        VStack(spacing: Spacing.xl) {
            // Заголовок
            VStack(spacing: Spacing.s) {
                Image(systemName: "crown.fill")
                    .font(.system(size: 48))
                    .foregroundColor(.orange)

                Text(localizationManager.localized("feature_gate_premium_required"))
                    .font(.title)
                    .fontWeight(.bold)

                Text(String(format: localizationManager.localized("feature_gate_upgrade_description"),
                           requiredLevel.displayName))
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
            .padding(.top, Spacing.xl)

            // Преимущества премиум
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("feature_gate_premium_benefits"))
                    .font(.headline)
                    .padding(.bottom, Spacing.s)

                benefitRow(icon: "checkmark.circle.fill", text: localizationManager.localized("feature_gate_benefit_1"))
                benefitRow(icon: "checkmark.circle.fill", text: localizationManager.localized("feature_gate_benefit_2"))
                benefitRow(icon: "checkmark.circle.fill", text: localizationManager.localized("feature_gate_benefit_3"))
                benefitRow(icon: "checkmark.circle.fill", text: localizationManager.localized("feature_gate_benefit_4"))
            }
            .padding(.horizontal, Spacing.xl)

            Spacer()

            // Кнопки действий
            VStack(spacing: Spacing.m) {
                // Кнопка апгрейда
                Button(action: upgradeToPremium) {
                    Text(String(format: localizationManager.localized("feature_gate_upgrade_to"),
                               requiredLevel.displayName))
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.m)
                        .background(Color.orange)
                        .cornerRadius(12)
                        .shadow(color: Color.orange.opacity(0.3), radius: 5)
                }

                // Кнопка отмены
                Button(action: {
                    showingUpgradePrompt = false
                }) {
                    Text(localizationManager.localized("feature_gate_maybe_later"))
                        .font(.body)
                        .foregroundColor(.secondary)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.m)
                }
            }
            .padding(.horizontal, Spacing.xl)
            .padding(.bottom, Spacing.xl)
        }
        .background(Color(.systemBackground))
        .cornerRadius(20)
        .shadow(color: Color.black.opacity(0.1), radius: 10)
        .ignoresSafeArea(edges: .bottom)
    }

    // MARK: - Helper Views

    private func benefitRow(icon: String, text: String) -> some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: icon)
                .foregroundColor(.green)
                .font(.title3)

            Text(text)
                .font(.body)

            Spacer()
        }
    }

    // MARK: - Messages

    private var defaultLockMessage: String {
        String(format: localizationManager.localized("feature_gate_locked"),
               requiredLevel.displayName)
    }

    private var upgradeMessage: String {
        localizationManager.localized("feature_gate_tap_to_upgrade")
    }

    // MARK: - Actions

    private func upgradeToPremium() {
        showingUpgradePrompt = false

        // Навигация к тарифам
        navigationManager.navigateTo(.tariffs)

        // Логирование
        MasterLogger.shared.business("User initiated upgrade from FeatureGate: \(featureId)")
    }
}

// MARK: - Convenience Initializers

extension FeatureGateView {

    /// Простая блокировка премиум функций
    init(premium content: () -> Content) where Content: View {
        self.init(
            featureId: "premium_feature",
            requiredLevel: .premium,
            gateType: .lock,
            content: content
        )
    }

    /// Блокировка с кастомным сообщением
    init(
        _ featureId: String,
        message: String,
        content: () -> Content
    ) where Content: View {
        self.init(
            featureId: featureId,
            lockMessage: message,
            content: content
        )
    }

    /// Blur эффект для премиум контента
    init(blurred content: () -> Content) where Content: View {
        self.init(
            featureId: "premium_feature",
            gateType: .blur,
            content: content
        )
    }

    /// Полностью скрытый премиум контент
    init(hidden content: () -> Content) where Content: View {
        self.init(
            featureId: "premium_feature",
            requiredLevel: .premium,
            lockMessage: nil,
            showUpgradePrompt: false,
            gateType: .hidden,
            content: content
        )
    }
}

// MARK: - Preview

#if DEBUG
struct FeatureGateView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            // Premium locked content
            FeatureGateView(
                featureId: "ai_assistant_advanced",
                requiredLevel: .premium,
                lockMessage: "Advanced AI features require Premium subscription"
            ) {
                VStack {
                    Text("🤖 Advanced AI Assistant")
                        .font(.title)
                    Text("Ask complex questions and get detailed analysis")
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color.blue.opacity(0.1))
                .cornerRadius(12)
            }
            .environmentObject(SubscriptionManager.shared)
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
            .previewDisplayName("Premium Locked")

            // Family locked content
            FeatureGateView(
                featureId: "parental_control_advanced",
                requiredLevel: .family,
                lockMessage: "Advanced parental controls require Family or Premium"
            ) {
                VStack {
                    Text("👨‍👩‍👧 Family Protection")
                        .font(.title)
                    Text("Monitor and control multiple family devices")
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color.green.opacity(0.1))
                .cornerRadius(12)
            }
            .environmentObject(SubscriptionManager.shared)
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
            .previewDisplayName("Family Locked")
        }
    }
}
#endif