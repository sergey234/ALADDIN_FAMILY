import Foundation
import Combine

/**
 * 🌐 Family Chat WebSocket Manager
 * Real-time обновления для семейного чата
 */

class FamilyChatWebSocket: NSObject, ObservableObject, URLSessionWebSocketDelegate {
    
    // MARK: - Published Properties
    
    @Published var isConnected: Bool = false
    @Published var connectionStatus: ConnectionStatus = .disconnected
    @Published var lastError: String? = nil
    
    // MARK: - Callbacks
    
    var onNewMessage: ((FamilyChatMessageResponse) -> Void)?
    var onTyping: ((String) -> Void)? // Имя пользователя
    var onMessageDeleted: ((String) -> Void)? // ID сообщения
    var onMessageEdited: ((String, String) -> Void)? // ID сообщения, новый текст
    var onReaction: ((String, MessageReaction) -> Void)? // ID сообщения, реакция
    var onReadStatus: ((String, String) -> Void)? // ID сообщения, статус
    
    // MARK: - Private Properties
    
    private var webSocketTask: URLSessionWebSocketTask?
    private var urlSession: URLSession?
    private var reconnectTimer: Timer?
    private var pingTimer: Timer?
    private var reconnectAttempts: Int = 0
    private let maxReconnectAttempts: Int = 5
    private let reconnectDelay: TimeInterval = 3.0
    
    private let familyId: String?
    private let baseURL: String
    
    enum ConnectionStatus {
        case disconnected
        case connecting
        case connected
        case reconnecting
        case error
    }
    
    // MARK: - Initialization
    
    init(familyId: String?, baseURL: String = AppConfig.apiBaseURL) {
        self.familyId = familyId
        self.baseURL = baseURL.replacingOccurrences(of: "/api", with: "").replacingOccurrences(of: "https://", with: "wss://").replacingOccurrences(of: "http://", with: "ws://")
        super.init()
    }
    
    // MARK: - Connection Methods
    
    func connect() {
        guard connectionStatus != .connected && connectionStatus != .connecting else {
            print("⚠️ FamilyChatWebSocket: Уже подключен или подключается")
            return
        }
        
        connectionStatus = .connecting
        isConnected = false
        
        let wsURL = "\(baseURL)/ws/family/chat"
        guard let url = URL(string: wsURL) else {
            connectionStatus = .error
            lastError = "Неверный URL WebSocket"
            return
        }
        
        var request = URLRequest(url: url)
        if let token = AppConfig.authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        if let familyId = familyId {
            request.setValue(familyId, forHTTPHeaderField: "X-Family-Id")
        }
        
        urlSession = URLSession(configuration: .default, delegate: self, delegateQueue: nil)
        webSocketTask = urlSession?.webSocketTask(with: request)
        webSocketTask?.resume()
        
        receiveMessage()
        startPingTimer()
        
        print("✅ FamilyChatWebSocket: Подключение к \(wsURL)")
    }
    
    func disconnect() {
        stopPingTimer()
        stopReconnectTimer()
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        webSocketTask = nil
        urlSession?.invalidateAndCancel()
        urlSession = nil
        
        connectionStatus = .disconnected
        isConnected = false
        
        print("✅ FamilyChatWebSocket: Отключено")
    }
    
    // MARK: - Send Methods
    
    func sendTyping() {
        sendMessage(type: "typing", data: [:])
    }
    
    func sendMessage(type: String, data: [String: Any]) {
        guard let task = webSocketTask, connectionStatus == .connected else {
            print("⚠️ FamilyChatWebSocket: Не подключен, сообщение не отправлено")
            return
        }
        
        var messageData: [String: Any] = ["type": type]
        messageData.merge(data) { (_, new) in new }
        
        guard let jsonData = try? JSONSerialization.data(withJSONObject: messageData),
              let jsonString = String(data: jsonData, encoding: .utf8) else {
            print("❌ FamilyChatWebSocket: Ошибка сериализации сообщения")
            return
        }
        
        let message = URLSessionWebSocketTask.Message.string(jsonString)
        task.send(message) { error in
            if let error = error {
                print("❌ FamilyChatWebSocket: Ошибка отправки: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Receive Methods
    
    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            guard let self = self else { return }
            
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    self.handleMessage(text)
                case .data(let data):
                    if let text = String(data: data, encoding: .utf8) {
                        self.handleMessage(text)
                    }
                @unknown default:
                    break
                }
                
                // Продолжаем получать сообщения
                self.receiveMessage()
                
            case .failure(let error):
                print("❌ FamilyChatWebSocket: Ошибка получения сообщения: \(error.localizedDescription)")
                self.handleDisconnection()
            }
        }
    }
    
