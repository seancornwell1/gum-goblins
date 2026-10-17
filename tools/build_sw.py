#!/usr/bin/env python3
"""Writes the offline file list and a content-hash version into sw.js.

Run after changing any asset or code:  python3 tools/build_sw.py
"""
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCLUDE = ["index.html", "manifest.webmanifest", "css", "js", "assets", "vendor"]
SKIP_EXT = {".map", ".md"}


def main():
    files = []
    for entry in INCLUDE:
        p = os.path.join(ROOT, entry)
        if os.path.isfile(p):
            files.append(entry)
            continue
        for d, _, names in os.walk(p):
            for n in sorted(names):
                if os.path.splitext(n)[1] in SKIP_EXT:
                    continue
                files.append(os.path.relpath(os.path.join(d, n), ROOT).replace(os.sep, "/"))
    files.sort()
    h = hashlib.sha256()
    for f in files:
        with open(os.path.join(ROOT, f), "rb") as fh:
            h.update(f.encode() + fh.read())
    version = h.hexdigest()[:12]
    sw_path = os.path.join(ROOT, "sw.js")
    src = open(sw_path).read()
    src = re.sub(r"const VERSION = '[^']*';", f"const VERSION = '{version}';", src)
    src = re.sub(r"const FILES = \[[^\]]*\];", "const FILES = " + json.dumps(files, indent=0).replace("\n", "\n  ")[:-1] + "];", src, flags=re.S)
    open(sw_path, "w").write(src)
    print(f"sw.js: {len(files)} files, version {version}")


if __name__ == "__main__":
    main()
