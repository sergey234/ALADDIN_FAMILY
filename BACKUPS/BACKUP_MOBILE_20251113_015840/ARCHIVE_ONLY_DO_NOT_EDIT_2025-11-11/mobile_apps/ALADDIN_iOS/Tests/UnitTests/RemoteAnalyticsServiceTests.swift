import XCTest
@testable import ALADDIN

final class RemoteAnalyticsServiceTests: XCTestCase {
    private var service: RemoteAnalyticsService!
    private var session: URLSession!
    
    override func setUpWithError() throws {
        try super.setUpWithError()
        let configuration = URLSessionConfiguration.ephemeral
        configuration.protocolClasses = [MockURLProtocol.self]
        session = URLSession(configuration: configuration)
        service = RemoteAnalyticsService(
            baseURL: URL(string: "https://qa.aladdin.family/api")!,
            authTokenProvider: { "test-token" },
            urlSession: session
        )
    }
    
    override func tearDownWithError() throws {
        service = nil
        session = nil
        MockURLProtocol.requestHandler = nil
        try super.tearDownWithError()
    }
    
    func testFetchSummaryDecodesUnifiedDashboard() async throws {
        let expectedURL = URL(string: "https://qa.aladdin.family/api/security/unified-dashboard")!
        var capturedRequest: URLRequest?
        let responseJSON = """
        {
            "totalThreatsBlocked": 18,
            "vpnThreats": 12,
            "avThreats": 6,
            "securityScore": 86.5
        }
        """.data(using: .utf8)!
        
        MockURLProtocol.requestHandler = { request in
            capturedRequest = request
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 200,
                httpVersion: nil,
                headerFields: ["Content-Type": "application/json"]
            )!
            return (response, responseJSON)
        }
        
        let filters = AnalyticsFilters(onlyBlocked: true, includeFamily: true, includeDevices: false)
        let summary = try await service.fetchSummary(period: "day", filters: filters)
        
        XCTAssertEqual(summary.threatsDetected, 18)
        XCTAssertEqual(summary.threatsBlocked, 12)
        XCTAssertEqual(summary.itemsScanned, 6)
        XCTAssertEqual(summary.protectionLevel, 86.5)
        XCTAssertEqual(capturedRequest?.url, expectedURL)
        XCTAssertEqual(capturedRequest?.value(forHTTPHeaderField: "Authorization"), "Bearer test-token")
        XCTAssertEqual(capturedRequest?.value(forHTTPHeaderField: "Accept"), "application/json")
    }
    
    func testFetchSecurityAnalyticsNormalizesCategories() async throws {
        let responseJSON = """
        {
            "vpnThreatsBlocked": 3,
            "avThreatsDetected": 2,
            "totalThreats": 5,
            "vpnStats": {
                "threatsByCategory": {
                    "vpn_blocked": 3
                }
            },
            "avStats": {
                "threatsByCategory": {
                    "malware_detected": 2
                }
            },
            "securityLevel": "high",
            "recommendations": ["Enable continuous VPN"]
        }
        """.data(using: .utf8)!
        
        MockURLProtocol.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 200,
                httpVersion: nil,
                headerFields: ["Content-Type": "application/json"]
            )!
            return (response, responseJSON)
        }
        
        let analytics = try await service.fetchSecurityAnalytics(period: "week")
        XCTAssertEqual(analytics.blockedThreats.count, 2)
        let categories = Dictionary(uniqueKeysWithValues: analytics.blockedThreats.map { ($0.type, $0.count) })
        XCTAssertEqual(categories["network"], 3)
        XCTAssertEqual(categories["file"], 2)
    }
    
    func testFetchSummaryFallsBackOnServerError() async throws {
        MockURLProtocol.requestHandler = { request in
            let response = HTTPURLResponse(url: request.url!, statusCode: 500, httpVersion: nil, headerFields: nil)!
            return (response, Data())
        }
        
        let filters = AnalyticsFilters(onlyBlocked: false, includeFamily: true, includeDevices: true)
        let summary = try await service.fetchSummary(period: "month", filters: filters)
        
        XCTAssertGreaterThanOrEqual(summary.threatsDetected, 0)
        XCTAssertGreaterThanOrEqual(summary.threatsBlocked, 0)
    }
}

private final class MockURLProtocol: URLProtocol {
    typealias Handler = (URLRequest) throws -> (HTTPURLResponse, Data)
    static var requestHandler: Handler?
    
    override class func canInit(with request: URLRequest) -> Bool {
        true
    }
    
    override class func canonicalRequest(for request: URLRequest) -> URLRequest {
        request
    }
    
    override func startLoading() {
        guard let handler = MockURLProtocol.requestHandler else {
            client?.urlProtocol(self, didFailWithError: URLError(.badServerResponse))
            return
        }
        
        do {
            let (response, data) = try handler(request)
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch {
            client?.urlProtocol(self, didFailWithError: error)
        }
    }
    
    override func stopLoading() {}
}

