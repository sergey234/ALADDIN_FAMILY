import SwiftUI
import UIKit
import PhotosUI

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
    @State private var pendingCropImage: UIImage?
    @State private var showAvatarCrop: Bool = false
    @State private var showPasswordResetSheet: Bool = false
    
    // MARK: - Body
    
    private var hasChanges: Bool {
        name != storedName || alias != storedAlias
    }

    var body: some View {
        profileEditNavigation
        .sheet(isPresented: $showImagePicker) {
            ImagePicker(selectedImage: $pendingCropImage)
        }
        .sheet(isPresented: $showAvatarCrop) {
            if let pendingCropImage {
                AvatarCropEditor(
                    image: pendingCropImage,
                    onCommit: { cropped in
                        // QA-01 A: persist photo immediately (same path as Hub), Save = name/email.
                        selectedImage = cropped
                        _ = ProfileImageManager.shared.saveProfileImage(cropped, for: .main)
                        showAvatarCrop = false
                        self.pendingCropImage = nil
                        HapticFeedback.notification(.success)
                        ToastManager.shared.showSuccess(
                            localizationManager.localized("profile_edit_photo_saved")
                        )
                    },
                    onCancel: {
                        showAvatarCrop = false
                        self.pendingCropImage = nil
                    }
                )
                .environmentObject(localizationManager)
            }
        }
        .onChange(of: pendingCropImage) { img in
            guard img != nil else { return }
            showAvatarCrop = true
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

    @ViewBuilder
    private var profileEditNavigation: some View {
        if #available(iOS 16.0, *) {
            NavigationStack {
                profileEditForm
            }
        } else {
            NavigationView {
                profileEditForm
            }
            .navigationViewStyle(StackNavigationViewStyle())
        }
    }

    private var profileEditForm: some View {
        ZStack {
            StormMeshBackground(variant: .neutral)
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(localizationManager.localized("profile_edit_background_accessibility"))

            ScrollView(.vertical, showsIndicators: true) {
                VStack(spacing: 24) {
                    avatarSection
                    editFields
                    resetPasswordRow
                }
                .padding(.horizontal, 20)
                .padding(.top, 20)
                .padding(.bottom, 40)
            }
            .accessibilityElement(children: .contain)
            .accessibilityLabel(localizationManager.localized("profile_edit_form_accessibility"))
        }
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
        .modifier(StormHiddenNavBarModifier())
        .aladdinToolbar {
            ToolbarItem(placement: .principal) {
                Text(localizationManager.localized("profile_edit_title"))
                    .font(AladdinFamilyType.body(weight: .semibold))
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
                    .lineLimit(1)
                    .minimumScaleFactor(0.85)
            }
            ToolbarItem(placement: .navigationBarLeading) {
                Button(localizationManager.localized("profile_edit_cancel")) {
                    dismiss()
                }
                .font(AladdinFamilyType.body())
                .foregroundColor(.white)
            }
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(localizationManager.localized("profile_edit_save")) {
                    saveProfile()
                }
                .font(AladdinFamilyType.body(weight: .semibold))
                .foregroundColor(hasChanges ? Color.secondaryGold : Color.white.opacity(0.35))
                .disabled(!hasChanges)
            }
        }
    }
    
    // MARK: - Avatar Section
    
    private var avatarSection: some View {
        VStack(spacing: 12) {
            Button(action: {
                showImagePicker = true
            }) {
                ZStack {
                    Circle()
                        .fill(Color.black.opacity(0.35))
                        .frame(width: 96, height: 96)
                    if let selectedImage {
                        Image(uiImage: selectedImage)
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(width: 96, height: 96)
                            .clipShape(Circle())
                    } else if hasName {
                        Text(avatarInitial)
                            .font(AladdinFamilyType.title2())
                            .foregroundColor(.white)
                    } else {
                        Image(systemName: "person.crop.circle.fill")
                            .font(.system(size: 72))
                            .foregroundColor(.white.opacity(0.75))
                    }
                }
            }
            .accessibilityLabel(localizationManager.localized("profile_edit_avatar_a11y"))

            Button(action: {
                showImagePicker = true
            }) {
                Text(localizationManager.localized("profile_edit_photo_hint"))
                    .font(AladdinFamilyType.body())
                    .foregroundColor(Color.secondaryGold)
            }
            .accessibilityLabel(localizationManager.localized("profile_edit_photo_hint"))
        }
        .frame(maxWidth: .infinity)
    }
    
    // MARK: - Edit Fields
    
    private var editFields: some View {
        VStack(spacing: 16) {
            nameField
            emailField
        }
    }

    private var nameField: some View {
        fieldShell(title: localizationManager.localized("profile_edit_name_label"), value: name) {
            TextField(localizationManager.localized("profile_edit_name_placeholder"), text: $name)
                .font(AladdinFamilyType.body())
                .foregroundColor(.white)
                .textContentType(.name)
                .textFieldStyle(.plain)
        }
    }

    private var emailField: some View {
        fieldShell(title: localizationManager.localized("profile_edit_email_label"), value: alias) {
            TextField(localizationManager.localized("profile_edit_email_placeholder"), text: $alias)
                .font(AladdinFamilyType.body())
                .foregroundColor(.white)
                .keyboardType(.emailAddress)
                .textContentType(.emailAddress)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .textFieldStyle(.plain)
        }
    }

    private var resetPasswordRow: some View {
        Button(action: resetPassword) {
            HStack(spacing: 8) {
                Text(localizationManager.localized("profile_edit_reset_password"))
                    .font(AladdinFamilyType.body())
                Spacer()
                Image(systemName: "chevron.right")
                    .font(AladdinFamilyType.caption(weight: .semibold))
            }
            .foregroundColor(Color.secondaryGold)
            .padding(.vertical, 14)
            .padding(.horizontal, 16)
            .frame(maxWidth: .infinity)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.black.opacity(0.35))
            )
        }
        .buttonStyle(.plain)
        .accessibilityLabel(localizationManager.localized("profile_edit_reset_password_accessibility"))
    }
    
    // MARK: - Helper Views
    
    private func fieldShell<Content: View>(title: String, value: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(AladdinFamilyType.body(weight: .semibold))
                .foregroundColor(.white)
            content()
                .padding(16)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.black.opacity(0.35))
                )
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(value)")
    }
    
    // MARK: - Actions
    
    private func saveProfile() {
        // Сохранение профиля в @AppStorage
        storedName = name.trimmingCharacters(in: .whitespacesAndNewlines)
        storedAlias = alias.trimmingCharacters(in: .whitespacesAndNewlines)

        if let image = selectedImage {
            _ = ProfileImageManager.shared.saveProfileImage(image, for: .main)
        }
        
        dismiss()
    }
    
    private func resetPassword() {
        showPasswordResetSheet = true
    }
    
    private var hasName: Bool {
        !name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    private var avatarInitial: String {
        let trimmed = name.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let first = trimmed.first else { return "" }
        return String(first).uppercased()
    }
}

