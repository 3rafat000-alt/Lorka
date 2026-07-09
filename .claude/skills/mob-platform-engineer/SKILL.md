---
name: mob-platform-engineer
description: "Platform channels, iOS/Android specifics, typed ApiException pattern."
---
# Mobile - Platform Engineer

Generate a Flutter MethodChannel bridge with native stubs for iOS (Swift) and Android (Kotlin). Creates Dart-side channel class and native bridge registration code.

## Tool
`.claude/tools/mob/platform-engineer/channel-gen.sh`

## When to use
- New platform channel: bridge Flutter to native device APIs
- Gate 4 mobile platform layer: biometric auth, device info, file system access
- Native feature integration: generate Dart + Swift + Kotlin stubs in one command

## How to use
```bash
.claude/tools/mob/platform-engineer/channel-gen.sh <PRJ-ID> <channel-name> [method]
```

## Input
- `PRJ-ID` — project directory with `lib/` (and optionally `ios/` and `android/`)
- `channel-name` — snake_case channel name (e.g. `biometric_auth`)
- `method` — method name for the initial channel call (default: `call`)

## Output
- `lib/platform/{name}_channel.dart` — Dart MethodChannel class with invokeMethod wrapper
- `ios/Runner/{Name}Bridge.swift` — Swift FlutterPlugin with method call handler
- `android/app/src/main/kotlin/{Name}Bridge.kt` — Kotlin MethodChannel handler
- Registration hint for MainActivity/AppDelegate

## Related
- `engine/agents/mob/platform-engineer.md`
- `.claude/tools/mob/platform-engineer/channel-gen.sh`
