import UIKit
import Combine

// MARK: - Support Chat Interface для iOS
class SupportChatInterface: UIViewController {
    
    // MARK: - UI Components
    private let chatTableView = UITableView()
    private let messageInputView = UIView()
    private let messageTextField = UITextField()
    private let sendButton = UIButton()
    private let quickActionsView = UIView()
    private let statusIndicator = UIView()
    private let typingIndicator = UIActivityIndicatorView()
    
    // MARK: - Properties
    private var messages: [SupportMessage] = []
    private var cancellables = Set<AnyCancellable>()
    private let supportAPI = UnifiedSupportAPIManager()
    private var isTyping = false
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
        setupBindings()
        loadInitialMessages()
    }
    
    // MARK: - UI Setup
    private func setupUI() {
        view.backgroundColor = StormSkyColors.backgroundPrimary
        
        // Navigation Bar
        navigationItem.title = "AI Помощник"
        navigationItem.leftBarButtonItem = UIBarButtonItem(
            title: "Закрыть",
            style: .plain,
            target: self,
            action: #selector(closeButtonTapped)
        )
        
        // Chat Table View
        chatTableView.delegate = self
        chatTableView.dataSource = self
        chatTableView.backgroundColor = .clear
        chatTableView.separatorStyle = .none
        chatTableView.register(SupportMessageCell.self, forCellReuseIdentifier: "MessageCell")
        chatTableView.transform = CGAffineTransform(scaleX: 1, y: -1)
        
        // Message Input View
        messageInputView.backgroundColor = StormSkyColors.backgroundSecondary
        messageInputView.layer.cornerRadius = 25
        messageInputView.layer.borderWidth = 1
        messageInputView.layer.borderColor = StormSkyColors.accent.cgColor
        
        // Message Text Field
        messageTextField.placeholder = "Напишите ваш вопрос..."
        messageTextField.backgroundColor = .clear
        messageTextField.textColor = StormSkyColors.textPrimary
        messageTextField.font = UIFont.systemFont(ofSize: 16)
        messageTextField.returnKeyType = .send
        messageTextField.delegate = self
        
        // Send Button
        sendButton.setTitle("📤", for: .normal)
        sendButton.titleLabel?.font = UIFont.systemFont(ofSize: 20)
        sendButton.backgroundColor = StormSkyColors.accent
        sendButton.layer.cornerRadius = 20
        sendButton.addTarget(self, action: #selector(sendButtonTapped), for: .touchUpInside)
        
        // Quick Actions View
        setupQuickActions()
        
        // Status Indicator
        statusIndicator.backgroundColor = StormSkyColors.success
        statusIndicator.layer.cornerRadius = 6
        statusIndicator.layer.borderWidth = 2
        statusIndicator.layer.borderColor = StormSkyColors.accent.cgColor
        
        // Typing Indicator
        typingIndicator.style = .medium
        typingIndicator.color = StormSkyColors.accent
        typingIndicator.hidesWhenStopped = true
        
        // Add subviews
        view.addSubview(chatTableView)
        view.addSubview(quickActionsView)
        view.addSubview(messageInputView)
        messageInputView.addSubview(messageTextField)
        messageInputView.addSubview(sendButton)
        view.addSubview(statusIndicator)
        view.addSubview(typingIndicator)
    }
    
    private func setupQuickActions() {
        let actions = [
            ("🛡️ Безопасность", "security"),
            ("👨‍👩‍👧‍👦 Семья", "family"),
            ("🔧 Настройки", "settings"),
            ("❓ Помощь", "help")
        ]
        
        let stackView = UIStackView()
        stackView.axis = .horizontal
        stackView.distribution = .fillEqually
        stackView.spacing = 10
        
        for (title, action) in actions {
            let button = UIButton()
            button.setTitle(title, for: .normal)
            button.titleLabel?.font = UIFont.systemFont(ofSize: 12)
            button.backgroundColor = StormSkyColors.backgroundSecondary
            button.setTitleColor(StormSkyColors.textPrimary, for: .normal)
            button.layer.cornerRadius = 15
            button.layer.borderWidth = 1
            button.layer.borderColor = StormSkyColors.accent.cgColor
            button.addTarget(self, action: #selector(quickActionTapped(_:)), for: .touchUpInside)
            button.tag = actions.firstIndex(where: { $0.1 == action }) ?? 0
            stackView.addArrangedSubview(button)
        }
        
        quickActionsView.addSubview(stackView)
        stackView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            stackView.topAnchor.constraint(equalTo: quickActionsView.topAnchor, constant: 8),
            stackView.leadingAnchor.constraint(equalTo: quickActionsView.leadingAnchor, constant: 16),
            stackView.trailingAnchor.constraint(equalTo: quickActionsView.trailingAnchor, constant: -16),
            stackView.bottomAnchor.constraint(equalTo: quickActionsView.bottomAnchor, constant: -8)
        ])
    }
    
    private func setupConstraints() {
        [chatTableView, messageInputView, quickActionsView, messageTextField, sendButton, statusIndicator, typingIndicator].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
        }
        
        NSLayoutConstraint.activate([
            // Status Indicator
            statusIndicator.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 10),
            statusIndicator.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            statusIndicator.widthAnchor.constraint(equalToConstant: 12),
            statusIndicator.heightAnchor.constraint(equalToConstant: 12),
            
            // Chat Table View
            chatTableView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 40),
            chatTableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            chatTableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            chatTableView.bottomAnchor.constraint(equalTo: quickActionsView.topAnchor),
            
            // Quick Actions View
            quickActionsView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            quickActionsView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            quickActionsView.bottomAnchor.constraint(equalTo: messageInputView.topAnchor),
            quickActionsView.heightAnchor.constraint(equalToConstant: 60),
            
            // Message Input View
            messageInputView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            messageInputView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            messageInputView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -16),
            messageInputView.heightAnchor.constraint(equalToConstant: 50),
            
            // Message Text Field
            messageTextField.leadingAnchor.constraint(equalTo: messageInputView.leadingAnchor, constant: 16),
            messageTextField.trailingAnchor.constraint(equalTo: sendButton.leadingAnchor, constant: -8),
            messageTextField.centerYAnchor.constraint(equalTo: messageInputView.centerYAnchor),
            messageTextField.heightAnchor.constraint(equalToConstant: 30),
            
            // Send Button
            sendButton.trailingAnchor.constraint(equalTo: messageInputView.trailingAnchor, constant: -8),
            sendButton.centerYAnchor.constraint(equalTo: messageInputView.centerYAnchor),
            sendButton.widthAnchor.constraint(equalToConstant: 40),
            sendButton.heightAnchor.constraint(equalToConstant: 40),
            
            // Typing Indicator
            typingIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            typingIndicator.bottomAnchor.constraint(equalTo: quickActionsView.topAnchor, constant: -10)
        ])
    }
    
    private func setupBindings() {
        // Keyboard handling
        NotificationCenter.default.publisher(for: UIResponder.keyboardWillShowNotification)
            .sink { [weak self] notification in
                self?.handleKeyboardShow(notification)
            }
            .store(in: &cancellables)
        
        NotificationCenter.default.publisher(for: UIResponder.keyboardWillHideNotification)
            .sink { [weak self] _ in
                self?.handleKeyboardHide()
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Actions
    @objc private func closeButtonTapped() {
        dismiss(animated: true)
    }
    
    @objc private func sendButtonTapped() {
        sendMessage()
    }
    
    @objc private func quickActionTapped(_ sender: UIButton) {
        let actions = ["security", "family", "settings", "help"]
        let action = actions[sender.tag]
        sendQuickAction(action)
    }
    
    // MARK: - Message Handling
    private func sendMessage() {
        guard let text = messageTextField.text, !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        let userMessage = SupportMessage(
            id: UUID().uuidString,
            text: text,
            isFromUser: true,
            timestamp: Date(),
            category: "general"
        )
        
        addMessage(userMessage)
        messageTextField.text = ""
        
        // Send to API
        sendToAPI(text: text)
    }
    
    private func sendQuickAction(_ action: String) {
        let quickMessages = [
            "security": "Расскажи о функциях безопасности ALADDIN",
            "family": "Как настроить родительский контроль?",
            "settings": "Помоги с настройками приложения",
            "help": "Мне нужна помощь с приложением"
        ]
        
        if let message = quickMessages[action] {
            messageTextField.text = message
            sendMessage()
        }
    }
    
    private func sendToAPI(text: String) {
        showTypingIndicator(true)
        
        let request = SupportRequest(
            message: text,
            category: "general",
            priority: .medium,
            context: SupportContext(
                userID: "current_user",
                deviceInfo: "iOS",
                appVersion: "1.0.0"
            )
        )
        
        supportAPI.sendSupportRequest(request)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.showTypingIndicator(false)
                    if case .failure(let error) = completion {
                        self?.showError(error.localizedDescription)
                    }
                },
                receiveValue: { [weak self] response in
                    self?.handleAPIResponse(response)
                }
            )
            .store(in: &cancellables)
    }
    
    private func handleAPIResponse(_ response: SupportResponse) {
        let aiMessage = SupportMessage(
            id: UUID().uuidString,
            text: response.message,
            isFromUser: false,
            timestamp: Date(),
            category: response.category ?? "general"
        )
        
        addMessage(aiMessage)
    }
    
    private func addMessage(_ message: SupportMessage) {
        messages.insert(message, at: 0)
        chatTableView.reloadData()
    }
    
    private func loadInitialMessages() {
        let welcomeMessage = SupportMessage(
            id: "welcome",
            text: "👋 Привет! Я AI помощник ALADDIN. Чем могу помочь?",
            isFromUser: false,
            timestamp: Date(),
            category: "welcome"
        )
        
        addMessage(welcomeMessage)
    }
    
    private func showTypingIndicator(_ show: Bool) {
        isTyping = show
        if show {
            typingIndicator.startAnimating()
        } else {
            typingIndicator.stopAnimating()
        }
    }
    
    private func showError(_ message: String) {
        let alert = UIAlertController(title: "Ошибка", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
    
    // MARK: - Keyboard Handling
    private func handleKeyboardShow(_ notification: Notification) {
        guard let keyboardFrame = notification.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect else { return }
        
        UIView.animate(withDuration: 0.3) {
            self.messageInputView.transform = CGAffineTransform(translationX: 0, y: -keyboardFrame.height)
        }
    }
    
    private func handleKeyboardHide() {
        UIView.animate(withDuration: 0.3) {
            self.messageInputView.transform = .identity
        }
    }
}

// MARK: - Table View Data Source & Delegate
extension SupportChatInterface: UITableViewDataSource, UITableViewDelegate {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return messages.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "MessageCell", for: indexPath) as! SupportMessageCell
        cell.configure(with: messages[indexPath.row])
        return cell
    }
    
    func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
        return UITableView.automaticDimension
    }
}

