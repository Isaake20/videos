"""Shared helpers for the video-factory scripts (stdlib only)."""
import json, os, re, sys, time, unicodedata, urllib.request, urllib.parse, urllib.error

ROOT = os.environ.get("VF_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
UA = "video-factory/1.0 (automated short-video pipeline)"


def path(*parts):
    p = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def http(url, data=None, headers=None, timeout=60, method=None):
    h = {"User-Agent": UA}
    h.update(headers or {})
    if isinstance(data, (dict, list)):
        data = json.dumps(data).encode()
        h.setdefault("Content-Type", "application/json")
    for attempt in range(5):
        req = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 502, 503) or attempt == 4:
                raise
            time.sleep(min(float(e.headers.get("Retry-After") or 0) or 2 ** (attempt + 1), 20))


def get_json(url, **kw):
    return json.loads(http(url, **kw))


def load(p, default=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def die(msg, code=1):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(code)
