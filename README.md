# PovaJIT-Tools (100% Source-Built StikDebug + idevice_pair)

Clean CI build monorepo compiling **both** components of the iOS 26 / iOS 17.4+ JIT enabling toolchain directly from audited source code, with **zero precompiled binaries checked into the repository**:

1. **`ios-jit-enabler/`** — StikDebug Swift source (AGPL-3.0, upstream `StikDebug/StikDebug`), stripped of any checked-in `libidevice_ffi.a` or generated `idevice.h`. In GitHub Actions (`macos-15`), `libidevice_ffi.a` and `idevice.h` are freshly compiled from pinned `jkcoxson/idevice` commit `2dca9a58a9a1dd02ec7d6213fcfd8fe861e74132` (`aarch64-apple-ios`), then linked into `Pova-StikDebug.ipa`.
2. **`win-pairing-tool/`** — `idevice_pair` v1.2.0 pure Rust source (`jkcoxson/idevice_pair`), stripped of macOS `Assets.car` / `icon.icns`, compiled cleanly on `windows-latest` with `cargo build --release --locked` into `Pova-idevice_pair.exe`.

## Source Provenance & Compatibility Notes

- StikDebug `MapSelectionView.swift` wraps iOS 26 SDK `.glassEffect(in: .rect(cornerRadius: 12))` with `#if compiler(>=6.2)` so Xcode 16.4 (`macos-15`) compiles cleanly while retaining iOS 26 Swift 6.2 support.
- `AppIcon.appiconset` (1024x1024 PNG) replaces Xcode 26 `.icon` composer asset for Xcode 16.4 compatibility.
- SwiftPM package `CodeEditorView` is pinned via `Package.resolved` to `0.15.4` (`Rearrange` `1.8.1`).
