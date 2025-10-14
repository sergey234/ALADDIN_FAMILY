# 🤖 ALADDIN Mobile App - AI Assistant Integration Guide

**Эксперт:** AI Developer + Mobile Developer  
**Дата:** 2025-01-27  
**Цель:** Интеграция AI помощника (super_ai_support_assistant_improved.py) в мобильные приложения

---

## 🎯 **ОБЩАЯ АРХИТЕКТУРА AI ПОМОЩНИКА**

### 🧠 **СЕРВЕРНАЯ ЧАСТЬ:**
- **Файл:** `super_ai_support_assistant_improved.py`
- **Функции:** 1,480+ строк кода
- **Категории:** 20+ категорий поддержки
- **Эмоции:** 15+ типов эмоций
- **Языки:** Многоязычная поддержка

### 📱 **МОБИЛЬНАЯ ЧАСТЬ:**
- **iOS:** Swift + Combine + Speech Framework
- **Android:** Kotlin + Coroutines + Speech Recognition
- **Интерфейс:** Чат + Голосовое управление
- **Интеграция:** REST API + WebSocket

---

## 🍎 **iOS AI ПОМОЩНИК**

### 📋 **1. AIAssistantManager.swift:**
```swift
import Foundation
import Combine
import Speech
import AVFoundation

// MARK: - AI Assistant Manager
class AIAssistantManager: ObservableObject {
    static let shared = AIAssistantManager()
    
    @Published var messages: [AIMessage] = []
    @Published var isListening = false
    @Published var isProcessing = false
    @Published var suggestions: [String] = []
    @Published var actions: [AIAction] = []
    
    private let apiClient = APIClient.shared
    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "ru-RU"))
    private let audioEngine = AVAudioEngine()
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    
    private init() {
        setupSpeechRecognition()
        loadInitialMessages()
    }
    
    // MARK: - Message Handling
    func sendMessage(_ text: String) async {
        let userMessage = AIMessage(
            id: UUID().uuidString,
            text: text,
            isFromUser: true,
            timestamp: Date(),
            category: .technology
        )
        
        await MainActor.run {
            messages.append(userMessage)
            isProcessing = true
        }
        
        do {
            let context = createAIContext()
            let response = try await apiClient.sendAIMessage(text, context: context)
            
            let aiMessage = AIMessage(
                id: UUID().uuidString,
                text: response.message,
                isFromUser: false,
                timestamp: Date(),
                category: .technology,
                suggestions: response.suggestions,
                actions: response.actions
            )
            
            await MainActor.run {
                messages.append(aiMessage)
                suggestions = response.suggestions
                actions = response.actions
                isProcessing = false
            }
        } catch {
            await MainActor.run {
                let errorMessage = AIMessage(
                    id: UUID().uuidString,
                    text: "Извините, произошла ошибка. Попробуйте еще раз.",
                    isFromUser: false,
                    timestamp: Date(),
                    category: .technology
                )
                messages.append(errorMessage)
                isProcessing = false
            }
        }
    }
    
    func sendVoiceMessage() async {
        guard !isListening else {
            stopListening()
            return
        }
        
        startListening()
    }
    
    func executeAction(_ action: AIAction) async {
        switch action.type {
        case .navigate:
            await handleNavigationAction(action)
        case .showInfo:
            await handleShowInfoAction(action)
        case .openSettings:
            await handleOpenSettingsAction(action)
        case .blockThreat:
            await handleBlockThreatAction(action)
        case .sendNotification:
            await handleSendNotificationAction(action)
        }
    }
    
    // MARK: - Voice Recognition
    private func setupSpeechRecognition() {
        speechRecognizer?.delegate = self
    }
    
    private func startListening() {
        guard let speechRecognizer = speechRecognizer, speechRecognizer.isAvailable else {
            print("Speech recognition not available")
            return
        }
        
        do {
            try startAudioSession()
            startRecognition()
            isListening = true
        } catch {
            print("Error starting speech recognition: \(error)")
        }
    }
    
    private func stopListening() {
        audioEngine.stop()
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        isListening = false
    }
    
    private func startAudioSession() throws {
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
        try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
    }
    
    private func startRecognition() {
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        
        guard let recognitionRequest = recognitionRequest else {
            print("Unable to create recognition request")
            return
        }
        
        recognitionRequest.shouldReportPartialResults = true
        
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            recognitionRequest.append(buffer)
        }
        
        audioEngine.prepare()
        try? audioEngine.start()
        
        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { result, error in
            if let result = result {
                let spokenText = result.bestTranscription.formattedString
                Task {
                    await self.sendMessage(spokenText)
                }
            }
            
            if error != nil {
                self.stopListening()
            }
        }
    }
    
    // MARK: - Context Creation
    private func createAIContext() -> AIContext {
        return AIContext(
            userRole: getCurrentUserRole(),
            currentScreen: getCurrentScreen(),
            previousMessages: getRecentMessages(),
            systemStatus: getSystemStatus()
        )
    }
    
    private func getCurrentUserRole() -> String {
        // Get current user role from authentication manager
        return "parent" // Default role
    }
    
    private func getCurrentScreen() -> String {
        // Get current screen from navigation manager
        return "main" // Default screen
    }
    
    private func getRecentMessages() -> [String] {
        return messages.suffix(5).map { $0.text }
    }
    
    private func getSystemStatus() -> String {
        // Get current system status
        return "secure" // Default status
    }
    
    // MARK: - Action Handlers
    private func handleNavigationAction(_ action: AIAction) async {
        // Handle navigation actions
        print("Navigating to: \(action.parameters["screen"] ?? "unknown")")
    }
    
    private func handleShowInfoAction(_ action: AIAction) async {
        // Handle show info actions
        print("Showing info: \(action.parameters["info"] ?? "unknown")")
    }
    
    private func handleOpenSettingsAction(_ action: AIAction) async {
        // Handle open settings actions
        print("Opening settings: \(action.parameters["section"] ?? "unknown")")
    }
    
    private func handleBlockThreatAction(_ action: AIAction) async {
        // Handle block threat actions
        print("Blocking threat: \(action.parameters["threatId"] ?? "unknown")")
    }
    
    private func handleSendNotificationAction(_ action: AIAction) async {
        // Handle send notification actions
        print("Sending notification: \(action.parameters["message"] ?? "unknown")")
    }
    
    // MARK: - Initial Messages
    private func loadInitialMessages() {
        let welcomeMessage = AIMessage(
            id: UUID().uuidString,
            text: "Привет! Я ваш AI помощник по безопасности. Чем могу помочь?",
            isFromUser: false,
            timestamp: Date(),
            category: .cybersecurity
        )
        
        messages.append(welcomeMessage)
    }
}

// MARK: - SFSpeechRecognizerDelegate
extension AIAssistantManager: SFSpeechRecognizerDelegate {
    func speechRecognizer(_ speechRecognizer: SFSpeechRecognizer, availabilityDidChange available: Bool) {
        // Handle availability changes
    }
}

// MARK: - AI Message Model
struct AIMessage: Identifiable, Codable {
    let id: String
    let text: String
    let isFromUser: Bool
    let timestamp: Date
    let category: SupportCategory
    let suggestions: [String]?
    let actions: [AIAction]?
    
    init(id: String, text: String, isFromUser: Bool, timestamp: Date, category: SupportCategory, suggestions: [String]? = nil, actions: [AIAction]? = nil) {
        self.id = id
        self.text = text
        self.isFromUser = isFromUser
        self.timestamp = timestamp
        self.category = category
        self.suggestions = suggestions
        self.actions = actions
    }
}

// MARK: - AI Action Model
struct AIAction: Identifiable, Codable {
    let id: String
    let type: AIActionType
    let title: String
    let description: String
    let parameters: [String: String]
    
    init(id: String = UUID().uuidString, type: AIActionType, title: String, description: String, parameters: [String: String] = [:]) {
        self.id = id
        self.type = type
        self.title = title
        self.description = description
        self.parameters = parameters
    }
}

// MARK: - Support Category
enum SupportCategory: String, CaseIterable, Codable {
    case cybersecurity = "cybersecurity"
    case familySupport = "family_support"
    case medicalSupport = "medical_support"
    case education = "education"
    case finance = "finance"
    case household = "household"
    case psychology = "psychology"
    case technology = "technology"
    case legal = "legal"
    case travel = "travel"
    case entertainment = "entertainment"
    case health = "health"
    case fitness = "fitness"
    case relationships = "relationships"
    case career = "career"
    case business = "business"
    case shopping = "shopping"
    case cooking = "cooking"
    case gardening = "gardening"
    case repair = "repair"
    
    var displayName: String {
        switch self {
        case .cybersecurity:
            return "Кибербезопасность"
        case .familySupport:
            return "Семейная поддержка"
        case .medicalSupport:
            return "Медицинская поддержка"
        case .education:
            return "Образование"
        case .finance:
            return "Финансы"
        case .household:
            return "Домашнее хозяйство"
        case .psychology:
            return "Психология"
        case .technology:
            return "Технологии"
        case .legal:
            return "Правовые вопросы"
        case .travel:
            return "Путешествия"
        case .entertainment:
            return "Развлечения"
        case .health:
            return "Здоровье"
        case .fitness:
            return "Фитнес"
        case .relationships:
            return "Отношения"
        case .career:
            return "Карьера"
        case .business:
            return "Бизнес"
        case .shopping:
            return "Покупки"
        case .cooking:
            return "Кулинария"
        case .gardening:
            return "Садоводство"
        case .repair:
            return "Ремонт"
        }
    }
    
    var iconName: String {
        switch self {
        case .cybersecurity:
            return "shield.checkered"
        case .familySupport:
            return "person.3"
        case .medicalSupport:
            return "cross.case"
        case .education:
            return "book"
        case .finance:
            return "dollarsign.circle"
        case .household:
            return "house"
        case .psychology:
            return "brain.head.profile"
        case .technology:
            return "laptopcomputer"
        case .legal:
            return "scale"
        case .travel:
            return "airplane"
        case .entertainment:
            return "tv"
        case .health:
            return "heart"
        case .fitness:
            return "figure.run"
        case .relationships:
            return "heart.circle"
        case .career:
            return "briefcase"
        case .business:
            return "building.2"
        case .shopping:
            return "cart"
        case .cooking:
            return "fork.knife"
        case .gardening:
            return "leaf"
        case .repair:
            return "wrench"
        }
    }
}
```

