#!/usr/bin/env python3
"""Research pack for a topic: facts + freely licensed images from Wikipedia/Commons.
usage: wiki.py <slug> "<Article title>" ["<Second article>" ...]
Writes work/<slug>/research.json and work/<slug>/img/*.jpg with licence + author."""
import re, sys, time, urllib.parse
from common import http, get_json, load, save, path, die

if len(sys.argv) < 3:
    die(__doc__)
slug, titles = sys.argv[1], sys.argv[2:]
lang = load(path("config", "channel.json"), {}).get("wiki_lang", "es")
base = f"https://{lang}.wikipedia.org"
OK = re.compile(r"^(cc0|cc[ -]by|public domain|pd|no restrictions)", re.I)
pack = {"articles": [], "images": []}
n = 0
seen = set()
for title in titles:
    q = urllib.parse.quote(title.replace(" ", "_"), safe="")
    try:
        s = get_json(f"{base}/api/rest_v1/page/summary/{q}")
    except Exception as e:
        print(f"skip {title}: {e}"); continue
    ext = get_json(f"{base}/w/api.php?action=query&format=json&prop=extracts&explaintext=1&exlimit=1&redirects=1&titles={q}")
    text = next(iter(ext["query"]["pages"].values())).get("extract", "")[:9000]
    pack["articles"].append({"title": s.get("title"), "url": s["content_urls"]["desktop"]["page"],
                             "description": s.get("description"), "summary": s.get("extract"), "text": text})
    try:
        items = get_json(f"{base}/api/rest_v1/page/media-list/{q}")["items"]
    except Exception:
        items = []
    files = [i["title"] for i in items if i.get("type") == "image" and not i["title"].lower().endswith(".svg")][:8]
    for i in range(0, len(files), 6):
        tq = urllib.parse.quote("|".join(files[i:i + 6]))
        info = get_json(f"{base}/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata|size&iiurlwidth=1280&titles={tq}")
        for p in info.get("query", {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [None])[0]
            if not ii:
                continue
            md = ii.get("extmetadata", {})
            lic = md.get("LicenseShortName", {}).get("value", "")
            if p["title"] in seen:
                continue
            seen.add(p["title"])
            if n >= (30 if slug.endswith("-largo") else 10) or not OK.match(lic) or ii.get("width", 0) < 700:
                continue  # only reusable licences, only usable resolution
            author = re.sub(r"<[^>]+>", "", md.get("Artist", {}).get("value", "desconocido")).strip()[:80]
            n += 1
            fn = f"img/{n:02d}.jpg"
            time.sleep(1.5)  # Wikimedia rate limits bursts
            try:
                blob = http(ii.get("thumburl") or ii["url"], timeout=25)
            except Exception as e:
                try:  # some thumbnails redirect to a host the network may not allow: fall back to the original
                    if ii.get("size", 9e9) > 8e6:
                        raise
                    blob = http(ii["url"], timeout=40)
                except Exception:
                    n -= 1; print(f"skip image {p['title']}: {e}"); continue
            open(path("work", slug, fn), "wb").write(blob)
            pack["images"].append({"file": fn, "title": p["title"], "license": lic, "author": author,
                                   "source": ii.get("descriptionurl"), "article": s.get("title"),
                                   "description": re.sub(r"<[^>]+>", "", md.get("ImageDescription", {}).get("value", ""))[:200]})
if not pack["articles"]:
    die("no article found")
save(path("work", slug, "research.json"), pack)
print(f"{len(pack['articles'])} articles, {len(pack['images'])} licensed images -> work/{slug}/")
for im in pack["images"]:
    print(f"  {im['file']}  [{im['license']}] {im['title']} — {im['description'][:70]}")
