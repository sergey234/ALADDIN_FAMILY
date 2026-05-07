# Safari Content Blocker: Final Xcode Checklist

This checklist is for restoring and validating Safari Content Blocker in production/TestFlight.

## 1) Target and Embedding

- [ ] Main app target includes `Embed App Extensions` build phase.
- [ ] `ALADDINContentBlocker.appex` is present in `Embed App Extensions`.
- [ ] Embed destination is `PlugIns` (`dstSubfolderSpec = 13`).
- [ ] Extension target product type is `com.apple.product-type.app-extension`.

## 2) Extension Info.plist

- [ ] `NSExtensionPointIdentifier = com.apple.Safari.content-blocker`.
- [ ] `NSExtensionPrincipalClass = $(PRODUCT_MODULE_NAME).ActionRequestHandler`.
- [ ] `PRODUCT_BUNDLE_IDENTIFIER` is exactly `family.aladdin.ios.ALADDINContentBlocker`.
- [ ] Main app bundle id is `family.aladdin.ios` (same Team, same distribution setup).

## 3) Signing and Provisioning (Release/TestFlight critical)

- [ ] Main app and extension are signed under the same Apple Team (`6CJVBBUGSN`).
- [ ] Main app distribution profile includes app bundle id.
- [ ] Extension distribution profile includes extension bundle id (`family.aladdin.ios.ALADDINContentBlocker`).
- [ ] No stale/manual profile UUID mismatch in Xcode Release config.
- [ ] If CI uses manual signing, app and extension profiles are both installed and renamed to UUID-based filenames.

## 4) Capabilities and Entitlements

- [ ] Confirm if App Group is required for blocker rules sharing (`group.com.aladdin.family`).
- [ ] If App Group is used, add `.entitlements` to both app and extension.
- [ ] Add `com.apple.security.application-groups` with `group.com.aladdin.family` to both targets.
- [ ] Set `CODE_SIGN_ENTITLEMENTS` for both targets in Debug and Release.

## 5) Build/Archive Validation

- [ ] `xcodebuild archive` succeeds for Release.
- [ ] Archive contains `ALADDINContentBlocker.appex` under `Products/Applications/ALADDIN.app/PlugIns/`.
- [ ] Exported IPA contains `PlugIns/ALADDINContentBlocker.appex`.
- [ ] CI logs include both profiles and no extension signing errors.

## 6) Runtime Validation on Device/TestFlight

- [ ] Install TestFlight build on real device.
- [ ] Open app and enable Safari filter categories.
- [ ] Go to iOS Settings -> Safari -> Extensions/Content Blockers and verify `ALADDIN` entry exists.
- [ ] Enable blocker and return to app.
- [ ] App status updates to `enabled` (not `disabled`/`missing`).
- [ ] Disable blocker in iOS Settings and verify app shows `needs activation`.
- [ ] If extension missing in build, app shows explicit `extension missing` state.

## 7) Failure Matrix (what to fix)

- Missing entry in iOS Safari settings:
  - usually extension not embedded or wrong bundle id/signing profile.
- Entry exists but cannot enable:
  - usually profile/certificate mismatch or extension signing invalid.
- App always shows disabled:
  - extension works, but user did not enable in iOS Safari settings.
- App shows extension missing:
  - extension target absent from archive/TestFlight or not installed.

## 8) Go/No-Go for Production

- [ ] All checks above green on at least one Release archive and one TestFlight build.
- [ ] QA sign-off with screenshots:
  - extension visible in iOS settings,
  - blocker enabled,
  - app state updated correctly after returning from Settings.

