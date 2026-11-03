"""Tune the Capacitor Android project for a landscape, fullscreen arcade game.

`npx cap add android` regenerates a stock project, so CI runs this script right
after that step. It:

  1. locks the activity to landscape and asks for a larger heap,
  2. replaces MainActivity with an immersive fullscreen + keep-screen-on build,
  3. repaints every launcher icon density from www/icon-192.png.
"""
import io
import os
import sys

from PIL import Image

APP_ID = "com.harsh.fightkaro"
MANIFEST = "android/app/src/main/AndroidManifest.xml"
ACTIVITY = "android/app/src/main/java/" + APP_ID.replace(".", "/") + "/MainActivity.java"

MAIN_ACTIVITY = """package %s;

import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        immersive();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            immersive();
        }
    }

    @SuppressWarnings("deprecation")
    private void immersive() {
        View decor = getWindow().getDecorView();
        decor.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                        | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
    }
}
""" % APP_ID


def patch_manifest():
    try:
        src = io.open(MANIFEST, encoding="utf-8").read()
    except FileNotFoundError:
        sys.exit("AndroidManifest.xml missing - run `npx cap add android` first")

    if 'android:screenOrientation' not in src:
        if "<activity" not in src:
            sys.exit("<activity> tag not found in manifest")
        src = src.replace(
            "<activity",
            '<activity\n            android:screenOrientation="sensorLandscape"',
            1,
        )

    if "android:largeHeap" not in src:
        src = src.replace("<application", '<application\n        android:largeHeap="true"', 1)

    io.open(MANIFEST, "w", encoding="utf-8").write(src)
    print("manifest patched: landscape + largeHeap")


def patch_activity():
    if not os.path.isdir(os.path.dirname(ACTIVITY)):
        sys.exit("MainActivity package directory not found: " + ACTIVITY)
    io.open(ACTIVITY, "w", encoding="utf-8").write(MAIN_ACTIVITY)
    print("MainActivity replaced with immersive fullscreen build")


DENSITIES = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192,
}
FOREGROUND = {
    "mdpi": 108,
    "hdpi": 162,
    "xhdpi": 216,
    "xxhdpi": 324,
    "xxxhdpi": 432,
}


def patch_icons():
    source = Image.open("www/icon-192.png").convert("RGBA")
    changed = 0
    for density, size in DENSITIES.items():
        folder = "android/app/src/main/res/mipmap-" + density
        if not os.path.isdir(folder):
            continue
        big = source.resize((size, size), Image.LANCZOS)
        for name in ("ic_launcher.png", "ic_launcher_round.png"):
            big.save(os.path.join(folder, name))
            changed += 1
        fg = source.resize((FOREGROUND[density], FOREGROUND[density]), Image.LANCZOS)
        fg.save(os.path.join(folder, "ic_launcher_foreground.png"))
        changed += 1
    print("launcher icons repainted:", changed, "files")


if __name__ == "__main__":
    patch_manifest()
    patch_activity()
    patch_icons()
