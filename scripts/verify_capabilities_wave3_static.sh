#!/usr/bin/env bash
# WAVE3 L10 / cap-I1 — static gates (no xcodebuild).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

echo "== WAVE3 static verify =="

# L10: never ship continuous background location mode in this wave
if /usr/libexec/PlistBuddy -c 'Print :UIBackgroundModes' Info.plist 2>/dev/null | grep -q 'location'; then
  echo "FAIL: UIBackgroundModes contains 'location' (Packet-Tunnel-style continuous GPS — OUT of WAVE3)"
  FAIL=1
else
  echo "OK: no UIBackgroundModes location"
fi

# L5: purpose strings mention place alerts / SOS (not empty generic only)
WHEN=$(/usr/libexec/PlistBuddy -c 'Print :NSLocationWhenInUseUsageDescription' Info.plist 2>/dev/null || true)
ALWAYS=$(/usr/libexec/PlistBuddy -c 'Print :NSLocationAlwaysAndWhenInUseUsageDescription' Info.plist 2>/dev/null || true)
if echo "$WHEN" | grep -qiE 'SOS|place|emergency|места|экстрен'; then
  echo "OK: WhenInUse purpose specific"
else
  echo "FAIL: NSLocationWhenInUseUsageDescription too generic"
  FAIL=1
fi
if echo "$ALWAYS" | grep -qiE 'Always|enter|exit|place|геозон|мест|непрерывн|continuous'; then
  echo "OK: Always purpose specific"
else
  echo "FAIL: NSLocationAlwaysAndWhenInUseUsageDescription too generic"
  FAIL=1
fi

# L3: important types cover place departure
if grep -q 'geofence_place_departure' Core/Notifications/NotificationManager.swift \
  && grep -q 'geofence_' Core/Notifications/NotificationManager.swift; then
  echo "OK: L3 important geofence types present"
else
  echo "FAIL: L3 geofence important types missing"
  FAIL=1
fi

# L1: bootstrap Always gate
if grep -q 'Always required' Core/Family/GeofenceMonitoringBootstrap.swift \
  || grep -q 'forBackground: true' Core/Family/GeofenceMonitoringBootstrap.swift; then
  echo "OK: L1 Always gate in bootstrap"
else
  echo "FAIL: L1 Always gate missing"
  FAIL=1
fi

# L2: requestState
if grep -q 'requestState(for:' Core/Managers/LocationManager.swift; then
  echo "OK: L2 requestState present"
else
  echo "FAIL: L2 requestState missing"
  FAIL=1
fi

# L4 client + server artifacts (deploy separate)
if grep -q 'familyGeofenceEvent' Core/Config/AppConfig.swift \
  && test -f app/services/geofence_family_notify.py \
  && grep -q 'geofence-event' app/routers/family.py; then
  echo "OK: L4 client+server code present (deploy needs GO)"
else
  echo "FAIL: L4 geofence-event path incomplete"
  FAIL=1
fi

# No Packet Tunnel in active entitlements (main)
if grep -q 'packet-tunnel\|PacketTunnel' ALADDIN.entitlements 2>/dev/null; then
  echo "FAIL: Packet Tunnel entitlement in ALADDIN.entitlements"
  FAIL=1
else
  echo "OK: no Packet Tunnel in main entitlements"
fi

# ST Report must be ExtensionKit (ASC 409 if NSExtension in PlugIns)
if grep -q 'EXAppExtensionAttributes' ALADDINDeviceActivityReport/Info.plist \
  && ! grep -q '<key>NSExtension</key>' ALADDINDeviceActivityReport/Info.plist \
  && grep -q 'com.apple.product-type.extensionkit-extension' ALADDIN.xcodeproj/project.pbxproj \
  && grep -q 'Embed ExtensionKit Extensions' ALADDIN.xcodeproj/project.pbxproj \
  && grep -q 'dstSubfolderSpec = 16' ALADDIN.xcodeproj/project.pbxproj; then
  echo "OK: DeviceActivityReport ExtensionKit layout"
else
  echo "FAIL: DeviceActivityReport still NSExtension/PlugIns (ASC upload will 409)"
  FAIL=1
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "== FAIL =="
  exit 1
fi
echo "== ALL OK =="
exit 0
