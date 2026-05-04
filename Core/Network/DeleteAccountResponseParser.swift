import Foundation

/// Parses `DELETE /api/user/delete` responses: canonical `APIResponse<Bool>`, empty body, or gateway envelopes.
enum DeleteAccountResponseParser {
    static func parse(path: String, data: Data?, statusCode: Int) -> APIResponse<Bool>? {
        guard isUserDeleteAccountPath(path) else { return nil }
        guard (200...299).contains(statusCode) else { return nil }

        if let data = data, !data.isEmpty {
            if let std = try? JSONDecoder().decode(APIResponse<Bool>.self, from: data) {
                return std
            }
            struct DeleteAccountGatewayEnvelope: Decodable {
                let function: String?
                let result: String?
                let source: String?
                let version: String?
                let timestamp: String?
            }
            guard let env = try? JSONDecoder().decode(DeleteAccountGatewayEnvelope.self, from: data) else {
                return nil
            }
            let ver = (env.version ?? "").lowercased()
            let src = (env.source ?? "").lowercased()
            if ver.contains("mock-real-protection") || ver.contains("sfm_mock") || src == "sfm_mock" || src == "mock" {
                return APIResponse(success: false, data: false, message: nil, error: "gateway_envelope")
            }
            if let r = env.result?.trimmingCharacters(in: .whitespacesAndNewlines), !r.isEmpty,
               let innerData = r.data(using: .utf8),
               let inner = try? JSONDecoder().decode(APIResponse<Bool>.self, from: innerData) {
                return inner
            }
            if env.function == "delete_user_delete" {
                return APIResponse(success: true, data: true, message: env.timestamp, error: nil)
            }
            return nil
        }

        return APIResponse(success: true, data: true, message: nil, error: nil)
    }

    private static func isUserDeleteAccountPath(_ path: String) -> Bool {
        path.contains("/api/user/delete") || path.contains("/user/delete")
    }
}
