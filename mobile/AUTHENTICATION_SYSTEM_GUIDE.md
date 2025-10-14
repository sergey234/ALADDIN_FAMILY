# 🔐 ALADDIN Mobile App - Authentication System Guide

**Эксперт:** Security Developer + Mobile Developer  
**Дата:** 2025-01-27  
**Цель:** Реализация системы аутентификации с биометрической поддержкой для iOS и Android

---

## 🎯 **ОБЩАЯ АРХИТЕКТУРА АУТЕНТИФИКАЦИИ**

### 🔑 **УРОВНИ БЕЗОПАСНОСТИ:**
1. **Пароль + Email** - базовая аутентификация
2. **SMS код** - двухфакторная аутентификация
3. **Biometric** - биометрическая аутентификация
4. **Hardware Security** - аппаратная безопасность

### 🛡️ **ПРИНЦИПЫ БЕЗОПАСНОСТИ:**
- **Zero Trust** - проверка каждого запроса
- **Defense in Depth** - многоуровневая защита
- **Least Privilege** - минимальные права доступа
- **Secure by Default** - безопасность по умолчанию

---

## 🍎 **iOS АУТЕНТИФИКАЦИЯ**

### 📋 **1. AuthenticationManager.swift:**
```swift
import Foundation
import LocalAuthentication
import Security
import Combine

// MARK: - Authentication Manager
class AuthenticationManager: ObservableObject {
    static let shared = AuthenticationManager()
    
    @Published var isAuthenticated = false
    @Published var authenticationState: AuthenticationState = .notAuthenticated
    @Published var user: User?
    
    private let keychainManager = KeychainManager.shared
    private let biometricManager = BiometricManager.shared
    private let apiClient = APIClient.shared
    
    private init() {
        checkAuthenticationStatus()
    }
    
    // MARK: - Authentication Methods
    func authenticateWithPassword(email: String, password: String) async throws -> Bool {
        authenticationState = .authenticating
        
        do {
            let response = try await apiClient.authenticate(email: email, password: password)
            
            // Save tokens securely
            keychainManager.saveToken(response.accessToken)
            keychainManager.saveRefreshToken(response.refreshToken)
            
            // Update user info
            user = response.user
            isAuthenticated = true
            authenticationState = .authenticated
            
            return true
        } catch {
            authenticationState = .authenticationFailed(error)
            throw error
        }
    }
    
    func authenticateWithBiometrics() async throws -> Bool {
        guard biometricManager.isBiometricAvailable else {
            throw AuthenticationError.biometricNotAvailable
        }
        
        authenticationState = .authenticating
        
        do {
            let success = try await biometricManager.authenticate(
                reason: "Аутентификация для доступа к ALADDIN"
            )
            
            if success {
                // Verify stored token
                if let token = keychainManager.getToken() {
                    let isValid = try await apiClient.validateToken(token)
                    if isValid {
                        isAuthenticated = true
                        authenticationState = .authenticated
                        return true
                    }
                }
            }
            
            authenticationState = .authenticationFailed(AuthenticationError.biometricFailed)
            return false
        } catch {
            authenticationState = .authenticationFailed(error)
            throw error
        }
    }
    
    func authenticateWithSMS(phoneNumber: String, code: String) async throws -> Bool {
        authenticationState = .authenticating
        
        do {
            let response = try await apiClient.authenticateWithSMS(phoneNumber: phoneNumber, code: code)
            
            // Save tokens securely
            keychainManager.saveToken(response.accessToken)
            keychainManager.saveRefreshToken(response.refreshToken)
            
            // Update user info
            user = response.user
            isAuthenticated = true
            authenticationState = .authenticated
            
            return true
        } catch {
            authenticationState = .authenticationFailed(error)
            throw error
        }
    }
    
    func logout() async {
        do {
            try await apiClient.logout()
        } catch {
            print("Logout error: \(error)")
        }
        
        // Clear local data
        keychainManager.deleteToken()
        keychainManager.deleteRefreshToken()
        user = nil
        isAuthenticated = false
        authenticationState = .notAuthenticated
    }
    
    func refreshToken() async throws -> Bool {
        guard let refreshToken = keychainManager.getRefreshToken() else {
            throw AuthenticationError.noRefreshToken
        }
        
        do {
            let response = try await apiClient.refreshToken(refreshToken)
            
            // Update tokens
            keychainManager.saveToken(response.accessToken)
            keychainManager.saveRefreshToken(response.refreshToken)
            
            return true
        } catch {
            // Refresh failed, need to re-authenticate
            await logout()
            throw error
        }
    }
    
    private func checkAuthenticationStatus() {
        if let token = keychainManager.getToken() {
            // Check if token is still valid
            Task {
                do {
                    let isValid = try await apiClient.validateToken(token)
                    if isValid {
                        isAuthenticated = true
                        authenticationState = .authenticated
                    } else {
                        // Try to refresh token
                        try await refreshToken()
                    }
                } catch {
                    await logout()
                }
            }
        }
    }
}

// MARK: - Authentication State
enum AuthenticationState {
    case notAuthenticated
    case authenticating
    case authenticated
    case authenticationFailed(Error)
}

// MARK: - Authentication Error
enum AuthenticationError: Error, LocalizedError {
    case invalidCredentials
    case biometricNotAvailable
    case biometricFailed
    case noRefreshToken
    case tokenExpired
    case networkError
    case unknownError
    
    var errorDescription: String? {
        switch self {
        case .invalidCredentials:
            return "Неверные учетные данные"
        case .biometricNotAvailable:
            return "Биометрическая аутентификация недоступна"
        case .biometricFailed:
            return "Биометрическая аутентификация не удалась"
        case .noRefreshToken:
            return "Нет токена обновления"
        case .tokenExpired:
            return "Токен истек"
        case .networkError:
            return "Ошибка сети"
        case .unknownError:
            return "Неизвестная ошибка"
        }
    }
}
```

