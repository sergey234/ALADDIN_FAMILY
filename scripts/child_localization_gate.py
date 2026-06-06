#!/usr/bin/env python3
"""Gate: child UI keys must resolve in RU+EN.

Modes:
  default — child keys from core mnemo screens (incremental batches)
  --mnemo-full — all child+parent+onboarding mnemo keys (~350+, B15-T01)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALIZATION_MANAGER = ROOT / "Core/Localization/LocalizationManager.swift"
RU_STRINGS = ROOT / "Resources/Localization/ru.lproj/Localizable.strings"
EN_STRINGS = ROOT / "Resources/Localization/en.lproj/Localizable.strings"

CHILD_CORE_SCREENS = [
    ROOT / "Screens/08_ChildInterfaceScreen.swift",
    ROOT / "Screens/ChildContentScreen.swift",
    ROOT / "Screens/ChildContentExperienceScreen.swift",
    ROOT / "Core/Content/Mnemonics/MnemoPictogramEncodeCTA.swift",
    ROOT / "Core/Content/Mnemonics/MnemoPictogramDrawingSheet.swift",
    ROOT / "Core/Content/Mnemonics/MnemoPictogramRecallHint.swift",
    ROOT / "Core/Content/Mnemonics/MnemoBaselineAssessmentView.swift",
    ROOT / "Core/Content/Mnemonics/MnemoStudyCapstoneExperienceView.swift",
    ROOT / "Core/Content/Mnemonics/MnemoChampionshipExperienceView.swift",
    ROOT / "Core/Content/Mnemonics/MnemoTableExperienceView.swift",
    ROOT / "Core/Content/Mnemonics/MnemoHintLadderRecallView.swift",
]

MANAGER_KEY_RE = re.compile(r'"([A-Za-z0-9_.:-]+)"\s*:')
LOCALIZED_CALL_RE = re.compile(r'localized\(\s*"([A-Za-z0-9_.:-]+)"')
PICTOGRAM_KEY_LITERAL_RE = re.compile(r'"((?:child_mnemo_pictogram_)[A-Za-z0-9_.:-]+)"')
MNEMO_PICTOGRAM_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoPictogramEncodeCTA.swift",
    ROOT / "Core/Content/Mnemonics/MnemoPictogramDrawingSheet.swift",
    ROOT / "Core/Content/Mnemonics/MnemoPictogramRecallHint.swift",
]
BASELINE_KEY_LITERAL_RE = re.compile(r'"((?:child_mnemo_baseline_)[A-Za-z0-9_.:-]+)"')
MNEMO_BASELINE_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoBaselineAssessmentView.swift",
    ROOT / "Core/Content/Mnemonics/MnemonicBaselineAssessment.swift",
    ROOT / "Screens/ChildContentScreen.swift",
]
# Interpolated in MnemonicBaselineAssessment.wordLocalizationKeys (B12-T07 gate).
MNEMO_BASELINE_EXPANDED_KEYS = [f"child_mnemo_baseline_word_{i}" for i in range(1, 6)]
CAPSTONE_KEY_LITERAL_RE = re.compile(r'"((?:child_mnemo_capstone_)[A-Za-z0-9_.:-]+)"')
MNEMO_CAPSTONE_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoStudyCapstoneExperienceView.swift",
    ROOT / "Core/Content/Mnemonics/MnemonicCapstoneStore.swift",
    ROOT / "Core/Content/Mnemonics/MnemonicRewardBridge.swift",
]
# Interpolated in MnemonicCapstoneStore.topicLocalizationKeys (B12-T07 gate).
MNEMO_CAPSTONE_EXPANDED_KEYS = [f"child_mnemo_capstone_topic_{i}" for i in range(1, 7)]
MNEMO_CAPSTONE_REWARD_KEYS = ["child_mnemo_reward_capstone"]
MICRO_WIN_KEY_LITERAL_RE = re.compile(r'"((?:child_mnemo_reward_micro_win)[A-Za-z0-9_.:-]+)"')
MNEMO_MICRO_WIN_EXPANDED_KEYS = ["child_mnemo_reward_micro_win"]
CHAMPIONSHIP_KEY_LITERAL_RE = re.compile(r'"((?:child_mnemo_championship_)[A-Za-z0-9_.:-]+)"')
MNEMO_CHAMPIONSHIP_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoChampionshipExperienceView.swift",
    ROOT / "Screens/ChildContentExperienceScreen.swift",
]
TABLE_KEY_LITERAL_RE = re.compile(r'"((?:child_mnemo_table_)[A-Za-z0-9_.:-]+)"')
MNEMO_TABLE_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoTableExperienceView.swift",
    ROOT / "Core/Content/Mnemonics/MnemonicTableEngine.swift",
]
MNEMO_TABLE_EXPANDED_KEYS = [f"child_mnemo_table_cell_{i}" for i in range(1, 7)]
HINT_LADDER_KEY_LITERAL_RE = re.compile(r'"((?:child_mnemo_hint_ladder_)[A-Za-z0-9_.:-]+)"')
MNEMO_HINT_LADDER_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoHintLadderRecallView.swift",
    ROOT / "Core/Content/Mnemonics/MnemonicHintLadder.swift",
]
WARMUP_KEY_LITERAL_RE = re.compile(r'"((?:child_mnemo_warmup_|child_mnemo_phase_warmup)[A-Za-z0-9_.:-]+)"')
MNEMO_WARMUP_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoWarmupPhaseView.swift",
    ROOT / "Core/Content/Mnemonics/MnemoLessonFlow.swift",
]
REFLECT_KEY_LITERAL_RE = re.compile(r'"((?:child_mnemo_reflect_|child_mnemo_phase_reflect)[A-Za-z0-9_.:-]+)"')
TECHNIQUE_PICKER_KEY_LITERAL_RE = re.compile(
    r'"((?:child_mnemo_technique_picker_|child_mnemo_phase_technique_pick)[A-Za-z0-9_.:-]+)"'
)
MNEMO_REFLECT_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoReflectPhaseView.swift",
]
MNEMO_TECHNIQUE_PICKER_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoTechniquePickerView.swift",
    ROOT / "Core/Content/Mnemonics/MnemonicStudyTechniqueMap.swift",
    ROOT / "Core/Content/Mnemonics/MnemoLessonFlow.swift",
]
MNEMO_TECHNIQUE_PICKER_EXPANDED_KEYS = [
    "child_mnemo_phase_technique_pick",
    "child_mnemo_technique_picker_title",
    "child_mnemo_technique_picker_subtitle",
    "child_mnemo_technique_picker_prompt",
    "child_mnemo_technique_picker_recommended_badge",
    "child_mnemo_technique_picker_context_vocab",
    "child_mnemo_technique_picker_context_formula",
    "child_mnemo_technique_picker_context_dates",
    "child_mnemo_technique_picker_context_general",
    "child_mnemo_technique_picker_selected_format",
    "child_mnemo_technique_picker_continue",
]
MNEMO_REFLECT_EXPANDED_KEYS = [
    "child_mnemo_phase_reflect",
    "child_mnemo_reflect_title",
    "child_mnemo_reflect_subtitle",
    "child_mnemo_reflect_prompt",
    "child_mnemo_reflect_feedback_ok",
    "child_mnemo_reflect_feedback_hint",
    "child_mnemo_reflect_technique_format",
]
MNEMO_WARMUP_EXPANDED_KEYS = [
    "child_mnemo_phase_warmup",
    "child_mnemo_warmup_title",
    "child_mnemo_warmup_subtitle",
    "child_mnemo_warmup_technique_format",
    "child_mnemo_warmup_focus_prompt",
    "child_mnemo_warmup_timer_format",
    "child_mnemo_warmup_start_encode",
    "child_mnemo_warmup_skip",
]
MNEMO_HINT_LADDER_EXPANDED_KEYS = [
    "child_mnemo_hint_ladder_step_image",
    "child_mnemo_hint_ladder_step_letter",
    "child_mnemo_hint_ladder_step_choice",
    "child_mnemo_hint_ladder_recall_image_prompt",
    "child_mnemo_hint_ladder_show_letter",
    "child_mnemo_hint_ladder_show_choices",
    "child_mnemo_hint_ladder_letter_format",
    "child_mnemo_hint_ladder_try_again",
]
PARENT_GUIDE_KEY_LITERAL_RE = re.compile(r'"((?:parent_mnemo_guide_)[A-Za-z0-9_.:-]+)"')
MNEMO_PARENT_GUIDE_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoParentGuideContent.swift",
]
PARENT_SEMESTER_PROGRESS_KEY_LITERAL_RE = re.compile(
    r'"((?:parent_dashboard_mnemo_semester_progress_)[A-Za-z0-9_.:-]+)"'
)
MNEMO_PARENT_SEMESTER_PROGRESS_SOURCES = [
    ROOT / "Core/Content/Mnemonics/MnemoParentSemesterProgressView.swift",
]
MNEMO_PARENT_SEMESTER_PROGRESS_EXPANDED_KEYS = [
    "parent_dashboard_mnemo_semester_progress_title",
    "parent_dashboard_mnemo_semester_progress_headline",
    "parent_dashboard_mnemo_semester_progress_next_label",
    "parent_dashboard_mnemo_semester_progress_threshold",
    "parent_dashboard_mnemo_semester_progress_remaining",
    "parent_dashboard_mnemo_semester_progress_complete",
]
MNEMO_PARENT_GUIDE_TECHNIQUE_RAW_VALUES = [
    "rhymePeg",
    "linkChain",
    "memoryPalace",
    "keyword",
    "acronym",
    "chunking",
    "rhythmCode",
    "framePeg",
    "storyLink",
    "spacedReview",
]
MNEMO_PARENT_GUIDE_EXPANDED_KEYS = [
    "parent_mnemo_guide_title",
    "parent_mnemo_guide_subtitle",
    "parent_mnemo_guide_open_cta",
    "parent_mnemo_guide_intro_title",
    "parent_mnemo_guide_intro_lead",
    "parent_mnemo_guide_intro_aim_title",
    "parent_mnemo_guide_intro_aim_association",
    "parent_mnemo_guide_intro_aim_imagination",
    "parent_mnemo_guide_intro_aim_location",
    "parent_mnemo_guide_intro_4d_title",
    "parent_mnemo_guide_intro_4d_body",
    "parent_mnemo_guide_srs_title",
    "parent_mnemo_guide_srs_lead",
    "parent_mnemo_guide_srs_tip_calm",
    "parent_mnemo_guide_srs_tip_routine",
    "parent_mnemo_guide_srs_tip_praise",
    "parent_mnemo_guide_mq_title",
    "parent_mnemo_guide_mq_lead",
    "parent_mnemo_guide_mq_scale",
    "parent_mnemo_guide_mq_quarterly",
] + [f"parent_mnemo_guide_technique_{raw}" for raw in MNEMO_PARENT_GUIDE_TECHNIQUE_RAW_VALUES]
MNEMO_FULL_MIN_KEYS = 350
MNEMO_FULL_SCAN_PATHS = [
    ROOT / "Core/Content/Mnemonics",
    ROOT / "Screens/ChildContentScreen.swift",
    ROOT / "Screens/ChildContentExperienceScreen.swift",
    ROOT / "Screens/ParentDashboardView.swift",
    ROOT / "Screens/08_ChildInterfaceScreen.swift",
]
MNEMO_FULL_KEY_RE = re.compile(
    r'"((?:child_mnemo_|parent_mnemo_|parent_dashboard_mnemo_|onboarding_mnemo_)[A-Za-z0-9_.:-]+)"'
)
MNEMO_TECHNIQUE_STAGE_KEYS = [
    "child_mnemo_technique_stage_awareness",
    "child_mnemo_technique_stage_practice",
    "child_mnemo_technique_stage_fluent",
    "child_mnemo_technique_stage_master",
]
MNEMO_TECHNIQUE_KEYS = [
    "child_mnemo_technique_rhyme_peg",
    "child_mnemo_technique_link_chain",
    "child_mnemo_technique_memory_palace",
    "child_mnemo_technique_keyword",
    "child_mnemo_technique_acronym",
    "child_mnemo_technique_chunking",
    "child_mnemo_technique_rhythm_code",
    "child_mnemo_technique_frame_peg",
    "child_mnemo_technique_story_link",
    "child_mnemo_technique_spaced_review",
]
MNEMO_BRAND_STATIC_KEYS = [
    "child_mnemo_brand_promise",
    "child_mnemo_brand_superpower_title",
    "child_mnemo_brand_superpower_toast",
    "parent_mnemo_brand_smart_title",
    "parent_mnemo_brand_smart_subtitle",
    "onboarding_mnemo_academy_title",
    "onboarding_mnemo_academy_desc",
]
MNEMO_CATALOG_CHROME_KEYS = [
    "child_mnemo_label_songs_kids",
    "child_mnemo_label_games_school",
    "child_mnemo_label_study_school",
    "child_mnemo_label_cartoons_school",
    "child_mnemo_label_music_teen",
    "child_mnemo_label_video_teen",
    "child_mnemo_label_movies_young",
    "child_mnemo_label_education_young",
    "child_mnemo_subtitle_songs_kids",
    "child_mnemo_subtitle_games_school",
    "child_mnemo_subtitle_study_school",
    "child_mnemo_subtitle_cartoons_school",
    "child_mnemo_subtitle_music_teen",
    "child_mnemo_subtitle_video_teen",
    "child_mnemo_subtitle_movies_young",
    "child_mnemo_subtitle_education_young",
    "child_mnemo_catalog_greeting_songs_kids",
    "child_mnemo_catalog_greeting_games_school",
    "child_mnemo_catalog_greeting_study_school",
    "child_mnemo_catalog_greeting_cartoons_school",
    "child_mnemo_catalog_greeting_music_teen",
    "child_mnemo_catalog_greeting_video_teen",
    "child_mnemo_catalog_greeting_movies_young",
    "child_mnemo_catalog_greeting_education_young",
]
MNEMO_GAMES_PAIR_EXPANDED_KEYS = [
    f"child_mnemo_games_12_pair_{index}_{kind}"
    for index in range(1, 7)
    for kind in ("word", "image")
]
MNEMO_MISC_FULL_KEYS = [
    "child_mnemo_journey_hint",
    "child_mnemo_recall_guided_hint",
    "child_mnemo_srs_next_review",
    "parent_dashboard_mnemo_mastery_title",
    "parent_dashboard_mnemo_mastery_subtitle",
]
STRINGS_LINE_RE = re.compile(r'^\s*"([^"]+)"\s*=\s*"((?:\\.|[^"\\])*)"\s*;\s*$')


def parse_strings(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = STRINGS_LINE_RE.match(line)
        if not match:
            continue
        values[match.group(1)] = match.group(2)
    return values


def parse_manager_language_block(
    content: str,
    anchor: str,
    language_pattern: str,
    next_pattern: str,
) -> set[str]:
    anchor_pos = content.find(anchor)
    if anchor_pos == -1:
        return set()
    scoped = content[anchor_pos:]
    start_match = re.search(language_pattern, scoped)
    if not start_match:
        return set()
    after_start = scoped[start_match.end():]
    next_match = re.search(next_pattern, after_start)
    if not next_match:
        return set()
    block = after_start[:next_match.start()]
    return set(MANAGER_KEY_RE.findall(block))


def collect_child_keys_from_core_screens() -> set[str]:
    keys: set[str] = set()
    for screen in CHILD_CORE_SCREENS:
        text = screen.read_text(encoding="utf-8", errors="ignore")
        keys.update(LOCALIZED_CALL_RE.findall(text))
    for source in MNEMO_PICTOGRAM_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "accessibilityIdentifier" in line:
                continue
            keys.update(PICTOGRAM_KEY_LITERAL_RE.findall(line))
    keys.update(MNEMO_BASELINE_EXPANDED_KEYS)
    for source in MNEMO_BASELINE_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "accessibilityIdentifier" in line:
                continue
            keys.update(BASELINE_KEY_LITERAL_RE.findall(line))
    keys.update(MNEMO_CAPSTONE_EXPANDED_KEYS)
    keys.update(MNEMO_CAPSTONE_REWARD_KEYS)
    keys.update(MNEMO_MICRO_WIN_EXPANDED_KEYS)
    for source in [ROOT / "Core/Content/Mnemonics/MnemonicRewardBridge.swift"]:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "accessibilityIdentifier" in line:
                continue
            keys.update(MICRO_WIN_KEY_LITERAL_RE.findall(line))
    for source in MNEMO_CAPSTONE_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "accessibilityIdentifier" in line:
                continue
            keys.update(CAPSTONE_KEY_LITERAL_RE.findall(line))
    for source in MNEMO_CHAMPIONSHIP_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "accessibilityIdentifier" in line:
                continue
            keys.update(CHAMPIONSHIP_KEY_LITERAL_RE.findall(line))
    keys.update(MNEMO_TABLE_EXPANDED_KEYS)
    for source in MNEMO_TABLE_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "accessibilityIdentifier" in line:
                continue
            keys.update(TABLE_KEY_LITERAL_RE.findall(line))
    keys.update(MNEMO_REFLECT_EXPANDED_KEYS)
    for source in MNEMO_REFLECT_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "accessibilityIdentifier" in line:
                continue
            keys.update(REFLECT_KEY_LITERAL_RE.findall(line))
    keys.update(MNEMO_TECHNIQUE_PICKER_EXPANDED_KEYS)
    for source in MNEMO_TECHNIQUE_PICKER_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "accessibilityIdentifier" in line:
                continue
            keys.update(TECHNIQUE_PICKER_KEY_LITERAL_RE.findall(line))
    keys.update(MNEMO_WARMUP_EXPANDED_KEYS)
    for source in MNEMO_WARMUP_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "accessibilityIdentifier" in line:
                continue
            keys.update(WARMUP_KEY_LITERAL_RE.findall(line))
    keys.update(MNEMO_HINT_LADDER_EXPANDED_KEYS)
    for source in MNEMO_HINT_LADDER_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "accessibilityIdentifier" in line:
                continue
            keys.update(HINT_LADDER_KEY_LITERAL_RE.findall(line))
    return {k for k in keys if k.startswith("child_")}


def collect_parent_guide_keys() -> set[str]:
    keys: set[str] = set(MNEMO_PARENT_GUIDE_EXPANDED_KEYS)
    for source in MNEMO_PARENT_GUIDE_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            keys.update(PARENT_GUIDE_KEY_LITERAL_RE.findall(line))
    return {k for k in keys if k.startswith("parent_mnemo_guide_")}


def collect_parent_semester_progress_keys() -> set[str]:
    keys: set[str] = set(MNEMO_PARENT_SEMESTER_PROGRESS_EXPANDED_KEYS)
    for source in MNEMO_PARENT_SEMESTER_PROGRESS_SOURCES:
        for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
            keys.update(PARENT_SEMESTER_PROGRESS_KEY_LITERAL_RE.findall(line))
    return keys


def collect_mnemo_full_keys() -> set[str]:
    """B15-T01: scan Mnemonics + mnemo screens; include programmatic key expansions."""
    keys: set[str] = set()
    for path in MNEMO_FULL_SCAN_PATHS:
        files = [path] if path.is_file() else sorted(path.rglob("*.swift"))
        for source in files:
            for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
                if "accessibilityIdentifier" in line:
                    continue
                keys.update(MNEMO_FULL_KEY_RE.findall(line))
    keys.update(MNEMO_BRAND_STATIC_KEYS)
    keys.update(MNEMO_CATALOG_CHROME_KEYS)
    keys.update(MNEMO_GAMES_PAIR_EXPANDED_KEYS)
    keys.update(MNEMO_MISC_FULL_KEYS)
    keys.update(MNEMO_TECHNIQUE_KEYS)
    keys.update(MNEMO_TECHNIQUE_STAGE_KEYS)
    keys.update(MNEMO_PARENT_GUIDE_EXPANDED_KEYS)
    keys.update(MNEMO_PARENT_SEMESTER_PROGRESS_EXPANDED_KEYS)
    keys.update(MNEMO_BASELINE_EXPANDED_KEYS)
    keys.update(MNEMO_CAPSTONE_EXPANDED_KEYS)
    keys.update(MNEMO_CAPSTONE_REWARD_KEYS)
    keys.update(MNEMO_MICRO_WIN_EXPANDED_KEYS)
    keys.update(MNEMO_TABLE_EXPANDED_KEYS)
    keys.update(MNEMO_REFLECT_EXPANDED_KEYS)
    keys.update(MNEMO_TECHNIQUE_PICKER_EXPANDED_KEYS)
    keys.update(MNEMO_WARMUP_EXPANDED_KEYS)
    keys.update(MNEMO_HINT_LADDER_EXPANDED_KEYS)
    for index in range(8):
        for suffix in ("title", "subtitle", "kpi"):
            keys.add(f"child_mnemo_semester_{index}_{suffix}")
    for index in range(1, 41):
        keys.add(f"child_mnemo_journey_stop_{index:02d}")
    keys.add("child_mnemo_journey_stop_current")
    keys.add("child_mnemo_journey_title")
    return keys


def main() -> int:
    mnemo_full = "--mnemo-full" in sys.argv
    prefix_filter: str | None = None
    args = sys.argv[1:]
    if "--prefix" in args:
        idx = args.index("--prefix")
        if idx + 1 < len(args):
            prefix_filter = args[idx + 1]
    manager_content = LOCALIZATION_MANAGER.read_text(encoding="utf-8")
    anchor = "var translations: [Language: [String: String]] = ["
    ru_manager_keys = parse_manager_language_block(
        manager_content,
        anchor=anchor,
        language_pattern=r"\n\s*\.russian:\s*\[",
        next_pattern=r"\n\s*\.english:\s*\[",
    )
    en_manager_keys = parse_manager_language_block(
        manager_content,
        anchor=anchor,
        language_pattern=r"\n\s*\.english:\s*\[",
        next_pattern=r"\n\s*\.arabic:\s*\[",
    )
    ru_strings = parse_strings(RU_STRINGS)
    en_strings = parse_strings(EN_STRINGS)

    if prefix_filter and prefix_filter.startswith("parent_dashboard_mnemo_semester_progress"):
        child_keys = sorted(collect_parent_semester_progress_keys())
        if prefix_filter != "parent_dashboard_mnemo_semester_progress_":
            child_keys = [k for k in child_keys if k.startswith(prefix_filter)]
    elif prefix_filter and prefix_filter.startswith("parent_mnemo"):
        child_keys = sorted(collect_parent_guide_keys())
        if prefix_filter != "parent_mnemo_":
            child_keys = [k for k in child_keys if k.startswith(prefix_filter)]
    elif mnemo_full:
        child_keys = sorted(collect_mnemo_full_keys())
        if prefix_filter:
            child_keys = [k for k in child_keys if k.startswith(prefix_filter)]
    else:
        child_keys = sorted(collect_child_keys_from_core_screens())
        if prefix_filter:
            child_keys = [k for k in child_keys if k.startswith(prefix_filter)]

    missing_ru = [
        key for key in child_keys if key not in ru_manager_keys and key not in ru_strings
    ]
    missing_en = [
        key for key in child_keys if key not in en_manager_keys and key not in en_strings
    ]

    if missing_ru or missing_en:
        print("❌ child-localization-gate failed")
        if missing_ru:
            print(f"- Missing RU for {len(missing_ru)} keys: {missing_ru[:80]}")
        if missing_en:
            print(f"- Missing EN for {len(missing_en)} keys: {missing_en[:80]}")
        print("\nFix: add keys to LocalizationManager.swift or Localizable.strings.")
        return 1

    if mnemo_full and len(child_keys) < MNEMO_FULL_MIN_KEYS:
        print("❌ child-localization-gate failed")
        print(
            f"- MNEMO full gate expects ≥{MNEMO_FULL_MIN_KEYS} keys, got {len(child_keys)}"
        )
        return 1

    print("✅ child-localization-gate passed")
    if mnemo_full:
        print(f"- Mnemo full keys checked: {len(child_keys)} (min {MNEMO_FULL_MIN_KEYS})")
    else:
        print(f"- Child keys checked: {len(child_keys)}")
    print("- Coverage: RU+EN resolved via LocalizationManager and/or Localizable.strings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
