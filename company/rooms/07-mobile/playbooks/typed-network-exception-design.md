# Playbook — Typed Network Exception Design (specialty procedure)

> Owner: `mob-platform-engineer` (Freya Lindgren). The room's sharpest recurring job outside the core gate procedure, and the room's own steel rule (named explicitly in `company/nexus/gates.yaml`'s Gate-4 artifact list): mapping every network and platform-channel failure to a named, typed `ApiException` subtype so nothing fails silently on the client. A network call that isn't wrapped this way isn't finished, whatever else it does correctly.

## When to run this

Any time `mob-flutter-engineer` adds a new datasource that makes a network call, `mob-platform-engineer` bridges a new `MethodChannel`/`EventChannel`, or a Gate-5 finding traces a swallowed exception, an unhandled crash, or a generic "something went wrong" error message back to this room.

## Steps

### 1. Ask the question before writing a single line
"What can actually fail here, and what does the caller need to know to react correctly?" A timeout is not the same failure as a 401, which is not the same failure as a 422 with field-level validation errors, which is not the same failure as a 500. A generic `catch (e)` treats all four the same — which means the Bloc layer, and eventually the user, can't react correctly to any of them.

### 2. Design or extend the `ApiException` hierarchy — never invent a one-off
```dart
sealed class ApiException implements Exception {
  final String message;
  const ApiException(this.message);
}

class NetworkTimeoutException extends ApiException {
  const NetworkTimeoutException() : super('Request timed out');
}

class UnauthorizedException extends ApiException {
  const UnauthorizedException() : super('Session expired or invalid');
}

class ValidationException extends ApiException {
  final Map<String, List<String>> fieldErrors;   // shape matches the frozen OpenAPI 422 envelope
  const ValidationException(this.fieldErrors) : super('Validation failed');
}

class ServerErrorException extends ApiException {
  final int statusCode;
  const ServerErrorException(this.statusCode) : super('Server error');
}

class UnknownApiException extends ApiException {
  const UnknownApiException(super.message);   // explicit, logged last resort — never silent
}
```
Check the existing hierarchy first (`grep -rn "extends ApiException" lib/`) before adding a subtype — a new subtype is a deliberate design decision, not a default reflex for every new endpoint.

### 3. Wrap every network client call at the interceptor/datasource boundary
```dart
try {
  final response = await dio.get(path);
  return ResponseDto.fromJson(response.data);
} on DioException catch (e) {
  throw switch (e.type) {
    DioExceptionType.connectionTimeout ||
    DioExceptionType.receiveTimeout => const NetworkTimeoutException(),
    DioExceptionType.badResponse => _mapStatusCode(e.response!),
    _ => UnknownApiException(e.message ?? 'Unknown network failure'),
  };
}
```
Never a bare `catch (e) { return null; }` or `catch (e) { print(e); }` — every catch either maps into the hierarchy or is a defect, not a shortcut.

### 4. Confirm the 422 shape matches the frozen contract exactly
```bash
grep -n "422" docs/PRJ-XXXX_OpenAPI.yaml
```
`ValidationException`'s `fieldErrors` shape must byte-match what `bck-api-engineer` actually returns — confirmed against the frozen `OpenAPI.yaml`, never guessed from a "probably looks like this" assumption.

### 5. Map every platform-channel failure the same way
```dart
try {
  final result = await _channel.invokeMethod('getSecureValue', {'key': key});
  return result as String?;
} on PlatformException catch (e) {
  throw switch (e.code) {
    'UNAVAILABLE' => const PlatformCapabilityUnavailableException(),
    'PERMISSION_DENIED' => const PermissionDeniedException(),
    _ => UnknownApiException(e.message ?? 'Unknown platform failure'),
  };
}
```
Document each channel method's contract (arguments, return shape, the specific native-side error codes it can throw) in a comment block directly above the Dart-side call — the native implementation and the Dart mapping are read together, not assumed to agree.

### 6. Configure a timeout on every network call — no exceptions
```dart
final dio = Dio(BaseOptions(
  connectTimeout: const Duration(seconds: 10),
  receiveTimeout: const Duration(seconds: 15),
));
```
A network call with no configured timeout is a hang waiting to happen, not a defect deferred — every client instance sets one explicitly.

### 7. Write the "nothing swallowed" test as the PRIMARY test case
```bash
# example shape — adapt to the project's test framework
flutter test --plain-name "maps every DioExceptionType to a typed ApiException"
```
Assert every `DioExceptionType` value and every documented `PlatformException` code maps to a named subtype, never falls through to a silently-discarded catch. A datasource with a happy-path test and no exception-mapping test has not demonstrated the room's steel rule, only that the happy path works.

### 8. Mechanically confirm no unmapped catch blocks remain
```bash
python3 company/os/toolkit/ceo/sofi_scan.py search "catch (e)" --prj PRJ-XXXX --md
```
Every hit gets inspected — a `catch (e)` that immediately re-throws a typed `ApiException` is fine; a `catch (e)` that swallows, prints, or returns `null` silently is not. This grep is the mechanical half of the room's steel rule, run before `mob-lead`'s review pass spends model tokens re-deriving the same list by eye.

## Worked example (shape only)

```
Call: GET /wallet/balance
Failure modes (from OpenAPI.yaml): 401 (expired session), 404 (wallet not found), 500 (server error), timeout.
Mapping: 401 -> UnauthorizedException, 404 -> ServerErrorException(404) [or a dedicated NotFoundException if this recurs],
         500 -> ServerErrorException(500), timeout -> NetworkTimeoutException.
Bloc reaction: UnauthorizedException -> trigger re-auth flow; NetworkTimeoutException -> show retry affordance;
               ServerErrorException -> show generic error state with a support reference; never the same generic message for all four.
Test: BalanceDatasourceMapsEveryFailureMode — asserts each simulated DioException/status code produces the expected typed subtype.
```

## Rules

- Never write a network or platform-channel call's `try` before deciding what its `catch` maps into — that decision IS the design, not an afterthought.
- Never invent a one-off exception type without checking the existing hierarchy first — a proliferating set of near-duplicate subtypes is as bad as no typing at all.
- Never ship a network call with no configured timeout.
- Never store a credential recovered from a network response or a platform channel outside secure storage (Keychain/Keystore) while designing this layer — the two disciplines meet at exactly this boundary.
- The "nothing swallowed" test and the `sofi_scan.py search "catch (e)"` sweep are both mandatory, not optional, for every datasource and platform-channel bridge this room ships — `mob-lead`'s review checks for both explicitly as part of the room's Gate-4 bar.
- Pairs with the core `gate-4-build-procedure.md` (step 4 dispatches this playbook's owner) and `mob-state-engineer`'s explicit `error` state design (the two roles co-own what a caught `ApiException` actually renders as on screen).
