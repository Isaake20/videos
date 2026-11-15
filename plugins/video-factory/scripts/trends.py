#!/usr/bin/env python3
"""Collect trend signals -> state/trends.json.
Sources: Google Trends daily RSS (several countries), most-viewed Wikipedia
articles, Hacker News front page, Wikipedia "on this day" (evergreen fallback)."""
import datetime as dt, re, sys, xml.etree.ElementTree as ET
from common import http, get_json, load, save, path

cfg = load(path("config", "channel.json"), {})
GEOS = cfg.get("trend_geos", ["MX", "ES", "AR", "CO", "US"])
WIKI = cfg.get("wiki_lang", "es")
NS = {"ht": "https://trends.google.com/trending/rss"}
out, errors = [], []


def traffic(s):
    m = re.match(r"([\d.,]+)\s*([KMkm]?)", s or "")
    if not m:
        return 0
    n = float(m.group(1).replace(",", ""))
    return int(n * {"K": 1e3, "M": 1e6, "": 1}[m.group(2).upper()])


for geo in GEOS:
    try:
        root = ET.fromstring(http(f"https://trends.google.com/trending/rss?geo={geo}"))
        for it in root.iter("item"):
            out.append({
                "source": "google_trends", "geo": geo, "topic": it.findtext("title"),
                "signal": traffic(it.findtext("ht:approx_traffic", "", NS)),
                "context": [n.findtext("ht:news_item_title", "", NS) for n in it.findall("ht:news_item", NS)][:3],
            })
    except Exception as e:
        errors.append(f"google_trends {geo}: {e}")

for back in (1, 2, 3):  # pageview data lags a day or two
    d = dt.date.today() - dt.timedelta(days=back)
    try:
        arts = get_json(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/{WIKI}.wikipedia/all-access/{d:%Y/%m/%d}")["items"][0]["articles"]
        for a in arts[:80]:
            if ":" in a["article"]:
                continue
            out.append({"source": "wikipedia_top", "geo": WIKI, "topic": a["article"].replace("_", " "),
                        "signal": a["views"], "context": [f"rank {a['rank']} on {d}"]})
        break
    except Exception as e:
        errors.append(f"wikipedia_top {d}: {e}")

try:
    for i in get_json("https://hacker-news.firebaseio.com/v0/topstories.json")[:20]:
        s = get_json(f"https://hacker-news.firebaseio.com/v0/item/{i}.json")
        out.append({"source": "hacker_news", "geo": "global", "topic": s.get("title"),
                    "signal": s.get("score", 0), "context": [s.get("url", "")]})
except Exception as e:
    errors.append(f"hacker_news: {e}")

try:
    t = dt.date.today()
    ev = get_json(f"https://{WIKI}.wikipedia.org/api/rest_v1/feed/onthisday/events/{t.month}/{t.day}")["events"]
    for e in ev[:25]:
        out.append({"source": "on_this_day", "geo": WIKI, "topic": e["text"], "signal": 0,
                    "context": [str(e.get("year", ""))] + [p["title"].replace("_", " ") for p in e.get("pages", [])[:3]]})
except Exception as e:
    errors.append(f"on_this_day: {e}")

done = {v["topic_key"] for v in load(path("state", "history.json"), [])}
for o in out:
    o["already_covered"] = (o["topic"] or "").lower() in done
save(path("state", "trends.json"), {"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(), "errors": errors, "candidates": out})
by = {}
for o in out:
    by[o["source"]] = by.get(o["source"], 0) + 1
print(f"{len(out)} candidates {by}; errors: {errors or 'none'} -> state/trends.json")
sys.exit(0 if out else 1)
