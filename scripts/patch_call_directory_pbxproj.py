#!/usr/bin/env python3
"""Add ALADDINCallDirectory target + new antifake Swift files to project.pbxproj."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBX = ROOT / "ALADDIN.xcodeproj" / "project.pbxproj"

MAIN_SWIFT = [
    ("Core/Security/AntifakeAccessPolicy.swift", "AFCD0302F90000200C7D34B", "AFCD0312F90000200C7D34B"),
    ("Core/Security/AntifakeCheckHistoryStore.swift", "AFCD0322F90000200C7D34B", "AFCD0332F90000200C7D34B"),
    ("Core/Security/AntifakeCallDirectorySyncService.swift", "AFCD0342F90000200C7D34B", "AFCD0352F90000200C7D34B"),
    ("Core/Security/AntifakeCallObserverService.swift", "AFCD0362F90000200C7D34B", "AFCD0372F90000200C7D34B"),
    ("Shared/AntifakeCallDirectory/AntifakeCallDirectoryStore.swift", "AFCD0032F90000200C7D34B", "AFCD0042F90000200C7D34B"),
    ("Shared/Components/AntifakeCallDirectorySettingsCard.swift", "AFCD0382F90000200C7D34B", "AFCD0392F90000200C7D34B"),
    ("Shared/Components/AntifakeCheckHistorySection.swift", "AFCD0402F90000200C7D34B", "AFCD0412F90000200C7D34B"),
    ("Shared/Components/AntifakeQuickVoiceCaptureView.swift", "AFCD0422F90000200C7D34B", "AFCD0432F90000200C7D34B"),
]

EXT_HANDLER = ("ALADDINCallDirectory/CallDirectoryHandler.swift", "AFCD0012F90000200C7D34B", "AFCD0022F90000200C7D34B")
STORE_FILE_REF = "AFCD0032F90000200C7D34B"
STORE_EXT_BUILD = "AFCD0052F90000200C7D34B"

# Extension target IDs
T_NATIVE = "AFCD0172F90000200C7D34B"
T_CONFIG_LIST = "AFCD0182F90000200C7D34B"
T_DEBUG = "AFCD0192F90000200C7D34B"
T_RELEASE = "AFCD0202F90000200C7D34B"
T_GROUP = "AFCD0212F90000200C7D34B"
T_ENT = "AFCD0092F90000200C7D34B"
T_PLIST = "AFCD0082F90000200C7D34B"
T_PRODUCT = "AFCD0102F90000200C7D34B"
T_EMBED = "AFCD0112F90000200C7D34B"
T_SOURCES = "AFCD0142F90000200C7D34B"
T_FRAMEWORKS = "AFCD0152F90000200C7D34B"
T_RESOURCES = "AFCD0162F90000200C7D34B"
T_PROXY = "AFCD0122F90000200C7D34B"
T_DEPEND = "AFCD0132F90000200C7D34B"


def insert_once(content: str, marker: str, block: str, label: str) -> str:
    if block.strip() in content or label in content:
        return content
    if marker not in content:
        print(f"WARN: marker not found for {label}")
        return content
    return content.replace(marker, block + marker, 1)


def main() -> int:
    content = PBX.read_text(encoding="utf-8")
    if T_NATIVE in content:
        print("Call Directory target already present — patching main sources only")
    else:
        # PBXBuildFile
        build_files = f"""
\t\t{T_EMBED} /* ALADDINCallDirectory.appex in Embed App Extensions */ = {{isa = PBXBuildFile; fileRef = {T_PRODUCT} /* ALADDINCallDirectory.appex */; settings = {{ATTRIBUTES = (RemoveHeadersOnCopy, ); }}; }};
\t\t{EXT_HANDLER[2]} /* CallDirectoryHandler.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {EXT_HANDLER[1]} /* CallDirectoryHandler.swift */; }};
\t\t{STORE_EXT_BUILD} /* AntifakeCallDirectoryStore.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {STORE_FILE_REF} /* AntifakeCallDirectoryStore.swift */; }};
/* END PATCH BUILD */"""
        content = insert_once(content, "/* End PBXBuildFile section */", build_files, "PBXBuildFile ext")

        file_refs = f"""
