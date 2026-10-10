#!/usr/bin/env bash
# fhc-11 / G7 — static gate for Family Habit Custom Hybrid (Variant 2).
# No xcodebuild. Exit 0 = G7 PASS.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

check_grep() {
  local file="$1" pattern="$2" label="$3"
  if grep -qE "$pattern" "$file" 2>/dev/null; then
    echo "OK  $label"
  else
    echo "FAIL $label ($file ~ /$pattern/)"
    fail=1
  fi
}

check_not_grep() {
  local file="$1" pattern="$2" label="$3"
  if grep -qE "$pattern" "$file" 2>/dev/null; then
    echo "FAIL $label (found forbidden in $file)"
    fail=1
  else
    echo "OK  $label"
  fi
}

echo ">>> fhc-11 model"
check_grep "Core/Family/FamilyHabitRemindersModels.swift" 'struct FamilyHabitCustomReminder' "custom model"
check_grep "Core/Family/FamilyHabitRemindersModels.swift" 'maxPerFamily = 5' "max 5"
check_grep "Core/Family/FamilyHabitRemindersModels.swift" 'case onceDaily = "once_daily"' "mode once_daily"
check_grep "Core/Family/FamilyHabitRemindersModels.swift" 'case window' "mode window"
check_grep "Core/Family/FamilyHabitRemindersModels.swift" 'var custom: \[FamilyHabitCustomReminder\]' "config.custom"
check_grep "Core/Family/FamilyHabitRemindersModels.swift" 'func windowNotificationSlots' "window slots"
check_grep "Core/Family/FamilyHabitRemindersModels.swift" 'func normalizedList' "normalizedList"

echo ">>> fhc-11 scheduler"
check_grep "Core/Family/FamilyHabitRemindersScheduler.swift" 'customIdNamespace = "family\.habit\.custom\."' "id namespace"
check_grep "Core/Family/FamilyHabitRemindersScheduler.swift" 'customPresetPrefix = "custom\."' "preset prefix"
check_grep "Core/Family/FamilyHabitRemindersScheduler.swift" 'func fireCustomTestNotification' "test-push API"
check_grep "Core/Family/FamilyHabitRemindersScheduler.swift" 'func scheduleOnceAt' "once_at schedule path"
check_grep "Core/Family/FamilyHabitRemindersScheduler.swift" 'customOnceAtIdentifier' "once_at id helper"

echo ">>> fhc-11 service soft-fail (S1)"
check_grep "Core/Family/FamilyHabitRemindersService.swift" 'struct HabitRemindersBody' "POST body"
check_grep "Core/Family/FamilyHabitRemindersService.swift" 'let custom: \[FamilyHabitCustomReminder\]' "body.custom"
check_grep "Core/Family/FamilyHabitRemindersService.swift" 'func applyServerConfig' "applyServerConfig"
check_grep "Core/Family/FamilyHabitRemindersService.swift" 'func configAfterSyncFailure' "configAfterSyncFailure"
check_grep "Core/Family/FamilyHabitRemindersService.swift" 'family_habit_custom_server_outdated' "outdated-server key"
check_grep "Core/Family/FamilyHabitRemindersService.swift" 'family_habit_custom_sync_failed' "sync-failed key"
# Failure path must not assign factory empty as wipe
if grep -n 'config = \.empty' "Core/Family/FamilyHabitRemindersService.swift" 2>/dev/null; then
  echo "FAIL service assigns config = .empty (wipe risk)"
  fail=1
else
  echo "OK  no config = .empty wipe in service"
fi

echo ">>> fhc-11 deep link + Done"
check_grep "Core/Family/UnicornDeepLinkRouter.swift" 'habit/done' "done deep link path"
check_grep "Core/Family/UnicornDeepLinkRouter.swift" 'custom\.' "custom preset in router"

echo ">>> fhc-11 UI + test-push (S2)"
check_grep "Shared/Components/FamilyHabitRemindersSection.swift" 'FamilyHabitCustomRemindersBlock' "custom block under Medicine section"
check_grep "Shared/Components/FamilyHabitCustomRemindersBlock.swift" 'family_habit_custom_test_push' "test-push key in UI"
check_grep "Shared/Components/FamilyHabitCustomRemindersBlock.swift" 'fireCustomTestNotification' "test-push calls scheduler"

echo ">>> fhc-11 localization keys (RU+EN)"
for key in \
  family_habit_custom_section_title \
  family_habit_custom_add \
  family_habit_custom_test_push \
  family_habit_custom_test_push_body \
  family_habit_custom_sync_failed \
  family_habit_custom_server_outdated \
  family_habit_custom_limit_reached
do
  count=$(grep -c "\"${key}\"" "Core/Localization/LocalizationManager.swift" || true)
  if [[ "$count" -ge 2 ]]; then
    echo "OK  loc key $key (×$count)"
  else
    echo "FAIL loc key $key (need RU+EN, found $count)"
    fail=1
  fi
done

echo ">>> fhc-11 server store (no wipe on omit)"
check_grep "app/services/family_habit_reminders_store.py" '_normalize_custom' "store normalize custom"
check_grep "app/services/family_habit_reminders_store.py" 'do not wipe stored custom' "omit custom no-wipe comment"
check_grep "app/routers/family.py" 'custom' "router mentions custom"

echo ">>> fhc-11 unit tests present"
check_grep "Tests/UnitTests/FamilyHabitRemindersPolicyTests.swift" 'testMaxFiveCustom' "max 5 test"
check_grep "Tests/UnitTests/FamilyHabitRemindersPolicyTests.swift" 'testTitleClampAndEmptyDrop' "empty title test"
check_grep "Tests/UnitTests/FamilyHabitRemindersPolicyTests.swift" 'testUnknownModeDoesNotCrashAndSkipsSchedule' "unknown mode test"
check_grep "Tests/UnitTests/FamilyHabitRemindersPolicyTests.swift" 'testConfigAfterSyncFailureNeverEmptyWhenHadCustom' "soft-fail test"
check_grep "Tests/UnitTests/FamilyHabitRemindersPolicyTests.swift" 'testWindowSixtyMinuteSlotsExactThenCap' "window slot math test"
check_grep "Tests/UnitTests/FamilyHabitRemindersPolicyTests.swift" 'testPolicyUnchangedWithCustomPresent' "policy unchanged test"

echo ">>> fhc-15/16/17"
check_grep "Shared/Components/FamilyHabitCustomRemindersBlock.swift" 'family_habit_custom_once_at_picker' "once_at DatePicker"
check_grep "Shared/Components/FamilyHabitCustomRemindersBlock.swift" 'func moveCustom' "reorder ▲▼"
check_grep "Core/Family/UnicornDeepLinkRouter.swift" 'family_habit_custom_create' "analytics create event"
check_grep "Core/Family/UnicornDeepLinkRouter.swift" 'allowedParamKeys' "analytics no-title keys"
check_grep "Core/Family/FamilyHabitRemindersService.swift" 'disableCustomAfterOnceAtDone' "once_at Done disables"

echo ">>> fhc-11 no-mock / stop-list smoke"
check_not_grep "Core/Family/FamilyHabitRemindersService.swift" 'sfm_mock' "no sfm_mock in service"
check_not_grep "Shared/Components/FamilyHabitCustomRemindersBlock.swift" 'sfm_mock' "no sfm_mock in custom UI"

if [[ "$fail" -ne 0 ]]; then
  echo "verify_family_habit_custom_static: FAIL"
  exit 1
fi
echo "verify_family_habit_custom_static: OK (G7)"
exit 0
