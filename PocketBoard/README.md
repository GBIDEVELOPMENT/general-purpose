# PocketBoard

Direct Android keyboard and touchpad remote for a Windows PC, with no account, cloud or intermediary.

## Version 0.3

- Dark charcoal, keyboard-first screen: compact status, **seven slightly angled red, orange, yellow, green, blue, indigo, violet touchpad stripes**, type/dictate field and three control rows. Android's installed IME opens automatically after connecting, and the layout resizes to keep all controls visible above it.
- Touchpad supports pointer movement, tap, double-tap and long-press right-click.
- Volume down/up/mute, copy, select-all-and-copy, paste, Esc, Tab, Enter and Backspace.
- **Apps** opens Windows Alt+Tab and keeps Alt held; **Next** advances; **Choose** releases Alt to switch. To prevent a stuck Alt key, the receiver releases Alt automatically after 12 seconds without another Apps/Next action.
- **Discover** scans the current Wi-Fi using UDP port 38477 and lists PocketBoard Windows receivers. Choose one, and the app enrolls with no code or PC approval. The stored token and pinned TLS certificate are reused on future reconnections. Saved connections still auto-reconnect.
- Tray icon continues to offer Pause/Resume and revoke all known phone tokens. Windows executable starts at sign-in via its startup shortcut.

## Windows installation

Publish with `dotnet publish windows/PocketBoard.Windows.csproj -c Release -r win-x64 -o out/windows`. On the HP, stop the prior PocketBoard tray process before replacing the EXE, then restart it. The `windows/install.ps1` helper installs user startup and, when elevated, a private-network/local-subnet-only inbound TCP rule on port **38476** and UDP discovery on **38477**.

For an existing install, run these two commands in elevated PowerShell on trusted home Wi-Fi:

```powershell
New-NetFirewallRule -DisplayName 'PocketBoard discovery' -Direction Inbound -Action Allow -Protocol UDP -LocalPort 38477 -Profile Private -RemoteAddress LocalSubnet
```

## Security implications

**Automatic enrollment intentionally trades first-connection authentication for convenience.** Any device that can reach the receiver from its local IPv4 subnet may enroll and inject keyboard/mouse input while receiving is enabled, with no Windows confirmation. This can include untrusted guests on the same Wi-Fi. Do not use this mode on shared/untrusted networks. Pause receiving from the tray when not in use, use a private trusted Wi-Fi and never forward these ports on the router. Network restrictions are a practical boundary, not a replacement for device authentication.

Messages use TLS; the Android client pins the server certificate after first enrollment (trust on first use). Discovery responses are unencrypted, so malicious LAN devices can spoof discovery or intercept an initial enrollment. A previously pinned host certificate change is rejected. Unpairing/revocation clears tokens, but because code-free enrollment remains enabled, another device on the subnet could immediately enroll again.

The receiver requires an awake, signed-in interactive desktop. Secure Windows login and UAC screens are unsupported. Android voice dictation uses the existing keyboard's speech features. On-device APK and visual acceptance are still pending; CI compilation alone cannot establish layout behavior across every keyboard.

## Build

- Windows: .NET 8 Windows Desktop Runtime on host, .NET 8 SDK to compile.
- Android: JDK 17, Android SDK 35, Gradle 8.11.1; CI produces a debug APK via GitHub Actions.


## Renaming compatibility (0.5)

The project and user-visible app are now **PocketBoard**. The Android package ID
`dev.pocketkeyboard`, Kotlin namespace, discovery wire format, and Windows
`%LOCALAPPDATA%\PocketKeyboard` authentication storage remain unchanged.
This intentionally preserves an in-place Android upgrade, enrolled phone tokens,
and the pinned Windows certificate. The Windows output executable is now
`PocketBoard.Windows.exe`, and the install script replaces the legacy startup
shortcut with `PocketBoard.lnk`.

GitHub Actions publishes `PocketBoard-0.5-debug.apk` inside the
`PocketBoard-Android-debug` artifact. The Gradle packaging task names
distributable APK files using `versionName`; update versionName for future builds.