\t\t{EXT_HANDLER[1]} /* CallDirectoryHandler.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = CallDirectoryHandler.swift; sourceTree = "<group>"; }};
\t\t{T_ENT} /* ALADDINCallDirectory.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = ALADDINCallDirectory.entitlements; sourceTree = "<group>"; }};
\t\t{T_PLIST} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
\t\t{T_PRODUCT} /* ALADDINCallDirectory.appex */ = {{isa = PBXFileReference; explicitFileType = "wrapper.app-extension"; includeInIndex = 0; path = ALADDINCallDirectory.appex; sourceTree = BUILT_PRODUCTS_DIR; }};
/* END PATCH FILEREF ext */"""
        content = insert_once(content, "/* End PBXFileReference section */", file_refs, "PBXFileReference ext")

        group = f"""
\t\t{T_GROUP} /* ALADDINCallDirectory */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{EXT_HANDLER[1]} /* CallDirectoryHandler.swift */,
\t\t\t\t{T_PLIST} /* Info.plist */,
\t\t\t\t{T_ENT} /* ALADDINCallDirectory.entitlements */,
\t\t\t);
\t\t\tpath = ALADDINCallDirectory;
\t\t\tsourceTree = "<group>";
\t\t}};
/* END PATCH GROUP ext */"""
        content = insert_once(content, "\t\tAFSh0212F90000100C7D34B /* ALADDINAntifakeShare */ = {", group, "PBXGroup ext")
        content = content.replace(
            "\t\t\t\tAFSh0212F90000100C7D34B /* ALADDINAntifakeShare */,\n",
            "\t\t\t\tAFSh0212F90000100C7D34B /* ALADDINAntifakeShare */,\n\t\t\t\t{T_GROUP} /* ALADDINCallDirectory */,\n".format(T_GROUP=T_GROUP),
            1,
        )

        content = content.replace(
            "\t\t\t\tAFSh0102F90000100C7D34B /* ALADDINAntifakeShare.appex */,\n",
            "\t\t\t\tAFSh0102F90000100C7D34B /* ALADDINAntifakeShare.appex */,\n\t\t\t\t{T_PRODUCT} /* ALADDINCallDirectory.appex */,\n".format(T_PRODUCT=T_PRODUCT),
            1,
        )

        target = f"""
\t\t{T_NATIVE} /* ALADDINCallDirectory */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {T_CONFIG_LIST} /* Build configuration list for PBXNativeTarget "ALADDINCallDirectory" */;
\t\t\tbuildPhases = (
\t\t\t\t{T_SOURCES} /* Sources */,
\t\t\t\t{T_FRAMEWORKS} /* Frameworks */,
\t\t\t\t{T_RESOURCES} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tname = ALADDINCallDirectory;
\t\t\tproductName = ALADDINCallDirectory;
\t\t\tproductReference = {T_PRODUCT} /* ALADDINCallDirectory.appex */;
\t\t\tproductType = "com.apple.product-type.app-extension";
\t\t}};
/* END PATCH TARGET */"""
        content = insert_once(content, "/* End PBXNativeTarget section */", target, "PBXNativeTarget")

        content = content.replace(
            "\t\t\t\tAFSh0172F90000100C7D34B /* ALADDINAntifakeShare */,\n",
            "\t\t\t\tAFSh0172F90000100C7D34B /* ALADDINAntifakeShare */,\n\t\t\t\t{T_NATIVE} /* ALADDINCallDirectory */,\n".format(T_NATIVE=T_NATIVE),
            1,
        )

        content = content.replace(
            "\t\t\t\tAFSh0112F90000100C7D34B /* ALADDINAntifakeShare.appex in Embed App Extensions */,\n",
            "\t\t\t\tAFSh0112F90000100C7D34B /* ALADDINAntifakeShare.appex in Embed App Extensions */,\n\t\t\t\t{T_EMBED} /* ALADDINCallDirectory.appex in Embed App Extensions */,\n".format(T_EMBED=T_EMBED),
            1,
        )

        content = content.replace(
            "\t\t\tdependencies = (\n\t\t\t\t5E61A0A62EFB38ED0039093A /* PBXTargetDependency */,\n\t\t\t\tAFSh0132F90000100C7D34B /* PBXTargetDependency */,\n\t\t\t);",
            "\t\t\tdependencies = (\n\t\t\t\t5E61A0A62EFB38ED0039093A /* PBXTargetDependency */,\n\t\t\t\tAFSh0132F90000100C7D34B /* PBXTargetDependency */,\n\t\t\t\t{T_DEPEND} /* PBXTargetDependency */,\n\t\t\t);".format(T_DEPEND=T_DEPEND),
            1,
        )

        proxy = f"""
