#!/usr/bin/env bash
# ASC 10 screens — status bar 9:41 + export folders (1290x2796 + 1242x2688).
# DO NOT run Simulator / xcodebuild without owner phrase: GO на сборку / GO на сим.
# Usage (after app is on booted sim and GO granted):
#   ./scripts/asc_capture_10_screens_prepare.sh
set -euo pipefail

OUT="${HOME}/Downloads/ALADDIN_ASC_10_$(date +%Y-%m-%d)"
mkdir -p "${OUT}/raw" "${OUT}/1290x2796" "${OUT}/1242x2688"

echo "OUT=${OUT}"
echo "Screens (navigate manually, then press Enter for each):"
echo " 01 Onboarding family-in-pocket"
echo " 02 SimpleHome Aladdin start"
echo " 03 All sections menu"
echo " 04 Location family"
echo " 05 Driving"
echo " 06 Child overview"
echo " 07 Child more (sleep/reward)"
echo " 08 Antifake text"
echo " 09 Antifake voice/history"
echo " 10 Settings WITHOUT diagnostics row"

UDID="$(xcrun simctl list devices booted | awk -F '[()]' '/Booted/{print $2; exit}')"
if [[ -z "${UDID}" ]]; then
  echo "No booted Simulator. Boot one after GO, then re-run."
  exit 1
fi

xcrun simctl status_bar "${UDID}" override \
  --time "9:41" \
  --batteryState charged \
  --batteryLevel 100 \
  --cellularBars 4 \
  --wifiBars 3

echo "Status bar set to 9:41 on ${UDID}"

for i in $(seq -w 1 10); do
  read -r -p "Ready for screen ${i}? Enter to capture… " _
  RAW="${OUT}/raw/${i}.png"
  xcrun simctl io "${UDID}" screenshot "${RAW}"
  sips -z 2796 1290 "${RAW}" --out "${OUT}/1290x2796/${i}_1290x2796.png" >/dev/null
  sips -z 2688 1242 "${RAW}" --out "${OUT}/1242x2688/${i}_1242x2688.png" >/dev/null
  echo "Saved ${i}"
done

echo "Done. Upload 1290x2796 to ASC 6.7\"; optional 1242x2688 to 6.5\"."
echo "Do not edit Figma OB_00…07."