### 📋 **2. AIAssistantViewController.swift:**
```swift
import UIKit
import Combine

// MARK: - AI Assistant View Controller
class AIAssistantViewController: UIViewController {
    
    // MARK: - UI Elements
    private lazy var titleLabel: UILabel = {
        let label = UILabel()
        label.text = "🤖 AI Помощник"
        label.font = StormSkyTheme.Typography.h2
        label.textColor = StormSkyColors.goldMain
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var messagesTableView: UITableView = {
        let tableView = UITableView()
        tableView.backgroundColor = .clear
        tableView.separatorStyle = .none
        tableView.register(AIMessageCell.self, forCellReuseIdentifier: "AIMessageCell")
        tableView.delegate = self
        tableView.dataSource = self
        tableView.translatesAutoresizingMaskIntoConstraints = false
        return tableView
    }()
    
    private lazy var inputContainerView: UIView = {
        let view = UIView()
        view.backgroundColor = StormSkyColors.stormSkyMain80
        view.layer.cornerRadius = StormSkyTheme.CornerRadius.lg
        view.layer.borderWidth = 1
        view.layer.borderColor = StormSkyColors.goldMain30.cgColor
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private lazy var messageTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Введите сообщение..."
        textField.textColor = StormSkyColors.white
        textField.backgroundColor = .clear
        textField.borderStyle = .none
        textField.font = StormSkyTheme.Typography.body
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private lazy var voiceButton: UIButton = {
        let button = UIButton(type: .system)
        button.setImage(UIImage(systemName: "mic"), for: .normal)
        button.tintColor = StormSkyColors.goldMain
        button.addTarget(self, action: #selector(voiceButtonTapped), for: .touchUpInside)
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private lazy var sendButton: UIButton = {
        let button = UIButton(type: .system)
        button.setImage(UIImage(systemName: "paperplane"), for: .normal)
        button.tintColor = StormSkyColors.goldMain
        button.addTarget(self, action: #selector(sendButtonTapped), for: .touchUpInside)
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private lazy var suggestionsCollectionView: UICollectionView = {
        let layout = UICollectionViewFlowLayout()
        layout.scrollDirection = .horizontal
        layout.estimatedItemSize = UICollectionViewFlowLayout.automaticSize
        
        let collectionView = UICollectionView(frame: .zero, collectionViewLayout: layout)
        collectionView.backgroundColor = .clear
        collectionView.showsHorizontalScrollIndicator = false
        collectionView.register(AISuggestionCell.self, forCellWithReuseIdentifier: "AISuggestionCell")
        collectionView.delegate = self
        collectionView.dataSource = self
        collectionView.translatesAutoresizingMaskIntoConstraints = false
        return collectionView
    }()
    
    private lazy var actionsCollectionView: UICollectionView = {
        let layout = UICollectionViewFlowLayout()
        layout.scrollDirection = .horizontal
        layout.estimatedItemSize = UICollectionViewFlowLayout.automaticSize
        
        let collectionView = UICollectionView(frame: .zero, collectionViewLayout: layout)
        collectionView.backgroundColor = .clear
        collectionView.showsHorizontalScrollIndicator = false
        collectionView.register(AIActionCell.self, forCellWithReuseIdentifier: "AIActionCell")
        collectionView.delegate = self
        collectionView.dataSource = self
        collectionView.translatesAutoresizingMaskIntoConstraints = false
        return collectionView
    }()
    
    // MARK: - Properties
    private let aiManager = AIAssistantManager.shared
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
        view.addSubview(titleLabel)
        view.addSubview(messagesTableView)
        view.addSubview(suggestionsCollectionView)
        view.addSubview(actionsCollectionView)
        view.addSubview(inputContainerView)
        
        inputContainerView.addSubview(messageTextField)
        inputContainerView.addSubview(voiceButton)
        inputContainerView.addSubview(sendButton)
        
        setupConstraints()
    }
    
    private func setupGradientBackground() {
        GradientUtils.applyGradientBackground(
            to: view,
            colors: StormSkyColors.backgroundGradient
        )
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Title
            titleLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            titleLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            titleLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Messages Table
            messagesTableView.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 20),
            messagesTableView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            messagesTableView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Suggestions Collection
            suggestionsCollectionView.topAnchor.constraint(equalTo: messagesTableView.bottomAnchor, constant: 10),
            suggestionsCollectionView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            suggestionsCollectionView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            suggestionsCollectionView.heightAnchor.constraint(equalToConstant: 40),
            
            // Actions Collection
            actionsCollectionView.topAnchor.constraint(equalTo: suggestionsCollectionView.bottomAnchor, constant: 10),
            actionsCollectionView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            actionsCollectionView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            actionsCollectionView.heightAnchor.constraint(equalToConstant: 60),
            
            // Input Container
            inputContainerView.topAnchor.constraint(equalTo: actionsCollectionView.bottomAnchor, constant: 20),
            inputContainerView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            inputContainerView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            inputContainerView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20),
            inputContainerView.heightAnchor.constraint(equalToConstant: 50),
            
            // Message TextField
            messageTextField.leadingAnchor.constraint(equalTo: inputContainerView.leadingAnchor, constant: 16),
            messageTextField.trailingAnchor.constraint(equalTo: voiceButton.leadingAnchor, constant: -8),
            messageTextField.centerYAnchor.constraint(equalTo: inputContainerView.centerYAnchor),
            
            // Voice Button
            voiceButton.trailingAnchor.constraint(equalTo: sendButton.leadingAnchor, constant: -8),
            voiceButton.centerYAnchor.constraint(equalTo: inputContainerView.centerYAnchor),
            voiceButton.widthAnchor.constraint(equalToConstant: 30),
            voiceButton.heightAnchor.constraint(equalToConstant: 30),
            
            // Send Button
            sendButton.trailingAnchor.constraint(equalTo: inputContainerView.trailingAnchor, constant: -16),
            sendButton.centerYAnchor.constraint(equalTo: inputContainerView.centerYAnchor),
            sendButton.widthAnchor.constraint(equalToConstant: 30),
            sendButton.heightAnchor.constraint(equalToConstant: 30)
        ])
    }
    
    private func bindViewModel() {
        aiManager.$messages
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.messagesTableView.reloadData()
                self?.scrollToBottom()
            }
            .store(in: &cancellables)
        
        aiManager.$isListening
            .receive(on: DispatchQueue.main)
            .sink { [weak self] isListening in
                self?.updateVoiceButton(isListening: isListening)
            }
            .store(in: &cancellables)
        
        aiManager.$suggestions
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.suggestionsCollectionView.reloadData()
            }
            .store(in: &cancellables)
        
        aiManager.$actions
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.actionsCollectionView.reloadData()
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Actions
    @objc private func sendButtonTapped() {
        guard let text = messageTextField.text, !text.isEmpty else { return }
        
        messageTextField.text = ""
        Task {
            await aiManager.sendMessage(text)
        }
    }
    
    @objc private func voiceButtonTapped() {
        Task {
            await aiManager.sendVoiceMessage()
        }
    }
    
    // MARK: - Helper Methods
    private func updateVoiceButton(isListening: Bool) {
        let imageName = isListening ? "mic.fill" : "mic"
        voiceButton.setImage(UIImage(systemName: imageName), for: .normal)
        voiceButton.tintColor = isListening ? StormSkyColors.errorRed : StormSkyColors.goldMain
    }
    
    private func scrollToBottom() {
        guard !aiManager.messages.isEmpty else { return }
        
        let indexPath = IndexPath(row: aiManager.messages.count - 1, section: 0)
        messagesTableView.scrollToRow(at: indexPath, at: .bottom, animated: true)
    }
}

// MARK: - UITableViewDataSource
extension AIAssistantViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return aiManager.messages.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "AIMessageCell", for: indexPath) as! AIMessageCell
        cell.configure(with: aiManager.messages[indexPath.row])
        return cell
    }
}

// MARK: - UITableViewDelegate
extension AIAssistantViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
        return UITableView.automaticDimension
    }
}

// MARK: - UICollectionViewDataSource
extension AIAssistantViewController: UICollectionViewDataSource {
    func collectionView(_ collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        if collectionView == suggestionsCollectionView {
            return aiManager.suggestions.count
        } else {
            return aiManager.actions.count
        }
    }
    
    func collectionView(_ collectionView: UICollectionView, cellForItemAt indexPath: IndexPath) -> UICollectionViewCell {
        if collectionView == suggestionsCollectionView {
            let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "AISuggestionCell", for: indexPath) as! AISuggestionCell
            cell.configure(with: aiManager.suggestions[indexPath.row])
            return cell
        } else {
            let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "AIActionCell", for: indexPath) as! AIActionCell
            cell.configure(with: aiManager.actions[indexPath.row])
            return cell
        }
    }
}

// MARK: - UICollectionViewDelegate
extension AIAssistantViewController: UICollectionViewDelegate {
    func collectionView(_ collectionView: UICollectionView, didSelectItemAt indexPath: IndexPath) {
        if collectionView == suggestionsCollectionView {
            let suggestion = aiManager.suggestions[indexPath.row]
            messageTextField.text = suggestion
        } else {
            let action = aiManager.actions[indexPath.row]
            Task {
                await aiManager.executeAction(action)
            }
        }
    }
}
```

