import NetworkExtension

final class PacketTunnelProvider: NEPacketTunnelProvider {
    private let vpnServerAddress = "vpn.aladdin-ai.ru"

    override func startTunnel(options: [String : NSObject]?, completionHandler: @escaping (Error?) -> Void) {
        let tunnelSettings = NEPacketTunnelNetworkSettings(tunnelRemoteAddress: vpnServerAddress)
        tunnelSettings.ipv4Settings = NEIPv4Settings(addresses: ["10.0.0.2"], subnetMasks: ["255.255.255.0"])
        tunnelSettings.ipv4Settings?.includedRoutes = [NEIPv4Route.default()]
        tunnelSettings.mtu = 1400 as NSNumber

        setTunnelNetworkSettings(tunnelSettings) { error in
            if let error = error {
                NSLog("[PacketTunnelProvider] Failed to set tunnel settings: \(error.localizedDescription)")
                completionHandler(error)
                return
            }

            self.startHandlingPackets()
            completionHandler(nil)
        }
    }

    override func stopTunnel(with reason: NEProviderStopReason, completionHandler: @escaping () -> Void) {
        completionHandler()
    }

    private func startHandlingPackets() {
        packetFlow.readPackets { [weak self] packets, protocols in
            guard let self = self else { return }
            // TODO: integrate real VPN transport (e.g., WireGuard/IPSec) with backend tunnel
            if !packets.isEmpty {
                NSLog("[PacketTunnelProvider] Received \(packets.count) packets for processing")
            }

            self.startHandlingPackets()
        }
    }
}
