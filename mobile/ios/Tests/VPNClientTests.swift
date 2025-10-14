//
//  VPNClientTests.swift
//  ALADDIN Security Tests
//
//  Created by AI Assistant on 2025-01-27.
//  Copyright © 2025 ALADDIN Security. All rights reserved.
//

import XCTest
@testable import ALADDIN_Security

class VPNClientTests: XCTestCase {
    
    var vpnClient: ALADDINVPNClient!
    var mockAPIClient: MockAPIClient!
    
    override func setUpWithError() throws {
        mockAPIClient = MockAPIClient()
        vpnClient = ALADDINVPNClient(apiClient: mockAPIClient)
    }
    
    override func tearDownWithError() throws {
        vpnClient = nil
        mockAPIClient = nil
    }
    
    // MARK: - Initialization Tests
    
    func testVPNClientInitialization() throws {
        XCTAssertNotNil(vpnClient)
        XCTAssertEqual(vpnClient.status, .disconnected)
        XCTAssertNil(vpnClient.currentConnection)
        XCTAssertFalse(vpnClient.isConnecting)
    }
    
    func testDefaultServersLoaded() throws {
        XCTAssertFalse(vpnClient.availableServers.isEmpty)
        XCTAssertEqual(vpnClient.availableServers.count, 6)
        
        let serverNames = vpnClient.availableServers.map { $0.name }
        XCTAssertTrue(serverNames.contains("Сингапур"))
        XCTAssertTrue(serverNames.contains("Германия"))
        XCTAssertTrue(serverNames.contains("Гонконг"))
        XCTAssertTrue(serverNames.contains("Япония"))
        XCTAssertTrue(serverNames.contains("США"))
        XCTAssertTrue(serverNames.contains("Канада"))
    }
    
    // MARK: - Server Selection Tests
    
    func testSelectBestServer() throws {
        let bestServer = vpnClient.selectBestServer()
        XCTAssertNotNil(bestServer)
        XCTAssertTrue(bestServer!.isAvailable)
        XCTAssertGreaterThan(bestServer!.performanceScore, 0)
    }
    
    func testSelectBestServerWithUnavailableServers() throws {
        // Make all servers unavailable
        vpnClient.availableServers = vpnClient.availableServers.map { server in
            VPNServer(
                id: server.id,
                name: server.name,
                country: server.country,
                flag: server.flag,
                ip: server.ip,
                port: server.port,
                protocol: server.protocol,
                isAvailable: false,
                performanceScore: server.performanceScore,
                ping: server.ping,
                load: server.load
            )
        }
        
        let bestServer = vpnClient.selectBestServer()
        XCTAssertNil(bestServer)
    }
    
    func testGetQuickConnectServers() throws {
        let quickServers = vpnClient.getQuickConnectServers()
        XCTAssertLessThanOrEqual(quickServers.count, 4)
        XCTAssertTrue(quickServers.allSatisfy { $0.isAvailable })
        
        // Check if servers are sorted by ping
        let pings = quickServers.map { $0.ping }
        XCTAssertEqual(pings, pings.sorted())
    }
    
    // MARK: - Connection Tests
    
    func testConnectToServer() async throws {
        let server = vpnClient.availableServers.first!
        
        let expectation = XCTestExpectation(description: "VPN connection")
        
        Task {
            let result = await vpnClient.connect(to: server)
            XCTAssertTrue(result)
            expectation.fulfill()
        }
        
        await fulfillment(of: [expectation], timeout: 5.0)
        
        XCTAssertEqual(vpnClient.status, .connected)
        XCTAssertNotNil(vpnClient.currentConnection)
        XCTAssertEqual(vpnClient.currentConnection?.server.id, server.id)
    }
    
    func testConnectWithoutServer() async throws {
        let expectation = XCTestExpectation(description: "VPN connection without server")
        
        Task {
            let result = await vpnClient.connect()
            XCTAssertTrue(result)
            expectation.fulfill()
        }
        
        await fulfillment(of: [expectation], timeout: 5.0)
        
        XCTAssertEqual(vpnClient.status, .connected)
        XCTAssertNotNil(vpnClient.currentConnection)
    }
    
    func testDisconnect() async throws {
        // First connect
        await vpnClient.connect()
        XCTAssertEqual(vpnClient.status, .connected)
        
        // Then disconnect
        let expectation = XCTestExpectation(description: "VPN disconnection")
        
        Task {
            let result = await vpnClient.disconnect()
            XCTAssertTrue(result)
            expectation.fulfill()
        }
        
        await fulfillment(of: [expectation], timeout: 5.0)
        
        XCTAssertEqual(vpnClient.status, .disconnected)
        XCTAssertNil(vpnClient.currentConnection)
    }
    