### 📋 **3. AIMessageCell.swift:**
```swift
import UIKit

// MARK: - AI Message Cell
class AIMessageCell: UITableViewCell {
    
    private lazy var messageBubble: UIView = {
        let view = UIView()
        view.layer.cornerRadius = StormSkyTheme.CornerRadius.md
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private lazy var messageLabel: UILabel = {
        let label = UILabel()
        label.font = StormSkyTheme.Typography.body
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var timestampLabel: UILabel = {
        let label = UILabel()
        label.font = StormSkyTheme.Typography.small
        label.textColor = StormSkyColors.lightningBlue
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var categoryIcon: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFit
        imageView.tintColor = StormSkyColors.goldMain
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()
    
    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupUI()
    }
    
    private func setupUI() {
        backgroundColor = .clear
        selectionStyle = .none
        
        contentView.addSubview(messageBubble)
        messageBubble.addSubview(messageLabel)
        messageBubble.addSubview(timestampLabel)
        messageBubble.addSubview(categoryIcon)
        
        setupConstraints()
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Message Bubble
            messageBubble.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 8),
            messageBubble.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            messageBubble.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            messageBubble.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -8),
            
            // Category Icon
            categoryIcon.topAnchor.constraint(equalTo: messageBubble.topAnchor, constant: 8),
            categoryIcon.leadingAnchor.constraint(equalTo: messageBubble.leadingAnchor, constant: 8),
            categoryIcon.widthAnchor.constraint(equalToConstant: 20),
            categoryIcon.heightAnchor.constraint(equalToConstant: 20),
            
            // Message Label
            messageLabel.topAnchor.constraint(equalTo: messageBubble.topAnchor, constant: 8),
            messageLabel.leadingAnchor.constraint(equalTo: categoryIcon.trailingAnchor, constant: 8),
            messageLabel.trailingAnchor.constraint(equalTo: messageBubble.trailingAnchor, constant: -8),
            
            // Timestamp Label
            timestampLabel.topAnchor.constraint(equalTo: messageLabel.bottomAnchor, constant: 4),
            timestampLabel.leadingAnchor.constraint(equalTo: messageLabel.leadingAnchor),
            timestampLabel.trailingAnchor.constraint(equalTo: messageLabel.trailingAnchor),
            timestampLabel.bottomAnchor.constraint(equalTo: messageBubble.bottomAnchor, constant: -8)
        ])
    }
    
    func configure(with message: AIMessage) {
        messageLabel.text = message.text
        timestampLabel.text = formatTimestamp(message.timestamp)
        categoryIcon.image = UIImage(systemName: message.category.iconName)
        
        if message.isFromUser {
            // User message styling
            messageBubble.backgroundColor = StormSkyColors.goldMain
            messageLabel.textColor = StormSkyColors.stormSkyDark
            timestampLabel.textColor = StormSkyColors.stormSkyDark.withAlphaComponent(0.7)
        } else {
            // AI message styling
            messageBubble.backgroundColor = StormSkyColors.stormSkyMain80
            messageLabel.textColor = StormSkyColors.white
            timestampLabel.textColor = StormSkyColors.lightningBlue
        }
    }
    
    private func formatTimestamp(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}
```