    private func handleMessage(_ text: String) {
        guard let data = text.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = json["type"] as? String else {
            return
        }
        
        switch type {
        case "new_message":
            if let messageData = json["message"] as? [String: Any],
               let jsonData = try? JSONSerialization.data(withJSONObject: messageData),
               let message = try? JSONDecoder().decode(FamilyChatMessageResponse.self, from: jsonData) {
                DispatchQueue.main.async {
                    self.onNewMessage?(message)
                }
            }
            
        case "typing":
            if let userName = json["user"] as? String {
                DispatchQueue.main.async {
                    self.onTyping?(userName)
                }
            }
            
        case "message_deleted":
            if let messageId = json["message_id"] as? String {
                DispatchQueue.main.async {
                    self.onMessageDeleted?(messageId)
                }
            }
            
        case "message_edited":
            if let messageId = json["message_id"] as? String,
               let newText = json["text"] as? String {
                DispatchQueue.main.async {
                    self.onMessageEdited?(messageId, newText)
                }
            }
            
        case "reaction":
            if let messageId = json["message_id"] as? String,
               let reactionData = json["reaction"] as? [String: Any],
               let jsonData = try? JSONSerialization.data(withJSONObject: reactionData),
               let reaction = try? JSONDecoder().decode(MessageReaction.self, from: jsonData) {
                DispatchQueue.main.async {
                    self.onReaction?(messageId, reaction)
                }
            }
            
        case "read_status":
            if let messageId = json["message_id"] as? String,
               let status = json["status"] as? String {
                DispatchQueue.main.async {
                    self.onReadStatus?(messageId, status)
                }
            }
            
        default:
            print("⚠️ FamilyChatWebSocket: Неизвестный тип сообщения: \(type)")
        }
    }
    
    // MARK: - Ping/Pong
    
    private func startPingTimer() {
        pingTimer = Timer.scheduledTimer(withTimeInterval: 30.0, repeats: true) { [weak self] _ in
            self?.sendPing()
        }
    }
    
    private func stopPingTimer() {
        pingTimer?.invalidate()
        pingTimer = nil
    }
    
    private func sendPing() {
        webSocketTask?.sendPing { error in
            if let error = error {
                print("❌ FamilyChatWebSocket: Ошибка ping: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Reconnection
    
    private func handleDisconnection() {
        guard connectionStatus == .connected else { return }
        
        connectionStatus = .disconnected
        isConnected = false
        stopPingTimer()
        
        if reconnectAttempts < maxReconnectAttempts {
            reconnectAttempts += 1
            connectionStatus = .reconnecting
            startReconnectTimer()
        } else {
            connectionStatus = .error
            lastError = "Превышено количество попыток переподключения"
        }
    }
    
    private func startReconnectTimer() {
        stopReconnectTimer()
        reconnectTimer = Timer.scheduledTimer(withTimeInterval: reconnectDelay, repeats: false) { [weak self] _ in
            self?.connect()
        }
    }
    
    private func stopReconnectTimer() {
        reconnectTimer?.invalidate()
        reconnectTimer = nil
    }
    
    // MARK: - URLSessionWebSocketDelegate
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
        DispatchQueue.main.async {
            self.connectionStatus = .connected
            self.isConnected = true
            self.reconnectAttempts = 0
            self.lastError = nil
            print("✅ FamilyChatWebSocket: Подключено успешно")
        }
    }
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        DispatchQueue.main.async {
            self.handleDisconnection()
            print("⚠️ FamilyChatWebSocket: Соединение закрыто: \(closeCode)")
        }
    }
}

