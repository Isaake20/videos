#!/usr/bin/env python3
"""Deterministic production line for one video. usage: pipeline.py <slug> [--draft]
validate -> voice -> music -> render -> technical checks -> record in state/history.json"""
import datetime as dt, glob, json, os, subprocess, sys
from common import load, save, path, die

slug = sys.argv[1]; draft = "--draft" in sys.argv
here = os.path.dirname(os.path.abspath(__file__))
cfg = load(path("config", "channel.json"), {})
script = load(path("work", slug, "script.json")) or die("no script.json")


def step(name, args, optional=False):
    print(f"== {name}", flush=True)
    r = subprocess.run([sys.executable, os.path.join(here, args[0])] + args[1:])
    if r.returncode and not optional:
        die(f"{name} failed (exit {r.returncode})", r.returncode)
    return r.returncode == 0


step("validate", ["validate_script.py", path("work", slug, "script.json")])
step("voice", ["tts.py", slug] + (["--draft"] if draft else []))
if not draft and cfg.get("elevenlabs", {}).get("music") and script.get("music_prompt"):
    step("music", ["music.py", slug, script["music_prompt"]], optional=True)
step("render", ["render.py", slug])

day = dt.date.today().isoformat()
odir = path("output", *(["drafts"] if draft else []), f"{day}-{slug}", "x")[:-2]
v = os.path.join(odir, "video.mp4")
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", v],
                               capture_output=True, text=True).stdout)
vs = next(s for s in pr["streams"] if s["codec_type"] == "video")
dur = float(pr["format"]["duration"])
checks = {"1080x1920": (vs["width"], vs["height"]) == (1080, 1920), "under_60s": dur <= 60,
          "has_audio": any(s["codec_type"] == "audio" for s in pr["streams"]),
          "under_100MB": int(pr["format"]["size"]) < 100e6}
print("checks:", checks)
if not all(checks.values()):
    die("technical checks failed")
if not draft:
    hist = load(path("state", "history.json"), [])
    hist.append({"date": day, "slug": slug, "title": script["title"], "topic_key": script["trend"]["topic"].lower(),
                 "chars": load(path("work", slug, "timing.json"))["chars"], "output": os.path.relpath(odir, path("x")[:-2])})
    save(path("state", "history.json"), hist)
print(f"DONE {'(draft) ' if draft else ''}{v}  {dur:.1f}s")
