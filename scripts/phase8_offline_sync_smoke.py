#!/usr/bin/env python3
"""
Phase 8.1 smoke checks for offline mode and sync flow.

This is a deterministic source-contract smoke that validates:
1) Offline queue + retry primitives exist.
2) Content sync manager handles online/offline and delta/full fallback.
3) Family roster sync path triggers profile reconcile.
"""

from __future__ import annotations

import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def must_contain(text: str, needle: str, context: str) -> None:
    require(needle in text, f"{context}: missing `{needle}`")


def must_match(text: str, pattern: str, context: str) -> None:
    require(re.search(pattern, text, flags=re.MULTILINE) is not None, f"{context}: missing pattern `{pattern}`")


def check_offline_manager() -> None:
    body = read("Core/Offline/OfflineManager.swift")
    must_contain(body, "@Published var isOnline: Bool", "OfflineManager online status")
    must_contain(body, "pendingOperationsCount", "OfflineManager queue metric")
    must_contain(body, "func execute<T>(", "OfflineManager execution gateway")
    must_contain(body, "addToPendingQueue(", "OfflineManager queue append")
    must_contain(body, "processPendingOperations()", "OfflineManager queue processing")
    must_match(body, r"if !wasOnline && self\?\.isOnline == true", "OfflineManager reconnect trigger")
    print("OK OfflineManager queue/retry/reconnect contract")


def check_content_sync_manager() -> None:
    body = read("Core/Content/Sync/ContentSyncManager.swift")
    must_contain(body, "guard OfflineManager.shared.isOnline else", "ContentSyncManager offline guard")
    must_contain(body, "fetchManifest()", "ContentSyncManager manifest fetch")
    must_contain(body, "fetchDelta(from: localVersion)", "ContentSyncManager delta fetch")
    must_contain(body, "applyDelta", "ContentSyncManager merge logic")
    must_match(body, r"catch \{\n\s*let manifest = try await apiClient\.fetchManifest\(\)", "ContentSyncManager full fallback")
    print("OK ContentSyncManager delta/full fallback contract")


def check_family_sync_path() -> None:
    body = read("ViewModels/FamilyViewModel.swift")
    must_contain(body, "apiService.getFamilyMembers", "FamilyViewModel family sync fetch")
    must_contain(body, "ProfileManager.shared.syncChildRosterFromServer(", "FamilyViewModel roster reconcile bridge")
    must_contain(body, "lastChildRosterReconcileSummary", "FamilyViewModel reconcile diagnostics")
    print("OK FamilyViewModel family->profile sync bridge")


def main() -> int:
    print("PHASE 8.1 OFFLINE+SYNC SMOKE")
    check_offline_manager()
    check_content_sync_manager()
    check_family_sync_path()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError) as exc:
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