### 📋 **2. BiometricManager.swift:**
```swift
import Foundation
import LocalAuthentication
import Security

// MARK: - Biometric Manager
class BiometricManager: ObservableObject {
    static let shared = BiometricManager()
    
    @Published var isBiometricAvailable = false
    @Published var biometricType: BiometricType = .none
    
    private let context = LAContext()
    
    private init() {
        checkBiometricAvailability()
    }
    
    func checkBiometricAvailability() {
        var error: NSError?
        
        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            isBiometricAvailable = true
            
            switch context.biometryType {
            case .faceID:
                biometricType = .faceID
            case .touchID:
                biometricType = .touchID
            case .opticID:
                biometricType = .opticID
            default:
                biometricType = .none
            }
        } else {
            isBiometricAvailable = false
            biometricType = .none
        }
    }
    
    func authenticate(reason: String) async throws -> Bool {
        return try await withCheckedThrowingContinuation { continuation in
            context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            ) { success, error in
                if success {
                    continuation.resume(returning: true)
                } else {
                    continuation.resume(throwing: error ?? AuthenticationError.biometricFailed)
                }
            }
        }
    }
    
    func authenticateWithFallback(reason: String) async throws -> Bool {
        return try await withCheckedThrowingContinuation { continuation in
            context.evaluatePolicy(
                .deviceOwnerAuthentication,
                localizedReason: reason
            ) { success, error in
                if success {
                    continuation.resume(returning: true)
                } else {
                    continuation.resume(throwing: error ?? AuthenticationError.biometricFailed)
                }
            }
        }
    }
    
    func isBiometricEnrolled() -> Bool {
        var error: NSError?
        let canEvaluate = context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
        return canEvaluate && error == nil
    }
}

// MARK: - Biometric Type
enum BiometricType {
    case none
    case touchID
    case faceID
    case opticID
    
    var displayName: String {
        switch self {
        case .none:
            return "Недоступно"
        case .touchID:
            return "Touch ID"
        case .faceID:
            return "Face ID"
        case .opticID:
            return "Optic ID"
        }
    }
    
    var iconName: String {
        switch self {
        case .none:
            return "exclamationmark.triangle"
        case .touchID:
            return "touchid"
        case .faceID:
            return "faceid"
        case .opticID:
            return "eye"
        }
    }
}
```