    func testConnectWhenAlreadyConnected() async throws {
        // Connect first time
        await vpnClient.connect()
        XCTAssertEqual(vpnClient.status, .connected)
        
        // Try to connect again
        let expectation = XCTestExpectation(description: "Second VPN connection")
        
        Task {
            let result = await vpnClient.connect()
            XCTAssertFalse(result) // Should fail
            expectation.fulfill()
        }
        
        await fulfillment(of: [expectation], timeout: 5.0)
    }
    
    // MARK: - Connection Info Tests
    
    func testGetConnectionSummaryWhenDisconnected() throws {
        let summary = vpnClient.getConnectionSummary()
        
        XCTAssertFalse(summary["isConnected"] as! Bool)
        XCTAssertEqual(summary["statusText"] as! String, "Отключен")
        XCTAssertTrue((summary["serverInfo"] as! [String: Any]).isEmpty)
        XCTAssertEqual(summary["connectionTime"] as! Double, 0.0)
    }
    
    func testGetConnectionSummaryWhenConnected() async throws {
        await vpnClient.connect()
        
        let summary = vpnClient.getConnectionSummary()
        
        XCTAssertTrue(summary["isConnected"] as! Bool)
        XCTAssertEqual(summary["statusText"] as! String, "Подключен")
        XCTAssertFalse((summary["serverInfo"] as! [String: Any]).isEmpty)
        XCTAssertGreaterThan(summary["connectionTime"] as! Double, 0.0)
    }
    
    func testUpdateTraffic() async throws {
        await vpnClient.connect()
        
        let initialBytesSent = vpnClient.currentConnection?.bytesSent ?? 0
        let initialBytesReceived = vpnClient.currentConnection?.bytesReceived ?? 0
        
        vpnClient.updateTraffic(bytesSent: 1000, bytesReceived: 2000)
        
        XCTAssertEqual(vpnClient.currentConnection?.bytesSent, initialBytesSent + 1000)
        XCTAssertEqual(vpnClient.currentConnection?.bytesReceived, initialBytesReceived + 2000)
    }
    
    // MARK: - Performance Tests
    
    func testConnectionPerformance() throws {
        measure {
            let expectation = XCTestExpectation(description: "Performance test")
            
            Task {
                await vpnClient.connect()
                expectation.fulfill()
            }
            
            wait(for: [expectation], timeout: 10.0)
        }
    }
    
    func testServerSelectionPerformance() throws {
        measure {
            for _ in 0..<1000 {
                _ = vpnClient.selectBestServer()
            }
        }
    }
    
    // MARK: - Error Handling Tests
    
    func testConnectionWithInvalidServer() async throws {
        let invalidServer = VPNServer(
            id: "invalid",
            name: "Invalid Server",
            country: "XX",
            flag: "🚫",
            ip: "0.0.0.0",
            port: 0,
            protocol: .wireguard,
            isAvailable: false,
            performanceScore: 0.0,
            ping: 999,
            load: 100
        )
        
        let expectation = XCTestExpectation(description: "Invalid server connection")
        
        Task {
            let result = await vpnClient.connect(to: invalidServer)
            XCTAssertFalse(result)
            expectation.fulfill()
        }
        
        await fulfillment(of: [expectation], timeout: 5.0)
    }
    
    // MARK: - Memory Tests
    
    func testMemoryUsage() throws {
        let initialMemory = getMemoryUsage()
        
        // Create multiple VPN clients
        var clients: [ALADDINVPNClient] = []
        for _ in 0..<100 {
            let client = ALADDINVPNClient(apiClient: mockAPIClient)
            clients.append(client)
        }
        
        let finalMemory = getMemoryUsage()
        let memoryIncrease = finalMemory - initialMemory
        
        // Memory increase should be reasonable (less than 10MB)
        XCTAssertLessThan(memoryIncrease, 10 * 1024 * 1024)
    }
    
    // MARK: - Helper Methods
    
    private func getMemoryUsage() -> UInt64 {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4
        
        let kerr: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_,
                         task_flavor_t(MACH_TASK_BASIC_INFO),
                         $0,
                         &count)
            }
        }
        
        if kerr == KERN_SUCCESS {
            return info.resident_size
        } else {
            return 0
        }
    }
}

// MARK: - Mock API Client
class MockAPIClient: ALADDINAPIClient {
    func getVPNServers() async throws -> [VPNServer] {
        // Return empty array to use default servers
        return []
    }
}

