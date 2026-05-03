import XCTest
@testable import ALADDIN

final class APIServiceTests: XCTestCase {

    private var mockNetwork: MockNetworkManager!
    private var service: APIService!

    override func setUpWithError() throws {
        mockNetwork = MockNetworkManager()
        service = APIService(networkManager: mockNetwork)
    }

    override func tearDownWithError() throws {
        service = nil
        mockNetwork = nil
    }

    func testInitializationUsesInjectedNetworkManager() {
        XCTAssertTrue(service.networkManager === mockNetwork)
    }

    func testGetNetworkProtectionStatusUsesStubbedResponse() {
        let expected = NetworkProtectionStatusResponse(
            isConnected: true,
            serverLocation: "Germany",
            ipAddress: "192.168.0.1",
            ping: 15,
            downloadSpeed: "120 Mbps",
            uploadSpeed: "45 Mbps",
            sessionTime: "00:10:00",
            threatsBlocked: 12
        )
        mockNetwork.stubGET(endpoint: AppConfig.Endpoint.networkProtectionStatus, response: expected)
        let expectation = expectation(description: "network protection status")

        service.getNetworkProtectionStatus { (result: Result<NetworkProtectionStatusResponse, Error>) in
            switch result {
            case .success(let response):
                XCTAssertEqual(response.ipAddress, expected.ipAddress)
                XCTAssertEqual(response.threatsBlocked, expected.threatsBlocked)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }

        wait(for: [expectation], timeout: 2.0)
        XCTAssertEqual(mockNetwork.lastGETEndpoint, AppConfig.Endpoint.networkProtectionStatus)
    }

    func testConnectNetworkProtectionUsesStubbedResponse() {
        let expected = APIResponse(success: true, data: true, message: "connected", error: nil)
        mockNetwork.stubPOST(endpoint: AppConfig.Endpoint.networkProtectionConnect, response: expected)
        let expectation = expectation(description: "network protection connect")

        service.connectNetworkProtection { (result: Result<APIResponse<Bool>, Error>) in
            switch result {
            case .success(let response):
                XCTAssertTrue(response.success)
                XCTAssertEqual(response.message, expected.message)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }

        wait(for: [expectation], timeout: 2.0)
        XCTAssertEqual(mockNetwork.lastPOSTEndpoint, AppConfig.Endpoint.networkProtectionConnect)
    }

    func testRegisterDeviceTokenUsesCorrectEndpoint() {
        let expected = APIResponse(success: true, data: true, message: "ok", error: nil)
        mockNetwork.stubPOST(endpoint: AppConfig.Endpoint.deviceRegister, response: expected)
        let expectation = expectation(description: "device token registered")

        service.registerDeviceToken("test-token-123") { (result: Result<APIResponse<Bool>, Error>) in
            switch result {
            case .success(let response):
                XCTAssertTrue(response.success)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }

        wait(for: [expectation], timeout: 2.0)
        XCTAssertEqual(mockNetwork.lastPOSTEndpoint, AppConfig.Endpoint.deviceRegister)
        XCTAssertNotNil(mockNetwork.lastPOSTBodyData)
    }

    func testNetworkErrorPropagatesFromNetworkManager() {
        mockNetwork.shouldReturnError = true
        mockNetwork.errorToReturn = NetworkError.unknown(nil)
        let expectation = expectation(description: "Network error propagated")

        service.getNetworkProtectionStatus { (result: Result<NetworkProtectionStatusResponse, Error>) in
            switch result {
            case .success:
                XCTFail("Expected failure, got success")
            case .failure:
                expectation.fulfill()
            }
        }

        wait(for: [expectation], timeout: 2.0)
    }
}

// MARK: - Mock Network Manager

final class MockNetworkManager: NetworkManager {

    var shouldReturnError = false
    var errorToReturn: Error = NetworkError.unknown(nil)
    var lastGETEndpoint: String?
    var lastPOSTEndpoint: String?
    var lastPOSTBodyData: Data?

    private var getStubs: [String: Any] = [:]
    private var postStubs: [String: Any] = [:]

    func stubGET<T: Decodable>(endpoint: String, response: T) {
        getStubs[endpoint] = response
    }

    func stubPOST<T: Decodable>(endpoint: String, response: T) {
        postStubs[endpoint] = response
    }

    override func get<T: Decodable>(
        endpoint: String,
        queryParams: [String: String]? = nil,
        requiresAuth: Bool = true,
        additionalHeaders: [String: String]? = nil,
        onHeaders: (([AnyHashable: Any]) -> Void)? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        lastGETEndpoint = endpoint
        if shouldReturnError {
            completion(.failure(errorToReturn))
            return
        }
        guard let response = getStubs[endpoint] as? T else {
            completion(.failure(NetworkError.unknown(nil)))
            return
        }
        completion(.success(response))
    }

    override func post<T: Decodable, B: Encodable>(
        endpoint: String,
        body: B,
        requiresAuth: Bool = true,
        extraHeaders: [String: String]? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        lastPOSTEndpoint = endpoint
        if shouldReturnError {
            completion(.failure(errorToReturn))
            return
        }
        lastPOSTBodyData = try? JSONEncoder().encode(body)
        guard let response = postStubs[endpoint] as? T else {
            completion(.failure(NetworkError.unknown(nil)))
            return
        }
        completion(.success(response))
    }
}
