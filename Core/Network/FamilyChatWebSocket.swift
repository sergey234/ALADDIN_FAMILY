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
    var onTyping: ((String, Bool) -> Void)? // Имя пользователя, печатает ли сейчас
    var onPresence: ((String, Bool) -> Void)? // Имя пользователя, online/offline
    var onConnectionStatus: ((ConnectionStatus) -> Void)?
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
    
    /// WS часто отдаёт snake_case; REST может быть camelCase — пробуем оба декодера.
    private static let snakeCaseMessageDecoder: JSONDecoder = {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        return d
    }()
    
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
        
        setConnectionStatus(.connecting)
        SyncEngine.shared.publish(domain: .familyChat, operation: "ws_connect", state: .syncing)
        isConnected = false
        
        let wsURL = "\(baseURL)/ws/family/chat"
        guard let url = URL(string: wsURL) else {
            setConnectionStatus(.error)
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
        if connectionStatus == .connected {
            sendMessage(type: "presence", data: ["status": "offline"])
        }
        stopPingTimer()
        stopReconnectTimer()
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        webSocketTask = nil
        urlSession?.invalidateAndCancel()
        urlSession = nil
        
        setConnectionStatus(.disconnected)
        SyncEngine.shared.publish(domain: .familyChat, operation: "ws_disconnect", state: .idle)
        isConnected = false
        
        print("✅ FamilyChatWebSocket: Отключено")
    }
    
    // MARK: - Send Methods
    
    func sendTyping() {
        sendMessage(type: "typing", data: ["is_typing": true])
    }

    func sendStopTyping() {
        sendMessage(type: "typing", data: ["is_typing": false])
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
            let blob: [String: Any]? = (json["message"] as? [String: Any]) ?? (json["payload"] as? [String: Any])
            if let messageData = blob,
               let jsonData = try? JSONSerialization.data(withJSONObject: messageData) {
                let message =
                    (try? Self.snakeCaseMessageDecoder.decode(FamilyChatMessageResponse.self, from: jsonData))
                    ?? (try? JSONDecoder().decode(FamilyChatMessageResponse.self, from: jsonData))
                if let message {
                    DispatchQueue.main.async {
                        self.onNewMessage?(message)
                        SyncEngine.shared.publish(
                            domain: .familyChat,
                            operation: "ws_new_message",
                            state: .synced,
                            recordId: message.id
                        )
                    }
                }
            }
            
        case "typing":
            let userName = (json["user"] as? String)
                ?? (json["user_name"] as? String)
                ?? (json["sender"] as? String)
            let isTyping = (json["is_typing"] as? Bool) ?? true
            if let userName, !userName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                DispatchQueue.main.async {
                    self.onTyping?(userName, isTyping)
                }
            }

        case "presence", "presence_update", "member_presence":
            let userName = (json["user"] as? String)
                ?? (json["user_name"] as? String)
                ?? (json["member"] as? String)
            let isOnline: Bool = {
                if let flag = json["is_online"] as? Bool { return flag }
                if let flag = json["online"] as? Bool { return flag }
                if let status = (json["status"] as? String)?.lowercased() {
                    return status == "online"
                }
                return true
            }()
            if let userName, !userName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                DispatchQueue.main.async {
                    self.onPresence?(userName, isOnline)
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
        if connectionStatus == .disconnected || connectionStatus == .error {
            return
        }
        
        setConnectionStatus(.disconnected)
        isConnected = false
        stopPingTimer()
        
        if reconnectAttempts < maxReconnectAttempts {
            reconnectAttempts += 1
            setConnectionStatus(.reconnecting)
            startReconnectTimer()
        } else {
            setConnectionStatus(.error)
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
            self.setConnectionStatus(.connected)
            self.isConnected = true
            self.reconnectAttempts = 0
            self.lastError = nil
            self.sendMessage(type: "presence", data: ["status": "online"])
            print("✅ FamilyChatWebSocket: Подключено успешно")
        }
    }
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        DispatchQueue.main.async {
            self.handleDisconnection()
            print("⚠️ FamilyChatWebSocket: Соединение закрыто: \(closeCode)")
        }
    }

    private func setConnectionStatus(_ status: ConnectionStatus) {
        connectionStatus = status
        switch status {
        case .connected:
            SyncEngine.shared.publish(domain: .familyChat, operation: "ws_status", state: .synced)
        case .connecting, .reconnecting:
            SyncEngine.shared.publish(domain: .familyChat, operation: "ws_status", state: .syncing)
        case .disconnected:
            SyncEngine.shared.publish(domain: .familyChat, operation: "ws_status", state: .idle)
        case .error:
            SyncEngine.shared.publish(domain: .familyChat, operation: "ws_status", state: .error(lastError ?? "websocket_error"))
        }
        if Thread.isMainThread {
            onConnectionStatus?(status)
        } else {
            DispatchQueue.main.async {
                self.onConnectionStatus?(status)
            }
        }
    }
}

