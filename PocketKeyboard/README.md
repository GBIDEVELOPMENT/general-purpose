# PocketKeyboard

A local, account-free Android keyboard for your Windows desktop. The Windows host is a single, tray-only .NET 8 application; Android uses the **existing** system IME, including voice dictation.

## How it works

1. Build or download the Windows x64 release and start `PocketKeyboard.Windows.exe` in your signed-in Windows session.
2. In the Windows **notification area** (sometimes behind the ^ overflow arrow), right-click the blue information icon and choose **Pair a phone…**. The pairing window shows local IP addresses, TCP port **38476**, and a six-digit code valid for three minutes.
3. Install the Android APK. Enter the HP's **Wi-Fi** IP (currently `10.0.0.172`, potentially different later), and the code. Tap **Connect**.
4. Focus a normal desktop app on Windows. Type or dictate on your phone. A status banner indicates successful connection. Use **Clear buffer** when starting another text passage; it clears only the Android composition history.
5. The Windows tray menu offers **Pause receiving**, **Resume receiving**, **Forget all paired phones** and **Exit**. Pausing preserves pairing but blocks input.

No intermediary servers, accounts, telemetry, Android accessibility service or keyboard replacement. Traffic uses TLS with a per-host self-signed certificate; pairing issues a random 256-bit secret. Android pins the server certificate after the first successful six-digit pairing. Pair on a trusted LAN; the one-time code is an authentication mechanism, but it does not independently prevent an active on-path relay during initial pairing.

## Build

Windows: `dotnet publish windows/PocketKeyboard.Windows.csproj -c Release -r win-x64 -o out/windows` (requires .NET 8 SDK to build; Windows Desktop Runtime 8 to run). Android: from `android/`, `gradle :app:assembleDebug` with Android SDK 35 and JDK 17. GitHub Actions also builds both.

## Windows startup

After publishing, run `windows/install.ps1` from the folder containing the EXE, or pass `-Executable C:\path\to\PocketKeyboard.Windows.exe`. This adds a **current-user startup shortcut** and, with Administrator approval, a **private/local-subnet-only** Windows Firewall inbound rule for TCP 38476. A startup entry launches the tray app at sign-in, not as a Windows Service (Windows services cannot inject input into the signed-in user's desktop).

## Limitations / safety

- Windows must be awake, signed in and running the tray process. UAC secure desktop and lock screens are intentionally excluded. Elevated targets may refuse input.
- Input is sent to **whatever window has focus**. Avoid passwords and other sensitive fields until verifying the intended target. Pause from the tray to prevent accidental input.
- Android edits are mirrored using Unicode characters and left/right/backspace operations, including most autocorrect and dictation revisions. The remote cursor is assumed to be at the end of the most recently transmitted Android buffer; clicking another Windows location or editing the remote buffer independently can desynchronize the editor.
- Commands queued during disconnection are discarded, never replayed. The connection automatically retries only after previously successful pairing.
- Unicode injection handles printable text. Function keys, shortcuts, mouse controls and clipboard are future work. Some apps and games do not accept injected Unicode.
- Initial version is source-level prototype; APK and Windows runtime acceptance on real devices are pending. Do not treat CI compilation as real-device acceptance.
- The Windows receiver currently listens on all IPv4 interfaces. Configure the inbound firewall rule to **LocalSubnet** only, and do not forward TCP 38476 through your router. On hostile networks, disconnect or pause.
- The Android trust manager accepts a self-signed certificate only long enough to compare its SHA-256 fingerprint with the saved pin, or to establish the initial authenticated pairing. A stolen pairing code during initial connection or compromised paired device requires revoking tokens from Windows tray.

## Roadmap

1. Build and test Windows receiver and Android APK in CI.
2. Install on HP, test typing/voice corrections and reconnection under Gboard on Pixel; verify firewall rule and notifications.
3. Add explicit modifier shortcuts, keyboard layouts, accessibility adjustments, robust selection handling, and input-permission controls only after real-world use establishes need.

Project is isolated from the general-purpose repo's audit and integration machinery.

