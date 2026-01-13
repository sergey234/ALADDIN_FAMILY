import SwiftUI

/**
 * ⚙️ Component Settings Modal
 * Базовое модальное окно для настроек компонентов
 * Используется как основа для модальных окон настроек
 */

struct ComponentSettingsModal<Content: View>: View {
    let componentId: String
    let title: String
    @Binding var isPresented: Bool
    let content: () -> Content
    let onSave: (() -> Void)?
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var hasChanges: Bool = false
    
    init(
        componentId: String,
        title: String,
        isPresented: Binding<Bool>,
        onSave: (() -> Void)? = nil,
        @ViewBuilder content: @escaping () -> Content
    ) {
        self.componentId = componentId
        self.title = title
        self._isPresented = isPresented
        self.onSave = onSave
        self.content = content
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        content()
                    }
                    .padding(Spacing.m)
                }
            }
            .navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: {
                        isPresented = false
                    }) {
                        Text(localizationManager.localized("common.cancel"))
                            .foregroundColor(.textPrimary)
                    }
                    .accessibilityLabel("Cancel")
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    if let onSave = onSave {
                        Button(action: {
                            onSave()
                            isPresented = false
                        }) {
                            Text(localizationManager.localized("common.save"))
                                .foregroundColor(.blue)
                                .fontWeight(.semibold)
                        }
                        .accessibilityLabel("Save")
                        .disabled(!hasChanges)
                    }
                }
            }
        }
        .accessibilityElement(children: .contain)
    }
}

