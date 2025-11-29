import SwiftUI

/**
 * 👨‍👩‍👧‍👦 Add Member Options Modal
 * Модальное окно выбора способа добавления члена семьи
 * 
 * Варианты:
 * 1. Создать новую семью (MainScreenWithRegistration)
 * 2. Сканировать QR-код (QRScannerModal)
 * 3. Ввести код приглашения (InvitationCodeInputModal)
 */

struct AddMemberOptionsModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var showCreateFamily: Bool = false
    @State private var showQRScanner: Bool = false
    @State private var showCodeInput: Bool = false
    @State private var scannedCode: String = ""
    @State private var familyCreated: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Заголовок
                VStack(spacing: 8) {
                    Text("Добавить участника")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.primary)
                    
                    Text("Выберите способ добавления")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.top, 20)
                
                // Варианты добавления
                VStack(spacing: 12) {
                    // Вариант 1: Создать новую семью
                    optionButton(
                        icon: "plus.circle.fill",
                        title: "Создать новую семью",
                        description: "Регистрация администратора",
                        color: .orange
                    ) {
                        showCreateFamily = true
                        // Закрываем основной модал после открытия регистрации
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                            isPresented = false
                        }
                    }
                    
                    // Вариант 2: Сканировать QR-код
                    optionButton(
                        icon: "qrcode.viewfinder",
                        title: "Сканировать QR-код",
                        description: "Присоединиться к существующей",
                        color: .blue
                    ) {
                        showQRScanner = true
                        // Закрываем основной модал после открытия сканера
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                            isPresented = false
                        }
                    }
                    
                    // Вариант 3: Ввести код
                    optionButton(
                        icon: "textformat.123",
                        title: "Ввести код приглашения",
                        description: "Присоединиться по коду",
                        color: .green
                    ) {
                        showCodeInput = true
                        // Закрываем основной модал после открытия ввода кода
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                            isPresented = false
                        }
                    }
                }
                
                // Текст о конфиденциальности
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "lock.shield.fill")
                            .font(.system(size: 16))
                            .foregroundColor(.blue)
                        Text("Конфиденциальность")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.primary)
                    }
                    
                    Text("Компания Aladdin не собирает персональные данные пользователей. По этой причине регистрация проходит по QR-коду без указания номера телефона и почты.")
                        .font(.system(size: 12))
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding(16)
                .background(Color.blue.opacity(0.05))
                .cornerRadius(12)
                
                Spacer()
                
                // Кнопка отмены
                Button("Отмена") {
                    isPresented = false
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
            .navigationBarHidden(true)
        }
        .fullScreenCover(isPresented: $showCreateFamily) {
            MainScreenWithRegistration(
                registrationVM: FamilyRegistrationViewModel(),
                onComplete: {
                    // После завершения регистрации закрываем оба модала
                    showCreateFamily = false
                    isPresented = false
                    
                    // Навигация на нужный экран по роли
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        if let roleString = UserDefaults.standard.string(forKey: "current_user_role"),
                           let role = FamilyRole(rawValue: roleString) {
                            switch role {
                            case .parent:
                                navigationManager.navigateTo(.parentalControl)
                            case .child:
                                navigationManager.navigateTo(.childInterface)
                            case .grandparent:
                                navigationManager.navigateTo(.elderlyInterface)
                            }
                        }
                    }
                }
            )
        }
        .fullScreenCover(isPresented: $showQRScanner) {
            QRScannerModal(isPresented: $showQRScanner) { code in
                // После сканирования QR автоматически открываем ввод кода
                scannedCode = code
                showCodeInput = true
            }
        }
        .sheet(isPresented: $showCodeInput) {
            InvitationCodeInputModal(
                isPresented: $showCodeInput,
                initialCode: scannedCode.isEmpty ? nil : scannedCode
            )
        }
        .onChange(of: showCodeInput) { newValue in
            if !newValue {
                // Сбрасываем scannedCode после закрытия
                scannedCode = ""
            }
        }
    }
    
    // MARK: - Option Button
    
    private func optionButton(
        icon: String,
        title: String,
        description: String,
        color: Color,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: {
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
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Preview

struct AddMemberOptionsModal_Previews: PreviewProvider {
    @State static var isPresented = true
    
    static var previews: some View {
        AddMemberOptionsModal(isPresented: $isPresented)
    }
}
