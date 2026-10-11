#!/usr/bin/env python3
"""Build dist/index.html from src/template.html + data/plan.json.

The data is inlined rather than fetched, so the page works from a file:// URL
and inside the iOS Files preview, where sibling files can't be loaded.
"""
import json, base64, hashlib, pathlib, sys, subprocess

ROOT = pathlib.Path(__file__).resolve().parent
SRC  = ROOT / 'src' / 'template.html'
DATA = ROOT / 'data' / 'plan.json'
DIST = ROOT / 'docs'   # GitHub Pages serves this folder from main

def main():
    DIST.mkdir(exist_ok=True)

    try:
        plan = json.loads(DATA.read_text())
    except json.JSONDecodeError as e:
        sys.exit('plan.json is not valid JSON: line %d, column %d — %s' % (e.lineno, e.colno, e.msg))

    icon = DIST / 'icon-180.png'
    if not icon.exists():
        subprocess.run([sys.executable, str(ROOT / 'tools' / 'make_icon.py'),
                        '%s:180' % (DIST / 'icon-180.png'),
                        '%s:192' % (DIST / 'icon-192.png'),
                        '%s:512' % (DIST / 'icon-512.png')], check=True)

    icon_uri = 'data:image/png;base64,' + base64.b64encode(icon.read_bytes()).decode()

    html = SRC.read_text()
    # json.dumps output is embedded in a <script>; close out any literal </script>.
    html = html.replace('__PLAN_JSON__', json.dumps(plan, ensure_ascii=False).replace('</', '<\\/'))
    html = html.replace('__ICON_DATA_URI__', icon_uri)

    out = DIST / 'index.html'
    out.write_text(html)

    (DIST / 'manifest.webmanifest').write_text(json.dumps({
        'name': 'Week', 'short_name': 'Week', 'start_url': './index.html',
        'display': 'standalone', 'background_color': '#0e0f12', 'theme_color': '#0e0f12',
        'icons': [{'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
                  {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png'}],
    }, indent=2))

    # Cache name is tied to the build so a rebuild invalidates the old copy.
    stamp = hashlib.sha1(html.encode()).hexdigest()[:10]
    (DIST / 'sw.js').write_text(
        "const C = 'week-%s';\n"
        "const ASSETS = ['./', './index.html', './icon-180.png', './icon-192.png', './icon-512.png'];\n"
        "self.addEventListener('install', e => {\n"
        "  e.waitUntil(caches.open(C).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));\n"
        "});\n"
        "self.addEventListener('activate', e => {\n"
        "  e.waitUntil(caches.keys()\n"
        "    .then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k))))\n"
        "    .then(() => self.clients.claim()));\n"
        "});\n"
        "self.addEventListener('fetch', e => {\n"
        "  if (e.request.method !== 'GET') return;\n"
        "  e.respondWith(\n"
        "    fetch(e.request).then(r => {\n"
        "      const copy = r.clone();\n"
        "      caches.open(C).then(c => c.put(e.request, copy));\n"
        "      return r;\n"
        "    }).catch(() => caches.match(e.request).then(m => m || caches.match('./index.html')))\n"
        "  );\n"
        "});\n" % stamp)

    print('built %s  (%.1f KB, self-contained)' % (out.relative_to(ROOT), out.stat().st_size / 1024))
    print('       docs/sw.js  (cache week-%s)' % stamp)

if __name__ == '__main__':
    main()
