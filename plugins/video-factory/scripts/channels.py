#!/usr/bin/env python3
"""Analyse reference channels from their public RSS feeds -> state/channels.json.
Measures what works (views/day, title patterns, cadence, Shorts share). It reads
only public metadata: it never downloads or copies anyone's video."""
import datetime as dt, re, statistics, sys, xml.etree.ElementTree as ET
from common import http, load, save, path

NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "m": "http://search.yahoo.com/mrss/"}
cfgp = path("config", "channels.json")
cfg = load(cfgp, {"channels": []})
now = dt.datetime.now(dt.timezone.utc)
report, changed = [], False


def resolve(handle):
    html = http(f"https://www.youtube.com/{handle}", headers={
        "User-Agent": "Mozilla/5.0", "Accept-Language": "en", "Cookie": "SOCS=CAI"}).decode("utf-8", "ignore")
    m = re.search(r'"externalId":"(UC[\w-]{22})"|channel_id=(UC[\w-]{22})', html)
    return (m.group(1) or m.group(2)) if m else None


for ch in cfg["channels"]:
    try:
        if not ch.get("id"):
            ch["id"] = resolve(ch["handle"]); changed = True
            if not ch["id"]:
                raise RuntimeError("could not resolve channel id")
        root = ET.fromstring(http(f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"))
        vids = []
        for e in root.findall("a:entry", NS):
            pub = dt.datetime.fromisoformat(e.findtext("a:published", "", NS))
            st = e.find("m:group/m:community/m:statistics", NS)
            views = int(st.get("views")) if st is not None else 0
            age = max((now - pub).total_seconds() / 86400, 0.25)
            link = e.find("a:link", NS).get("href")
            title = e.findtext("a:title", "", NS)
            vids.append({"title": title, "url": link, "published": pub.isoformat(), "views": views,
                         "views_per_day": round(views / age), "is_short": "/shorts/" in link,
                         "title_len": len(title), "has_number": bool(re.search(r"\d", title)),
                         "is_question": "?" in title, "caps_words": len(re.findall(r"\b[A-ZÁÉÍÓÚÑ]{3,}\b", title))})
        if not vids:
            raise RuntimeError("empty feed")
        dates = sorted(dt.datetime.fromisoformat(v["published"]) for v in vids)
        span = max((dates[-1] - dates[0]).days, 1)
        vpd = [v["views_per_day"] for v in vids]
        med = statistics.median(vpd)
        for v in vids:
            v["outlier_score"] = round(v["views_per_day"] / med, 2) if med else 0
        report.append({
            "handle": ch["handle"], "name": root.findtext("a:title", "", NS), "why": ch.get("why", ""),
            "videos_sampled": len(vids), "uploads_per_week": round(len(vids) / span * 7, 1),
            "shorts_share": round(sum(v["is_short"] for v in vids) / len(vids), 2),
            "median_views_per_day": med, "avg_title_len": round(statistics.mean(v["title_len"] for v in vids)),
            "question_title_share": round(sum(v["is_question"] for v in vids) / len(vids), 2),
            "number_title_share": round(sum(v["has_number"] for v in vids) / len(vids), 2),
            "top_videos": sorted(vids, key=lambda v: -v["outlier_score"])[:5],
        })
    except Exception as ex:
        report.append({"handle": ch.get("handle"), "error": str(ex)})

if changed:
    save(cfgp, cfg)
save(path("state", "channels.json"), {"fetched_at": now.isoformat(), "channels": report})
for r in report:
    if "error" in r:
        print(f"{r['handle']}: ERROR {r['error']}")
    else:
        print(f"{r['handle']}: {r['uploads_per_week']}/wk, shorts {r['shorts_share']:.0%}, median {r['median_views_per_day']:.0f} views/day; top: {r['top_videos'][0]['title'][:70]!r} x{r['top_videos'][0]['outlier_score']}")
sys.exit(0 if any("error" not in r for r in report) else 1)