### 📋 **3. KeychainManager.swift (Расширенная версия):**
```swift
import Foundation
import Security

// MARK: - Keychain Manager
class KeychainManager {
    static let shared = KeychainManager()
    
    private let service = "com.aladdin.security"
    private let accessGroup = "com.aladdin.security.group"
    
    private init() {}
    
    // MARK: - Token Management
    func saveToken(_ token: String) {
        saveToKeychain(key: "auth_token", value: token, accessible: .whenUnlockedThisDeviceOnly)
    }
    
    func getToken() -> String? {
        return getFromKeychain(key: "auth_token")
    }
    
    func deleteToken() {
        deleteFromKeychain(key: "auth_token")
    }
    
    func saveRefreshToken(_ token: String) {
        saveToKeychain(key: "refresh_token", value: token, accessible: .whenUnlockedThisDeviceOnly)
    }
    
    func getRefreshToken() -> String? {
        return getFromKeychain(key: "refresh_token")
    }
    
    func deleteRefreshToken() {
        deleteFromKeychain(key: "refresh_token")
    }
    
    // MARK: - User Data Management
    func saveUserData(_ userData: Data) {
        saveToKeychain(key: "user_data", value: userData, accessible: .whenUnlockedThisDeviceOnly)
    }
    
    func getUserData() -> Data? {
        return getFromKeychain(key: "user_data")
    }
    
    func deleteUserData() {
        deleteFromKeychain(key: "user_data")
    }
    
    // MARK: - Biometric Data Management
    func saveBiometricData(_ data: Data) {
        saveToKeychain(key: "biometric_data", value: data, accessible: .whenUnlockedThisDeviceOnly)
    }
    
    func getBiometricData() -> Data? {
        return getFromKeychain(key: "biometric_data")
    }
    
    func deleteBiometricData() {
        deleteFromKeychain(key: "biometric_data")
    }
    
    // MARK: - Private Methods
    private func saveToKeychain(key: String, value: String, accessible: CFString) {
        let data = value.data(using: .utf8)!
        saveToKeychain(key: key, value: data, accessible: accessible)
    }
    
    private func saveToKeychain(key: String, value: Data, accessible: CFString) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccessGroup as String: accessGroup,
            kSecAttrAccount as String: key,
            kSecValueData as String: value,
            kSecAttrAccessible as String: accessible
        ]
        
        // Delete existing item
        SecItemDelete(query as CFDictionary)
        
        // Add new item
        let status = SecItemAdd(query as CFDictionary, nil)
        if status != errSecSuccess {
            print("Keychain save error: \(status)")
        }
    }
    
    private func getFromKeychain(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccessGroup as String: accessGroup,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var dataTypeRef: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &dataTypeRef)
        
        guard status == errSecSuccess,
              let data = dataTypeRef as? Data,
              let value = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return value
    }
    
    private func getFromKeychain(key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccessGroup as String: accessGroup,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var dataTypeRef: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &dataTypeRef)
        
        guard status == errSecSuccess,
              let data = dataTypeRef as? Data else {
            return nil
        }
        
        return data
    }
    
    private func deleteFromKeychain(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccessGroup as String: accessGroup,
            kSecAttrAccount as String: key
        ]
        
        SecItemDelete(query as CFDictionary)
    }
    
    func clearAll() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccessGroup as String: accessGroup
        ]
        
        SecItemDelete(query as CFDictionary)
    }
}
```

