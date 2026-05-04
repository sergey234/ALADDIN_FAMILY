import XCTest
@testable import ALADDIN

final class DeleteAccountResponseParserTests: XCTestCase {

    func test_canonicalAPIResponse_decodes() throws {
        let json = #"{"success":true,"data":true,"message":"ok","error":null}"#
        let data = try XCTUnwrap(json.data(using: .utf8))
        let r = DeleteAccountResponseParser.parse(path: "/api/user/delete", data: data, statusCode: 200)
        XCTAssertEqual(r?.success, true)
        XCTAssertEqual(r?.data, true)
    }

    func test_emptyBody_200_isSuccess() {
        let r = DeleteAccountResponseParser.parse(path: "/api/user/delete", data: nil, statusCode: 200)
        XCTAssertEqual(r?.success, true)
        XCTAssertEqual(r?.data, true)
    }

    func test_mockRealProtection_isGatewayEnvelope() throws {
        let json = #"{"function":"delete_user_delete","result":"","version":"3.0.0-mock-real-protection"}"#
        let data = try XCTUnwrap(json.data(using: .utf8))
        let r = DeleteAccountResponseParser.parse(path: "/api/user/delete", data: data, statusCode: 200)
        XCTAssertEqual(r?.success, false)
        XCTAssertEqual(r?.error, "gateway_envelope")
    }

    func test_deleteUserDeleteFunctionWithoutMock_isSuccess() throws {
        let json = #"{"function":"delete_user_delete","result":"","version":"3.0.0"}"#
        let data = try XCTUnwrap(json.data(using: .utf8))
        let r = DeleteAccountResponseParser.parse(path: "/api/user/delete", data: data, statusCode: 200)
        XCTAssertEqual(r?.success, true)
        XCTAssertEqual(r?.data, true)
    }

    func test_nonDeletePath_returnsNil() throws {
        let json = #"{"success":true,"data":true}"#
        let data = try XCTUnwrap(json.data(using: .utf8))
        let r = DeleteAccountResponseParser.parse(path: "/api/other", data: data, statusCode: 200)
        XCTAssertNil(r)
    }
}
