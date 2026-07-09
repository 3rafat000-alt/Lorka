---
description: Build mobile for new feature. /mob-new <feature>
agent: mob-lead
---

# 🆕 MOBILE — NEW FEATURE: $ARGUMENTS

## Delegation (parallel)

### 1. Flutter Engineer — @mob-flutter-engineer
🎭 **Role:** Flutter Engineer — clean architecture
📂 **Context:** API contract frozen + UI spec frozen · Gate 4
🎯 **Command:** Implement feature-first clean architecture. GetIt DI. DTOs matching API contract. Repository pattern
📐 **Format:** Code in `lib/features/<feature>/`

### 2. State Engineer — @mob-state-engineer
🎭 **Role:** State Engineer — Bloc/Cubit
📂 **Context:** Feature + API endpoints
🎯 **Command:** Implement Bloc/Cubit for all states (initial/loading/loaded/error). HydratedBloc persistence. Bloc tests
📐 **Format:** Code in `lib/features/<feature>/bloc/` · `test/`

### 3. Platform Engineer — @mob-platform-engineer
🎭 **Role:** Platform Engineer — native channels
📂 **Context:** Feature with native requirements
🎯 **Command:** Implement platform channels for iOS/Android. Permissions, deep linking. Typed ApiException pattern
📐 **Format:** Code in `lib/platform/` · platform-specific

### 4. Perf Profiler — @mob-perf-profiler
🎭 **Role:** Perf Profiler — measurements
📂 **Context:** Built mobile feature
🎯 **Command:** Profile app size, memory leaks, frame drops, startup time. Before/after measurements
📐 **Format:** `docs/Mobile_Perf_Report.md` · budgets enforced

### 5. Release Engineer — @mob-release-engineer
🎭 **Role:** Release Engineer — store builds
📂 **Context:** Feature complete
🎯 **Command:** Configure build, signing, versioning. Release checklist
📐 **Format:** Release config + checklist

## Handoff
→ João Silva reviews + merges → QA Room `/qa-new "mobile: $ARGUMENTS"`