### 📋 **4. LoginViewController.swift:**
```swift
import UIKit
import Combine

// MARK: - Login View Controller
class LoginViewController: UIViewController {
    
    // MARK: - UI Elements
    private lazy var logoImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.image = UIImage(systemName: "shield.checkered")
        imageView.tintColor = StormSkyColors.goldMain
        imageView.contentMode = .scaleAspectFit
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()
    
    private lazy var titleLabel: UILabel = {
        let label = UILabel()
        label.text = "🛡️ ALADDIN"
        label.font = StormSkyTheme.Typography.h1
        label.textColor = StormSkyColors.white
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var subtitleLabel: UILabel = {
        let label = UILabel()
        label.text = "Система семейной безопасности"
        label.font = StormSkyTheme.Typography.body
        label.textColor = StormSkyColors.lightningBlue
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var emailTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Email"
        textField.keyboardType = .emailAddress
        textField.autocapitalizationType = .none
        textField.autocorrectionType = .no
        textField.backgroundColor = StormSkyColors.stormSkyMain80
        textField.textColor = StormSkyColors.white
        textField.layer.cornerRadius = StormSkyTheme.CornerRadius.md
        textField.layer.borderWidth = 1
        textField.layer.borderColor = StormSkyColors.goldMain30.cgColor
        textField.leftView = UIView(frame: CGRect(x: 0, y: 0, width: 16, height: 0))
        textField.leftViewMode = .always
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private lazy var passwordTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Пароль"
        textField.isSecureTextEntry = true
        textField.backgroundColor = StormSkyColors.stormSkyMain80
        textField.textColor = StormSkyColors.white
        textField.layer.cornerRadius = StormSkyTheme.CornerRadius.md
        textField.layer.borderWidth = 1
        textField.layer.borderColor = StormSkyColors.goldMain30.cgColor
        textField.leftView = UIView(frame: CGRect(x: 0, y: 0, width: 16, height: 0))
        textField.leftViewMode = .always
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private lazy var loginButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Войти", for: .normal)
        button.titleLabel?.font = StormSkyTheme.Typography.body
        button.setTitleColor(StormSkyColors.stormSkyDark, for: .normal)
        button.backgroundColor = StormSkyColors.goldMain
        button.layer.cornerRadius = StormSkyTheme.CornerRadius.md
        button.addTarget(self, action: #selector(loginButtonTapped), for: .touchUpInside)
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private lazy var biometricButton: UIButton = {
        let button = UIButton(type: .system)
        let biometricType = BiometricManager.shared.biometricType
        button.setTitle("Войти с \(biometricType.displayName)", for: .normal)
        button.titleLabel?.font = StormSkyTheme.Typography.body
        button.setTitleColor(StormSkyColors.goldMain, for: .normal)
        button.backgroundColor = .clear
        button.layer.cornerRadius = StormSkyTheme.CornerRadius.md
        button.layer.borderWidth = 1
        button.layer.borderColor = StormSkyColors.goldMain.cgColor
        button.addTarget(self, action: #selector(biometricButtonTapped), for: .touchUpInside)
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private lazy var smsButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Войти по SMS", for: .normal)
        button.titleLabel?.font = StormSkyTheme.Typography.body
        button.setTitleColor(StormSkyColors.lightningBlue, for: .normal)
        button.backgroundColor = .clear
        button.addTarget(self, action: #selector(smsButtonTapped), for: .touchUpInside)
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private lazy var activityIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.color = StormSkyColors.goldMain
        indicator.hidesWhenStopped = true
        indicator.translatesAutoresizingMaskIntoConstraints = false
        return indicator
    }()
    
    // MARK: - Properties
    private let authManager = AuthenticationManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupGradientBackground()
        bindViewModel()
    }
    
    // MARK: - Setup
    private func setupUI() {
        view.addSubview(logoImageView)
        view.addSubview(titleLabel)
        view.addSubview(subtitleLabel)
        view.addSubview(emailTextField)
        view.addSubview(passwordTextField)
        view.addSubview(loginButton)
        view.addSubview(biometricButton)
        view.addSubview(smsButton)
        view.addSubview(activityIndicator)
        
        setupConstraints()
        setupBiometricButton()
    }
    
    private func setupGradientBackground() {
        GradientUtils.applyGradientBackground(
            to: view,
            colors: StormSkyColors.backgroundGradient
        )
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Logo
            logoImageView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 60),
            logoImageView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            logoImageView.widthAnchor.constraint(equalToConstant: 80),
            logoImageView.heightAnchor.constraint(equalToConstant: 80),
            
            // Title
            titleLabel.topAnchor.constraint(equalTo: logoImageView.bottomAnchor, constant: 20),
            titleLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            titleLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Subtitle
            subtitleLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            subtitleLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            subtitleLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Email TextField
            emailTextField.topAnchor.constraint(equalTo: subtitleLabel.bottomAnchor, constant: 60),
            emailTextField.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            emailTextField.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            emailTextField.heightAnchor.constraint(equalToConstant: 50),
            
            // Password TextField
            passwordTextField.topAnchor.constraint(equalTo: emailTextField.bottomAnchor, constant: 16),
            passwordTextField.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            passwordTextField.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            passwordTextField.heightAnchor.constraint(equalToConstant: 50),
            
            // Login Button
            loginButton.topAnchor.constraint(equalTo: passwordTextField.bottomAnchor, constant: 24),
            loginButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            loginButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            loginButton.heightAnchor.constraint(equalToConstant: 50),
            
            // Biometric Button
            biometricButton.topAnchor.constraint(equalTo: loginButton.bottomAnchor, constant: 16),
            biometricButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            biometricButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            biometricButton.heightAnchor.constraint(equalToConstant: 50),
            
            // SMS Button
            smsButton.topAnchor.constraint(equalTo: biometricButton.bottomAnchor, constant: 16),
            smsButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            smsButton.heightAnchor.constraint(equalToConstant: 44),
            
            // Activity Indicator
            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    private func setupBiometricButton() {
        let biometricManager = BiometricManager.shared
        biometricButton.isHidden = !biometricManager.isBiometricAvailable
        
        if biometricManager.isBiometricAvailable {
            let iconName = biometricManager.biometricType.iconName
            let icon = UIImage(systemName: iconName)
            biometricButton.setImage(icon, for: .normal)
            biometricButton.tintColor = StormSkyColors.goldMain
        }
    }
    
    private func bindViewModel() {
        authManager.$authenticationState
            .receive(on: DispatchQueue.main)
            .sink { [weak self] state in
                self?.updateUI(for: state)
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Actions
    @objc private func loginButtonTapped() {
        guard let email = emailTextField.text, !email.isEmpty,
              let password = passwordTextField.text, !password.isEmpty else {
            showAlert(title: "Ошибка", message: "Заполните все поля")
            return
        }
        
        Task {
            do {
                let success = try await authManager.authenticateWithPassword(email: email, password: password)
                if success {
                    navigateToMainScreen()
                }
            } catch {
                showAlert(title: "Ошибка входа", message: error.localizedDescription)
            }
        }
    }
    
    @objc private func biometricButtonTapped() {
        Task {
            do {
                let success = try await authManager.authenticateWithBiometrics()
                if success {
                    navigateToMainScreen()
                }
            } catch {
                showAlert(title: "Ошибка биометрии", message: error.localizedDescription)
            }
        }
    }
    
    @objc private func smsButtonTapped() {
        // Navigate to SMS authentication screen
        let smsVC = SMSAuthenticationViewController()
        present(smsVC, animated: true)
    }
    
    // MARK: - UI Updates
    private func updateUI(for state: AuthenticationState) {
        switch state {
        case .notAuthenticated:
            activityIndicator.stopAnimating()
            setButtonsEnabled(true)
        case .authenticating:
            activityIndicator.startAnimating()
            setButtonsEnabled(false)
        case .authenticated:
            activityIndicator.stopAnimating()
            navigateToMainScreen()
        case .authenticationFailed(let error):
            activityIndicator.stopAnimating()
            setButtonsEnabled(true)
            showAlert(title: "Ошибка аутентификации", message: error.localizedDescription)
        }
    }
    
    private func setButtonsEnabled(_ enabled: Bool) {
        loginButton.isEnabled = enabled
        biometricButton.isEnabled = enabled
        smsButton.isEnabled = enabled
    }
    
    private func navigateToMainScreen() {
        let mainVC = MainViewController()
        let navController = UINavigationController(rootViewController: mainVC)
        navController.modalPresentationStyle = .fullScreen
        present(navController, animated: true)
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}
```