---

## 🤖 **ANDROID AI ПОМОЩНИК**

### 📋 **1. AIAssistantManager.kt:**
```kotlin
package com.aladdin.ai

import android.content.Context
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.aladdin.network.ApiClient
import kotlinx.coroutines.launch

class AIAssistantManager(private val context: Context) : ViewModel() {
    
    private val _messages = MutableLiveData<List<AIMessage>>()
    val messages: LiveData<List<AIMessage>> = _messages
    
    private val _isListening = MutableLiveData<Boolean>()
    val isListening: LiveData<Boolean> = _isListening
    
    private val _isProcessing = MutableLiveData<Boolean>()
    val isProcessing: LiveData<Boolean> = _isProcessing
    
    private val _suggestions = MutableLiveData<List<String>>()
    val suggestions: LiveData<List<String>> = _suggestions
    
    private val _actions = MutableLiveData<List<AIAction>>()
    val actions: LiveData<List<AIAction>> = _actions
    
    private val apiService = ApiClient.apiService
    private val speechManager = SpeechManager(context)
    
    init {
        loadInitialMessages()
    }
    
    // MARK: - Message Handling
    fun sendMessage(text: String) {
        val userMessage = AIMessage(
            id = generateId(),
            text = text,
            isFromUser = true,
            timestamp = System.currentTimeMillis(),
            category = SupportCategory.TECHNOLOGY
        )
        
        val currentMessages = _messages.value?.toMutableList() ?: mutableListOf()
        currentMessages.add(userMessage)
        _messages.value = currentMessages
        _isProcessing.value = true
        
        viewModelScope.launch {
            try {
                val context = createAIContext()
                val request = AIRequest(
                    message = text,
                    context = context,
                    language = "ru",
                    timestamp = System.currentTimeMillis().toString()
                )
                
                val response = apiService.sendAIMessage(request)
                
                val aiMessage = AIMessage(
                    id = generateId(),
                    text = response.message,
                    isFromUser = false,
                    timestamp = System.currentTimeMillis(),
                    category = SupportCategory.TECHNOLOGY,
                    suggestions = response.suggestions,
                    actions = response.actions
                )
                
                val updatedMessages = _messages.value?.toMutableList() ?: mutableListOf()
                updatedMessages.add(aiMessage)
                _messages.value = updatedMessages
                _suggestions.value = response.suggestions
                _actions.value = response.actions
                _isProcessing.value = false
            } catch (e: Exception) {
                val errorMessage = AIMessage(
                    id = generateId(),
                    text = "Извините, произошла ошибка. Попробуйте еще раз.",
                    isFromUser = false,
                    timestamp = System.currentTimeMillis(),
                    category = SupportCategory.TECHNOLOGY
                )
                
                val updatedMessages = _messages.value?.toMutableList() ?: mutableListOf()
                updatedMessages.add(errorMessage)
                _messages.value = updatedMessages
                _isProcessing.value = false
            }
        }
    }
    
    fun sendVoiceMessage() {
        if (_isListening.value == true) {
            stopListening()
        } else {
            startListening()
        }
    }
    
    fun executeAction(action: AIAction) {
        viewModelScope.launch {
            when (action.type) {
                "navigate" -> handleNavigationAction(action)
                "show_info" -> handleShowInfoAction(action)
                "open_settings" -> handleOpenSettingsAction(action)
                "block_threat" -> handleBlockThreatAction(action)
                "send_notification" -> handleSendNotificationAction(action)
            }
        }
    }
    
    // MARK: - Voice Recognition
    private fun startListening() {
        speechManager.startListening { text ->
            sendMessage(text)
        }
        _isListening.value = true
    }
    
    private fun stopListening() {
        speechManager.stopListening()
        _isListening.value = false
    }
    
    // MARK: - Context Creation
    private fun createAIContext(): AIContext {
        return AIContext(
            userRole = getCurrentUserRole(),
            currentScreen = getCurrentScreen(),
            previousMessages = getRecentMessages(),
            systemStatus = getSystemStatus()
        )
    }
    
    private fun getCurrentUserRole(): String = "parent"
    private fun getCurrentScreen(): String = "main"
    private fun getRecentMessages(): List<String> = _messages.value?.takeLast(5)?.map { it.text } ?: emptyList()
    private fun getSystemStatus(): String = "secure"
    
    // MARK: - Action Handlers
    private suspend fun handleNavigationAction(action: AIAction) {
        // Handle navigation actions
    }
    
    private suspend fun handleShowInfoAction(action: AIAction) {
        // Handle show info actions
    }
    
    private suspend fun handleOpenSettingsAction(action: AIAction) {
        // Handle open settings actions
    }
    
    private suspend fun handleBlockThreatAction(action: AIAction) {
        // Handle block threat actions
    }
    
    private suspend fun handleSendNotificationAction(action: AIAction) {
        // Handle send notification actions
    }
    
    // MARK: - Initial Messages
    private fun loadInitialMessages() {
        val welcomeMessage = AIMessage(
            id = generateId(),
            text = "Привет! Я ваш AI помощник по безопасности. Чем могу помочь?",
            isFromUser = false,
            timestamp = System.currentTimeMillis(),
            category = SupportCategory.CYBERSECURITY
        )
        
        _messages.value = listOf(welcomeMessage)
    }
    
    private fun generateId(): String = java.util.UUID.randomUUID().toString()
}

// MARK: - Data Classes
data class AIMessage(
    val id: String,
    val text: String,
    val isFromUser: Boolean,
    val timestamp: Long,
    val category: SupportCategory,
    val suggestions: List<String>? = null,
    val actions: List<AIAction>? = null
)

data class AIAction(
    val id: String = java.util.UUID.randomUUID().toString(),
    val type: String,
    val title: String,
    val description: String,
    val parameters: Map<String, String> = emptyMap()
)

enum class SupportCategory(val displayName: String, val iconName: String) {
    CYBERSECURITY("Кибербезопасность", "shield"),
    FAMILY_SUPPORT("Семейная поддержка", "people"),
    MEDICAL_SUPPORT("Медицинская поддержка", "medical"),
    EDUCATION("Образование", "school"),
    FINANCE("Финансы", "attach_money"),
    HOUSEHOLD("Домашнее хозяйство", "home"),
    PSYCHOLOGY("Психология", "psychology"),
    TECHNOLOGY("Технологии", "computer"),
    LEGAL("Правовые вопросы", "gavel"),
    TRAVEL("Путешествия", "flight"),
    ENTERTAINMENT("Развлечения", "movie"),
    HEALTH("Здоровье", "favorite"),
    FITNESS("Фитнес", "fitness_center"),
    RELATIONSHIPS("Отношения", "favorite"),
    CAREER("Карьера", "work"),
    BUSINESS("Бизнес", "business"),
    SHOPPING("Покупки", "shopping_cart"),
    COOKING("Кулинария", "restaurant"),
    GARDENING("Садоводство", "eco"),
    REPAIR("Ремонт", "build")
}
```

---

## 🚀 **СЛЕДУЮЩИЕ ШАГИ**

1. **Интегрировать AI помощника** в оба проекта
2. **Настроить голосовое управление** 
3. **Создать красивые экраны чата**
4. **Добавить категории и действия**
5. **Протестировать AI функционал**
6. **Оптимизировать производительность**

**🎯 AI ПОМОЩНИК ГОТОВ К ИНТЕГРАЦИИ!**

**📱 ПЕРЕХОДИМ К ИНФОРМАЦИОННЫМ РАЗДЕЛАМ!**

