import XCTest
import Combine
@testable import ALADDINMobile

// MARK: - Support Integration Tests для iOS
class SupportIntegrationTests: XCTestCase {
    
    var supportAPI: UnifiedSupportAPIManager!
    var cancellables: Set<AnyCancellable>!
    
    override func setUp() {
        super.setUp()
        supportAPI = UnifiedSupportAPIManager()
        cancellables = Set<AnyCancellable>()
    }
    
    override func tearDown() {
        cancellables = nil
        supportAPI = nil
        super.tearDown()
    }
    
    // MARK: - API Tests
    func testSupportAPIInitialization() {
        XCTAssertNotNil(supportAPI, "Support API should initialize successfully")
    }
    
    func testSendSupportRequest() {
        let expectation = XCTestExpectation(description: "Support request sent")
        
        let request = SupportRequest(
            message: "Тестовое сообщение",
            category: "general",
            priority: .medium,
            context: SupportContext(
                userID: "test_user",
                deviceInfo: "iOS Test",
                appVersion: "1.0.0"
            )
        )
        
        supportAPI.sendSupportRequest(request)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        XCTFail("API request failed: \(error)")
                    }
                    expectation.fulfill()
                },
                receiveValue: { response in
                    XCTAssertNotNil(response, "Response should not be nil")
                    XCTAssertFalse(response.message.isEmpty, "Response message should not be empty")
                    XCTAssertEqual(response.category, "general", "Response category should match")
                }
            )
            .store(in: &cancellables)
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    func testGetRecentTickets() {
        let expectation = XCTestExpectation(description: "Recent tickets loaded")
        
        supportAPI.getRecentTickets()
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        XCTFail("Get recent tickets failed: \(error)")
                    }
                    expectation.fulfill()
                },
                receiveValue: { tickets in
                    XCTAssertNotNil(tickets, "Tickets should not be nil")
                    XCTAssertTrue(tickets is [SupportTicket], "Should return array of tickets")
                }
            )
            .store(in: &cancellables)
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    func testGetSupportStatus() {
        let expectation = XCTestExpectation(description: "Support status loaded")
        
        supportAPI.getSupportStatus()
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        XCTFail("Get support status failed: \(error)")
                    }
                    expectation.fulfill()
                },
                receiveValue: { status in
                    XCTAssertNotNil(status, "Status should not be nil")
                    XCTAssertTrue([SupportStatus.online, .busy, .offline].contains(status), "Status should be valid")
                }
            )
            .store(in: &cancellables)
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    // MARK: - UI Tests
    func testSupportChatInterfaceInitialization() {
        let chatVC = SupportChatInterface()
        XCTAssertNotNil(chatVC, "Support chat interface should initialize")
    }
    
    func testSupportMainInterfaceInitialization() {
        let mainVC = SupportMainInterface()
        XCTAssertNotNil(mainVC, "Support main interface should initialize")
    }
    
    func testSupportMessageCreation() {
        let message = SupportMessage(
            id: "test_id",
            text: "Тестовое сообщение",
            isFromUser: true,
            timestamp: Date(),
            category: "general"
        )
        
        XCTAssertEqual(message.id, "test_id")
        XCTAssertEqual(message.text, "Тестовое сообщение")
        XCTAssertTrue(message.isFromUser)
        XCTAssertEqual(message.category, "general")
    }
    
    // MARK: - Integration Tests
    func testChatToAPIIntegration() {
        let expectation = XCTestExpectation(description: "Chat to API integration")
        
        let chatVC = SupportChatInterface()
        let testMessage = "Интеграционный тест"
        
        // Simulate sending message through chat interface
        let request = SupportRequest(
            message: testMessage,
            category: "general",
            priority: .medium,
            context: SupportContext(
                userID: "integration_test",
                deviceInfo: "iOS Integration Test",
                appVersion: "1.0.0"
            )
        )
        
        supportAPI.sendSupportRequest(request)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        XCTFail("Chat to API integration failed: \(error)")
                    }
                    expectation.fulfill()
                },
                receiveValue: { response in
                    XCTAssertNotNil(response, "API should respond to chat message")
                    XCTAssertTrue(response.message.contains("ALADDIN") || response.message.contains("помощник"), "Response should be relevant")
                }
            )
            .store(in: &cancellables)
        
        wait(for: [expectation], timeout: 15.0)
    }
    
    func testQuickActionsIntegration() {
        let mainVC = SupportMainInterface()
        
        // Test quick action categories
        let quickActions = ["security", "family", "settings", "help"]
        
        for action in quickActions {
            // Simulate quick action tap
            let request = SupportRequest(
                message: "Быстрое действие: \(action)",
                category: action,
                priority: .medium,
                context: SupportContext(
                    userID: "quick_action_test",
                    deviceInfo: "iOS Quick Action Test",
                    appVersion: "1.0.0"
                )
            )
            
            let expectation = XCTestExpectation(description: "Quick action: \(action)")
            
            supportAPI.sendSupportRequest(request)
                .sink(
                    receiveCompletion: { completion in
                        if case .failure(let error) = completion {
                            XCTFail("Quick action \(action) failed: \(error)")
                        }
                        expectation.fulfill()
                    },
                    receiveValue: { response in
                        XCTAssertNotNil(response, "Quick action \(action) should get response")
                    }
                )
                .store(in: &cancellables)
            
            wait(for: [expectation], timeout: 10.0)
        }
    }
    
    // MARK: - Error Handling Tests
    func testNetworkErrorHandling() {
        let expectation = XCTestExpectation(description: "Network error handling")
        
        // Simulate network error by using invalid endpoint
        let invalidAPI = UnifiedSupportAPIManager(baseURL: "https://invalid-endpoint.com")
        
        let request = SupportRequest(
            message: "Test with invalid endpoint",
            category: "general",
            priority: .medium,
            context: SupportContext(
                userID: "error_test",
                deviceInfo: "iOS Error Test",
                appVersion: "1.0.0"
            )
        )
        
        invalidAPI.sendSupportRequest(request)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        // This should fail, which is expected
                        XCTAssertNotNil(error, "Should handle network error gracefully")
                        expectation.fulfill()
                    } else {
                        XCTFail("Should have failed with network error")
                    }
                },
                receiveValue: { _ in
                    XCTFail("Should not receive value with invalid endpoint")
                }
            )
            .store(in: &cancellables)
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testEmptyMessageHandling() {
        let expectation = XCTestExpectation(description: "Empty message handling")
        
        let request = SupportRequest(
            message: "",
            category: "general",
            priority: .medium,
            context: SupportContext(
                userID: "empty_test",
                deviceInfo: "iOS Empty Test",
                appVersion: "1.0.0"
            )
        )
        
        supportAPI.sendSupportRequest(request)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        // Should handle empty message gracefully
                        XCTAssertTrue(error.localizedDescription.contains("empty") || 
                                    error.localizedDescription.contains("invalid"), 
                                    "Should provide meaningful error for empty message")
                        expectation.fulfill()
                    } else {
                        XCTFail("Should have failed with empty message")
                    }
                },
                receiveValue: { _ in
                    XCTFail("Should not process empty message")
                }
            )
            .store(in: &cancellables)
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    // MARK: - Performance Tests
    func testAPIPerformance() {
        let expectation = XCTestExpectation(description: "API performance test")
        
        let startTime = CFAbsoluteTimeGetCurrent()
        
        let request = SupportRequest(
            message: "Performance test message",
            category: "general",
            priority: .medium,
            context: SupportContext(
                userID: "performance_test",
                deviceInfo: "iOS Performance Test",
                appVersion: "1.0.0"
            )
        )
        
        supportAPI.sendSupportRequest(request)
            .sink(
                receiveCompletion: { completion in
                    let timeElapsed = CFAbsoluteTimeGetCurrent() - startTime
                    
                    if case .failure(let error) = completion {
                        XCTFail("Performance test failed: \(error)")
                    } else {
                        // API should respond within 5 seconds
                        XCTAssertLessThan(timeElapsed, 5.0, "API response should be under 5 seconds")
                    }
                    expectation.fulfill()
                },
                receiveValue: { _ in
                    let timeElapsed = CFAbsoluteTimeGetCurrent() - startTime
                    XCTAssertLessThan(timeElapsed, 5.0, "API response should be under 5 seconds")
                }
            )
            .store(in: &cancellables)
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    // MARK: - UI Performance Tests
    func testChatInterfacePerformance() {
        measure {
            let chatVC = SupportChatInterface()
            _ = chatVC.view // Force view loading
            
            // Simulate adding multiple messages
            for i in 0..<100 {
                let message = SupportMessage(
                    id: "perf_\(i)",
                    text: "Performance test message \(i)",
                    isFromUser: i % 2 == 0,
                    timestamp: Date(),
                    category: "general"
                )
                // In real implementation, this would add to the chat
            }
        }
    }
    
    func testMainInterfacePerformance() {
        measure {
            let mainVC = SupportMainInterface()
            _ = mainVC.view // Force view loading
            
            // Simulate loading multiple tickets
            let tickets = (0..<50).map { i in
                SupportTicket(
                    id: "ticket_\(i)",
                    title: "Test Ticket \(i)",
                    status: .open,
                    category: "general",
                    createdAt: Date(),
                    lastMessage: "Test message \(i)"
                )
            }
            // In real implementation, this would populate the table view
        }
    }
}

