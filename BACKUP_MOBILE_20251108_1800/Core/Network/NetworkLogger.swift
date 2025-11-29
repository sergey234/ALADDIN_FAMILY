import Foundation

enum NetworkLogger {
    static func logRequest(_ request: URLRequest) {
        #if DEBUG
        var headers = request.allHTTPHeaderFields ?? [:]
        if headers["Authorization"] != nil { headers["Authorization"] = "<redacted>" }
        print("➡️ Request: \(request.httpMethod ?? "GET") \(request.url?.absoluteString ?? "-") headers=\(headers)")
        #endif
    }

    static func logResponse(_ response: URLResponse?, data: Data?) {
        #if DEBUG
        if let http = response as? HTTPURLResponse {
            print("⬅️ Response: status=\(http.statusCode) url=\(http.url?.absoluteString ?? "-")")
        }
        #endif
    }
}









