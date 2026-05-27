import SwiftUI

/// P1-02: настройки согласия родителя на AI-компаньона (семейный scope).
struct CompanionParentConsentSection: View {
    @State private var childCanUseCompanion = true
    @State private var memoryEnabled = false
    @State private var allowUnicorn = true
    @State private var allowAladdin = false
    @State private var isLoading = true
    @State private var isSaving = false
    @State private var statusMessage: String?
    @State private var errorText: String?

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: 8) {
                Text("🦄")
                    .font(.title2)
                Text("AI-компаньон для детей")
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }

            Text("Родитель решает, может ли ребёнок общаться с героями и сохранять ли память разговоров (152-ФЗ / COPPA).")
                .font(.caption)
                .foregroundColor(.textSecondary)

            if isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity)
            } else {
                consentToggle(
                    title: "Разрешить «Разговор с героем»",
                    subtitle: "Ребёнок видит кнопку в Играх и может писать герою",
                    isOn: $childCanUseCompanion
                )

                consentToggle(
                    title: "Память компаньона",
                    subtitle: "Краткие безопасные заметки для персонализации (экспорт и удаление ниже)",
                    isOn: $memoryEnabled
                )
                .disabled(!childCanUseCompanion)
                .opacity(childCanUseCompanion ? 1 : 0.45)

                VStack(alignment: .leading, spacing: 8) {
                    Text("Разрешённые герои")
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    heroChip(id: "unicorn", emoji: "🦄", title: "Единорог", isOn: $allowUnicorn)
                    heroChip(id: "aladdin", emoji: "🧞", title: "Аладдин (13+)", isOn: $allowAladdin)
                }
                .disabled(!childCanUseCompanion)
                .opacity(childCanUseCompanion ? 1 : 0.45)

                Button {
                    Task { await save() }
                } label: {
                    HStack {
                        if isSaving { ProgressView().tint(.white) }
                        Text(isSaving ? "Сохраняем…" : "Сохранить настройки компаньона")
                    }
                    .font(.bodyBold)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                }
                .background(Color.purple.opacity(0.85), in: RoundedRectangle(cornerRadius: 12))
                .disabled(isSaving || (!allowUnicorn && !allowAladdin))

                if let statusMessage {
                    Text(statusMessage)
                        .font(.caption)
                        .foregroundColor(.green)
                }
                if let errorText {
                    Text(errorText)
                        .font(.caption)
                        .foregroundColor(.orange)
                }
            }
        }
        .padding(Spacing.m)
        .background(Color.purple.opacity(0.08))
        .cornerRadius(CornerRadius.medium)
        .task { await load() }
        .onChange(of: childCanUseCompanion) { enabled in
            if !enabled {
                memoryEnabled = false
            }
        }
    }

    @ViewBuilder
    private func consentToggle(title: String, subtitle: String, isOn: Binding<Bool>) -> some View {
        Toggle(isOn: isOn) {
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.weight(.semibold))
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
        }
        .tint(Color.purple)
    }

    @ViewBuilder
    private func heroChip(id: String, emoji: String, title: String, isOn: Binding<Bool>) -> some View {
        Button {
            isOn.wrappedValue.toggle()
        } label: {
            HStack {
                Text(emoji)
                Text(title)
                    .font(.subheadline)
                Spacer()
                Image(systemName: isOn.wrappedValue ? "checkmark.circle.fill" : "circle")
                    .foregroundColor(isOn.wrappedValue ? .purple : .secondary)
            }
            .padding(10)
            .background(Color.backgroundMedium.opacity(0.35))
            .cornerRadius(10)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("companion_consent_hero_\(id)")
    }

    private func load() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            let s = try await CompanionAPIService.shared.fetchConsent()
            childCanUseCompanion = s.childCanUseCompanion
            memoryEnabled = s.memoryEnabled
            allowUnicorn = s.allowedCharacters.contains("unicorn")
            allowAladdin = s.allowedCharacters.contains("aladdin")
            if !allowUnicorn && !allowAladdin {
                allowUnicorn = true
            }
        } catch {
            errorText = "Не удалось загрузить настройки: \(error.localizedDescription)"
        }
    }

    private func save() async {
        isSaving = true
        errorText = nil
        statusMessage = nil
        defer { isSaving = false }

        var chars: [String] = []
        if allowUnicorn { chars.append("unicorn") }
        if allowAladdin { chars.append("aladdin") }
        guard !chars.isEmpty else {
            errorText = "Выберите хотя бы одного героя."
            return
        }

        let payload = CompanionConsentSettings(
            memoryEnabled: memoryEnabled && childCanUseCompanion,
            childCanUseCompanion: childCanUseCompanion,
            allowedCharacters: chars
        )

        do {
            _ = try await CompanionAPIService.shared.updateConsent(payload)
            statusMessage = "Сохранено для всей семьи."
            NotificationCenter.default.post(name: .companionConsentDidSave, object: nil)
            HapticFeedback.impact(.light)
        } catch {
            errorText = error.localizedDescription
        }
    }
}
