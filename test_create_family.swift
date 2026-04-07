import Foundation

struct FamilyMemberResponse: Codable {}

struct CreateFamilyResponse: Codable {
    let family_id: String
    let short_code: String
    let creator_member_id: String
    let qr_code_data: String
    let expires_at: String
    let success: Bool?
    let members: [FamilyMemberResponse]?
    let access_token: String?
    let refresh_token: String?
    
    enum CodingKeys: String, CodingKey {
        case family_id
        case short_code
        case creator_member_id
        case qr_code_data
        case expires_at
        case success
        case members
        case access_token
        case refresh_token
    }
}

let jsonStr = """
{"family_id":"FAM_1BBEE4BCA3D4","qr_code_data":"{\\"family_id\\": \\"FAM_1BBEE4BCA3D4\\", \\"timestamp\\": 1775551531, \\"type\\": \\"family_registration\\"}","short_code":"77II","creator_member_id":"MEM_09C18F12","expires_at":"2026-04-08T11:45:31.724551"}
"""

let data = jsonStr.data(using: .utf8)!
do {
    let decoded = try JSONDecoder().decode(CreateFamilyResponse.self, from: data)
    print("Success: \\(decoded.family_id)")
} catch {
    print("Error: \\(error)")
}