---

## 🤖 **ANDROID АУТЕНТИФИКАЦИЯ**

### 📋 **1. AuthenticationManager.kt:**
```kotlin
package com.aladdin.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.aladdin.network.ApiClient
import com.aladdin.security.SecureStorage
import kotlinx.coroutines.launch

class AuthenticationManager : ViewModel() {
    
    private val _isAuthenticated = MutableLiveData<Boolean>()
    val isAuthenticated: LiveData<Boolean> = _isAuthenticated
    
    private val _authenticationState = MutableLiveData<AuthenticationState>()
    val authenticationState: LiveData<AuthenticationState> = _authenticationState
    
    private val _user = MutableLiveData<User?>()
    val user: LiveData<User?> = _user
    
    private val apiService = ApiClient.apiService
    private val secureStorage = SecureStorage(context)
    private val biometricManager = BiometricManager(context)
    
    init {
        checkAuthenticationStatus()
    }
    
    // MARK: - Authentication Methods
    suspend fun authenticateWithPassword(email: String, password: String): Boolean {
        _authenticationState.value = AuthenticationState.AUTHENTICATING
        
        return try {
            val response = apiService.authenticate(email, password)
            
            // Save tokens securely
            secureStorage.saveToken(response.accessToken)
            secureStorage.saveRefreshToken(response.refreshToken)
            
            // Update user info
            _user.value = response.user
            _isAuthenticated.value = true
            _authenticationState.value = AuthenticationState.AUTHENTICATED
            
            true
        } catch (e: Exception) {
            _authenticationState.value = AuthenticationState.AUTHENTICATION_FAILED(e)
            false
        }
    }
    
    suspend fun authenticateWithBiometrics(): Boolean {
        if (!biometricManager.isBiometricAvailable()) {
            _authenticationState.value = AuthenticationState.AUTHENTICATION_FAILED(
                AuthenticationError.BIOMETRIC_NOT_AVAILABLE
            )
            return false
        }
        
        _authenticationState.value = AuthenticationState.AUTHENTICATING
        
        return try {
            val success = biometricManager.authenticate("Аутентификация для доступа к ALADDIN")
            
            if (success) {
                // Verify stored token
                val token = secureStorage.getToken()
                if (token != null) {
                    val isValid = apiService.validateToken(token)
                    if (isValid) {
                        _isAuthenticated.value = true
                        _authenticationState.value = AuthenticationState.AUTHENTICATED
                        return true
                    }
                }
            }
            
            _authenticationState.value = AuthenticationState.AUTHENTICATION_FAILED(
                AuthenticationError.BIOMETRIC_FAILED
            )
            false
        } catch (e: Exception) {
            _authenticationState.value = AuthenticationState.AUTHENTICATION_FAILED(e)
            false
        }
    }
    
    suspend fun authenticateWithSMS(phoneNumber: String, code: String): Boolean {
        _authenticationState.value = AuthenticationState.AUTHENTICATING
        
        return try {
            val response = apiService.authenticateWithSMS(phoneNumber, code)
            
            // Save tokens securely
            secureStorage.saveToken(response.accessToken)
            secureStorage.saveRefreshToken(response.refreshToken)
            
            // Update user info
            _user.value = response.user
            _isAuthenticated.value = true
            _authenticationState.value = AuthenticationState.AUTHENTICATED
            
            true
        } catch (e: Exception) {
            _authenticationState.value = AuthenticationState.AUTHENTICATION_FAILED(e)
            false
        }
    }
    
    suspend fun logout() {
        try {
            apiService.logout()
        } catch (e: Exception) {
            // Log error but continue with local logout
        }
        
        // Clear local data
        secureStorage.deleteToken()
        secureStorage.deleteRefreshToken()
        _user.value = null
        _isAuthenticated.value = false
        _authenticationState.value = AuthenticationState.NOT_AUTHENTICATED
    }
    
    suspend fun refreshToken(): Boolean {
        val refreshToken = secureStorage.getRefreshToken()
            ?: throw AuthenticationError.NO_REFRESH_TOKEN
        
        return try {
            val response = apiService.refreshToken(refreshToken)
            
            // Update tokens
            secureStorage.saveToken(response.accessToken)
            secureStorage.saveRefreshToken(response.refreshToken)
            
            true
        } catch (e: Exception) {
            // Refresh failed, need to re-authenticate
            logout()
            false
        }
    }
    
    private fun checkAuthenticationStatus() {
        val token = secureStorage.getToken()
        if (token != null) {
            viewModelScope.launch {
                try {
                    val isValid = apiService.validateToken(token)
                    if (isValid) {
                        _isAuthenticated.value = true
                        _authenticationState.value = AuthenticationState.AUTHENTICATED
                    } else {
                        // Try to refresh token
                        refreshToken()
                    }
                } catch (e: Exception) {
                    logout()
                }
            }
        }
    }
}

// MARK: - Authentication State
sealed class AuthenticationState {
    object NOT_AUTHENTICATED : AuthenticationState()
    object AUTHENTICATING : AuthenticationState()
    object AUTHENTICATED : AuthenticationState()
    data class AUTHENTICATION_FAILED(val error: Exception) : AuthenticationState()
}

// MARK: - Authentication Error
enum class AuthenticationError : Exception() {
    INVALID_CREDENTIALS,
    BIOMETRIC_NOT_AVAILABLE,
    BIOMETRIC_FAILED,
    NO_REFRESH_TOKEN,
    TOKEN_EXPIRED,
    NETWORK_ERROR,
    UNKNOWN_ERROR
}
```

