import XCTest
@testable import ALADDIN

final class CompanionCapabilitiesPayloadTests: XCTestCase {

    func testDecodesCompanionCharactersArrayInUI() throws {
        let json = """
        {
          "app_id":"aladdin_family",
          "age_band":"parent",
          "content_policy":"family_pg13",
          "features":{
            "chat":{"enabled":true,"ui":{"text_input":true,"streaming":true},"limits":{}},
            "voice_realtime":{"enabled":true,"ui":{"mic_button":true,"realtime_websocket":true,"ephemeral_token_required":true},"limits":{}},
            "companion":{"enabled":true,"ui":{"hub_visible":true,"characters":["unicorn","aladdin","genie"],"trust_bar":true},"limits":{}}
          }
        }
        """

        let data = try XCTUnwrap(json.data(using: .utf8))
        let payload = try JSONDecoder().decode(CompanionCapabilitiesPayload.self, from: data)

        let companion = try XCTUnwrap(payload.features?["companion"])
        XCTAssertEqual(companion.enabled, true)
        XCTAssertEqual(companion.ui?.flag("hub_visible"), true)
        XCTAssertEqual(companion.ui?.flag("trust_bar"), true)
        XCTAssertEqual(companion.ui?.characters ?? [], ["unicorn", "aladdin", "genie"])
    }
}
