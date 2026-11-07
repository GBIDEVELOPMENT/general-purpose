# Font Shelf Android signing and upgrades

Font Shelf's debug APKs are useful for testing, but **installed fonts live in the Android app's private WebView/IndexedDB data**. Android only permits an in-place app upgrade when the application ID and signing certificate match, and the new version code is higher.

## What CI does now

- Every `Font Shelf Android debug APK` workflow run assigns its increasing `GITHUB_RUN_NUMBER` as the APK's `versionCode`.
- It checks the version code and verifies the APK's v2 signature and SHA-256 certificate fingerprint before uploading the APK.
- On a **push to main only**, CI can restore a repository-configured stable *debug* keystore using the `FONTSHELF_DEBUG_KEYSTORE_BASE64` Actions secret.
- If that secret is absent, a GitHub runner generates its own debug certificate, so the build is a **disposable preview**. Installing a later runner-signed APK over it may fail with an incompatible-signature error. Uninstalling the app clears its private font library.

## One-time owner action before daily use

Generate a dedicated Android **debug** signing key on a trusted computer. Example (JDK `keytool`):

```sh
keytool -genkeypair -v \
  -keystore fontshelf-debug.keystore \
  -alias androiddebugkey -keyalg RSA -keysize 2048 \
  -validity 10000 -storepass android -keypass android \
  -dname "CN=Font Shelf Debug,O=Local Development,C=CA"
```

1. Keep `fontshelf-debug.keystore` in a secure offline backup. Never commit it, upload it as a public artifact, or paste its base64 value into chat.
2. Encode the full keystore as base64, then add it as repository Actions secret **`FONTSHELF_DEBUG_KEYSTORE_BASE64`** in GitHub: `GBIDEVELOPMENT/general-purpose` → Settings → Secrets and variables → Actions.
3. Trigger the **Font Shelf Android debug APK** workflow on `main`; inspect its signing step and certificate SHA-256 in the logs. Subsequent main builds using the same secret and increasing version code are eligible for in-place upgrades.
4. If the first installed APK was signed with a different certificate, there is **no supported in-place upgrade from that APK**. Preserve data externally before uninstalling; Font Shelf does not yet offer built-in library export/backup. To avoid loss, install only the stable-key-signed builds once the secret is configured.

The default debug alias and passwords here are deliberately conventional and **not a production release-signing scheme**. For public distribution, use a separate private release keystore, a distinct properly protected signing workflow and a supported backup/export process.

## Qualification status

- [Build, source tests and packaged font assets](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/42346040564): passed.
- [Installed Android 35 WebView test](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/42346736856): passed once. It exercised offline font parsing and ZIP, saved/hid/restored a font, Activity recreation, family and individual tags, and a named list.
- Still required before daily-use qualification: physical-device picker imports, broad font/ZIP fixtures, storage-quota failure and recovery, app upgrade on the *same* signing certificate, and user-controlled export/backup.