// MARK: - Text Field Delegate
extension SupportChatInterface: UITextFieldDelegate {
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        sendMessage()
        return true
    }
}

// MARK: - Support Message Model
struct SupportMessage {
    let id: String
    let text: String
    let isFromUser: Bool
    let timestamp: Date
    let category: String
}

// MARK: - Support Message Cell
class SupportMessageCell: UITableViewCell {
    private let messageLabel = UILabel()
    private let timeLabel = UILabel()
    private let bubbleView = UIView()
    
    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupUI() {
        backgroundColor = .clear
        selectionStyle = .none
        transform = CGAffineTransform(scaleX: 1, y: -1)
        
        bubbleView.layer.cornerRadius = 16
        bubbleView.layer.borderWidth = 1
        
        messageLabel.numberOfLines = 0
        messageLabel.font = UIFont.systemFont(ofSize: 16)
        
        timeLabel.font = UIFont.systemFont(ofSize: 12)
        timeLabel.textColor = StormSkyColors.textSecondary
        
        [bubbleView, messageLabel, timeLabel].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            addSubview($0)
        }
        
        NSLayoutConstraint.activate([
            bubbleView.topAnchor.constraint(equalTo: topAnchor, constant: 8),
            bubbleView.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -8),
            bubbleView.widthAnchor.constraint(lessThanOrEqualToConstant: 280),
            
            messageLabel.topAnchor.constraint(equalTo: bubbleView.topAnchor, constant: 12),
            messageLabel.leadingAnchor.constraint(equalTo: bubbleView.leadingAnchor, constant: 12),
            messageLabel.trailingAnchor.constraint(equalTo: bubbleView.trailingAnchor, constant: -12),
            
            timeLabel.topAnchor.constraint(equalTo: messageLabel.bottomAnchor, constant: 4),
            timeLabel.leadingAnchor.constraint(equalTo: bubbleView.leadingAnchor, constant: 12),
            timeLabel.trailingAnchor.constraint(equalTo: bubbleView.trailingAnchor, constant: -12),
            timeLabel.bottomAnchor.constraint(equalTo: bubbleView.bottomAnchor, constant: -8)
        ])
    }
    
    func configure(with message: SupportMessage) {
        messageLabel.text = message.text
        timeLabel.text = formatTime(message.timestamp)
        
        if message.isFromUser {
            // User message - right aligned
            bubbleView.backgroundColor = StormSkyColors.accent
            messageLabel.textColor = .white
            timeLabel.textColor = .white.withAlphaComponent(0.8)
            bubbleView.layer.borderColor = StormSkyColors.accent.cgColor
            
            NSLayoutConstraint.activate([
                bubbleView.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
                bubbleView.leadingAnchor.constraint(greaterThanOrEqualTo: leadingAnchor, constant: 60)
            ])
        } else {
            // AI message - left aligned
            bubbleView.backgroundColor = StormSkyColors.backgroundSecondary
            messageLabel.textColor = StormSkyColors.textPrimary
            timeLabel.textColor = StormSkyColors.textSecondary
            bubbleView.layer.borderColor = StormSkyColors.accent.cgColor
            
            NSLayoutConstraint.activate([
                bubbleView.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
                bubbleView.trailingAnchor.constraint(lessThanOrEqualTo: trailingAnchor, constant: -60)
            ])
        }
    }
    
    private func formatTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

