import UIKit

class ViewController: UIViewController {
    
    // MARK: - IBOutlets
    @IBOutlet weak var mainScrollView: UIScrollView!
    @IBOutlet weak var contentView: UIView!
    @IBOutlet weak var headerView: UIView!
    @IBOutlet weak var logoLabel: UILabel!
    @IBOutlet weak var profileButton: UIButton!
    @IBOutlet weak var cardsStackView: UIStackView!
    @IBOutlet weak var aiAssistantView: UIView!
    @IBOutlet weak var aiTitleLabel: UILabel!
    @IBOutlet weak var aiMessageLabel: UILabel!
    @IBOutlet weak var aiInputTextField: UITextField!
    @IBOutlet weak var aiSendButton: UIButton!
    
    // MARK: - Properties
    private var aiAssistant = UnifiedSupportAPI()
    private var isAIActive = false
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupCards()
        setupAIAssistant()
        applyStormSkyTheme()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        updateSecurityStatus()
    }
    
    // MARK: - UI Setup
    private func setupUI() {
        // Настройка основного интерфейса
        view.backgroundColor = StormSkyColors.primaryBackground
        
        // Настройка заголовка
        setupHeader()
        
        // Настройка AI помощника
        setupAIAssistantView()
    }
    
    private func setupHeader() {
        headerView.backgroundColor = StormSkyColors.primaryBackground
        logoLabel.text = "🌩️ ALADDIN"
        logoLabel.textColor = StormSkyColors.accentColor
        logoLabel.font = UIFont.boldSystemFont(ofSize: 24)
        
        profileButton.backgroundColor = StormSkyColors.accentColor
        profileButton.setTitleColor(StormSkyColors.primaryBackground, for: .normal)
        profileButton.layer.cornerRadius = 20
        profileButton.setTitle("👤", for: .normal)
    }
    
    private func setupCards() {
        // Создание карточек функций
        let protectionCard = createFunctionCard(
            icon: "🛡️",
            title: "Защита",
            subtitle: "VPN • Антивирус",
            action: #selector(protectionCardTapped)
        )
        
        let familyCard = createFunctionCard(
            icon: "👨‍👩‍👧‍👦",
            title: "Семья",
            subtitle: "Профили • Контроль",
            action: #selector(familyCardTapped)
        )
        
        let analyticsCard = createFunctionCard(
            icon: "📊",
            title: "Аналитика",
            subtitle: "Статистика • Отчеты",
            action: #selector(analyticsCardTapped)
        )
        
        let settingsCard = createFunctionCard(
            icon: "⚙️",
            title: "Настройки",
            subtitle: "Конфигурация",
            action: #selector(settingsCardTapped)
        )
        
        // Добавление карточек в стек
        cardsStackView.addArrangedSubview(protectionCard)
        cardsStackView.addArrangedSubview(familyCard)
        cardsStackView.addArrangedSubview(analyticsCard)
        cardsStackView.addArrangedSubview(settingsCard)
    }
    
    private func createFunctionCard(icon: String, title: String, subtitle: String, action: Selector) -> UIView {
        let cardView = UIView()
        cardView.backgroundColor = UIColor.white.withAlphaComponent(0.1)
        cardView.layer.cornerRadius = 15
        cardView.layer.borderWidth = 1
        cardView.layer.borderColor = UIColor.white.withAlphaComponent(0.2).cgColor
        
        // Применение glassmorphism эффекта
        cardView.applyGlassmorphism(style: .light)
        
        // Настройка контента карточки
        let iconLabel = UILabel()
        iconLabel.text = icon
        iconLabel.font = UIFont.systemFont(ofSize: 32)
        iconLabel.textAlignment = .center
        
        let titleLabel = UILabel()
        titleLabel.text = title
        titleLabel.font = UIFont.boldSystemFont(ofSize: 16)
        titleLabel.textColor = StormSkyColors.primaryText
        titleLabel.textAlignment = .center
        
        let subtitleLabel = UILabel()
        subtitleLabel.text = subtitle
        subtitleLabel.font = UIFont.systemFont(ofSize: 12)
        subtitleLabel.textColor = StormSkyColors.primaryText.withAlphaComponent(0.8)
        subtitleLabel.textAlignment = .center
        
        // Добавление элементов в карточку
        cardView.addSubview(iconLabel)
        cardView.addSubview(titleLabel)
        cardView.addSubview(subtitleLabel)
        
        // Настройка constraints
        iconLabel.translatesAutoresizingMaskIntoConstraints = false
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        subtitleLabel.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            iconLabel.topAnchor.constraint(equalTo: cardView.topAnchor, constant: 20),
            iconLabel.centerXAnchor.constraint(equalTo: cardView.centerXAnchor),
            
            titleLabel.topAnchor.constraint(equalTo: iconLabel.bottomAnchor, constant: 10),
            titleLabel.leadingAnchor.constraint(equalTo: cardView.leadingAnchor, constant: 10),
            titleLabel.trailingAnchor.constraint(equalTo: cardView.trailingAnchor, constant: -10),
            
            subtitleLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 5),
            subtitleLabel.leadingAnchor.constraint(equalTo: cardView.leadingAnchor, constant: 10),
            subtitleLabel.trailingAnchor.constraint(equalTo: cardView.trailingAnchor, constant: -10),
            subtitleLabel.bottomAnchor.constraint(equalTo: cardView.bottomAnchor, constant: -20)
        ])
        
        // Добавление жеста нажатия
        let tapGesture = UITapGestureRecognizer(target: self, action: action)
        cardView.addGestureRecognizer(tapGesture)
        cardView.isUserInteractionEnabled = true
        
        return cardView
    }
    
    private func setupAIAssistantView() {
        aiAssistantView.backgroundColor = StormSkyColors.accentColor.withAlphaComponent(0.1)
        aiAssistantView.layer.cornerRadius = 15
        aiAssistantView.layer.borderWidth = 2
        aiAssistantView.layer.borderColor = StormSkyColors.accentColor.cgColor
        
        aiTitleLabel.text = "🤖 AI Помощник"
        aiTitleLabel.textColor = StormSkyColors.accentColor
        aiTitleLabel.font = UIFont.boldSystemFont(ofSize: 18)
        
        aiMessageLabel.text = "Привет! Я помогу настроить защиту для вашей семьи. Чем могу помочь?"
        aiMessageLabel.textColor = StormSkyColors.primaryText
        aiMessageLabel.font = UIFont.systemFont(ofSize: 14)
        aiMessageLabel.numberOfLines = 0
        
        aiInputTextField.placeholder = "Задайте вопрос..."
        aiInputTextField.backgroundColor = UIColor.white.withAlphaComponent(0.1)
        aiInputTextField.layer.cornerRadius = 25
        aiInputTextField.layer.borderWidth = 1
        aiInputTextField.layer.borderColor = UIColor.white.withAlphaComponent(0.3).cgColor
        aiInputTextField.textColor = StormSkyColors.primaryText
        
        aiSendButton.backgroundColor = StormSkyColors.accentColor
        aiSendButton.setTitleColor(StormSkyColors.primaryBackground, for: .normal)
        aiSendButton.layer.cornerRadius = 25
        aiSendButton.setTitle("➤", for: .normal)
    }
    
    private func applyStormSkyTheme() {
        // Применение цветовой схемы "Грозовое небо с золотыми акцентами"
        view.backgroundColor = StormSkyColors.primaryBackground
        
        // Настройка навигации
        navigationController?.navigationBar.barTintColor = StormSkyColors.primaryBackground
        navigationController?.navigationBar.tintColor = StormSkyColors.accentColor
        navigationController?.navigationBar.titleTextAttributes = [
            .foregroundColor: StormSkyColors.primaryText
        ]
    }
    
    // MARK: - Actions
    @objc private func protectionCardTapped() {
        // Переход к экрану защиты
        print("🛡️ Protection card tapped")
        // TODO: Implement navigation to protection screen
    }
    
    @objc private func familyCardTapped() {
        // Переход к экрану семьи
        print("👨‍👩‍👧‍👦 Family card tapped")
        // TODO: Implement navigation to family screen
    }
    
    @objc private func analyticsCardTapped() {
        // Переход к экрану аналитики
        print("📊 Analytics card tapped")
        // TODO: Implement navigation to analytics screen
    }
    
    @objc private func settingsCardTapped() {
        // Переход к экрану настроек
        print("⚙️ Settings card tapped")
        // TODO: Implement navigation to settings screen
    }
    
    @IBAction func profileButtonTapped(_ sender: UIButton) {
        // Переход к профилю пользователя
        print("👤 Profile button tapped")
        // TODO: Implement profile navigation
    }
    
    @IBAction func aiSendButtonTapped(_ sender: UIButton) {
        // Отправка сообщения AI помощнику
        guard let message = aiInputTextField.text, !message.isEmpty else { return }
        
        sendMessageToAI(message: message)
        aiInputTextField.text = ""
    }
    
    // MARK: - AI Assistant
    private func sendMessageToAI(message: String) {
        // Отправка сообщения AI помощнику
        print("🤖 Sending message to AI: \(message)")
        
        // Показ индикатора загрузки
        showAILoadingIndicator()
        
        // Отправка запроса к AI API
        Task {
            do {
                let response = try await aiAssistant.sendMessage(message)
                await MainActor.run {
                    self.hideAILoadingIndicator()
                    self.updateAIMessage(response)
                }
            } catch {
                await MainActor.run {
                    self.hideAILoadingIndicator()
                    self.showAIError(error)
                }
            }
        }
    }
    
    private func showAILoadingIndicator() {
        aiMessageLabel.text = "🤖 AI помощник печатает..."
        isAIActive = true
    }
    
    private func hideAILoadingIndicator() {
        isAIActive = false
    }
    
    private func updateAIMessage(_ response: String) {
        aiMessageLabel.text = response
    }
    
    private func showAIError(_ error: Error) {
        aiMessageLabel.text = "❌ Ошибка: \(error.localizedDescription)"
    }
    
    // MARK: - Security
    private func updateSecurityStatus() {
        // Обновление статуса безопасности
        print("🛡️ Updating security status...")
        // TODO: Implement security status update
    }
}

// MARK: - Extensions
extension ViewController: UITextFieldDelegate {
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        if textField == aiInputTextField {
            aiSendButtonTapped(aiSendButton)
            return true
        }
        return false
    }
}