// MARK: - Image Picker

/// P1.5 S37: PHPicker (not UIImagePicker) — nested sheet + simulator photo library reliable.
struct ImagePicker: UIViewControllerRepresentable {
    @Binding var selectedImage: UIImage?
    @Environment(\.dismiss) private var dismiss

    func makeUIViewController(context: Context) -> PHPickerViewController {
        var config = PHPickerConfiguration(photoLibrary: .shared())
        config.filter = .images
        config.selectionLimit = 1
        let picker = PHPickerViewController(configuration: config)
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: PHPickerViewController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    final class Coordinator: NSObject, PHPickerViewControllerDelegate {
        let parent: ImagePicker

        init(_ parent: ImagePicker) {
            self.parent = parent
        }

        func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
            defer { parent.dismiss() }
            guard let provider = results.first?.itemProvider,
                  provider.canLoadObject(ofClass: UIImage.self) else { return }
            provider.loadObject(ofClass: UIImage.self) { object, _ in
                guard let image = object as? UIImage else { return }
                DispatchQueue.main.async {
                    self.parent.selectedImage = image
                }
            }
        }
    }
}

/// Тёмная прозрачная шапка есть только с iOS 16. На 15.2 шапка остаётся системной.
struct StormHiddenNavBarModifier: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 16.0, *) {
            content
                .toolbarColorScheme(.dark, for: .navigationBar)
                .toolbarBackground(.hidden, for: .navigationBar)
        } else {
            content
        }
    }
}

// После скрытой шапки обычный `.toolbar` в Xcode 16.3 подходит под два метода сразу.
private struct ALADDINToolbar<Items: ToolbarContent>: ViewModifier {
    var items: Items

    func body(content: Content) -> some View {
        content.toolbar { items }
    }
}

extension View {
    func aladdinToolbar<Items: ToolbarContent>(@ToolbarContentBuilder content: () -> Items) -> some View {
        modifier(ALADDINToolbar(items: content()))
    }
}

// MARK: - Preview

struct ProfileEditView_Previews: PreviewProvider {
    static var previews: some View {
        ProfileEditView()
            .environmentObject(LocalizationManager())
    }
}
