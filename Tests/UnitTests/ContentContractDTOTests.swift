import XCTest
@testable import ALADDIN

final class ContentContractDTOTests: XCTestCase {

    func testManifestFlatDTODecodes() throws {
        let json = Data(
            """
            {
              "manifest_version": 4,
              "generated_at": "2026-04-24T10:00:00Z",
              "min_supported_app_version": "1.0.0",
              "checksum_sha256": "abc123",
              "signature": "sig",
              "categories": [
                {
                  "id": "child_interface_category_games",
                  "titleKey": "child_interface_category_games",
                  "icon": "🎮",
                  "ageBand": "school_7_12"
                }
              ],
              "items": [
                {
                  "id": "child_interface_category_games.1",
                  "categoryId": "child_interface_category_games",
                  "type": "game",
                  "ageBand": "school_7_12",
                  "version": 1,
                  "metadata": {
                    "locale": "ru",
                    "title": "Математический квест",
                    "subtitle": "Контент-пакет",
                    "description": "Описание",
                    "tags": ["seed"],
                    "estimatedDurationSec": 300
                  },
                  "payloadURL": null,
                  "checksumSHA256": null,
                  "isOfflineAvailable": true
                }
              ]
            }
            """.utf8
        )

        let dto = try JSONDecoder().decode(ManifestContractDTO.self, from: json)
        let manifest = dto.toDomain()
        XCTAssertEqual(manifest.manifestVersion, 4)
        XCTAssertEqual(manifest.categories.count, 1)
        XCTAssertEqual(manifest.items.count, 1)
    }

    func testManifestEnvelopeDTODecodes() throws {
        let json = Data(
            """
            {
              "manifest": {
                "manifest_version": 2,
                "generated_at": "2026-04-24T10:00:00Z",
                "min_supported_app_version": "1.0.0",
                "checksum_sha256": "xyz",
                "signature": null,
                "categories": [],
                "items": []
              }
            }
            """.utf8
        )

        let dto = try JSONDecoder().decode(ManifestContractDTO.self, from: json)
        XCTAssertEqual(dto.manifestVersion, 2)
    }

    func testDeltaEnvelopeDTOWithSnakeCaseDecodes() throws {
        let json = Data(
            """
            {
              "delta": {
                "from_version": 1,
                "to_version": 2,
                "added": [],
                "updated": [],
                "removed_ids": ["a", "b"],
                "checksum_sha256": "delta-hash"
              }
            }
            """.utf8
        )

        let dto = try JSONDecoder().decode(DeltaContractDTO.self, from: json)
        let patch = dto.toDomain()
        XCTAssertEqual(patch.fromVersion, 1)
        XCTAssertEqual(patch.toVersion, 2)
        XCTAssertEqual(patch.removedIds.count, 2)
    }

    func testParentalReportItemDecodesSnakeCase() throws {
        let json = Data(
            """
            {
              "id": 12,
              "user_id": 1001,
              "type": "weekly",
              "content": {
                "sites_count": 5,
                "top_sites": [{"site": "example.org", "visits": 3, "hours": 0, "minutes": 20, "category": "search"}]
              },
              "created_at": "2026-05-01T12:00:00.000Z"
            }
            """.utf8
        )

        let item = try JSONDecoder().decode(ParentalReportItem.self, from: json)
        XCTAssertEqual(item.id, 12)
        XCTAssertEqual(item.userId, 1001)
        XCTAssertEqual(item.type, "weekly")
        let sites = item.content["sites_count"]?.value
        if let i = sites as? Int {
            XCTAssertEqual(i, 5)
        } else if let d = sites as? Double {
            XCTAssertEqual(Int(d), 5)
        } else {
            XCTFail("Unexpected sites_count type: \(String(describing: sites))")
        }
    }
}