// MARK: - Mock Support API for Testing
class MockSupportAPIManager: UnifiedSupportAPIManager {
    override func sendSupportRequest(_ request: SupportRequest) -> AnyPublisher<SupportResponse, Error> {
        return Future<SupportResponse, Error> { promise in
            DispatchQueue.global().asyncAfter(deadline: .now() + 0.5) {
                let response = SupportResponse(
                    message: "Mock response for: \(request.message)",
                    category: request.category,
                    priority: request.priority,
                    suggestions: ["Mock suggestion 1", "Mock suggestion 2"],
                    timestamp: Date()
                )
                promise(.success(response))
            }
        }
        .eraseToAnyPublisher()
    }
    
    override func getRecentTickets() -> AnyPublisher<[SupportTicket], Error> {
        return Future<[SupportTicket], Error> { promise in
            DispatchQueue.global().asyncAfter(deadline: .now() + 0.3) {
                let tickets = (0..<5).map { i in
                    SupportTicket(
                        id: "mock_ticket_\(i)",
                        title: "Mock Ticket \(i)",
                        status: .open,
                        category: "general",
                        createdAt: Date(),
                        lastMessage: "Mock last message \(i)"
                    )
                }
                promise(.success(tickets))
            }
        }
        .eraseToAnyPublisher()
    }
    
    override func getSupportStatus() -> AnyPublisher<SupportStatus, Error> {
        return Future<SupportStatus, Error> { promise in
            DispatchQueue.global().asyncAfter(deadline: .now() + 0.1) {
                promise(.success(.online))
            }
        }
        .eraseToAnyPublisher()
    }
}

