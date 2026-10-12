#!/usr/bin/env python3
"""Publish an instant PG Robotics install landing without changing Flutter's Dart app.

Executed after flutter build web and tools/postbuild_pwa.py.
  /index.html: fast install welcome screen for browser visitors
  /app.html: unchanged Flutter app, also PWA start_url
This keeps a single shared iOS/Web Flutter application and preserves its runtime.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import sys

BASE = Path(__file__).resolve().parent.parent
WEB = BASE / "build" / "web"
LANDING = BASE / "deploy" / "install.html"


def main() -> None:
    index = WEB / "index.html"
    app = WEB / "app.html"
    manifest = WEB / "manifest.json"
    worker = WEB / "pg-pwa-sw.js"
    for required in (index, manifest, worker, LANDING, WEB / "main.dart.js"):
        if not required.is_file():
            raise RuntimeError(f"Missing required file: {required}")

    original = index.read_text(encoding="utf-8")
    if "flutter_bootstrap.js" not in original:
        raise RuntimeError("Flutter index.html no longer has a recognized bootstrap; abort")
    if app.exists():
        raise RuntimeError("app.html already exists; refusing repeated index transform")

    # The Flutter app still runs with original /pg-robotics-pwa/ base href.
    # Use an inline branded loading state, avoiding a white rectangle as engine starts.
    splash = """
<meta name="robots" content="noindex, nofollow, noarchive">
<script>
  // In normal browsers, show the installation gate rather than the Flutter app.
  if (!window.matchMedia('(display-mode: standalone)').matches && navigator.standalone !== true) {
    location.replace('./');
  }
</script>
<style>
  #pg-flutter-splash{position:fixed;inset:0;z-index:999999;display:grid;place-content:center;gap:16px;text-align:center;background:#0a0b0d;color:#fff;font:800 18px -apple-system,BlinkMacSystemFont,Arial,sans-serif;letter-spacing:2px}
  #pg-flutter-splash img{display:block;width:73px;height:73px;margin:auto;border-radius:18px}
  #pg-flutter-splash small{display:block;color:#aaa;font-size:11px;letter-spacing:1px;font-weight:500}
  #pg-flutter-splash .bar{width:150px;height:3px;margin:6px auto 0;background:#3a3b34;border-radius:5px;overflow:hidden}
  #pg-flutter-splash .bar:before{display:block;content:"";background:#ffe019;width:48%;height:100%;animation:pg-progress 1.35s ease-in-out infinite alternate}
  @keyframes pg-progress{from{transform:translateX(-100%)}to{transform:translateX(290%)}}
</style>
<script>
  (function(){
    function remove(){var p=document.getElementById('pg-flutter-splash');if(p)p.remove();}
    window.addEventListener('flutter-first-frame', remove, {once:true});
    // Defensive fallback in case Flutter changes its first-frame notification.
    window.addEventListener('load',function(){setTimeout(remove,16000);});
  })();
</script>
"""
    first_frame = """
<div id="pg-flutter-splash" role="status" aria-label="PG Robotics завантажується">
  <img src="icons/Icon-192.png" alt="">
  <div>PG ROBOTICS</div><small>ЗАВАНТАЖЕННЯ ЗАСТОСУНКУ</small>
  <div class="bar"></div>
</div>
"""
    if "</head>" not in original or "<body>" not in original:
        raise RuntimeError("Unexpected Flutter HTML layout; abort")
    app_html = original.replace("</head>", splash + "\n</head>", 1).replace(
        "<body>", "<body>\n" + first_frame, 1
    )
    app.write_text(app_html, encoding="utf-8")

    landing = LANDING.read_text(encoding="utf-8")
    if "<!doctype html>" not in landing.lower() or 'id="install"' not in landing:
        raise RuntimeError("Landing page validation failed")
    index.write_text(landing, encoding="utf-8")

    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    # Preserve the identity of the PWA installed previously with start_url '.'.
    metadata["id"] = "."
    metadata["start_url"] = "./app.html"
    metadata["scope"] = "."
    metadata["display"] = "standalone"
    metadata["name"] = "PG Robotics"
    metadata["short_name"] = "PG Robotics"
    manifest.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    source = worker.read_text(encoding="utf-8")
    m = re.search(r"const START = (\[[^\n;]+\]);", source)
    if not m:
        raise RuntimeError("Unsupported SW pre-cache structure")
    files = json.loads(m.group(1))
    if "app.html" not in files:
        files.append("app.html")
    if "index.html" not in files:
        files.append("index.html")
    source = source[:m.start(1)] + json.dumps(files, ensure_ascii=False) + source[m.end(1):]
    # Cache each actual navigation URL; keep the correct offline screen for app.html.
    source = source.replace("cache.put('index.html', response.clone())", "cache.put(r, response.clone())")
    source = source.replace(
        "(await cache.match('index.html')) || Response.error()",
        "(await cache.match(r)) || (await cache.match('app.html')) || (await cache.match('index.html')) || Response.error()",
    )
    # Bump cache name even when Dart app did not change.
    version = hashlib.sha256(index.read_bytes() + app.read_bytes()).hexdigest()[:12]
    source = re.sub(r"const CACHE = 'pg-robotics-[a-f0-9]+';",
                    f"const CACHE = 'pg-robotics-{version}';", source, count=1)
    worker.write_text(source, encoding="utf-8")

    assert (WEB / "flutter_bootstrap.js").is_file()
    assert (WEB / "main.dart.js").is_file()
    assert "app.html" in json.loads(manifest.read_text(encoding="utf-8"))["start_url"]
    print("Install welcome screen ready: /")
    print("Native-feeling Flutter web application ready: /app.html")
    print("PWA manifest starts the app directly. Offline cache:", version)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
