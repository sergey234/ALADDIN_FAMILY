import SwiftUI
import UIKit

/// 👤 Profile Edit View
/// Модальное окно редактирования профиля пользователя
struct ProfileEditView: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var name: String = "Сергей Хлыстов"
    @State private var email: String = "sergey@aladdin.app"
    @State private var phone: String = "+7 (999) 123-45-67"
    @State private var showImagePicker: Bool = false
    @State private var selectedImage: UIImage?
    
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
                    .accessibilityLabel("Фон редактирования профиля")
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 20) {
                        // Аватар
                        avatarSection
                        
                        // Поля редактирования
                        editFields
                        
                        // Кнопки действий
                        actionButtons
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 40)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Форма редактирования профиля")
            }
            .navigationTitle("Редактировать профиль")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        dismiss()
                    }
                    .foregroundColor(.blue)
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Сохранить") {
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
        .onAppear {
            // Загружаем сохраненное фото при открытии
            selectedImage = ProfileImageManager.shared.loadProfileImage()
        }
    }
    
    // MARK: - Avatar Section
    
    private var avatarSection: some View {
        VStack(spacing: 16) {
            Text("ФОТО ПРОФИЛЯ")
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
                                    Text("С")
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
            .accessibilityLabel("Изменить фото профиля")
            
            Text("Нажмите, чтобы изменить фото")
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
            Text("ИНФОРМАЦИЯ")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: 16) {
                // Имя
                editField(
                    title: "Имя",
                    text: $name,
                    placeholder: "Введите ваше имя",
                    icon: "person.fill"
                )
                
                // Email
                editField(
                    title: "Email",
                    text: $email,
                    placeholder: "Введите email",
                    icon: "envelope.fill",
                    keyboardType: .emailAddress
                )
                
                // Телефон
                editField(
                    title: "Телефон",
                    text: $phone,
                    placeholder: "Введите номер телефона",
                    icon: "phone.fill",
                    keyboardType: .phonePad
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
                    
                    Text("Сохранить изменения")
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
            .accessibilityLabel("Сохранить изменения")
            
            // Сбросить пароль
            Button(action: {
                resetPassword()
            }) {
                HStack(spacing: 12) {
                    Image(systemName: "key.fill")
                        .font(.system(size: 16))
                    
                    Text("Сбросить пароль")
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
            .accessibilityLabel("Сбросить пароль")
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
        // Сохранение профиля
        print("Сохранение профиля: \(name), \(email), \(phone)")
        
        // Сохраняем фото профиля, если оно было выбрано
        if let image = selectedImage {
            _ = ProfileImageManager.shared.saveProfileImage(image)
            print("✅ Profile image saved")
        }
        
        dismiss()
    }
    
    private func resetPassword() {
        // Сброс пароля
        print("Сброс пароля")
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
    }
}
