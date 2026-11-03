# FightKaro — Android app

An offline Android build of the **FightKaro / Sansad Showdown** browser fighter. The web game is
bundled inside the APK, so it runs without internet: pick your neta, choose a stage and a CPU
difficulty, and fight in landscape.

## What is inside

- `www/` — the complete game bundle (HTML, JS, CSS, fighter portraits, fonts), with the Google
  Fonts and the network-only extras pulled local so the app works with no connection.
- `capacitor.config.json` — app id `com.harsh.fightkaro`, display name `FightKaro`, web root `www`.
- `scripts/patch-android.py` — post-generate tweaks: landscape lock, immersive fullscreen,
  keep-screen-on, larger heap, and launcher icons generated from the game's own icon.
- `.github/workflows/build-apk.yml` — builds the APK on every push to `main`, uploads it as a
  workflow artifact and attaches it to the `apk-latest` release.

## Get the APK

Every push to `main` builds a fresh APK:

1. **Release (easiest):** open the [releases page](../../releases/tag/apk-latest) and download
   `fightkaro.apk`.
2. **Artifacts:** Actions → *Build APK* → latest run → *Artifacts* → `fightkaro-apk`.

Transfer the APK to the phone, allow "install unknown apps" for your file manager or browser,
and install. Android 6.0 or newer.

The build is debug-signed. To publish on the Play Store you would need your own signing key —
add it as repository secrets and switch the Gradle task to `assembleRelease`.

## Build locally

```bash
npm install
npx cap add android
python3 -m pip install pillow
python3 scripts/patch-android.py
npx cap sync android
cd android && ./gradlew assembleDebug
```

Requires Node 20+, JDK 17 and the Android SDK.

## Controls

Touch: on-screen stick to move, buttons for PUNCH / KICK / GRAB / SUPER. Hold back on the stick
to block, tap up to jump, down to crouch.

## Notes

- Online "play with a friend" is hidden — it needs the game's server, which an offline APK does
  not have. Local play against the CPU is fully available.
- The game itself is a fan-made political parody created by its original authors
  (`fightkaro.com`, `@shivmbuilds`). This repository only repackages the published bundle for
  Android; all game content and characters remain theirs. Do not redistribute commercially
  without their permission.
