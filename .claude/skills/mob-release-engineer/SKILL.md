---
name: mob-release-engineer
description: "Store builds, signing, versioning, release channels."
---
# Mobile - Release Engineer

Build and sign Flutter app for store submission. Supports Android (appbundle) and iOS (archive) with dry-run mode.

## Tool
`.claude/tools/mob/release-engineer/build-sign.sh`

## When to use
- Gate 7 production release: build signed artifacts for store submission
- CI/CD pipeline: scriptable build step for Android/iOS
- Dry-run: validate build pipeline without executing destructive steps

## How to use
```bash
.claude/tools/mob/release-engineer/build-sign.sh <PRJ-ID> <platform> [--dry-run]
```

## Input
- `PRJ-ID` — project directory
- `platform` — `android` or `ios`
- `--dry-run` — show commands without executing

## Output
- Android: run `flutter clean` → `flutter pub get` → `flutter build appbundle --release`, report AAB path and size
- iOS: run `flutter clean` → `flutter pub get` → `flutter build ios --release`, with xcarchive manual fallback instructions
- Post-build checklist: verify pubspec version, run tests, upload to store

## Related
- `engine/agents/mob/release-engineer.md`
- `.claude/tools/mob/release-engineer/build-sign.sh`
