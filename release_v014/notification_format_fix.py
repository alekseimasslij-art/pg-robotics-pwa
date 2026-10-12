#!/usr/bin/env python3
"""iOS Web Push content: headline as title, no duplicated brand or placeholder body.

Note: iOS itself always adds "from <Home Screen app name>" for PWA Web Push.
This UI chrome cannot be removed by JavaScript, a server, or an icon update.
"""
from pathlib import Path
import re
import sys

sw = Path("build/web/pg-pwa-sw.js")
if not sw.is_file():
    sys.exit("Web Push SW was not generated")
source = sw.read_text(encoding="utf-8")
before = "body: data.body || 'Нова публікація'"
after = "body: data.body || ''"
if source.count(before) != 1:
    sys.exit("Unexpected Web Push handler; not publishing unverified changes")
source = source.replace(before, after, 1)
source = source.replace("data.title || 'PG Robotics'", "data.title || 'Нова публікація'", 1)
# A new cache namespace ensures previously installed devices use the current worker.
source, count = re.subn(r"(const CACHE = 'pg-robotics-[^']+)'(\s*;)",
                        r"\1-push14'\2", source, count=1)
if count != 1:
    sys.exit("PWA cache version format changed")
sw.write_text(source, encoding="utf-8")
print("Web Push text format fixed for PWA (system 'from' subtitle remains on iOS).")
