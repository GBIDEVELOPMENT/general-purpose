# Diagnose Windows On-Screen Keyboard (OSK) input blocking

Reported on November 6, 2026: while Windows `osk.exe` is open, the Android
PocketBoard phone reports connected but **both** Windows mouse movement and key
input cease responding. Minimizing OSK immediately restores control, without a
reconnect. This is an observed symptom, not yet a verified UIPI failure.

The Windows receiver now exposes **tray > Input diagnostics**. It maintains
process-local aggregate counts of protocol commands received, `SendInput`
attempts, failed `SendInput` calls and the last failed call's local timestamp,
Win32 error and foreground process name. It deliberately does **not** capture
typed text, keys, token values, client addresses or message payloads. Counters
reset when the receiver process restarts.

## Reproduction and interpretation

1. Run the updated Windows receiver; connect the existing Android app.
2. With OSK minimized, move the phone touchpad and open **Input diagnostics**.
   Record the three counts.
3. Make OSK visible; attempt mouse movement several times on the phone.
   Use the receiver's tray **Input diagnostics** to compare counts.
4. Minimize OSK, send a few further moves, and compare the counts again.

Interpretation:
- **Received commands stop increasing**: investigate phone-to-receiver delivery,
  receive-loop blockage or scheduling. The phone's connected indicator alone does
  not establish command delivery.
- **Received commands increase, SendInput calls do not**: inspect dispatch or
  command processing before the injection API.
- **SendInput failures increase**: Windows rejects or cannot deliver injections.
  Last Win32 error is helpful if nonzero, but UI privilege isolation (UIPI) can
  block calls without a useful error.
- **SendInput calls succeed but the cursor is stationary**: success only means
  events were inserted into the input stream. Investigate desktop/session,
  accessibility input routing, focus and interactions with OSK; do not infer
  correct delivery based on `SendInput` return values alone.

## Safety constraints

Do not grant blanket administrator privileges, disable Windows security
boundaries, automate closing OSK, or synthesize unsolicited input as a probe.
Any workaround should follow a reproducible diagnosis on the actual PC. This
change is receiver-only: the Android APK, pairing tokens, certificate pinning
and transport format are unchanged.
