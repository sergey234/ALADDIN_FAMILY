import NetworkExtension

/// WAVE3 F2 — NE Content Filter data provider (parental hosts). Not a VPN / Packet Tunnel.
final class ContentFilterDataProvider: NEFilterDataProvider {

    private var blockedHosts: Set<String> = []

    override func startFilter(completionHandler: @escaping (Error?) -> Void) {
        reloadRules()
        completionHandler(nil)
    }

    override func stopFilter(
        with reason: NEProviderStopReason,
        completionHandler: @escaping () -> Void
    ) {
        completionHandler()
    }

    override func handleNewFlow(_ flow: NEFilterFlow) -> NEFilterNewFlowVerdict {
        reloadRules()
        guard let host = host(from: flow)?.lowercased(), !host.isEmpty else {
            return .allow()
        }
        for blocked in blockedHosts {
            if blocked.isEmpty { continue }
            if host == blocked || host.hasSuffix(".\(blocked)") {
                return .drop()
            }
            // Category seeds from Safari CB (e.g. "facebook", "tiktok") — substring match.
            if !blocked.contains(".") && host.contains(blocked) {
                return .drop()
            }
        }
        return .allow()
    }

    private func reloadRules() {
        guard let url = FileManager.default
            .containerURL(forSecurityApplicationGroupIdentifier: "group.ai.aladdin")?
            .appendingPathComponent("content_filter_rules.json"),
              let data = try? Data(contentsOf: url),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let hosts = json["blockedHosts"] as? [String] else {
            blockedHosts = []
            return
        }
        blockedHosts = Set(hosts.map { $0.lowercased() })
    }

    private func host(from flow: NEFilterFlow) -> String? {
        if let browser = flow as? NEFilterBrowserFlow, let url = browser.url {
            return url.host
        }
        if let socket = flow as? NEFilterSocketFlow {
            return socket.remoteHostname
        }
        return flow.url?.host
    }
}
