#!/usr/bin/env python3
"""YouTube desk: publish, comments and analytics through the official YouTube APIs (stdlib only).

usage:
  youtube.py check                         who am I + quota-free sanity check
  youtube.py upload <output-dir>           upload video.mp4 + thumbnail.jpg of a finished, QA-passed video
  youtube.py comments                      pending comments -> state/comments_inbox.json
  youtube.py reply <comment-id> "<text>"   answer one comment (capped per day)
  youtube.py analytics [days]              per-video numbers -> state/analytics.json
  youtube.py retention <video-id>          audience retention curve of one video

Auth: the refresh token is read from the environment variable YT_REFRESH_TOKEN. The OAuth client is either
the environment variables YT_CLIENT_ID + YT_CLIENT_SECRET, or a network secret for oauth2.googleapis.com
(Basic auth, injected by the proxy). Exit code 3 = credentials missing or rejected.
"""
import datetime as dt, json, os, sys, urllib.error, urllib.parse, urllib.request
from common import load, save, path, die, UA

API = "https://www.googleapis.com/youtube/v3"
cfg = load(path("config", "channel.json"), {})
PUB = cfg.get("publish", {})
COM = cfg.get("community", {})
_token = None


def call(url, data=None, headers=None, method=None, raw=False, timeout=120):
    h = {"User-Agent": UA}
    h.update(headers or {})
    if isinstance(data, (dict, list)):
        data = json.dumps(data).encode(); h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return (r.headers, body) if raw else (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")[:600]
        die(f"YouTube API {e.code} on {url.split('?')[0]}: {msg}", 3 if e.code in (400, 401, 403) and "oauth2" in url else 1)
    except urllib.error.URLError as e:
        die(f"network error on {url.split('?')[0]}: {e.reason} (is the host allowed in the environment?)", 3)


def token():
    global _token
    if _token:
        return _token
    rt = os.environ.get("YT_REFRESH_TOKEN")
    if not rt:
        die("YT_REFRESH_TOKEN is not set: YouTube is not connected yet (see README, 'Conectar YouTube')", 3)
    form = {"grant_type": "refresh_token", "refresh_token": rt}
    if os.environ.get("YT_CLIENT_ID") and os.environ.get("YT_CLIENT_SECRET"):  # client kept as environment variables
        form.update(client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"])
    body = urllib.parse.urlencode(form).encode()
    r = call("https://oauth2.googleapis.com/token", body, {"Content-Type": "application/x-www-form-urlencoded"})
    _token = r.get("access_token") or die("token endpoint returned no access_token", 3)
    return _token


def api(pathq, data=None, method=None, base=API):
    return call(f"{base}/{pathq}", data, {"Authorization": "Bearer " + token()}, method)


def me():
    items = api("channels?part=snippet,statistics&mine=true").get("items") or die("this Google account has no YouTube channel", 3)
    return items[0]


def today():
    return dt.date.today().isoformat()


def cmd_check():
    c = me()
    print(json.dumps({"channel_id": c["id"], "title": c["snippet"]["title"], "subscribers": c["statistics"].get("subscriberCount"),
                      "videos": c["statistics"].get("videoCount"), "publish_enabled": bool(PUB.get("enabled")),
                      "privacy": PUB.get("privacy", "private")}, ensure_ascii=False, indent=2))


def cmd_upload(odir):
    odir = os.path.abspath(odir)
    video, mp = os.path.join(odir, "video.mp4"), os.path.join(odir, "metadata.json")
    meta = load(mp) or die(f"no metadata.json in {odir}")
    if not PUB.get("enabled"):
        die("publishing is disabled (config/channel.json -> publish.enabled)")
    if meta.get("draft") or os.sep + "drafts" + os.sep in odir + os.sep:
        die("drafts are never published")
    if (load(os.path.join(odir, "qa_video.json")) or {}).get("verdict") != "pass":
        die("qa_video.json has no passing verdict: the video QA must approve before publishing")
    if meta.get("youtube_id"):
        die(f"already published as {meta['youtube_id']}")
    log = load(path("state", "published.json"), [])
    if sum(1 for p in log if p["date"] == today()) >= int(PUB.get("max_uploads_per_day", 1)):
        die("daily upload cap reached (publish.max_uploads_per_day)")
    tags = [t.lstrip("#") for t in meta.get("hashtags", [])][:15]
    body = {"snippet": {"title": meta["title"][:100], "description": meta["description"][:4900], "tags": tags,
                        "categoryId": str(PUB.get("category_id", "27")), "defaultLanguage": cfg.get("language", "es"),
                        "defaultAudioLanguage": cfg.get("language", "es")},
            "status": {"privacyStatus": PUB.get("privacy", "private"), "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": True}}
    size = os.path.getsize(video)
    hdrs, _ = call(f"https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", body,
                   {"Authorization": "Bearer " + token(), "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)}, raw=True)
    loc = hdrs.get("Location") or die("no resumable upload URL returned")
    with open(video, "rb") as f:
        _, out = call(loc, f.read(), {"Authorization": "Bearer " + token(), "Content-Type": "video/mp4"}, method="PUT", raw=True, timeout=900)
    res = json.loads(out); vid = res["id"]
    thumb = os.path.join(odir, "thumbnail.jpg"); thumb_ok = False
    if os.path.exists(thumb):
        try:
            with open(thumb, "rb") as f:
                call(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}", f.read(),
                     {"Authorization": "Bearer " + token(), "Content-Type": "image/jpeg"}, raw=True)
            thumb_ok = True
        except SystemExit:
            print("warning: thumbnail not set (the channel may need phone verification for custom thumbnails)", file=sys.stderr)
    meta.update({"youtube_id": vid, "youtube_url": f"https://youtu.be/{vid}", "published_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "privacy": res.get("status", {}).get("privacyStatus")})
    save(mp, meta)
    log.append({"date": today(), "video_id": vid, "title": meta["title"], "privacy": meta["privacy"], "thumbnail_set": thumb_ok,
                "output": os.path.relpath(odir, path("x")[:-2])})
    save(path("state", "published.json"), log)
    print(f"PUBLISHED https://youtu.be/{vid} privacy={meta['privacy']} thumbnail={'ok' if thumb_ok else 'no'}")


def cmd_comments():
    ch = me()["id"]
    answered = {r["comment_id"] for r in load(path("state", "replies.json"), [])}
    r = api(f"commentThreads?part=snippet,replies&allThreadsRelatedToChannelId={ch}&order=time&maxResults=50&moderationStatus=published")
    inbox = []
    for t in r.get("items", []):
        top = t["snippet"]["topLevelComment"]; s = top["snippet"]
        if s.get("authorChannelId", {}).get("value") == ch or top["id"] in answered:
            continue
        if any(x["snippet"].get("authorChannelId", {}).get("value") == ch for x in t.get("replies", {}).get("comments", [])):
            continue
        inbox.append({"comment_id": top["id"], "video_id": s.get("videoId"), "author": s.get("authorDisplayName"),
                      "text": s.get("textOriginal"), "likes": s.get("likeCount"), "published_at": s.get("publishedAt")})
    save(path("state", "comments_inbox.json"), {"fetched_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "pending": inbox})
    print(f"{len(inbox)} pending comments -> state/comments_inbox.json")


def cmd_reply(cid, text):
    text = text.strip()
    if not text or len(text) > 500:
        die("reply must be 1-500 characters")
    log = load(path("state", "replies.json"), [])
    if any(r["comment_id"] == cid for r in log):
        die("this comment was already answered")
    if sum(1 for r in log if r["date"] == today()) >= int(COM.get("max_replies_per_day", 15)):
        die("daily reply cap reached (community.max_replies_per_day)")
    if not COM.get("enabled"):
        die("replies are disabled (config/channel.json -> community.enabled)")
    res = api("comments?part=snippet", {"snippet": {"parentId": cid, "textOriginal": text}})
    log.append({"date": today(), "comment_id": cid, "reply_id": res.get("id"), "text": text})
    save(path("state", "replies.json"), log)
    print("replied", res.get("id"))


def cmd_analytics(days=28):
    end = dt.date.today(); start = end - dt.timedelta(days=int(days))
    q = urllib.parse.urlencode({"ids": "channel==MINE", "startDate": start.isoformat(), "endDate": end.isoformat(),
                                "metrics": "views,averageViewDuration,averageViewPercentage,likes,comments,subscribersGained",
                                "dimensions": "video", "sort": "-views", "maxResults": 50})
    r = api("reports?" + q, base="https://youtubeanalytics.googleapis.com/v2")
    cols = [c["name"] for c in r.get("columnHeaders", [])]
    rows = [dict(zip(cols, row)) for row in r.get("rows", [])]
    titles = {p["video_id"]: p["title"] for p in load(path("state", "published.json"), [])}
    for row in rows:
        row["title"] = titles.get(row["video"])
    save(path("state", "analytics.json"), {"fetched_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "days": int(days), "videos": rows})
    print(f"{len(rows)} videos -> state/analytics.json")


def cmd_retention(vid):
    end = dt.date.today(); start = end - dt.timedelta(days=90)
    q = urllib.parse.urlencode({"ids": "channel==MINE", "startDate": start.isoformat(), "endDate": end.isoformat(),
                                "metrics": "audienceWatchRatio", "dimensions": "elapsedVideoTimeRatio", "filters": f"video=={vid}"})
    r = api("reports?" + q, base="https://youtubeanalytics.googleapis.com/v2")
    curve = [{"t": row[0], "watch_ratio": row[1]} for row in r.get("rows", [])]
    save(path("state", "retention", f"{vid}.json"), {"video_id": vid, "curve": curve})
    print(f"{len(curve)} points -> state/retention/{vid}.json")


if __name__ == "__main__":
    a = sys.argv[1:]
    cmds = {"check": (cmd_check, 0), "upload": (cmd_upload, 1), "comments": (cmd_comments, 0), "reply": (cmd_reply, 2),
            "analytics": (cmd_analytics, 0), "retention": (cmd_retention, 1)}
    if not a or a[0] not in cmds:
        die(__doc__)
    fn, n = cmds[a[0]]
    if len(a) - 1 < n:
        die(__doc__)
    fn(*a[1:1 + max(n, len(a) - 1)])
