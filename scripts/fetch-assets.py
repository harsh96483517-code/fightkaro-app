"""Top up the bundled web game with the binary assets the mirror did not carry.

The published `www/` folder holds the HTML/CSS/JS shell, the fighter portraits and
the fonts, but the 3D fighter models (`models/*.glb`) and the soundtrack / SFX
(`assets/*.mp3`) live only on the live site. GitHub Actions runners have open
internet, so CI pulls exactly those files here, right before the web assets are
synced into the Android project.

Every path is derived from the game's own JavaScript, so the list stays correct if
the build hashes change. That includes the Draco decoder (`.wasm` + `.js`) the 3D
engine needs before it can decompress the fighter models. Files that the server does not have (a few internal SFX
names are only fallbacks) are skipped, and the script always exits 0 — a missing
sound must never fail the APK build.
"""
import glob
import os
import re
import sys
import urllib.error
import urllib.request

BASE = "https://fightkaro.com/"
WWW = "www"
TIMEOUT = 60
UA = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Mobile Safari/537.36"

ASSET_EXT = r"(?:glb|gltf|mp3|ogg|wav|m4a|ktx2|hdr|bin|webp|jpg|jpeg|wasm|js)"
PATTERN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./-]*\." + ASSET_EXT)
WANTED_PREFIX = ("assets/", "models/", "audio/", "sfx/", "sounds/")

FIGHTERS = ["modi", "rahul", "didi", "trump", "yogi", "nitin", "mbapu"]


def referenced_paths():
    blob = []
    for path in glob.glob(os.path.join(WWW, "assets", "*.js")) + [os.path.join(WWW, "index.html")]:
        if os.path.exists(path):
            blob.append(open(path, encoding="utf-8", errors="ignore").read())
    found = set()
    for match in PATTERN.finditer("\n".join(blob)):
        candidate = match.group(0).lstrip("/")
        if candidate.startswith(WANTED_PREFIX):
            found.add(candidate)
    # the game builds the mobile model URLs at runtime, so they never appear literally
    for name in FIGHTERS:
        found.add("models/mobile/%s.glb" % name)
    return found


def download(rel):
    target = os.path.join(WWW, rel)
    if os.path.exists(target) and os.path.getsize(target) > 0:
        return "have"
    os.makedirs(os.path.dirname(target), exist_ok=True)
    req = urllib.request.Request(BASE + rel, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return "skip"
            body = resp.read()
    except urllib.error.HTTPError as exc:
        return "404" if exc.code == 404 else "http %s" % exc.code
    except Exception as exc:  # noqa: BLE001 - network hiccup must not fail the build
        return "error: %s" % exc.__class__.__name__
    if not body:
        return "empty"
    with open(target, "wb") as fh:
        fh.write(body)
    return "ok"


def main():
    paths = sorted(referenced_paths())
    tally = {"ok": 0, "have": 0, "skip": 0, "404": 0, "empty": 0}
    problems = []
    total = 0
    for rel in paths:
        result = download(rel)
        tally[result] = tally.get(result, 0) + 1
        if result not in tally:
            problems.append("%s -> %s" % (rel, result))
        if result == "ok":
            total += os.path.getsize(os.path.join(WWW, rel))

    print("asset paths considered:", len(paths))
    for key, count in sorted(tally.items()):
        print("  %-8s %d" % (key, count))
    print("downloaded: %.1f MB" % (total / (1024 * 1024)))
    if problems:
        print("non-fatal problems:")
        for line in problems[:20]:
            print("  " + line)

    models = glob.glob(os.path.join(WWW, "models", "**", "*.glb"), recursive=True)
    audio = glob.glob(os.path.join(WWW, "assets", "**", "*.mp3"), recursive=True)
    print("models on disk:", len(models), "audio files on disk:", len(audio))
    if not models:
        sys.exit("no fighter models were downloaded - the APK would not be playable")


if __name__ == "__main__":
    main()
