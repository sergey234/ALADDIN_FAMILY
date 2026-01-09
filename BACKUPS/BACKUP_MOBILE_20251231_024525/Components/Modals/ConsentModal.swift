import SwiftUI

struct ConsentModal: View {
    @Binding var isPresented: Bool
    let onConsentGiven: () -> Void
    @State private var showFullConsent: Bool = false
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Заголовок
                    VStack(spacing: 12) {
                        Image(systemName: "hand.raised.fill")
                            .font(.system(size: 50))
                            .foregroundColor(.blue)
                        
                        Text(localizationManager.localized("consent_modal_title"))
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("consent_modal_description"))
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    
                    // Текст согласия
                    VStack(alignment: .leading, spacing: 16) {
                        Text(localizationManager.localized("consent_modal_consent_title"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        VStack(alignment: .leading, spacing: 12) {
                            Text(localizationManager.localized("consent_modal_consent_text"))
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(.primary)
                            
                            VStack(alignment: .leading, spacing: 8) {
                                consentItem(localizationManager.localized("consent_modal_item_family_account"))
                                consentItem(localizationManager.localized("consent_modal_item_role_age"))
                                consentItem(localizationManager.localized("consent_modal_item_qr_code"))
                                consentItem(localizationManager.localized("consent_modal_item_security_settings"))
                            }
                        }
                        
                        Text(localizationManager.localized("consent_modal_guarantees_title"))
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.primary)
                            .padding(.top, 8)
                        
                        VStack(alignment: .leading, spacing: 8) {
                            consentItem(localizationManager.localized("consent_modal_guarantee_no_phone_email"))
                            consentItem(localizationManager.localized("consent_modal_guarantee_no_third_party"))
                            consentItem(localizationManager.localized("consent_modal_guarantee_app_only"))
                            consentItem(localizationManager.localized("consent_modal_guarantee_security"))
                        }
                    }
                    .padding(20)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(12)
                    
                    // Кнопка "Читать полный текст"
                    Button(action: {
                        withAnimation(.spring(response: 0.5, dampingFraction: 0.8)) {
                            showFullConsent.toggle()
                        }
                    }) {
                        HStack {
                            Text(showFullConsent ? localizationManager.localized("consent_modal_hide_full") : localizationManager.localized("consent_modal_read_full"))
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.blue)
                            
                            Image(systemName: showFullConsent ? "chevron.up" : "chevron.down")
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundColor(.blue)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(12)
                    }
                    
                    // Раздвигающийся блок с полным текстом согласия
                    if showFullConsent {
                        VStack(alignment: .leading, spacing: 16) {
                            Text(localizationManager.localized("consent_modal_full_title"))
                                .font(.system(size: 18, weight: .bold))
                                .foregroundColor(.primary)
                            
                            fullConsentText()
                        }
                        .padding(20)
                        .background(Color.blue.opacity(0.05))
                        .cornerRadius(12)
                        .transition(.move(edge: .top).combined(with: .opacity))
                    }
                    
                    // Кнопки
                    VStack(spacing: 12) {
                        Button(action: {
                            onConsentGiven()
                            isPresented = false
                        }) {
                            Text(localizationManager.localized("consent_modal_agree"))
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .frame(height: 50)
                                .background(Color.blue)
                                .cornerRadius(12)
                        }
                        
                        Button(localizationManager.localized("consent_modal_decline")) {
                            isPresented = false
                        }
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.secondary)
                    }
                }
                .padding(20)
            }
            .navigationTitle(localizationManager.localized("consent_modal_nav_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("consent_modal_close")) {
                        isPresented = false
                    }
                }
            }
            .id("consent_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        }
    }
    
    private func consentItem(_ text: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 14))
                .foregroundColor(.green)
                .padding(.top, 2)
            
            Text(text)
                .font(.system(size: 14))
                .foregroundColor(.primary)
        }
    }
    
    private func fullConsentText() -> some View {
        VStack(alignment: .leading, spacing: 12) {
            consentSection(
                title: localizationManager.localized("consent_modal_section_1_title"),
                text: localizationManager.localized("consent_modal_section_1_text")
            )
            
            consentSection(
                title: localizationManager.localized("consent_modal_section_2_title"),
                text: localizationManager.localized("consent_modal_section_2_text")
            )
            
            consentSection(
                title: localizationManager.localized("consent_modal_section_3_title"),
                text: localizationManager.localized("consent_modal_section_3_text")
            )
            
            consentSection(
                title: localizationManager.localized("consent_modal_section_4_title"),
                text: localizationManager.localized("consent_modal_section_4_text")
            )
            
            consentSection(
                title: localizationManager.localized("consent_modal_section_5_title"),
                text: localizationManager.localized("consent_modal_section_5_text")
            )
            
            consentSection(
                title: localizationManager.localized("consent_modal_section_6_title"),
                text: localizationManager.localized("consent_modal_section_6_text")
            )
            
            consentSection(
                title: localizationManager.localized("consent_modal_section_7_title"),
                text: localizationManager.localized("consent_modal_section_7_text")
            )
            
            consentSection(
                title: localizationManager.localized("consent_modal_section_8_title"),
                text: localizationManager.localized("consent_modal_section_8_text")
            )
        }
    }
    
    private func consentSection(title: String, text: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.system(size: 15, weight: .semibold))
                .foregroundColor(.primary)
            
            Text(text)
                .font(.system(size: 14))
                .foregroundColor(.secondary)
                .lineSpacing(4)
        }
        .padding(.vertical, 8)
    }
}

struct ConsentModal_Previews: PreviewProvider {
    @State static var isPresented = true
    
    static var previews: some View {
        ConsentModal(
            isPresented: $isPresented,
            onConsentGiven: {
                print("Consent given")
            }
        )
    }
}