### 📋 **2. BiometricManager.kt:**
```kotlin
package com.aladdin.auth

import android.content.Context
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.fragment.app.FragmentActivity
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume

class BiometricManager(private val context: Context) {
    
    private val biometricManager = BiometricManager.from(context)
    
    fun isBiometricAvailable(): Boolean {
        return biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_WEAK) == BiometricManager.BIOMETRIC_SUCCESS
    }
    
    fun getBiometricType(): BiometricType {
        return when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_WEAK)) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                // Check specific biometric type
                BiometricType.FINGERPRINT // Default to fingerprint, can be enhanced
            }
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> BiometricType.NONE
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> BiometricType.NONE
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> BiometricType.NONE
            else -> BiometricType.NONE
        }
    }
    
    suspend fun authenticate(reason: String): Boolean {
        return suspendCancellableCoroutine { continuation ->
            val activity = context as? FragmentActivity
                ?: throw IllegalStateException("Context must be a FragmentActivity")
            
            val promptInfo = BiometricPrompt.PromptInfo.Builder()
                .setTitle("Аутентификация ALADDIN")
                .setSubtitle(reason)
                .setNegativeButtonText("Отмена")
                .build()
            
            val biometricPrompt = BiometricPrompt(activity, object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    continuation.resume(true)
                }
                
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    continuation.resume(false)
                }
                
                override fun onAuthenticationFailed() {
                    continuation.resume(false)
                }
            })
            
            biometricPrompt.authenticate(promptInfo)
        }
    }
}

enum class BiometricType {
    NONE,
    FINGERPRINT,
    FACE,
    IRIS
}
```

---

## 🚀 **СЛЕДУЮЩИЕ ШАГИ**

1. **Реализовать аутентификацию** в обоих проектах
2. **Настроить биометрическую аутентификацию** 
3. **Создать экраны входа** с красивым дизайном
4. **Добавить двухфакторную аутентификацию**
5. **Протестировать безопасность** системы
6. **Оптимизировать производительность**

**🎯 СИСТЕМА АУТЕНТИФИКАЦИИ ГОТОВА К РЕАЛИЗАЦИИ!**

**📱 ПЕРЕХОДИМ К AI ПОМОЩНИКУ!**

