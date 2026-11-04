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


## Layout qualification, version 0.6

The previous weighted trackpad consumed all height on keyboard-hidden screens,
creating an excessively tall portrait touchpad and obscuring controls behind
the IME. PocketBoard now limits the touchpad to a **landscape aspect ratio**
(about 1.85:1), computes its height from the actual remaining visible region,
and explicitly accounts for Android's keyboard insets on edge-to-edge Android.
Unused space is deliberately left charcoal-colored. Every shortcut is a
single-line, width-flexible control with adaptive text sizing. The action bar
remains above the IME rather than relying on scrolling.

**Acceptance requirement:** With Gboard open on Pixel 6 Pro, every row must be
visible and tappable, the touchpad must remain landscape, and no control label
may be clipped. CI compilation alone does not prove the real-device layout.


## PocketBoard 0.7 colorful UI

Implements the approved dark, playful mockup as native Android UI:
the rainbow keyboard logo and multicolored wordmark, violet Discover pill,
green connected-status pill, wide rainbow trackpad with cursor ornament,
indigo input surface with a keyboard/voice shortcut, and 14 gradient-colored
action tiles with large icon glyphs and compact labels. Every tile still
dispatches the original remote command; the microphone affordance opens the
system keyboard where the existing IME can provide dictation.

The keyboard is the lower half of the intended layout and is supplied by
the user's Android IME, not drawn by PocketBoard. The touchpad height is
capped, all three shortcut rows are reserved before it expands, and
real-device keyboard-open acceptance remains required. Visual smoke tests
should inspect short labels, small portrait widths, Gboard appearance,
and alternative IME heights.

## PocketBoard 0.8 media and app-switcher controls

The first shortcut row now groups **volume down, volume up, mute, previous track, play/pause, and next track**, using Windows virtual media keys that target the active system media session. The second row groups **Apps, Next app, and Choose** for the existing Alt+Tab workflow. Copy/Paste and navigation remain in their own compact rows. The fourth row is budgeted above the Android IME, and the rainbow touchpad yields space first. The Windows tray receiver must be updated with this release for media keys to work.

## PocketBoard 0.9 system-bar and flat-UI fixes

- Android 15+ edge-to-edge insets now reserve the real **top status/cutout
  inset**, so the header no longer overlaps the Android clock and indicators.
  The IME/navigation inset is still reserved at the bottom.
- All interactive colored buttons are **solid flat fills**, with no gradient
  or elevation. Press feedback remains a lightweight ripple.
- The six media keys and four bottom navigation keys show **icons only**;
  their full action names remain available to TalkBack.
- The seven touchpad stripes extend beyond the clipped rounded edges so no
  black/charcoal triangles appear at the left or right.
- This remains an Android-only change. The Windows receiver does not need
  updating. Confirm the status-bar clearance and Gboard-fit on hardware.

## PocketBoard 0.10 touchpad calibration

On the Pixel 6 Pro, the user reports a complete horizontal thumb swipe only
moved the Windows cursor one-third of the display width. The touchpad's
relative-motion gain is now **4.5** instead of **1.5** (3×), so the same
physical swipe should cover approximately the full Windows display.
Fractional movement is carried across gesture events to preserve delicate
slow movements. The existing ±300 pixel per-event safety clamp remains.
This is a calibration prediction; real-device testing should verify whether
Windows mouse acceleration changes the observed response.

## PocketBoard 0.11 vector symbol system

Editable standalone SVGs are in assets/symbols/ with matching Android
VectorDrawables in android/app/src/main/res/drawable/pb_*.xml.
All shortcut buttons use flat circular colors. Media navigation uses
bar-and-triangle symbols, Copy uses two overlapping sheets, Select All & Copy
adds the checkmark, Paste adds a plus, and Tab uses the distinctive
shaft-and-arrow symbol. Esc is the literal label Esc.

The entry field includes independent Clear (white disc/black X) and
Microphone controls. Clearing resets the Android edit buffer only.
Play/Pause flips its icon after each local press, initially displaying Play,
without querying remote playback state. System media control continues to
send the same Windows play/pause command. TalkBack descriptions remain.

## PocketBoard 0.12 button silhouette

Colored circular button backgrounds are now **1:1.08 width-to-height vertical ovals**:
49 × 53 dp on shortcut rows and 38 × 41 dp inside the input field.
SVG symbols and text glyphs remain rendered within centered square viewports
and are never stretched. Existing row heights stay unchanged, preserving the
keyboard-open layout budget.

## PocketBoard 0.13 shape and volume symbols

The 1:1.08 oval experiment is superseded by a **1:1 superellipse**
(exponent 2.55), a subtle circle-to-squircle transformation with flatter
sides, without stretching the symbols. Editable button silhouette SVG is
in assets/symbols/button_squircle.svg with a matching native vector drawable.

The three volume actions now use the same white speaker silhouette and
right-hand X, + or minus marks from the supplied reference. Three new
SVGs and matching Android vector drawables implement them. Colored button
backgrounds, sizing, positions, connection behavior and the Windows
companion remain unchanged.

## PocketBoard 0.14 clipboard icon fidelity and grouped controls

All clipboard controls now share an identical two-sheet composition:
one rounded rear-sheet outline and one rounded foreground sheet.
- Copy: the two sheets only.
- Select All & Copy: the same sheets, with a dark checkmark on the front.
- Paste: the same sheets, with a dark plus sign on the front.

Matching SVGs and Android vector resources are updated in place.
The three app-switcher controls and three clipboard controls occupy a
single six-button row, in that order. The media and keyboard rows retain
their controls and colors. Removing the extra row frees 56dp vertically,
which remains available to the touchpad/keyboard-first layout.
This is Android-only; the Windows receiver is unchanged.

## PocketBoard 0.15 compact controls

One-row icon, Connected checkmark and magnifying-glass discovery. Blank 16dp spacer below trackpad retained. Clear and microphone backgrounds 34dp with unchanged 22dp glyphs inside 40dp slots. Apps, Choose, blank, Copy, All+Copy, Paste. Bottom row blank, Esc, Tab, Enter; Backspace removed. Native vector icons added. Windows protocol unchanged.

## PocketBoard 0.16: icon and alignment refinements

The final controls row now uses six equal slots, with three blanks followed by
Esc, Tab, and Enter in slots 4-6. The Apps action uses the white four-panel
reference shape, stored in assets/symbols/apps.svg and pb_apps.xml.
The Choose and Connected indicator share the same heavier checkmark vector,
with less rounded corners and unchanged overall glyph footprint.

The trackpad maximum height increases by 17% from 135 dp to 158 dp and its
initial height from 125 dp to 146 dp. The responsive available-space limit
remains in force so Gboard can still occupy the bottom of the screen.
The input field stays 41 dp high; its bottom-to-first-row gap is now
18 dp, matching the 18 dp reserved gap from touchpad to input field.
No Windows receiver changes are necessary.
