import json
from pathlib import Path
import plistlib
import sys

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_SUFFIXES = {
    ".a",
    ".dylib",
    ".so",
    ".dll",
    ".exe",
    ".car",
    ".lib",
    ".ipa",
    ".app",
    ".xcarchive",
}


def main() -> int:
    errors: list[str] = []

    prebuilt = [
        p
        for p in ROOT.rglob("*")
        if ".git" not in p.parts and p.is_file() and p.suffix.lower() in FORBIDDEN_SUFFIXES
    ]
    if prebuilt:
        errors.append(f"Prebuilt binaries present in repo: {prebuilt}")

    header = ROOT / "ios-jit-enabler/StikDebug/idevice/idevice.h"
    if header.exists():
        errors.append("Generated header idevice.h should not be pre-committed")

    modulemap = ROOT / "ios-jit-enabler/StikDebug/idevice/module.modulemap"
    if not modulemap.is_file() or "module idevice" not in modulemap.read_text(encoding="utf-8"):
        errors.append("Missing valid idevice/module.modulemap")

    map_view = ROOT / "ios-jit-enabler/StikDebug/Views/MapSelectionView.swift"
    mv_text = map_view.read_text(encoding="utf-8")
    if "#if compiler(>=6.2)" not in mv_text or ".glassEffect" not in mv_text:
        errors.append("MapSelectionView.swift missing #if compiler(>=6.2) guard")

    plist_path = ROOT / "ios-jit-enabler/StikDebug/Info.plist"
    with plist_path.open("rb") as fh:
        plist = plistlib.load(fh)
    schemes = [s for t in plist.get("CFBundleURLTypes", []) for s in t.get("CFBundleURLSchemes", [])]
    if "stikjit" not in schemes or "stikdebug" not in schemes:
        errors.append(f"Info.plist missing stikjit/stikdebug schemes: {schemes}")

    ent_path = ROOT / "ios-jit-enabler/StikDebug/StikDebug.entitlements"
    with ent_path.open("rb") as fh:
        ent = plistlib.load(fh)
    if "group.com.stik.stikdebug" not in ent.get("com.apple.security.application-groups", []):
        errors.append("StikDebug.entitlements missing app group")

    appicon_json = ROOT / "ios-jit-enabler/StikDebug/Assets.xcassets/AppIcon.appiconset/Contents.json"
    appicon_png = ROOT / "ios-jit-enabler/StikDebug/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png"
    if not appicon_png.is_file():
        errors.append("Missing AppIcon-1024.png")
    icon_meta = json.loads(appicon_json.read_text(encoding="utf-8"))
    if icon_meta["images"][0]["filename"] != "AppIcon-1024.png":
        errors.append("Unexpected AppIcon filename in Contents.json")

    yml_text = (ROOT / "ios-jit-enabler/project.yml").read_text(encoding="utf-8")
    for token in ("com.stik.stikdebug", "-lidevice_ffi", "CodeEditorView", "LanguageSupport"):
        if token not in yml_text:
            errors.append(f"project.yml missing token: {token}")

    wf_text = (ROOT / ".github/workflows/build-jit-tools.yml").read_text(encoding="utf-8")
    for token in ("2dca9a58a9a1dd02ec7d6213fcfd8fe861e74132", "macos-15", "windows-latest", "xcodegen"):
        if token not in wf_text:
            errors.append(f"Workflow missing token: {token}")

    for rel in ("win-pairing-tool/Cargo.toml", "win-pairing-tool/Cargo.lock", "win-pairing-tool/build.rs"):
        if not (ROOT / rel).is_file():
            errors.append(f"Missing {rel}")

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    print("ALL CHECKS PASSED (zero prebuilt binaries, clean project.yml, guarded Swift 6.2 API, valid CI workflow)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