\t\t{T_PROXY} /* PBXContainerItemProxy */ = {{
\t\t\tisa = PBXContainerItemProxy;
\t\t\tcontainerPortal = A0FFFFF6 /* Project object */;
\t\t\tproxyType = 1;
\t\t\tremoteGlobalIDString = {T_NATIVE};
\t\t\tremoteInfo = ALADDINCallDirectory;
\t\t}};
/* END PROXY */"""
        content = insert_once(content, "/* End PBXContainerItemProxy section */", proxy, "PBXContainerItemProxy")

        depend = f"""
\t\t{T_DEPEND} /* PBXTargetDependency */ = {{
\t\t\tisa = PBXTargetDependency;
\t\t\ttarget = {T_NATIVE} /* ALADDINCallDirectory */;
\t\t\ttargetProxy = {T_PROXY} /* PBXContainerItemProxy */;
\t\t}};
/* END DEPEND */"""
        content = insert_once(content, "/* End PBXTargetDependency section */", depend, "PBXTargetDependency")

        phases = f"""
\t\t{T_SOURCES} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tfiles = (
\t\t\t\t{EXT_HANDLER[2]} /* CallDirectoryHandler.swift in Sources */,
\t\t\t\t{STORE_EXT_BUILD} /* AntifakeCallDirectoryStore.swift in Sources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{T_FRAMEWORKS} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{T_RESOURCES} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* END PHASES */"""
        content = insert_once(content, "/* End PBXSourcesBuildPhase section */", phases, "PBXSourcesBuildPhase ext")

        configs = f"""
\t\t{T_DEBUG} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tCODE_SIGN_ENTITLEMENTS = ALADDINCallDirectory/ALADDINCallDirectory.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 231;
\t\t\t\tDEVELOPMENT_TEAM = "";
\t\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\t\tINFOPLIST_FILE = ALADDINCallDirectory/Info.plist;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 15.0;
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t\t"@executable_path/../../Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = family.aladdin.ios.ALADDINCallDirectory;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{T_RELEASE} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tCODE_SIGN_ENTITLEMENTS = ALADDINCallDirectory/ALADDINCallDirectory.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 231;
\t\t\t\tDEVELOPMENT_TEAM = "";
\t\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\t\tINFOPLIST_FILE = ALADDINCallDirectory/Info.plist;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 15.0;
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t\t"@executable_path/../../Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = family.aladdin.ios.ALADDINCallDirectory;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = Release;
\t\t}};
\t\t{T_CONFIG_LIST} /* Build configuration list for PBXNativeTarget "ALADDINCallDirectory" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{T_DEBUG} /* Debug */,
\t\t\t\t{T_RELEASE} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
/* END CONFIGS */"""
        content = insert_once(content, "/* End XCBuildConfiguration section */", configs, "XCBuildConfiguration ext")

        ta_line = (
            "\t\t\tAFSh0172F90000100C7D34B = {\n"
            "\t\t\t\tCreatedOnToolsVersion = 16.0;\n"
            "\t\t\t};\n"
            f"\t\t\t{T_NATIVE} = {{\n"
            "\t\t\t\tCreatedOnToolsVersion = 16.0;\n"
            "\t\t\t}};"
        )
        content = content.replace(
            "\t\t\tAFSh0172F90000100C7D34B = {\n\t\t\t\tCreatedOnToolsVersion = 16.0;\n\t\t\t};",
            ta_line,
            1,
        )

    # Main app swift files
    for path, file_ref, build_file in MAIN_SWIFT:
        if file_ref in content:
            continue
        name = Path(path).name
        fr = f"\t\t{file_ref} /* {name} */ = {{isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; name = {name}; path = {path}; sourceTree = \"<group>\"; }};\n"
        bf = f"\t\t{build_file} /* {name} in Sources */ = {{isa = PBXBuildFile; fileRef = {file_ref} /* {name} */; }};\n"
        content = insert_once(content, "/* End PBXFileReference section */", fr, f"fileref {name}")
        content = insert_once(content, "/* End PBXBuildFile section */", bf, f"buildfile {name}")
        content = insert_once(
            content,
            "\t\t\t\tAFSh0022F90000100C7D34B /* AntifakeSharePayloadStore.swift in Sources */,",
            f"\t\t\t\t{build_file} /* {name} in Sources */,\n",
            f"main source {name}",
        )

    PBX.write_text(content, encoding="utf-8")
    print("Patched", PBX)
    return 0


if __name__ == "__main__":
    sys.exit(main())
