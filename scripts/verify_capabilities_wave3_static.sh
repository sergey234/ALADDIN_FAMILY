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

# L12: Always upgrade opt-in (default false on bootstrap)
if grep -q 'requestAlwaysUpgrade: Bool = false' Core/Family/GeofenceMonitoringBootstrap.swift \
  && grep -q 'geofence_always_button_allow' Screens/02_FamilyScreen.swift; then
  echo "OK: L12 progressive Always (opt-in)"
else
  echo "FAIL: L12 Always still auto-upgraded by default"
  FAIL=1
fi

# L6: resolve before save + use current spot
if grep -q 'resolveAndStore' Core/Services/GeofenceGeocodingService.swift \
  && grep -q 'addGeofenceWithResolvedCoords' Screens/02_FamilyScreen.swift \
  && grep -q 'geofences_use_current_location' Resources/Localization/ru.lproj/Localizable.strings \
  && grep -q 'geofences_use_current_location' Resources/Localization/en.lproj/Localizable.strings; then
  echo "OK: L6 place coords resolve + RU/EN strings"
else
  echo "FAIL: L6 place coords / loc incomplete"
  FAIL=1
fi

# L13: cloud sync helper + no UI hydrate from mock GET required
if test -f Core/Family/GeofencePlacesCloudSync.swift \
  && grep -q 'GeofencePlacesCloudSync' Screens/02_FamilyScreen.swift; then
  echo "OK: L13 places cloud sync (soft upsert)"
else
  echo "FAIL: L13 GeofencePlacesCloudSync missing"
  FAIL=1
fi

# L14: precise only for place setup helper
if grep -q 'getCurrentLocationForPlaceSetup' Core/Managers/LocationManager.swift; then
  echo "OK: L14 precise place-setup helper"
else
  echo "FAIL: L14 precise place-setup helper missing"
  FAIL=1
fi

# L7 SOS one-shot location
if grep -q 'captureSOSLocationPin' Core/Family/FamilyImOkService.swift \
  && grep -q 'need_help_location_named' Resources/Localization/ru.lproj/Localizable.strings; then
  echo "OK: L7 SOS one-shot location"
else
  echo "FAIL: L7 SOS location incomplete"
  FAIL=1
fi

# B1/B2 Shield Action target
if test -f ALADDINShieldAction/ShieldActionExtension.swift \
  && grep -q 'ai.aladdin.ShieldAction' ALADDIN.xcodeproj/project.pbxproj \
  && grep -q 'STACT0112F90000200C7D34B' ALADDIN.xcodeproj/project.pbxproj \
  && grep -q 'shield-action-service' ALADDINShieldAction/Info.plist \
  && grep -q 'secondaryButtonLabel' ALADDINShieldConfiguration/ShieldConfigurationExtension.swift; then
  echo "OK: Shield Action target + Ask Parent UI"
else
  echo "FAIL: Shield Action target incomplete"
  FAIL=1
fi

# H1: unused privacy claims must stay out of Info.plist
if grep -qE 'NSHomeKitUsageDescription|NSBluetoothAlwaysUsageDescription|NSAppleMusicUsageDescription|NSSiriUsageDescription|NSLocalNetworkUsageDescription|NSRemindersUsageDescription' Info.plist; then
  echo "FAIL: H1 unused privacy keys still in Info.plist"
  FAIL=1
else
  echo "OK: H1 unused privacy keys removed"
fi

# D4: Critical stays false until Apple Assigned; Comm/NE/FC may be true (owner GO 2026-10-17)
if grep -q 'allowsCriticalAlerts' Core/Config/AppConfig.swift \
  && grep -q 'allowsCommunicationNotifications' Core/Config/AppConfig.swift \
  && grep -q 'allowsSystemContentFilter' Core/Config/AppConfig.swift \
  && grep -q 'allowsCriticalAlerts' Core/Notifications/NotificationManager.swift; then
  if awk '/#if APP_STORE_BUILD/,/#else/' Core/Config/AppConfig.swift | grep -q 'allowsCriticalAlerts = false'; then
    echo "OK: D4 Critical gated false; Comm/NE/FC per owner GO"
  else
    echo "FAIL: D4 App Store path must keep allowsCriticalAlerts = false until Assigned"
    FAIL=1
  fi
else
  echo "FAIL: D4 AppStoreBuildPolicy / NotificationManager critical gate missing"
  FAIL=1
fi

# L16 copy: P1 + A3 + teen in both Localizable.strings
LOC_OK=1
for k in geofence_consent_title geofence_adult_share_title geofence_always_teen_body geofences_title; do
  if ! grep -q "\"$k\"" Resources/Localization/ru.lproj/Localizable.strings \
    || ! grep -q "\"$k\"" Resources/Localization/en.lproj/Localizable.strings; then
    echo "FAIL: L16/loc missing key $k in RU or EN strings"
    FAIL=1
    LOC_OK=0
  fi
done
if [[ "$LOC_OK" -eq 1 ]]; then
  echo "OK: L16 P1/A3/teen + geofences_title in RU+EN strings"
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "== FAIL =="
  exit 1
fi
echo "== ALL OK =="
exit 0
