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

## PocketBoard 0.17: matched header geometry and balanced vertical rhythm

The rainbow header artwork now uses the same 2.55-exponent superellipse
outline as the main action buttons, with no square black backing. The
40dp-tall app icon, Connected status and Discover button share the same
height; Discover uses the actual action-button squircle, and Connected
uses a less pill-like 13dp corner radius appropriate to its wider shape.

The trackpad is visually centered between the 41dp header and the
41dp text field with 18dp on each side: 18dp above the pad, then 2dp
pad margin plus 16dp empty feedback area below. The text field retains
an 18dp gap to the first controls row (15dp plus the row's 3dp margin).
Available-height calculations reserve the updated trackpad margins to
prevent clipping when the software keyboard is present. Touch actions
and Windows receiver behavior are unchanged.

## PocketBoard 0.18: keyboard-first operation

The Android IME opens by default when PocketBoard's window takes focus,
including after returning to the app or dismissing a discovery dialog.
The text field is automatically focused on launch, without tapping it,
and stays editable throughout connection attempts and reconnects.
Typing, voice input and text corrections use the existing text-change
protocol; only connected sessions can transmit input, so disconnected
keystrokes are local and are not queued or replayed after reconnection.
Touchpad and shortcut-button touches do not request keyboard focus.
Android still controls whether the IME is actually displayed (for example,
when a hardware keyboard is active or the user explicitly dismisses it).
No change to Windows input protocol or pairing security is required.

## PocketBoard 1.0: centered connected indicator

The connected status displays its existing bold vector checkmark immediately
after the word "Connected" as an inline text span. The label and symbol are
centered together within the unchanged 40dp green squircle bar rather than
separating the checkmark to the far right edge. Accessibility announces the
status as "Connected". All other screen controls, spacing, networking and
keyboard behaviour remain unchanged. Version 1.0 uses Android versionCode 19
to upgrade cleanly over previous 0.x builds.

## PocketBoard 1.0.1: source-traced adaptive launcher art

The launcher icon now consists of independently reusable SVG artwork in
`assets/launcher/`: the closely cropped white keyboard, the source-reference
squircle mask, a circular mask and a square seven-band rainbow background.
Circle/squircle composite previews are supplied. The in-app header now uses
that same traced keyboard with the reference squircle outline.

Android 8+ launchers apply the user's chosen icon mask directly to separate
rainbow background and white keyboard foreground VectorDrawable layers. Both
standard and round launcher icon references use the adaptive composition,
which avoids the earlier black square and double-cropping. Launcher-specific
mask shapes are controlled by Android, not selected in application code.
See `assets/launcher/README.md` for provenance and visual acceptance checks.
Android versionCode 20/versionName 1.0.1 makes this install an upgrade over 1.0.
No Windows receiver or network protocol changes.

## PocketBoard 1.0.2: canonical traced art shipped

**The UI now uses the reference-traced buttons and glyphs**, with the source files in `assets/button-silhouettes/` and `assets/button-symbols/` and exact path-data matches in Android VectorDrawables. Connected uses the specially refined `connected-pill.svg`, with the checkmark centered alongside the text. The reference Search, Clear and Mic contours replace the generic header/entry squircle. Media controls use the smaller reference family (45dp); utility tiles use 49dp and navigation tiles 51dp within the existing 53dp rows. Play/Pause retains one fixed shape and switches only its symbol on presses, without pretending to know remote playback state. Window-overlay icons represent Copy, Select All & Copy, and Paste; commands and their TalkBack descriptions are unchanged.

All runtime UI colours are drawn from `PocketBoardPalette.kt`. The launcher/header and touchpad's seven stripes now use canonical hues; original launcher keyboard geometry and adaptive masking remain intact. White reference SVG source traces are preserved exactly, while foreground control glyphs render in canonical cream. An offline CI test, `android/verify_canonical_art.py`, locks palette values, validates SVG/vector contour identity, and blocks accidental unapproved runtime colours. Original raster inputs are in `assets/references/`, the supplied font is in `assets/fonts/` (with the runtime copy under `res/font/`), and outgoing artwork is quarantined in `assets/retired-art/`. The prior generic squircle, coarse Connected outline, unused Backspace icon and obsolete launcher resource are not part of the shipped drawable set.

Android versionCode 21/versionName 1.0.2. Windows protocol, receiver and pairing unchanged. **Physical-device acceptance remains outstanding**: inspect Gboard-open 320/412dp layouts, finger targets, reference-contour fidelity, the connected checkmark baseline and color contrast. The original Connected artwork is green with cream lettering, which may have limited accessibility contrast. CI compilation and source-contract validation cannot substitute for on-device visual checks.


## Button silhouette correction (1.0.2 artwork hotfix)

The first 1.0.2 button traces were internally consistent but visually faceted
because excessive contour simplification generated polygons. All sixteen
visible buttons have now been independently retraced as smooth Bézier contours.
The detailed Connected shape, foreground symbols, canonical palette, fonts,
launcher and remote-control behavior are unchanged. The CI verification now
checks both source-to-Android exact path identity and cubic outline presence.
Physical-device visual acceptance with Gboard remains necessary.

## PocketBoard 1.0.3: header typography, controls and rainbow accessibility

All Connected-pill status labels are uppercase at **16sp** (previously 13sp).
The lettering is bottom-anchored with a 10dp inset in the unchanged 40dp
pill, so enlargement grows upward, keeping the lower edge in place.
The input field is **13sp** (previously 16sp), with a 50%-opaque placeholder.
Clear and Microphone tiles and glyphs shrink by **10%**, retaining their
original 40×41dp action slots and the 41dp text-bar height.

The reference-traced header icon has transparent inset; optical scale
1.09× horizontally / 1.11× vertically equalizes its visible dimensions
with Discover without altering either 40×40dp layout box or the row's
vertical alignment. The button contours and keyboard artwork remain intact.

Yellow `#FFD42A` and deeper emerald green `#007E59` replace the
ambiguous old adjacent rainbow bands across Android, SVG previews,
the launcher and all canonical UI uses. Their computed luminance
contrast improves from 1.32:1 to 3.56:1; cream on status-green is 4.66:1.
The original raster references are preserved unchanged.
Source-contract checks validate these values. Physical-device inspection,
colour discrimination acceptance and Gboard-open measurements still
remain required. versionCode 22 / versionName 1.0.3; Windows protocol,
companion and pairing unchanged.

## PocketBoard 1.0.4: equal-column control grid and two-finger trackpad scroll

The three control rows are now an invisible equal-width A/B grid. Both columns
have the same width and all three rows share 53dp height + 3dp top spacing,
preserving the Gboard-open available-height calculation. Groups are
**edge-justified**: A left, B right; all visible neighbors use 6dp separation,
including the narrower media/volume buttons, rather than oversized equal
slots. Tiles preserve their native, imperfect silhouette proportions and their
previous action colours. At narrow widths button faces shrink only as needed
to fit the half-column without clipping.

| Row | Column A (left edge) | Column B (right edge) |
| --- | --- | --- |
| 1 | Copy, Paste, Select All & Copy | Previous track, Play/Pause, Next track |
| 2 | Alt-Tab (Apps), Select (Choose) | Volume Down, Volume Up, Mute |
| 3 | Empty | Tab, Enter, Esc |

A two-finger gesture now cancels single-finger recognition and converts
centroid movement into bounded natural vertical/horizontal wheel steps
(28dp travel per notch; max four notches per event). Sub-notch movement is
carried forward. Finger identity is tracked across index reorderings, and
lifting one finger doesn't resume cursor motion or synthesize a tap until
all fingers are up. One-finger pointer, tap/double-tap and long-press
right-click behavior stays intact.

**The Windows companion must also be upgraded.** Its authenticated protocol
now accepts `mouse_scroll` with signed integer `vertical` and `horizontal`
steps in [-4, 4], injects Win32 WHEEL/HWHEEL as 120-unit detents, and ignores
missing/invalid inputs. An older receiver will simply ignore scroll packets;
pointer and other commands continue working. Existing pairing/security and
the command queue are unchanged.

Version code 23 / version 1.0.4. CI Windows and Android builds plus the
canonical-art contract are required. Device acceptance still needs the
320dp and 412dp / Gboard-open layouts, 2-finger vertical and horizontal
scroll, accidental-click suppression and gesture reversal checked on hardware.
