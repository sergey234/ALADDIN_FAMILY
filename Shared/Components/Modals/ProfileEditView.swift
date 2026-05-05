import SwiftUI
import UIKit

/// 👤 Profile Edit View
/// Модальное окно редактирования профиля пользователя
struct ProfileEditView: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @AppStorage("profile_name") private var storedName: String = ""
    @AppStorage("profile_alias") private var storedAlias: String = ""
    
    @State private var name: String = ""
    @State private var alias: String = ""
    @State private var showImagePicker: Bool = false
    @State private var selectedImage: UIImage?
    @State private var showPasswordResetSheet: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ZStack {
                // Фон
                LinearGradient(
                    colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                    .ignoresSafeArea()
                    .accessibilityElement(children: .ignore)
                    .accessibilityLabel(localizationManager.localized("profile_edit_background_accessibility"))
                
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(spacing: 20) {
                        // Аватар
                        avatarSection
                        
                        // Поля редактирования
                        editFields
                        
                        // Кнопки действий
                        actionButtons
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 20)
                    .padding(.bottom, 100)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("profile_edit_form_accessibility"))
            }
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(localizationManager.localized("profile_edit_title"))
                        .font(.headline)
                        .multilineTextAlignment(.center)
                        .lineLimit(2)
                }
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("profile_edit_cancel")) {
                        dismiss()
                    }
                    .foregroundColor(.blue)
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("profile_edit_save")) {
                        saveProfile()
                    }
                    .foregroundColor(.blue)
                    .font(.system(size: 16, weight: .semibold))
                }
            }
        }
        .sheet(isPresented: $showImagePicker) {
            ImagePicker(selectedImage: $selectedImage)
        }
        .sheet(isPresented: $showPasswordResetSheet) {
            PasswordResetSheet(initialEmail: PasswordResetEmailResolver.resolved(storedAlias: storedAlias))
                .environmentObject(localizationManager)
        }
        .onAppear {
            // Загружаем сохраненное фото при открытии
            selectedImage = ProfileImageManager.shared.loadProfileImage(for: .main)
            
            // Загружаем сохраненные значения из @AppStorage
            name = storedName
            alias = storedAlias
        }
    }
    
    // MARK: - Avatar Section
    
    private var avatarSection: some View {
        VStack(spacing: 16) {
            Text(localizationManager.localized("profile_edit_photo_title"))
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            Button(action: {
                showImagePicker = true
            }) {
                ZStack {
                    Circle()
                        .fill(LinearGradient(
                            colors: [.blue, .blue.opacity(0.7)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ))
                        .frame(width: 120, height: 120)
                        .overlay(
                            Group {
                                if let selectedImage = selectedImage {
                                    Image(uiImage: selectedImage)
                                        .resizable()
                                        .aspectRatio(contentMode: .fill)
                                        .frame(width: 120, height: 120)
                                        .clipShape(Circle())
                                } else {
                                    Text(avatarInitial)
                                        .font(.system(size: 40, weight: .bold))
                                        .foregroundColor(.white)
                                }
                            }
                        )
                    
                    // Кнопка редактирования
                    VStack {
                        Spacer()
                        HStack {
                            Spacer()
                            Circle()
                                .fill(Color.blue)
                                .frame(width: 32, height: 32)
                                .overlay(
                                    Image(systemName: "camera.fill")
                                        .font(.system(size: 14))
                                        .foregroundColor(.white)
                                )
                        }
                    }
                    .frame(width: 120, height: 120)
                }
            }
            .accessibilityLabel(localizationManager.localized("profile_edit_change_photo_accessibility"))
            
            Text(localizationManager.localized("profile_edit_photo_hint"))
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Edit Fields
    
    private var editFields: some View {
        VStack(spacing: 16) {
            Text(localizationManager.localized("profile_edit_info_title"))
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: 16) {
                // Имя
                editField(
                    title: localizationManager.localized("profile_edit_name_label"),
                    text: $name,
                    placeholder: localizationManager.localized("profile_edit_name_placeholder"),
                    icon: "person.fill"
                )
                
                editField(
                    title: localizationManager.localized("profile_edit_email_label"),
                    text: $alias,
                    placeholder: localizationManager.localized("profile_edit_email_placeholder"),
                    icon: "character.textbox"
                )
                
            }
        }
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Action Buttons
    
    private var actionButtons: some View {
        VStack(spacing: 16) {
            // Сохранить изменения
            Button(action: {
                saveProfile()
            }) {
                HStack(spacing: 12) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 16))
                    
                    Text(localizationManager.localized("profile_edit_save_changes"))
                        .font(.body)
                        .fontWeight(.bold)
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 16)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(LinearGradient(
                            colors: [.blue, .blue.opacity(0.7)],
                            startPoint: .leading,
                            endPoint: .trailing
                        ))
                )
            }
            .accessibilityLabel(localizationManager.localized("profile_edit_save_changes_accessibility"))
            
            // Сбросить пароль
            Button(action: {
                resetPassword()
            }) {
                HStack(spacing: 12) {
                    Image(systemName: "key.fill")
                        .font(.system(size: 16))
                    
                    Text(localizationManager.localized("profile_edit_reset_password"))
                        .font(.body)
                        .fontWeight(.bold)
                }
                .foregroundColor(.blue)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 16)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.blue.opacity(0.1))
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.blue, lineWidth: 1)
                        )
                )
            }
            .accessibilityLabel(localizationManager.localized("profile_edit_reset_password_accessibility"))
        }
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
    private func editField(
        title: String,
        text: Binding<String>,
        placeholder: String,
        icon: String,
        keyboardType: UIKeyboardType = .default
    ) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.body)
                .fontWeight(.bold)
                .foregroundColor(.primary)
            
            HStack(spacing: 16) {
                Image(systemName: icon)
                    .font(.system(size: 16))
                    .foregroundColor(.blue)
                    .frame(width: 20)
                
                TextField(placeholder, text: text)
                    .font(.body)
                    .foregroundColor(.primary)
                    .keyboardType(keyboardType)
                    .textFieldStyle(PlainTextFieldStyle())
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.gray.opacity(0.3))
            )
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(text.wrappedValue)")
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: 16)
            .fill(Color.gray.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    // MARK: - Actions
    
    private func saveProfile() {
        // Сохранение профиля в @AppStorage
        storedName = name.trimmingCharacters(in: .whitespacesAndNewlines)
        storedAlias = alias.trimmingCharacters(in: .whitespacesAndNewlines)
        
        print("✅ Profile saved: name=\(storedName), alias=\(storedAlias)")
        
        // Сохраняем фото профиля, если оно было выбрано
        if let image = selectedImage {
            _ = ProfileImageManager.shared.saveProfileImage(image, for: .main)
            print("✅ Profile image saved")
        }
        
        dismiss()
    }
    
    private func resetPassword() {
        showPasswordResetSheet = true
    }
    
    private var avatarInitial: String {
        let trimmed = name.trimmingCharacters(in: .whitespacesAndNewlines)
        if let first = trimmed.first {
            return String(first).uppercased()
        }
        return localizationManager.localized("profile_edit_initial_placeholder")
    }
}

// MARK: - Image Picker

struct ImagePicker: UIViewControllerRepresentable {
    @Binding var selectedImage: UIImage?
    @Environment(\.dismiss) private var dismiss
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .photoLibrary
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePicker
        
        init(_ parent: ImagePicker) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let image = info[.originalImage] as? UIImage {
                parent.selectedImage = image
            }
            parent.dismiss()
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }
}

// MARK: - Preview

struct ProfileEditView_Previews: PreviewProvider {
    static var previews: some View {
        ProfileEditView()
            .environmentObject(LocalizationManager())
    }
}
