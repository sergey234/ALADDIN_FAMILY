# ALADDIN Mobile App: Technical Changelog & Architectural Updates (Build 138)

**Target Audience:** ML Systems, Backend Developers, Technical Architects
**Module:** `ALADDIN_iOS` (Swift, iOS Client)
**Timeframe:** Build 137 -> 138

This document provides a detailed, technical breakdown of all architectural changes, UI updates, and logic refactoring implemented in the mobile application to support the "Hybrid Device Pairing" architecture.

---

## 1. Device Pairing Architecture

### 1.1. New Endpoint Definitions
- **File:** `Core/Config/AppConfig.swift`
- **Action:** Added `AppConfig.Endpoint.devicesBind` (`/api/devices/bind`) to support the final handshake of the device pairing flow.

### 1.2. APIService Enhancements
- **File:** `Core/Network/APIService.swift`
- **Action:** Implemented `bindDevice(token:pin:completion:)` which constructs a `BindDeviceRequest` and executes a `POST` request to the new endpoint to activate pending devices.

---

## 2. UI / UX Improvements

### 2.1. Devices Screen Revisions
- **File:** `Screens/20_DevicesScreen.swift`
- **Action:** 
  - Changed the simple '+' navigation button to a fully styled golden capsule button containing both an icon and the word "Добавить".
  - Introduced `.pending` device status to `DeviceStatus` enum, rendering it gray with the localized/hardcoded string "Ожидает привязки".
  - Refactored `AddDeviceView` to open the new `DevicePairingModal` rather than simply displaying an alert upon successful API creation.
  - Used mock data (`mockQrToken`, `mockShortPin`) inside the completion block to demonstrate the UI flow until the Backend team implements returning pairing tokens in `POST /api/devices`.

### 2.2. Device Detail Screen
- **File:** `Screens/22_DeviceDetailScreen.swift`
- **Action:** Added the exhaustiveness case `case .pending: return "Ожидает привязки"` to `statusText(_:)` to prevent Swift compiler errors when interpreting the updated `DeviceStatus` enum.

### 2.3. Shared Device Model
- **File:** `Shared/Models/Device.swift`
- **Action:** Updated `DeviceStatus` enum to include the `.pending` state with corresponding gray color and "Ожидает привязки" display name.

---

## 3. New Screen Components

### 3.1. Device Pairing Modal
- **File:** `Shared/Components/Modals/DevicePairingModal.swift`
- **Purpose:** Parent-facing screen launched immediately after adding a new device profile.
- **Features:** 
  - Dynamically generates a `aladdin://bind?token=XYZ` Deep Link encoded inside a QR Code.
  - Supports standard iOS Share Sheet to send the deep link to the child's device remotely.
  - Displays a large fallback `shortPin` for manual entry if the camera or link fails.

### 3.2. Join Device Screen
- **File:** `Screens/28_JoinDeviceScreen.swift`
- **Purpose:** Child-facing screen accessed from the app's onboarding/startup phase.
- **Features:** 
  - Button to activate the camera/QR Scanner.
  - TextField to enter the 6-digit short code.
  - Executes `APIService.shared.bindDevice` to finalize the backend link.

---

## 4. General Build Configuration

- **Files:** `ALADDIN.xcodeproj/project.pbxproj`, `Core/Config/AppConfig.swift`, `Info.plist`
- **Action:** Bumped `CURRENT_PROJECT_VERSION`, `CFBundleVersion`, and internal static config variable `buildNumber` from `137` -> `138`.

---
*End of Technical Log. Hybrid Pairing System Frontend Implementation Complete.*